import json
import pandas as pd

def main():
    # 1. Load files
    with open("eval/results.json") as f:
        results = json.load(f)
    with open("data/actions.json") as f:
        actions = json.load(f)

    # 2. Checks
    print(f"✅ Actions count: {len(actions)} (Should be 30)")
    print(f"✅ Assumptions count: {len(results['assumptions'])} (Should be 6)")

    # Check for NaNs or negatives
    for method in ["baseline", "seasonal"]:
        m = results[method]
        assert m["lost_units"] >= 0, f"Negative lost units in {method}"
        assert m["forecast_error"] >= 0, f"Negative error in {method}"
        print(f"✅ {method.capitalize()} looks valid. Lost: {m['lost_units']}, Error: {m['forecast_error']}")

    # Check methods differ
    assert results["baseline"]["lost_units"] != results["seasonal"]["lost_units"] or results["baseline"]["forecast_error"] != results["seasonal"]["forecast_error"], "⚠️ WARNING: Methods have identical results! Check for bugs."

    print("🎉 All basic checks passed!")

if __name__ == "__main__":
    main()
