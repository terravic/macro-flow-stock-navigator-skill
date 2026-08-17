"""
UI Dashboard Renderer for Gemini Enterprise & Spark UI.
Renders concise, executive Markdown dashboards and structured JSON payloads.
Uses clean status circle colors (🟢, 🟡, 🔴) with a professional, business-like tone.
"""

import json
from datetime import datetime
from typing import Dict, Any, List

class SparkDashboardRenderer:
    """
    Renders the executive Macro Flow Stock Navigator dashboard.
    """

    @classmethod
    def render_markdown(
        cls,
        ticker_info: Dict[str, Any],
        indicators: Dict[str, Dict[str, Any]],
        decision: Dict[str, Any],
        is_synthetic: bool = False
    ) -> str:
        """
        Builds a concise, business-like Markdown response.
        """
        ticker = ticker_info.get("ticker", "UNKNOWN")
        price = ticker_info.get("current_price", 0.0)
        chg = ticker_info.get("change_pct", 0.0)
        chg_str = f"+{chg:.2f}%" if chg >= 0 else f"{chg:.2f}%"
        action_badge = decision.get("signal_badge", "🟡 NEUTRAL")
        archetype_name = decision.get("archetype_name", "General Stock")
        macro_regime = decision.get("macro_regime", {})
        playbook = decision.get("options_playbook", {})
        tactical = playbook.get("tactical_execution", {})
        warnings = playbook.get("risk_warnings", [])
        
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
        data_mode_notice = " *(Simulated Benchmark)*" if is_synthetic else ""

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
        lines.append(f"| **Macro Regime** | {macro_regime.get('name', 'Balanced Rotation')} | **Timestamp** | {timestamp_str}{data_mode_notice} |")
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
        lines.append(f"- **Technical Health:** Price vs 50-MA: `{ticker_info.get('diff_ma50_pct', 0.0):+.2f}%` | 200-MA: `{ticker_info.get('diff_ma200_pct', 0.0):+.2f}%` | RSI(14): `{ticker_info.get('rsi_14', 50.0)}` | 30d Volatility: `{ticker_info.get('historical_vol_30d', 0.0)}%` | Beta: `{ticker_info.get('beta', 1.0)}`")
        lines.append(f"- **Regime Context:** {macro_regime.get('summary', '')}")
        lines.append("")

        favorable = decision.get("favorable_forces", [])
        hostile = decision.get("hostile_forces", [])

        if favorable:
            lines.append("**Key Macro Tailwinds (Positive Drivers):**")
            for f in favorable:
                lines.append(f"- 🟢 **{f['indicator']} (`{f['ratio']}`)** is {f['trend']}: {f['meaning']}.")
        else:
            lines.append("- *No dominant macro tailwinds detected.*")

        lines.append("")
        if hostile:
            lines.append("**Key Macro Headwinds (Risk Factors):**")
            for h in hostile:
                lines.append(f"- 🔴 **{h['indicator']} (`{h['ratio']}`)** is {h['trend']}: {h['meaning']}.")
        else:
            lines.append("- *No major macro headwinds detected.*")

        lines.append("")

        # ---------------------------------------------------------
        # 4. STRATEGIC OPTIONS PLAYBOOK
        # ---------------------------------------------------------
        lines.append("## 3. Strategic Options Playbook")
        lines.append("")
        lines.append(f"### Strategy: **{tactical.get('strategy', 'Neutral Options Overlay')}**")
        lines.append(f"*{tactical.get('rationale', '')}*")
        lines.append("")
        lines.append("| Execution Parameter | Tactical Specification | Target / Rationale |")
        lines.append("| :--- | :--- | :--- |")
        lines.append(f"| **Target Delta** | `{tactical.get('recommended_delta', 'N/A')}` | Statistical probability of profit |")
        lines.append(f"| **Strike Selection** | `{tactical.get('optimal_strike', 'N/A')}` | Anchored relative to technical support & resistance |")
        lines.append(f"| **Target DTE** | `{tactical.get('target_dte', '30-45 DTE')}` | Optimal theta decay horizon |")
        lines.append(f"| **Target Return** | `{tactical.get('estimated_annualized_yield', 'N/A')}` | Expected annualized return |")
        lines.append(f"| **Profit Target** | `{tactical.get('profit_target', '50% of credit')}` | Defined-risk exit threshold |")
        lines.append(f"| **Stop Loss Rule** | `{tactical.get('stop_loss_rule', '2x credit')}` | Strict risk-defined exit criteria |")
        lines.append("")

        # ---------------------------------------------------------
        # 5. RISK CONSIDERATIONS
        # ---------------------------------------------------------
        lines.append("### Key Risk Considerations")
        for w in warnings:
            lines.append(f"- 🔴 {w}")

        lines.append("")
        lines.append("---")
        lines.append("*Disclaimer: Macro Flow Stock Navigator is an analytical decision-support tool. Not personalized financial or investment advice. Always evaluate position sizing and liquidity before executing trades.*")

        return "\n".join(lines)

    @classmethod
    def render_json(
        cls,
        ticker_info: Dict[str, Any],
        indicators: Dict[str, Dict[str, Any]],
        decision: Dict[str, Any],
        is_synthetic: bool = False
    ) -> str:
        """
        Builds a structured JSON payload for programmatic consumption.
        """
        payload = {
            "metadata": {
                "skill": "macro-flow-stock-navigator",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
                "is_synthetic": is_synthetic
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
