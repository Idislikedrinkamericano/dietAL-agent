"""Dependency-free smoke tests for the gram-based parser."""
import importlib.util
from pathlib import Path

MODULE = Path(__file__).parent / "diet_agent" / "nutrition_db.py"
spec = importlib.util.spec_from_file_location("nutrition_db", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def by_name(items, name):
    return next(x for x in items if x["name"] == name)


def approx(actual, expected, tol=0.1):
    assert abs(actual - expected) <= tol, (actual, expected)


items = mod.parse_meal_text("午饭吃了200g鸡胸肉和150g米饭")
approx(by_name(items, "鸡胸肉")["grams"], 200)
approx(by_name(items, "米饭")["grams"], 150)

items = mod.parse_meal_text("吃了两个鸡蛋和一碗半米饭")
approx(by_name(items, "鸡蛋")["grams"], 100)
approx(by_name(items, "米饭")["grams"], 225)

items = mod.parse_meal_text("鸡胸肉180克，半杯拿铁")
approx(by_name(items, "鸡胸肉")["grams"], 180)
approx(by_name(items, "拿铁")["grams"], 150)

n = mod.estimate_nutrition("鸡胸肉", 200)
approx(n["calories"], 330)
approx(n["protein"], 62)

print(f"OK: {mod.food_count()} foods; gram parsing smoke tests passed")
