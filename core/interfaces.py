from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class LLMConfig:
    """LLM 连接配置。仅支持 OpenAI 兼容协议（含国产代理服务）。"""
    base_url: Optional[str]  # OpenAI 兼容接口的 Base URL，留空则使用官方地址
    api_key: str
    model_name: str
    temperature: float = 0.7

@dataclass
class EmbedConfig:
    """Embedding 连接配置。仅支持 OpenAI 兼容协议（含国产代理服务）。"""
    base_url: Optional[str]  # OpenAI 兼容接口的 Base URL，留空则使用官方地址
    api_key: str
    model_name: str


class IRAGBackend(ABC):
    """
    RAG核心服务的抽象基类接口约束。
    """

    @abstractmethod
    def ping_llm(self, config: LLMConfig) -> bool:
        """测试大语言模型配置连通性"""
        pass

    @abstractmethod
    def ping_embedding(self, config: EmbedConfig) -> bool:
        """测试向量模型连通性"""
        pass

    @abstractmethod
    def initialize(self, llm_config: LLMConfig, embed_config: EmbedConfig) -> bool:
        """初始化整个 RAG 后端实例"""
        pass

    @abstractmethod
    def ingest_documents(self, file_paths: List[str]) -> bool:
        """解析切分并入库文档"""
        pass

    @abstractmethod
    def chat(self, query: str, chat_history: List[Dict[str, str]] = None) -> str:
        """RAG对话请求"""
        pass

