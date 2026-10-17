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
    
    # Check no NaNs across all three methods
    for m in ["baseline", "seasonal", "smoothed"]:
        assert not np.isnan(results[m]["forecast_error"])
        assert not np.isnan(results[m]["avg_leftover_units"])
        assert not np.isnan(results[m]["lost_value"])
        assert results[m]["lost_units"] >= 0
    
    # Check actions length
    assert len(actions) == 3

def test_zero_demand_no_lost_units():
    # Create fake data with zero demand in test window
    dates = pd.date_range(start='2009-12-07', periods=120, freq='W-MON')
    df = pd.DataFrame({"SKU_000": [10.0]*112 + [0.0]*8}, index=dates)
    products = pd.DataFrame({"sku": ["SKU_000"], "description": ["A"], "average_price": [10.0]})
    
    results, _ = run_replay(df, products, test_weeks=8)
    for m in ["baseline", "seasonal", "smoothed"]:
        assert results[m]["lost_units"] == 0
        assert results[m]["lost_value"] == 0.0

def test_actions_method_options():
    # Construct a dataset where seasonal forecast is higher than baseline forecast.
    # Total weeks: 68 (60 train weeks, 8 test weeks).
    # Last year at week 68 - 52 = 16 has a surge of 60 units against a base of 20 units (ratio = 2.0).
    # In recent weeks up to index 68, demand is steady at 10 units.
    # Baseline forecast at week 68 will be 10.0.
    # Seasonal forecast at week 68 will be 20.0 (higher).
    n_weeks = 68
    dates = pd.date_range(start='2009-12-07', periods=n_weeks, freq='W-MON')
    data = [10.0] * n_weeks
    data[16] = 60.0
    df = pd.DataFrame({"SKU_TEST": data}, index=dates)
    products = pd.DataFrame({"sku": ["SKU_TEST"], "description": ["Test Item"], "average_price": [10.0]})
    
    res_base, act_base = run_replay(df, products, test_weeks=8, actions_method="baseline")
    res_seas, act_seas = run_replay(df, products, test_weeks=8, actions_method="seasonal")
    res_smooth, act_smooth = run_replay(df, products, test_weeks=8, actions_method="smoothed")
    res_auto, act_auto = run_replay(df, products, test_weeks=8, actions_method="auto")
    
    # Check results are identical regardless of actions_method across all options
    assert res_base == res_seas == res_smooth == res_auto
    
    # Check forecasts in actions
    assert act_base[0]["baseline_forecast"] == act_seas[0]["baseline_forecast"] == act_smooth[0]["baseline_forecast"]
    assert act_base[0]["forecast"] == act_base[0]["baseline_forecast"]
    assert act_seas[0]["forecast"] > act_base[0]["forecast"]
    
    # Check baseline gives lower quantity when seasonal forecast is higher
    assert act_base[0]["quantity"] < act_seas[0]["quantity"]

    # Check auto behavior: chooses smoothed if smoothed error < baseline error, else baseline
    if res_auto["smoothed"]["forecast_error"] < res_auto["baseline"]["forecast_error"]:
        assert act_auto[0]["forecast"] == act_smooth[0]["forecast"]
    else:
        assert act_auto[0]["forecast"] == act_base[0]["forecast"]
