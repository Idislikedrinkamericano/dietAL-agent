"""State shared across the LangGraph workflow."""
from typing import TypedDict


class NutritionFacts(TypedDict):
    calories: float
    protein: float
    carbs: float
    fat: float


class MealItem(TypedDict, total=False):
    name: str
    amount: str
    grams: float
    assumed: bool
    nutrition: NutritionFacts


class DietState(TypedDict, total=False):
    user_input: str
    intent: str
    parsed_items: list[dict]
    new_meals: list[MealItem]
    daily_meals: list[MealItem]
    daily_totals: NutritionFacts
    goals: NutritionFacts
    feedback: str
    date: str
