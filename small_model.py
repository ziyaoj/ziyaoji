import time
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from config import SMALL_MODEL_PATH, SMALL_MODEL_DEVICE, SMALL_MODEL_MAX_LENGTH

# 全局变量，延迟加载模型
_tokenizer = None
_model = None

# 低置信度关键词
LOW_CONFIDENCE_KEYWORDS = ["不确定", "不太确定", "无法", "不知道", "抱歉"]

def _load_model():
    """懒加载本地小模型"""
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        print(f"正在加载本地小模型: {SMALL_MODEL_PATH}")
        _tokenizer = AutoTokenizer.from_pretrained(SMALL_MODEL_PATH, trust_remote_code=True)
        _model = AutoModelForCausalLM.from_pretrained(
            SMALL_MODEL_PATH,
            torch_dtype=torch.float32,  # 使用float32以兼容CPU
            device_map=SMALL_MODEL_DEVICE,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        print("本地小模型加载完成")

def small_model_answer(question: str) -> str:
    """使用本地DeepSeek 1.5b模型回答问题"""
    try:
        _load_model()
        
        # 构建提示词
        prompt = f"请简洁地回答以下问题：{question}"
        
        # 编码输入
        inputs = _tokenizer(prompt, return_tensors="pt", max_length=SMALL_MODEL_MAX_LENGTH, truncation=True)
        inputs = {k: v.to(SMALL_MODEL_DEVICE) for k, v in inputs.items()}
        
        # 生成回答
        with torch.no_grad():
            outputs = _model.generate(
                **inputs,
                max_new_tokens=256,
                temperature=0.7,
                do_sample=True,
                top_p=0.95,
                pad_token_id=_tokenizer.eos_token_id
            )
        
        # 解码输出
        answer = _tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # 移除输入提示词，只返回回答部分
        if prompt in answer:
            answer = answer.replace(prompt, "").strip()
        
        return answer if answer else "无法生成回答"
        
    except Exception as e:
        print(f"小模型推理错误: {e}")
        # 降级到简单回答
        time.sleep(0.1)
        return "[小模型] 我不太确定如何回答这个问题"

def low_confidence(answer: str) -> bool:
    """判断小模型回答是否置信度低"""
    return any(keyword in answer for keyword in LOW_CONFIDENCE_KEYWORDS) or len(answer) < 10
