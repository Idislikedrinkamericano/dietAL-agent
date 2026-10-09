"""交互式 demo：直接输入吃了啥，agent 记账并点评。"""
import sys
from diet_agent import build_graph, DEFAULT_GOALS

BANNER = """
🍱 饭搭子 Diet Agent 启动！
直接输入你吃了啥，比如：午饭吃了两碗米饭和一块鸡胸肉
命令：/today 查看今日汇总，/goals 查看目标，/undo 撤销上一条，quit 退出
"""


def main() -> None:
    app = build_graph()
    goals = dict(DEFAULT_GOALS)
    print(BANNER)
    while True:
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n明天见！")
            break
        if not text:
            continue
        if text.lower() in ("quit", "exit", "退出"):
            print("明天见！")
            break
        if text == "/goals":
            print(f"今日目标：{goals['calories']}kcal / 蛋白{goals['protein']}g / "
                  f"碳水{goals['carbs']}g / 脂肪{goals['fat']}g")
            continue
        if text == "/today":
            from diet_agent.store import load_today
            day = load_today()
            t = day["totals"]
            print(f"今日已记 {len(day['meals'])} 条：{t['calories']}kcal / "
                  f"蛋白{t['protein']}g / 碳水{t['carbs']}g / 脂肪{t['fat']}g")
            continue
        if text == "/undo":
            from diet_agent.store import undo_last_meal
            removed = undo_last_meal()
            if removed:
                print(f"已撤销：{removed['name']} ({removed['amount']})")
            else:
                print("今天还没有可以撤销的记录。")
            continue
        result = app.invoke({"user_input": text, "goals": goals})
        print(result["feedback"])
        print()


if __name__ == "__main__":
    sys.exit(main())
