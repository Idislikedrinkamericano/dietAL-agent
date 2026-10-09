"""食物营养数据库 + 启发式解析/估算。

v1 为了零依赖可运行，用内置的常见食物表做估算。
想更准时，把 estimate() 换成 LLM 调用即可（graph.py 里留了钩子）。
营养值为每份常见份量的估算，仅供参考。
"""
import re

# 食物名 -> 每份营养（常见份量）
FOOD_DB: dict[str, dict] = {
    "米饭":     {"unit": "碗",  "calories": 260, "protein": 5.0,  "carbs": 57.0, "fat": 0.6},
    "面条":     {"unit": "碗",  "calories": 300, "protein": 9.0,  "carbs": 60.0, "fat": 2.0},
    "馒头":     {"unit": "个",  "calories": 220, "protein": 6.0,  "carbs": 47.0, "fat": 1.0},
    "包子":     {"unit": "个",  "calories": 200, "protein": 7.0,  "carbs": 30.0, "fat": 6.0},
    "鸡胸肉":   {"unit": "100g","calories": 165, "protein": 31.0, "carbs": 0.0,  "fat": 3.6},
    "鸡腿":     {"unit": "个",  "calories": 250, "protein": 26.0, "carbs": 0.0,  "fat": 15.0},
    "鸡蛋":     {"unit": "个",  "calories": 70,  "protein": 6.0,  "carbs": 0.6,  "fat": 5.0},
    "牛肉":     {"unit": "100g","calories": 250, "protein": 26.0, "carbs": 0.0,  "fat": 15.0},
    "猪肉":     {"unit": "100g","calories": 290, "protein": 20.0, "carbs": 0.0,  "fat": 22.0},
    "鱼":       {"unit": "100g","calories": 130, "protein": 22.0, "carbs": 0.0,  "fat": 4.0},
    "虾":       {"unit": "100g","calories": 100, "protein": 20.0, "carbs": 1.0,  "fat": 1.5},
    "沙拉":     {"unit": "份",  "calories": 150, "protein": 5.0,  "carbs": 10.0, "fat": 10.0},
    "蔬菜":     {"unit": "份",  "calories": 80,  "protein": 3.0,  "carbs": 12.0, "fat": 2.0},
    "水果":     {"unit": "份",  "calories": 90,  "protein": 1.0,  "carbs": 22.0, "fat": 0.5},
    "香蕉":     {"unit": "根",  "calories": 105, "protein": 1.3,  "carbs": 27.0, "fat": 0.4},
    "苹果":     {"unit": "个",  "calories": 95,  "protein": 0.5,  "carbs": 25.0, "fat": 0.3},
    "牛奶":     {"unit": "杯",  "calories": 150, "protein": 8.0,  "carbs": 12.0, "fat": 8.0},
    "拿铁":     {"unit": "杯",  "calories": 150, "protein": 8.0,  "carbs": 12.0, "fat": 7.0},
    "咖啡":     {"unit": "杯",  "calories": 10,  "protein": 1.0,  "carbs": 0.0,  "fat": 0.0},
    "可乐":     {"unit": "罐",  "calories": 140, "protein": 0.0,  "carbs": 39.0, "fat": 0.0},
    "奶茶":     {"unit": "杯",  "calories": 350, "protein": 5.0,  "carbs": 60.0, "fat": 10.0},
    "面包":     {"unit": "片",  "calories": 130, "protein": 4.0,  "carbs": 24.0, "fat": 2.0},
    "汉堡":     {"unit": "个",  "calories": 550, "protein": 25.0, "carbs": 40.0, "fat": 30.0},
    "薯条":     {"unit": "份",  "calories": 400, "protein": 4.0,  "carbs": 50.0, "fat": 20.0},
    "饺子":     {"unit": "个",  "calories": 50,  "protein": 2.5,  "carbs": 6.0,  "fat": 2.0},
    "豆腐":     {"unit": "100g","calories": 80,  "protein": 8.0,  "carbs": 2.0,  "fat": 4.0},
    "酸奶":     {"unit": "杯",  "calories": 120, "protein": 8.0,  "carbs": 15.0, "fat": 3.0},
    "坚果":     {"unit": "把",  "calories": 170, "protein": 6.0,  "carbs": 6.0,  "fat": 15.0},
    "燕麦":     {"unit": "碗",  "calories": 200, "protein": 7.0,  "carbs": 35.0, "fat": 4.0},
}

CN_NUM = {"一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5,
          "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


def _parse_servings(text: str, food: str) -> float:
    """从文本里找份量，如 '两碗米饭' -> 2。找不到默认 1。"""
    # 数字+量词+食物名，如 2碗米饭 / 两碗米饭 / 3个鸡蛋
    m = re.search(r"([0-9一二两三四五六七八九十]+)\s*[碗个杯份根把片罐只块]\s*" + re.escape(food), text)
    if m:
        raw = m.group(1)
        if raw.isdigit():
            return float(raw)
        return float(CN_NUM.get(raw, 1))
    # 克数，如 200g鸡胸肉 / 200克鸡胸肉
    m = re.search(r"([0-9]+)\s*(g|克)\s*" + re.escape(food), text)
    if m:
        return float(m.group(1)) / 100.0  # 按100g为一份折算
    return 1.0


def parse_meal_text(text: str) -> list[dict]:
    """启发式解析：找出文本里提到的食物和份量。"""
    found = []
    for food in FOOD_DB:
        if food in text:
            servings = _parse_servings(text, food)
            found.append({"name": food, "servings": servings})
    return found


def estimate_nutrition(name: str, servings: float) -> dict:
    """查表估算单个食物的营养。"""
    base = FOOD_DB[name]
    return {
        "calories": round(base["calories"] * servings, 1),
        "protein": round(base["protein"] * servings, 1),
        "carbs": round(base["carbs"] * servings, 1),
        "fat": round(base["fat"] * servings, 1),
    }


def unit_of(name: str) -> str:
    return FOOD_DB[name]["unit"]
