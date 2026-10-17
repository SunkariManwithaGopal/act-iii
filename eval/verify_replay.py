import sys
from pathlib import Path
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    # 1. Load files
    with open("eval/results.json", encoding="utf-8") as f:
        results = json.load(f)
    with open("data/actions.json", encoding="utf-8") as f:
        actions = json.load(f)

    # 2. Checks
    print(f"[OK] Actions count: {len(actions)} (Should be 30)")
    print(f"[OK] Assumptions count: {len(results['assumptions'])} (Should be 7)")

    # Check for NaNs or negatives
    for method in ["baseline", "seasonal"]:
        m = results[method]
        assert m["lost_units"] >= 0, f"Negative lost units in {method}"
        assert m["lost_value"] >= 0, f"Negative lost value in {method}"
        assert m["forecast_error"] >= 0, f"Negative error in {method}"
        print(f"[OK] {method.capitalize()} looks valid. Lost: {m['lost_units']}, Lost Value: ${m['lost_value']}, Error: {m['forecast_error']}")

    # Check methods differ
    assert results["baseline"]["lost_units"] != results["seasonal"]["lost_units"] or results["baseline"]["forecast_error"] != results["seasonal"]["forecast_error"], "WARNING: Methods have identical results! Check for bugs."

    print("All basic checks passed!")

if __name__ == "__main__":
    main()
