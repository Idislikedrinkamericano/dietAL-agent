# 🍱 DietAL Agent

A small LangGraph project that helps you log meals in plain language.

You type something like:

```text
I ate two bowls of rice and 200g of chicken breast.
```

The program will:

1. understand what foods you mentioned,
2. estimate calories and macros,
3. add the meal to today's log,
4. show your daily total,
5. give a short suggestion.

[中文说明](README.zh-CN.md)

---

## What this project is

This is a learning project for understanding how an AI agent workflow works.

The current flow is:

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

If you set an OpenAI API key, the meal parser uses an LLM.
If you do not set a key, the project still works with a simpler local parser.

Nutrition numbers are not guessed by the LLM. They are calculated from the local food database in `diet_agent/nutrition_db.py`.

---

## How to open and run it

### 1. Open Terminal

On macOS:

- press `Command + Space`
- search for `Terminal`
- open it

### 2. Download the project

Run:

```bash
git clone https://github.com/Idislikedrinkamericano/dietAL-agent.git
```

Then enter the project folder:

```bash
cd dietAL-agent
```

### 3. Create a Python environment

Run:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

After activation, you should see something like `(.venv)` at the beginning of the Terminal line.

### 4. Install the packages

Run:

```bash
python -m pip install -r requirements.txt
```

This means:

> Install all Python packages that this project needs.

You usually only need to do this once.

### 5. Start the app

Run:

```bash
python demo.py
```

This means:

> Start the DietAL Agent program.

You should then see a prompt like:

```text
🍱 饭搭子 Diet Agent 启动！
>
```

Now type what you ate and press Enter.

Example:

```text
> 午饭吃了两碗米饭和200g鸡胸肉
```

---

## Useful commands inside the app

While the app is running:

```text
/today
```

Shows today's nutrition total.

```text
/goals
```

Shows the current daily goals.

```text
quit
```

Closes the app.

---

## Optional: turn on the LLM parser

You do not need an API key to run the project.

Without a key, DietAL uses the simple local parser.

If you want the program to understand more natural sentences, set your OpenAI API key before running the app:

```bash
export OPENAI_API_KEY="your-key"
python demo.py
```

Do not put your real API key into GitHub or commit it into the repository.

You can also choose another model:

```bash
export OPENAI_MODEL="gpt-4.1-mini"
```

If the LLM call fails, the program automatically falls back to the local parser.

---

## Example

Input:

```text
午饭吃了两碗米饭和200g鸡胸肉
```

The program may produce something like:

```text
已记录：米饭(2×碗): 520.0kcal 蛋白10.0g；
鸡胸肉(2×100g): 330.0kcal 蛋白62.0g

今日累计：
850.0kcal / 蛋白72.0g / 碳水114.0g / 脂肪7.8g
```

---

## Main files

```text
dietAL-agent/
├── demo.py
├── requirements.txt
├── diet_agent/
│   ├── graph.py
│   ├── llm_parser.py
│   ├── nutrition_db.py
│   ├── state.py
│   └── store.py
```

What they do:

- `demo.py` — starts the command-line app
- `graph.py` — defines the LangGraph workflow
- `llm_parser.py` — turns natural language into structured meal data
- `nutrition_db.py` — stores food nutrition values and performs nutrition calculations
- `state.py` — defines the shared data passed through the graph
- `store.py` — saves today's food log

---

## Current limitation

This is still a small learning project.

The nutrition database currently supports only a limited set of common foods. Even when the LLM parser is enabled, unsupported foods may not be logged yet.

---

## Next steps

Planned improvements:

- turn nutrition lookup into an explicit tool,
- let users set their own calorie and protein goals,
- add memory for follow-up messages such as "add one more egg to that meal",
- improve feedback,
- support food photos later.
