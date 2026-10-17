import pytest
from forecasting.tune import load_pre_test, window_error, N_TEST
from forecasting.methods import baseline


def test_test_weeks_are_dropped():
    weekly, ts = load_pre_test()
    assert len(weekly) == ts


def test_window_cannot_reach_test_period():
    weekly, ts = load_pre_test()
    with pytest.raises(AssertionError):
        window_error(weekly, ts - 4, ts + 1, baseline)

