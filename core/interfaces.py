from abc import ABC, abstractmethod
from typing import List, Dict, Any

class IRAGBackend(ABC):
    """
    检索增强生成 (RAG) 核心服务的抽象基类接口约束。
    """

    @abstractmethod
    def upload_file(self, file_bytes: bytes, file_name: str, session_id: str) -> Dict[str, Any]:
        """
        接收上传的文件数据流，执行数据切分与向量化实体建立。

        Args:
            file_bytes (bytes): 客户端上传的物理文件二进制数据流。
            file_name (str): 文件的带有扩展名的原始字符串文件名称。
            session_id (str): 客户端会话唯一标识符，用于底层数据库物理或逻辑架构的隔离处理。

        Returns:
            Dict[str, Any]: JSON 结构的标准格式响应报文。
            固定结构要求:
            - success (bool): 代表当前请求整体成功或失败的标记状态。
            - message (str): 执行结束对外的结果文字化描述反馈。
            - data (Dict[str, Any], optional): 业务拓展数据承接树层。
        """
        pass

    @abstractmethod
    def ask_question(self, question: str, chat_history: List[Dict[str, str]], session_id: str) -> Dict[str, Any]:
        """
        执行包含上下文继承依赖的知识库实体检索调用和合并生成任务响应。

        Args:
            question (str): 当前单次发起请求的无修饰对话请求字符串。
            chat_history (List[Dict[str, str]]): 多轮通信历史序列化。
                单条数据字典结构准则:`{"role": "user/assistant", "content": "..."}`。
            session_id (str): 客户端会话隔离校验唯一标识符。

        Returns:
            Dict[str, Any]: JSON 结构的标准格式响应报文。
            固定结构要求:
            - success (bool): 代表当前请求整体成功或失败的标记状态。
            - message (str): 执行结束对外的结果文字化描述反馈。
            - data (Dict[str, Any], optional): 业务拓展数据承接树层，包含:
                - answer (str): 合并后的直接回答文案。
                - sources (List[str]): 支撑前项回答内容直接参考的原数据库相关段落序列清单。
        """
        pass

    @abstractmethod
    def clear_context(self, session_id: str) -> Dict[str, Any]:
        """
        清空并移除当前指定的全局会话在系统底座所包含有的专有碎片记忆体和检索数据信息。

        Args:
            session_id (str): 客户端会话隔离校验唯一标识符。

        Returns:
            Dict[str, Any]: JSON 结构的标准格式响应报文。
            固定结构要求:
            - success (bool): 代表当前请求整体成功或失败的标记状态。
            - message (str): 执行结束对外的结果文字化描述反馈。
            - data (None): 为空。
        """
        pass
