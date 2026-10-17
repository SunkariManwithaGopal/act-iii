"""
AMD Token Factory Explanation Service
Author: P2 (Backend & AMD Integration)

Calls the OpenAI-compatible chat API on AMD to generate 3-sentence plain English
explanations for shop inventory reordering decisions.
"""

import json
import os
from typing import Dict, Any
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SYSTEM_PROMPT = (
    "You help a small shop buyer. Use only the numbers provided. "
    "If you are unsure, say there is not enough data. "
    "Write 3 short sentences in plain English."
)

def explain(action: Dict[str, Any]) -> str:
    """
    Calls the AMD Token Factory LLM to explain a single inventory action.
    
    Args:
        action: Dictionary containing sku, description, action, quantity,
                forecast, baseline_forecast, stock, buffer, etc.
                
    Returns:
        A 3-sentence plain English explanation string.
    """
    base_url = os.getenv("LLM_BASE_URL")
    api_key = os.getenv("LLM_API_KEY")
    model = os.getenv("LLM_MODEL")

    if not base_url or not api_key or not model or api_key == "your_amd_api_key_here":
        raise ValueError("AMD credentials not configured in environment variables.")

    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
        timeout=30.0
    )

    user_prompt = json.dumps(action, indent=2)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        max_tokens=150
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("Empty response received from AMD LLM.")

    return content.strip()


def generate_fallback_stub(action: Dict[str, Any]) -> str:
    """
    Deterministic 3-sentence fallback explanation matching system rules.
    Used when AMD server is offline or keys are not yet configured.
    """
    sku = action.get("sku", "Product")
    desc = action.get("description", sku)
    act = action.get("action", "hold").upper()
    qty = action.get("quantity", 0)
    fc = action.get("forecast", 0)
    stock = action.get("stock", 0)

    if act == "REORDER":
        return (
            f"Expected demand for {desc} is {fc} units while current stock is only {stock}. "
            f"We recommend placing a reorder of {qty} units with the 1.2x buffer to prevent stockouts. "
            f"This order ensures full inventory availability for the upcoming week."
        )
    else:
        return (
            f"Current stock of {desc} stands at {stock} units against a forecasted demand of {fc}. "
            f"Existing inventory is sufficient to cover the 1.2x safety buffer without placing a new order. "
            f"We recommend holding current stock and reviewing sales next week."
        )
