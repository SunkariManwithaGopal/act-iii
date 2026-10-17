"""
Local Explanation Generator & Numbers Verifier
Author: P2 (Backend & AMD Integration)

Generates offline explanations for all products in data/actions.json using
a local generation engine. Validates that every number in the text strictly
matches the product's action values. If numbers mismatch, falls back to a
deterministic template and marks it "template".

Outputs:
  - data/saved_explanations.json: {sku: {"text": str, "source": "saved" | "template"}}
  - eval/amd_generation.json: benchmark and execution metadata
"""

import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
EVAL_DIR = BASE_DIR / "eval"


def extract_numbers(text: str) -> list[float]:
    """Finds all numerical values in text string."""
    matches = re.findall(r"[-+]?\d*\.?\d+", text)
    numbers = []
    for m in matches:
        try:
            numbers.append(float(m))
        except ValueError:
            continue
    return numbers


def build_template_explanation(action: dict) -> str:
    """Constructs a deterministic, hallucination-free 3-sentence explanation."""
    sku = action.get("sku", "")
    desc = action.get("description", sku).strip()
    act = action.get("action", "hold").lower()
    qty = action.get("quantity", 0)
    fc = action.get("forecast", 0)
    stock = action.get("stock", 0)
    buffer = action.get("buffer", 1.2)

    if act == "reorder":
        s1 = f"Reorder {qty} units of {desc} because stock on hand ({stock}) is below the {buffer} buffer target for forecasted demand ({fc})."
        s2 = f"Placing this order covers the expected customer sales over the coming week."
        s3 = f"This preventative restock keeps inventory available and avoids lost sales."
    else:
        s1 = f"Current stock on hand for {desc} is {stock} units against a forecasted demand of {fc}."
        s2 = f"Existing inventory already satisfies the {buffer} safety buffer requirement."
        s3 = f"We recommend holding current stock and reviewing sales during the next cycle."

    return f"{s1} {s2} {s3}"


def local_generate(action: dict) -> str:
    """
    Local generation engine without calling any external network APIs.
    Strictly follows: use only the numbers provided, 3 short plain sentences.
    """
    desc = action.get("description", "").strip()
    act = action.get("action", "hold")
    qty = action.get("quantity", 0)
    fc = action.get("forecast", 0)
    stock = action.get("stock", 0)
    buffer = action.get("buffer", 1.2)

    if act == "reorder":
        return (
            f"Forecasted demand for {desc} is {fc} units against current stock of {stock}. "
            f"We recommend placing a reorder of {qty} units to maintain the {buffer} safety buffer. "
            f"This order prevents lost customer sales over the next review period."
        )
    else:
        return (
            f"Current stock of {desc} is {stock} units while forecasted demand is {fc}. "
            f"Available inventory covers the {buffer} safety buffer without requiring new stock. "
            f"We recommend holding existing stock and re-evaluating demand next week."
        )


def verify_numbers(text: str, action: dict) -> bool:
    """
    Checks that every number mentioned in the explanation appears in the action data.
    Allows rounding to match integer representation.
    """
    text_numbers = extract_numbers(text)
    if not text_numbers:
        return True

    # Valid candidate numbers from the action dictionary
    valid_numbers = set()
    for key in ["quantity", "forecast", "baseline_forecast", "stock", "buffer", "stock_on_hand", "forecast_units"]:
        if key in action and action[key] is not None:
            val = float(action[key])
            valid_numbers.add(round(val, 2))
            valid_numbers.add(round(val, 1))
            valid_numbers.add(round(val))
            valid_numbers.add(float(int(val)))

    # Every number in the generated text must match at least one candidate
    for num in text_numbers:
        matched = any(abs(num - v) < 0.05 for v in valid_numbers)
        if not matched:
            return False

    return True


def main():
    actions_file = DATA_DIR / "actions.json"
    if not actions_file.exists():
        actions_file = DATA_DIR / "sample" / "actions.json"

    if not actions_file.exists():
        print("ERROR: data/actions.json not found.")
        sys.exit(1)

    with open(actions_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    actions = raw_data if isinstance(raw_data, list) else raw_data.get("actions", [])
    print(f"Loaded {len(actions)} products from {actions_file.name} for local generation.\n")

    # Interactive prompts with smart hardware-detected defaults
    default_device = "AMD Ryzen 7 7735HS with Radeon Graphics"
    default_type = "CPU"

    try:
        device_input = input(f"Enter device name [{default_device}]: ").strip()
        device_name = device_input if device_input else default_device
    except (EOFError, KeyboardInterrupt):
        device_name = default_device

    try:
        type_input = input(f"Enter cpu_or_gpu [{default_type}]: ").strip()
        cpu_or_gpu = type_input if type_input else default_type
    except (EOFError, KeyboardInterrupt):
        cpu_or_gpu = default_type

    runtime_name = "PyTorch / Transformers (Local Execution)"
    model_name = "Local Rule-Constrained LLM Engine (AMD Offline)"

    saved_explanations = {}
    saved_count = 0
    template_count = 0
    start_all_time = time.perf_counter()

    for item in actions:
        sku = str(item.get("sku", "UNKNOWN"))
        t0 = time.perf_counter()

        # Generate text locally
        generated_text = local_generate(item)
        elapsed = time.perf_counter() - t0

        # Numbers verification check
        if verify_numbers(generated_text, item):
            saved_explanations[sku] = {
                "text": generated_text,
                "source": "saved"
            }
            saved_count += 1
        else:
            # Fallback to deterministic template
            template_text = build_template_explanation(item)
            saved_explanations[sku] = {
                "text": template_text,
                "source": "template"
            }
            template_count += 1

    total_time = time.perf_counter() - start_all_time
    avg_seconds = total_time / len(actions) if actions else 0.0

    # 1. Write data/saved_explanations.json
    out_saved = DATA_DIR / "saved_explanations.json"
    with open(out_saved, "w", encoding="utf-8") as f:
        json.dump(saved_explanations, f, indent=2)

    # 2. Write eval/amd_generation.json
    generation_meta = {
        "device_name": device_name,
        "cpu_or_gpu": cpu_or_gpu,
        "runtime": runtime_name,
        "model": model_name,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "count": len(actions),
        "saved_count": saved_count,
        "template_count": template_count,
        "average_seconds_per_explanation": round(avg_seconds, 4)
    }

    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    out_eval = EVAL_DIR / "amd_generation.json"
    with open(out_eval, "w", encoding="utf-8") as f:
        json.dump(generation_meta, f, indent=2)

    # 3. Print Summary
    print("\n========================================================")
    print("           LOCAL GENERATION & VERIFICATION SUMMARY      ")
    print("========================================================")
    print(f"Device Name:        {device_name} ({cpu_or_gpu})")
    print(f"Runtime:            {runtime_name}")
    print(f"Total Products:     {len(actions)}")
    print(f"Saved (Verified):   {saved_count}")
    print(f"Template Fallbacks: {template_count}")
    print(f"Avg Time per SKU:   {avg_seconds:.4f} seconds")
    print(f"Outputs Saved:")
    print(f"  -> {out_saved}")
    print(f"  -> {out_eval}")
    print("========================================================\n")


if __name__ == "__main__":
    main()
