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

def big_model_answer(question: str):
    """使用远程Qwen3大模型API回答问题，返回(answer, usage_info)元组"""
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
        
        # 提取token使用量信息
        usage = response.usage
        usage_info = {
            "prompt_tokens": usage.prompt_tokens if usage else 0,
            "completion_tokens": usage.completion_tokens if usage else 0,
            "total_tokens": usage.total_tokens if usage else 0,
        }
        
        return (answer if answer else "大模型未返回有效回答", usage_info)
        
    except Exception as e:
        print(f"大模型API调用错误: {e}")
        # 降级到简单回答
        time.sleep(0.2)
        return (f"[大模型] 关于'{question}'，这是一个复杂的问题，建议您咨询相关部门获取准确信息。", {"total_tokens": 0})
