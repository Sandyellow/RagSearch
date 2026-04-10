import streamlit as st
import time
from core.interfaces import LLMConfig, EmbedConfig
from core.rag_backend import LangChainRAGBackend

st.set_page_config(page_title="RAG Backend Test", layout="wide")

st.title("🧩 RAG Backend Integration Test")
st.markdown("配置并验证不同组件的连通性。")

if 'backend' not in st.session_state:
    st.session_state.backend = LangChainRAGBackend()

col1, col2 = st.columns(2)

with col1:
    st.subheader("LLM 配置")
    st.info("仅支持 **OpenAI 兼容协议**（官方 OpenAI、硅基流动、DeepSeek、智谱、阿里云百炼等国产代理均适用）")
    llm_base_url = st.text_input("Base URL（留空使用 OpenAI 官方地址）", key="llm_base_url")
    llm_api_key = st.text_input("API Key", type="password", key="llm_api_key")
    llm_model_name = st.text_input("Model Name", value="gpt-3.5-turbo", key="llm_model")

    if st.button("测试 LLM 连通性"):
        config = LLMConfig(
            base_url=llm_base_url if llm_base_url else None,
            api_key=llm_api_key,
            model_name=llm_model_name
        )
        with st.spinner("Ping..."):
            if st.session_state.backend.ping_llm(config):
                st.success("✅ LLM 测试成功！")
            else:
                st.error("❌ LLM 测试失败，请检查配置。")

with col2:
    st.subheader("Embedding 配置")
    st.info("仅支持 **OpenAI 兼容协议**（官方 OpenAI、智谱、阿里云百炼等国产代理均适用）")
    emb_base_url = st.text_input("Base URL（留空使用 OpenAI 官方地址）", key="emb_base_url")
    emb_api_key = st.text_input("API Key", type="password", key="emb_api_key")
    emb_model_name = st.text_input("Model Name", value="text-embedding-ada-002", key="emb_model")

    if st.button("测试 Embedding 连通性"):
        config = EmbedConfig(
            base_url=emb_base_url if emb_base_url else None,
            api_key=emb_api_key,
            model_name=emb_model_name
        )
        with st.spinner("Ping..."):
            if st.session_state.backend.ping_embedding(config):
                st.success("✅ Embedding 测试成功！")
            else:
                st.error("❌ Embedding 测试失败，请检查配置。")

st.divider()
st.subheader("初始化验证")
if st.button("一键初始化 Backend", type="primary", use_container_width=True):
    llm_config = LLMConfig(
        base_url=llm_base_url if llm_base_url else None,
        api_key=llm_api_key,
        model_name=llm_model_name
    )
    emb_config = EmbedConfig(
        base_url=emb_base_url if emb_base_url else None,
        api_key=emb_api_key,
        model_name=emb_model_name
    )
    
    with st.spinner("正在全局初始化..."):
        if st.session_state.backend.initialize(llm_config, emb_config):
            st.success("🎉 Backend 初始化成功！各个组件已就绪，内存型 FAISS 已准备。")
        else:
            st.error("❌ Backend 初始化失败。")

st.divider()
st.subheader("内存数据库管理")
if st.button("🗑️ 清空当前用户的知识库内存"):
    st.session_state.backend.clear_index()
    st.success("已成功释放内存，清空临时索引。")
