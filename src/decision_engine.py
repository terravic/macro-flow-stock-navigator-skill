"""
Decision Engine & Alignment Matrix.
Evaluates macro indicator conditions against stock archetypes, determines market regimes,
and outputs stock signals and tactical option playbooks.
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

        # 5. Build Unified View & Executive Finding
        unified_synthesis = cls._build_unified_synthesis(
            ticker_info=ticker_info,
            indicators=indicators,
            alignment_score=alignment_score,
            macro_regime=macro_regime,
            options_playbook=options_playbook
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
            "options_playbook": options_playbook,
            "unified_synthesis": unified_synthesis
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
                    force_item["status"] = "Tailwind"
                    favorable_forces.append(force_item)
                elif impact < -0.3:
                    force_item["status"] = "Headwind"
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
                "badge": "Defensive Flight",
                "summary": "Capital is rotating into defensive assets, gold, and low-volatility shelters."
            }
        elif "Rising" in ndx_trend and "Falling" in rsp_trend:
            return {
                "name": "Mega-Cap Tech Leadership (Narrow Concentration)",
                "badge": "Mega-Cap Tech Dominance",
                "summary": "Nasdaq and mega-cap leaders driving performance while broad equal-weight breadth lags."
            }
        elif "Rising" in rsp_trend and "Rising" in sphb_trend:
            return {
                "name": "Broad Market Risk-On Expansion",
                "badge": "Broad Risk-On Expansion",
                "summary": "Healthy market breadth with broad participation across cyclicals and high-beta growth."
            }
        elif "Rising" in vix_trend and "Falling" in ndx_trend:
            return {
                "name": "Market De-Risking / Volatility Expansion",
                "badge": "Volatility Expansion",
                "summary": "Fear index is elevating; option premiums are expanding as market hedges downside."
            }
        else:
            return {
                "name": "Consolidation / Sector Rotation",
                "badge": "Balanced Rotation",
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
                return "STRONG BUY", "STRONG BUY", "High"
            else:
                return "ACCUMULATE / BUY ON DIPS", "BUY ON DIPS", "Medium"
        elif score >= ALIGNMENT_THRESHOLDS["ACCUMULATE"]:
            return "ACCUMULATE / BUY", "ACCUMULATE", "Medium-High"
        elif score >= ALIGNMENT_THRESHOLDS["NEUTRAL_LOW"]:
            return "NEUTRAL / RANGING", "NEUTRAL (RANGING)", "Moderate"
        elif score >= ALIGNMENT_THRESHOLDS["REDUCE"]:
            return "REDUCE / TIGHTEN STOPS", "REDUCE / TRIM", "Medium"
        else:
            return "SELL / PROTECT / AVOID", "PROTECT / SELL", "High"

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
        Generates tactical option strategies tailored to macro alignment and ticker volatility,
        with deep focus on Selling Covered Calls and Selling Cash-Secured Puts.
        """
        price = ticker_info.get("current_price", 100.0)
        ma50 = ticker_info.get("ma50", price)
        vol = ticker_info.get("historical_vol_30d", 30.0)
        rsi = ticker_info.get("rsi_14", 50.0)
        options_data = ticker_info.get("options_data", {})

        calls = options_data.get("calls", [])
        puts = options_data.get("puts", [])
        dte = options_data.get("selected_dte", 30)
        atm_iv = options_data.get("implied_volatility_atm", vol)

        # 1. Compute Options Volatility & Flow Analytics
        analytics = cls._analyze_options_chain(ticker_info, options_data)

        # 2. Screen Selling Covered Calls Matrix
        cc_matrix = cls._screen_covered_calls(calls, price, dte)

        # 3. Screen Selling Cash-Secured Puts Matrix
        csp_matrix = cls._screen_cash_secured_puts(puts, price, dte)

        # 4. Detect Unusual Option Flow & Big Moves
        uoa_list = cls._detect_unusual_option_activity(calls, puts, price)

        is_high_vol = vol >= 35.0 or rsi <= 35.0 or analytics["iv_rv_spread"] > 3.0
        is_bullish = alignment_score >= 15.0
        is_bearish = alignment_score <= -20.0

        # Choose primary prescribed strategy focused on Selling Covered Calls vs Selling Cash-Secured Puts
        if is_bullish or (is_high_vol and not is_bearish):
            rule = OPTIONS_RULES.get("CASH_SECURED_PUTS", {
                "target_delta": "0.20 - 0.30 Delta",
                "target_dte": "30 - 45 DTE",
                "profit_target": "75% - 85% of max credit",
                "stop_loss": "Roll down and out if stock breaches strike with heavy volume",
                "ideal_condition": "Macro Alignment is Positive + Elevated IV."
            })
            strat_name = "Cash-Secured Puts (CSP) / Discount Accumulation"
            best_csp = csp_matrix.get("balanced", {})
            opt_strike_val = best_csp.get("strike", round(price * 0.92, 2))
            opt_yield = best_csp.get("annualized_roc", 18.5)
            
            tactical_execution = {
                "strategy": strat_name,
                "rationale": "Favorable macro alignment & elevated put skew offer attractive premium to acquire stock at a discount or generate high-yield collateral cashflow.",
                "recommended_delta": rule["target_delta"],
                "optimal_strike": f"${opt_strike_val:.2f} (~{best_csp.get('otm_pct', 8.0):.1f}% OTM, net cost ${best_csp.get('net_cost_basis', opt_strike_val):.2f})",
                "target_dte": f"{dte} DTE ({options_data.get('selected_expiration', 'Next Monthly')})",
                "estimated_annualized_yield": f"{opt_yield:.1f}% Annualized Return on Collateral (ROC)",
                "profit_target": rule["profit_target"],
                "stop_loss_rule": rule["stop_loss"],
                "ideal_condition": rule["ideal_condition"]
            }
        elif is_bearish:
            rule = OPTIONS_RULES.get("COVERED_CALLS", {
                "target_delta": "0.30 - 0.40 Delta",
                "target_dte": "21 - 35 DTE",
                "profit_target": "80% - 90% of max credit",
                "stop_loss": "Roll up and out if stock breaks above resistance",
                "ideal_condition": "Macro Alignment is Bearish / Hostile + Defensive overlay."
            })
            strat_name = "Covered Calls / Defensive Cashflow Overlay"
            best_cc = cc_matrix.get("aggressive", {})
            opt_strike_val = best_cc.get("strike", round(price * 1.03, 2))
            opt_yield = best_cc.get("yield_unassigned", 22.0)
            
            tactical_execution = {
                "strategy": strat_name,
                "rationale": "Hostile macro regime favors aggressive short call premium collection to generate defensive income and hedge downside valuation drift.",
                "recommended_delta": rule["target_delta"],
                "optimal_strike": f"${opt_strike_val:.2f} (~{best_cc.get('otm_pct', 3.0):.1f}% OTM above resistance)",
                "target_dte": f"{dte} DTE ({options_data.get('selected_expiration', 'Next Monthly')})",
                "estimated_annualized_yield": f"{opt_yield:.1f}% Annualized Cash Flow Yield",
                "profit_target": rule["profit_target"],
                "stop_loss_rule": rule["stop_loss"],
                "ideal_condition": rule["ideal_condition"]
            }
        else: # Neutral / Ranging
            rule = OPTIONS_RULES.get("COVERED_CALLS", {
                "target_delta": "0.25 - 0.35 Delta",
                "target_dte": "30 - 45 DTE",
                "profit_target": "75% - 85% of max credit",
                "stop_loss": "Roll up and out if stock breaches strike with heavy volume",
                "ideal_condition": "Macro Alignment is Neutral / Ranging."
            })
            strat_name = "Covered Calls / Systematic Income Harvest"
            best_cc = cc_matrix.get("balanced", {})
            opt_strike_val = best_cc.get("strike", round(price * 1.06, 2))
            opt_yield = best_cc.get("yield_unassigned", 15.5)

            tactical_execution = {
                "strategy": strat_name,
                "rationale": "Neutral macro consolidation. Monetize sideways range by selling OTM upside call premium while maintaining stock upside participation.",
                "recommended_delta": rule["target_delta"],
                "optimal_strike": f"${opt_strike_val:.2f} (~{best_cc.get('otm_pct', 6.0):.1f}% OTM above resistance)",
                "target_dte": f"{dte} DTE ({options_data.get('selected_expiration', 'Next Monthly')})",
                "estimated_annualized_yield": f"{opt_yield:.1f}% Annualized Cash Flow Yield",
                "profit_target": rule["profit_target"],
                "stop_loss_rule": rule["stop_loss"],
                "ideal_condition": rule["ideal_condition"]
            }

        risk_warnings = []
        if hostile_forces:
            for h in hostile_forces[:2]:
                risk_warnings.append(f"{h['indicator']} ({h['ratio']}) is {h['trend']}: {h['meaning']}.")
        if vol > 45.0:
            risk_warnings.append(f"Elevated 30-day volatility ({vol:.1f}%) indicates wide price swings; prefer conservative strike selection.")
        if analytics["iv_rv_spread"] < -5.0:
            risk_warnings.append(f"Implied Volatility ({analytics['iv_atm']:.1f}%) is discounted vs Realized Vol ({analytics['hv_30d']:.1f}%); option premiums are relatively lean.")
        if not risk_warnings:
            risk_warnings.append("Macro indicators are balanced; monitor upcoming earnings release and FOMC rate decisions.")

        return {
            "strategy": strat_name,
            "tactical_execution": tactical_execution,
            "options_analytics": analytics,
            "covered_call_matrix": cc_matrix,
            "cash_secured_put_matrix": csp_matrix,
            "unusual_activity": uoa_list,
            "options_chain": {
                "expiration": options_data.get("selected_expiration", ""),
                "dte": dte,
                "calls": calls[:15],
                "puts": puts[:15]
            },
            "risk_warnings": risk_warnings
        }

    @classmethod
    def _analyze_options_chain(
        cls,
        ticker_info: Dict[str, Any],
        options_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculates key options indicators: IV Rank, IV/RV spread, PCR (Vol & OI),
        Max Pain Theory Strike, and 30-day Expected Move cone.
        """
        price = float(ticker_info.get("current_price", 100.0))
        hv_30d = float(ticker_info.get("historical_vol_30d", 30.0))
        iv_atm = float(options_data.get("implied_volatility_atm", hv_30d))
        dte = int(options_data.get("selected_dte", 30))
        
        calls = options_data.get("calls", [])
        puts = options_data.get("puts", [])

        # 1. IV vs RV Spread
        iv_rv_spread = round(iv_atm - hv_30d, 1)

        # 2. IV Rank & Percentile (Estimated based on annualized historical volatility channel)
        min_iv_est = max(10.0, hv_30d * 0.65)
        max_iv_est = max(50.0, hv_30d * 1.85)
        iv_rank = round(float(np.clip(((iv_atm - min_iv_est) / (max_iv_est - min_iv_est)) * 100.0, 0.0, 100.0)), 1)
        iv_percentile = round(float(np.clip(iv_rank * 0.95 + 5.0, 0.0, 100.0)), 1)

        # 3. Put-Call Ratio by Volume & Open Interest
        total_call_vol = sum(c.get("volume", 0) for c in calls)
        total_put_vol = sum(p.get("volume", 0) for p in puts)
        pcr_vol = round(total_put_vol / total_call_vol, 2) if total_call_vol > 0 else 1.0

        total_call_oi = sum(c.get("openInterest", 0) for c in calls)
        total_put_oi = sum(p.get("openInterest", 0) for p in puts)
        pcr_oi = round(total_put_oi / total_call_oi, 2) if total_call_oi > 0 else 1.0

        # 4. Max Pain Strike Calculation
        max_pain = cls._calculate_max_pain(calls, puts, price)

        # 5. Expected Move (1-Sigma)
        t_fraction = max(1, dte) / 365.0
        expected_move = round(price * (iv_atm / 100.0) * np.sqrt(t_fraction), 2)
        expected_upper = round(price + expected_move, 2)
        expected_lower = round(price - expected_move, 2)
        expected_move_pct = round((expected_move / price) * 100.0, 1)

        return {
            "iv_atm": round(iv_atm, 1),
            "hv_30d": round(hv_30d, 1),
            "iv_rv_spread": iv_rv_spread,
            "iv_rank": iv_rank,
            "iv_percentile": iv_percentile,
            "pcr_volume": pcr_vol,
            "pcr_open_interest": pcr_oi,
            "total_call_volume": total_call_vol,
            "total_put_volume": total_put_vol,
            "max_pain_strike": max_pain,
            "expected_move_30d": expected_move,
            "expected_move_pct": expected_move_pct,
            "expected_move_upper": expected_upper,
            "expected_move_lower": expected_lower
        }

    @staticmethod
    def _calculate_max_pain(calls: List[Dict[str, Any]], puts: List[Dict[str, Any]], spot: float) -> float:
        """
        Calculates the strike price where total option holder loss is maximized (Max Pain strike).
        """
        all_strikes = sorted(list(set([c.get("strike", 0) for c in calls] + [p.get("strike", 0) for p in puts])))
        if not all_strikes:
            return round(spot, 2)

        min_loss = float("inf")
        max_pain_strike = spot

        for strike in all_strikes:
            total_loss = 0.0
            # Call loss: if strike < k, call holders lose money
            for c in calls:
                k = c.get("strike", 0)
                oi = c.get("openInterest", 0)
                if strike > k:
                    total_loss += (strike - k) * oi * 100.0
            # Put loss: if strike > k, put holders lose money
            for p in puts:
                k = p.get("strike", 0)
                oi = p.get("openInterest", 0)
                if strike < k:
                    total_loss += (k - strike) * oi * 100.0
            
            if total_loss < min_loss:
                min_loss = total_loss
                max_pain_strike = strike

        return round(float(max_pain_strike), 2)

    @staticmethod
    def _screen_covered_calls(calls: List[Dict[str, Any]], spot: float, dte: int) -> Dict[str, Any]:
        """
        Screens optimal OTM call strikes across Conservative (0.20Δ), Balanced (0.30Δ),
        and Aggressive (0.40Δ) tiers for Selling Covered Calls.
        """
        otm_calls = [c for c in calls if c.get("strike", 0) >= spot]
        if not otm_calls:
            otm_calls = calls

        def find_closest_call(target_delta: float) -> Dict[str, Any]:
            if not otm_calls:
                return {}
            # Sort by delta closeness
            best = min(otm_calls, key=lambda c: abs(c.get("delta", 0.5) - target_delta))
            strike = best.get("strike", spot * 1.05)
            mid = best.get("mid", best.get("lastPrice", spot * 0.02))
            delta = best.get("delta", target_delta)
            theta = best.get("theta", -0.05)
            otm_pct = round(((strike - spot) / spot) * 100.0, 1)
            
            # Annualized Yield if Unassigned: (Premium / Spot) * (365 / DTE) * 100
            yield_unassigned = round((mid / spot) * (365.0 / max(1, dte)) * 100.0, 1)
            # Total Return if Called Away: ((Strike - Spot + Premium) / Spot) * 100
            return_called = round(((strike - spot + mid) / spot) * 100.0, 1)
            # Downside Cushion Buffer: (Premium / Spot) * 100
            downside_buf = round((mid / spot) * 100.0, 1)

            return {
                "tier_name": f"{int(target_delta*100)}Δ Tier",
                "strike": strike,
                "delta": delta,
                "theta": theta,
                "bid": best.get("bid", mid * 0.95),
                "ask": best.get("ask", mid * 1.05),
                "mid": mid,
                "otm_pct": otm_pct,
                "yield_unassigned": yield_unassigned,
                "return_called_away": return_called,
                "downside_protection": downside_buf,
                "dte": dte
            }

        return {
            "conservative": find_closest_call(0.20),
            "balanced": find_closest_call(0.30),
            "aggressive": find_closest_call(0.40)
        }

    @staticmethod
    def _screen_cash_secured_puts(puts: List[Dict[str, Any]], spot: float, dte: int) -> Dict[str, Any]:
        """
        Screens optimal OTM put strikes across Conservative (0.20Δ), Balanced (0.30Δ),
        and Aggressive (0.40Δ) tiers for Selling Cash-Secured Puts.
        """
        otm_puts = [p for p in puts if p.get("strike", 0) <= spot]
        if not otm_puts:
            otm_puts = puts

        def find_closest_put(target_delta: float) -> Dict[str, Any]:
            if not otm_puts:
                return {}
            # Delta on puts is negative (-0.20, -0.30, -0.40)
            best = min(otm_puts, key=lambda p: abs(abs(p.get("delta", -0.5)) - target_delta))
            strike = best.get("strike", spot * 0.95)
            mid = best.get("mid", best.get("lastPrice", spot * 0.02))
            delta = best.get("delta", -target_delta)
            theta = best.get("theta", -0.05)
            otm_pct = round(((spot - strike) / spot) * 100.0, 1)
            
            # Collateral required per contract = Strike * 100
            collateral = round(strike * 100.0, 2)
            # Net Effective Cost Basis if assigned = Strike - Premium
            net_cost = round(strike - mid, 2)
            discount_pct = round(((spot - net_cost) / spot) * 100.0, 1)
            # Annualized Return on Collateral (ROC) = (Premium / Strike) * (365 / DTE) * 100
            annualized_roc = round((mid / strike) * (365.0 / max(1, dte)) * 100.0, 1)

            return {
                "tier_name": f"{int(target_delta*100)}Δ Tier",
                "strike": strike,
                "delta": delta,
                "theta": theta,
                "bid": best.get("bid", mid * 0.95),
                "ask": best.get("ask", mid * 1.05),
                "mid": mid,
                "otm_pct": otm_pct,
                "collateral_required": collateral,
                "net_cost_basis": net_cost,
                "discount_pct": discount_pct,
                "annualized_roc": annualized_roc,
                "dte": dte
            }

        return {
            "conservative": find_closest_put(0.20),
            "balanced": find_closest_put(0.30),
            "aggressive": find_closest_put(0.40)
        }

    @staticmethod
    def _detect_unusual_option_activity(
        calls: List[Dict[str, Any]],
        puts: List[Dict[str, Any]],
        spot: float
    ) -> List[Dict[str, Any]]:
        """
        Detects unusual option flow anomalies and institutional positioning (Volume > 1.5x Open Interest).
        """
        uoa_candidates = []

        for c in calls:
            vol = c.get("volume", 0)
            oi = c.get("openInterest", 0)
            vol_oi = c.get("vol_oi_ratio", 0.0)
            mid = c.get("mid", c.get("lastPrice", 0.0))
            dollar_flow = round(vol * mid * 100.0, 2)
            
            if vol >= 30 and (vol_oi >= 1.4 or dollar_flow >= 50000.0):
                strike = c.get("strike", spot)
                sentiment = "Bullish Call Buying / Sweep" if strike >= spot else "In-the-Money Call Accumulation"
                uoa_candidates.append({
                    "option_type": "CALL",
                    "strike": strike,
                    "contract": c.get("contractSymbol", f"Call ${strike}"),
                    "volume": vol,
                    "open_interest": oi,
                    "vol_oi_ratio": vol_oi,
                    "mid_price": mid,
                    "dollar_flow": dollar_flow,
                    "sentiment": sentiment,
                    "in_the_money": c.get("inTheMoney", False)
                })

        for p in puts:
            vol = p.get("volume", 0)
            oi = p.get("openInterest", 0)
            vol_oi = p.get("vol_oi_ratio", 0.0)
            mid = p.get("mid", p.get("lastPrice", 0.0))
            dollar_flow = round(vol * mid * 100.0, 2)
            
            if vol >= 30 and (vol_oi >= 1.4 or dollar_flow >= 50000.0):
                strike = p.get("strike", spot)
                sentiment = "Protective Put Buying / Hedge" if strike <= spot else "In-the-Money Put Sweep"
                uoa_candidates.append({
                    "option_type": "PUT",
                    "strike": strike,
                    "contract": p.get("contractSymbol", f"Put ${strike}"),
                    "volume": vol,
                    "open_interest": oi,
                    "vol_oi_ratio": vol_oi,
                    "mid_price": mid,
                    "dollar_flow": dollar_flow,
                    "sentiment": sentiment,
                    "in_the_money": p.get("inTheMoney", False)
                })

        # Rank by total dollar premium flow
        uoa_candidates.sort(key=lambda x: x["dollar_flow"], reverse=True)
        return uoa_candidates[:6]

    @staticmethod
    def _format_gauge(score: float) -> str:
        """
        Creates a clean visual gauge.
        """
        normalized = int(np.clip((score + 100.0) / 20.0, 0, 10))
        filled = "=" * normalized
        empty = "-" * (10 - normalized)
        
        if score >= 20:
            color_badge = "Bullish"
        elif score <= -20:
            color_badge = "Bearish"
        else:
            color_badge = "Neutral"

        return f"[{filled}{empty}] {score:+.1f}/100 ({color_badge})"

    @classmethod
    def _build_unified_synthesis(
        cls,
        ticker_info: Dict[str, Any],
        indicators: Dict[str, Dict[str, Any]],
        alignment_score: float,
        macro_regime: Dict[str, str],
        options_playbook: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Creates a unified executive synthesis of stock movement:
        - Traffic Light Status (GREEN, YELLOW, RED)
        - 1-Sentence Headline Verdict
        - 4 Core Health Pillars (Real Economy, Credit Health, Market Sentiment, Institutional Floor)
        - Quantitative Action Plan (Directive, cash income, return rate, buffer)
        """
        ticker = ticker_info.get("ticker", "STOCK")
        price = ticker_info.get("current_price", 100.0)
        options_data = ticker_info.get("options_data", {})
        csp_matrix = options_playbook.get("cash_secured_put_matrix", {})
        cc_matrix = options_playbook.get("covered_call_matrix", {})

        # 1. Composite Unified Health Score (-100 to +100)
        tech_score = 0.0
        if ticker_info.get("diff_ma50_pct", 0.0) > 0:
            tech_score += 10.0
        else:
            tech_score -= 10.0
        if ticker_info.get("diff_ma200_pct", 0.0) > 0:
            tech_score += 10.0
        else:
            tech_score -= 10.0

        gex_regime = options_data.get("gamma_regime", "")
        if "POSITIVE GAMMA" in gex_regime:
            gamma_score = 15.0
        elif "NEGATIVE GAMMA" in gex_regime:
            gamma_score = -15.0
        else:
            gamma_score = 0.0

        composite_score = float(np.clip(alignment_score * 0.60 + tech_score + gamma_score, -100.0, 100.0))

        # 2. Traffic Light Status & Headline Verdict
        if composite_score >= 18.0:
            traffic_light = "GREEN LIGHT"
            traffic_color = "#059669"  # Emerald
            verdict_headline = f"Market conditions are solidly in {ticker}'s favor with healthy business fundamentals and strong institutional price support."
            direction_title = "Favorable Uptrend / Safe Accumulation"
        elif composite_score <= -18.0:
            traffic_light = "RED LIGHT"
            traffic_color = "#E11D48"  # Rose
            verdict_headline = f"Warning lights are flashing across borrowing and macro markets; protect capital and avoid chasing {ticker}."
            direction_title = "Defensive / Downside Risk Caution"
        else:
            traffic_light = "YELLOW LIGHT"
            traffic_color = "#D97706"  # Amber
            verdict_headline = f"{ticker} is moving sideways in a neutral channel with balanced push-and-pull between buyers and sellers."
            direction_title = "Neutral / Sideways Range-Bound"

        # 3. Four Health Pillars
        # Pillar 1: Real Economy (Physical Goods & Shipping)
        copx_gld = indicators.get("COPX_GLD", {}).get("trend_signal", "Neutral")
        pkg_spy = indicators.get("PKG_SPY", {}).get("trend_signal", "Neutral")
        xly_xlp = indicators.get("XLY_XLP", {}).get("trend_signal", "Neutral")

        real_eco_bull = sum(1 for s in [copx_gld, pkg_spy, xly_xlp] if "Rising" in s)
        if real_eco_bull >= 2:
            p1_status = "Healthy & Expanding"
            p1_text = "Physical goods, factories, and shipping freight demand expanding."
        elif real_eco_bull == 0:
            p1_status = "Slowing Down"
            p1_text = "Physical demand and shipping freight volumes cooling down."
        else:
            p1_status = "Steady / Stable"
            p1_text = "Everyday physical goods and freight shipping demand holding steady."

        # Pillar 2: Borrowing Health (Corporate Debts & Solvency)
        hyg_lqd = indicators.get("HYG_LQD", {}).get("trend_signal", "Neutral")
        if "Rising" in hyg_lqd:
            p2_status = "Solid / Easy Borrowing"
            p2_text = "Credit spreads narrow; corporate borrowing and liquidity healthy."
        elif "Falling" in hyg_lqd:
            p2_status = "Tightening Stress"
            p2_text = "Widening credit spreads; corporate borrowing and debt costs increasing."
        else:
            p2_status = "Normal / Balanced"
            p2_text = "Credit markets balanced with stable corporate debt financing."

        # Pillar 3: Market Sentiment (Fear vs Greed)
        vix9d_vix = indicators.get("VIX9D_VIX", {}).get("trend_signal", "Neutral")
        vix_spx = indicators.get("VIX_SPX", {}).get("trend_signal", "Neutral")
        lottery_ratio = options_data.get("lottery_call_ratio", 10.0)

        if "Rising" in vix9d_vix or "Rising" in vix_spx:
            p3_status = "Anxious / Guarded"
            p3_text = "Elevated put hedging; short-term downside anxiety elevated."
        elif lottery_ratio > 25.0:
            p3_status = "Over-Excited (FOMO)"
            p3_text = "High retail lottery call speculation; pullback risk elevated."
        else:
            p3_status = "Calm & Orderly"
            p3_text = "Market sentiment calm; volatility orderly without panic spikes."

        # Pillar 4: Institutional Setup (Dealer Gamma Cushion & Safety Floor)
        flip_strike = options_data.get("gamma_flip_strike", price * 0.95)

        if price >= flip_strike:
            p4_status = "Supportive Floor"
            p4_text = f"Positive dealer gamma cushion above ${flip_strike:.2f} floor."
        else:
            p4_status = "Below Safety Floor"
            p4_text = f"Below ${flip_strike:.2f} safety floor; accelerating negative gamma zone."

        # 4. Action Plan
        best_csp = csp_matrix.get("balanced", {})
        best_cc = cc_matrix.get("balanced", {})
        selected_dte = options_data.get("selected_dte", 30)

        if composite_score >= 0:
            strike = best_csp.get("strike", round(price * 0.92, 2))
            premium = best_csp.get("premium", round(price * 0.02, 2))
            buffer_pct = best_csp.get("otm_pct", 8.0)
            net_cost = best_csp.get("net_cost_basis", round(strike - premium, 2))
            cash_upfront = int(premium * 100)
            ann_roc = best_csp.get("annualized_roc", 18.0)
            directive = f"Sell ${strike:.2f} Put ({selected_dte} DTE)"
            rate_val = ann_roc
            rate_label = "Annualized ROC"
            buffer_val = buffer_pct
            buffer_label = "Downside Buffer"
            
            action_headline = f"Get Paid ${cash_upfront} Today to Buy {ticker} at an {buffer_pct:.1f}% Discount"
            action_steps = [
                f"1. Sell one ${strike:.2f} Put contract (expiring in {selected_dte} days).",
                f"2. Collect ${cash_upfront} upfront cash deposited immediately into your account.",
                f"3. Unassigned Outcome: If {ticker} stays above ${strike:.2f}, pocket the entire ${cash_upfront} ({ann_roc:.1f}% annualized return).",
                f"4. Assigned Outcome: If {ticker} drops below ${strike:.2f}, acquire shares at net basis of ${net_cost:.2f} ({buffer_pct:.1f}% discount)."
            ]
            action_summary = f"Collect ${cash_upfront} upfront cash per contract with downside protection to ${net_cost:.2f}."
        else:
            strike = best_cc.get("strike", round(price * 1.05, 2))
            premium = best_cc.get("premium", round(price * 0.02, 2))
            upside_pct = best_cc.get("otm_pct", 5.0)
            cash_upfront = int(premium * 100)
            ann_yield = best_cc.get("yield_unassigned", 18.0)
            max_profit = int((strike - price + premium) * 100)
            directive = f"Sell ${strike:.2f} Call ({selected_dte} DTE)"
            rate_val = ann_yield
            rate_label = "Annualized Yield"
            buffer_val = upside_pct
            buffer_label = "Price Upside Cap"

            action_headline = f"Collect ${cash_upfront} Defense Cash on Your {ticker} Shares"
            action_steps = [
                f"1. If holding 100 shares of {ticker}, sell one ${strike:.2f} Call contract ({selected_dte} DTE).",
                f"2. Collect ${cash_upfront} upfront cash credit as immediate downside defense.",
                f"3. Unassigned Outcome: If {ticker} stays below ${strike:.2f}, retain shares and keep ${cash_upfront} ({ann_yield:.1f}% annualized yield).",
                f"4. Called Away Outcome: If {ticker} rallies past ${strike:.2f}, deliver shares at ${strike:.2f} for total profit of ${max_profit}."
            ]
            action_summary = f"Collect ${cash_upfront} upfront cash per 100 shares for downside defense while allowing {upside_pct:.1f}% upside."

        return {
            "traffic_light": traffic_light,
            "traffic_color": traffic_color,
            "composite_score": round(composite_score, 1),
            "direction_title": direction_title,
            "verdict_headline": verdict_headline,
            "pillars": {
                "real_economy": {
                    "title": "Real Economy (Goods & Shipping)",
                    "status": p1_status,
                    "explanation": p1_text
                },
                "borrowing_health": {
                    "title": "Borrowing Health (Corporate Debts)",
                    "status": p2_status,
                    "explanation": p2_text
                },
                "crowd_mood": {
                    "title": "Crowd Mood (Fear vs Greed)",
                    "status": p3_status,
                    "explanation": p3_text
                },
                "smart_money": {
                    "title": "Smart Money (Institutional Safety Floor)",
                    "status": p4_status,
                    "safety_floor": f"${flip_strike:.2f}",
                    "explanation": p4_text
                }
            },
            "plain_dollar_action": {
                "headline": action_headline,
                "directive": directive,
                "cash_collected_dollars": cash_upfront,
                "rate_val": round(rate_val, 1),
                "rate_label": rate_label,
                "buffer_val": round(buffer_val, 1),
                "buffer_label": buffer_label,
                "summary": action_summary,
                "steps": action_steps
            }
        }
