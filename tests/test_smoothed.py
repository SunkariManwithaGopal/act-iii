import numpy as np
import pandas as pd
from forecasting.methods import smoothed
from forecasting.tune import load_pre_test, seasonal_variant, N_TEST


def test_smoothed_equals_tune_variant_on_validation_windows():
    weekly, ts = load_pre_test()          # test weeks already dropped
    assert len(weekly) == ts
    windows = [(ts - 16, ts - 8), (ts - 8, ts)]
    for sku in list(weekly.columns)[:3]:  # three products
        s = weekly[sku]
        for start, end in windows:
            for t in range(start, end):
                assert np.isclose(smoothed(s, t, 0.2),
                                  seasonal_variant(s, t, 0.2, 0),
                                  rtol=1e-9, atol=1e-9)


def test_smoothed_ignores_values_at_or_after_t():
    rng = np.random.default_rng(1)
    s = pd.Series(rng.integers(0, 500, 120).astype(float))
    for t in (10, 60, 100):
        before = smoothed(s, t)
        s2 = s.copy()
        s2.iloc[t:] = 99999
        assert smoothed(s2, t) == before


def test_smoothed_empty_history_is_zero():
    assert smoothed(pd.Series([1.0, 2.0]), 0) == 0.0

