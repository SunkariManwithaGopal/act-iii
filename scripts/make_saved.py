"""
Pre-generate and Save Explanations Script
Author: P2 (Backend & AMD Integration)

Reads data/actions.json (or sample fallback), calls llm.explain.explain for each product,
and writes data/saved_explanations.json as {sku: text}.
"""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from llm.explain import explain, generate_fallback_stub
DATA_DIR = BASE_DIR / "data"

def main():
    actions_file = DATA_DIR / "actions.json"
    if not actions_file.exists():
        actions_file = DATA_DIR / "sample" / "actions.json"

    if not actions_file.exists():
        print("ERROR: Neither data/actions.json nor data/sample/actions.json found.")
        return

    with open(actions_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    actions = data.get("actions", [])
    print(f"Loaded {len(actions)} products from {actions_file.name} to generate explanations...")

    saved_explanations = {}
    succeeded = 0
    failed = 0

    for item in actions:
        sku = str(item.get("sku", "UNKNOWN"))
        print(f"Processing SKU {sku} ({item.get('description', '')})...")
        try:
            # Try live AMD explain call
            explanation = explain(item)
            saved_explanations[sku] = explanation
            succeeded += 1
            print(f"  [SUCCESS - LIVE] {sku}")
        except Exception as e:
            # Fallback to deterministic rule-based template
            fallback = generate_fallback_stub(item)
            saved_explanations[sku] = fallback
            failed += 1
            print(f"  [FALLBACK - SAVED STUB] {sku} (Reason: {e})")

    out_file = DATA_DIR / "saved_explanations.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(saved_explanations, f, indent=2)

    print("\n========================================")
    print(f"Finished generating explanations!")
    print(f"Total Products: {len(actions)}")
    print(f"Live Calls Succeeded: {succeeded}")
    print(f"Fallback Stubs Saved: {failed}")
    print(f"Output File: {out_file}")
    print("========================================")

if __name__ == "__main__":
    main()
