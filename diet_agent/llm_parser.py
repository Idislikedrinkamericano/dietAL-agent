"""LLM meal parser. The model extracts food + grams; nutrition math stays deterministic."""
import json
import os
from openai import OpenAI
from .nutrition_db import FOOD_DB, ALIASES, default_unit_grams


def _strip_code_fence(text: str) -> str:
    text = text.strip()
    fence = chr(96) * 3
    if text.startswith(fence):
        lines = text.splitlines()[1:]
        if lines and lines[-1].strip() == fence:
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return text


def parse_meal_with_llm(text: str) -> list[dict]:
    allowed = [{"name": n, "household_units_g": default_unit_grams(n)} for n in FOOD_DB]
    prompt = f"""
You are a meal parser. Return JSON only:
{{"items":[{{"name":"鸡胸肉","grams":200,"amount":"200g","assumed":false}}]}}

Rules:
- name must be one of the allowed foods.
- Convert every quantity to grams.
- Explicit grams are never assumed.
- Household units (个/碗/杯/片/份/块/根/勺) may use the supplied default gram weights and must set assumed=true.
- If quantity is omitted, use one reasonable household unit from the supplied defaults and set assumed=true.
- Do not invent nutrition values.
- Do not force branded menu products into a generic food if the mapping is uncertain.
- Positive grams only, max 5000g per item.

Allowed foods:
{json.dumps(allowed, ensure_ascii=False)}
""".strip()

    client = OpenAI()
    response = client.responses.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
        input=[{"role": "system", "content": prompt}, {"role": "user", "content": text}],
    )
    payload = json.loads(_strip_code_fence(response.output_text))
    out = []
    for item in payload.get("items", []):
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        try:
            grams = float(item.get("grams"))
        except (TypeError, ValueError):
            continue
        if name in FOOD_DB and 0 < grams <= 5000:
            amount = str(item.get("amount") or f"{grams:g}g")
            out.append({"name": name, "grams": round(grams, 1), "amount": amount, "assumed": bool(item.get("assumed", False))})
    return out
