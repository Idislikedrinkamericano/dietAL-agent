"""LangGraph workflow: classify -> parse -> estimate -> log -> feedback."""
import os
from langgraph.graph import StateGraph, END

from .state import DietState
from .nutrition_db import parse_meal_text, estimate_nutrition, food_count
from .llm_parser import parse_meal_with_llm
from .store import load_today, save

DEFAULT_GOALS = {"calories": 2200.0, "protein": 120.0, "carbs": 275.0, "fat": 73.0}


def _llm_available() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY"))


def classify_intent(state: DietState) -> dict:
    text = state["user_input"].strip()
    lower = text.lower()
    meal_actions = ("吃了", "刚吃", "吃的", "早餐", "午饭", "晚饭", "夜宵", "加餐", "喝了", "ate ", "i ate", "i had", "had ")
    correction_or_question = ("我觉得", "不对", "不是", "算错", "没这么", "这么低", "这么高", "太低", "太高", "应该是", "真的吗", "为什么", "怎么算", "calorie", "calories")
    has_meal_action = any(m in lower for m in meal_actions)
    looks_like_discussion = any(m in lower for m in correction_or_question)
    if looks_like_discussion and not has_meal_action:
        return {"intent": "conversation"}
    if ("?" in text or "？" in text) and not has_meal_action:
        return {"intent": "conversation"}
    return {"intent": "log_meal"}


def route_intent(state: DietState) -> str:
    return state.get("intent", "log_meal")


def conversation_response(state: DietState) -> dict:
    day = load_today()
    return {
        "daily_meals": day["meals"], "daily_totals": day["totals"], "date": day["date"],
        "feedback": "这句话看起来是在讨论或纠正上一条记录，所以我没有再次记账。需要改错时可以先用 /undo 撤销上一条。",
    }


def parse_meal(state: DietState) -> dict:
    text = state["user_input"]
    if _llm_available():
        try:
            items = parse_meal_with_llm(text)
            if items:
                return {"parsed_items": items}
        except Exception as exc:
            print(f"[LLM parser fallback: {exc}]")
    return {"parsed_items": parse_meal_text(text)}


def estimate_nutrition_node(state: DietState) -> dict:
    meals = []
    for item in state.get("parsed_items", []):
        nutrition = estimate_nutrition(item["name"], item["grams"])
        meals.append({
            "name": item["name"],
            "amount": item["amount"],
            "grams": item["grams"],
            "assumed": item.get("assumed", False),
            "nutrition": nutrition,
        })
    return {"new_meals": meals}


def update_log(state: DietState) -> dict:
    day = load_today()
    for meal in state.get("new_meals", []):
        day["meals"].append(meal)
        for k in ("calories", "protein", "carbs", "fat"):
            day["totals"][k] = round(day["totals"][k] + meal["nutrition"][k], 1)
    save(day)
    return {"daily_meals": day["meals"], "daily_totals": day["totals"], "date": day["date"]}


def feedback(state: DietState) -> dict:
    totals = state["daily_totals"]
    goals = state.get("goals") or DEFAULT_GOALS

    if not state.get("new_meals"):
        names = ", ".join(m["name"] for m in state.get("daily_meals", [])[-3:])
        return {"feedback": (
            f"没识别出食物（当前内置库有 {food_count()} 种）。"
            "可以写明确重量，如“200g鸡胸肉”，或者“两个鸡蛋 / 一碗半米饭”。"
            f" 今天已记：{names or '无'}。"
        )}

    lines, assumptions = [], []
    for meal in state["new_meals"]:
        n = meal["nutrition"]
        lines.append(
            f"{meal['name']}({meal['amount']}): {n['calories']}kcal "
            f"蛋白{n['protein']}g / 碳水{n['carbs']}g / 脂肪{n['fat']}g"
        )
        if meal.get("assumed"):
            assumptions.append(meal["name"])

    tips = []
    if totals["calories"] > goals["calories"]:
        tips.append(f"热量已超过目标约{round(totals['calories']-goals['calories'])}kcal。")
    if totals["fat"] > goals["fat"]:
        tips.append(f"脂肪已超过目标约{round(totals['fat']-goals['fat'],1)}g。")
    if totals["carbs"] > goals["carbs"]:
        tips.append(f"碳水已超过目标约{round(totals['carbs']-goals['carbs'],1)}g。")
    if totals["protein"] < goals["protein"] * 0.5:
        tips.append("当前蛋白摄入还不到目标的一半。")

    summary = (
        f"已记录：{'；'.join(lines)}\n"
        f"今日累计：{totals['calories']}kcal / 蛋白{totals['protein']}g / "
        f"碳水{totals['carbs']}g / 脂肪{totals['fat']}g"
    )
    if assumptions:
        summary += "\n📏 " + "、".join(assumptions) + "的份量使用了默认克重估算；知道实际克数时直接输入会更准。"
    if tips:
        summary += "\n💡 " + " ".join(tips)
    else:
        summary += "\n💡 当前累计没有明显超出你设置的营养目标。"
    return {"feedback": summary}


def build_graph():
    g = StateGraph(DietState)
    g.add_node("classify_intent", classify_intent)
    g.add_node("conversation_response", conversation_response)
    g.add_node("parse_meal", parse_meal)
    g.add_node("estimate_nutrition", estimate_nutrition_node)
    g.add_node("update_log", update_log)
    g.add_node("feedback", feedback)
    g.set_entry_point("classify_intent")
    g.add_conditional_edges("classify_intent", route_intent, {"log_meal": "parse_meal", "conversation": "conversation_response"})
    g.add_edge("conversation_response", END)
    g.add_edge("parse_meal", "estimate_nutrition")
    g.add_edge("estimate_nutrition", "update_log")
    g.add_edge("update_log", "feedback")
    g.add_edge("feedback", END)
    return g.compile()
