"""Daily JSON log. A new calendar day starts with an empty log."""
import json
import os
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
STORE_PATH = os.path.join(DATA_DIR, "daily_log.json")


def _empty_day() -> dict:
    return {"date": date.today().isoformat(), "meals": [], "totals": {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}}


def load_today() -> dict:
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
    day = load_today()
    if not day["meals"]:
        return None
    removed = day["meals"].pop()
    _recalculate(day)
    save(day)
    return removed


def reset_today() -> None:
    save(_empty_day())


def _recalculate(day: dict) -> None:
    totals = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
    for meal in day["meals"]:
        for key in totals:
            totals[key] = round(totals[key] + meal["nutrition"][key], 1)
    day["totals"] = totals
