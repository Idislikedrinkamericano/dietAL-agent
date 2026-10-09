"""每日记录的 JSON 持久化：每天零点自动清零。"""
import json
import os
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
STORE_PATH = os.path.join(DATA_DIR, "daily_log.json")


def _empty_day() -> dict:
    return {
        "date": date.today().isoformat(),
        "meals": [],
        "totals": {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0},
    }


def load_today() -> dict:
    """读出今天的记录；如果是昨天的数据则清零。"""
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(STORE_PATH):
        with open(STORE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("date") == date.today().isoformat():
            return data
    data = _empty_day()
    save(data)
    return data


def save(data: dict) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def undo_last_meal() -> dict | None:
    """撤销今天最后一条已记录食物，并重新计算累计营养。"""
    day = load_today()
    if not day["meals"]:
        return None
    removed = day["meals"].pop()
    totals = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
    for meal in day["meals"]:
        for key in totals:
            totals[key] = round(totals[key] + meal["nutrition"][key], 1)
    day["totals"] = totals
    save(day)
    return removed
