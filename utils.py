import csv
import os
from datetime import datetime

# 复杂问题关键词（可自行扩展）
COMPLEX_KEYWORDS = ["分析", "对比", "规划", "设计", "为什么", "如何", "解释", "原因", "区别"]

def complexity_score(question: str) -> int:
    q = question.strip()
    
    # 1) 空问题保护（early return）
    if not q:
        return 0
    
    score = 0

    # 2) 长度打分（分档）
    length = len(q)
    if length > 30:
        score += 3
    elif length > 20:
        score += 2
    elif length > 10:
        score += 1

    # 3) 关键词加分
    for k in COMPLEX_KEYWORDS:
        if k in q:
            score += 1

    # 4) 标点复杂度（多问句、多分句）
    score += min(q.count("？"), 1)  # 问号最多加 1 分
    score += min(q.count("，"), 1)  # 逗号最多加 1 分
    score += min(q.count(";") + q.count("；"), 1)  # 分号最多加 1 分

    return score


def log_event(question: str, score: int, route: str, response_time: float, cost: float):
    """记录事件到日志文件，处理并发安全"""
    # 使用 'a+' 模式打开，然后检查文件是否为空来决定是否写表头
    # 这样可以避免 TOCTOU 竞态条件
    with open("logs.csv", "a+", newline="", encoding="utf-8") as f:
        # 移动到文件末尾并获取位置来判断文件是否为空
        f.seek(0, 2)
        is_empty = f.tell() == 0
        
        writer = csv.writer(f)
        if is_empty:
            writer.writerow(["timestamp", "question", "score", "route", "response_time", "cost"])
        writer.writerow([datetime.now().isoformat(timespec="seconds"), question, score, route, response_time, cost])