# Streamlit RAG 搜索引擎项目 (RagSearch)

RagSearch 是一个基于 Streamlit 和 LangChain 构建的本地化 RAG (Retrieval-Augmented Generation) 文档问答工具。

项目包含上传 PDF文件，对其进行切片、向量化计算，然后响应用户的问题的能力。

---

## 📂 项目结构说明

- `app.py`: **前端交互层**，构建基于 Streamlit 的交互页面、会话状态流转与系统主调入口。
- `core/`: **底层服务层**，完全独立解耦的 AI 算法后端与 RAG 核心逻辑组块。
  - `interfaces.py`: 定义标准通信契约定义的抽象基类，规范统一的响应体及调用参数保障机制。
  - `rag_backend.py`: 具体核心逻辑承接类，专注于底层向量引擎连接及对话推理拼合检索实作。
- `.env`: **个人变量文件**，存放 `API_KEY` 等敏感资产（**警告：本项目已将其在 `.gitignore` 忽略，请绝对不要推送到代码库**）。
- `requirements.txt`: 统一的库框架及版本清单。

---

## ⚡ 快速开始指南

### 1. 准备并隔离开发环境
强烈建议创建一个全新的 Python 虚拟环境以避免依赖包冲突（基于 Python 3.10+）：

**在 Windows PowerShell 中：**
```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\activate
```

*(在 Mac/Linux 下激活命令为: `source venv/bin/activate`)*

### 2. 安装项目依赖
当你激活完虚拟环境后（终端前面会看到 `(venv)` 字样），安装本项目的依赖：
```powershell
pip install -r requirements.txt
```

### 3. 运行服务
项目开发完毕后，确保在项目根目录 `RagSearch/` 之下，运行以下 Streamlit 引擎指令：
```powershell
streamlit run app.py
```

终端运行后，浏览器会自动打开 `http://localhost:8501`。你的页面即部署成功！

---

## 🤝 开发协作提示
如果有新的包需要安装，请运行 `pip install <包名>` 后，务必将其版本号及时同步至 `requirements.txt` 以免造成其他成员环境错误。
