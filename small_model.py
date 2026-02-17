import time
from collections import deque
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from config import SMALL_MODEL_PATH, SMALL_MODEL_DEVICE, SMALL_MODEL_MAX_LENGTH

# 全局变量，延迟加载模型
_tokenizer = None
_model = None

# ========== 新增：上下文记忆管理 ==========
# 最多保留最近 3 轮对话（可调），避免超出 max_length
MAX_HISTORY_ROUNDS = 3


def _load_model():
    """懒加载本地小模型"""
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        print(f"正在加载本地小模型: {SMALL_MODEL_PATH}")
        _tokenizer = AutoTokenizer.from_pretrained(SMALL_MODEL_PATH, trust_remote_code=True)
        _model = AutoModelForCausalLM.from_pretrained(
            SMALL_MODEL_PATH,
            torch_dtype=torch.float32,
            device_map=SMALL_MODEL_DEVICE,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        print("本地小模型加载完成")


def small_model_answer(question: str, history: list = None) -> str:
    """
    使用本地DeepSeek 1.5b模型回答问题

    参数:
        question: 用户当前问题
        history: 对话历史列表，每个元素是 {"role": "user"/"assistant", "content": "..."}
                 传入 None 则无上下文（兼容旧调用方式）
    """
    try:
        _load_model()

        # ========== 改进：构建带上下文记忆的提示词 ==========
        messages = [
            {
                "role": "system",
                "content": (
                    "你是校园问答助手。请用一两句话简短回答，不超过100字。"
                    "直接给出答案，不要重复问题，不要说多余的话。"
                ),
            },
        ]

        # 加入历史对话（最近 N 轮）
        if history:
            recent = history[-(MAX_HISTORY_ROUNDS * 2):]  # 每轮2条：user+assistant
            messages.extend(recent)

        # 加入当前问题
        messages.append({"role": "user", "content": question})

        prompt = _tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        # 编码输入
        inputs = _tokenizer(
            prompt, return_tensors="pt",
            max_length=SMALL_MODEL_MAX_LENGTH, truncation=True
        )
        inputs = {k: v.to(SMALL_MODEL_DEVICE) for k, v in inputs.items()}

        # ========== 改进：更短的生成参数 ==========
        with torch.no_grad():
            outputs = _model.generate(
                **inputs,
                max_new_tokens=80,  # 从128减少到80，更严格控制长度
                temperature=0.3,
                do_sample=True,
                top_p=0.8,
                repetition_penalty=1.2,  # 略微提高重复惩罚
                no_repeat_ngram_size=3,
                eos_token_id=_tokenizer.eos_token_id,
                pad_token_id=_tokenizer.eos_token_id
            )

        # 只解码新生成部分
        gen_ids = outputs[0][inputs["input_ids"].shape[-1]:]
        answer = _tokenizer.decode(gen_ids, skip_special_tokens=True).strip()

        # 如果有代码块，直接保留
        if "```" in answer:
            return answer

        # ========== 改进：更严格的截断 —— 最多两句且不超过100字 ==========
        answer = _truncate_answer(answer, max_sentences=2, max_chars=100)

        return answer if answer else "无法生成回答"

    except Exception as e:
        print(f"小模型推理错误: {e}")
        time.sleep(0.1)
        return "[小模型] 暂时繁忙，请稍后再试"


def _truncate_answer(text: str, max_sentences: int = 2, max_chars: int = 100) -> str:
    """截断回答：最多 max_sentences 句，且不超过 max_chars 个字符"""
    seps = ["。", "！", "？", ".", "!", "?"]
    sentences = []
    buf = ""
    for ch in text:
        buf += ch
        if ch in seps:
            sentences.append(buf.strip())
            buf = ""
            if len(sentences) >= max_sentences:
                break

    result = "".join(sentences) if sentences else text

    # 硬截断到 max_chars
    if len(result) > max_chars:
        # 在 max_chars 范围内找最后一个句号截断
        truncated = result[:max_chars]
        for sep in seps:
            idx = truncated.rfind(sep)
            if idx > 0:
                return truncated[:idx + 1]
        return truncated + "…"

    return result


def low_confidence(answer: str) -> bool:
    """判断小模型回答是否置信度低"""
    keywords = [
        "不确定", "不太确定", "不知道", "抱歉", "对不起",
        "不具备", "不能", "无法提供", "建议咨询", "我不是", "不能回答"
    ]
    exception_phrases = ["无法避免", "不能说", "不能否认"]

    for k in keywords:
        if k in answer:
            if any(exc in answer and k in exc for exc in exception_phrases):
                continue
            return True

    return len(answer) < 5