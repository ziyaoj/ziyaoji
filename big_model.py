import time
from openai import OpenAI
from config import BIG_MODEL_API_KEY, BIG_MODEL_API_BASE, BIG_MODEL_NAME, BIG_MODEL_MAX_TOKENS

# 全局变量，延迟创建客户端
_client = None

def _get_client():
    """懒加载OpenAI客户端"""
    global _client
    if _client is None:
        if not BIG_MODEL_API_KEY:
            raise ValueError("未配置QWEN_API_KEY，请在.env文件中配置或设置环境变量")
        _client = OpenAI(
            api_key=BIG_MODEL_API_KEY,
            base_url=BIG_MODEL_API_BASE
        )
    return _client

def big_model_answer(question: str) -> str:
    """使用远程Qwen3大模型API回答问题"""
    try:
        client = _get_client()
        
        # 调用Qwen API
        response = client.chat.completions.create(
            model=BIG_MODEL_NAME,
            messages=[
                {"role": "system", "content": "你是一个校园问答助手，请准确、详细地回答学生的问题。"},
                {"role": "user", "content": question}
            ],
            max_tokens=BIG_MODEL_MAX_TOKENS,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content.strip()
        return answer if answer else "大模型未返回有效回答"
        
    except Exception as e:
        print(f"大模型API调用错误: {e}")
        # 降级到简单回答
        time.sleep(0.2)
        return f"[大模型] 关于'{question}'，这是一个复杂的问题，建议您咨询相关部门获取准确信息。"
