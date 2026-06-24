"""下载项目所需的 HuggingFace 模型到 models/ 目录"""

import os
from pathlib import Path

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

from huggingface_hub import snapshot_download

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

MODELS = [
    ("THUDM/chatglm3-6b", MODELS_DIR / "chatglm3-6b"),
    ("BAAI/bge-small-zh-v1.5", MODELS_DIR / "bge-small-zh-v1.5"),
    ("BAAI/bge-reranker-base", MODELS_DIR / "bge-reranker-base"),
]


def main():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    for repo_id, local_dir in MODELS:
        print(f"正在下载 {repo_id} -> {local_dir}")
        snapshot_download(repo_id=repo_id, local_dir=str(local_dir), resume_download=True)
        print(f"  完成: {local_dir.name}")
    print("全部模型下载完成！")


if __name__ == "__main__":
    main()
