"""
Data fetcher for Macro Flow Stock Navigator.
Retrieves market data using yfinance with offline fallback and synthetic data support.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd

from src.config import (
    INDICATOR_TICKERS,
    TICKER_ARCHETYPE_LOOKUP,
    STOCK_ARCHETYPES
)

class MarketDataFetcher:
    """
    Manages live and synthetic market data fetching, ticker metric calculations,
    and fallback handling.
    """

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), "..", "sample_data")
        os.makedirs(self.cache_dir, exist_ok=True)

    def fetch_market_and_ticker_data(
        self,
        ticker: str,
        lookback_days: int = 120,
        mode: str = "auto"
    ) -> Tuple[Dict[str, pd.Series], Dict[str, Any], bool]:
        """
        Fetches price series for all macro indicators and target ticker.
        Returns:
            - prices_dict: Dict[str, pd.Series]
            - ticker_info: Dict[str, Any]
            - is_synthetic: bool
        """
        ticker = ticker.upper().strip()

        if mode == "synthetic":
            return self._load_or_generate_synthetic_data(ticker, lookback_days)

        try:
            import yfinance as yf
            
            # List of all symbols to fetch
            symbols_map = {
                "RSP": "RSP",
                "SPY": "SPY",
                "GLD": "GLD",
                "QQQ": "QQQ",
                "IWM": "IWM",
                "SPHB": "SPHB",
                "SPLV": "SPLV",
                "XLY": "XLY",
                "XLP": "XLP",
                "VIX": "^VIX",
                "SPX": "^GSPC",
            }
            symbols_to_download = list(set(symbols_map.values()))
            if ticker not in symbols_to_download:
                symbols_to_download.append(ticker)

            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days + 60) # buffer for 50-MA

            df_all = yf.download(
                tickers=symbols_to_download,
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d"),
                progress=False,
                auto_adjust=True
            )

            if df_all.empty or "Close" not in df_all:
                if mode == "live":
                    raise ValueError(f"Failed to fetch live data for {ticker} and macro symbols.")
                return self._load_or_generate_synthetic_data(ticker, lookback_days)

            close_df = df_all["Close"]
            
            # Build price dict
            prices_dict = {}
            for name, symbol in symbols_map.items():
                if symbol in close_df.columns:
                    s = close_df[symbol].dropna()
                    if len(s) > 10:
                        prices_dict[name] = s
                elif hasattr(close_df, 'name') and close_df.name == symbol:
                    prices_dict[name] = close_df.dropna()

            # Ensure SPX exists
            if "SPX" not in prices_dict and "SPY" in prices_dict:
                prices_dict["SPX"] = prices_dict["SPY"] * 10.0

            # Target ticker series
            if ticker in close_df.columns:
                target_series = close_df[ticker].dropna()
            else:
                target_series = close_df.iloc[:, 0].dropna()

            prices_dict[ticker] = target_series

            # Calculate technical metrics for ticker
            ticker_info = self._calculate_ticker_metrics(ticker, target_series, prices_dict.get("SPY"))
            return prices_dict, ticker_info, False

        except Exception as e:
            if mode == "live":
                raise e
            # Fallback to synthetic
            return self._load_or_generate_synthetic_data(ticker, lookback_days)

    def _calculate_ticker_metrics(
        self,
        ticker: str,
        target_series: pd.Series,
        spy_series: Optional[pd.Series] = None
    ) -> Dict[str, Any]:
        """
        Computes technical indicators for target ticker: Price, 50-MA, 200-MA, RSI, Beta, Volatility.
        """
        if len(target_series) == 0:
            return self._default_ticker_metrics(ticker)

        current_price = float(target_series.iloc[-1])
        prev_price = float(target_series.iloc[-2]) if len(target_series) > 1 else current_price
        change_pct = ((current_price - prev_price) / prev_price) * 100.0

        # Moving averages
        ma50 = float(target_series.rolling(min(50, len(target_series)), min_periods=5).mean().iloc[-1])
        ma200 = float(target_series.rolling(min(200, len(target_series)), min_periods=20).mean().iloc[-1])
        
        diff_ma50_pct = ((current_price - ma50) / ma50) * 100.0 if ma50 != 0 else 0.0
        diff_ma200_pct = ((current_price - ma200) / ma200) * 100.0 if ma200 != 0 else 0.0

        # 14-day RSI
        rsi_14 = self._calculate_rsi(target_series, period=14)

        # 30-day Annualized Historical Volatility
        returns = target_series.pct_change().dropna()
        vol_30d = float(returns.tail(30).std() * np.sqrt(252) * 100.0) if len(returns) >= 5 else 35.0

        # Beta against SPY
        beta = 1.0
        if spy_series is not None and len(spy_series) > 10:
            spy_returns = spy_series.pct_change().dropna()
            aligned = pd.DataFrame({"target": returns, "spy": spy_returns}).dropna()
            if len(aligned) > 10:
                cov = np.cov(aligned["target"], aligned["spy"])[0, 1]
                var_spy = np.var(aligned["spy"])
                if var_spy > 0:
                    beta = float(cov / var_spy)

        # Classify Archetype
        archetype_key = self._classify_archetype(ticker, beta, vol_30d)
        archetype_data = STOCK_ARCHETYPES.get(archetype_key, STOCK_ARCHETYPES["MEGA_CAP_TECH"])

        return {
            "ticker": ticker,
            "current_price": round(current_price, 2),
            "change_pct": round(change_pct, 2),
            "ma50": round(ma50, 2),
            "diff_ma50_pct": round(diff_ma50_pct, 2),
            "ma200": round(ma200, 2),
            "diff_ma200_pct": round(diff_ma200_pct, 2),
            "rsi_14": round(rsi_14, 1),
            "historical_vol_30d": round(vol_30d, 1),
            "beta": round(beta, 2),
            "archetype_key": archetype_key,
            "archetype_name": archetype_data["name"],
            "archetype_desc": archetype_data["description"]
        }

    def _calculate_rsi(self, series: pd.Series, period: int = 14) -> float:
        """
        Computes Wilder's Relative Strength Index.
        """
        delta = series.diff().dropna()
        if len(delta) < period:
            return 50.0
        
        gain = delta.clip(lower=0)
        loss = -1 * delta.clip(upper=0)
        
        avg_gain = gain.rolling(window=period, min_periods=period).mean().iloc[-1]
        avg_loss = loss.rolling(window=period, min_periods=period).mean().iloc[-1]
        
        if pd.isna(avg_gain) or pd.isna(avg_loss) or (avg_gain + avg_loss) == 0:
            return 50.0
        
        rs = avg_gain / (avg_loss if avg_loss != 0 else 1e-6)
        rsi = 100.0 - (100.0 / (1.0 + rs))
        return float(rsi)

    def _classify_archetype(self, ticker: str, beta: float, vol_30d: float) -> str:
        """
        Maps ticker to archetype taxonomy using lookup or dynamic heuristics.
        """
        if ticker in TICKER_ARCHETYPE_LOOKUP:
            return TICKER_ARCHETYPE_LOOKUP[ticker]

        # Heuristic classification for arbitrary tickers
        if beta > 1.45 or vol_30d > 45.0:
            return "HIGH_BETA_GROWTH"
        elif beta < 0.80 and vol_30d < 22.0:
            return "DEFENSIVE_VALUE"
        elif beta > 1.15:
            return "MEGA_CAP_TECH"
        else:
            return "CYCLICAL_INDUSTRIAL"

    def _default_ticker_metrics(self, ticker: str) -> Dict[str, Any]:
        return {
            "ticker": ticker,
            "current_price": 100.0,
            "change_pct": 0.0,
            "ma50": 100.0,
            "diff_ma50_pct": 0.0,
            "ma200": 100.0,
            "diff_ma200_pct": 0.0,
            "rsi_14": 50.0,
            "historical_vol_30d": 25.0,
            "beta": 1.0,
            "archetype_key": "MEGA_CAP_TECH",
            "archetype_name": STOCK_ARCHETYPES["MEGA_CAP_TECH"]["name"],
            "archetype_desc": STOCK_ARCHETYPES["MEGA_CAP_TECH"]["description"]
        }

    def _load_or_generate_synthetic_data(
        self,
        ticker: str,
        lookback_days: int = 120
    ) -> Tuple[Dict[str, pd.Series], Dict[str, Any], bool]:
        """
        Generates clean synthetic market data for offline execution and testing.
        100% synthetic, zero real/PHI data.
        """
        synthetic_file = os.path.join(self.cache_dir, "synthetic_market_data.json")
        
        # Check if pre-generated file exists
        if os.path.exists(synthetic_file):
            try:
                with open(synthetic_file, "r") as f:
                    raw = json.load(f)
                dates = pd.date_range(end=datetime.now(), periods=len(raw.get("SPY", [])), freq="B")
                prices_dict = {k: pd.Series(v, index=dates) for k, v in raw.items()}
                
                # If target ticker is not in cache, synthesize it
                if ticker not in prices_dict:
                    prices_dict[ticker] = self._synthesize_ticker_series(ticker, prices_dict["SPY"], len(dates))
                
                ticker_info = self._calculate_ticker_metrics(ticker, prices_dict[ticker], prices_dict["SPY"])
                return prices_dict, ticker_info, True
            except Exception:
                pass

        # Generate on the fly
        dates = pd.date_range(end=datetime.now(), periods=lookback_days + 40, freq="B")
        n = len(dates)
        np.random.seed(42)

        # Baseline index simulation (geometric Brownian motion)
        spy_returns = np.random.normal(0.0004, 0.01, n)
        spy_prices = 500.0 * np.cumprod(1 + spy_returns)
        spy_s = pd.Series(spy_prices, index=dates)

        # Macro assets
        rsp_s = pd.Series(165.0 * np.cumprod(1 + np.random.normal(0.0003, 0.009, n)), index=dates)
        gld_s = pd.Series(210.0 * np.cumprod(1 + np.random.normal(0.0002, 0.008, n)), index=dates)
        qqq_s = pd.Series(440.0 * np.cumprod(1 + np.random.normal(0.0006, 0.013, n)), index=dates)
        iwm_s = pd.Series(205.0 * np.cumprod(1 + np.random.normal(0.0003, 0.014, n)), index=dates)
        sphb_s = pd.Series(85.0 * np.cumprod(1 + np.random.normal(0.0005, 0.015, n)), index=dates)
        splv_s = pd.Series(68.0 * np.cumprod(1 + np.random.normal(0.0002, 0.006, n)), index=dates)
        xly_s = pd.Series(185.0 * np.cumprod(1 + np.random.normal(0.0004, 0.012, n)), index=dates)
        xlp_s = pd.Series(78.0 * np.cumprod(1 + np.random.normal(0.0002, 0.005, n)), index=dates)
        vix_vals = np.clip(16.0 + np.cumsum(np.random.normal(0, 0.8, n)), 11.0, 38.0)
        vix_s = pd.Series(vix_vals, index=dates)

        prices_dict = {
            "SPY": spy_s,
            "SPX": spy_s * 10.0,
            "RSP": rsp_s,
            "GLD": gld_s,
            "QQQ": qqq_s,
            "IWM": iwm_s,
            "SPHB": sphb_s,
            "SPLV": splv_s,
            "XLY": xly_s,
            "XLP": xlp_s,
            "VIX": vix_s
        }

        # Synthesize target ticker
        target_s = self._synthesize_ticker_series(ticker, spy_s, n)
        prices_dict[ticker] = target_s

        ticker_info = self._calculate_ticker_metrics(ticker, target_s, spy_s)
        return prices_dict, ticker_info, True

    def _synthesize_ticker_series(self, ticker: str, spy_series: pd.Series, length: int) -> pd.Series:
        """
        Creates synthetic stock price path consistent with ticker's known profile.
        """
        np.random.seed(abs(hash(ticker)) % 10000)
        base_price_map = {
            "GOOG": 175.0,
            "GOOGL": 175.0,
            "SOFI": 9.50,
            "AAPL": 225.0,
            "NVDA": 125.0,
            "MSFT": 420.0,
            "TSLA": 210.0,
            "JNJ": 160.0,
            "CAT": 350.0
        }
        start_price = base_price_map.get(ticker, 100.0)
        
        # Archetype beta influence
        archetype_key = TICKER_ARCHETYPE_LOOKUP.get(ticker, "MEGA_CAP_TECH")
        beta = STOCK_ARCHETYPES[archetype_key]["default_beta"]
        
        spy_ret = spy_series.pct_change().fillna(0).values
        noise = np.random.normal(0.0002, 0.015 * beta, length)
        ticker_ret = (spy_ret * beta) + noise
        
        prices = start_price * np.cumprod(1 + ticker_ret)
        return pd.Series(prices, index=spy_series.index)
