# RAGFlow

基于 RAG 的智能问答系统，支持 PDF/Word 文档检索与 ChatGLM3-6B 本地问答。

## 功能特性

- 文档加载与分块（PDF、Word、TXT）
- FAISS 向量检索 + BGE 重排序
- ChatGLM3-6B 4-bit 本地推理
- Vue3 前端：对话、知识库、Chunk 可视化、PDF 导出

## 项目结构

```
LLM_QA_System/
├── backend/          # FastAPI 后端
├── core/             # RAG 核心（向量库、LLM、问答链）
├── frontend/         # Vue3 前端
├── data/docs/        # 本地文档目录（不上传，见 data/docs/README.md）
├── models/           # 本地模型（需自行下载，见 models/README.md）
├── vector_db/        # 向量库（运行后生成）
├── download_models.py
├── rebuild_db_v3.py
└── requirements.txt
```

## 环境要求

- Python 3.10+
- Node.js 18+
- NVIDIA GPU（推荐 8GB+ 显存，用于 4-bit ChatGLM3-6B）

## 快速开始

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 下载模型

```bash
python download_models.py
```

详见 [models/README.md](models/README.md)。

### 3. 构建向量库

将文档放入 `data/docs/` 后执行：

```bash
python rebuild_db_v3.py
```

### 4. 启动服务

```bash
# 后端
uvicorn backend.main:app --host 127.0.0.1 --port 8000

# 前端（新终端）
cd frontend
npm install
npm run dev
```

浏览器访问前端开发地址（默认 `http://localhost:5173`）。

## 说明

- **模型文件**、**知识库文档**、**向量库**、**node_modules** 已加入 `.gitignore`，不会上传到 GitHub
- 克隆仓库后需按上述步骤下载模型、放入文档并重建向量库
