from __future__ import annotations

import json
import os
from typing import Any


def _format_change(value: Any) -> str:
    if value is None:
        return "not available"
    try:
        if value != value:
            return "not available"
        direction = "up" if value >= 0 else "down"
        return f"{direction} {abs(float(value)):.1f}%"
    except (TypeError, ValueError):
        return "not available"


def deterministic_summary(kpis: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"Units were {_format_change(kpis.get('units_change_vs_previous_pct'))} versus the previous day.",
            f"Orders were {_format_change(kpis.get('order_count_change_vs_previous_pct'))} versus the previous day.",
            f"Average order size was {_format_change(kpis.get('average_order_size_change_vs_avg7_pct'))} versus the seven-day average.",
            f"Waste rate was {_format_change(kpis.get('waste_rate_pct_change_vs_avg7_pct'))} versus the seven-day average.",
        ]
    )


def llm_summary(kpis: dict[str, Any]) -> str:
    api_key = os.getenv("LLM_API_KEY")
    model = os.getenv("LLM_MODEL")
    if not api_key or not model:
        raise RuntimeError("LLM_API_KEY and LLM_MODEL are required when --use-llm is enabled")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("install the optional AI dependency with: pip install -e '.[ai]'") from exc

    client_options: dict[str, str] = {"api_key": api_key}
    if os.getenv("LLM_BASE_URL"):
        client_options["base_url"] = os.environ["LLM_BASE_URL"]
    client = OpenAI(**client_options)
    response = client.chat.completions.create(
        model=model,
        temperature=0.1,
        max_tokens=180,
        messages=[
            {
                "role": "system",
                "content": (
                    "Summarize synthetic retail KPIs for a manager in no more than four short bullets. "
                    "State only supported observations, do not invent causes, and label missing comparisons."
                ),
            },
            {"role": "user", "content": json.dumps(kpis, ensure_ascii=True, default=str)},
        ],
    )
    return response.choices[0].message.content or ""

