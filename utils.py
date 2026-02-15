import csv
import os
from datetime import datetime

# 复杂问题关键词（可自行扩展）
COMPLEX_KEYWORDS = ["分析", "对比", "规划", "设计", "为什么", "如何", "解释", "原因", "区别"]

def complexity_score(question: str) -> int:
    score = 0
    q = question.strip()

    # 1) 长度打分（分档）
    length = len(q)
    if length > 30:
        score += 3
    elif length > 20:
        score += 2
    elif length > 10:
        score += 1

    # 2) 关键词加分
    for k in COMPLEX_KEYWORDS:
        if k in q:
            score += 1

    # 3) 标点复杂度（多问句、多分句）
    score += min(q.count("？"), 1)  # 问号最多加 1 分
    score += min(q.count("，"), 1)  # 逗号最多加 1 分
    score += min(q.count(";") + q.count("；"), 1)  # 分号最多加 1 分

    # 4) 空问题保护
    if not q:
        return 0

    return score


def log_event(question: str, score: int, route: str, response_time: float, cost: float):
    file_exists = os.path.exists("logs.csv")
    with open("logs.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "question", "score", "route", "response_time", "cost"])
        writer.writerow([datetime.now().isoformat(timespec="seconds"), question, score, route, response_time, cost])