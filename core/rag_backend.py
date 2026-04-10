import logging
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from core.interfaces import (
    IRAGBackend,
    LLMConfig,
    EmbedConfig
)

logger = logging.getLogger(__name__)

# Streamlit Cloud 内存保护：单 Session 最多允许缓存的向量 Chunk 数量
_MAX_CHUNKS = 2000

class LangChainRAGBackend(IRAGBackend):
    def __init__(self):
        self.llm = None
        self.embeddings = None
        self.vector_store = None
        self._chunk_count = 0  # 当前已入库的 Chunk 总数

    def _build_llm(self, config: LLMConfig):
        """内部工厂：构建 OpenAI 兼容协议的 LLM 客户端。"""
        return ChatOpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            model=config.model_name,
            temperature=config.temperature,
            max_retries=2
        )

    def _build_embeddings(self, config: EmbedConfig):
        """内部工厂：构建 OpenAI 兼容协议的 Embedding 客户端。
        
        使用 SafeOpenAIEmbeddings 子类处理部分第三方服务要求
        input 必须为列表的 API 差异（避免 'No schema matches' 错误）。
        """
        class SafeOpenAIEmbeddings(OpenAIEmbeddings):
            def embed_query(self, text: str) -> List[float]:
                return self.embed_documents([text])[0]

        return SafeOpenAIEmbeddings(
            api_key=config.api_key,
            base_url=config.base_url,
            model=config.model_name,
            check_embedding_ctx_length=False  # 禁用本地 tiktoken 长度检查，兼容非官方模型
        )

    def ping_llm(self, config: LLMConfig) -> bool:
        try:
            temp_llm = self._build_llm(config)
            response = temp_llm.invoke("Hi")
            return response is not None
        except Exception as e:
            logger.error(f"LLM Ping 失败: {e}")
            return False

    def ping_embedding(self, config: EmbedConfig) -> bool:
        try:
            temp_embed = self._build_embeddings(config)
            result = temp_embed.embed_query("test")
            return len(result) > 0
        except Exception as e:
            logger.error(f"Embedding Ping 失败: {e}")
            return False

    def initialize(self, llm_config: LLMConfig, embed_config: EmbedConfig) -> bool:
        try:
            self.llm = self._build_llm(llm_config)
            self.embeddings = self._build_embeddings(embed_config)
            # FAISS 将在摄入文档时按需初始化
            return True
        except Exception as e:
            logger.error(f"后端初始化失败: {e}")
            return False

    def clear_index(self):
        """清空内存中的知识库索引以释放资源"""
        self.vector_store = None
        self._chunk_count = 0
        logger.info("知识库索引已清空，内存释放。")

    def ingest_documents(self, file_paths: List[str]) -> bool:
        if not self.embeddings:
            raise RuntimeError("后端服务尚未初始化。请先调用 initialize()。")

        all_docs = []
        for path in file_paths:
            try:
                # 简单应对 pdf 和 txt
                if path.lower().endswith(".pdf"):
                    loader = PyPDFLoader(path)
                    docs = loader.load()
                else:
                    loader = TextLoader(path, encoding="utf-8")
                    docs = loader.load()
                all_docs.extend(docs)
            except Exception as e:
                logger.error(f"文件加载异常 {path}: {e}")
        
        if not all_docs:
            return False

        # 进行文本切分
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150
        )
        splits = text_splitter.split_documents(all_docs)

        # OOM 保护：检查是否超过单 Session 的最大 Chunk 数量限制
        if self._chunk_count + len(splits) > _MAX_CHUNKS:
            logger.warning(
                f"拒绝入库：当前已有 {self._chunk_count} 个 Chunk，"
                f"新增 {len(splits)} 个将超过上限 {_MAX_CHUNKS}。"
                "请先调用 clear_index() 清空知识库后再上传。"
            )
            return False
        
        try:
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(splits, self.embeddings)
            else:
                self.vector_store.add_documents(documents=splits)
            self._chunk_count += len(splits)
            logger.info(f"入库成功，当前 Chunk 总数：{self._chunk_count}/{_MAX_CHUNKS}")
            return True
        except Exception as e:
            logger.error(f"向量入库失败: {e}")
            return False

    def chat(self, query: str, chat_history: List[Dict[str, str]] = None) -> str:
        if not self.llm or not self.vector_store:
            raise RuntimeError("服务未初始化完全。")
            
        # 1. 检索相似片段
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 4})
        docs = retriever.invoke(query)
        context_text = "\n\n".join([doc.page_content for doc in docs])
        
        # 2. 组装历史消息
        messages = [
            SystemMessage(content=f"你是一个有用的 RAG 助手。请基于以下提供的参考背景信息来回答用户的问题。如果信息不够，请如实说明。\n\n--- 背景信息 ---\n{context_text}")
        ]
        
        if chat_history:
            for message in chat_history:
                role = message.get("role", "user")
                content = message.get("content", "")
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))
                    
        # 3. 添加当前提问
        messages.append(HumanMessage(content=query))
        
        # 4. 生成回答
        response = self.llm.invoke(messages)
        return response.content
