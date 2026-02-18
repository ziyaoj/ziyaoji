import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Small model configuration (local Qwen2 1.5B for Chinese dialogue)
# Note: Using Qwen2-1.5B-Instruct for better Chinese conversation capabilities
# Qwen2 1.5B is optimized for Chinese dialogue and general Q&A scenarios
SMALL_MODEL_PATH = os.getenv("SMALL_MODEL_PATH", "Qwen/Qwen2-1.5B-Instruct")
SMALL_MODEL_DEVICE = "cpu"  # Use CPU for integrated graphics
SMALL_MODEL_MAX_LENGTH = 512

# Big model configuration (remote Qwen3 API)
BIG_MODEL_API_KEY = os.getenv("QWEN_API_KEY", "")
BIG_MODEL_API_BASE = os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
BIG_MODEL_NAME = os.getenv("QWEN_MODEL_NAME", "qwen-plus")
BIG_MODEL_MAX_TOKENS = 1000
