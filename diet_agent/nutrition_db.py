"""Gram-based nutrition database and lightweight meal parser.

All nutrition values are approximate per 100g. Household units are converted to
estimated grams so the math stays consistent. This is a demo, not medical advice.
"""
import re

def _f(kcal, protein, carbs, fat, units=None):
    return {
        "per_100g": {"calories": float(kcal), "protein": float(protein), "carbs": float(carbs), "fat": float(fat)},
        "units": units or {},
    }

FOOD_DB = {
    # staples
    "米饭": _f(130, 2.7, 28.2, 0.3, {"碗": 150, "份": 150}),
    "糙米": _f(123, 2.7, 25.6, 1.0, {"碗": 150}),
    "面条": _f(138, 4.5, 25.0, 2.1, {"碗": 200, "份": 200}),
    "意大利面": _f(158, 5.8, 30.9, 0.9, {"碗": 200, "份": 200}),
    "燕麦": _f(389, 16.9, 66.3, 6.9, {"碗": 40, "份": 40}),
    "馒头": _f(223, 7.0, 47.0, 1.1, {"个": 100}),
    "包子": _f(220, 8.0, 32.0, 7.0, {"个": 90}),
    "饺子": _f(220, 10.0, 28.0, 8.0, {"个": 25}),
    "面包": _f(265, 9.0, 49.0, 3.2, {"片": 35}),
    "贝果": _f(250, 10.0, 49.0, 1.5, {"个": 100}),
    "玉米": _f(96, 3.4, 21.0, 1.5, {"根": 120}),
    "红薯": _f(86, 1.6, 20.1, 0.1, {"个": 180}),
    "土豆": _f(77, 2.0, 17.0, 0.1, {"个": 170}),
    # protein
    "鸡胸肉": _f(165, 31.0, 0.0, 3.6, {"块": 150, "份": 150}),
    "鸡腿": _f(209, 26.0, 0.0, 10.9, {"个": 120}),
    "鸡蛋": _f(143, 12.6, 0.7, 9.5, {"个": 50, "只": 50}),
    "牛肉": _f(250, 26.0, 0.0, 15.0, {"份": 150}),
    "瘦牛肉": _f(200, 29.0, 0.0, 8.0, {"份": 150}),
    "猪肉": _f(242, 27.0, 0.0, 14.0, {"份": 150}),
    "三文鱼": _f(208, 20.0, 0.0, 13.0, {"份": 150}),
    "金枪鱼": _f(132, 29.0, 0.0, 1.0, {"份": 120}),
    "鱼": _f(130, 22.0, 0.0, 4.0, {"份": 150}),
    "虾": _f(99, 24.0, 0.2, 0.3, {"份": 120}),
    "豆腐": _f(76, 8.1, 1.9, 4.8, {"块": 200, "份": 150}),
    "豆浆": _f(33, 3.0, 1.7, 1.8, {"杯": 250}),
    "希腊酸奶": _f(59, 10.0, 3.6, 0.4, {"杯": 170}),
    "酸奶": _f(63, 5.3, 7.0, 1.6, {"杯": 180}),
    "牛奶": _f(61, 3.2, 4.8, 3.3, {"杯": 240}),
    "蛋白粉": _f(400, 80.0, 8.0, 6.0, {"勺": 30}),
    # vegetables
    "西兰花": _f(34, 2.8, 6.6, 0.4, {"份": 100}),
    "菠菜": _f(23, 2.9, 3.6, 0.4, {"份": 100}),
    "生菜": _f(15, 1.4, 2.9, 0.2, {"份": 100}),
    "番茄": _f(18, 0.9, 3.9, 0.2, {"个": 120}),
    "黄瓜": _f(15, 0.7, 3.6, 0.1, {"根": 180}),
    "胡萝卜": _f(41, 0.9, 9.6, 0.2, {"根": 60}),
    "蘑菇": _f(22, 3.1, 3.3, 0.3, {"份": 100}),
    "青椒": _f(20, 0.9, 4.6, 0.2, {"个": 120}),
    "蔬菜": _f(35, 2.0, 7.0, 0.3, {"份": 150}),
    "沙拉": _f(50, 2.0, 7.0, 2.0, {"份": 200}),
    # fruit
    "香蕉": _f(89, 1.1, 22.8, 0.3, {"根": 118, "个": 118}),
    "苹果": _f(52, 0.3, 13.8, 0.2, {"个": 182}),
    "橙子": _f(47, 0.9, 11.8, 0.1, {"个": 140}),
    "草莓": _f(32, 0.7, 7.7, 0.3, {"份": 150}),
    "蓝莓": _f(57, 0.7, 14.5, 0.3, {"份": 150}),
    "葡萄": _f(69, 0.7, 18.1, 0.2, {"份": 150}),
    "西瓜": _f(30, 0.6, 7.6, 0.2, {"份": 250}),
    "牛油果": _f(160, 2.0, 8.5, 14.7, {"个": 150}),
    "水果": _f(55, 0.6, 14.0, 0.2, {"份": 150}),
    # snacks / drinks
    "坚果": _f(607, 20.0, 21.0, 54.0, {"把": 28, "份": 28}),
    "花生酱": _f(588, 25.0, 20.0, 50.0, {"勺": 16}),
    "巧克力": _f(535, 7.7, 59.4, 29.7, {"块": 20}),
    "薯片": _f(536, 7.0, 53.0, 35.0, {"份": 50}),
    "可乐": _f(42, 0.0, 10.6, 0.0, {"罐": 330, "杯": 300}),
    "咖啡": _f(2, 0.1, 0.0, 0.0, {"杯": 240}),
    "拿铁": _f(60, 3.2, 5.0, 3.0, {"杯": 300}),
    "奶茶": _f(95, 1.5, 15.0, 3.5, {"杯": 500}),
    "橙汁": _f(45, 0.7, 10.4, 0.2, {"杯": 240}),
    # fast food / generic dishes
    "汉堡": _f(275, 12.5, 20.0, 15.0, {"个": 200}),
    "芝士汉堡": _f(300, 15.0, 22.0, 17.0, {"个": 220}),
    "薯条": _f(312, 3.4, 41.0, 15.0, {"份": 120}),
    "披萨": _f(266, 11.0, 33.0, 10.0, {"片": 107}),
    "炸鸡": _f(280, 24.0, 10.0, 16.0, {"块": 120}),
    "炒饭": _f(180, 5.0, 28.0, 6.0, {"碗": 250, "份": 250}),
    "炒面": _f(190, 6.0, 27.0, 7.0, {"碗": 250, "份": 250}),
    "寿司": _f(150, 6.0, 28.0, 2.0, {"个": 35, "份": 210}),
    "墨西哥卷": _f(210, 9.0, 25.0, 8.0, {"个": 300}),
    "三明治": _f(220, 11.0, 26.0, 8.0, {"个": 180}),
}

ALIASES = {
    "白饭": "米饭", "米": "米饭", "鸡胸": "鸡胸肉", "鸡肉": "鸡胸肉",
    "牛排": "瘦牛肉", "西红柿": "番茄", "酸奶杯": "酸奶",
    "burger": "汉堡", "fries": "薯条", "banana": "香蕉", "apple": "苹果",
    "latte": "拿铁", "milk": "牛奶", "egg": "鸡蛋", "eggs": "鸡蛋",
}

CN_NUM = {
    "半": 0.5, "一": 1, "一个": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
}
UNIT_PATTERN = "碗|个|杯|份|根|把|片|罐|只|块|勺"


def _canonicalize(text: str) -> str:
    for alias, target in sorted(ALIASES.items(), key=lambda x: len(x[0]), reverse=True):
        text = text.replace(alias, target)
    return text


def _number(raw: str) -> float:
    raw = raw.strip()
    if re.fullmatch(r"\d+(?:\.\d+)?", raw):
        return float(raw)
    if raw == "一半" or raw == "半":
        return 0.5
    if raw.endswith("半") and len(raw) > 1:
        return _number(raw[:-1]) + 0.5
    return float(CN_NUM.get(raw, 1))


def _find_quantity(text: str, food: str) -> tuple[float, str, bool]:
    esc = re.escape(food)

    # explicit grams before/after food
    patterns = [
        rf"(\d+(?:\.\d+)?)\s*(?:g|克|gram|grams)\s*{esc}",
        rf"{esc}\s*(\d+(?:\.\d+)?)\s*(?:g|克|gram|grams)",
    ]
    for pat in patterns:
        m = re.search(pat, text, flags=re.I)
        if m:
            grams = float(m.group(1))
            return grams, f"{grams:g}g", False

    # ml: lightweight density approximation 1ml≈1g
    patterns_ml = [
        rf"(\d+(?:\.\d+)?)\s*(?:ml|毫升)\s*{esc}",
        rf"{esc}\s*(\d+(?:\.\d+)?)\s*(?:ml|毫升)",
    ]
    for pat in patterns_ml:
        m = re.search(pat, text, flags=re.I)
        if m:
            grams = float(m.group(1))
            return grams, f"{grams:g}ml", True

    # household unit before food, e.g. 两个鸡蛋 / 一碗半米饭
    m = re.search(rf"([0-9]+(?:\.[0-9]+)?|[一二两三四五六七八九十半]+(?:半)?)\s*({UNIT_PATTERN})\s*{esc}", text)
    if m:
        qty, unit = _number(m.group(1)), m.group(2)
        grams_per = FOOD_DB[food]["units"].get(unit)
        if grams_per:
            grams = qty * grams_per
            return grams, f"{qty:g}×{unit}≈{grams:g}g", True

    # household unit after food, e.g. 鸡蛋2个
    m = re.search(rf"{esc}\s*([0-9]+(?:\.[0-9]+)?)\s*({UNIT_PATTERN})", text)
    if m:
        qty, unit = float(m.group(1)), m.group(2)
        grams_per = FOOD_DB[food]["units"].get(unit)
        if grams_per:
            grams = qty * grams_per
            return grams, f"{qty:g}×{unit}≈{grams:g}g", True

    # no amount: use first household unit if one exists, otherwise 100g
    units = FOOD_DB[food]["units"]
    if units:
        unit, grams = next(iter(units.items()))
        return float(grams), f"1×{unit}≈{grams:g}g", True
    return 100.0, "默认100g", True


def parse_meal_text(text: str) -> list[dict]:
    """Parse supported foods and normalize all quantities to grams."""
    normalized = _canonicalize(text.lower())
    found = []
    occupied = set()
    # longest names first so 芝士汉堡 wins over 汉堡
    for food in sorted(FOOD_DB, key=len, reverse=True):
        if food in normalized:
            # avoid duplicate substring matches
            idx = normalized.find(food)
            span = set(range(idx, idx + len(food)))
            if occupied & span:
                continue
            grams, amount, assumed = _find_quantity(normalized, food)
            found.append({"name": food, "grams": round(grams, 1), "amount": amount, "assumed": assumed})
            occupied |= span
    return found


def estimate_nutrition(name: str, grams: float) -> dict:
    base = FOOD_DB[name]["per_100g"]
    factor = grams / 100.0
    return {k: round(v * factor, 1) for k, v in base.items()}


def food_count() -> int:
    return len(FOOD_DB)


def default_unit_grams(name: str) -> dict:
    return dict(FOOD_DB[name]["units"])
