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

    return "FAQ 未命中"

def route_question(question: str):
    score = complexity_score(question)
    route = "faq"
    start = time.time()

    if score <= 1:
        answer = faq_answer(question)
        route = "faq"
    elif score <= 3:
        answer = small_model_answer(question)
        route = "small_model"
        if low_confidence(answer):
            answer = big_model_answer(question)
            route = "big_model_fallback"
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
