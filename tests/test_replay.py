import pytest
import pandas as pd
import numpy as np
from tests.make_fake_weekly import fake_weekly
from forecasting.replay import run_replay

def test_replay_outputs_valid():
    df = fake_weekly(n_weeks=120, n_skus=3, seed=0)
    products = pd.DataFrame({
        "sku": ["SKU_000", "SKU_001", "SKU_002"],
        "description": ["A", "B", "C"],
        "average_price": [10.0, 15.0, 20.0]
    })
    
    results, actions = run_replay(df, products, test_weeks=8)
    
    # Check no NaNs
    assert not np.isnan(results["baseline"]["forecast_error"])
    assert not np.isnan(results["seasonal"]["avg_leftover_units"])
    assert not np.isnan(results["baseline"]["lost_value"])
    assert not np.isnan(results["seasonal"]["lost_value"])
    
    # Check actions length
    assert len(actions) == 3

def test_zero_demand_no_lost_units():
    # Create fake data with zero demand in test window
    dates = pd.date_range(start='2009-12-07', periods=120, freq='W-MON')
    df = pd.DataFrame({"SKU_000": [10.0]*112 + [0.0]*8}, index=dates)
    products = pd.DataFrame({"sku": ["SKU_000"], "description": ["A"], "average_price": [10.0]})
    
    results, _ = run_replay(df, products, test_weeks=8)
    assert results["baseline"]["lost_units"] == 0
    assert results["seasonal"]["lost_units"] == 0
    assert results["baseline"]["lost_value"] == 0.0
    assert results["seasonal"]["lost_value"] == 0.0
