"""独立脚本：重建向量库（不使用 langchain_community）"""
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(__file__))

print("=" * 60)
print(" 重建向量库")
print("=" * 60)

# ============================================
# 使用独立的文档加载器
# ============================================
from docx2txt import process as docx2txt_process
from pypdf import PdfReader
import json

def load_documents(doc_dir):
    """加载所有文档（不依赖 langchain_community）"""
    from langchain_core.documents import Document
    
    documents = []
    
    for filename in os.listdir(doc_dir):
        file_path = os.path.join(doc_dir, filename)
        
        try:
            if filename.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                print(f"[OK] {filename}: {len(text)} 字符")
                
            elif filename.endswith('.pdf'):
                reader = PdfReader(file_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                print(f"[OK] {filename}: {len(text)} 字符")
                
            elif filename.endswith('.docx'):
                text = docx2txt_process(file_path)
                print(f"[OK] {filename}: {len(text)} 字符")
                
            else:
                print(f"[SKIP] {filename}: 不支持的文件格式")
                continue
            
            if text.strip():
                doc = Document(
                    page_content=text,
                    metadata={"source": filename}
                )
                documents.append(doc)
                
        except Exception as e:
            print(f"[FAIL] {filename}: {type(e).__name__}: {e}")
    
    print(f"\n总共加载 {len(documents)} 个文档")
    return documents

# ============================================
# 加载文档
# ============================================
print("\n[1/4] 加载文档...")
doc_dir = os.path.join(os.path.dirname(__file__), "data", "docs")
documents = load_documents(doc_dir)

if not documents:
    print("✗ 没有文档可处理，退出")
    sys.exit(1)

# ============================================
# 文本切分
# ============================================
print("\n[2/4] 切分文档...")
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""]
)
split_docs = text_splitter.split_documents(documents)
print(f"切分为 {len(split_docs)} 个 Chunk")

# ============================================
# 生成 Embedding 并构建向量库
# ============================================
print("\n[3/4] 构建向量库...")

# 加载 Embedding 模型
from langchain_huggingface import HuggingFaceEmbeddings
import torch

model_name = os.path.join(os.path.dirname(__file__), "models", "bge-base-zh-v1.5")
if not os.path.exists(model_name):
    model_name = "BAAI/bge-base-zh-v1.5"  # 备用在线路径

print(f"使用 Embedding 模型: {model_name}")

embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs={"device": "cuda" if torch.cuda.is_available() else "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

# 构建 FAISS 向量库
from langchain_community.vectorstores import FAISS

vector_store = FAISS.from_documents(split_docs, embeddings)

# ============================================
# 保存向量库
# ============================================
print("\n[4/4] 保存向量库...")
save_path = os.path.join(os.path.dirname(__file__), "vector_db")
os.makedirs(save_path, exist_ok=True)

vector_store.save_local(save_path)

# 保存 Chunk 信息
chunk_info_path = os.path.join(save_path, "chunk_info.txt")
with open(chunk_info_path, "w", encoding="utf-8") as f:
    for i, doc in enumerate(split_docs):
        f.write(f"{'='*100}\n")
        f.write(f"Chunk {i+1}\n")
        f.write(f"来源: {doc.metadata.get('source', 'unknown')}\n")
        f.write(f"页码:P{doc.metadata.get('page', 1)}\n")
        f.write(f"长度: {len(doc.page_content)}\n")
        f.write(f"\n{doc.page_content}\n\n")

print(f"\n{'='*60}")
print(f" ✓ 向量库重建完成！")
print(f"   文档数: {len(documents)}")
print(f"   Chunk数: {len(split_docs)}")
print(f"   向量数: {vector_store.index.ntotal}")
print(f"   保存路径: {save_path}")
print(f"{'='*60}")
