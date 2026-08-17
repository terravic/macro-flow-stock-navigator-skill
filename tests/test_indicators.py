import pytest
import numpy as np
import pandas as pd
from src.indicators import MacroIndicatorCalculator

def test_slope_calculation():
    # Uptrending series
    series_up = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0, 15.0])
    slope_up = MacroIndicatorCalculator.calculate_linear_slope(series_up, lookback=5)
    assert slope_up > 0.0

    # Downtrending series
    series_down = pd.Series([15.0, 14.0, 13.0, 12.0, 11.0, 10.0])
    slope_down = MacroIndicatorCalculator.calculate_linear_slope(series_down, lookback=5)
    assert slope_down < 0.0

def test_percentile_calculation():
    series = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0])
    p_min = MacroIndicatorCalculator.calculate_percentile(series, 10.0)
    assert p_min == 0.0

    p_max = MacroIndicatorCalculator.calculate_percentile(series, 55.0)
    assert p_max == 100.0

    p_mid = MacroIndicatorCalculator.calculate_percentile(series, 35.0)
    assert 50.0 <= p_mid <= 70.0

def test_compute_all_indicators():
    dates = pd.date_range("2026-01-01", periods=60, freq="B")
    mock_data = {
        "SPY": pd.Series(500.0 + np.linspace(0, 10, 60), index=dates),
        "SPX": pd.Series(5000.0 + np.linspace(0, 100, 60), index=dates),
        "RSP": pd.Series(160.0 + np.linspace(0, 2, 60), index=dates),
        "GLD": pd.Series(210.0 + np.linspace(0, -3, 60), index=dates),
        "QQQ": pd.Series(440.0 + np.linspace(0, 15, 60), index=dates),
        "IWM": pd.Series(200.0 + np.linspace(0, 4, 60), index=dates),
        "SPHB": pd.Series(85.0 + np.linspace(0, 5, 60), index=dates),
        "SPLV": pd.Series(68.0 + np.linspace(0, 1, 60), index=dates),
        "XLY": pd.Series(180.0 + np.linspace(0, 8, 60), index=dates),
        "XLP": pd.Series(78.0 + np.linspace(0, 1, 60), index=dates),
        "VIX": pd.Series(15.0 + np.linspace(0, -2, 60), index=dates),
    }

    indicators = MacroIndicatorCalculator.compute_all_indicators(mock_data)
    assert len(indicators) == 8
    assert "RSP_SPY" in indicators
    assert "GLD_SPX" in indicators
    assert "NDX_SPX" in indicators
    assert "IWM_SPY" in indicators
    assert "SPX_GDP" in indicators
    assert "SPHB_SPLV" in indicators
    assert "XLY_XLP" in indicators
    assert "VIX_SPX" in indicators

    for k, ind in indicators.items():
        assert "current_value" in ind
        assert "ma50" in ind
        assert "trend_signal" in ind
        assert "market_meaning" in ind
