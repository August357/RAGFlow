from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Depends,
    HTTPException
)
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

from backend.schemas import AskRequest, BuildDBRequest, RegisterRequest, LoginRequest
from backend.system_api import get_system_info
from backend.auth import register_user, authenticate_user, create_access_token, get_current_user, save_chat_history, get_chat_history
from backend.database import get_db
from core.qa_chain import ask
from core.llm import load_model
from core.vector_store import (
    build_vector_db,
    list_knowledge_files,
    preview_file,
    delete_file,
    load_config
)

app = FastAPI()


@app.on_event("startup")
def preload_llm():
    """先加载 LLM，再懒加载 Embedding，避免 Windows 上 4-bit 量化崩溃"""
    print("正在预加载 ChatGLM3-6B 模型...")
    load_model()
    print("ChatGLM3-6B 预加载完成")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# 文档目录
DOCS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "docs"
)


# ==========================
# 问答接口
# ==========================

@app.post("/api/ask")
def ask_api(
    req: AskRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        result = ask(req.query)

        save_chat_history(
            user_id=current_user["user_id"],
            question=req.query,
            answer=result.get("answer", ""),
            sources=result.get("sources", [])
        )

        return result

    except Exception as e:
        import traceback

        print("\n")
        print("=" * 80)
        print("ASK接口异常")
        traceback.print_exc()
        print("=" * 80)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==========================
# 用户注册接口
# ==========================

@app.post("/api/register")
def register(req: RegisterRequest):
    success = register_user(req.username, req.password)
    if success:
        return {"msg": "注册成功"}
    else:
        raise HTTPException(status_code=400, detail="用户名已存在")


# ==========================
# 用户登录接口
# ==========================

@app.post("/api/login")
def login(req: LoginRequest):
    user = authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    access_token = create_access_token(
        data={"sub": user["username"], "user_id": user["user_id"]}
    )

    return {
        "token": access_token,
        "username": user["username"]
    }


# ==========================
# 保存聊天记录接口
# ==========================

@app.post("/api/chat/save")
def save_chat(req: dict, current_user: dict = Depends(get_current_user)):
    success = save_chat_history(
        user_id=current_user["user_id"],
        question=req.get("question"),
        answer=req.get("answer"),
        sources=req.get("sources", [])
    )
    return {"success": success}


# ==========================
# 获取聊天历史接口
# ==========================

@app.get("/api/chat/history")
def get_history(current_user: dict = Depends(get_current_user)):
    history = get_chat_history(current_user["user_id"])
    return {"history": history}


# ==========================
# 配置接口
# ==========================

@app.get("/api/config")
def get_config():
    return load_config()


# 全局变量跟踪构建进度
build_progress = {"progress": 0, "status": "idle"}

# ==========================
# 修改Chunk配置接口
# ==========================

@app.post("/api/build-db")
def build_db(req: BuildDBRequest):
    global build_progress

    # 重置进度
    build_progress = {"progress": 0, "status": "building"}

    try:
        success = build_vector_db(
            chunk_size=req.chunk_size,
            chunk_overlap=req.chunk_overlap,
            split_mode=req.split_mode,
            top_k=req.top_k
        )

        build_progress = {"progress": 100, "status": "completed"}

        return {
            "success": success
        }
    except Exception as e:
        build_progress = {"progress": 0, "status": "failed"}
        raise HTTPException(status_code=500, detail=str(e))


# ==========================
# 获取构建进度接口
# ==========================

@app.get("/api/build-status")
def get_build_status():
    return build_progress


# ==========================
# 文件列表接口
# ==========================

@app.get("/api/files")
def get_files():
    return {
        "files": list_knowledge_files()
    }


# ==========================
# 文件预览接口
# ==========================

@app.get("/api/preview/{filename}")
def preview(filename: str):
    return {
        "content": preview_file(filename)
    }


# ==========================
# 删除文件接口
# ==========================

@app.delete("/api/file/{filename}")
def delete(filename: str):
    result = delete_file(filename)
    return {
        "msg": result
    }


# ==========================
# 上传文件接口
# ==========================

@app.post("/api/upload")
async def upload(file: UploadFile):
    path = os.path.join(DOCS_DIR, file.filename)
    os.makedirs(DOCS_DIR, exist_ok=True)
    
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    return {
        "msg": "上传成功"
    }


# ==========================
# Chunk可视化接口
# ==========================

@app.get("/api/chunks")
def get_chunks(source: str = None):
    """获取 Chunk 信息，按文档分组；可选 source 参数只返回指定文档"""
    from core.vector_store import list_chunks_grouped_by_source

    data = list_chunks_grouped_by_source()
    if not data["documents"]:
        return {
            "documents": [],
            "total": 0,
            "document_count": 0,
            "message": "暂无 Chunk 信息。请先在「配置」页重建向量库。",
        }

    if source:
        matched = [d for d in data["documents"] if d["source"] == source]
        return {
            "documents": matched,
            "total": sum(d["chunk_count"] for d in matched),
            "document_count": len(matched),
        }

    return data


# ==========================
# 系统监控接口
# ==========================

@app.get("/api/system")
def system_info():
    return get_system_info()


# ==========================
# 首页统计接口
# ==========================

@app.get("/api/dashboard")
def dashboard():
    docs_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "docs"
    )

    file_count = 0

    if os.path.exists(docs_dir):
        file_count = len(os.listdir(docs_dir))

    chunk_count = 0

    chunk_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "vector_db",
        "chunk_info.txt"
    )

    if os.path.exists(chunk_path):
        with open(chunk_path, "r", encoding="utf-8") as f:
            text = f.read()
            chunk_count = text.count("Chunk")

    vector_db_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "vector_db",
        "index.faiss"
    )

    return {
        "files": file_count,
        "chunks": chunk_count,
        "model": "ChatGLM3-6B",
        "embedding": "BGE-large-zh",
        "vector_db": os.path.exists(vector_db_path)
    }


# ==========================
# 首页详情接口（加分项）
# ==========================

@app.get("/api/dashboard-detail")
def dashboard_detail():
    docs_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "docs"
    )

    recent_files = []
    if os.path.exists(docs_dir):
        files = os.listdir(docs_dir)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(docs_dir, x)), reverse=True)
        recent_files = files[:5]

    faiss_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "vector_db",
        "index.faiss"
    )

    faiss_size = "0MB"
    if os.path.exists(faiss_path):
        size = os.path.getsize(faiss_path)
        faiss_size = f"{round(size / 1024**2, 2)}MB"

    return {
        "recent_files": recent_files,
        "faiss_size": faiss_size,
        "questions": 0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
