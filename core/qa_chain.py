"""
RAG问答链核心模块
整合检索、重排序、Prompt构建和LLM调用
"""

import os
import gc
import json
import torch

from langchain_community.vectorstores import FAISS

from core.llm import load_model
from core.prompt import prompt_builder
from core.vector_store import get_embedding_model, VECTOR_DB_PATH

# ============================================
# 项目根目录
# ============================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================================
# 关闭HF联网警告
# ============================================

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "true"

# ============================================
# Reranker模型（懒加载）
# ============================================

_reranker = None

def load_reranker():
    """懒加载BGE-Reranker模型"""
    global _reranker
    if _reranker is not None:
        return _reranker
    
    try:
        from FlagEmbedding import FlagReranker
        print("正在加载BGE-Reranker...")
        
        import os as _os
        local_model = _os.path.join(_os.path.dirname(__file__), "..", "models", "bge-reranker-base")
        local_model = _os.path.abspath(local_model)
        
        if _os.path.exists(local_model):
            model_path = local_model
            print(f"使用本地Reranker: {model_path}")
        else:
            model_path = "BAAI/bge-reranker-base"
            print("本地模型不存在，使用在线模型")
        
        _reranker = FlagReranker(
            model_path,
            use_fp16=torch.cuda.is_available(),
            device="cuda" if torch.cuda.is_available() else "cpu"
        )
        print("BGE-Reranker加载成功！")
        return _reranker
    except ImportError:
        print("FlagEmbedding未安装，跳过Reranker")
        return None
    except Exception as e:
        print(f"加载Reranker失败: {e}")
        return None

# ============================================
# 动态加载向量库
# ============================================

def load_vector_store():
    """加载FAISS向量库"""
    return FAISS.load_local(
        VECTOR_DB_PATH,
        get_embedding_model(),
        allow_dangerous_deserialization=True
    )

# ============================================
# 文档检索（使用MMR，支持动态TopK）
# ============================================

def retrieve(query: str, top_k: int = None) -> list:
    """
    使用相似度检索并过滤低匹配文档
    
    Args:
        query: 用户查询
        top_k: 返回数量（可选，默认从配置文件读取）
        
    Returns:
        list: 检索到的文档列表
    """
    vector_store = load_vector_store()

    docs_with_scores = vector_store.similarity_search_with_score(
        query,
        k=10
    )

    if top_k is None:
        config_path = os.path.join(BASE_DIR, "vector_db", "config.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        else:
            config = {"top_k": 5}
        top_k = config.get("top_k", 5)

    # BGE 归一化向量下 L2 距离越小越相似；0.6 过严会漏掉相关文档
    max_distance = 1.2
    docs = [doc for doc, score in docs_with_scores if score < max_distance]

    if not docs:
        docs = [doc for doc, _ in docs_with_scores[:top_k]]

    return docs[:top_k]

# ============================================
# Reranker重排序
# ============================================

# BGE-Reranker 分数低于此阈值视为与知识库无关（cross-encoder logits）
RERANK_MIN_SCORE = -0.5


def rerank(query: str, docs: list, top_n: int = 3) -> list:
    """
    使用BGE-Reranker对检索结果重排序，并过滤低相关度文档
    
    Args:
        query: 用户查询
        docs: 检索到的文档列表
        top_n: 返回前N个
    
    Returns:
        list: 重排序后的文档列表；全部不相关时返回空列表
    """
    if not docs:
        return []

    reranker = load_reranker()
    if not reranker:
        return docs[:top_n]

    pairs = [(query, doc.page_content) for doc in docs]
    scores = reranker.compute_score(pairs)
    if not isinstance(scores, list):
        scores = [scores]

    scored_docs = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
    best_score = scored_docs[0][1]
    print(f"Reranker 最佳分数: {best_score:.3f} (阈值: {RERANK_MIN_SCORE})")

    if best_score < RERANK_MIN_SCORE:
        print("【相关性过滤】判定与知识库无关，不引用任何文档")
        return []

    min_score = max(best_score - 2.0, RERANK_MIN_SCORE)
    filtered = [doc for doc, score in scored_docs if score >= min_score]
    return filtered[:top_n]


def _call_llm_direct(query: str) -> str:
    """不基于知识库，直接调用 LLM"""
    global _reranker
    _reranker = None
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    model, tokenizer = load_model()
    response, _ = model.chat(tokenizer, query, history=[])
    return response

# ============================================
# 主问答函数
# ============================================

def ask(query: str, use_reranker: bool = True) -> dict:
    """
    主问答函数
    
    Args:
        query: 用户问题
        use_reranker: 是否使用Reranker
    
    Returns:
        dict: {answer, sources, context_length, retrieved_docs}
    """
    global _reranker
    print(f"\n===== 问题: {query} =====")

    chat_keywords = [
        "你好",
        "您好",
        "谢谢",
        "再见",
        "你是谁",
        "介绍一下你"
    ]

    if query.strip() in chat_keywords:
        print("\n【闲聊模式】直接调用LLM")
        response = _call_llm_direct(query)
        return {
            "answer": response,
            "sources": [],
            "context_length": 0,
            "retrieved_docs": 0
        }
    
    # 1. 检索文档（使用MMR）
    print("\n【步骤1】检索文档...")
    raw_docs = retrieve(query)
    print(f"检索到 {len(raw_docs)} 个文档")
    
    # 2. Reranker重排序
    if use_reranker:
        print("\n【步骤2】Reranker重排序...")
        docs = rerank(query, raw_docs)
        print(f"重排序后保留 {len(docs)} 个文档")
    else:
        docs = raw_docs
    
    # 3. 无相关文档：通用 LLM 回答，不展示来源
    if not docs:
        print("\n【通用模式】知识库无相关内容，直接调用 LLM（不引用来源）")
        response = _call_llm_direct(query)
        return {
            "answer": response,
            "sources": [],
            "context_length": 0,
            "retrieved_docs": 0
        }
    
    # 4. 输出检索结果（调试）
    print("\n【步骤3】检索结果详情：")
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "未知来源")
        chunk_id = doc.metadata.get("chunk_id", i + 1)
        page = doc.metadata.get("page", "未知")
        print(f"\n【文档 {i+1}】{source} (P{page} Chunk{chunk_id})")
        print(f"内容预览：{doc.page_content[:150]}...")
        print("-" * 60)
    
    # 5. 构建Prompt（使用统一的PromptBuilder）
    print("\n【步骤4】构建Prompt...")
    prompt_result = prompt_builder.build_rag_prompt(query, docs)
    prompt = prompt_result["prompt"]
    sources = prompt_result["sources"]
    context_length = prompt_result["context_length"]
    print(f"上下文长度: {context_length} 字符")
    
    # 5. 调用LLM（释放 Reranker 占用的显存）
    print("\n【步骤5】调用LLM...")
    print("=== 进入LLM调用前 ===")
    response = _call_llm_direct(prompt)
    
    print("=== 回答完成 ===")
    
    print("\n【步骤6】回答完成！")
    
    return {
        "answer": response,
        "sources": sources,
        "context_length": context_length,
        "retrieved_docs": len(docs)
    }


# ============================================
# 测试函数
# ============================================

def test_qa():
    """测试问答功能"""
    result = ask("什么是人工智能？")
    print("\n" + "="*50)
    print("最终回答：")
    print(result["answer"])


if __name__ == "__main__":
    test_qa()
