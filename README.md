# 🍱 DietAL Agent

A small LangGraph diet-tracking agent. You type what you ate; it parses the meal, estimates nutrition, saves today's log, and gives simple feedback.

[中文说明](README.zh-CN.md)

## How it works

```text
Your message
   ↓
Meal parser
   ↓
Nutrition lookup
   ↓
Daily log
   ↓
Feedback
```

With an OpenAI API key, meal parsing uses an LLM. Without a key, it falls back to a simple local parser.

Nutrition values come from the local food database instead of being guessed by the LLM.

## Run it

On macOS, open Terminal and paste this whole block:

```bash
git clone https://github.com/Idislikedrinkamericano/dietAL-agent.git
cd dietAL-agent
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python demo.py
```

After the app starts, type what you ate:

```text
> 午饭吃了两碗米饭和200g鸡胸肉
```

Useful commands:

```text
/today   show today's totals
/goals   show daily goals
/undo    remove the last logged item
quit     exit
```

## Optional: enable the LLM parser

```bash
export OPENAI_API_KEY="your-key"
python demo.py
```

Do not commit your real API key to GitHub.

## Main files

- `demo.py` — starts the app
- `diet_agent/graph.py` — LangGraph workflow
- `diet_agent/llm_parser.py` — LLM meal parsing
- `diet_agent/nutrition_db.py` — food database and nutrition calculation
- `diet_agent/store.py` — daily log storage
- `diet_agent/state.py` — shared graph state

## Current limitations

This is still a learning project. The food database is small, branded restaurant items may not be recognized accurately, and the agent does not yet have full conversational memory.

Next: nutrition tools, editable goals, better memory, and image input.
