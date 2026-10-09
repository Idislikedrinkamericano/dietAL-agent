"""State 定义：整个图共享的数据结构。"""
from typing import TypedDict


class NutritionFacts(TypedDict):
    calories: float  # kcal
    protein: float   # g
    carbs: float     # g
    fat: float       # g


class MealItem(TypedDict):
    name: str            # 食物名，如 "鸡胸肉"
    amount: str          # 份量描述，如 "2碗"
    nutrition: NutritionFacts


class DietState(TypedDict, total=False):
    user_input: str              # 用户原始输入，如 "午饭吃了两碗米饭"
    parsed_items: list[dict]     # parse_meal 输出: [{"name":..., "servings":...}]
    new_meals: list[MealItem]    # estimate_nutrition 输出: 带营养估算的条目
    daily_meals: list[MealItem]  # 今天已记录的所有餐食
    daily_totals: NutritionFacts # 今天累计摄入
    goals: NutritionFacts        # 每日目标
    feedback: str                # feedback 节点生成的点评
    date: str                    # 记录日期 YYYY-MM-DD
