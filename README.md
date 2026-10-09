# 🍱 饭搭子 Diet Agent

一个极简的 LangGraph 饮食记录 agent：你随手发一句话，它解析食物、估算营养、记账，并给一句点评。

## 运行

```bash
pip install -r requirements.txt
python demo.py
```

不配置 API key 也能运行：系统会自动使用原来的关键词 + 正则解析器。

如果想启用 V2 的 LLM meal parser：

```bash
export OPENAI_API_KEY="your-key"
# 可选，默认 gpt-4.1-mini
export OPENAI_MODEL="gpt-4.1-mini"
python demo.py
```

配置后，`parse_meal` 会优先调用 LLM；如果调用失败、返回格式异常，或没有识别出支持的食物，会自动回退到本地解析器。

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
| `parse_meal` | 自然语言 → `[{name, servings}]`；有 API key 时用 LLM，否则/失败时回退关键词 + 正则 |
| `estimate_nutrition` | 查内置食物库估算热量/蛋白/碳水/脂肪 |
| `update_log` | 追加到今日记录，累计并写入 `data/daily_log.json`（每天零点自动清零） |
| `feedback` | 对比目标生成点评 |

## 文件

- `diet_agent/state.py` — `DietState` 定义
- `diet_agent/graph.py` — 4 个节点 + 图组装 + LLM fallback
- `diet_agent/llm_parser.py` — OpenAI Responses API meal parser
- `diet_agent/nutrition_db.py` — 30 种常见食物营养表 + 启发式解析
- `diet_agent/store.py` — JSON 持久化
- `demo.py` — 交互式 CLI

## 下一步可玩

1. **Nutrition Tool**：把营养查询封装成显式 tool，让 Agent 真正调用工具
2. **可编辑目标**：支持“每天 1800 kcal、蛋白 140g”
3. **Memory**：理解“刚才那顿再加一个鸡蛋”
4. **LLM feedback**：让模型解释确定性的营养数据，而不是自己算热量
5. **拍照识别**：多模态输入，直接拍食物照片


## V2 设计原则

LLM 只负责自然语言理解；热量和宏量营养素仍然由本地 `FOOD_DB` 做确定性计算。这样比让模型直接“猜热量”更容易测试，也更可控。
