import time

def small_model_answer(question: str) -> str:
    time.sleep(0.1)
    return f"[小模型回答] {question}"

def low_confidence(answer: str) -> bool:
    return "不确定" in answer or len(answer) < 10
