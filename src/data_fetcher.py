"""
Data fetcher for Macro Flow Stock Navigator.
Retrieves real-time and historical market data for macro ratio indicators
and target stock equities.
"""

import os
import urllib.parse
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
import requests

from src.config import (
    INDICATOR_TICKERS,
    TICKER_ARCHETYPE_LOOKUP,
    STOCK_ARCHETYPES
)

class MarketDataFetcher:
    """
    Fetches real-time and historical market data for target equities
    and macroeconomic ratio benchmarks.
    """

    MACRO_SYMBOLS = {
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

    def __init__(self, request_timeout: int = 12):
        self.timeout = request_timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def fetch_series_from_api(self, symbol: str, range_str: str = "1y") -> Optional[pd.Series]:
        """
        Fetches historical daily close price series for a given ticker symbol.
        """
        encoded_symbol = urllib.parse.quote(symbol)
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded_symbol}?range={range_str}&interval=1d"
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            if response.status_code != 200:
                return None
            data = response.json()
            result = data.get("chart", {}).get("result")
            if not result:
                return None
            
            timestamps = result[0].get("timestamp", [])
            indicators = result[0].get("indicators", {}).get("quote", [{}])[0]
            closes = indicators.get("close", [])
            
            if not timestamps or not closes:
                return None
            
            dates = [datetime.fromtimestamp(ts).strftime("%Y-%m-%d") for ts in timestamps]
            clean_pairs = [(d, float(c)) for d, c in zip(dates, closes) if c is not None and not np.isnan(c)]
            if not clean_pairs:
                return None
            
            dates_clean, closes_clean = zip(*clean_pairs)
            series = pd.Series(closes_clean, index=pd.to_datetime(dates_clean)).sort_index()
            return series
        except Exception:
            return None

    def fetch_market_and_ticker_data(
        self,
        ticker: str,
        lookback_days: int = 120
    ) -> Tuple[Dict[str, pd.Series], Dict[str, Any]]:
        """
        Fetches real price series for all 8 macro indicators and the target stock ticker.
        Returns:
            - prices_dict: Dict[str, pd.Series]
            - ticker_info: Dict[str, Any]
        """
        ticker = ticker.upper().strip()
        prices_dict: Dict[str, pd.Series] = {}

        # 1. Fetch Target Ticker Series
        target_series = self.fetch_series_from_api(ticker, range_str="1y")
        if target_series is None or len(target_series) < 5:
            # Attempt fallback via yfinance if installed
            try:
                import yfinance as yf
                df_ticker = yf.download(ticker, period="1y", progress=False, auto_adjust=True)
                if not df_ticker.empty and "Close" in df_ticker:
                    target_series = df_ticker["Close"].dropna()
            except Exception:
                pass

        if target_series is None or len(target_series) < 5:
            raise ValueError(f"Failed to fetch market data for ticker '{ticker}'. Please ensure the symbol is valid.")

        prices_dict[ticker] = target_series

        # 2. Fetch Macro Benchmark Symbols
        for name, symbol in self.MACRO_SYMBOLS.items():
            s = self.fetch_series_from_api(symbol, range_str="1y")
            if s is not None and len(s) > 5:
                prices_dict[name] = s

        # Derive SPX if needed
        if "SPX" not in prices_dict and "SPY" in prices_dict:
            prices_dict["SPX"] = prices_dict["SPY"] * 10.0

        # Calculate technical metrics for target ticker
        ticker_info = self._calculate_ticker_metrics(ticker, target_series, prices_dict.get("SPY"))
        return prices_dict, ticker_info

    def _calculate_ticker_metrics(
        self,
        ticker: str,
        target_series: pd.Series,
        spy_series: Optional[pd.Series] = None
    ) -> Dict[str, Any]:
        """
        Computes real technical metrics: Current Price, 50-MA, 200-MA, RSI(14), Beta, and Volatility.
        """
        current_price = float(target_series.iloc[-1])
        prev_price = float(target_series.iloc[-2]) if len(target_series) > 1 else current_price
        change_pct = ((current_price - prev_price) / prev_price) * 100.0

        # 50-day and 200-day Moving Averages
        ma50_series = target_series.rolling(min(50, len(target_series)), min_periods=5).mean()
        ma50 = float(ma50_series.iloc[-1])
        ma200_series = target_series.rolling(min(200, len(target_series)), min_periods=20).mean()
        ma200 = float(ma200_series.iloc[-1]) if len(target_series) >= 20 else ma50

        diff_ma50_pct = ((current_price - ma50) / ma50) * 100.0 if ma50 != 0 else 0.0
        diff_ma200_pct = ((current_price - ma200) / ma200) * 100.0 if ma200 != 0 else 0.0

        # 14-day RSI
        rsi_14 = self._calculate_rsi(target_series, period=14)

        # 30-day Annualized Historical Volatility
        returns = target_series.pct_change().dropna()
        vol_30d = float(returns.tail(30).std() * np.sqrt(252) * 100.0) if len(returns) >= 5 else 30.0

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

        # Historical series slice for interactive visualization
        tail_len = min(60, len(target_series))
        dates_tail = [d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)[:10] for d in target_series.index[-tail_len:]]
        closes_tail = [round(float(c), 2) for c in target_series.iloc[-tail_len:]]
        ma50_tail = [round(float(m), 2) if not pd.isna(m) else round(float(closes_tail[i]), 2) for i, m in enumerate(ma50_series.iloc[-tail_len:])]
        ma200_tail = [round(float(m), 2) if not pd.isna(m) else round(float(closes_tail[i]), 2) for i, m in enumerate(ma200_series.iloc[-tail_len:])]

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
            "archetype_desc": archetype_data["description"],
            "price_history": {
                "dates": dates_tail,
                "prices": closes_tail,
                "ma50": ma50_tail,
                "ma200": ma200_tail
            }
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
        Maps ticker to archetype taxonomy using known lookup or dynamic heuristics.
        """
        if ticker in TICKER_ARCHETYPE_LOOKUP:
            return TICKER_ARCHETYPE_LOOKUP[ticker]

        # Dynamic heuristics based on realized beta and volatility
        if beta > 1.45 or vol_30d > 45.0:
            return "HIGH_BETA_GROWTH"
        elif beta < 0.80 and vol_30d < 22.0:
            return "DEFENSIVE_VALUE"
        elif beta > 1.15:
            return "MEGA_CAP_TECH"
        else:
            return "CYCLICAL_INDUSTRIAL"
