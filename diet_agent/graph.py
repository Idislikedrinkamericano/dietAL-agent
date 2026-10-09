"""LangGraph 图：parse_meal -> estimate_nutrition -> update_log -> feedback"""
import os
from langgraph.graph import StateGraph, END

from .state import DietState
from .nutrition_db import parse_meal_text, estimate_nutrition, unit_of, FOOD_DB
from .llm_parser import parse_meal_with_llm
from .store import load_today, save

# 默认每日目标（可在 demo 里改）
DEFAULT_GOALS = {"calories": 2200.0, "protein": 120.0, "carbs": 275.0, "fat": 73.0}


def _llm_available() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY"))


# ---------------- 节点 0：判断用户是在记账，还是在讨论/纠正 ----------------
def classify_intent(state: DietState) -> dict:
    """区分“我要记录一顿饭”和“我在讨论/质疑上一条结果”。

    这一步很重要：如果用户只是说“我觉得这个热量不对”，不能再次把
    句子里的“汉堡”当成一顿新饭记进去。
    """
    text = state["user_input"].strip()
    lower = text.lower()

    meal_actions = (
        "吃了", "刚吃", "吃的", "早餐", "午饭", "晚饭", "夜宵", "加餐",
        "喝了", "喝的", "ate ", "i ate", "i had", "had ",
    )
    correction_or_question = (
        "我觉得", "不对", "不是", "算错", "没这么", "这么低", "这么高",
        "太低", "太高", "应该是", "真的吗", "为什么", "怎么算", "热量没",
        "calorie", "calories",
    )

    has_meal_action = any(marker in lower for marker in meal_actions)
    looks_like_discussion = any(marker in lower for marker in correction_or_question)

    if looks_like_discussion and not has_meal_action:
        return {"intent": "conversation"}
    if ("?" in text or "？" in text) and not has_meal_action:
        return {"intent": "conversation"}
    return {"intent": "log_meal"}


def route_intent(state: DietState) -> str:
    return state.get("intent", "log_meal")


def conversation_response(state: DietState) -> dict:
    """讨论/纠正消息只回复，不改饮食记录。"""
    day = load_today()
    totals = day["totals"]
    return {
        "daily_meals": day["meals"],
        "daily_totals": totals,
        "date": day["date"],
        "feedback": (
            "这句话看起来是在讨论或纠正上一条记录，所以我没有再次记账。\n"
            "目前热量来自本地的通用食物数据库；像餐厅品牌、具体汉堡型号、"
            "lettuce wrap、鸡柳这类商品还不能精确匹配，所以会退化成“通用汉堡”的估值。\n"
            "如果上一条记错了，可以输入 /undo 撤销上一条记录。"
        ),
    }


# ---------------- 节点 1：解析 ----------------
def parse_meal(state: DietState) -> dict:
    """把自然语言解析成 [{"name": "米饭", "servings": 2.0}]。

    有 OPENAI_API_KEY 时优先使用 LLM；没有 key、调用失败，或模型没有
    解析出支持的食物时，自动回退到 v1 的关键词 + 正则解析。
    """
    text = state["user_input"]
    if _llm_available():
        try:
            items = parse_meal_with_llm(text)
            if items:
                return {"parsed_items": items}
        except Exception as exc:
            print(f"[LLM parser fallback: {exc}]")

    return {"parsed_items": parse_meal_text(text)}


# ---------------- 节点 2：估算营养 ----------------
def estimate_nutrition_node(state: DietState) -> dict:
    """给每个解析出的食物估算营养。"""
    meals = []
    for item in state.get("parsed_items", []):
        name, servings = item["name"], item["servings"]
        nutrition = estimate_nutrition(name, servings)
        meals.append({
            "name": name,
            "amount": f"{servings:g}×{unit_of(name)}",
            "nutrition": nutrition,
        })
    return {"new_meals": meals}


# ---------------- 节点 3：记账 ----------------
def update_log(state: DietState) -> dict:
    """把新餐食追加到今日记录，更新累计值并落盘。"""
    day = load_today()
    for meal in state.get("new_meals", []):
        day["meals"].append(meal)
        for k in ("calories", "protein", "carbs", "fat"):
            day["totals"][k] = round(day["totals"][k] + meal["nutrition"][k], 1)
    save(day)
    return {
        "daily_meals": day["meals"],
        "daily_totals": day["totals"],
        "date": day["date"],
    }


# ---------------- 节点 4：点评 ----------------
def feedback(state: DietState) -> dict:
    """对比目标，给一句人话点评。"""
    totals = state["daily_totals"]
    goals = state.get("goals") or DEFAULT_GOALS

    if not state.get("new_meals"):
        names = ", ".join(m["name"] for m in state.get("daily_meals", [])[-3:])
        return {"feedback": f"没识别出食物（库里有 {len(FOOD_DB)} 种常见食物，换个说法试试，比如'两碗米饭'）。今天已记：{names or '无'}。"}

    lines = []
    for meal in state["new_meals"]:
        n = meal["nutrition"]
        lines.append(f"{meal['name']}({meal['amount']}): {n['calories']}kcal 蛋白{n['protein']}g")

    tips = []
    if totals["protein"] < goals["protein"] * 0.5:
        tips.append("蛋白还差不少，晚上加个鸡蛋或鸡胸肉？")
    if totals["calories"] > goals["calories"]:
        tips.append("热量超标了，晚上吃清淡点。")
    if totals["carbs"] > goals["carbs"] * 0.8 and totals["protein"] < goals["protein"] * 0.6:
        tips.append("碳水偏高、蛋白偏低，下次多点肉少点饭。")

    summary = (f"已记录：{'；'.join(lines)}\n"
               f"今日累计：{totals['calories']}kcal / 蛋白{totals['protein']}g / "
               f"碳水{totals['carbs']}g / 脂肪{totals['fat']}g")
    if tips:
        summary += "\n💡 " + " ".join(tips)
    else:
        summary += "\n💡 今天吃得不错，继续保持！"
    return {"feedback": summary}


def build_graph():
    """组装并编译图。"""
    g = StateGraph(DietState)
    g.add_node("classify_intent", classify_intent)
    g.add_node("conversation_response", conversation_response)
    g.add_node("parse_meal", parse_meal)
    g.add_node("estimate_nutrition", estimate_nutrition_node)
    g.add_node("update_log", update_log)
    g.add_node("feedback", feedback)
    g.set_entry_point("classify_intent")
    g.add_conditional_edges(
        "classify_intent",
        route_intent,
        {"log_meal": "parse_meal", "conversation": "conversation_response"},
    )
    g.add_edge("conversation_response", END)
    g.add_edge("parse_meal", "estimate_nutrition")
    g.add_edge("estimate_nutrition", "update_log")
    g.add_edge("update_log", "feedback")
    g.add_edge("feedback", END)
    return g.compile()
