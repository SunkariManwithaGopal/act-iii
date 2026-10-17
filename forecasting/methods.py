import pandas as pd
import numpy as np

def baseline(s: pd.Series, t: int) -> float:
    """
    Simple average of the previous 4 weeks up to index t.
    """
    start = max(0, t - 4)
    window = s.iloc[start:t]
    if len(window) == 0:
        return 0.0
    val = float(window.mean())
    return 0.0 if np.isnan(val) else val

def seasonal(s: pd.Series, t: int, alpha: float = 0.4) -> float:
    """
    Recent level (exponential weighted mean of all past weeks) times
    last year's same-week ratio, clipped to 0.5x-2.0x. Uses only s.iloc[:t].
    """
    past = s.iloc[:t]
    if len(past) == 0:
        return 0.0
    level = past.ewm(alpha=alpha, adjust=False).mean().iloc[-1]
    ratio = 1.0
    if t >= 56:
        base = s.iloc[t - 56:t - 52].mean()
        if base > 0 and not np.isnan(base):
            ratio = float(np.clip(s.iloc[t - 52] / base, 0.5, 2.0))
    out = level * ratio
    return 0.0 if np.isnan(out) else float(out)
