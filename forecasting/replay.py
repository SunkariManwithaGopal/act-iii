import sys
from pathlib import Path

# Ensure repo root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import argparse
import json
import numpy as np
import pandas as pd

from forecasting.methods import baseline, seasonal, smoothed

def run_replay(weekly_units: pd.DataFrame, products: pd.DataFrame, test_weeks=8, actions_method="baseline"):
    if actions_method not in ("baseline", "seasonal", "smoothed", "auto"):
        raise ValueError(f"actions_method must be 'baseline', 'seasonal', 'smoothed', or 'auto', got {actions_method}")

    n_weeks = len(weekly_units)
    train_weeks = n_weeks - test_weeks
    
    results = {
        "test_weeks": test_weeks,
        "num_products": len(weekly_units.columns),
        "baseline": {"forecast_error": 0.0, "lost_units": 0, "lost_value": 0.0, "avg_leftover_units": 0.0, "leftover_value": 0.0},
        "seasonal": {"forecast_error": 0.0, "lost_units": 0, "lost_value": 0.0, "avg_leftover_units": 0.0, "leftover_value": 0.0},
        "smoothed": {"forecast_error": 0.0, "lost_units": 0, "lost_value": 0.0, "avg_leftover_units": 0.0, "leftover_value": 0.0},
        "assumptions": [
            "Public sales data from UCI Online Retail II.",
            "Stock levels are simulated, not real.",
            "1-week delivery time for all orders.",
            "Target buffer stock is 1.2x the forecast.",
            "Average price is used as a stand-in for cost/value.",
            "test window is the 8-week pre-Christmas build-up starting 2011-10-10",
            "lost_value and leftover_value both use average price as a stand-in; we added lost_value after seeing the first results",
            "the smoothed method (exponential average, alpha 0.2) was chosen on two validation windows before the test window, after the first test results had been seen",
            "forecast error is the only measure used to choose which method drives the suggested orders"
        ]
    }
    
    actions = []
    final_stocks = {"baseline": {}, "seasonal": {}, "smoothed": {}}

    for method_name, method_func in [("baseline", baseline), ("seasonal", seasonal), ("smoothed", smoothed)]:
        total_abs_miss = 0.0
        total_actual = 0.0
        total_lost = 0.0
        total_lost_value = 0.0
        weekly_leftover_units = []
        weekly_leftover_value = []
        
        for sku in weekly_units.columns:
            s = weekly_units[sku]
            avg_price = float(products.loc[products['sku'] == sku, 'average_price'].values[0])
            description = str(products.loc[products['sku'] == sku, 'description'].values[0])
            
            # Start stock = 1.2 * mean of 4 weeks before test
            start_stock = 1.2 * s.iloc[train_weeks-4:train_weeks].mean()
            if pd.isna(start_stock): start_stock = 0.0
            
            stock = start_stock
            incoming = 0.0
            
            for t in range(train_weeks, n_weeks):
                demand = float(s.iloc[t])
                stock += incoming
                
                sold = min(stock, demand)
                lost = demand - sold
                total_lost += lost
                total_lost_value += lost * avg_price
                stock -= sold
                
                weekly_leftover_units.append(stock)
                weekly_leftover_value.append(stock * avg_price)
                
                # Forecast for next week (t+1)
                fc_next_t = t + 1 if t + 1 < n_weeks else t
                try:
                    fc_next = method_func(s, fc_next_t)
                except Exception:
                    fc_next = 0.0
                if pd.isna(fc_next): fc_next = 0.0
                
                order = max(0.0, 1.2 * fc_next - stock)
                incoming = order # arrives next week
                
                # Forecast error for current week t
                try:
                    fc_t = method_func(s, t)
                except Exception:
                    fc_t = 0.0
                if pd.isna(fc_t): fc_t = 0.0
                
                total_abs_miss += abs(fc_t - demand)
                total_actual += demand
            
            final_stocks[method_name][sku] = {
                "final_stock": stock,
                "description": description,
                "avg_price": avg_price
            }

        results[method_name]["forecast_error"] = round(total_abs_miss / total_actual, 4) if total_actual > 0 else 0.0
        results[method_name]["lost_units"] = int(total_lost)
        results[method_name]["lost_value"] = round(total_lost_value, 2)
        results[method_name]["avg_leftover_units"] = round(sum(weekly_leftover_units) / len(weekly_leftover_units), 2) if weekly_leftover_units else 0.0
        results[method_name]["leftover_value"] = round(sum(weekly_leftover_value) / len(weekly_leftover_value), 2) if weekly_leftover_value else 0.0

    # Determine which method to use for actions
    chosen_method = actions_method
    if actions_method == "auto":
        if results["smoothed"]["forecast_error"] < results["baseline"]["forecast_error"]:
            chosen_method = "smoothed"
            print(f"Auto selected 'smoothed': forecast_error {results['smoothed']['forecast_error']} < baseline {results['baseline']['forecast_error']}")
        else:
            chosen_method = "baseline"
            print(f"Auto selected 'baseline': forecast_error {results['baseline']['forecast_error']} <= smoothed {results['smoothed']['forecast_error']}")

    # Generate actions based on chosen method's end state
    for sku in weekly_units.columns:
        s = weekly_units[sku]
        info = final_stocks[chosen_method][sku]
        
        try:
            seasonal_fc = float(seasonal(s, n_weeks))
        except Exception:
            seasonal_fc = 0.0
        try:
            baseline_fc = float(baseline(s, n_weeks))
        except Exception:
            baseline_fc = 0.0
        try:
            smoothed_fc = float(smoothed(s, n_weeks))
        except Exception:
            smoothed_fc = 0.0
            
        if pd.isna(seasonal_fc): seasonal_fc = 0.0
        if pd.isna(baseline_fc): baseline_fc = 0.0
        if pd.isna(smoothed_fc): smoothed_fc = 0.0
        
        if chosen_method == "baseline":
            chosen_fc = baseline_fc
        elif chosen_method == "seasonal":
            chosen_fc = seasonal_fc
        else:
            chosen_fc = smoothed_fc
            
        quantity = int(np.ceil(max(0, 1.2 * chosen_fc - info["final_stock"])))
        action = "reorder" if quantity > 0 else "hold"
        
        actions.append({
            "sku": sku,
            "description": info["description"],
            "action": action,
            "quantity": quantity,
            "forecast": round(chosen_fc, 2),
            "baseline_forecast": round(baseline_fc, 2),
            "stock": round(info["final_stock"], 2),
            "buffer": 1.2
        })

    return results, actions

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run replay simulation")
    parser.add_argument("--actions-method", choices=["baseline", "seasonal", "smoothed", "auto"], default="baseline", help="Forecast method used for generating actions")
    args = parser.parse_args()

    data_dir = Path("data")
    eval_dir = Path("eval")
    eval_dir.mkdir(exist_ok=True)
    
    weekly_units = pd.read_parquet(data_dir / "weekly_units.parquet")
    products = pd.read_csv(data_dir / "products.csv")
    
    if not isinstance(weekly_units.index, pd.DatetimeIndex):
        weekly_units.index = pd.to_datetime(weekly_units.index)
        
    results, actions = run_replay(weekly_units, products, test_weeks=8, actions_method=args.actions_method)
    
    with open(eval_dir / "results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    with open(data_dir / "actions.json", "w", encoding="utf-8") as f:
        json.dump(actions, f, indent=2)
        
    print("[OK] Replay complete.")
    for m in ["baseline", "seasonal", "smoothed"]:
        print(f"{m.capitalize():8} -> Error: {results[m]['forecast_error']}, Lost: {results[m]['lost_units']}, Lost Value: £{results[m]['lost_value']}, Avg Leftover Units: {results[m]['avg_leftover_units']}, Leftover Value: £{results[m]['leftover_value']}")
