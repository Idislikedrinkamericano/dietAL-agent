"""LLM-based meal parsing with a deterministic fallback path.

The parser converts free-form meal descriptions into the same compact
[{"name": "...", "servings": 1.0}] shape used by the rest of the graph.
Nutrition math remains deterministic and is still handled by nutrition_db.py.
"""
import json
import os

from openai import OpenAI

from .nutrition_db import FOOD_DB


def _strip_code_fence(text: str) -> str:
    text = text.strip()
    fence = chr(96) * 3
    if text.startswith(fence):
        lines = text.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == fence:
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def parse_meal_with_llm(text: str) -> list[dict]:
    """Parse a meal description with an OpenAI model."""
    allowed = [{"name": name, "unit": facts["unit"]} for name, facts in FOOD_DB.items()]
    model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
    client = OpenAI()

    instructions = f"""
You are a meal parser for a nutrition logging app.
Return JSON only, with this exact shape:
{{"items":[{{"name":"food name","servings":1.0}}]}}

Rules:
- "name" MUST be one of the allowed foods listed below.
- "servings" MUST be a positive number in that food's listed base unit.
- Normalize quantities to the base unit. Example: if 鸡胸肉 uses 100g,
  then 200g鸡胸肉 => 2.0 servings.
- 半/half => 0.5. 一碗半/one and a half => 1.5.
- If a supported food is mentioned without a quantity, use 1.0.
- Ignore foods that cannot reasonably map to an allowed food.
- Do not invent nutrition values and do not add commentary.

Allowed foods and base units:
{json.dumps(allowed, ensure_ascii=False)}
""".strip()

    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": text},
        ],
    )
    raw = _strip_code_fence(response.output_text)
    payload = json.loads(raw)
    items = payload.get("items", [])
    if not isinstance(items, list):
        raise ValueError("LLM parser returned an invalid items field.")

    parsed = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        try:
            servings = float(item.get("servings"))
        except (TypeError, ValueError):
            continue
        if name in FOOD_DB and 0 < servings <= 100:
            parsed.append({"name": name, "servings": servings})
    return parsed
