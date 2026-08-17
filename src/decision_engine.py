"""
Decision Engine & Alignment Matrix.
Evaluates macro indicator conditions against stock archetypes, determines market regimes,
and outputs stock signals and tactical option playbooks.
Uses clean red, yellow, green status circles in a concise, business-like format.
"""

from typing import Dict, List, Any, Tuple
import numpy as np

from src.config import (
    STOCK_ARCHETYPES,
    ALIGNMENT_THRESHOLDS,
    OPTIONS_RULES
)

class AlignmentDecisionEngine:
    """
    Synthesizes macro indicators, archetype sensitivities, and technicals
    into actionable stock signals and option execution blueprints.
    """

    @classmethod
    def evaluate(
        cls,
        ticker_info: Dict[str, Any],
        indicators: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Executes full decision alignment workflow.
        """
        archetype_key = ticker_info.get("archetype_key", "MEGA_CAP_TECH")
        archetype = STOCK_ARCHETYPES.get(archetype_key, STOCK_ARCHETYPES["MEGA_CAP_TECH"])
        weights = archetype["indicator_weights"]

        # 1. Compute Alignment Score & Force Breakdown
        alignment_score, favorable_forces, hostile_forces = cls._compute_alignment_score(indicators, weights)

        # 2. Identify Macro Regime
        macro_regime = cls._determine_macro_regime(indicators)

        # 3. Determine Overall Stock Action Signal
        stock_signal, signal_badge, conviction = cls._determine_stock_signal(alignment_score, ticker_info)

        # 4. Synthesize Options Playbook
        options_playbook = cls._build_options_playbook(
            ticker_info=ticker_info,
            alignment_score=alignment_score,
            stock_signal=stock_signal,
            macro_regime=macro_regime,
            hostile_forces=hostile_forces
        )

        return {
            "ticker": ticker_info["ticker"],
            "archetype_key": archetype_key,
            "archetype_name": archetype["name"],
            "macro_regime": macro_regime,
            "alignment_score": round(alignment_score, 1),
            "alignment_gauge": cls._format_gauge(alignment_score),
            "stock_signal": stock_signal,
            "signal_badge": signal_badge,
            "conviction": conviction,
            "favorable_forces": favorable_forces,
            "hostile_forces": hostile_forces,
            "options_playbook": options_playbook
        }

    @classmethod
    def _compute_alignment_score(
        cls,
        indicators: Dict[str, Dict[str, Any]],
        weights: Dict[str, float]
    ) -> Tuple[float, List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Calculates weighted alignment score (-100 to +100) and separates favorable vs hostile forces.
        """
        weighted_sum = 0.0
        total_weight = 0.0
        favorable_forces = []
        hostile_forces = []

        for ind_id, ind_data in indicators.items():
            if ind_id in weights:
                w = weights[ind_id]
                raw_score = ind_data.get("raw_sentiment_score", 0.0)
                impact = raw_score * w
                weighted_sum += impact
                total_weight += abs(w)

                force_item = {
                    "indicator": ind_data.get("display_name", ind_id),
                    "ratio": ind_data.get("ratio_tickers", ind_id),
                    "trend": ind_data.get("trend_signal", ""),
                    "impact_score": round(impact, 2),
                    "meaning": ind_data.get("market_meaning", "")
                }

                if impact > 0.3:
                    force_item["status"] = "🟢 Tailwind"
                    favorable_forces.append(force_item)
                elif impact < -0.3:
                    force_item["status"] = "🔴 Headwind"
                    hostile_forces.append(force_item)

        # Normalize score to -100 to +100
        max_possible = total_weight * 2.0
        normalized_score = (weighted_sum / max_possible * 100.0) if max_possible > 0 else 0.0
        normalized_score = float(np.clip(normalized_score, -100.0, 100.0))

        # Sort forces by magnitude of impact
        favorable_forces.sort(key=lambda x: x["impact_score"], reverse=True)
        hostile_forces.sort(key=lambda x: x["impact_score"])

        return normalized_score, favorable_forces, hostile_forces

    @classmethod
    def _determine_macro_regime(cls, indicators: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """
        Classifies the broader macroeconomic market regime.
        """
        ndx_trend = indicators.get("NDX_SPX", {}).get("trend_signal", "")
        rsp_trend = indicators.get("RSP_SPY", {}).get("trend_signal", "")
        gld_trend = indicators.get("GLD_SPX", {}).get("trend_signal", "")
        sphb_trend = indicators.get("SPHB_SPLV", {}).get("trend_signal", "")
        vix_trend = indicators.get("VIX_SPX", {}).get("trend_signal", "")

        if "Rising" in gld_trend and "Falling" in sphb_trend:
            return {
                "name": "Risk-Off Defensive Flight",
                "badge": "🔴 Defensive Flight",
                "summary": "Capital is rotating into defensive assets, gold, and low-volatility shelters."
            }
        elif "Rising" in ndx_trend and "Falling" in rsp_trend:
            return {
                "name": "Mega-Cap Tech Leadership (Narrow Concentration)",
                "badge": "🟢 Mega-Cap Tech Dominance",
                "summary": "Nasdaq and mega-cap leaders driving performance while broad equal-weight breadth lags."
            }
        elif "Rising" in rsp_trend and "Rising" in sphb_trend:
            return {
                "name": "Broad Market Risk-On Expansion",
                "badge": "🟢 Broad Risk-On Expansion",
                "summary": "Healthy market breadth with broad participation across cyclicals and high-beta growth."
            }
        elif "Rising" in vix_trend and "Falling" in ndx_trend:
            return {
                "name": "Market De-Risking / Volatility Expansion",
                "badge": "🔴 Volatility Expansion",
                "summary": "Fear index is elevating; option premiums are expanding as market hedges downside."
            }
        else:
            return {
                "name": "Consolidation / Sector Rotation",
                "badge": "🟡 Balanced Rotation",
                "summary": "Cross-current rotation between sectors; market breadth is mixed."
            }

    @classmethod
    def _determine_stock_signal(
        cls,
        score: float,
        ticker_info: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """
        Determines the stock action signal and conviction level.
        """
        diff_ma50 = ticker_info.get("diff_ma50_pct", 0.0)
        rsi = ticker_info.get("rsi_14", 50.0)

        if score >= ALIGNMENT_THRESHOLDS["STRONG_BUY"]:
            if diff_ma50 >= -2.0 and rsi < 72:
                return "STRONG BUY", "🟢 STRONG BUY", "High"
            else:
                return "ACCUMULATE / BUY ON DIPS", "🟢 BUY ON DIPS", "Medium"
        elif score >= ALIGNMENT_THRESHOLDS["ACCUMULATE"]:
            return "ACCUMULATE / BUY", "🟢 ACCUMULATE", "Medium-High"
        elif score >= ALIGNMENT_THRESHOLDS["NEUTRAL_LOW"]:
            return "NEUTRAL / RANGING", "🟡 NEUTRAL (RANGING)", "Moderate"
        elif score >= ALIGNMENT_THRESHOLDS["REDUCE"]:
            return "REDUCE / TIGHTEN STOPS", "🔴 REDUCE / TRIM", "Medium"
        else:
            return "SELL / PROTECT / AVOID", "🔴 PROTECT / SELL", "High"

    @classmethod
    def _build_options_playbook(
        cls,
        ticker_info: Dict[str, Any],
        alignment_score: float,
        stock_signal: str,
        macro_regime: Dict[str, str],
        hostile_forces: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generates tactical option strategies tailored to macro alignment and ticker volatility.
        """
        price = ticker_info.get("current_price", 100.0)
        ma50 = ticker_info.get("ma50", price)
        vol = ticker_info.get("historical_vol_30d", 30.0)
        rsi = ticker_info.get("rsi_14", 50.0)

        is_high_vol = vol >= 35.0 or rsi <= 35.0
        is_bullish = alignment_score >= 15.0
        is_bearish = alignment_score <= -20.0

        if is_bullish:
            if is_high_vol:
                rule = OPTIONS_RULES["CASH_SECURED_PUTS"]
                strat_name = "Cash-Secured Puts (CSP) / Bull Put Spread"
                strike_pct = 0.90
                target_strike = round(price * strike_pct, 2)
                if price > ma50 and target_strike > ma50:
                    target_strike = round(ma50 * 0.98, 2)
                
                tactical_execution = {
                    "strategy": strat_name,
                    "rationale": "Macro alignment is favorable and elevated implied volatility inflates put option premium.",
                    "recommended_delta": rule["target_delta"],
                    "optimal_strike": f"${target_strike:.2f} (~{round((1 - target_strike/price)*100, 1)}% OTM, below support)",
                    "target_dte": rule["target_dte"],
                    "estimated_annualized_yield": "18.5% - 28.0% ROC (on cash collateral)",
                    "profit_target": rule["profit_target"],
                    "stop_loss_rule": rule["stop_loss"],
                    "ideal_condition": rule["ideal_condition"]
                }
            else:
                rule = OPTIONS_RULES["BULL_CALL_DEBIT_SPREAD"]
                strat_name = "Bull Call Debit Spread"
                strike_long = round(price * 0.99, 2)
                strike_short = round(price * 1.08, 2)
                tactical_execution = {
                    "strategy": strat_name,
                    "rationale": "Favorable macro alignment combined with low IV creates cost-effective directional upside exposure.",
                    "recommended_delta": rule["target_delta"],
                    "optimal_strike": f"Buy ${strike_long:.2f} Call / Sell ${strike_short:.2f} Call",
                    "target_dte": rule["target_dte"],
                    "estimated_annualized_yield": "1.8x - 2.5x Max ROI on risk capital",
                    "profit_target": rule["profit_target"],
                    "stop_loss_rule": rule["stop_loss"],
                    "ideal_condition": rule["ideal_condition"]
                }
        elif is_bearish:
            rule = OPTIONS_RULES["BEAR_PUT_SPREAD"]
            strat_name = "Bear Put Spread / Downside Hedge"
            strike_long = round(price * 0.99, 2)
            strike_short = round(price * 0.90, 2)
            tactical_execution = {
                "strategy": strat_name,
                "rationale": "Macro alignment is hostile. Defined-risk bear spread hedges downside against multiple contraction.",
                "recommended_delta": rule["target_delta"],
                "optimal_strike": f"Buy ${strike_long:.2f} Put / Sell ${strike_short:.2f} Put",
                "target_dte": rule["target_dte"],
                "estimated_annualized_yield": "2.0x - 3.0x Max Payout on hedge capital",
                "profit_target": rule["profit_target"],
                "stop_loss_rule": rule["stop_loss"],
                "ideal_condition": rule["ideal_condition"]
            }
        else:
            if is_high_vol:
                rule = OPTIONS_RULES["IRON_CONDOR"]
                strat_name = "Iron Condor / Range Premium Harvest"
                put_strike = round(price * 0.90, 2)
                call_strike = round(price * 1.10, 2)
                tactical_execution = {
                    "strategy": strat_name,
                    "rationale": "Macro regime is range-bound. Harvest elevated implied volatility across both wings.",
                    "recommended_delta": rule["target_delta"],
                    "optimal_strike": f"Short Put: ${put_strike:.2f} | Short Call: ${call_strike:.2f}",
                    "target_dte": rule["target_dte"],
                    "estimated_annualized_yield": "15.0% - 22.0% ROC",
                    "profit_target": rule["profit_target"],
                    "stop_loss_rule": rule["stop_loss"],
                    "ideal_condition": rule["ideal_condition"]
                }
            else:
                rule = OPTIONS_RULES["COVERED_CALLS"]
                strat_name = "Covered Calls / Cashflow Overlay"
                call_strike = round(price * 1.07, 2)
                tactical_execution = {
                    "strategy": strat_name,
                    "rationale": "Consolidating macro trend. Monetize sideways action by selling OTM upside call premium.",
                    "recommended_delta": rule["target_delta"],
                    "optimal_strike": f"${call_strike:.2f} (~{round((call_strike/price - 1)*100, 1)}% OTM above resistance)",
                    "target_dte": rule["target_dte"],
                    "estimated_annualized_yield": "12.0% - 18.0% Annualized Cash Flow",
                    "profit_target": rule["profit_target"],
                    "stop_loss_rule": rule["stop_loss"],
                    "ideal_condition": rule["ideal_condition"]
                }

        risk_warnings = []
        if hostile_forces:
            for h in hostile_forces[:2]:
                risk_warnings.append(f"{h['indicator']} ({h['ratio']}) is {h['trend']}: {h['meaning']}.")
        if vol > 45.0:
            risk_warnings.append(f"Elevated 30-day volatility ({vol:.1f}%) indicates high realized turbulence.")
        if not risk_warnings:
            risk_warnings.append("Macro indicators are aligned; monitor upcoming CPI and FOMC rate decisions.")

        return {
            "strategy": strat_name,
            "tactical_execution": tactical_execution,
            "risk_warnings": risk_warnings
        }

    @staticmethod
    def _format_gauge(score: float) -> str:
        """
        Creates a clean visual gauge with status circle.
        """
        normalized = int(np.clip((score + 100.0) / 20.0, 0, 10))
        filled = "█" * normalized
        empty = "░" * (10 - normalized)
        
        if score >= 20:
            color_badge = "🟢 Bullish"
        elif score <= -20:
            color_badge = "🔴 Bearish"
        else:
            color_badge = "🟡 Neutral"

        return f"[{filled}{empty}] {score:+.1f}/100 ({color_badge})"
