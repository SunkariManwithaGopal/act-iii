"""Tune a gentler seasonal variant using ONLY weeks before the test window.
Does not edit forecasting/methods.py. Never reads or scores the last 8 weeks.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from forecasting.methods import baseline, seasonal

N_TEST = 8
ALPHAS = [0.2, 0.4, 0.6]
WS = [0, 0.25, 0.5, 0.75, 1.0]


def load_pre_test(path="data/weekly_units.parquet"):
    """Load the data and DROP the test weeks immediately."""
    full = pd.read_parquet(path)
    test_start = len(full) - N_TEST
    weekly = full.iloc[:test_start]          # test weeks are gone from here on
    assert len(weekly) == test_start
    assert len(weekly) + N_TEST == len(full)
    return weekly, test_start


def seasonal_variant(s, t, alpha, w):
    past = s.iloc[:t]
    level = past.ewm(alpha=alpha, adjust=False).mean().iloc[-1]
    ratio = 1.0
    if t >= 56:
        base = s.iloc[t - 56:t - 52].mean()
        if base > 0:
            ratio = float(np.clip(s.iloc[t - 52] / base, 0.5, 2.0))
    return float(level * (1 + w * (ratio - 1)))


def window_error(weekly, start, end, fn):
    """Total absolute miss / total actual units, one week ahead."""
    assert 0 <= start < end <= len(weekly), "window reaches into the test period"
    miss = total = 0.0
    for sku in weekly.columns:
        s = weekly[sku]
        for t in range(start, end):
            actual = float(s.iloc[t])
            miss += abs(fn(s, t) - actual)
            total += actual
    return miss / total


def sanity_check(weekly, windows):
    for start, end in windows.values():
        for sku in weekly.columns:
            s = weekly[sku]
            for t in range(start, end):
                a = seasonal_variant(s, t, 0.4, 1.0)
                b = seasonal(s, t)
                if not np.isclose(a, b, rtol=1e-9, atol=1e-9):
                    raise AssertionError(f"variant != methods.seasonal for {sku} t={t}: {a} vs {b}")
    print("Sanity check passed: alpha=0.4, w=1 matches methods.seasonal everywhere.")


def main():
    weekly, ts = load_pre_test()
    windows = {"A": (ts - 16, ts - 8), "B": (ts - 8, ts)}
    print(f"Weeks available for tuning: {ts} (test window excluded). "
          f"A = weeks {windows['A']}, B = weeks {windows['B']}")
    sanity_check(weekly, windows)

    base = {k: window_error(weekly, a, b, baseline) for k, (a, b) in windows.items()}
    base["avg"] = (base["A"] + base["B"]) / 2

    rows = []
    for alpha in ALPHAS:
        for w in WS:
            fn = lambda s, t, al=alpha, ww=w: seasonal_variant(s, t, al, ww)
            e = {k: window_error(weekly, a, b, fn) for k, (a, b) in windows.items()}
            rows.append({"alpha": alpha, "w": w, "error_A": e["A"], "error_B": e["B"],
                         "avg": (e["A"] + e["B"]) / 2,
                         "beats_baseline_both": e["A"] < base["A"] and e["B"] < base["B"]})

    print(f"\n{'setting':<18}{'error A':>10}{'error B':>10}{'average':>10}  beats baseline on both?")
    for r in rows:
        print(f"alpha={r['alpha']}, w={r['w']:<5}{r['error_A']:>10.4f}{r['error_B']:>10.4f}"
              f"{r['avg']:>10.4f}  {'YES' if r['beats_baseline_both'] else 'no'}")
    print(f"{'BASELINE':<18}{base['A']:>10.4f}{base['B']:>10.4f}{base['avg']:>10.4f}")

    best = min(rows, key=lambda r: r["avg"])
    adoptable = [r for r in rows if r["beats_baseline_both"]]
    print(f"\nBest setting by average error: alpha={best['alpha']}, w={best['w']} "
          f"(avg {best['avg']:.4f} vs baseline {base['avg']:.4f})")
    if adoptable:
        print(f"{len(adoptable)} setting(s) beat the baseline on BOTH windows (adoptable).")
    else:
        print("NO setting beats the baseline on both windows. Nothing is adoptable.")

    Path("eval").mkdir(exist_ok=True)
    with open("eval/tuning.json", "w") as f:
        json.dump({"windows_weeks": {k: list(v) for k, v in windows.items()},
                   "test_window_used": False,
                   "baseline": {k: round(v, 4) for k, v in base.items()},
                   "settings": [{**r, **{k: round(r[k], 4) for k in ("error_A", "error_B", "avg")}} for r in rows],
                   "best_by_average": {"alpha": best["alpha"], "w": best["w"], "avg": round(best["avg"], 4)},
                   "any_adoptable": bool(adoptable)}, f, indent=2)
    print("Saved eval/tuning.json")


if __name__ == "__main__":
    main()
