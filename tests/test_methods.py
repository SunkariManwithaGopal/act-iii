import numpy as np
import pandas as pd
from forecasting.methods import baseline, seasonal


def make_series(n=120, seed=0):
    rng = np.random.default_rng(seed)
    return pd.Series(rng.integers(0, 500, n).astype(float))


def test_baseline_is_mean_of_previous_four():
    s = pd.Series([1, 2, 3, 4, 5, 6, 7, 8], dtype=float)
    assert baseline(s, 6) == (3 + 4 + 5 + 6) / 4


def test_forecast_ignores_values_at_or_after_t():
    s = make_series()
    for t in (20, 100):
        for f in (baseline, seasonal):
            before = f(s, t)
            s2 = s.copy()
            s2.iloc[t:] = 99999
            assert f(s2, t) == before

