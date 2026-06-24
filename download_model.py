import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
from huggingface_hub import snapshot_download

# 下载完整6B模型
snapshot_download(
    repo_id="THUDM/chatglm3-6b",
    local_dir="E:/RAG/LLM_QA_System/models/chatglm3-6b",  # 改到E盘
    resume_download=True
)
print("基础模型下载完成！")