import streamlit as st
from core.interfaces import LLMConfig, EmbedConfig
from core.rag_backend import LangChainRAGBackend

st.set_page_config(page_title="RAG Search | 配置", page_icon="·", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.page-title { font-size: 1.4rem; font-weight: 600; color: #1a202c; margin-bottom: 0.2rem; }
.page-subtitle { font-size: 0.88rem; color: #718096; margin-bottom: 1.2rem; }
.field-label { font-size: 0.8rem; font-weight: 500; color: #4a5568; margin-bottom: 0.2rem; }
</style>
""", unsafe_allow_html=True)

# ── 持久化 Backend 实例 ─────────────────────────────────────────────
if "backend" not in st.session_state:
    st.session_state.backend = LangChainRAGBackend()

# ── 持久化配置字段（切换页面后保留） ──────────────────────────────────
# 使用独立 session_state key，与 widget key 分离，确保跨页导航不丢失
_cfg_defaults = {
    "cfg_llm_base_url":  "",
    "cfg_llm_api_key":   "",
    "cfg_llm_model":     "gpt-3.5-turbo",
    "cfg_emb_base_url":  "",
    "cfg_emb_api_key":   "",
    "cfg_emb_model":     "text-embedding-ada-002",
}
for _k, _v in _cfg_defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── 页面标题 ────────────────────────────────────────────────────────
st.markdown('<div class="page-title">服务配置</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">配置 LLM 与 Embedding 服务，完成后初始化后端。</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

# ══════════════════════════════════════════════════════════════════
# LLM 配置列
# ══════════════════════════════════════════════════════════════════
with col1:
    st.markdown("**LLM 配置**")
    st.caption("支持 OpenAI 兼容协议（OpenAI、DeepSeek、硅基流动、阿里云百炼等）")

    llm_base_url = st.text_input(
        "Base URL（留空使用 OpenAI 官方地址）",
        value=st.session_state.cfg_llm_base_url,
        placeholder="https://api.example.com/v1",
        key="_w_llm_base_url"
    )
    llm_api_key = st.text_input(
        "API Key",
        value=st.session_state.cfg_llm_api_key,
        type="password",
        placeholder="sk-...",
        key="_w_llm_api_key"
    )
    llm_model = st.text_input(
        "Model Name",
        value=st.session_state.cfg_llm_model,
        placeholder="gpt-3.5-turbo",
        key="_w_llm_model"
    )

    # 同步到持久化 key
    st.session_state.cfg_llm_base_url = llm_base_url
    st.session_state.cfg_llm_api_key  = llm_api_key
    st.session_state.cfg_llm_model    = llm_model

    if st.button("测试 LLM 连通性", use_container_width=True):
        with st.spinner("连接中..."):
            ok = st.session_state.backend.ping_llm(LLMConfig(
                base_url=llm_base_url or None,
                api_key=llm_api_key,
                model_name=llm_model
            ))
        if ok:
            st.success("LLM 连通正常")
        else:
            st.error("LLM 连接失败，请检查配置")

# ══════════════════════════════════════════════════════════════════
# Embedding 配置列
# ══════════════════════════════════════════════════════════════════
with col2:
    st.markdown("**Embedding 配置**")
    st.caption("支持 OpenAI 兼容协议（OpenAI、智谱、阿里云百炼等）")

    emb_base_url = st.text_input(
        "Base URL（留空使用 OpenAI 官方地址）",
        value=st.session_state.cfg_emb_base_url,
        placeholder="https://api.example.com/v1",
        key="_w_emb_base_url"
    )
    emb_api_key = st.text_input(
        "API Key",
        value=st.session_state.cfg_emb_api_key,
        type="password",
        placeholder="sk-...",
        key="_w_emb_api_key"
    )
    emb_model = st.text_input(
        "Model Name",
        value=st.session_state.cfg_emb_model,
        placeholder="text-embedding-ada-002",
        key="_w_emb_model"
    )

    # 同步到持久化 key
    st.session_state.cfg_emb_base_url = emb_base_url
    st.session_state.cfg_emb_api_key  = emb_api_key
    st.session_state.cfg_emb_model    = emb_model

    if st.button("测试 Embedding 连通性", use_container_width=True):
        with st.spinner("连接中..."):
            ok = st.session_state.backend.ping_embedding(EmbedConfig(
                base_url=emb_base_url or None,
                api_key=emb_api_key,
                model_name=emb_model
            ))
        if ok:
            st.success("Embedding 连通正常")
        else:
            st.error("Embedding 连接失败，请检查配置")

st.divider()

# ══════════════════════════════════════════════════════════════════
# 初始化 Backend
# ══════════════════════════════════════════════════════════════════
backend = st.session_state.backend
is_initialized = backend.llm is not None and backend.embeddings is not None

if is_initialized:
    st.success("后端已初始化，可前往知识库管理上传文档。")

if st.button("初始化后端", type="primary", use_container_width=True):
    with st.spinner("正在初始化..."):
        ok = backend.initialize(
            LLMConfig(
                base_url=llm_base_url or None,
                api_key=llm_api_key,
                model_name=llm_model
            ),
            EmbedConfig(
                base_url=emb_base_url or None,
                api_key=emb_api_key,
                model_name=emb_model
            )
        )
    if ok:
        st.success("后端初始化成功，可前往知识库管理上传文档。")
    else:
        st.error("初始化失败，请检查配置后重试。")

st.divider()

st.markdown("**知识库管理**")
st.caption(f"当前已入库 {backend._chunk_count} 个 Chunk，索引状态：{'就绪' if backend.vector_store else '空库'}")
if st.button("清空知识库（释放内存）"):
    backend.clear_index()
    st.success("知识库已清空。")
    st.rerun()
