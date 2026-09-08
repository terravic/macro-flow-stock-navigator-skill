"""
UI Dashboard Renderer.
Renders concise, executive Markdown dashboards and structured JSON/HTML payloads.
"""

import json
from datetime import datetime
from typing import Dict, Any, List

class DashboardRenderer:
    """
    Renders the executive Macro Flow Stock Navigator dashboard.
    """

    @classmethod
    def render_markdown(
        cls,
        ticker_info: Dict[str, Any],
        indicators: Dict[str, Dict[str, Any]],
        decision: Dict[str, Any],
        shares_held: int = 0,
        cash_available: float = 0.0
    ) -> str:
        """
        Builds a concise, business-like Markdown response focusing on Macro alignment
        and dedicated Options Selling analysis (Covered Calls & Cash-Secured Puts).
        """
        ticker = ticker_info.get("ticker", "UNKNOWN")
        price = ticker_info.get("current_price", 0.0)
        chg = ticker_info.get("change_pct", 0.0)
        chg_str = f"+{chg:.2f}%" if chg >= 0 else f"{chg:.2f}%"
        action_badge = decision.get("signal_badge", "NEUTRAL")
        archetype_name = decision.get("archetype_name", "General Stock")
        macro_regime = decision.get("macro_regime", {})
        playbook = decision.get("options_playbook", {})
        tactical = playbook.get("tactical_execution", {})
        opt_analytics = playbook.get("options_analytics", {})
        cc_matrix = playbook.get("covered_call_matrix", {})
        csp_matrix = playbook.get("cash_secured_put_matrix", {})
        uoa_list = playbook.get("unusual_activity", [])
        warnings = playbook.get("risk_warnings", [])
        last_trade_date = ticker_info.get("last_trade_date", datetime.now().strftime("%Y-%m-%d"))
        
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M UTC")

        lines = []

        # ---------------------------------------------------------
        # 1. HEADER & EXECUTIVE SUMMARY
        # ---------------------------------------------------------
        lines.append(f"# Macro Flow Stock Navigator: {ticker}")
        lines.append("")
        lines.append("| Metric | Value | Metric | Value |")
        lines.append("| :--- | :--- | :--- | :--- |")
        lines.append(f"| **Current Price** | ${price:.2f} ({chg_str}) | **Stock Archetype** | {archetype_name} |")
        lines.append(f"| **Recommended Action** | {action_badge} | **Macro Alignment** | {decision.get('alignment_gauge', '')} |")
        lines.append(f"| **Macro Regime** | {macro_regime.get('name', 'Balanced Rotation')} | **Last Session Close** | {last_trade_date} |")
        lines.append(f"| **Analysis Timestamp** | {timestamp_str} | **Market Status** | Real-Time / Last Close ({last_trade_date}) |")
        lines.append("")

        # Optional Portfolio Overlay (Shares Held or Cash Collateral)
        if shares_held > 0 or cash_available > 0:
            lines.append("## Portfolio Positioning & Tailored Options Recommendations")
            lines.append("")
            if shares_held > 0:
                num_contracts = shares_held // 100
                remainder = shares_held % 100
                lines.append(f"### Tailored Covered Call Strategy ({shares_held:,} Shares Held)")
                if num_contracts > 0:
                    lines.append(f"- **Covered Call Capacity:** `{num_contracts} contract(s)` (100 shares per contract). Remainder unhedged: `{remainder} shares`.")
                    balanced_cc = cc_matrix.get("balanced", {})
                    cons_cc = cc_matrix.get("conservative", {})
                    agg_cc = cc_matrix.get("aggressive", {})
                    
                    if balanced_cc:
                        mid_p = balanced_cc.get("mid", 0.0)
                        prem_total = mid_p * 100.0 * num_contracts
                        lines.append(f"- **Recommended Strike:** `${balanced_cc.get('strike', 0.0):.2f}` ({balanced_cc.get('delta', 0.0):+.2f}Δ, ~{balanced_cc.get('otm_pct', 0.0):.1f}% OTM) expiring in `{balanced_cc.get('dte', 30)}d`.")
                        lines.append(f"- **Est. Income Generated:** `${prem_total:,.2f}` upfront cash premium (`+{balanced_cc.get('yield_unassigned', 0.0):.1f}%` annualized yield).")
                        lines.append(f"- **If Called Away:** Total realized gain of `+${((balanced_cc.get('strike', price) - price + mid_p) * 100.0 * num_contracts):,.2f}` (`+{balanced_cc.get('return_called_away', 0.0):.1f}%`).")
                        lines.append(f"- **Alternative Tiers:** Conservative Strike: `${cons_cc.get('strike', 0.0):.2f}` (`${cons_cc.get('mid', 0.0)*100*num_contracts:,.2f}` income) | Aggressive Strike: `${agg_cc.get('strike', 0.0):.2f}` (`${agg_cc.get('mid', 0.0)*100*num_contracts:,.2f}` income).")
                else:
                    lines.append(f"- *Note:* Covered calls require increments of 100 shares per contract. You hold {shares_held} shares. Accumulate {100 - remainder} more shares to sell 1 covered call contract.")
                lines.append("")

            if cash_available > 0:
                balanced_csp = csp_matrix.get("balanced", {})
                cons_csp = csp_matrix.get("conservative", {})
                agg_csp = csp_matrix.get("aggressive", {})
                
                strike = balanced_csp.get("strike", price * 0.95)
                req_per_contract = strike * 100.0
                num_csp = int(cash_available // req_per_contract)
                lines.append(f"### Tailored Cash-Secured Put Strategy (${cash_available:,.2f} Cash Available)")
                if num_csp > 0:
                    mid_p = balanced_csp.get("mid", 0.0)
                    prem_total = mid_p * 100.0 * num_csp
                    unused_cash = cash_available - (num_csp * req_per_contract)
                    lines.append(f"- **Cash-Secured Put Capacity:** `{num_csp} contract(s)` at `${strike:.2f}` strike (Collateral utilized: `${num_csp * req_per_contract:,.2f}`, Unused cash: `${unused_cash:,.2f}`).")
                    lines.append(f"- **Target Strike:** `${strike:.2f}` ({balanced_csp.get('delta', 0.0):+.2f}Δ, ~{balanced_csp.get('otm_pct', 0.0):.1f}% discount) expiring in `{balanced_csp.get('dte', 30)}d`.")
                    lines.append(f"- **Est. Cash Premium Harvest:** `+${prem_total:,.2f}` upfront credit (`+{balanced_csp.get('annualized_roc', 0.0):.1f}%` annualized ROC).")
                    lines.append(f"- **Net Effective Purchase Price if Assigned:** `${balanced_csp.get('net_cost_basis', strike - mid_p):.2f}` (`{balanced_csp.get('discount_pct', 0.0):.1f}%` discount below current market price ${price:.2f}).")
                    lines.append(f"- **Alternative Tiers:** Conservative Strike: `${cons_csp.get('strike', 0.0):.2f}` ({int(cash_available // (cons_csp.get('strike', strike)*100))} contracts, `+${cons_csp.get('annualized_roc', 0.0):.1f}%` ROC) | Aggressive Strike: `${agg_csp.get('strike', 0.0):.2f}` (`+${agg_csp.get('annualized_roc', 0.0):.1f}%` ROC).")
                else:
                    lines.append(f"- *Note:* 1 Cash-Secured Put contract at the balanced strike (${strike:.2f}) requires `${req_per_contract:,.2f}` in collateral. You have `${cash_available:,.2f}`.")
                lines.append("")

        # ---------------------------------------------------------
        # 2. MACRO INDICATORS TABLE
        # ---------------------------------------------------------
        lines.append("## 1. Macro Cross-Asset Indicators (8 Ratios)")
        lines.append("")
        lines.append("| Indicator | Ratio Tickers | Current Value | 50-MA Status | Trend | Interpretation |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")

        for ind_id, ind in indicators.items():
            disp_name = ind.get("display_name", ind_id)
            ratio = ind.get("ratio_tickers", ind_id)
            val = ind.get("current_value", 0.0)
            ma_stat = ind.get("ma50_status", "N/A")
            trend = ind.get("trend_signal", "Flat")
            meaning = ind.get("market_meaning", "")
            lines.append(f"| **{disp_name}** | `{ratio}` | `{val}` | {ma_stat} | {trend} | {meaning} |")

        lines.append("")

        # ---------------------------------------------------------
        # 3. MACRO DRIVERS & SENSITIVITY
        # ---------------------------------------------------------
        lines.append("## 2. Macro Drivers & Sensitivity Analysis")
        lines.append("")
        lines.append(f"- **Technical Health:** Price vs 50-MA: `{ticker_info.get('diff_ma50_pct', 0.0):+.2f}%` | 200-MA: `{ticker_info.get('diff_ma200_pct', 0.0):+.2f}%` | RSI(14): `{ticker_info.get('rsi_14', 50.0)}` | 30d Realized Vol: `{ticker_info.get('historical_vol_30d', 0.0)}%` | Beta: `{ticker_info.get('beta', 1.0)}`")
        lines.append(f"- **Regime Context:** {macro_regime.get('summary', '')}")
        lines.append("")

        favorable = decision.get("favorable_forces", [])
        hostile = decision.get("hostile_forces", [])

        if favorable:
            lines.append("**Key Macro Tailwinds (Positive Drivers):**")
            for f in favorable:
                lines.append(f"- **{f['indicator']} (`{f['ratio']}`)** is {f['trend']}: {f['meaning']}.")
        else:
            lines.append("- *No dominant macro tailwinds detected.*")

        lines.append("")
        if hostile:
            lines.append("**Key Macro Headwinds (Risk Factors):**")
            for h in hostile:
                lines.append(f"- **{h['indicator']} (`{h['ratio']}`)** is {h['trend']}: {h['meaning']}.")
        else:
            lines.append("- *No major macro headwinds detected.*")

        lines.append("")

        # ---------------------------------------------------------
        # 4. OPTIONS VOLATILITY & KEY INDICATORS
        # ---------------------------------------------------------
        lines.append("## 3. Options Volatility & Market Indicators")
        lines.append("")
        lines.append("| Metric / Indicator | Value | Strategic Interpretation |")
        lines.append("| :--- | :--- | :--- |")
        lines.append(f"| **Implied Volatility (ATM)** | `{opt_analytics.get('iv_atm', 0.0)}%` | Pricing baseline for near-term option premium |")
        lines.append(f"| **30-Day Realized Volatility** | `{opt_analytics.get('hv_30d', 0.0)}%` | Historical asset price dispersion |")
        lines.append(f"| **IV vs RV Spread** | `{opt_analytics.get('iv_rv_spread', 0.0):+.1f}%` | {'Option premiums rich (favorable for selling)' if opt_analytics.get('iv_rv_spread', 0) >= 0 else 'Option premiums lean (conservative strike selection)'} |")
        lines.append(f"| **IV Rank & Percentile** | `{opt_analytics.get('iv_rank', 0.0)}%` / `{opt_analytics.get('iv_percentile', 0.0)}%` | Relative IV positioning across 52-week envelope |")
        lines.append(f"| **Put/Call Ratio (Vol / OI)** | `{opt_analytics.get('pcr_volume', 1.0)}` / `{opt_analytics.get('pcr_open_interest', 1.0)}` | Institutional hedging vs call speculation sentiment |")
        lines.append(f"| **Max Pain Theory Strike** | `${opt_analytics.get('max_pain_strike', price):.2f}` | Strike where total option expiration value is minimized |")
        lines.append(f"| **30-Day Expected Move (±1σ)** | `±${opt_analytics.get('expected_move_30d', 0.0):.2f} (±{opt_analytics.get('expected_move_pct', 0.0):.1f}%)` | Target range: `${opt_analytics.get('expected_move_lower', 0.0):.2f} – ${opt_analytics.get('expected_move_upper', 0.0):.2f}` |")
        lines.append("")

        # ---------------------------------------------------------
        # 5. COVERED CALL & CASH-SECURED PUT SCREENER MATRICES
        # ---------------------------------------------------------
        lines.append("## 4. Options Selling Playbook: Covered Calls & Cash-Secured Puts")
        lines.append("")
        lines.append(f"### Recommended Primary Focus: **{tactical.get('strategy', 'Neutral Options Overlay')}**")
        lines.append(f"*{tactical.get('rationale', '')}*")
        lines.append("")

        # Covered Call Screener Table
        lines.append("### A. Covered Call Screener Matrix (Long Stock + Sell Call)")
        lines.append("| Tier | Target Δ | Strike | Mid Price | OTM % | Ann. Yield (Unassigned) | Total Return (Called) | Downside Buffer | DTE |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for tier_key, tier_title in [("conservative", "Conservative (0.20Δ)"), ("balanced", "Balanced (0.30Δ)"), ("aggressive", "Aggressive (0.40Δ)")]:
            c = cc_matrix.get(tier_key, {})
            if c:
                lines.append(f"| **{tier_title}** | `{c.get('delta', 0.0):+.2f}` | `${c.get('strike', 0.0):.2f}` | `${c.get('mid', 0.0):.2f}` | `+{c.get('otm_pct', 0.0):.1f}%` | `+{c.get('yield_unassigned', 0.0):.1f}%` | `+{c.get('return_called_away', 0.0):.1f}%` | `+{c.get('downside_protection', 0.0):.1f}%` | `{c.get('dte', 30)}d` |")
        lines.append("")

        # Cash-Secured Put Screener Table
        lines.append("### B. Cash-Secured Put Screener Matrix (Sell Put + Cash Collateral)")
        lines.append("| Tier | Target Δ | Strike | Mid Price | OTM % | Required Collateral | Net Cost Basis | Discount vs Spot | Ann. ROC | DTE |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for tier_key, tier_title in [("conservative", "Conservative (0.20Δ)"), ("balanced", "Balanced (0.30Δ)"), ("aggressive", "Aggressive (0.40Δ)")]:
            p = csp_matrix.get(tier_key, {})
            if p:
                lines.append(f"| **{tier_title}** | `{p.get('delta', 0.0):+.2f}` | `${p.get('strike', 0.0):.2f}` | `${p.get('mid', 0.0):.2f}` | `-{p.get('otm_pct', 0.0):.1f}%` | `${p.get('collateral_required', 0.0):,.0f}` | `${p.get('net_cost_basis', 0.0):.2f}` | `{p.get('discount_pct', 0.0):.1f}%` | `+{p.get('annualized_roc', 0.0):.1f}%` | `{p.get('dte', 30)}d` |")
        lines.append("")

        # ---------------------------------------------------------
        # 6. UNUSUAL OPTION ACTIVITY
        # ---------------------------------------------------------
        if uoa_list:
            lines.append("## 5. Unusual Option Activity & Institutional Flow Detection")
            lines.append("")
            lines.append("| Type | Strike | Volume | Open Int | Vol/OI | Est. Dollar Flow | Institutional Sentiment |")
            lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
            for uoa in uoa_list:
                lines.append(f"| **{uoa.get('option_type')}** | `${uoa.get('strike', 0.0):.2f}` | `{uoa.get('volume', 0):,}` | `{uoa.get('open_interest', 0):,}` | `{uoa.get('vol_oi_ratio', 0.0):.1f}x` | `${uoa.get('dollar_flow', 0.0):,.0f}` | {uoa.get('sentiment', 'Flow Sweep')} |")
            lines.append("")

        # ---------------------------------------------------------
        # 7. RISK CONSIDERATIONS
        # ---------------------------------------------------------
        lines.append("## 6. Execution Rules & Risk Considerations")
        lines.append(f"- **Target DTE Window:** `{tactical.get('target_dte', '30-45 DTE')}` for optimal theta acceleration.")
        lines.append(f"- **Profit Target Rule:** Close position at `{tactical.get('profit_target', '50% of credit')}` captured.")
        lines.append(f"- **Stop Loss / Defensive Rule:** `{tactical.get('stop_loss_rule', '2x credit')}` or roll out in time upon test.")
        for w in warnings:
            lines.append(f"- {w}")

        lines.append("")
        lines.append("---")
        lines.append("*Disclaimer: Macro Flow Stock Navigator is an analytical decision-support tool. Not personalized financial advice. Always verify live order book liquidity and portfolio margin before trading.*")

        return "\n".join(lines)

    @classmethod
    def render_json(
        cls,
        ticker_info: Dict[str, Any],
        indicators: Dict[str, Dict[str, Any]],
        decision: Dict[str, Any]
    ) -> str:
        """
        Builds a structured JSON payload for programmatic consumption.
        """
        payload = {
            "metadata": {
                "skill": "macro-flow-stock-navigator",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat()
            },
            "ticker_info": ticker_info,
            "decision": {
                "action_signal": decision.get("stock_signal"),
                "signal_badge": decision.get("signal_badge"),
                "conviction": decision.get("conviction"),
                "alignment_score": decision.get("alignment_score"),
                "macro_regime": decision.get("macro_regime"),
                "favorable_forces": decision.get("favorable_forces"),
                "hostile_forces": decision.get("hostile_forces"),
            },
            "macro_indicators": indicators,
            "options_playbook": decision.get("options_playbook")
        }
        return json.dumps(payload, indent=2)

    @classmethod
    def render_html(
        cls,
        ticker_info: Dict[str, Any],
        indicators: Dict[str, Dict[str, Any]],
        decision: Dict[str, Any],
        shares_held: int = 0,
        cash_available: float = 0.0
    ) -> str:
        """
        Builds a rich, interactive HTML/JS/CSS Canvas Dashboard.
        Includes theme toggle, interactive charts, 8 Macro indicator visualizers,
        comprehensive Options Selling matrices (Covered Calls & Cash-Secured Puts),
        live option chain table explorer, unusual options flow tracker, and dual-mode payoff simulator.
        Features zero-dependency standalone native Canvas chart renderers with Chart.js enhancement.
        """
        ticker = ticker_info.get("ticker", "UNKNOWN")
        price = ticker_info.get("current_price", 0.0)
        chg = ticker_info.get("change_pct", 0.0)
        chg_str = f"+{chg:.2f}%" if chg >= 0 else f"{chg:.2f}%"
        chg_class = "positive" if chg >= 0 else "negative"
        last_trade_date = ticker_info.get("last_trade_date", datetime.now().strftime("%Y-%m-%d"))
        
        action_badge = decision.get("signal_badge", "NEUTRAL")
        archetype_name = decision.get("archetype_name", "General Stock")
        archetype_desc = ticker_info.get("archetype_desc", "")
        macro_regime = decision.get("macro_regime", {})
        playbook = decision.get("options_playbook", {})
        tactical = playbook.get("tactical_execution", {})
        opt_analytics = playbook.get("options_analytics", {})
        cc_matrix = playbook.get("covered_call_matrix", {})
        csp_matrix = playbook.get("cash_secured_put_matrix", {})
        uoa_list = playbook.get("unusual_activity", [])
        opt_chain = playbook.get("options_chain", {})
        warnings = playbook.get("risk_warnings", [])
        
        favorable = decision.get("favorable_forces", [])
        hostile = decision.get("hostile_forces", [])
        
        price_history = ticker_info.get("price_history", {
            "dates": [],
            "prices": [],
            "ma50": [],
            "ma200": []
        })

        # Format indicator and options data for JS injection
        indicators_json = json.dumps(indicators)
        history_json = json.dumps(price_history)
        decision_json = json.dumps(decision)
        ticker_json = json.dumps(ticker_info)
        playbook_json = json.dumps(playbook)

        first_ind_key = list(indicators.keys())[0] if indicators else "NDX_SPX"
        first_ind = indicators.get(first_ind_key, {})
        first_name = first_ind.get("display_name", first_ind_key)
        first_ratio = first_ind.get("ratio_tickers", first_ind_key)
        first_val_str = f"{first_ind.get('current_value', 0.0)} ({first_ind.get('ma50_status', 'N/A')})"
        first_pctl_str = f"{first_ind.get('percentile_90d', 50.0):.1f}% ({first_ind.get('trend_signal', 'Neutral')})"
        first_meaning = f"{first_name} ({first_ratio}): {first_ind.get('market_meaning', '')}"
        first_trend = first_ind.get("trend_signal", "Neutral")
        first_status_class = "trend-bullish" if "Above" in first_ind.get("ma50_status", "") or "Rising" in first_trend else ("trend-bearish" if "Below" in first_ind.get("ma50_status", "") or "Falling" in first_trend else "trend-neutral")

        # 1. Indicator cards HTML (Tab 2)
        ind_cards_html = []
        # 2. Indicator chart cards HTML (Tab 3 Grid)
        ind_chart_cards_html = []
        # 3. Macro selector pills HTML (Tab 3 Focus View)
        macro_pills_html = []

        for ind_id, ind in indicators.items():
            name = ind.get("display_name", ind_id)
            ratio = ind.get("ratio_tickers", ind_id)
            val = ind.get("current_value", 0.0)
            ma_stat = ind.get("ma50_status", "N/A")
            trend = ind.get("trend_signal", "Flat")
            meaning = ind.get("market_meaning", "")
            percentile = ind.get("percentile_90d", 50.0)
            status_class = "trend-bullish" if "Above" in ma_stat or "Rising" in trend else ("trend-bearish" if "Below" in ma_stat or "Falling" in trend else "trend-neutral")
            
            # Tab 2 Card
            ind_cards_html.append(f"""
            <div class="ind-card" data-trend="{status_class}">
                <div class="ind-card-header">
                    <div>
                        <div class="ind-card-title">{name}</div>
                        <div class="ind-card-ratio font-mono">{ratio}</div>
                    </div>
                    <span class="badge {status_class}">{trend}</span>
                </div>
                <div class="ind-card-body">
                    <div class="ind-metric-row">
                        <span class="label" data-tooltip="Latest calculated cross-asset ratio value (e.g. QQQ/SPY, HYG/TLT).">Current Value <span class="info-tip">?</span></span>
                        <span class="val font-mono">{val:.4f}</span>
                    </div>
                    <div class="ind-metric-row">
                        <span class="label" data-tooltip="Indicates whether the ratio is above or below its 50-day moving average, signaling momentum direction.">50-MA Status <span class="info-tip">?</span></span>
                        <span class="val">{ma_stat}</span>
                    </div>
                    <div class="ind-metric-row">
                        <span class="label" data-tooltip="Ranks current ratio level relative to its last 90 trading days (0% = 90d low, 100% = 90d high).">90d Percentile <span class="info-tip">?</span></span>
                        <span class="val">{percentile:.1f}%</span>
                    </div>
                    <div class="progress-track">
                        <div class="progress-bar" style="width: {min(100, max(0, percentile))}%;"></div>
                    </div>
                    <div class="ind-meaning">{meaning}</div>
                    <div style="margin-top: 10px; text-align: right;">
                        <button class="mini-inspect-btn" onclick="switchTab('charts'); selectFocusIndicator('{ind_id}');">
                            View Chart &rarr;
                        </button>
                    </div>
                </div>
            </div>
            """)

            # Tab 3 Indicator Chart Card
            ind_chart_cards_html.append(f"""
            <div class="card ind-chart-card">
                <div class="card-header" style="margin-bottom: 8px; padding-bottom: 8px;">
                    <div>
                        <div class="card-title" style="font-size: 13px;">{name}</div>
                        <div class="ind-card-ratio font-mono">{ratio}</div>
                    </div>
                    <span class="badge {status_class}" style="font-size: 10px; padding: 2px 6px;">{trend}</span>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 8px; color: var(--text-secondary);">
                    <span>Val: <b class="font-mono" style="color: var(--text-primary);">{val}</b></span>
                    <span>MA50: <b style="color: var(--text-primary);">{ma_stat}</b></span>
                    <span>Pctl: <b class="font-mono" style="color: var(--text-primary);">{percentile:.1f}%</b></span>
                </div>
                <div class="chart-container-sm">
                    <canvas id="chart_{ind_id}"></canvas>
                </div>
                <div style="margin-top: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 11px; color: var(--text-muted); flex: 1; margin-right: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{meaning}">
                        {meaning}
                    </div>
                    <button class="mini-inspect-btn" onclick="selectFocusIndicator('{ind_id}'); window.scrollTo({{top: document.getElementById('focusVisualizerCard').offsetTop - 80, behavior: 'smooth'}});">
                        Inspect
                    </button>
                </div>
            </div>
            """)

            # Tab 3 Selector Pill
            is_active_pill = "active" if ind_id == first_ind_key else ""
            macro_pills_html.append(f"""
            <button class="macro-pill-btn {is_active_pill}" data-key="{ind_id}" onclick="selectFocusIndicator('{ind_id}')">
                {ratio}
            </button>
            """)

        ind_cards_rendered = "\n".join(ind_cards_html)
        ind_chart_cards_rendered = "\n".join(ind_chart_cards_html)
        macro_pill_buttons_rendered = "\n".join(macro_pills_html)

        # 4. Covered Call Matrix Rows (Tab 4)
        cc_rows_html = []
        for tier_key, tier_title in [("conservative", "Conservative (0.20Δ)"), ("balanced", "Balanced (0.30Δ)"), ("aggressive", "Aggressive (0.40Δ)")]:
            c = cc_matrix.get(tier_key, {})
            if c:
                cc_rows_html.append(f"""
                <tr>
                    <td><b>{tier_title}</b></td>
                    <td class="font-mono">${c.get('strike', 0.0):.2f}</td>
                    <td class="font-mono">${c.get('mid', 0.0):.2f}</td>
                    <td class="font-mono">{c.get('delta', 0.0):+.2f}</td>
                    <td class="font-mono">{c.get('theta', 0.0):.3f}</td>
                    <td class="font-mono">+{c.get('otm_pct', 0.0):.1f}%</td>
                    <td class="font-mono" style="color: var(--accent-green); font-weight: 700;">+{c.get('yield_unassigned', 0.0):.1f}%</td>
                    <td class="font-mono" style="color: var(--accent-blue); font-weight: 700;">+{c.get('return_called_away', 0.0):.1f}%</td>
                    <td class="font-mono">+{c.get('downside_protection', 0.0):.1f}%</td>
                    <td>
                        <button class="mini-inspect-btn" onclick="loadIntoSimulator('CC', {c.get('strike', 0.0)}, {c.get('mid', 0.0)}, {price})">
                            Simulate
                        </button>
                    </td>
                </tr>
                """)
        cc_rows_rendered = "\n".join(cc_rows_html)

        # 5. Cash-Secured Put Matrix Rows (Tab 4)
        csp_rows_html = []
        for tier_key, tier_title in [("conservative", "Conservative (0.20Δ)"), ("balanced", "Balanced (0.30Δ)"), ("aggressive", "Aggressive (0.40Δ)")]:
            p = csp_matrix.get(tier_key, {})
            if p:
                csp_rows_html.append(f"""
                <tr>
                    <td><b>{tier_title}</b></td>
                    <td class="font-mono">${p.get('strike', 0.0):.2f}</td>
                    <td class="font-mono">${p.get('mid', 0.0):.2f}</td>
                    <td class="font-mono">{p.get('delta', 0.0):+.2f}</td>
                    <td class="font-mono">{p.get('theta', 0.0):.3f}</td>
                    <td class="font-mono">-{p.get('otm_pct', 0.0):.1f}%</td>
                    <td class="font-mono">${p.get('collateral_required', 0.0):,.0f}</td>
                    <td class="font-mono">${p.get('net_cost_basis', 0.0):.2f}</td>
                    <td class="font-mono" style="color: var(--accent-cyan); font-weight: 700;">{p.get('discount_pct', 0.0):.1f}%</td>
                    <td class="font-mono" style="color: var(--accent-green); font-weight: 700;">+{p.get('annualized_roc', 0.0):.1f}%</td>
                    <td>
                        <button class="mini-inspect-btn" onclick="loadIntoSimulator('CSP', {p.get('strike', 0.0)}, {p.get('mid', 0.0)}, {price})">
                            Simulate
                        </button>
                    </td>
                </tr>
                """)
        csp_rows_rendered = "\n".join(csp_rows_html)

        # 6. Unusual Option Activity Rows (Tab 4)
        uoa_rows_html = []
        for uoa in uoa_list:
            type_class = "trend-bullish" if uoa.get("option_type") == "CALL" else "trend-bearish"
            uoa_rows_html.append(f"""
            <tr>
                <td><span class="badge {type_class}">{uoa.get('option_type')}</span></td>
                <td class="font-mono" style="font-size: 11px;">{uoa.get('contract', '')}</td>
                <td class="font-mono">${uoa.get('strike', 0.0):.2f}</td>
                <td class="font-mono">{uoa.get('volume', 0):,}</td>
                <td class="font-mono">{uoa.get('open_interest', 0):,}</td>
                <td class="font-mono" style="font-weight: 700; color: var(--accent-amber);">{uoa.get('vol_oi_ratio', 0.0):.1f}x</td>
                <td class="font-mono" style="font-weight: 700; color: var(--accent-blue);">${uoa.get('dollar_flow', 0.0):,.0f}</td>
                <td style="font-size: 12px;">{uoa.get('sentiment', '')}</td>
            </tr>
            """)
        uoa_rows_rendered = "\n".join(uoa_rows_html) if uoa_rows_html else "<tr><td colspan='8' style='text-align:center; color: var(--text-muted);'>No unusual option volume anomalies detected.</td></tr>"

        # 7. Live Real-Time Option Chain Rows (Tab 4)
        chain_rows_html = []
        all_calls = opt_chain.get("calls", [])
        all_puts = opt_chain.get("puts", [])
        
        chain_items = []
        for c in all_calls:
            chain_items.append({"type": "CALL", "data": c})
        for p in all_puts:
            chain_items.append({"type": "PUT", "data": p})
        chain_items.sort(key=lambda x: x["data"].get("strike", 0.0))

        for item in chain_items:
            t = item["type"]
            d = item["data"]
            strike = d.get("strike", 0.0)
            bid = d.get("bid", 0.0)
            ask = d.get("ask", 0.0)
            mid = d.get("mid", d.get("lastPrice", 0.0))
            delta = d.get("delta", 0.0)
            theta = d.get("theta", 0.0)
            vol = d.get("volume", 0)
            oi = d.get("openInterest", 0)
            vol_oi = d.get("vol_oi_ratio", 0.0)
            iv = d.get("impliedVolatility", 0.0)
            itm = d.get("inTheMoney", False)
            itm_str = "ITM" if itm else "OTM"
            itm_badge = "trend-bearish" if (itm and t == "PUT") or (not itm and t == "CALL") else "trend-bullish"
            t_badge = "trend-bullish" if t == "CALL" else "trend-bearish"
            near_pct = abs((strike - price) / price) * 100.0
            near_class = "chain-row-ntm" if near_pct <= 10.0 else ""
            strategy_mode = "CC" if t == "CALL" else "CSP"

            chain_rows_html.append(f"""
            <tr class="chain-row {near_class}" data-type="{t}" data-near="{ 'true' if near_pct <= 10.0 else 'false' }">
                <td><span class="badge {t_badge}">{t}</span></td>
                <td class="font-mono" style="font-weight: 700;">${strike:.2f}</td>
                <td class="font-mono">${bid:.2f}</td>
                <td class="font-mono">${ask:.2f}</td>
                <td class="font-mono" style="font-weight: 700; color: var(--accent-blue);">${mid:.2f}</td>
                <td class="font-mono">{delta:+.2f}</td>
                <td class="font-mono">{theta:.3f}</td>
                <td class="font-mono">{vol:,}</td>
                <td class="font-mono">{oi:,}</td>
                <td class="font-mono" style="color: {'var(--accent-amber)' if vol_oi >= 1.5 else 'var(--text-secondary)'};">{vol_oi:.1f}x</td>
                <td class="font-mono">{iv:.1f}%</td>
                <td><span class="badge {itm_badge}" style="font-size: 10px; padding: 2px 6px;">{itm_str}</span></td>
                <td>
                    <button class="mini-inspect-btn" onclick="loadIntoSimulator('{strategy_mode}', {strike}, {mid}, {price})">
                        Simulate
                    </button>
                </td>
            </tr>
            """)
        chain_rows_rendered = "\n".join(chain_rows_html)

        # Default simulator initial strike and premium
        init_cc = cc_matrix.get("balanced", {}) or cc_matrix.get("conservative", {})
        init_strike = init_cc.get("strike", round(price * 1.05, 1))
        init_premium = init_cc.get("mid", round(price * 0.025, 2))

        # HTML template
        html_doc = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Macro Flow Stock Navigator: {ticker}</title>
    <!-- Optional Chart.js with automatic Zero-Dependency Canvas Engine Fallback -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
        :root {{
            --bg-body: #0a0e17;
            --bg-card: #121824;
            --bg-card-hover: #1a2233;
            --bg-input: #1b2333;
            --border-color: #243046;
            --border-focus: #3b82f6;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent-blue: #3b82f6;
            --accent-cyan: #06b6d4;
            --accent-green: #10b981;
            --accent-red: #ef4444;
            --accent-amber: #f59e0b;
            --card-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
            --header-bg: #0f1522;
        }}

        [data-theme="light"] {{
            --bg-body: #f1f5f9;
            --bg-card: #ffffff;
            --bg-card-hover: #f8fafc;
            --bg-input: #f1f5f9;
            --border-color: #cbd5e1;
            --border-focus: #2563eb;
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --text-muted: #94a3b8;
            --accent-blue: #2563eb;
            --accent-cyan: #0891b2;
            --accent-green: #059669;
            --accent-red: #dc2626;
            --accent-amber: #d97706;
            --card-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            --header-bg: #ffffff;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
        }}

        body {{
            background-color: var(--bg-body);
            color: var(--text-primary);
            font-size: 14px;
            line-height: 1.5;
            padding-bottom: 40px;
        }}

        .font-mono {{
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        }}

        /* Header Navigation */
        header {{
            background-color: var(--header-bg);
            border-bottom: 1px solid var(--border-color);
            padding: 16px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .brand-title {{
            font-size: 18px;
            font-weight: 700;
            letter-spacing: -0.02em;
        }}

        .brand-subtitle {{
            font-size: 12px;
            color: var(--text-secondary);
        }}

        .header-actions {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .market-status-pill {{
            font-size: 11px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 6px;
            background-color: var(--bg-input);
            border: 1px solid var(--border-color);
            color: var(--accent-cyan);
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .theme-toggle-btn {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 6px 14px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .theme-toggle-btn:hover {{
            border-color: var(--accent-blue);
        }}

        /* Container */
        .container {{
            max-width: 1320px;
            margin: 0 auto;
            padding: 24px 20px;
        }}

        /* Executive Banner */
        .executive-banner {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 20px 24px;
            margin-bottom: 20px;
            box-shadow: var(--card-shadow);
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
        }}

        .ticker-profile {{
            display: flex;
            align-items: baseline;
            gap: 12px;
        }}

        .ticker-symbol {{
            font-size: 28px;
            font-weight: 800;
            letter-spacing: -0.03em;
        }}

        .ticker-price {{
            font-size: 24px;
            font-weight: 700;
        }}

        .ticker-change {{
            font-size: 14px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 4px;
        }}

        .ticker-change.positive {{
            background-color: rgba(16, 185, 129, 0.15);
            color: var(--accent-green);
        }}

        .ticker-change.negative {{
            background-color: rgba(239, 68, 68, 0.15);
            color: var(--accent-red);
        }}

        .banner-metrics {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
        }}

        .metric-pill {{
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}

        .metric-pill .label {{
            font-size: 11px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }}

        .metric-pill .val {{
            font-size: 14px;
            font-weight: 700;
        }}

        /* Badges */
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        .badge-signal-buy {{
            background-color: rgba(16, 185, 129, 0.2);
            color: var(--accent-green);
            border: 1px solid var(--accent-green);
        }}

        .badge-signal-sell {{
            background-color: rgba(239, 68, 68, 0.2);
            color: var(--accent-red);
            border: 1px solid var(--accent-red);
        }}

        .badge-signal-neutral {{
            background-color: rgba(245, 158, 11, 0.2);
            color: var(--accent-amber);
            border: 1px solid var(--accent-amber);
        }}

        .trend-bullish {{
            background-color: rgba(16, 185, 129, 0.12);
            color: var(--accent-green);
        }}

        .trend-bearish {{
            background-color: rgba(239, 68, 68, 0.12);
            color: var(--accent-red);
        }}

        .trend-neutral {{
            background-color: rgba(148, 163, 184, 0.12);
            color: var(--text-secondary);
        }}

        /* Tabs Navigation */
        .tab-bar {{
            display: flex;
            gap: 8px;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 20px;
            overflow-x: auto;
        }}

        .tab-btn {{
            background: none;
            border: none;
            border-bottom: 2px solid transparent;
            padding: 10px 18px;
            color: var(--text-secondary);
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            white-space: nowrap;
        }}

        .tab-btn:hover {{
            color: var(--text-primary);
        }}

        .tab-btn.active {{
            color: var(--accent-blue);
            border-bottom-color: var(--accent-blue);
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        /* Grid Layouts */
        .grid-2 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .grid-3 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .grid-4 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }}

        .grid-6 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 14px;
            margin-bottom: 20px;
        }}

        /* Card Styles */
        .card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 20px;
            box-shadow: var(--card-shadow);
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border-color);
        }}

        .card-title {{
            font-size: 15px;
            font-weight: 700;
            letter-spacing: -0.01em;
        }}

        .card-desc {{
            font-size: 12px;
            color: var(--text-secondary);
        }}

        /* Indicator Card */
        .ind-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: 12px;
        }}

        .ind-card:hover {{
            background-color: var(--bg-card-hover);
        }}

        .ind-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }}

        .ind-card-title {{
            font-size: 14px;
            font-weight: 700;
        }}

        .ind-card-ratio {{
            font-size: 11px;
            color: var(--text-muted);
            font-family: ui-monospace, monospace;
        }}

        .ind-metric-row {{
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            margin-bottom: 4px;
        }}

        .ind-meaning {{
            font-size: 11px;
            color: var(--text-secondary);
            margin-top: 6px;
            line-height: 1.4;
        }}

        /* Progress Bar */
        .progress-track {{
            width: 100%;
            height: 6px;
            background-color: var(--bg-input);
            border-radius: 3px;
            overflow: hidden;
            margin: 6px 0;
        }}

        .progress-bar {{
            height: 100%;
            background-color: var(--accent-blue);
            border-radius: 3px;
        }}

        /* Table Styles */
        .table-wrap {{
            overflow-x: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 13px;
        }}

        th {{
            background-color: var(--bg-input);
            padding: 10px 14px;
            font-size: 11px;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 1px solid var(--border-color);
            white-space: nowrap;
        }}

        td {{
            padding: 12px 14px;
            border-bottom: 1px solid var(--border-color);
            white-space: nowrap;
        }}

        tr:hover td {{
            background-color: var(--bg-card-hover);
        }}

        /* Tactical Playbook Box */
        .playbook-hero {{
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(16, 185, 129, 0.05) 100%);
            border: 1px solid var(--border-color);
            border-left: 4px solid var(--accent-blue);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}

        .playbook-strategy-name {{
            font-size: 20px;
            font-weight: 800;
            color: var(--text-primary);
            margin-bottom: 6px;
        }}

        .playbook-rationale {{
            font-size: 13px;
            color: var(--text-secondary);
            margin-bottom: 16px;
        }}

        .tactical-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 14px;
        }}

        .tactical-cell {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            padding: 12px 14px;
            border-radius: 6px;
        }}

        .tactical-cell .label {{
            font-size: 11px;
            color: var(--text-muted);
            font-weight: 600;
            text-transform: uppercase;
        }}

        .tactical-cell .val {{
            font-size: 15px;
            font-weight: 700;
            color: var(--text-primary);
            margin-top: 4px;
        }}

        /* Interactive Simulator */
        .simulator-box {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }}

        .slider-control {{
            display: flex;
            align-items: center;
            gap: 16px;
            margin: 16px 0;
        }}

        .slider-control input[type="range"] {{
            flex-grow: 1;
            accent-color: var(--accent-blue);
            height: 6px;
        }}

        /* Strategy Mode Switcher */
        .strategy-mode-bar {{
            display: flex;
            gap: 10px;
            margin-bottom: 16px;
        }}

        .strategy-mode-btn {{
            background-color: var(--bg-input);
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .strategy-mode-btn.active {{
            background-color: var(--accent-blue);
            color: #ffffff;
            border-color: var(--accent-blue);
        }}

        /* Filters */
        .filter-group {{
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }}

        .filter-btn {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
        }}

        .filter-btn.active {{
            background-color: var(--accent-blue);
            color: #ffffff;
            border-color: var(--accent-blue);
        }}

        /* Forces Lists */
        .force-item {{
            display: flex;
            align-items: flex-start;
            gap: 10px;
            padding: 8px 0;
            border-bottom: 1px solid var(--border-color);
            font-size: 13px;
        }}

        .force-item:last-child {{
            border-bottom: none;
        }}

        .force-tag {{
            font-weight: 700;
            min-width: 90px;
        }}

        .force-desc {{
            color: var(--text-secondary);
        }}

        /* Chart Canvas Containers */
        .chart-container {{
            position: relative;
            height: 320px;
            width: 100%;
        }}

        .chart-container-sm {{
            position: relative;
            height: 180px;
            width: 100%;
        }}

        .chart-container canvas, .chart-container-sm canvas {{
            display: block;
            width: 100%;
            height: 100%;
        }}

        .macro-selector-bar {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-bottom: 12px;
        }}

        .macro-pill-btn {{
            background-color: var(--bg-input);
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .macro-pill-btn:hover {{
            border-color: var(--accent-blue);
            color: var(--text-primary);
        }}

        .macro-pill-btn.active {{
            background-color: var(--accent-blue);
            color: #ffffff;
            border-color: var(--accent-blue);
        }}

        .mini-inspect-btn {{
            background: none;
            border: 1px solid var(--border-color);
            color: var(--accent-blue);
            padding: 3px 10px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s ease;
        }}

        .mini-inspect-btn:hover {{
            background-color: var(--accent-blue);
            color: #ffffff;
            border-color: var(--accent-blue);
        }}

        .ind-chart-card {{
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        /* Search Input */
        .search-input {{
            background-color: var(--bg-input);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            outline: none;
        }}

        .search-input:focus {{
            border-color: var(--accent-blue);
        }}

        
        /* Educational Tooltip Styles */
        [data-tooltip] {{
            position: relative;
            cursor: help;
        }}

        .info-tip {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 15px;
            height: 15px;
            border-radius: 50%;
            background-color: var(--bg-input);
            border: 1px solid var(--border-color);
            color: var(--accent-blue);
            font-size: 10px;
            font-weight: 700;
            cursor: help;
            margin-left: 4px;
            vertical-align: middle;
            position: relative;
        }}

        .info-tip:hover {{
            background-color: var(--accent-blue);
            color: #ffffff;
            border-color: var(--accent-blue);
        }}

        [data-tooltip]::before {{
            content: attr(data-tooltip);
            position: absolute;
            bottom: calc(100% + 8px);
            left: 50%;
            transform: translateX(-50%) translateY(4px);
            background-color: #0b1120;
            color: #f8fafc;
            border: 1px solid #334155;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 11.5px;
            font-weight: 400;
            line-height: 1.4;
            letter-spacing: normal;
            text-transform: none;
            white-space: normal;
            width: max-content;
            max-width: 260px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
            pointer-events: none;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.2s ease, transform 0.2s ease;
            z-index: 999;
            text-align: left;
        }}

        [data-theme="light"] [data-tooltip]::before, html[data-theme="light"] [data-tooltip]::before, body[data-theme="light"] [data-tooltip]::before, .theme-light [data-tooltip]::before {{
            background-color: #ffffff;
            color: #0f172a;
            border-color: #cbd5e1;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        }}

        [data-tooltip]::after {{
            content: "";
            position: absolute;
            bottom: calc(100% + 2px);
            left: 50%;
            transform: translateX(-50%);
            border-width: 6px;
            border-style: solid;
            border-color: #334155 transparent transparent transparent;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.2s ease;
            z-index: 999;
            pointer-events: none;
        }}

        [data-theme="light"] [data-tooltip]::after, html[data-theme="light"] [data-tooltip]::after, body[data-theme="light"] [data-tooltip]::after, .theme-light [data-tooltip]::after {{
            border-color: #cbd5e1 transparent transparent transparent;
        }}

        [data-tooltip]:hover::before {{
            opacity: 1;
            visibility: visible;
            transform: translateX(-50%) translateY(0);
        }}

        [data-tooltip]:hover::after {{
            opacity: 1;
            visibility: visible;
        }}

        /* Tooltip position variants for edges */
        .tip-left[data-tooltip]::before {{
            left: 0;
            transform: translateX(0) translateY(4px);
        }}
        .tip-left[data-tooltip]::after {{
            left: 14px;
            transform: translateX(0);
        }}
        .tip-left[data-tooltip]:hover::before {{
            transform: translateX(0) translateY(0);
        }}

        .tip-right[data-tooltip]::before {{
            left: auto;
            right: 0;
            transform: translateX(0) translateY(4px);
        }}
        .tip-right[data-tooltip]::after {{
            left: auto;
            right: 14px;
            transform: translateX(0);
        }}
        .tip-right[data-tooltip]:hover::before {{
            transform: translateX(0) translateY(0);
        }}

        /* Footer */
        footer {{
            margin-top: 40px;
            text-align: center;
            font-size: 12px;
            color: var(--text-muted);
            padding: 20px;
            border-top: 1px solid var(--border-color);
        }}
    </style>
</head>
<body>

    <header>
        <div class="brand">
            <div>
                <div class="brand-title">Macro Flow Stock Navigator</div>
                <div class="brand-subtitle">Real-Time Cross-Asset Alignment & Options Decision Engine</div>
            </div>
        </div>
        <div class="header-actions">
            <div class="market-status-pill">
                <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background-color: var(--accent-green);"></span>
                <span>Session: {last_trade_date}</span>
            </div>
            <button id="themeToggleBtn" class="theme-toggle-btn" onclick="toggleTheme()">
                <span id="themeLabel">Light Mode</span>
            </button>
        </div>
    </header>

    <div class="container">

        <!-- Executive Banner -->
        <div class="executive-banner">
            <div class="ticker-profile">
                <div class="ticker-symbol font-mono">{ticker}</div>
                <div class="ticker-price font-mono">${price:.2f}</div>
                <div class="ticker-change {chg_class} font-mono">{chg_str}</div>
            </div>

            <div class="banner-metrics">
                <div class="metric-pill" data-tooltip="Overall directional posture (BUY, SELL, TRIM, ACCUMULATE, or NEUTRAL) synthesized from cross-asset macro tailwinds, moving average trends, and market regime context.">
                    <span class="label">Macro Signal <span class="info-tip">?</span></span>
                    <span class="val">
                        <span class="badge {'badge-signal-buy' if 'BUY' in action_badge else ('badge-signal-sell' if 'SELL' in action_badge else 'badge-signal-neutral')}">
                            {action_badge}
                        </span>
                    </span>
                </div>
                <div class="metric-pill" data-tooltip="The structural market classification for this equity (e.g. Mega-Cap Tech, High-Beta Growth, Cyclical, Defensive), determining which macro factors exert the strongest tailwinds or headwinds.">
                    <span class="label">Stock Archetype <span class="info-tip">?</span></span>
                    <span class="val">{archetype_name}</span>
                </div>
                <div class="metric-pill" data-tooltip="Quantifies net macro favorability on a scale of -100 to +100. Positive scores indicate macro tailwinds blowing in the stock's favor; negative scores denote macro headwinds.">
                    <span class="label">Macro Alignment <span class="info-tip">?</span></span>
                    <span class="val font-mono">{decision.get('alignment_score', 0.0):+.1f} / 100</span>
                </div>
                <div class="metric-pill" data-tooltip="The prevailing macro environment (e.g. Goldilocks Growth, Stagflationary Pressure, Flight to Safety, Reflation / Expansion) driven by yields, commodities, credit, and dollar trends.">
                    <span class="label">Macro Regime <span class="info-tip">?</span></span>
                    <span class="val">{macro_regime.get('name', 'Balanced Rotation')}</span>
                </div>
                <div class="metric-pill" data-tooltip="Implied Volatility (forward option pricing) minus 30-day Realized Volatility (actual historical movement). A positive spread means options are priced rich—ideal for selling calls and puts for premium.">
                    <span class="label">IV vs 30d RV <span class="info-tip">?</span></span>
                    <span class="val font-mono" style="color: {'var(--accent-green)' if opt_analytics.get('iv_rv_spread', 0) >= 0 else 'var(--accent-amber)'};">
                        {opt_analytics.get('iv_rv_spread', 0.0):+.1f}%
                    </span>
                </div>
            </div>
        </div>

        <!-- Navigation Tabs -->
        <div class="tab-bar">
            <button class="tab-btn active" onclick="switchTab('overview')">Executive Overview</button>
            <button class="tab-btn" onclick="switchTab('indicators')">8 Macro Indicators</button>
            <button class="tab-btn" onclick="switchTab('charts')">Trend & Factor Charts</button>
            <button class="tab-btn" onclick="switchTab('playbook')">Options Playbook & Simulator</button>
        </div>

        <!-- TAB 1: EXECUTIVE OVERVIEW -->
        <div id="tab-overview" class="tab-content active">
            <div class="grid-2">
                
                <!-- Archetype & Regime Alignment Card -->
                <div class="card">
                    <div class="card-header">
                        <div>
                            <div class="card-title">Archetype Alignment Matrix</div>
                            <div class="card-desc">{archetype_name}</div>
                        </div>
                    </div>
                    <p style="color: var(--text-secondary); margin-bottom: 16px; font-size: 13px;">
                        {archetype_desc}
                    </p>
                    <div style="background-color: var(--bg-input); padding: 14px; border-radius: 6px; margin-bottom: 16px;">
                        <div style="font-weight: 700; font-size: 12px; margin-bottom: 4px;">Macro Regime Context: {macro_regime.get('name', 'Balanced Rotation')}</div>
                        <div style="font-size: 12px; color: var(--text-secondary);">{macro_regime.get('summary', '')}</div>
                    </div>
                    <div class="tactical-grid">
                        <div class="tactical-cell" data-tooltip="50-day simple moving average: the medium-term price trend benchmark. Trading above indicates short-to-medium term bullish momentum.">
                            <div class="label">50-Day MA <span class="info-tip">?</span></div>
                            <div class="val font-mono">${ticker_info.get('ma50', 0.0):.2f} ({ticker_info.get('diff_ma50_pct', 0.0):+.2f}%)</div>
                        </div>
                        <div class="tactical-cell" data-tooltip="200-day simple moving average: the primary long-term institutional trend filter. Stocks above are in long-term uptrends.">
                            <div class="label">200-Day MA <span class="info-tip">?</span></div>
                            <div class="val font-mono">${ticker_info.get('ma200', 0.0):.2f} ({ticker_info.get('diff_ma200_pct', 0.0):+.2f}%)</div>
                        </div>
                        <div class="tactical-cell" data-tooltip="Measures sensitivity relative to the S&P 500. A beta of 1.5 means the stock moves ~1.5% for every 1.0% shift in the broad market.">
                            <div class="label">Beta (vs SPY) <span class="info-tip">?</span></div>
                            <div class="val font-mono">{ticker_info.get('beta', 1.0)}</div>
                        </div>
                        <div class="tactical-cell" data-tooltip="30-day annualized standard deviation of daily price returns. Reflects actual recent price turbulence.">
                            <div class="label">30d Realized Vol <span class="info-tip">?</span></div>
                            <div class="val font-mono">{ticker_info.get('historical_vol_30d', 0.0)}%</div>
                        </div>
                    </div>
                </div>

                <!-- Tailwinds vs Headwinds Card -->
                <div class="card">
                    <div class="card-header">
                        <div>
                            <div class="card-title">Macro Drivers & Sensitivity Forces</div>
                            <div class="card-desc">Active tailwinds and risk factors impacting {ticker}</div>
                        </div>
                    </div>

                    <div style="margin-bottom: 16px;">
                        <div style="font-size: 12px; font-weight: 700; color: var(--accent-green); text-transform: uppercase; margin-bottom: 8px;">
                            Active Macro Tailwinds
                        </div>
                        <div id="tailwindsList">
                            {''.join([f'<div class="force-item"><span class="force-tag" style="color: var(--accent-green);">{f["indicator"]}</span><span class="force-desc">{f["meaning"]} ({f["trend"]})</span></div>' for f in favorable]) if favorable else '<div style="color: var(--text-muted); font-size: 12px;">No dominant macro tailwinds detected.</div>'}
                        </div>
                    </div>

                    <div>
                        <div style="font-size: 12px; font-weight: 700; color: var(--accent-red); text-transform: uppercase; margin-bottom: 8px;">
                            Active Macro Headwinds
                        </div>
                        <div id="headwindsList">
                            {''.join([f'<div class="force-item"><span class="force-tag" style="color: var(--accent-red);">{h["indicator"]}</span><span class="force-desc">{h["meaning"]} ({h["trend"]})</span></div>' for h in hostile]) if hostile else '<div style="color: var(--text-muted); font-size: 12px;">No major macro headwinds detected.</div>'}
                        </div>
                    </div>
                </div>

            </div>

            <!-- Quick Options Playbook Summary -->
            <div class="playbook-hero">
                <div style="font-size: 12px; color: var(--accent-blue); font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">
                    Recommended Options Strategy
                </div>
                <div class="playbook-strategy-name">{tactical.get('strategy', 'Neutral Options Overlay')}</div>
                <div class="playbook-rationale">{tactical.get('rationale', '')}</div>
                <div class="tactical-grid">
                    <div class="tactical-cell" data-tooltip="Optimal strike price selected for options selling based on stock archetype, volatility skew, and support/resistance levels.">
                        <div class="label">Target Strike <span class="info-tip">?</span></div>
                        <div class="val font-mono">{tactical.get('optimal_strike', 'N/A')}</div>
                    </div>
                    <div class="tactical-cell" data-tooltip="Target delta range (e.g. 0.20Δ - 0.30Δ), providing high statistical win rates (70-80% probability of expiring worthless).">
                        <div class="label">Target Delta <span class="info-tip">?</span></div>
                        <div class="val font-mono">{tactical.get('recommended_delta', 'N/A')}</div>
                    </div>
                    <div class="tactical-cell" data-tooltip="Days To Expiration (DTE): 30 to 45 days is the 'sweet spot' where theta time decay accelerates most rapidly while maintaining healthy premium.">
                        <div class="label">Target DTE <span class="info-tip">?</span></div>
                        <div class="val font-mono">{tactical.get('target_dte', '30-45 DTE')}</div>
                    </div>
                    <div class="tactical-cell">
                        <div class="label">Est. Annualized Yield</div>
                        <div class="val font-mono">{tactical.get('estimated_annualized_yield', 'N/A')}</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 2: 8 MACRO INDICATORS -->
        <div id="tab-indicators" class="tab-content">
            <div class="filter-group">
                <button class="filter-btn active" onclick="filterIndicators('all', this)">All (8)</button>
                <button class="filter-btn" onclick="filterIndicators('trend-bullish', this)">Bullish Signals</button>
                <button class="filter-btn" onclick="filterIndicators('trend-bearish', this)">Bearish Signals</button>
                <button class="filter-btn" onclick="filterIndicators('trend-neutral', this)">Neutral Signals</button>
            </div>

            <div class="grid-4" id="indicatorsGrid">
                {ind_cards_rendered}
            </div>
        </div>

        <!-- TAB 3: TREND & FACTOR CHARTS -->
        <div id="tab-charts" class="tab-content">
            <!-- Row 1: Core Stock Trend & Macro Percentile Radar -->
            <div class="grid-2">
                <div class="card">
                    <div class="card-header">
                        <div>
                            <div class="card-title">{ticker} Price Trend & Moving Averages</div>
                            <div class="card-desc">Daily Close vs 50-MA & 200-MA (Data as of {last_trade_date} Close)</div>
                        </div>
                    </div>
                    <div class="chart-container">
                        <canvas id="priceChart"></canvas>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div>
                            <div class="card-title">Macro Indicators Percentile Radar</div>
                            <div class="card-desc">90-Day Cross-Asset Percentile Distribution (All 8 Factors)</div>
                        </div>
                    </div>
                    <div class="chart-container">
                        <canvas id="macroRadarChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Row 2: Interactive Focus Visualizer for Macro Indicators -->
            <div class="card" id="focusVisualizerCard" style="margin-bottom: 20px;">
                <div class="card-header">
                    <div>
                        <div class="card-title">Macro Indicator Detailed Focus Visualizer</div>
                        <div class="card-desc">Deep-dive dynamic ratio time-series, 50-day moving average, and trend trajectory</div>
                    </div>
                    <div id="focusBadge" class="badge {first_status_class}">{first_trend}</div>
                </div>
                
                <div class="macro-selector-bar" id="macroSelectorBar">
                    {macro_pill_buttons_rendered}
                </div>

                <div class="tactical-grid" style="margin: 12px 0 16px 0;">
                    <div class="tactical-cell">
                        <div class="label">Indicator Name</div>
                        <div id="focusIndName" class="val" style="font-size: 13px;">{first_name}</div>
                    </div>
                    <div class="tactical-cell">
                        <div class="label">Ratio Tickers</div>
                        <div id="focusIndRatio" class="val font-mono">{first_ratio}</div>
                    </div>
                    <div class="tactical-cell">
                        <div class="label">Current Ratio & 50-MA</div>
                        <div id="focusIndValue" class="val font-mono">{first_val_str}</div>
                    </div>
                    <div class="tactical-cell">
                        <div class="label">90-Day Percentile Rank</div>
                        <div id="focusIndPercentile" class="val font-mono">{first_pctl_str}</div>
                    </div>
                </div>

                <div class="chart-container" style="height: 300px;">
                    <canvas id="focusIndicatorChart"></canvas>
                </div>

                <div id="focusIndMeaning" style="margin-top: 14px; padding: 10px 14px; background-color: var(--bg-input); border-radius: 6px; font-size: 12px; color: var(--text-secondary);">
                    {first_meaning}
                </div>
            </div>

            <!-- Row 3: All 8 Macro Indicator Multi-Chart Grid -->
            <div style="margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="font-size: 16px; font-weight: 700; letter-spacing: -0.01em;">All 8 Macro Indicators Trend Matrix</h3>
                    <p style="font-size: 12px; color: var(--text-secondary);">Simultaneous multi-factor ratio & 50-MA visualizer for comprehensive market regime navigation</p>
                </div>
            </div>

            <div class="grid-4" id="indicatorChartsGrid">
                {ind_chart_cards_rendered}
            </div>
        </div>

        <!-- TAB 4: OPTIONS PLAYBOOK & SIMULATOR -->
        <div id="tab-playbook" class="tab-content">
            
            <!-- Strategy Recommendation Hero -->
            <div class="playbook-hero">
                <div style="font-size: 12px; color: var(--accent-blue); font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">
                    Strategic Options Specification
                </div>
                <div class="playbook-strategy-name">{tactical.get('strategy', 'Neutral Options Overlay')}</div>
                <div class="playbook-rationale">{tactical.get('rationale', '')}</div>
                
                <div class="tactical-grid" style="margin-top: 16px;">
                    <div class="tactical-cell" data-tooltip="Optimal strike price selected for options selling based on stock archetype, volatility skew, and support/resistance levels.">
                        <div class="label">Target Strike <span class="info-tip">?</span></div>
                        <div class="val font-mono">{tactical.get('optimal_strike', 'N/A')}</div>
                    </div>
                    <div class="tactical-cell" data-tooltip="Target delta range (e.g. 0.20Δ - 0.30Δ), providing high statistical win rates (70-80% probability of expiring worthless).">
                        <div class="label">Target Delta <span class="info-tip">?</span></div>
                        <div class="val font-mono">{tactical.get('recommended_delta', 'N/A')}</div>
                    </div>
                    <div class="tactical-cell" data-tooltip="Days To Expiration (DTE): 30 to 45 days is the 'sweet spot' where theta time decay accelerates most rapidly while maintaining healthy premium.">
                        <div class="label">Target DTE <span class="info-tip">?</span></div>
                        <div class="val font-mono">{tactical.get('target_dte', '30-45 DTE')}</div>
                    </div>
                    <div class="tactical-cell" data-tooltip="Estimated annualized return generated from recurring option premium harvesting.">
                        <div class="label">Target Return <span class="info-tip">?</span></div>
                        <div class="val font-mono">{tactical.get('estimated_annualized_yield', 'N/A')}</div>
                    </div>
                    <div class="tactical-cell" data-tooltip="Best practice rule: Buy back and close the short option once 50% to 75% of maximum profit is captured to free up capital and remove tail risk.">
                        <div class="label">Profit Target <span class="info-tip">?</span></div>
                        <div class="val font-mono">{tactical.get('profit_target', '50% of max')}</div>
                    </div>
                    <div class="tactical-cell" data-tooltip="Defensive exit rule to prevent catastrophic losses when price moves strongly against the position (e.g. close or roll if contract value reaches 2x initial credit).">
                        <div class="label">Stop Loss Rule <span class="info-tip">?</span></div>
                        <div class="val font-mono">{tactical.get('stop_loss_rule', '2x credit')}</div>
                    </div>
                </div>
            </div>

            <!-- Key Options Indicators Banner -->
            <div class="card" style="margin-bottom: 20px;">
                <div class="card-header">
                    <div>
                        <div class="card-title">Options Volatility & Market Indicator Signals</div>
                        <div class="card-desc">Real-time implied volatility pricing, skew, Put/Call ratios, and Max Pain strike</div>
                    </div>
                </div>
                <div class="grid-6">
                    <div class="tactical-cell" data-tooltip="ATM Implied Volatility (annualized volatility implied by option prices) vs 30-day Historical Volatility (realized stock swings).">
                        <div class="label">IV (ATM) vs 30d HV <span class="info-tip">?</span></div>
                        <div class="val font-mono">{opt_analytics.get('iv_atm', 0.0):.1f}% <span style="font-size: 11px; color: var(--text-secondary);">/ {opt_analytics.get('hv_30d', 0.0):.1f}%</span></div>
                    </div>
                    <div class="tactical-cell" data-tooltip="IV Rank measures where current IV sits between the 52-week high and low (0-100%). IV Percentile is the percentage of days in the past year IV was lower. High values (>50%) favor options selling.">
                        <div class="label">IV Rank / Percentile <span class="info-tip">?</span></div>
                        <div class="val font-mono">{opt_analytics.get('iv_rank', 0.0):.1f}% <span style="font-size: 11px; color: var(--text-secondary);">/ {opt_analytics.get('iv_percentile', 0.0):.1f}%</span></div>
                    </div>
                    <div class="tactical-cell" data-tooltip="The Volatility Risk Premium (VRP). When IV exceeds Realized Vol, options are statistically overpriced, offering an edge to sellers of Covered Calls and Cash-Secured Puts.">
                        <div class="label">IV - RV Spread <span class="info-tip">?</span></div>
                        <div class="val font-mono" style="color: {'var(--accent-green)' if opt_analytics.get('iv_rv_spread', 0) >= 0 else 'var(--accent-amber)'};">{opt_analytics.get('iv_rv_spread', 0.0):+.1f}%</div>
                    </div>
                    <div class="tactical-cell" data-tooltip="Ratio of traded Put volume to Call volume, and open Put contracts to Call contracts. Ratios > 1.0 indicate defensive hedging or bearish sentiment; < 0.7 reflects bullish call flow.">
                        <div class="label">Put/Call Ratio (Vol/OI) <span class="info-tip">?</span></div>
                        <div class="val font-mono">{opt_analytics.get('pcr_volume', 1.0):.2f} <span style="font-size: 11px; color: var(--text-secondary);">/ {opt_analytics.get('pcr_open_interest', 1.0):.2f}</span></div>
                    </div>
                    <div class="tactical-cell" data-tooltip="The strike price where option buyers lose the most money (and option sellers make the most) at expiration. Stock prices often gravitate toward Max Pain into expiration.">
                        <div class="label">Max Pain Strike <span class="info-tip">?</span></div>
                        <div class="val font-mono" style="color: var(--accent-cyan);">${opt_analytics.get('max_pain_strike', price):.2f}</div>
                    </div>
                    <div class="tactical-cell" data-tooltip="The 1-standard-deviation price range implied by options market pricing over the next 30 days (~68% statistical probability range).">
                        <div class="label">30d Expected Move (±1σ) <span class="info-tip">?</span></div>
                        <div class="val font-mono" style="font-size: 13px;">±${opt_analytics.get('expected_move_30d', 0.0):.2f} <span style="font-size: 11px; color: var(--text-secondary);">[${opt_analytics.get('expected_move_lower', 0.0):.2f}-${opt_analytics.get('expected_move_upper', 0.0):.2f}]</span></div>
                    </div>
                </div>
            </div>

            <!-- Dual Selling Screener Matrices (Covered Calls & Cash-Secured Puts) -->
            <div class="grid-2">
                
                <!-- Covered Call Screener Card -->
                <div class="card">
                    <div class="card-header">
                        <div>
                            <div class="card-title">Selling Covered Calls Screener</div>
                            <div class="card-desc">Generate income & downside cushion on long stock position (100 shares)</div>
                        </div>
                    </div>
                    <div class="table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th data-tooltip="Risk tier: Conservative (low probability of assignment), Balanced (optimal risk/reward), Aggressive (maximum premium income).">Tier <span class="info-tip">?</span></th>
                                    <th data-tooltip="The agreed price at which your shares will be sold if assigned.">Strike <span class="info-tip">?</span></th>
                                    <th data-tooltip="Midpoint of current Bid and Ask price for the option contract.">Mid <span class="info-tip">?</span></th>
                                    <th data-tooltip="Delta (Δ): Sensitivity of option price to a $1 move in the stock. Also approximates the probability of expiring In-The-Money (e.g. 0.30Δ ≈ 30% assignment risk).">Δ <span class="info-tip">?</span></th>
                                    <th data-tooltip="Theta (Θ): Daily time decay in dollars per share collected by the option seller as expiration approaches.">Θ <span class="info-tip">?</span></th>
                                    <th data-tooltip="Percentage distance from current stock price to the strike price (Out-of-The-Money buffer).">OTM % <span class="info-tip">?</span></th>
                                    <th data-tooltip="Annualized cash yield if the stock stays below the strike price and expires worthless (keeping 100% of shares and premium).">Yield Unassigned <span class="info-tip">?</span></th>
                                    <th data-tooltip="Total return (premium collected + stock capital gain up to strike) if the shares get called away at expiration.">Return Called <span class="info-tip">?</span></th>
                                    <th data-tooltip="Downside cushion: the percentage drop the stock can suffer before you incur a net loss on the position (protected by the collected premium).">Cushion <span class="info-tip">?</span></th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {cc_rows_rendered}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Cash-Secured Put Screener Card -->
                <div class="card">
                    <div class="card-header">
                        <div>
                            <div class="card-title">Selling Cash-Secured Puts Screener</div>
                            <div class="card-desc">Acquire shares at a guaranteed discount or collect cash yield</div>
                        </div>
                    </div>
                    <div class="table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th data-tooltip="Risk tier: Conservative (~0.20Δ, low assignment probability), Balanced (~0.30Δ), Aggressive (~0.40Δ, highest premium).">Tier <span class="info-tip">?</span></th>
                                    <th data-tooltip="The strike price at which you are obligated to buy 100 shares if assigned.">Strike <span class="info-tip">?</span></th>
                                    <th data-tooltip="Option premium collected per share (multiply by 100 for total cash received per contract).">Mid <span class="info-tip">?</span></th>
                                    <th data-tooltip="Delta (Δ): Probability of put expiring ITM and resulting in stock purchase at the strike.">Δ <span class="info-tip">?</span></th>
                                    <th data-tooltip="Theta (Θ): Daily time decay earned by the put seller each day the stock stays above strike.">Θ <span class="info-tip">?</span></th>
                                    <th data-tooltip="Percentage discount of the strike price below current market price.">OTM % <span class="info-tip">?</span></th>
                                    <th data-tooltip="Cash required to hold in your account to guarantee purchasing 100 shares at the strike (Strike x 100).">Collateral <span class="info-tip">?</span></th>
                                    <th data-tooltip="Effective purchase price per share if assigned (Strike Price minus Premium Received).">Net Basis <span class="info-tip">?</span></th>
                                    <th data-tooltip="Net percentage discount compared to current spot market price if assigned shares.">Discount <span class="info-tip">?</span></th>
                                    <th data-tooltip="Annualized Return on Capital (ROC) earned on the cash collateral held if the put expires unassigned.">Ann. ROC <span class="info-tip">?</span></th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {csp_rows_rendered}
                            </tbody>
                        </table>
                    </div>
                </div>

            </div>

            <!-- Unusual Option Activity (UOA) & Flow Detection -->
            <div class="card" style="margin-bottom: 20px;">
                <div class="card-header">
                    <div>
                        <div class="card-title">Unusual Option Activity (UOA) & Institutional Flow Tracker</div>
                        <div class="card-desc">Detects anomalous block trades, multi-contract sweeps (Volume &gt; 1.5x Open Interest), and directional positioning</div>
                    </div>
                </div>
                <div class="table-wrap">
                    <table id="uoaTable">
                        <thead>
                            <tr>
                                <th data-tooltip="Option contract type: Call (bullish right to buy) or Put (bearish right to sell / hedge).">Type <span class="info-tip">?</span></th>
                                <th>Contract</th>
                                <th>Strike</th>
                                <th data-tooltip="Number of option contracts traded during the current session.">Volume <span class="info-tip">?</span></th>
                                <th data-tooltip="Total number of outstanding, active option contracts held by market participants overnight.">Open Int <span class="info-tip">?</span></th>
                                <th data-tooltip="Volume to Open Interest Ratio. Ratios above 1.5x indicate new institutional opening positioning rather than closing existing trades.">Vol / OI <span class="info-tip">?</span></th>
                                <th data-tooltip="Estimated total institutional capital spent on this contract during the session (Volume x Mid x 100).">Est. Dollar Flow <span class="info-tip">?</span></th>
                                <th data-tooltip="Analytical interpretation of aggressive block buy sweeps vs defensive hedging flow.">Institutional Flow Sentiment <span class="info-tip">?</span></th>
                            </tr>
                        </thead>
                        <tbody>
                            {uoa_rows_rendered}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Live Real-Time Option Chain Explorer Table -->
            <div class="card" style="margin-bottom: 20px;">
                <div class="card-header">
                    <div>
                        <div class="card-title">Live Real-Time Option Chain Explorer</div>
                        <div class="card-desc">Target Expiration: <span class="font-mono" style="color: var(--accent-blue); font-weight: 700;">{opt_chain.get('expiration', 'Near-Month')} ({opt_chain.get('dte', 30)} DTE)</span> &bull; Spot Price: <span class="font-mono">${price:.2f}</span></div>
                    </div>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 14px;">
                    <div class="filter-group" style="margin-bottom: 0;">
                        <button class="filter-btn active" onclick="filterOptionChain('all', this)">All Options</button>
                        <button class="filter-btn" onclick="filterOptionChain('calls', this)">Calls Only</button>
                        <button class="filter-btn" onclick="filterOptionChain('puts', this)">Puts Only</button>
                        <button class="filter-btn" onclick="filterOptionChain('ntm', this)">Near Money (±10%)</button>
                    </div>
                    <div>
                        <input type="text" id="chainSearchInput" class="search-input" placeholder="Search strike or type..." oninput="searchOptionChain()">
                    </div>
                </div>

                <div class="table-wrap" style="max-height: 380px; overflow-y: auto;">
                    <table id="optionsChainTable">
                        <thead style="position: sticky; top: 0; z-index: 10;">
                            <tr>
                                <th data-tooltip="Call option (right to buy) or Put option (right to sell).">Type <span class="info-tip">?</span></th>
                                <th data-tooltip="Contract exercise strike price.">Strike <span class="info-tip">?</span></th>
                                <th data-tooltip="Highest price buyers are willing to pay for this contract.">Bid <span class="info-tip">?</span></th>
                                <th data-tooltip="Lowest price sellers are willing to accept for this contract.">Ask <span class="info-tip">?</span></th>
                                <th data-tooltip="Fair value midpoint between Bid and Ask.">Mid <span class="info-tip">?</span></th>
                                <th data-tooltip="Delta (Δ): Price sensitivity and rough probability of finishing In-The-Money.">Delta (Δ) <span class="info-tip">?</span></th>
                                <th data-tooltip="Theta (Θ): Dollar amount this option loses per day due to time decay.">Theta (Θ) <span class="info-tip">?</span></th>
                                <th data-tooltip="Total contracts traded today.">Volume <span class="info-tip">?</span></th>
                                <th data-tooltip="Total active open contracts.">Open Int <span class="info-tip">?</span></th>
                                <th data-tooltip="Volume-to-Open Interest ratio (elevated indicates aggressive institutional activity).">Vol / OI <span class="info-tip">?</span></th>
                                <th data-tooltip="Implied Volatility priced into this specific strike.">IV % <span class="info-tip">?</span></th>
                                <th data-tooltip="ITM (In The Money) has intrinsic value; OTM (Out of The Money) consists purely of time value.">Status <span class="info-tip">?</span></th>
                                <th data-tooltip="Click to immediately load this strike and premium into the interactive Payoff Simulator below.">Simulate</th>
                            </tr>
                        </thead>
                        <tbody id="chainTableBody">
                            {chain_rows_rendered}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Interactive Dual Strategy Payoff Simulator -->
            <div class="card">
                <div class="card-header">
                    <div>
                        <div class="card-title">Interactive Options Payoff Simulator</div>
                        <div class="card-desc">Model trade P&L at expiration across dynamic price shifts for Covered Calls vs Cash-Secured Puts</div>
                    </div>
                </div>

                <!-- Strategy Toggle Buttons -->
                <div class="strategy-mode-bar">
                    <button id="modeBtnCC" class="strategy-mode-btn active" onclick="setSimulatorStrategy('CC')">
                        Covered Call (Long 100 Shares + Short Call)
                    </button>
                    <button id="modeBtnCSP" class="strategy-mode-btn" onclick="setSimulatorStrategy('CSP')">
                        Cash-Secured Put (Short Put + Cash Collateral)
                    </button>
                </div>

                <!-- Parameter Controls -->
                <div class="grid-3" style="margin-bottom: 16px;">
                    <div>
                        <label style="font-size: 11px; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">Stock Cost / Spot Price ($):</label>
                        <input type="number" id="simStockPriceInput" class="search-input" style="width: 100%; margin-top: 4px; font-family: ui-monospace, monospace; font-size: 14px;" value="{price:.2f}" step="0.5" onchange="updateSimPayoff()">
                    </div>
                    <div>
                        <label style="font-size: 11px; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">Short Strike Price ($):</label>
                        <input type="number" id="simStrikeInput" class="search-input" style="width: 100%; margin-top: 4px; font-family: ui-monospace, monospace; font-size: 14px;" value="{init_strike:.2f}" step="0.5" onchange="updateSimPayoff()">
                    </div>
                    <div>
                        <label style="font-size: 11px; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">Option Premium Received ($):</label>
                        <input type="number" id="simPremiumInput" class="search-input" style="width: 100%; margin-top: 4px; font-family: ui-monospace, monospace; font-size: 14px;" value="{init_premium:.2f}" step="0.05" onchange="updateSimPayoff()">
                    </div>
                </div>

                <div class="slider-control">
                    <label for="priceSlider" style="font-weight: 600; min-width: 140px;">Simulated Price:</label>
                    <input type="range" id="priceSlider" min="{max(1.0, round(price * 0.7, 1))}" max="{round(price * 1.3, 1)}" step="0.5" value="{round(price, 1)}" oninput="updateSimPayoff()">
                    <span id="sliderPriceDisplay" class="font-mono" style="font-size: 16px; font-weight: 700; min-width: 80px;">${price:.2f}</span>
                </div>

                <div class="tactical-grid" style="margin-bottom: 20px;">
                    <div class="tactical-cell">
                        <div class="label">Simulated Price Move</div>
                        <div id="simPriceMove" class="val font-mono">0.0%</div>
                    </div>
                    <div class="tactical-cell">
                        <div class="label">Simulated Net P&L</div>
                        <div id="simDollarPnL" class="val font-mono" style="color: var(--accent-green);">$0.00</div>
                    </div>
                    <div class="tactical-cell" data-tooltip="Percentage return earned on the capital committed (Stock cost for Covered Calls; Cash collateral for Cash-Secured Puts).">
                        <div class="label">Return on Capital (ROC) <span class="info-tip">?</span></div>
                        <div id="simROCPct" class="val font-mono" style="color: var(--accent-green);">0.0%</div>
                    </div>
                    <div class="tactical-cell" data-tooltip="The underlying stock price where your net profit equals exactly $0.00 at expiration. Below this price (for long stock/puts), you enter net loss territory.">
                        <div class="label">Breakeven Price <span class="info-tip">?</span></div>
                        <div id="simBreakeven" class="val font-mono">${price * 0.95:.2f}</div>
                    </div>
                    <div class="tactical-cell">
                        <div class="label">Position Status</div>
                        <div id="simPnLStatus" class="val font-mono" style="font-size: 13px; color: var(--accent-green);">Max Profit Zone</div>
                    </div>
                </div>

                <div class="chart-container">
                    <canvas id="payoffChart"></canvas>
                </div>
            </div>

            <!-- Risk Warnings -->
            <div class="card" style="margin-top: 20px;">
                <div class="card-header">
                    <div class="card-title">Risk Considerations & Trade Management Rules</div>
                </div>
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    <div style="font-size: 13px; color: var(--text-secondary);">&bull; <b>Delta Assignment Management:</b> If option delta expands past ±0.70, consider rolling out in time to the next monthly cycle for additional credit.</div>
                    <div style="font-size: 13px; color: var(--text-secondary);">&bull; <b>Profit Capture Discipline:</b> Close short positions when 50% to 75% of max credit is captured to eliminate tail risk.</div>
                    {''.join([f'<div style="font-size: 13px; color: var(--text-secondary);">&bull; {w}</div>' for w in warnings])}
                </div>
            </div>
        </div>

    </div>

    <footer>
        Macro Flow Stock Navigator &bull; Real-Time Public Cross-Asset Market Data Feeds & Options Analytics
    </footer>

    <script>
        // Global Datasets
        const CURRENT_PRICE = {price};
        const TICKER_INFO = {ticker_json};
        const INDICATORS_DATA = {indicators_json};
        const HISTORY_DATA = {history_json};
        const DECISION_DATA = {decision_json};
        const PLAYBOOK_DATA = {playbook_json};
        
        let currentTheme = (function() {{
            try {{
                return localStorage.getItem("mf_theme") || "dark";
            }} catch(e) {{
                return "dark";
            }}
        }})();
        let priceChartInstance = null;
        let radarChartInstance = null;
        let focusIndicatorChartInstance = null;
        const indicatorChartInstances = {{}};
        let payoffChartInstance = null;
        let currentFocusKey = "{first_ind_key}";
        let currentSimStrategy = "CC"; // 'CC' or 'CSP'

        // Check if Chart.js is loaded from external CDN
        const hasChartJs = typeof Chart !== "undefined";

        // Native High-DPI Canvas Helper
        function setupCanvasContext(canvas) {{
            if (!canvas) return null;
            const dpr = window.devicePixelRatio || 1;
            const rect = canvas.getBoundingClientRect();
            const width = rect.width || canvas.parentElement.clientWidth || 300;
            const height = rect.height || canvas.parentElement.clientHeight || 150;
            
            canvas.width = Math.floor(width * dpr);
            canvas.height = Math.floor(height * dpr);
            
            const ctx = canvas.getContext("2d");
            ctx.resetTransform && ctx.resetTransform();
            ctx.scale(dpr, dpr);
            return {{ ctx, width, height }};
        }}

        // Native Canvas Chart Renderers (Zero-Dependency Engine)
        function drawNativeLineChart(canvasId, datasets, xLabels, options = {{}}) {{
            const canvas = document.getElementById(canvasId);
            const setup = setupCanvasContext(canvas);
            if (!setup) return;
            const {{ ctx, width, height }} = setup;
            const isDark = currentTheme === "dark";
            
            const padLeft = options.padLeft !== undefined ? options.padLeft : 45;
            const padRight = options.padRight !== undefined ? options.padRight : 15;
            const padTop = options.padTop !== undefined ? options.padTop : 20;
            const padBottom = options.padBottom !== undefined ? options.padBottom : 25;
            const plotW = width - padLeft - padRight;
            const plotH = height - padTop - padBottom;
            
            if (plotW <= 10 || plotH <= 10) return;

            // Compute global min & max
            let minVal = Infinity;
            let maxVal = -Infinity;
            datasets.forEach(ds => {{
                (ds.data || []).forEach(v => {{
                    if (v !== null && !isNaN(v)) {{
                        if (v < minVal) minVal = v;
                        if (v > maxVal) maxVal = v;
                    }}
                }});
            }});
            if (minVal === Infinity) {{ minVal = 0; maxVal = 100; }}
            const valSpan = maxVal - minVal || 1;
            minVal = minVal - valSpan * 0.05;
            maxVal = maxVal + valSpan * 0.05;
            const range = maxVal - minVal || 1;

            const gridColor = isDark ? "rgba(36, 48, 70, 0.6)" : "rgba(203, 213, 225, 0.6)";
            const textColor = isDark ? "#94a3b8" : "#64748b";

            // Grid lines & Y Ticks
            const yTicks = options.yTicks || 4;
            ctx.font = "10px ui-monospace, monospace";
            ctx.textAlign = "right";
            ctx.textBaseline = "middle";

            for (let i = 0; i <= yTicks; i++) {{
                const y = padTop + (plotH / yTicks) * i;
                const v = maxVal - (range / yTicks) * i;
                
                ctx.strokeStyle = gridColor;
                ctx.lineWidth = 1;
                ctx.setLineDash(options.gridDash || [2, 2]);
                ctx.beginPath();
                ctx.moveTo(padLeft, y);
                ctx.lineTo(padLeft + plotW, y);
                ctx.stroke();
                ctx.setLineDash([]);

                ctx.fillStyle = textColor;
                const fmtVal = Math.abs(v) < 10 ? v.toFixed(3) : v.toFixed(1);
                ctx.fillText(options.yPrefix ? options.yPrefix + fmtVal : fmtVal, padLeft - 6, y);
            }}

            // Draw Datasets
            datasets.forEach(ds => {{
                const pts = ds.data || [];
                if (pts.length < 2) return;
                const stepX = plotW / (pts.length - 1);

                // Area gradient fill
                if (ds.fill && ds.fillColor) {{
                    const grad = ctx.createLinearGradient(0, padTop, 0, padTop + plotH);
                    grad.addColorStop(0, ds.fillColor);
                    grad.addColorStop(1, "rgba(0, 0, 0, 0)");
                    ctx.fillStyle = grad;
                    ctx.beginPath();
                    ctx.moveTo(padLeft, padTop + plotH);
                    pts.forEach((p, idx) => {{
                        const px = padLeft + idx * stepX;
                        const py = padTop + plotH - ((p - minVal) / range) * plotH;
                        ctx.lineTo(px, py);
                    }});
                    ctx.lineTo(padLeft + plotW, padTop + plotH);
                    ctx.closePath();
                    ctx.fill();
                }}

                // Line Stroke
                ctx.strokeStyle = ds.color || "#3b82f6";
                ctx.lineWidth = ds.lineWidth || 2;
                if (ds.dash) ctx.setLineDash(ds.dash);
                else ctx.setLineDash([]);
                
                ctx.beginPath();
                pts.forEach((p, idx) => {{
                    const px = padLeft + idx * stepX;
                    const py = padTop + plotH - ((p - minVal) / range) * plotH;
                    if (idx === 0) ctx.moveTo(px, py);
                    else ctx.lineTo(px, py);
                }});
                ctx.stroke();
                ctx.setLineDash([]);
            }});

            // X-Axis Labels
            if (xLabels && xLabels.length > 0) {{
                ctx.fillStyle = textColor;
                ctx.textAlign = "center";
                ctx.textBaseline = "top";
                const numLabels = Math.min(5, xLabels.length);
                for (let i = 0; i < numLabels; i++) {{
                    const idx = Math.floor((i / (numLabels - 1)) * (xLabels.length - 1));
                    const px = padLeft + (idx / (xLabels.length - 1)) * plotW;
                    const lbl = xLabels[idx] || "";
                    ctx.fillText(lbl.length > 7 ? lbl.slice(5) : lbl, px, padTop + plotH + 6);
                }}
            }}
        }}

        function drawNativeRadarChart(canvasId, indicators) {{
            const canvas = document.getElementById(canvasId);
            const setup = setupCanvasContext(canvas);
            if (!setup) return;
            const {{ ctx, width, height }} = setup;
            const isDark = currentTheme === "dark";

            const cx = width / 2;
            const cy = height / 2;
            const radius = Math.min(cx, cy) - 36;
            if (radius <= 10) return;

            const gridColor = isDark ? "rgba(36, 48, 70, 0.8)" : "rgba(203, 213, 225, 0.8)";
            const textColor = isDark ? "#cbd5e1" : "#475569";
            const keys = Object.keys(indicators);
            const numPoints = keys.length || 8;
            const angleStep = (Math.PI * 2) / numPoints;

            // Concentric Polygon Rings
            const rings = 4;
            for (let r = 1; r <= rings; r++) {{
                const ringRadius = (radius / rings) * r;
                ctx.strokeStyle = gridColor;
                ctx.lineWidth = 1;
                ctx.beginPath();
                for (let i = 0; i < numPoints; i++) {{
                    const a = i * angleStep - Math.PI / 2;
                    const x = cx + Math.cos(a) * ringRadius;
                    const y = cy + Math.sin(a) * ringRadius;
                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                }}
                ctx.closePath();
                ctx.stroke();
            }}

            // Spokes & Text Labels
            ctx.font = "11px -apple-system, sans-serif";
            keys.forEach((k, i) => {{
                const ind = indicators[k];
                const label = ind.ratio_tickers || ind.display_name || k;
                const a = i * angleStep - Math.PI / 2;
                
                // Spoke
                ctx.strokeStyle = gridColor;
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(cx, cy);
                ctx.lineTo(cx + Math.cos(a) * radius, cy + Math.sin(a) * radius);
                ctx.stroke();

                // Label
                const lx = cx + Math.cos(a) * (radius + 18);
                const ly = cy + Math.sin(a) * (radius + 18);
                ctx.fillStyle = textColor;
                ctx.textAlign = Math.abs(Math.cos(a)) < 0.2 ? "center" : (Math.cos(a) > 0 ? "left" : "right");
                ctx.textBaseline = "middle";
                ctx.fillText(label, lx, ly);
            }});

            // Data Polygon Fill
            const dataCoords = [];
            keys.forEach((k, i) => {{
                const ind = indicators[k];
                const pctl = Math.max(0, Math.min(100, ind.percentile_90d || 50));
                const dRadius = (radius * pctl) / 100;
                const a = i * angleStep - Math.PI / 2;
                dataCoords.push({{
                    x: cx + Math.cos(a) * dRadius,
                    y: cy + Math.sin(a) * dRadius
                }});
            }});

            if (dataCoords.length > 2) {{
                ctx.fillStyle = "rgba(6, 182, 212, 0.25)";
                ctx.strokeStyle = "#06b6d4";
                ctx.lineWidth = 2;
                ctx.beginPath();
                dataCoords.forEach((pt, i) => {{
                    if (i === 0) ctx.moveTo(pt.x, pt.y);
                    else ctx.lineTo(pt.x, pt.y);
                }});
                ctx.closePath();
                ctx.fill();
                ctx.stroke();

                // Dots
                ctx.fillStyle = "#ffffff";
                dataCoords.forEach(pt => {{
                    ctx.beginPath();
                    ctx.arc(pt.x, pt.y, 3, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.stroke();
                }});
            }}
        }}

        // Theme Toggle
        function applyTheme(theme) {{
            currentTheme = theme;
            document.documentElement.setAttribute("data-theme", theme);
            const lbl = document.getElementById("themeLabel");
            if (lbl) lbl.innerText = theme === "dark" ? "Light Mode" : "Dark Mode";
            localStorage.setItem("mf_theme", theme);
            
            if (hasChartJs) {{
                updateChartTheme();
            }} else {{
                renderAllNativeCharts();
            }}
        }}

        function toggleTheme() {{
            applyTheme(currentTheme === "dark" ? "light" : "dark");
        }}

        // Tab Switching
        function switchTab(tabId) {{
            document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach(content => content.classList.remove("active"));
            
            const activeBtn = Array.from(document.querySelectorAll(".tab-btn")).find(btn => {{
                const onclick = btn.getAttribute("onclick") || "";
                return onclick.includes(`'${{tabId}}'`) || onclick.includes(`"${{tabId}}"`);
            }});
            if (activeBtn) activeBtn.classList.add("active");
            
            const activeContent = document.getElementById("tab-" + tabId);
            if (activeContent) activeContent.classList.add("active");

            // Allow layout reflow before rendering / resizing charts
            requestAnimationFrame(() => {{
                setTimeout(() => {{
                    if (tabId === "charts") {{
                        initCharts();
                    }} else if (tabId === "playbook") {{
                        initPayoffChart();
                    }}
                }}, 40);
            }});
        }}

        // Indicator Card Filtering (Tab 2)
        function filterIndicators(filterType, btn) {{
            document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            document.querySelectorAll(".ind-card").forEach(card => {{
                if (filterType === "all" || card.getAttribute("data-trend") === filterType) {{
                    card.style.display = "flex";
                }} else {{
                    card.style.display = "none";
                }}
            }});
        }}

        // Macro Indicator Focus Visualizer (Tab 3)
        function selectFocusIndicator(key) {{
            if (!INDICATORS_DATA[key]) return;
            currentFocusKey = key;
            const ind = INDICATORS_DATA[key];
            
            // Update button states
            document.querySelectorAll(".macro-pill-btn").forEach(btn => {{
                if (btn.getAttribute("data-key") === key) {{
                    btn.classList.add("active");
                }} else {{
                    btn.classList.remove("active");
                }}
            }});

            // Update stats displays
            const nameEl = document.getElementById("focusIndName");
            if (nameEl) nameEl.innerText = ind.display_name;
            const ratioEl = document.getElementById("focusIndRatio");
            if (ratioEl) ratioEl.innerText = ind.ratio_tickers;
            const valEl = document.getElementById("focusIndValue");
            if (valEl) valEl.innerText = `${{ind.current_value}} (${{ind.ma50_status}})`;
            const pctlEl = document.getElementById("focusIndPercentile");
            if (pctlEl) pctlEl.innerText = `${{ind.percentile_90d}}% (${{ind.trend_signal}})`;
            const meaningEl = document.getElementById("focusIndMeaning");
            if (meaningEl) meaningEl.innerText = `${{ind.display_name}} (${{ind.ratio_tickers}}): ${{ind.market_meaning}}`;
            
            const badgeEl = document.getElementById("focusBadge");
            if (badgeEl) {{
                badgeEl.innerText = ind.trend_signal;
                const statusClass = ind.ma50_status.includes("Above") || ind.trend_signal.includes("Rising") ? "trend-bullish" : (ind.ma50_status.includes("Below") || ind.trend_signal.includes("Falling") ? "trend-bearish" : "trend-neutral");
                badgeEl.className = "badge " + statusClass;
            }}

            renderFocusChart(key);
        }}

        function renderFocusChart(key) {{
            const ind = INDICATORS_DATA[key];
            if (!ind) return;

            const dates = (ind.history_dates && ind.history_dates.length > 0) ? ind.history_dates : (HISTORY_DATA.dates || Array.from({{length: (ind.history || []).length}}, (_, i) => `D-${{ind.history.length - i}}`));
            const values = ind.history || [];
            const ma50 = ind.history_ma50 || [];

            const isBullish = ind.ma50_status.includes("Above") || ind.trend_signal.includes("Rising");
            const isBearish = ind.ma50_status.includes("Below") || ind.trend_signal.includes("Falling");
            const lineColor = isBullish ? "#10b981" : (isBearish ? "#ef4444" : "#06b6d4");
            const fillColor = isBullish ? "rgba(16, 185, 129, 0.12)" : (isBearish ? "rgba(239, 68, 68, 0.12)" : "rgba(6, 182, 212, 0.12)");

            if (hasChartJs) {{
                try {{
                    const isDark = currentTheme === "dark";
                    const textColor = isDark ? "#94a3b8" : "#475569";
                    const gridColor = isDark ? "#243046" : "#e2e8f0";

                    const canvas = document.getElementById("focusIndicatorChart");
                    if (!canvas) return;
                    const ctx = canvas.getContext("2d");

                    if (focusIndicatorChartInstance) {{
                        focusIndicatorChartInstance.destroy();
                        focusIndicatorChartInstance = null;
                    }}

                    focusIndicatorChartInstance = new Chart(ctx, {{
                        type: "line",
                        data: {{
                            labels: dates,
                            datasets: [
                                {{
                                    label: `${{ind.display_name}} (${{ind.ratio_tickers}})`,
                                    data: values,
                                    borderColor: lineColor,
                                    backgroundColor: fillColor,
                                    borderWidth: 2,
                                    fill: true,
                                    tension: 0.15
                                }},
                                {{
                                    label: "50-Day MA",
                                    data: ma50.length > 0 ? ma50 : Array(values.length).fill(ind.ma50),
                                    borderColor: "#f59e0b",
                                    borderWidth: 1.5,
                                    borderDash: [4, 4],
                                    fill: false,
                                    pointRadius: 0
                                }}
                            ]
                        }},
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false,
                            interaction: {{ mode: "index", intersect: false }},
                            scales: {{
                                x: {{ grid: {{ color: gridColor }}, ticks: {{ color: textColor, maxTicksLimit: 8 }} }},
                                y: {{ grid: {{ color: gridColor }}, ticks: {{ color: textColor }} }}
                            }},
                            plugins: {{
                                legend: {{ labels: {{ color: textColor }} }}
                            }}
                        }}
                    }});
                    return;
                }} catch (e) {{
                    console.warn("Chart.js failed, falling back to native canvas:", e);
                }}
            }}

            // Native Canvas Fallback
            drawNativeLineChart("focusIndicatorChart", [
                {{ data: values, color: lineColor, fillColor: fillColor, fill: true, lineWidth: 2.5 }},
                {{ data: ma50, color: "#f59e0b", dash: [4, 4], lineWidth: 1.5 }}
            ], dates, {{ padLeft: 55, yTicks: 4 }});
        }}

        // Initialize All Trend & Factor Charts (Tab 3)
        function initCharts() {{
            if (hasChartJs) {{
                try {{
                    initChartJsTrendCharts();
                    return;
                }} catch (e) {{
                    console.warn("Chart.js initialization failed, utilizing native canvas engine:", e);
                }}
            }}
            renderAllNativeCharts();
        }}

        function renderAllNativeCharts() {{
            // 1. Target Stock Price Chart
            if (HISTORY_DATA.prices && HISTORY_DATA.prices.length > 0) {{
                drawNativeLineChart("priceChart", [
                    {{ data: HISTORY_DATA.prices, color: "#3b82f6", fillColor: "rgba(59, 130, 246, 0.15)", fill: true, lineWidth: 2 }},
                    {{ data: HISTORY_DATA.ma50, color: "#10b981", lineWidth: 1.5 }},
                    {{ data: HISTORY_DATA.ma200, color: "#f59e0b", dash: [4, 4], lineWidth: 1.5 }}
                ], HISTORY_DATA.dates, {{ padLeft: 55, yPrefix: "$", yTicks: 5 }});
            }}

            // 2. Macro Radar Chart
            drawNativeRadarChart("macroRadarChart", INDICATORS_DATA);

            // 3. Focus Indicator Chart
            renderFocusChart(currentFocusKey);

            // 4. Mini Matrix Sparkline Charts
            for (const key in INDICATORS_DATA) {{
                const ind = INDICATORS_DATA[key];
                const isBullish = ind.ma50_status.includes("Above") || ind.trend_signal.includes("Rising");
                const isBearish = ind.ma50_status.includes("Below") || ind.trend_signal.includes("Falling");
                const lineColor = isBullish ? "#10b981" : (isBearish ? "#ef4444" : "#06b6d4");
                const fillColor = isBullish ? "rgba(16, 185, 129, 0.1)" : (isBearish ? "rgba(239, 68, 68, 0.1)" : "rgba(6, 182, 212, 0.1)");
                
                drawNativeLineChart(`chart_${{key}}`, [
                    {{ data: ind.history || [], color: lineColor, fillColor: fillColor, fill: true, lineWidth: 1.5 }},
                    {{ data: ind.history_ma50 || [], color: "#f59e0b", dash: [3, 3], lineWidth: 1 }}
                ], [], {{ padLeft: 38, padRight: 10, padTop: 10, padBottom: 10, yTicks: 3 }});
            }}
        }}

        function initChartJsTrendCharts() {{
            const isDark = currentTheme === "dark";
            const textColor = isDark ? "#94a3b8" : "#475569";
            const gridColor = isDark ? "#243046" : "#e2e8f0";

            // 1. Target Stock Price Chart
            if (HISTORY_DATA.dates && HISTORY_DATA.dates.length > 0) {{
                const canvasPrice = document.getElementById("priceChart");
                if (canvasPrice) {{
                    if (!priceChartInstance) {{
                        const ctxPrice = canvasPrice.getContext("2d");
                        priceChartInstance = new Chart(ctxPrice, {{
                            type: "line",
                            data: {{
                                labels: HISTORY_DATA.dates,
                                datasets: [
                                    {{
                                        label: `${{TICKER_INFO.ticker || "Stock"}} Close Price`,
                                        data: HISTORY_DATA.prices,
                                        borderColor: "#3b82f6",
                                        backgroundColor: "rgba(59, 130, 246, 0.08)",
                                        borderWidth: 2,
                                        fill: true,
                                        tension: 0.1
                                    }},
                                    {{
                                        label: "50-Day MA",
                                        data: HISTORY_DATA.ma50,
                                        borderColor: "#10b981",
                                        borderWidth: 1.5,
                                        borderDash: [4, 4],
                                        fill: false
                                    }},
                                    {{
                                        label: "200-Day MA",
                                        data: HISTORY_DATA.ma200,
                                        borderColor: "#f59e0b",
                                        borderWidth: 1.5,
                                        borderDash: [6, 6],
                                        fill: false
                                    }}
                                ]
                            }},
                            options: {{
                                responsive: true,
                                maintainAspectRatio: false,
                                interaction: {{ mode: "index", intersect: false }},
                                scales: {{
                                    x: {{ grid: {{ color: gridColor }}, ticks: {{ color: textColor, maxTicksLimit: 8 }} }},
                                    y: {{ grid: {{ color: gridColor }}, ticks: {{ color: textColor }} }}
                                }},
                                plugins: {{
                                    legend: {{ labels: {{ color: textColor }} }}
                                }}
                            }}
                        }});
                    }} else {{
                        priceChartInstance.resize();
                        priceChartInstance.update();
                    }}
                }}
            }}

            // 2. Macro Radar Chart
            const canvasRadar = document.getElementById("macroRadarChart");
            if (canvasRadar) {{
                if (!radarChartInstance) {{
                    const ctxRadar = canvasRadar.getContext("2d");
                    const labels = [];
                    const percentiles = [];
                    for (const k in INDICATORS_DATA) {{
                        labels.push(INDICATORS_DATA[k].ratio_tickers || INDICATORS_DATA[k].display_name);
                        percentiles.push(INDICATORS_DATA[k].percentile_90d || 50.0);
                    }}

                    radarChartInstance = new Chart(ctxRadar, {{
                        type: "radar",
                        data: {{
                            labels: labels,
                            datasets: [{{
                                label: "90-Day Percentile",
                                data: percentiles,
                                backgroundColor: "rgba(6, 182, 212, 0.2)",
                                borderColor: "#06b6d4",
                                pointBackgroundColor: "#06b6d4",
                                pointBorderColor: "#fff",
                                pointHoverBackgroundColor: "#fff",
                                pointHoverBorderColor: "#06b6d4"
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {{
                                r: {{
                                    min: 0,
                                    max: 100,
                                    angleLines: {{ color: gridColor }},
                                    grid: {{ color: gridColor }},
                                    pointLabels: {{ color: textColor, font: {{ size: 10 }} }},
                                    ticks: {{ color: textColor, backdropColor: "transparent", stepSize: 25 }}
                                }}
                            }},
                            plugins: {{
                                legend: {{ labels: {{ color: textColor }} }}
                            }}
                        }}
                    }});
                }} else {{
                    radarChartInstance.resize();
                    radarChartInstance.update();
                }}
            }}

            // 3. Focus Indicator Chart
            if (!focusIndicatorChartInstance) {{
                renderFocusChart(currentFocusKey);
            }} else {{
                focusIndicatorChartInstance.resize();
                focusIndicatorChartInstance.update();
            }}

            // 4. Grid Charts
            initMacroIndicatorGridCharts(isDark, textColor, gridColor);
        }}

        function initMacroIndicatorGridCharts(isDark, textColor, gridColor) {{
            for (const key in INDICATORS_DATA) {{
                const ind = INDICATORS_DATA[key];
                const canvas = document.getElementById(`chart_${{key}}`);
                if (!canvas) continue;

                if (indicatorChartInstances[key]) {{
                    indicatorChartInstances[key].resize();
                    indicatorChartInstances[key].update();
                    continue;
                }}

                const dates = (ind.history_dates && ind.history_dates.length > 0) ? ind.history_dates : Array.from({{length: (ind.history || []).length}}, (_, i) => `${{i + 1}}`);
                const values = ind.history || [];
                const ma50 = ind.history_ma50 || [];

                const isBullish = ind.ma50_status.includes("Above") || ind.trend_signal.includes("Rising");
                const isBearish = ind.ma50_status.includes("Below") || ind.trend_signal.includes("Falling");
                const lineColor = isBullish ? "#10b981" : (isBearish ? "#ef4444" : "#06b6d4");
                const fillColor = isBullish ? "rgba(16, 185, 129, 0.08)" : (isBearish ? "rgba(239, 68, 68, 0.08)" : "rgba(6, 182, 212, 0.08)");

                const ctx = canvas.getContext("2d");
                indicatorChartInstances[key] = new Chart(ctx, {{
                    type: "line",
                    data: {{
                        labels: dates,
                        datasets: [
                            {{
                                label: ind.ratio_tickers,
                                data: values,
                                borderColor: lineColor,
                                backgroundColor: fillColor,
                                borderWidth: 1.5,
                                fill: true,
                                tension: 0.1,
                                pointRadius: values.length > 25 ? 0 : 2
                            }},
                            {{
                                label: "50-MA",
                                data: ma50.length > 0 ? ma50 : Array(values.length).fill(ind.ma50),
                                borderColor: "#f59e0b",
                                borderWidth: 1,
                                borderDash: [3, 3],
                                fill: false,
                                pointRadius: 0
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {{ mode: "index", intersect: false }},
                        scales: {{
                            x: {{ display: false }},
                            y: {{
                                grid: {{ color: gridColor }},
                                ticks: {{ color: textColor, font: {{ size: 9 }}, maxTicksLimit: 4 }}
                            }}
                        }},
                        plugins: {{
                            legend: {{ display: false }}
                        }}
                    }}
                }});
            }}
        }}

        // Option Chain Table Filtering
        function filterOptionChain(filterType, btn) {{
            document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            const rows = document.querySelectorAll("#chainTableBody tr");
            rows.forEach(row => {{
                const type = row.getAttribute("data-type");
                const isNear = row.getAttribute("data-near") === "true";

                if (filterType === "all") {{
                    row.style.display = "";
                }} else if (filterType === "calls" && type === "CALL") {{
                    row.style.display = "";
                }} else if (filterType === "puts" && type === "PUT") {{
                    row.style.display = "";
                }} else if (filterType === "ntm" && isNear) {{
                    row.style.display = "";
                }} else {{
                    row.style.display = "none";
                }}
            }});
        }}

        function searchOptionChain() {{
            const query = document.getElementById("chainSearchInput").value.toUpperCase().trim();
            const rows = document.querySelectorAll("#chainTableBody tr");
            rows.forEach(row => {{
                const text = row.innerText.toUpperCase();
                row.style.display = text.includes(query) ? "" : "none";
            }});
        }}

        // Options Payoff Simulator Controller
        function setSimulatorStrategy(strat) {{
            currentSimStrategy = strat;
            const btnCC = document.getElementById("modeBtnCC");
            const btnCSP = document.getElementById("modeBtnCSP");
            if (strat === "CC") {{
                btnCC.classList.add("active");
                btnCSP.classList.remove("active");
            }} else {{
                btnCSP.classList.add("active");
                btnCC.classList.remove("active");
            }}
            updateSimPayoff();
        }}

        function loadIntoSimulator(strat, strike, premium, spot) {{
            setSimulatorStrategy(strat);
            document.getElementById("simStockPriceInput").value = spot.toFixed(2);
            document.getElementById("simStrikeInput").value = strike.toFixed(2);
            document.getElementById("simPremiumInput").value = premium.toFixed(2);
            
            const slider = document.getElementById("priceSlider");
            slider.min = Math.max(1.0, (spot * 0.70)).toFixed(1);
            slider.max = (spot * 1.30).toFixed(1);
            slider.value = spot.toFixed(1);

            switchTab("playbook");
            updateSimPayoff();
        }}

        function initPayoffChart() {{
            if (hasChartJs) {{
                try {{
                    initChartJsPayoff();
                    return;
                }} catch (e) {{
                    console.warn("Chart.js payoff init failed, using native canvas:", e);
                }}
            }}
            updateSimPayoff();
        }}

        function initChartJsPayoff() {{
            const canvas = document.getElementById("payoffChart");
            if (!canvas) return;

            if (payoffChartInstance) {{
                updateSimPayoff();
                return;
            }}

            const isDark = currentTheme === "dark";
            const textColor = isDark ? "#94a3b8" : "#475569";
            const gridColor = isDark ? "#243046" : "#e2e8f0";

            const ctx = canvas.getContext("2d");
            payoffChartInstance = new Chart(ctx, {{
                type: "line",
                data: {{
                    labels: [],
                    datasets: [
                        {{
                            label: "Strategy Net P&L ($)",
                            data: [],
                            borderColor: "#10b981",
                            backgroundColor: "rgba(16, 185, 129, 0.12)",
                            borderWidth: 2.5,
                            fill: true,
                            tension: 0.1
                        }},
                        {{
                            label: "Zero Breakeven Line",
                            data: [],
                            borderColor: isDark ? "#64748b" : "#94a3b8",
                            borderWidth: 1,
                            borderDash: [5, 5],
                            fill: false,
                            pointRadius: 0
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{ mode: "index", intersect: false }},
                    scales: {{
                        x: {{
                            title: {{ display: true, text: "Underlying Stock Price at Expiration ($)", color: textColor, font: {{ weight: "bold" }} }},
                            grid: {{ color: gridColor }},
                            ticks: {{ color: textColor, maxTicksLimit: 12 }}
                        }},
                        y: {{
                            title: {{ display: true, text: "Strategy Total P&L ($ per contract)", color: textColor, font: {{ weight: "bold" }} }},
                            grid: {{ color: gridColor }},
                            ticks: {{ color: textColor }}
                        }}
                    }},
                    plugins: {{
                        legend: {{ labels: {{ color: textColor }} }}
                    }}
                }}
            }});

            updateSimPayoff();
        }}

        function updateSimPayoff() {{
            const stockCost = parseFloat(document.getElementById("simStockPriceInput").value) || CURRENT_PRICE;
            const strike = parseFloat(document.getElementById("simStrikeInput").value) || CURRENT_PRICE;
            const premium = parseFloat(document.getElementById("simPremiumInput").value) || (CURRENT_PRICE * 0.02);
            
            const slider = document.getElementById("priceSlider");
            const simPrice = parseFloat(slider.value);
            document.getElementById("sliderPriceDisplay").innerText = "$" + simPrice.toFixed(2);

            const pctMove = ((simPrice - stockCost) / stockCost) * 100.0;
            const sign = pctMove >= 0 ? "+" : "";
            document.getElementById("simPriceMove").innerText = sign + pctMove.toFixed(2) + "%";

            let dollarPnL = 0;
            let breakeven = 0;
            let statusText = "";
            let statusColor = "var(--accent-green)";
            let rocPct = 0;

            if (currentSimStrategy === "CC") {{
                // Covered Call: Long 100 shares at stockCost, Short 1 Call at strike for premium
                breakeven = stockCost - premium;
                if (simPrice >= strike) {{
                    dollarPnL = (strike - stockCost + premium) * 100.0;
                    statusText = "Max Profit (Shares Called Away at Strike)";
                    statusColor = "var(--accent-green)";
                }} else {{
                    dollarPnL = (simPrice - stockCost + premium) * 100.0;
                    if (simPrice >= breakeven) {{
                        statusText = "Profitable (Cushioned by Premium)";
                        statusColor = "var(--accent-cyan)";
                    }} else {{
                        statusText = "Downside Loss (Cushioned vs Outright Stock)";
                        statusColor = "var(--accent-red)";
                    }}
                }}
                rocPct = (dollarPnL / (stockCost * 100.0)) * 100.0;
            }} else {{
                // Cash-Secured Put: Short 1 Put at strike for premium, 100*strike collateral
                breakeven = strike - premium;
                if (simPrice >= strike) {{
                    dollarPnL = premium * 100.0;
                    statusText = "Max Profit (100% Premium Retained, Unassigned)";
                    statusColor = "var(--accent-green)";
                }} else {{
                    dollarPnL = (premium - (strike - simPrice)) * 100.0;
                    if (simPrice >= breakeven) {{
                        statusText = "Profitable (Assigned at Discount Basis)";
                        statusColor = "var(--accent-cyan)";
                    }} else {{
                        statusText = "Assigned Below Net Breakeven";
                        statusColor = "var(--accent-red)";
                    }}
                }}
                rocPct = (dollarPnL / (strike * 100.0)) * 100.0;
            }}

            const pnlSign = dollarPnL >= 0 ? "+$" : "-$";
            document.getElementById("simDollarPnL").innerText = pnlSign + Math.abs(dollarPnL).toFixed(2);
            document.getElementById("simDollarPnL").style.color = dollarPnL >= 0 ? "var(--accent-green)" : "var(--accent-red)";
            
            const rocSign = rocPct >= 0 ? "+" : "";
            document.getElementById("simROCPct").innerText = rocSign + rocPct.toFixed(2) + "%";
            document.getElementById("simROCPct").style.color = rocPct >= 0 ? "var(--accent-green)" : "var(--accent-red)";

            document.getElementById("simBreakeven").innerText = "$" + breakeven.toFixed(2);
            document.getElementById("simPnLStatus").innerText = statusText;
            document.getElementById("simPnLStatus").style.color = statusColor;

            // Recompute curve
            const low = Math.min(stockCost, strike) * 0.70;
            const high = Math.max(stockCost, strike) * 1.30;
            const step = (high - low) / 40;
            const prices = [];
            const pnlValues = [];
            const zeroLine = [];

            for (let p = low; p <= high; p += step) {{
                prices.push(p.toFixed(2));
                zeroLine.push(0);
                let pnl = 0;
                if (currentSimStrategy === "CC") {{
                    if (p >= strike) {{
                        pnl = (strike - stockCost + premium) * 100.0;
                    }} else {{
                        pnl = (p - stockCost + premium) * 100.0;
                    }}
                }} else {{
                    if (p >= strike) {{
                        pnl = premium * 100.0;
                    }} else {{
                        pnl = (premium - (strike - p)) * 100.0;
                    }}
                }}
                pnlValues.push(pnl.toFixed(2));
            }}

            if (payoffChartInstance && hasChartJs) {{
                payoffChartInstance.data.labels = prices;
                payoffChartInstance.data.datasets[0].data = pnlValues;
                payoffChartInstance.data.datasets[0].label = currentSimStrategy === "CC" ? "Covered Call Net P&L ($)" : "Cash-Secured Put Net P&L ($)";
                payoffChartInstance.data.datasets[1].data = zeroLine;
                payoffChartInstance.update();
            }} else {{
                drawNativeLineChart("payoffChart", [
                    {{ data: pnlValues.map(v => parseFloat(v)), color: "#10b981", fillColor: "rgba(16, 185, 129, 0.15)", fill: true, lineWidth: 2.5 }},
                    {{ data: zeroLine, color: "#64748b", dash: [4, 4], lineWidth: 1 }}
                ], prices, {{ padLeft: 60, yPrefix: "$", yTicks: 5 }});
            }}
        }}

        function updateChartTheme() {{
            const isDark = currentTheme === "dark";
            const textColor = isDark ? "#94a3b8" : "#475569";
            const gridColor = isDark ? "#243046" : "#e2e8f0";

            const allCharts = [
                priceChartInstance,
                radarChartInstance,
                focusIndicatorChartInstance,
                payoffChartInstance,
                ...Object.values(indicatorChartInstances)
            ];

            allCharts.forEach(chart => {{
                if (chart) {{
                    if (chart.options.scales) {{
                        if (chart.options.scales.x && chart.options.scales.x.grid) chart.options.scales.x.grid.color = gridColor;
                        if (chart.options.scales.x && chart.options.scales.x.ticks) chart.options.scales.x.ticks.color = textColor;
                        if (chart.options.scales.y && chart.options.scales.y.grid) chart.options.scales.y.grid.color = gridColor;
                        if (chart.options.scales.y && chart.options.scales.y.ticks) chart.options.scales.y.ticks.color = textColor;
                        if (chart.options.scales.r) {{
                            if (chart.options.scales.r.angleLines) chart.options.scales.r.angleLines.color = gridColor;
                            if (chart.options.scales.r.grid) chart.options.scales.r.grid.color = gridColor;
                            if (chart.options.scales.r.pointLabels) chart.options.scales.r.pointLabels.color = textColor;
                            if (chart.options.scales.r.ticks) chart.options.scales.r.ticks.color = textColor;
                        }}
                    }}
                    if (chart.options.plugins && chart.options.plugins.legend && chart.options.plugins.legend.labels) {{
                        chart.options.plugins.legend.labels.color = textColor;
                    }}
                    chart.update();
                }}
            }});
        }}

        // Window resize observer
        window.addEventListener("resize", () => {{
            if (hasChartJs) {{
                [priceChartInstance, radarChartInstance, focusIndicatorChartInstance, payoffChartInstance, ...Object.values(indicatorChartInstances)].forEach(chart => {{
                    if (chart) chart.resize();
                }});
            }} else {{
                renderAllNativeCharts();
            }}
        }});

        // Initialize on load
        document.addEventListener("DOMContentLoaded", () => {{
            applyTheme(currentTheme);
            // Pre-render native charts so they are immediately visible on tab switch
            setTimeout(() => {{
                if (!hasChartJs) renderAllNativeCharts();
            }}, 50);
        }});
    </script>
</body>
</html>"""
        return html_doc
