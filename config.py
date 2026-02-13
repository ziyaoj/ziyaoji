import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Small model configuration (local deepseek 1.5b)
# Note: Using deepseek-coder-1.3b-instruct as it's the closest available distilled model
# DeepSeek 1.5b refers to the model family; the actual model size is 1.3b
SMALL_MODEL_PATH = os.getenv("SMALL_MODEL_PATH", "deepseek-ai/deepseek-coder-1.3b-instruct")
SMALL_MODEL_DEVICE = "cpu"  # Use CPU for integrated graphics
SMALL_MODEL_MAX_LENGTH = 512

# Big model configuration (remote Qwen3 API)
BIG_MODEL_API_KEY = os.getenv("QWEN_API_KEY", "")
BIG_MODEL_API_BASE = os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
BIG_MODEL_NAME = os.getenv("QWEN_MODEL_NAME", "qwen-plus")
BIG_MODEL_MAX_TOKENS = 1000
