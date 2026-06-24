import os
import sys
import threading

os.environ["HF_HUB_DISABLE_SYMLINKS"] = "true"

try:
    from transformers import AutoModel, AutoTokenizer, BitsAndBytesConfig
    import torch
except ImportError as e:
    print(f"导入依赖失败: {e}")
    print("请运行: pip install transformers torch bitsandbytes accelerate")
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOCAL_MODEL_PATH = os.path.join(BASE_DIR, "models", "chatglm3-6b")

_model = None
_tokenizer = None
_lock = threading.Lock()


def load_model():
    """懒加载模型，只在第一次调用时加载"""
    global _model, _tokenizer

    if _model is not None:
        return _model, _tokenizer

    with _lock:
        if _model is not None:
            return _model, _tokenizer

        print("首次加载模型...")

        if not os.path.exists(LOCAL_MODEL_PATH):
            raise FileNotFoundError(f"模型目录不存在: {LOCAL_MODEL_PATH}")

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        print("正在加载Tokenizer...")
        try:
            _tokenizer = AutoTokenizer.from_pretrained(
                LOCAL_MODEL_PATH,
                trust_remote_code=True
            )
        except Exception as e:
            raise RuntimeError(f"加载Tokenizer失败: {e}") from e

        print("正在加载模型(4-bit)...")
        try:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
            )
            _model = AutoModel.from_pretrained(
                LOCAL_MODEL_PATH,
                trust_remote_code=True,
                quantization_config=quantization_config,
                device_map="auto",
                low_cpu_mem_usage=True,
            ).eval()
        except Exception as e:
            raise RuntimeError(f"加载模型失败: {e}") from e

        print("模型加载完成")
        if hasattr(_model, "hf_device_map"):
            print(_model.hf_device_map)

    return _model, _tokenizer


def test_model():
    model, tokenizer = load_model()
    response, history = model.chat(tokenizer, "你好", history=[])
    print("\n回答:", response)


if __name__ == "__main__":
    test_model()
