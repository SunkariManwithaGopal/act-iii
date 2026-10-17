import sys
from pathlib import Path

# Ensure repo root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import json
import numpy as np
import pandas as pd
from forecasting.methods import baseline, seasonal

def run_replay(weekly_units: pd.DataFrame, products: pd.DataFrame, test_weeks=8):
    n_weeks = len(weekly_units)
    train_weeks = n_weeks - test_weeks
    
    results = {
        "test_weeks": test_weeks,
        "num_products": len(weekly_units.columns),
        "baseline": {"forecast_error": 0.0, "lost_units": 0, "lost_value": 0.0, "avg_leftover_units": 0.0, "leftover_value": 0.0},
        "seasonal": {"forecast_error": 0.0, "lost_units": 0, "lost_value": 0.0, "avg_leftover_units": 0.0, "leftover_value": 0.0},
        "assumptions": [
            "Public sales data from UCI Online Retail II.",
            "Stock levels are simulated, not real.",
            "1-week delivery time for all orders.",
            "Target buffer stock is 1.2x the forecast.",
            "Average price is used as a stand-in for cost/value.",
            "Test window represents the peak gift season (last 8 weeks).",
            "lost_value and leftover_value both use average price as a stand-in; we added lost_value after seeing the first results"
        ]
    }
    
    actions = []
    seasonal_final_stocks = {}

    for method_name, method_func in [("baseline", baseline), ("seasonal", seasonal)]:
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
            
            if method_name == "seasonal":
                seasonal_final_stocks[sku] = {
                    "final_stock": stock,
                    "description": description,
                    "avg_price": avg_price
                }

        results[method_name]["forecast_error"] = round(total_abs_miss / total_actual, 4) if total_actual > 0 else 0.0
        results[method_name]["lost_units"] = int(total_lost)
        results[method_name]["lost_value"] = round(total_lost_value, 2)
        results[method_name]["avg_leftover_units"] = round(sum(weekly_leftover_units) / len(weekly_leftover_units), 2) if weekly_leftover_units else 0.0
        results[method_name]["leftover_value"] = round(sum(weekly_leftover_value) / len(weekly_leftover_value), 2) if weekly_leftover_value else 0.0

    # Generate actions based on seasonal simulation end state
    for sku in weekly_units.columns:
        s = weekly_units[sku]
        info = seasonal_final_stocks[sku]
        
        try:
            seasonal_fc = float(seasonal(s, n_weeks))
            baseline_fc = float(baseline(s, n_weeks))
        except Exception:
            seasonal_fc = 0.0
            baseline_fc = 0.0
            
        if pd.isna(seasonal_fc): seasonal_fc = 0.0
        if pd.isna(baseline_fc): baseline_fc = 0.0
        
        quantity = int(np.ceil(max(0, 1.2 * seasonal_fc - info["final_stock"])))
        action = "reorder" if quantity > 0 else "hold"
        
        actions.append({
            "sku": sku,
            "description": info["description"],
            "action": action,
            "quantity": quantity,
            "forecast": round(seasonal_fc, 2),
            "baseline_forecast": round(baseline_fc, 2),
            "stock": round(info["final_stock"], 2),
            "buffer": 1.2
        })

    return results, actions

if __name__ == "__main__":
    data_dir = Path("data")
    eval_dir = Path("eval")
    eval_dir.mkdir(exist_ok=True)
    
    weekly_units = pd.read_parquet(data_dir / "weekly_units.parquet")
    products = pd.read_csv(data_dir / "products.csv")
    
    if not isinstance(weekly_units.index, pd.DatetimeIndex):
        weekly_units.index = pd.to_datetime(weekly_units.index)
        
    results, actions = run_replay(weekly_units, products, test_weeks=8)
    
    with open(eval_dir / "results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    with open(data_dir / "actions.json", "w", encoding="utf-8") as f:
        json.dump(actions, f, indent=2)
        
    print("[OK] Replay complete.")
    print(f"Baseline -> Error: {results['baseline']['forecast_error']}, Lost: {results['baseline']['lost_units']}, Lost Value: ${results['baseline']['lost_value']}")
    print(f"Seasonal -> Error: {results['seasonal']['forecast_error']}, Lost: {results['seasonal']['lost_units']}, Lost Value: ${results['seasonal']['lost_value']}")
