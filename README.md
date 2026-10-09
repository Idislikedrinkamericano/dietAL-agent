# 🍱 饭搭子 Diet Agent

一个极简的 LangGraph 饮食记录 agent：你随手发一句话，它解析食物、估算营养、记账，并给一句点评。

## 运行

```bash
pip install -r requirements.txt
python demo.py
```

```
> 午饭吃了两碗米饭和一块鸡胸肉
已记录：米饭(2碗): 520.0kcal 蛋白10.0g；鸡胸肉(1块): 165.0kcal 蛋白31.0g
今日累计：685.0kcal / 蛋白41.0g / 碳水114.0g / 脂肪4.8g
💡 蛋白还差不少，晚上加个鸡蛋或鸡胸肉？
```

命令：`/today` 看今日汇总，`/goals` 看目标，`quit` 退出。

## 图结构

```
parse_meal → estimate_nutrition → update_log → feedback
```

| 节点 | 干什么 |
|---|---|
| `parse_meal` | 把自然语言转成 `[{name, servings}]`（v1 用关键词+正则） |
| `estimate_nutrition` | 查内置食物库估算热量/蛋白/碳水/脂肪 |
| `update_log` | 追加到今日记录，累计并写入 `data/daily_log.json`（每天零点自动清零） |
| `feedback` | 对比目标生成点评 |

## 文件

- `diet_agent/state.py` — `DietState` 定义
- `diet_agent/graph.py` — 4 个节点 + 图组装
- `diet_agent/nutrition_db.py` — 30 种常见食物营养表 + 启发式解析
- `diet_agent/store.py` — JSON 持久化
- `demo.py` — 交互式 CLI

## 下一步可玩

1. **LLM 化**：`parse_meal` / `estimate_nutrition` 换成 LLM 调用，食物识别更准（`graph.py` 里留了钩子）
2. **拍照识别**：多模态输入，直接拍食物照片
3. **每日提醒**：cron 每天晚上 9 点问"今天吃了啥"
4. **周报**：按周聚合，画趋势图
