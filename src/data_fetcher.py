"""
Data fetcher for Macro Flow Stock Navigator.
Retrieves real-time and historical market data for macro ratio indicators
and target stock equities.
"""

import os
import math
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
        # Historical series slice for interactive visualization
        tail_len = min(60, len(target_series))
        dates_tail = [d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)[:10] for d in target_series.index[-tail_len:]]
        closes_tail = [round(float(c), 2) for c in target_series.iloc[-tail_len:]]
        ma50_tail = [round(float(m), 2) if not pd.isna(m) else round(float(closes_tail[i]), 2) for i, m in enumerate(ma50_series.iloc[-tail_len:])]
        ma200_tail = [round(float(m), 2) if not pd.isna(m) else round(float(closes_tail[i]), 2) for i, m in enumerate(ma200_series.iloc[-tail_len:])]

        # Fetch option chain for options analysis (Covered Calls & Cash-Secured Puts)
        options_data = self.fetch_option_chain(ticker, current_price, vol_30d)

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
            },
            "options_data": options_data
        }

    def fetch_option_chain(
        self,
        ticker: str,
        spot_price: float = 100.0,
        historical_vol: float = 30.0
    ) -> Dict[str, Any]:
        """
        Fetches free real-time option chain data from Yahoo Finance.
        Falls back to a high-fidelity Black-Scholes synthetic model if network is unavailable.
        """
        ticker = ticker.upper().strip()
        session = requests.Session()
        session.headers.update(self.headers)
        
        try:
            # 1. Establish Yahoo Finance cookie session and get crumb
            session.get("https://fc.yahoo.com", timeout=self.timeout)
            r_crumb = session.get("https://query2.finance.yahoo.com/v1/test/getcrumb", timeout=self.timeout)
            if r_crumb.status_code == 200:
                crumb = r_crumb.text.strip()
                encoded_ticker = urllib.parse.quote(ticker)
                r_opt = session.get(
                    f"https://query2.finance.yahoo.com/v7/finance/options/{encoded_ticker}?crumb={crumb}",
                    timeout=self.timeout
                )
                if r_opt.status_code == 200:
                    data = r_opt.json()
                    res = data.get("optionChain", {}).get("result", [])
                    if res:
                        processed = self._process_yahoo_option_chain(res[0], spot_price, historical_vol)
                        if processed and (len(processed.get("calls", [])) > 0 or len(processed.get("puts", [])) > 0):
                            return processed
        except Exception:
            pass

        # Fallback to high-fidelity Black-Scholes option chain
        return self._generate_synthetic_option_chain(ticker, spot_price, historical_vol)

    def _process_yahoo_option_chain(
        self,
        result: Dict[str, Any],
        spot_price: float,
        historical_vol: float
    ) -> Dict[str, Any]:
        """
        Parses live Yahoo Finance option chain JSON and computes Greeks & flow metrics.
        """
        exp_timestamps = result.get("expirationDates", [])
        if not exp_timestamps:
            return {}

        exp_dates = [datetime.fromtimestamp(ts).strftime("%Y-%m-%d") for ts in exp_timestamps]
        options_list = result.get("options", [])
        if not options_list:
            return {}

        first_opt = options_list[0]
        exp_ts = first_opt.get("expirationDate", exp_timestamps[0])
        selected_exp_date = datetime.fromtimestamp(exp_ts).strftime("%Y-%m-%d")
        
        # Calculate DTE
        exp_dt = datetime.fromtimestamp(exp_ts)
        now_dt = datetime.now()
        dte = max(1, (exp_dt - now_dt).days)

        raw_calls = first_opt.get("calls", [])
        raw_puts = first_opt.get("puts", [])

        # Filter and compute Greeks for calls & puts
        calls_clean = []
        puts_clean = []
        iv_samples = []

        for c in raw_calls:
            strike = float(c.get("strike", 0.0))
            bid = float(c.get("bid", 0.0))
            ask = float(c.get("ask", 0.0))
            last = float(c.get("lastPrice", 0.0))
            mid = round((bid + ask) / 2.0, 2) if (bid > 0 and ask > 0) else last
            iv = float(c.get("impliedVolatility", 0.0))
            vol = int(c.get("volume", 0) or 0)
            oi = int(c.get("openInterest", 0) or 0)
            itm = bool(c.get("inTheMoney", strike < spot_price))
            
            if iv > 0.05 and iv < 2.5:
                iv_samples.append(iv)
            eff_iv = iv if (iv > 0.05 and iv < 2.5) else (historical_vol / 100.0)

            delta, _, theta, _ = self._calculate_greeks(spot_price, strike, dte, eff_iv)
            vol_oi = round(vol / oi, 2) if oi > 0 else (round(vol / 1.0, 2) if vol > 0 else 0.0)

            calls_clean.append({
                "strike": strike,
                "bid": bid,
                "ask": ask,
                "mid": mid,
                "lastPrice": last,
                "volume": vol,
                "openInterest": oi,
                "impliedVolatility": round(eff_iv * 100.0, 1),
                "inTheMoney": itm,
                "delta": delta,
                "theta": theta,
                "vol_oi_ratio": vol_oi,
                "contractSymbol": c.get("contractSymbol", "")
            })

        for p in raw_puts:
            strike = float(p.get("strike", 0.0))
            bid = float(p.get("bid", 0.0))
            ask = float(p.get("ask", 0.0))
            last = float(p.get("lastPrice", 0.0))
            mid = round((bid + ask) / 2.0, 2) if (bid > 0 and ask > 0) else last
            iv = float(p.get("impliedVolatility", 0.0))
            vol = int(p.get("volume", 0) or 0)
            oi = int(p.get("openInterest", 0) or 0)
            itm = bool(p.get("inTheMoney", strike > spot_price))
            
            if iv > 0.05 and iv < 2.5:
                iv_samples.append(iv)
            eff_iv = iv if (iv > 0.05 and iv < 2.5) else (historical_vol / 100.0)

            _, delta_put, _, theta_put = self._calculate_greeks(spot_price, strike, dte, eff_iv)
            vol_oi = round(vol / oi, 2) if oi > 0 else (round(vol / 1.0, 2) if vol > 0 else 0.0)

            puts_clean.append({
                "strike": strike,
                "bid": bid,
                "ask": ask,
                "mid": mid,
                "lastPrice": last,
                "volume": vol,
                "openInterest": oi,
                "impliedVolatility": round(eff_iv * 100.0, 1),
                "inTheMoney": itm,
                "delta": delta_put,
                "theta": theta_put,
                "vol_oi_ratio": vol_oi,
                "contractSymbol": p.get("contractSymbol", "")
            })

        # ATM IV estimate
        atm_iv = float(np.median(iv_samples) * 100.0) if iv_samples else historical_vol
        iv_rv_spread = round(atm_iv - historical_vol, 1)

        return {
            "source": "live_yahoo",
            "expiration_dates": exp_dates[:8],
            "selected_expiration": selected_exp_date,
            "selected_dte": dte,
            "implied_volatility_atm": round(atm_iv, 1),
            "historical_volatility_30d": round(historical_vol, 1),
            "iv_rv_spread": iv_rv_spread,
            "calls": sorted(calls_clean, key=lambda x: x["strike"]),
            "puts": sorted(puts_clean, key=lambda x: x["strike"])
        }

    def _generate_synthetic_option_chain(
        self,
        ticker: str,
        spot: float,
        historical_vol: float
    ) -> Dict[str, Any]:
        """
        Generates realistic Black-Scholes option chain for testing or offline environments.
        """
        dte = 32
        exp_date = (datetime.now() + pd.Timedelta(days=dte)).strftime("%Y-%m-%d")
        exp_dates = [
            (datetime.now() + pd.Timedelta(days=d)).strftime("%Y-%m-%d")
            for d in [11, 18, 32, 46, 60, 95]
        ]
        
        iv_dec = max(0.12, historical_vol / 100.0)
        atm_iv = round(historical_vol * 1.02, 1)

        # Generate strikes centered around spot
        step = 5.0 if spot > 150 else (2.5 if spot > 50 else 1.0)
        base_strike = round(spot / step) * step
        strikes = [round(base_strike + i * step, 2) for i in range(-12, 13)]

        calls = []
        puts = []

        for k in strikes:
            # Skew: OTM puts slightly higher IV, OTM calls lower IV
            skew_factor = 1.0 + (spot - k) / spot * 0.15
            iv_k = max(0.10, iv_dec * skew_factor)

            # Black-Scholes option price
            t = dte / 365.0
            r = 0.045
            d1 = (np.log(spot / k) + (r + 0.5 * iv_k**2) * t) / (iv_k * np.sqrt(t))
            d2 = d1 - iv_k * np.sqrt(t)

            nd1 = 0.5 * (1.0 + float(pd.Series([d1]).apply(lambda x: math.erf(x / math.sqrt(2.0))).iloc[0]))
            nd2 = 0.5 * (1.0 + float(pd.Series([d2]).apply(lambda x: math.erf(x / math.sqrt(2.0))).iloc[0]))
            n_minus_d1 = 1.0 - nd1
            n_minus_d2 = 1.0 - nd2

            call_price = max(0.05, spot * nd1 - k * np.exp(-r * t) * nd2)
            put_price = max(0.05, k * np.exp(-r * t) * n_minus_d2 - spot * n_minus_d1)

            # Greeks
            delta_call, delta_put, theta_call, theta_put = self._calculate_greeks(spot, k, dte, iv_k)

            # Simulated volume and OI
            distance = abs(spot - k) / spot
            base_vol = max(10, int(3500 * np.exp(-distance * 8)))
            base_oi = max(50, int(7500 * np.exp(-distance * 5)))

            # Inject a couple of realistic institutional unusual flow spikes
            vol_oi_call = round(base_vol / base_oi, 2)
            vol_oi_put = round(base_vol / base_oi, 2)
            if k == round(spot * 1.05, 2):
                base_vol = int(base_oi * 2.3)
                vol_oi_call = 2.3
            elif k == round(spot * 0.92, 2):
                base_vol = int(base_oi * 1.85)
                vol_oi_put = 1.85

            bid_call = max(0.01, round(call_price * 0.97, 2))
            ask_call = max(0.05, round(call_price * 1.03, 2))
            bid_put = max(0.01, round(put_price * 0.97, 2))
            ask_put = max(0.05, round(put_price * 1.03, 2))

            calls.append({
                "strike": k,
                "bid": bid_call,
                "ask": ask_call,
                "mid": round((bid_call + ask_call) / 2.0, 2),
                "lastPrice": round(call_price, 2),
                "volume": base_vol,
                "openInterest": base_oi,
                "impliedVolatility": round(iv_k * 100.0, 1),
                "inTheMoney": k < spot,
                "delta": delta_call,
                "theta": theta_call,
                "vol_oi_ratio": vol_oi_call,
                "contractSymbol": f"{ticker}{exp_date.replace('-', '')[2:]}C{int(k*1000):08d}"
            })

            puts.append({
                "strike": k,
                "bid": bid_put,
                "ask": ask_put,
                "mid": round((bid_put + ask_put) / 2.0, 2),
                "lastPrice": round(put_price, 2),
                "volume": base_vol,
                "openInterest": base_oi,
                "impliedVolatility": round(iv_k * 100.0, 1),
                "inTheMoney": k > spot,
                "delta": delta_put,
                "theta": theta_put,
                "vol_oi_ratio": vol_oi_put,
                "contractSymbol": f"{ticker}{exp_date.replace('-', '')[2:]}P{int(k*1000):08d}"
            })

        return {
            "source": "synthetic_model",
            "expiration_dates": exp_dates,
            "selected_expiration": exp_date,
            "selected_dte": dte,
            "implied_volatility_atm": atm_iv,
            "historical_volatility_30d": round(historical_vol, 1),
            "iv_rv_spread": round(atm_iv - historical_vol, 1),
            "calls": calls,
            "puts": puts
        }

    def _calculate_greeks(
        self,
        spot: float,
        strike: float,
        dte_days: int,
        iv: float,
        r: float = 0.045
    ) -> Tuple[float, float, float, float]:
        """
        Computes Black-Scholes Greeks: (delta_call, delta_put, theta_call, theta_put).
        """
        if spot <= 0 or strike <= 0:
            return 0.5, -0.5, 0.0, 0.0

        t = max(1, dte_days) / 365.0
        sigma = max(0.05, iv)

        d1 = (math.log(spot / strike) + (r + 0.5 * sigma * sigma) * t) / (sigma * math.sqrt(t))
        d2 = d1 - sigma * math.sqrt(t)

        nd1 = 0.5 * (1.0 + math.erf(d1 / math.sqrt(2.0)))
        nd2 = 0.5 * (1.0 + math.erf(d2 / math.sqrt(2.0)))
        norm_pdf_d1 = math.exp(-0.5 * d1 * d1) / math.sqrt(2.0 * math.pi)

        delta_call = round(float(nd1), 2)
        delta_put = round(float(nd1 - 1.0), 2)

        theta_call = (-spot * norm_pdf_d1 * sigma / (2.0 * math.sqrt(t)) - r * strike * math.exp(-r * t) * nd2) / 365.0
        theta_put = (-spot * norm_pdf_d1 * sigma / (2.0 * math.sqrt(t)) + r * strike * math.exp(-r * t) * (1.0 - nd2)) / 365.0

        return delta_call, delta_put, round(float(theta_call), 3), round(float(theta_put), 3)

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
