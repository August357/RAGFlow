import os
from sentence_transformers import SentenceTransformer

# 使用绝对路径
model_path = os.path.join(os.path.dirname(__file__), "models", "bge-small-zh-v1.5")
model_path = os.path.abspath(model_path)

print(f"模型路径: {model_path}")
print(f"路径存在: {os.path.exists(model_path)}")

model = SentenceTransformer(model_path, device="cpu")
print("加载成功")
