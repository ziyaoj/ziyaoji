import json
import os
import time
from utils import complexity_score, log_event
from small_model import small_model_answer, low_confidence
from big_model import big_model_answer

FAQ_PATH = os.path.join(os.path.dirname(__file__), "faq.json")
COST_PER_TOKEN = 0.001
_faq_cache = None


def _load_faq():
    """懒加载FAQ数据"""
    global _faq_cache
    if _faq_cache is None:
        with open(FAQ_PATH, "r", encoding="utf-8") as f:
            _faq_cache = json.load(f)
    return _faq_cache


def faq_answer(question: str) -> str:
    faq = _load_faq()
    best_match = None
    best_score = 0

    for item in faq:
        keywords = item.get("keywords", [])
        match_count = sum(1 for k in keywords if k in question)
        if match_count > best_score:
            best_score = match_count
            best_match = item

    if best_match:
        return best_match.get("answer", "暂无答案")
    return "我还不知道呢，请再描述得详细一点"


def route_question(question: str, history: list = None):
    """
    路由问题到合适的模型

    参数:
        question: 用户问题
        history: 对话历史列表（可选），传递给小模型以支持上下文记忆
    """
    score = complexity_score(question)
    start = time.time()
    route = "faq"
    cost = 0

    # 1) 低复杂度：先 FAQ
    if score <= 1:
        answer = faq_answer(question)
        route = "faq"

        if answer == "我还不知道呢，请再描述得详细一点":
            answer = small_model_answer(question, history=history)
            route = "small_model"

            if low_confidence(answer):
                answer, usage_info = big_model_answer(question)
                route = "big_model_fallback"
                cost = usage_info.get("total_tokens", 0) * COST_PER_TOKEN

    # 2) 中复杂度：先小模型
    elif score <= 3:
        answer = small_model_answer(question, history=history)
        route = "small_model"

        if low_confidence(answer):
            answer, usage_info = big_model_answer(question)
            route = "big_model_fallback"
            cost = usage_info.get("total_tokens", 0) * COST_PER_TOKEN

    # 3) 高复杂度：直接大模型
    else:
        answer, usage_info = big_model_answer(question)
        route = "big_model"
        cost = usage_info.get("total_tokens", 0) * COST_PER_TOKEN

    response_time = time.time() - start
    log_event(question, score, route, response_time, cost)

    meta = {
        "score": score,
        "route": route,
        "response_time": response_time,
        "cost": cost,
    }
    return answer, meta