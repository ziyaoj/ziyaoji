import csv
import os

def complexity_score(question: str) -> int:
    score = 0

    if len(question) > 30:
        score += 1

    keywords = ["分析", "对比", "规划", "设计", "为什么", "如何"]
    for k in keywords:
        if k in question:
            score += 1

    if question.count("？") > 1:
        score += 1

    return score

def log_event(question: str, score: int, route: str, response_time: float, cost: float):
    file_exists = os.path.exists("logs.csv")
    with open("logs.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "question", "score", "route", "response_time", "cost"])
        writer.writerow(["", question, score, route, response_time, cost])