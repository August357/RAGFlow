"""
FastAPI 路由模块
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
import os
import shutil

from backend.schemas import (
    ChatRequest, ChatResponse,
    UploadResponse, RebuildResponse,
    FileListResponse, DeleteResponse,
    PreviewResponse, ChunksResponse,
    StatusResponse, SystemInfoResponse,
    MessageResponse
)

# 导入核心模块
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.qa_chain import ask
from core.vector_store import (
    build_vector_db, list_knowledge_files,
    delete_file, preview_file, load_config
)
from core.llm import load_model
import torch

# 创建路由器
router = APIRouter(prefix="/api", tags=["RAG"])

# ==========================
# 系统状态
# ==========================

@router.get("/status", response_model=StatusResponse)
async def get_status():
    """获取系统状态"""
    try:
        # 检查向量库
        vector_db_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "vector_db"
        )
        vector_db_exists = os.path.exists(vector_db_path)
        
        # 获取配置
        config = load_config()
        
        # 统计文件和Chunk
        files = list_knowledge_files()
        
        # 估算Chunk数量（从配置或向量库）
        total_chunks = 0
        if vector_db_exists:
            try:
                from core.vector_store import load_vector_store
                vs = load_vector_store()
                if vs:
                    total_chunks = vs.index.ntotal if hasattr(vs.index, 'ntotal') else 0
            except:
                pass
        
        return StatusResponse(
            status="ready" if vector_db_exists else "loading",
            model_loaded=False,  # 懒加载，实际调用时才加载
            vector_db_exists=vector_db_exists,
            total_chunks=total_chunks,
            total_files=len(files)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system", response_model=SystemInfoResponse)
async def get_system_info():
    """获取系统信息"""
    try:
        return SystemInfoResponse(
            model_name="ChatGLM3-6B",
            embedding_model="BGE-small-zh-v1.5",
            device="cuda" if torch.cuda.is_available() else "cpu",
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            pytorch_version=torch.__version__
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================
# 问答接口
# ==========================

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """问答接口"""
    try:
        result = ask(request.query, request.use_reranker)
        return ChatResponse(
            answer=result.get("answer", "回答失败"),
            sources=result.get("sources", []),
            context_length=result.get("context_length", 0),
            retrieved_docs=result.get("retrieved_docs", 0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答失败: {str(e)}")


@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    """问答接口（兼容 /api/ask）"""
    try:
        result = ask(request.query, request.use_reranker)
        return ChatResponse(
            answer=result.get("answer", "回答失败"),
            sources=result.get("sources", []),
            context_length=result.get("context_length", 0),
            retrieved_docs=result.get("retrieved_docs", 0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答失败: {str(e)}")


# ==========================
# 文件管理
# ==========================

@router.get("/files", response_model=FileListResponse)
async def list_files():
    """获取知识库文件列表"""
    try:
        files = list_knowledge_files()
        return FileListResponse(files=files, total=len(files))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/file/{filename}", response_model=DeleteResponse)
async def delete_file_api(filename: str):
    """删除知识库文件"""
    try:
        result = delete_file(filename)
        success = "成功" in result
        return DeleteResponse(message=result, success=success)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preview/{filename}", response_model=PreviewResponse)
async def preview_file_api(filename: str):
    """预览文件内容"""
    try:
        content = preview_file(filename)
        return PreviewResponse(
            content=content,
            filename=filename,
            length=len(content)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================
# 文件上传
# ==========================

@router.post("/upload", response_model=UploadResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    """上传知识库文件"""
    try:
        # 目标目录
        save_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "docs"
        )
        os.makedirs(save_dir, exist_ok=True)
        
        uploaded_count = 0
        for file in files:
            file_path = os.path.join(save_dir, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            uploaded_count += 1
        
        # 重建向量库
        build_vector_db()
        
        return UploadResponse(
            message=f"成功上传 {uploaded_count} 个文件",
            success=True,
            files_uploaded=uploaded_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


# ==========================
# 向量库管理
# ==========================

@router.post("/rebuild", response_model=RebuildResponse)
async def rebuild_vector_db(request: RebuildRequest):
    """重建向量库"""
    try:
        result = build_vector_db(
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            split_mode=request.split_mode,
            top_k=request.top_k
        )
        
        if result:
            # 获取Chunk数量
            from core.vector_store import load_vector_store
            vs = load_vector_store()
            total_chunks = vs.index.ntotal if vs and hasattr(vs.index, 'ntotal') else 0
            
            return RebuildResponse(
                message="向量库重建成功",
                success=True,
                total_chunks=total_chunks
            )
        else:
            return RebuildResponse(
                message="向量库重建失败",
                success=False,
                total_chunks=0
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重建失败: {str(e)}")


# ==========================
# Chunk管理
# ==========================

@router.get("/chunks", response_model=ChunksResponse)
async def get_chunks():
    """获取所有Chunk信息"""
    try:
        chunk_info_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "vector_db",
            "chunk_info.txt"
        )
        
        if not os.path.exists(chunk_info_path):
            return ChunksResponse(chunks=[], total=0)
        
        chunks = []
        with open(chunk_info_path, "r", encoding="utf-8") as f:
            content = f.read()
            # 解析Chunk信息
            chunk_blocks = content.split("=" * 100)
            for block in chunk_blocks:
                if not block.strip():
                    continue
                lines = block.strip().split("\n")
                if len(lines) < 4:
                    continue
                
                # 解析元数据
                chunk_id = 0
                source = ""
                page = 1
                length = 0
                preview = ""
                
                for i, line in enumerate(lines):
                    if line.startswith("Chunk "):
                        chunk_id = int(line.split()[1])
                    elif line.startswith("来源:"):
                        source = line.split(":", 1)[1].strip()
                    elif line.startswith("页码:P"):
                        page = int(line.split("P")[1])
                    elif line.startswith("长度:"):
                        length = int(line.split(":")[1].strip())
                    elif i >= 4:  # 内容行
                        preview += line + "\n"
                
                if chunk_id > 0:
                    chunks.append(ChunkInfo(
                        chunk_id=chunk_id,
                        source=source,
                        page=page,
                        length=length,
                        preview=preview[:200]  # 预览前200字符
                    ))
        
        return ChunksResponse(chunks=chunks, total=len(chunks))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chunks/search")
async def search_chunks(keyword: str = ""):
    """搜索Chunk"""
    try:
        chunk_info_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "vector_db",
            "chunk_info.txt"
        )
        
        if not os.path.exists(chunk_info_path):
            return {"chunks": [], "total": 0}
        
        chunks = []
        with open(chunk_info_path, "r", encoding="utf-8") as f:
            content = f.read()
            chunk_blocks = content.split("=" * 100)
            for block in chunk_blocks:
                if not block.strip():
                    continue
                if keyword and keyword.lower() not in block.lower():
                    continue
                
                lines = block.strip().split("\n")
                if len(lines) < 4:
                    continue
                
                chunk_id = 0
                source = ""
                page = 1
                length = 0
                preview = ""
                
                for i, line in enumerate(lines):
                    if line.startswith("Chunk "):
                        chunk_id = int(line.split()[1])
                    elif line.startswith("来源:"):
                        source = line.split(":", 1)[1].strip()
                    elif line.startswith("页码:P"):
                        page = int(line.split("P")[1])
                    elif line.startswith("长度:"):
                        length = int(line.split(":")[1].strip())
                    elif i >= 4:
                        preview += line + "\n"
                
                if chunk_id > 0:
                    chunks.append({
                        "chunk_id": chunk_id,
                        "source": source,
                        "page": page,
                        "length": length,
                        "preview": preview[:200]
                    })
        
        return {"chunks": chunks, "total": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
