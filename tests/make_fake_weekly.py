import pandas as pd
import numpy as np

def fake_weekly(n_weeks=120, n_skus=3, seed=0):
    np.random.seed(seed)
    dates = pd.date_range(start='2009-12-07', periods=n_weeks, freq='W-MON')
    data = {}
    
    for i in range(n_skus):
        sku = f"SKU_{i:03d}"
        base = np.random.randint(10, 50)
        demand = np.random.poisson(base, n_weeks).astype(float)
        
        # Add a December bump (roughly weeks 46-52 of each year)
        for year in range(n_weeks // 52):
            start_idx = year * 52 + 46
            end_idx = min(start_idx + 6, n_weeks)
            demand[start_idx:end_idx] += np.random.randint(20, 40, end_idx - start_idx)
            
        data[sku] = np.maximum(0, demand)
        
    return pd.DataFrame(data, index=dates)
