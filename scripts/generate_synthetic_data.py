#!/usr/bin/env python3
"""
Synthetic Market Data Generator.
Creates realistic, offline multi-asset time series for testing
the Macro Flow Stock Navigator skill without internet access.
Contains NO sensitive or Protected Health Information (PHI).
"""

import json
import os
import argparse
from datetime import datetime
import numpy as np
import pandas as pd

def generate_synthetic_dataset(
    output_path: str,
    lookback_days: int = 150,
    seed: int = 101
) -> None:
    """
    Generates synthetic time series for macro ETFs and target stock tickers.
    """
    np.random.seed(seed)
    dates = [d.strftime("%Y-%m-%d") for d in pd.date_range(end=datetime.now(), periods=lookback_days, freq="B")]
    n = len(dates)

    # 1. Base Benchmark Market (SPY)
    spy_drift = 0.0004
    spy_vol = 0.010
    spy_returns = np.random.normal(spy_drift, spy_vol, n)
    spy_prices = 500.0 * np.cumprod(1 + spy_returns)

    # 2. Equal Weight RSP (Equal weight vs SPY)
    rsp_returns = (0.7 * spy_returns) + np.random.normal(0.0002, 0.008, n)
    rsp_prices = 162.0 * np.cumprod(1 + rsp_returns)

    # 3. Gold GLD (Low correlation)
    gld_returns = (-0.15 * spy_returns) + np.random.normal(0.0003, 0.007, n)
    gld_prices = 215.0 * np.cumprod(1 + gld_returns)

    # 4. Nasdaq QQQ (Tech momentum, Beta ~ 1.25)
    qqq_returns = (1.25 * spy_returns) + np.random.normal(0.0004, 0.008, n)
    qqq_prices = 450.0 * np.cumprod(1 + qqq_returns)

    # 5. Russell 2000 IWM (Small Cap, Beta ~ 1.20)
    iwm_returns = (1.15 * spy_returns) + np.random.normal(0.0001, 0.012, n)
    iwm_prices = 205.0 * np.cumprod(1 + iwm_returns)

    # 6. SPHB (High Beta S&P)
    sphb_returns = (1.45 * spy_returns) + np.random.normal(0.0002, 0.011, n)
    sphb_prices = 88.0 * np.cumprod(1 + sphb_returns)

    # 7. SPLV (Low Volatility S&P)
    splv_returns = (0.55 * spy_returns) + np.random.normal(0.0001, 0.005, n)
    splv_prices = 68.0 * np.cumprod(1 + splv_returns)

    # 8. XLY (Consumer Discretionary)
    xly_returns = (1.10 * spy_returns) + np.random.normal(0.0002, 0.009, n)
    xly_prices = 185.0 * np.cumprod(1 + xly_returns)

    # 9. XLP (Consumer Staples)
    xlp_returns = (0.50 * spy_returns) + np.random.normal(0.0001, 0.005, n)
    xlp_prices = 78.0 * np.cumprod(1 + xlp_returns)

    # 10. VIX (Mean-reverting fear index)
    vix_base = 15.0
    vix = np.zeros(n)
    vix[0] = 14.5
    for i in range(1, n):
        # Negative correlation with SPY return + mean reversion
        ret_shock = -spy_returns[i] * 120.0
        vix[i] = vix[i-1] + 0.15 * (vix_base - vix[i-1]) + ret_shock + np.random.normal(0, 0.6)
        vix[i] = np.clip(vix[i], 11.0, 42.0)

    # 11. Stock Tickers (Various archetypes)
    tickers_config = {
        "GOOG": {"start": 178.0, "beta": 1.25, "drift": 0.0005, "idiosyncratic": 0.010},
        "GOOGL": {"start": 178.0, "beta": 1.25, "drift": 0.0005, "idiosyncratic": 0.010},
        "SOFI": {"start": 9.80, "beta": 1.95, "drift": 0.0003, "idiosyncratic": 0.025},
        "NVDA": {"start": 128.0, "beta": 1.85, "drift": 0.0012, "idiosyncratic": 0.018},
        "AAPL": {"start": 228.0, "beta": 1.10, "drift": 0.0004, "idiosyncratic": 0.009},
        "MSFT": {"start": 435.0, "beta": 1.15, "drift": 0.0005, "idiosyncratic": 0.009},
        "TSLA": {"start": 215.0, "beta": 2.10, "drift": 0.0002, "idiosyncratic": 0.028},
        "JNJ": {"start": 162.0, "beta": 0.55, "drift": 0.0001, "idiosyncratic": 0.006},
        "CAT": {"start": 355.0, "beta": 1.30, "drift": 0.0004, "idiosyncratic": 0.012},
        "JPM": {"start": 210.0, "beta": 1.15, "drift": 0.0004, "idiosyncratic": 0.011},
    }

    dataset = {
        "dates": dates,
        "SPY": [round(x, 2) for x in spy_prices],
        "SPX": [round(x * 10.0, 2) for x in spy_prices],
        "RSP": [round(x, 2) for x in rsp_prices],
        "GLD": [round(x, 2) for x in gld_prices],
        "QQQ": [round(x, 2) for x in qqq_prices],
        "IWM": [round(x, 2) for x in iwm_prices],
        "SPHB": [round(x, 2) for x in sphb_prices],
        "SPLV": [round(x, 2) for x in splv_prices],
        "XLY": [round(x, 2) for x in xly_prices],
        "XLP": [round(x, 2) for x in xlp_prices],
        "VIX": [round(x, 2) for x in vix],
    }

    for sym, cfg in tickers_config.items():
        sym_ret = (cfg["beta"] * spy_returns) + np.random.normal(cfg["drift"], cfg["idiosyncratic"], n)
        sym_prices = cfg["start"] * np.cumprod(1 + sym_ret)
        dataset[sym] = [round(x, 2) for x in sym_prices]

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(dataset, f, indent=2)

    print(f"[SUCCESS] Generated synthetic market dataset with {len(dataset)} series across {n} trading days.")
    print(f"[OUTPUT] Saved to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic financial market dataset.")
    parser.add_argument(
        "--output",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "..", "sample_data", "synthetic_market_data.json"),
        help="Target output JSON path"
    )
    parser.add_argument("--days", type=int, default=150, help="Number of trading days to simulate")
    parser.add_argument("--seed", type=int, default=101, help="Random seed for reproducibility")
    args = parser.parse_args()

    generate_synthetic_dataset(args.output, args.days, args.seed)
