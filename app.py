import os
import uuid
import streamlit as st
from dotenv import load_dotenv
from core.rag_backend import RAGBackend

load_dotenv()

st.set_page_config(page_title="RagSearch", layout="wide")
st.title("Streamlit RAG Search")

# 实例化依赖并配置全局缓存
@st.cache_resource
def get_shared_backend() -> RAGBackend:
    """获取 RAG 后端全局单例服务实例。"""
    return RAGBackend()

backend = get_shared_backend()

# 会话状态变量构建
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())


# 控件区划分：侧边栏及管理入口
with st.sidebar:
    st.header("1. 上传检索文档")
    uploaded_file = st.file_uploader("支持文档集", type=["pdf", "docx"])
    
    if uploaded_file is not None:
        if st.button("提交知识文档构建"):
            with st.spinner("系统处理中..."):
                response = backend.upload_file(
                    file_bytes=uploaded_file.getvalue(), 
                    file_name=uploaded_file.name,
                    session_id=st.session_state.session_id
                )
                
                if response.get("success", False):
                    st.success(response.get("message", "文档处理完成。"))
                else:
                    st.error(response.get("message", "文档处理失败。"))
    
    st.divider()
    
    if st.button("清空独立状态上下文"):
        response = backend.clear_context(session_id=st.session_state.session_id)
        if response.get("success", False):
            st.session_state.chat_history = []
            st.success("指定上下文存储已注销回收清理。")
        else:
            st.error(response.get("message", "清空任务触发异常阻断。"))

# 控件区划分：主要消息响应对答视窗
st.header("2. 探索交互窗口")

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("发入指令或查询请求...")
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("队列请求推断中..."):
            response = backend.ask_question(
                question=user_input, 
                chat_history=st.session_state.chat_history,
                session_id=st.session_state.session_id
            )
            
            if response.get("success", False):
                data = response.get("data", {})
                answer_text = data.get("answer", "文本实体结构回拉获取失效。")
                
                st.markdown(answer_text)
                
                sources = data.get("sources", [])
                if sources:
                    with st.expander("辅助说明与文档碎片关联参考", expanded=False):
                        for idx, source_txt in enumerate(sources):
                            st.caption(f"[{idx+1}] {source_txt}")
                            
                st.session_state.chat_history.append({"role": "assistant", "content": answer_text})
            else:
                st.error(response.get("message", "业务组件响应获取未知系统故障拦截器。"))
