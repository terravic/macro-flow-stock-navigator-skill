"""
Macro Indicators Engine.
Calculates 14 multi-dimensional macro ratio indicators, moving averages, trend slopes,
and percentile distributions from market data.
"""

from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd

from src.config import DEFAULT_NOMINAL_GDP_TRILLIONS

class MacroIndicatorCalculator:
    """
    Computes macro relative strength indicators and trend dynamics.
    """

    @staticmethod
    def calculate_linear_slope(series: pd.Series, lookback: int = 15) -> float:
        """
        Calculates normalized percentage slope over lookback period.
        """
        clean_s = series.dropna()
        if len(clean_s) < 3:
            return 0.0
        
        window = min(lookback, len(clean_s))
        y = clean_s.iloc[-window:].values
        x = np.arange(len(y))
        
        cov = np.cov(x, y)[0, 1]
        var = np.var(x)
        slope = cov / var if var != 0 else 0.0
        
        mean_val = np.mean(y)
        if mean_val == 0:
            return 0.0
        normalized_slope = (slope / mean_val) * 100.0
        return float(normalized_slope)

    @staticmethod
    def calculate_percentile(series: pd.Series, current_val: float) -> float:
        """
        Computes the percentile rank of the current value in the series (0 to 100).
        """
        clean_s = series.dropna()
        if len(clean_s) == 0:
            return 50.0
        return float((clean_s < current_val).mean() * 100.0)

    @staticmethod
    def determine_trend_direction(slope: float, current_vs_ma: float) -> str:
        """
        Determines clean trend direction.
        """
        if slope > 0.15 and current_vs_ma > 0.5:
            return "Strong Rising"
        elif slope > 0.03:
            return "Rising"
        elif slope < -0.15 and current_vs_ma < -0.5:
            return "Strong Falling"
        elif slope < -0.03:
            return "Falling"
        else:
            return "Flat / Neutral"

    @classmethod
    def compute_indicator_profile(
        cls,
        name: str,
        display_name: str,
        ratio_tickers: str,
        num_series: pd.Series,
        denom_series: pd.Series,
        meaning_rising: str,
        meaning_falling: str,
        nominal_gdp_trillions: float = DEFAULT_NOMINAL_GDP_TRILLIONS,
        is_spx_gdp: bool = False
    ) -> Dict[str, Any]:
        """
        Computes metrics for a single ratio indicator.
        """
        df = pd.DataFrame({"num": num_series, "denom": denom_series}).dropna()
        
        if len(df) < 5:
            return {
                "id": name,
                "display_name": display_name,
                "ratio_tickers": ratio_tickers,
                "current_value": 0.0,
                "ma50": 0.0,
                "diff_ma50_pct": 0.0,
                "ma50_status": "N/A",
                "slope_pct": 0.0,
                "trend_signal": "Insufficient Data",
                "percentile_90d": 50.0,
                "raw_sentiment_score": 0.0,
                "market_meaning": "Insufficient historical data",
                "history": [],
                "history_dates": [],
                "history_ma50": []
            }

        if is_spx_gdp:
            spx_level = df["num"]
            ratio_series = (spx_level * 0.0085 / nominal_gdp_trillions) * 100.0
        else:
            ratio_series = df["num"] / df["denom"]

        current_val = float(ratio_series.iloc[-1])
        ma50_series = ratio_series.rolling(window=min(50, len(ratio_series)), min_periods=5).mean()
        current_ma50 = float(ma50_series.iloc[-1])
        
        diff_ma50_pct = ((current_val - current_ma50) / current_ma50 * 100.0) if current_ma50 != 0 else 0.0
        slope = cls.calculate_linear_slope(ratio_series, lookback=15)
        percentile = cls.calculate_percentile(ratio_series, current_val)
        trend_direction = cls.determine_trend_direction(slope, diff_ma50_pct)

        # Status indicator with metric
        if diff_ma50_pct > 1.0:
            ma50_status = f"Above (+{diff_ma50_pct:.2f}%)"
        elif diff_ma50_pct < -1.0:
            ma50_status = f"Below ({diff_ma50_pct:.2f}%)"
        else:
            ma50_status = f"At MA ({diff_ma50_pct:+.2f}%)"

        # Active market meaning
        if "Rising" in trend_direction:
            meaning = meaning_rising
            raw_score = 1.0 if "Strong" not in trend_direction else 1.5
        elif "Falling" in trend_direction:
            meaning = meaning_falling
            raw_score = -1.0 if "Strong" not in trend_direction else -1.5
        else:
            meaning = "Consolidating / Neutral Transition"
            raw_score = 0.0

        # Adjust raw score with MA50 confirmation
        if diff_ma50_pct > 0:
            raw_score += 0.5
        elif diff_ma50_pct < 0:
            raw_score -= 0.5

        tail_len = min(60, len(ratio_series))
        tail_ratio = ratio_series.iloc[-tail_len:]
        tail_ma50 = ma50_series.iloc[-tail_len:]

        dates_list = []
        for idx in tail_ratio.index:
            if hasattr(idx, "strftime"):
                dates_list.append(idx.strftime("%Y-%m-%d"))
            elif isinstance(idx, str) and len(idx) >= 10:
                dates_list.append(idx[:10])
            else:
                dates_list.append(str(idx))

        history_vals = [round(float(v), 4 if abs(v) < 10 else 2) for v in tail_ratio]
        history_ma50_vals = [
            round(float(m), 4 if abs(m) < 10 else 2) if not pd.isna(m) else history_vals[i]
            for i, m in enumerate(tail_ma50)
        ]

        return {
            "id": name,
            "display_name": display_name,
            "ratio_tickers": ratio_tickers,
            "current_value": round(current_val, 4 if current_val < 10 else 2),
            "ma50": round(current_ma50, 4 if current_ma50 < 10 else 2),
            "diff_ma50_pct": round(diff_ma50_pct, 2),
            "ma50_status": ma50_status,
            "slope_pct": round(slope, 3),
            "trend_signal": trend_direction,
            "percentile_90d": round(percentile, 1),
            "raw_sentiment_score": round(raw_score, 2),
            "market_meaning": meaning,
            "history": history_vals,
            "history_dates": dates_list,
            "history_ma50": history_ma50_vals
        }

    @classmethod
    def compute_all_indicators(
        cls,
        price_data: Dict[str, pd.Series],
        nominal_gdp: float = DEFAULT_NOMINAL_GDP_TRILLIONS
    ) -> Dict[str, Dict[str, Any]]:
        """
        Computes all 14 multi-dimensional macro indicators.
        """
        indicators = {}

        # 1. RSP / SPY
        if "RSP" in price_data and "SPY" in price_data:
            indicators["RSP_SPY"] = cls.compute_indicator_profile(
                name="RSP_SPY",
                display_name="Market Breadth (Equal vs Cap Weight)",
                ratio_tickers="RSP / SPY",
                num_series=price_data["RSP"],
                denom_series=price_data["SPY"],
                meaning_rising="Broad market participation expanding beyond Mega-Caps",
                meaning_falling="Mega-cap concentration; narrow leadership / breadth divergence"
            )

        # 2. GLD / SPX (Gold vs S&P 500)
        spx_series = price_data.get("SPX", price_data.get("SPY", pd.Series()))
        if "GLD" in price_data and len(spx_series) > 0:
            indicators["GLD_SPX"] = cls.compute_indicator_profile(
                name="GLD_SPX",
                display_name="Macro Risk Sentiment / Inflation Hedge",
                ratio_tickers="GLD / SPX",
                num_series=price_data["GLD"],
                denom_series=spx_series,
                meaning_rising="Risk-off flight to safety / stagflation and hedge demand",
                meaning_falling="Risk-on equity dominance; capital favoring productive assets"
            )

        # 3. NDX / SPX (Nasdaq 100 vs S&P 500)
        ndx_series = price_data.get("QQQ", price_data.get("NDX", pd.Series()))
        if len(ndx_series) > 0 and len(spx_series) > 0:
            indicators["NDX_SPX"] = cls.compute_indicator_profile(
                name="NDX_SPX",
                display_name="Tech Momentum vs Broad Market",
                ratio_tickers="NDX / SPX",
                num_series=ndx_series,
                denom_series=spx_series,
                meaning_rising="Tech leadership and growth multiple expansion",
                meaning_falling="Tech lagging; defensive/value rotation underway"
            )

        # 4. IWM / SPY (Russell 2000 vs S&P 500)
        if "IWM" in price_data and "SPY" in price_data:
            indicators["IWM_SPY"] = cls.compute_indicator_profile(
                name="IWM_SPY",
                display_name="Small Cap Strength / Economic Sentiment",
                ratio_tickers="IWM / SPY",
                num_series=price_data["IWM"],
                denom_series=price_data["SPY"],
                meaning_rising="Small-cap acceleration; domestic liquidity and growth expansion",
                meaning_falling="Small-cap lag; tight credit conditions and large-cap refuge"
            )

        # 5. SPX / GDP (Buffett Indicator)
        if len(spx_series) > 0:
            indicators["SPX_GDP"] = cls.compute_indicator_profile(
                name="SPX_GDP",
                display_name="Macro Valuation (S&P to US GDP Ratio)",
                ratio_tickers="SPX / GDP",
                num_series=spx_series,
                denom_series=pd.Series([1.0] * len(spx_series), index=spx_series.index),
                meaning_rising="Equity market valuation expanding relative to GDP",
                meaning_falling="Valuation contracting toward historic fair-value mean",
                nominal_gdp_trillions=nominal_gdp,
                is_spx_gdp=True
            )

        # 6. SPHB / SPLV (High Beta vs Low Volatility)
        if "SPHB" in price_data and "SPLV" in price_data:
            indicators["SPHB_SPLV"] = cls.compute_indicator_profile(
                name="SPHB_SPLV",
                display_name="Speculative Appetite vs Capital Preservation",
                ratio_tickers="SPHB / SPLV",
                num_series=price_data["SPHB"],
                denom_series=price_data["SPLV"],
                meaning_rising="Aggressive risk-on appetite; high beta outperformance",
                meaning_falling="Defensive capital preservation; flight to low-volatility"
            )

        # 7. XLY / XLP (Consumer Discretionary vs Staples)
        if "XLY" in price_data and "XLP" in price_data:
            indicators["XLY_XLP"] = cls.compute_indicator_profile(
                name="XLY_XLP",
                display_name="Cyclical Growth vs Defensive Consumer",
                ratio_tickers="XLY / XLP",
                num_series=price_data["XLY"],
                denom_series=price_data["XLP"],
                meaning_rising="Consumer confidence robust; cyclical discretionary spending",
                meaning_falling="Consumer caution; defensive staple rotation and slowdown watch"
            )

        # 8. VIX / SPX Ratio
        vix_series = price_data.get("VIX", pd.Series())
        if len(vix_series) > 0 and len(spx_series) > 0:
            indicators["VIX_SPX"] = cls.compute_indicator_profile(
                name="VIX_SPX",
                display_name="Normalized Market Fear vs Index Trend",
                ratio_tickers="VIX / SPX",
                num_series=vix_series,
                denom_series=spx_series / 100.0,
                meaning_rising="Elevated volatility and fear premium escalating",
                meaning_falling="Volatility compressing; steady market trend and low hedging demand"
            )

        # 9. COPX / GLD (Dr. Copper vs Gold: Global Physical Growth vs Fear)
        if "COPX" in price_data and "GLD" in price_data:
            indicators["COPX_GLD"] = cls.compute_indicator_profile(
                name="COPX_GLD",
                display_name="Global Industrial Pulse vs Monetary Fear",
                ratio_tickers="COPX / GLD",
                num_series=price_data["COPX"],
                denom_series=price_data["GLD"],
                meaning_rising="Physical infrastructure and industrial demand expanding faster than fear",
                meaning_falling="Industrial manufacturing slowdown; flight to monetary safety and gold"
            )

        # 10. HYG / LQD (High Yield vs Investment Grade Credit Spread)
        if "HYG" in price_data and "LQD" in price_data:
            indicators["HYG_LQD"] = cls.compute_indicator_profile(
                name="HYG_LQD",
                display_name="Corporate Credit Solvency & Risk Spread",
                ratio_tickers="HYG / LQD",
                num_series=price_data["HYG"],
                denom_series=price_data["LQD"],
                meaning_rising="Corporate credit spreads tightening; borrowing health and liquidity strong",
                meaning_falling="Credit default spreads widening; corporate debt distress and tightening"
            )

        # 11. TIP / IEF (Real Interest Rates & Cost of Capital)
        if "TIP" in price_data and "IEF" in price_data:
            indicators["TIP_IEF"] = cls.compute_indicator_profile(
                name="TIP_IEF",
                display_name="Real Interest Rates & Cost of Capital",
                ratio_tickers="TIP / IEF",
                num_series=price_data["TIP"],
                denom_series=price_data["IEF"],
                meaning_rising="Inflation compensation climbing; capital cost pressure",
                meaning_falling="Real rates easing / multiple expansion tailwind for growth"
            )

        # 12. VIX9D / VIX (Volatility Term Structure Panic Inversion)
        vix9d_series = price_data.get("VIX9D", pd.Series())
        if len(vix9d_series) > 0 and len(vix_series) > 0:
            indicators["VIX9D_VIX"] = cls.compute_indicator_profile(
                name="VIX9D_VIX",
                display_name="Volatility Term Structure Shock Inversion",
                ratio_tickers="VIX9D / VIX",
                num_series=vix9d_series,
                denom_series=vix_series,
                meaning_rising="Acute short-term panic shock; term structure inverting into backwardation",
                meaning_falling="Healthy volatility contango; market pricing calm and low crash anxiety"
            )

        # 13. XBI / XLV (Biotech Clinical Innovation vs Mature Pharma)
        if "XBI" in price_data and "XLV" in price_data:
            indicators["XBI_XLV"] = cls.compute_indicator_profile(
                name="XBI_XLV",
                display_name="Human Health Innovation vs Defensive Pharma",
                ratio_tickers="XBI / XLV",
                num_series=price_data["XBI"],
                denom_series=price_data["XLV"],
                meaning_rising="Speculative venture appetite expanding in human health breakthroughs",
                meaning_falling="Capital retreating into mature defensive dividend pharma"
            )

        # 14. PKG / SPY (Physical Cardboard Box Shipping Velocity)
        if "PKG" in price_data and "SPY" in price_data:
            indicators["PKG_SPY"] = cls.compute_indicator_profile(
                name="PKG_SPY",
                display_name="Physical Goods Shipping & Packaging Velocity",
                ratio_tickers="PKG / SPY",
                num_series=price_data["PKG"],
                denom_series=price_data["SPY"],
                meaning_rising="Real-world goods packaging and shipment volumes expanding",
                meaning_falling="Physical product delivery slowdown; digital-only divergence"
            )

        return indicators
