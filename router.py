import json
import time
from utils import complexity_score, log_event
from small_model import small_model_answer, low_confidence
from big_model import big_model_answer

FAQ_PATH = "faq.json"


def faq_answer(question: str) -> str:
    with open(FAQ_PATH, "r", encoding="utf-8") as f:
        faq = json.load(f)

    for item in faq:
        if any(k in question for k in item.get("keywords", [])):
            return item.get("answer", "暂无答案")

    return "我还不知道呢，请再描述得详细一点"


def route_question(question: str):
    score = complexity_score(question)
    start = time.time()
    route = "faq"

    # 1) 低复杂度：先 FAQ
    if score <= 1:
        answer = faq_answer(question)
        route = "faq"

        # FAQ 未命中再走小模型
        if answer == "我还不知道呢，请再描述得详细一点":
            answer = small_model_answer(question)
            route = "small_model"

            if low_confidence(answer):
                answer = big_model_answer(question)
                route = "big_model_fallback"

    # 2) 中复杂度：先小模型，低置信度再回退
    elif score <= 3:
        answer = small_model_answer(question)
        route = "small_model"

        if low_confidence(answer):
            answer = big_model_answer(question)
            route = "big_model_fallback"

    # 3) 高复杂度：直接大模型
    else:
        answer = big_model_answer(question)
        route = "big_model"

    response_time = time.time() - start
    cost = 0
    log_event(question, score, route, response_time, cost)

    meta = {
        "score": score,
        "route": route,
        "response_time": response_time,
        "cost": cost,
    }
    return answer, meta
