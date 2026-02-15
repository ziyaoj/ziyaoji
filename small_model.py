import time
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from config import SMALL_MODEL_PATH, SMALL_MODEL_DEVICE, SMALL_MODEL_MAX_LENGTH

# 全局变量，延迟加载模型
_tokenizer = None
_model = None


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

        # 构建提示词（chat 模板）
        messages = [
            {"role": "system", "content": "你是校园问答助手，请简洁回答用户问题。"},
            {"role": "user", "content": question},
        ]
        prompt = _tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        # 编码输入
        inputs = _tokenizer(prompt, return_tensors="pt", max_length=SMALL_MODEL_MAX_LENGTH, truncation=True)
        inputs = {k: v.to(SMALL_MODEL_DEVICE) for k, v in inputs.items()}

        # 生成回答（更短更快，但保证可用）
        with torch.no_grad():
            outputs = _model.generate(
                **inputs,
                max_new_tokens=128,
                temperature=0.3,
                do_sample=True,
                top_p=0.8,
                repetition_penalty=1.1,
                no_repeat_ngram_size=3,
                eos_token_id=_tokenizer.eos_token_id,
                pad_token_id=_tokenizer.eos_token_id
            )

        # ✅ 只解码新生成部分，避免系统提示被输出
        gen_ids = outputs[0][inputs["input_ids"].shape[-1]:]
        answer = _tokenizer.decode(gen_ids, skip_special_tokens=True).strip()

        # 如果有代码块，直接保留代码块
        if "```" in answer:
            return answer

        # 允许最多两句（避免太短）
        seps = ["。", "！", "？", ".", "!", "?"]
        sentences = []
        buf = ""
        for ch in answer:
            buf += ch
            if ch in seps:
                sentences.append(buf.strip())
                buf = ""
                if len(sentences) >= 2:
                    break
        answer = "".join(sentences) if sentences else answer

        return answer if answer else "无法生成回答"

    except Exception as e:
        print(f"小模型推理错误: {e}")
        # 降级到简单回答
        time.sleep(0.1)
        return "[小模型] 我不太确定如何回答这个问题"


def low_confidence(answer: str) -> bool:
    """判断小模型回答是否置信度低"""
    keywords = [
        "不确定", "不太确定", "无法", "不知道", "抱歉", "对不起",
        "不具备", "不能", "无法提供", "建议咨询", "我不是", "不能回答"
    ]
    return any(k in answer for k in keywords) or len(answer) < 10