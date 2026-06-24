"""独立脚本：重建向量库 - V2（备用切分器）"""
import sys
import os

sys.path.append(os.path.dirname(__file__))

print("=" * 60)
print(" 重建向量库 V2")
print("=" * 60)

# ============================================
# 加载文档
# ============================================
from docx2txt import process as docx2txt_process
from pypdf import PdfReader

def simple_split_text(text, chunk_size=500, overlap=50):
    """简单文本切分"""
    chunks = []
    total = len(text)
    start = 0
    i = 0
    while start < total:
        end = min(start + chunk_size, total)
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        i += 1
        if i % 50 == 0:
            print(f"  已切分 {i} 个 Chunk... (进度: {start}/{total})")
    return chunks

def load_documents(doc_dir):
    """加载文档"""
    documents = []
    for filename in os.listdir(doc_dir):
        file_path = os.path.join(doc_dir, filename)
        try:
            if filename.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            elif filename.endswith('.pdf'):
                reader = PdfReader(file_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
            elif filename.endswith('.docx'):
                text = docx2txt_process(file_path)
            else:
                continue
            
            if text.strip():
                documents.append({
                    "text": text,
                    "source": filename,
                    "length": len(text)
                })
                print(f"[OK] {filename}: {len(text)} 字符")
        except Exception as e:
            print(f"[FAIL] {filename}: {e}")
    
    return documents

# ============================================
# 主流程
# ============================================
print("\n[1/3] 加载文档...")
doc_dir = os.path.join(os.path.dirname(__file__), "data", "docs")
documents = load_documents(doc_dir)
print(f"加载 {len(documents)} 个文档")

if not documents:
    print("✗ 没有文档")
    sys.exit(1)

print("\n[2/3] 切分文档...")
all_chunks = []
for doc in documents:
    chunks = simple_split_text(doc["text"], chunk_size=500, overlap=50)
    for i, chunk in enumerate(chunks):
        all_chunks.append({
            "content": chunk,
            "metadata": {
                "source": doc["source"],
                "chunk_id": i + 1,
                "page": 1
            }
        })
print(f"切分为 {len(all_chunks)} 个 Chunk")

print("\n[3/3] 构建向量库...")
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import torch

# Embedding 模型
model_name = os.path.join(os.path.dirname(__file__), "models", "bge-base-zh-v1.5")
if not os.path.exists(model_name):
    model_name = "BAAI/bge-base-zh-v1.5"

print(f"Embedding 模型: {model_name}")
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs={"device": "cuda" if torch.cuda.is_available() else "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

# 转换为 LangChain Document
langchain_docs = [
    Document(page_content=c["content"], metadata=c["metadata"])
    for c in all_chunks
]

# 构建 FAISS
print("正在生成向量...")
vector_store = FAISS.from_documents(langchain_docs, embeddings)

# 保存
save_path = os.path.join(os.path.dirname(__file__), "vector_db")
os.makedirs(save_path, exist_ok=True)
vector_store.save_local(save_path)

# 保存 Chunk 信息
with open(os.path.join(save_path, "chunk_info.txt"), "w", encoding="utf-8") as f:
    for i, chunk in enumerate(all_chunks):
        f.write(f"{'='*100}\n")
        f.write(f"Chunk {i+1}\n")
        f.write(f"来源: {chunk['metadata']['source']}\n")
        f.write(f"页码:P{chunk['metadata']['page']}\n")
        f.write(f"长度: {len(chunk['content'])}\n")
        f.write(f"\n{chunk['content']}\n\n")

print(f"\n{'='*60}")
print(f" ✓ 向量库重建完成！")
print(f"   文档数: {len(documents)}")
print(f"   Chunk数: {len(all_chunks)}")
print(f"   向量数: {vector_store.index.ntotal}")
print(f"{'='*60}")
