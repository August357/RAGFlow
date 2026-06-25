"""独立脚本：分批重建向量库"""
import sys, os, gc

sys.path.append(os.path.dirname(__file__))

from docx2txt import process as docx2txt_process
from pypdf import PdfReader
import pickle

def simple_split_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

print("=" * 60)
print(" 分批重建向量库")
print("=" * 60)

doc_dir = os.path.join(os.path.dirname(__file__), "data", "docs")
files = os.listdir(doc_dir)
print(f"共 {len(files)} 个文件")

# 分批处理
all_docs = []
for filename in files:
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
            chunks = simple_split_text(text, chunk_size=500, overlap=50)
            for chunk in chunks:
                all_docs.append({
                    "content": chunk,
                    "source": filename
                })
            print(f"[OK] {filename}: {len(chunks)} 个 Chunk")
            
            # 释放内存
            del text, chunks
            gc.collect()
            
    except Exception as e:
        print(f"[FAIL] {filename}: {e}")

print(f"\n总计 {len(all_docs)} 个 Chunk")

# 构建向量库（一次传入所有 Chunk）
print("\n构建向量库...")
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import torch

model_name = os.path.join(os.path.dirname(__file__), "models", "bge-base-zh-v1.5")
if not os.path.exists(model_name):
    model_name = "BAAI/bge-base-zh-v1.5"

embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs={"device": "cpu"},  # 用 CPU 避免显存问题
    encode_kwargs={"normalize_embeddings": True}
)

langchain_docs = [
    Document(page_content=d["content"], metadata={"source": d["source"]})
    for d in all_docs
]

# 分批添加文档到 FAISS
print("分批添加文档...")
batch_size = 100
vector_store = None

for i in range(0, len(langchain_docs), batch_size):
    batch = langchain_docs[i:i+batch_size]
    if vector_store is None:
        vector_store = FAISS.from_documents(batch, embeddings)
    else:
        vector_store.add_documents(batch)
    print(f"  已处理 {min(i+batch_size, len(langchain_docs))}/{len(langchain_docs)}")
    
    gc.collect()

# 保存
save_path = os.path.join(os.path.dirname(__file__), "vector_db")
os.makedirs(save_path, exist_ok=True)
vector_store.save_local(save_path)

print(f"\n✓ 向量库重建完成！")
print(f"   Chunk数: {len(all_docs)}")
print(f"   向量数: {vector_store.index.ntotal}")
