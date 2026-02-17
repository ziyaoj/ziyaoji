import json
import os
import time
from utils import complexity_score, log_event
from small_model import small_model_answer, low_confidence
from big_model import big_model_answer

# 使用绝对路径避免工作目录问题
FAQ_PATH = os.path.join(os.path.dirname(__file__), "faq.json")

# 成本估算：每个token的成本（简化估算）
COST_PER_TOKEN = 0.001

# 模块级别缓存 FAQ 数据，避免重复读取文件
_faq_cache = None
_faq_mtime = 0


def _load_faq():
    """懒加载FAQ数据，支持热更新"""
    global _faq_cache, _faq_mtime
    current_mtime = os.path.getmtime(FAQ_PATH)
    if _faq_cache is None or current_mtime > _faq_mtime:
        with open(FAQ_PATH, "r", encoding="utf-8") as f:
            _faq_cache = json.load(f)
        _faq_mtime = current_mtime
    return _faq_cache


def faq_answer(question: str) -> str:
    """
    多级关键词匹配：
    规则：primary（第一关键词）和 secondary（第二关键词）必须同时命中才返回答案。
    - primary 列表中任意一个词出现在问题中 → 第一级命中
    - secondary 列表中任意一个词出现在问题中 → 第二级命中
    - 两级都命中才算匹配成功
    - 多条都匹配时，取 (primary命中数 + secondary命中数) 最高的
    """
    faq = _load_faq()
    q = question.lower()  # 统一小写，解决 WiFi/wifi 等大小写问题

    best_match = None
    best_score = 0

    for item in faq:
        primary_keywords = item.get("primary", [])
        secondary_keywords = item.get("secondary", [])

        # 兼容旧格式（平铺 keywords 列表）
        if not primary_keywords and not secondary_keywords:
            old_keywords = item.get("keywords", [])
            if old_keywords:
                match_count = sum(1 for k in old_keywords if k.lower() in q)
                # 与新格式 primary 权重对齐：旧格式关键词视为 primary 级别
                weighted_score = match_count * 3
                if weighted_score > best_score:
                    best_score = weighted_score
                    best_match = item
                continue

        # === 多级匹配：两级都必须命中 ===
        primary_hits = sum(1 for k in primary_keywords if k.lower() in q)
        secondary_hits = sum(1 for k in secondary_keywords if k.lower() in q)

        # 第一关键词 AND 第二关键词 都必须至少命中一个
        if primary_hits == 0 or secondary_hits == 0:
            continue

        # 总分 = primary命中数 × 3 + secondary命中数 × 1
        # primary 权重更高，确保主题越精准排越前
        score = primary_hits * 3 + secondary_hits

        if score > best_score:
            best_score = score
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
    # 空问题检查：对空字符串或纯空白字符串直接返回提示
    if not question or not question.strip():
        return "请输入您的问题", {"score": 0, "route": "invalid", "response_time": 0, "cost": 0}
    
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

            # 检查小模型异常返回或低置信度，自动降级到大模型
            if answer.startswith("[小模型]") or low_confidence(answer):
                answer, usage_info = big_model_answer(question, history=history)
                route = "big_model_fallback"
                cost = usage_info.get("total_tokens", 0) * COST_PER_TOKEN

    # 2) 中复杂度：先小模型，低置信度再回退
    elif score <= 3:
        answer = small_model_answer(question, history=history)
        route = "small_model"

        # 检查小模型异常返回或低置信度，自动降级到大模型
        if answer.startswith("[小模型]") or low_confidence(answer):
            answer, usage_info = big_model_answer(question, history=history)
            route = "big_model_fallback"
            cost = usage_info.get("total_tokens", 0) * COST_PER_TOKEN

    # 3) 高复杂度：直接大模型
    else:
        answer, usage_info = big_model_answer(question, history=history)
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