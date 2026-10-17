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

def seasonal(s: pd.Series, t: int) -> float:
    """
    Exponential weighted mean of recent trends, adjusted by the ratio
    of the same week last year (clipped to 0.5x–2.0x to prevent extreme outliers).
    """
    start = max(0, t - 4)
    recent = s.iloc[start:t]
    if len(recent) == 0:
        return 0.0
    
    recent_trend = recent.ewm(span=4).mean().iloc[-1]
    
    if t >= 52:
        val_last_year = float(s.iloc[t - 52])
        start_ly = max(0, t - 52 - 4)
        ly_window = s.iloc[start_ly:t - 52]
        ly_mean = ly_window.mean() if len(ly_window) > 0 else 0.0
        
        if ly_mean > 0 and not np.isnan(ly_mean):
            ratio = val_last_year / ly_mean
            ratio = float(np.clip(ratio, 0.5, 2.0))
            forecast = recent_trend * ratio
        else:
            forecast = recent_trend
    else:
        forecast = recent_trend
        
    return 0.0 if np.isnan(forecast) else float(forecast)
