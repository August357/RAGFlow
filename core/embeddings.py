import os
from langchain_huggingface import HuggingFaceEmbeddings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EMBEDDING_MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "bge-small-zh-v1.5"
)

def load_embedding_model(device="cpu"):
    """加载Embedding模型"""
    print("正在加载Embedding模型...")
    embedding_model = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_PATH,
        model_kwargs={
            "device": device
        },
        encode_kwargs={
            "normalize_embeddings": True
        }
    )
    print("Embedding模型加载成功！")
    return embedding_model

embeddings = load_embedding_model()
