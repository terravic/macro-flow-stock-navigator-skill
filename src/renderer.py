"""
UI Dashboard Renderer.
Renders concise, executive Markdown dashboards and structured JSON/HTML payloads
strictly adhering to DESIGN.md specifications.
"""

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime
from typing import Dict, Any, List


def detect_host_system_theme() -> str:
    """
    Queries the native OS appearance preference across macOS, Windows, and Linux
    as a backend fallback for headless or restricted webviews.
    Returns 'dark' or 'light'.
    """
    try:
        if sys.platform == "darwin":
            res = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
                timeout=1.5,
            )
            if res.returncode == 0 and "dark" in res.stdout.strip().lower():
                return "dark"
            return "light"
        elif sys.platform == "win32":
            import winreg  # type: ignore

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return "light" if int(val) == 1 else "dark"
        else:
            # Linux: check GTK_THEME, gsettings, and kdeglobals
            gtk_theme = os.environ.get("GTK_THEME", "").lower()
            if "dark" in gtk_theme:
                return "dark"
            if "light" in gtk_theme:
                return "light"

            for cmd in [
                ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
            ]:
                try:
                    res = subprocess.run(cmd, capture_output=True, text=True, timeout=1.5)
                    if res.returncode == 0:
                        out = res.stdout.strip().lower()
                        if "dark" in out:
                            return "dark"
                        if "light" in out or "default" in out:
                            return "light"
                except Exception:
                    pass

            kde_path = os.path.expanduser("~/.config/kdeglobals")
            if os.path.isfile(kde_path):
                with open(kde_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().lower()
                    if "breezedark" in content or "dark" in content:
                        return "dark"
    except Exception:
        pass
    return "dark"


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
        cash_available: float = 0.0,
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
        last_trade_date = ticker_info.get(
            "last_trade_date", datetime.now().strftime("%Y-%m-%d")
        )

        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M UTC")

        lines = []

        # ---------------------------------------------------------
        # 1. HEADER & EXECUTIVE SUMMARY
        # ---------------------------------------------------------
        lines.append(f"# Macro Flow Stock Navigator: {ticker}")
        lines.append("")
        lines.append("| Metric | Value | Metric | Value |")
        lines.append("| :--- | :--- | :--- | :--- |")
        lines.append(
            f"| **Current Price** | ${price:.2f} ({chg_str}) | **Stock Archetype** | {archetype_name} |"
        )
        lines.append(
            f"| **Recommended Action** | {action_badge} | **Macro Alignment** | {decision.get('alignment_gauge', '')} |"
        )
        lines.append(
            f"| **Macro Regime** | {macro_regime.get('name', 'Balanced Rotation')} | **Last Session Close** | {last_trade_date} |"
        )
        lines.append(
            f"| **Analysis Timestamp** | {timestamp_str} | **Market Status** | Real-Time / Last Close ({last_trade_date}) |"
        )
        lines.append("")

        # ---------------------------------------------------------
        # EXECUTIVE FINDING
        # ---------------------------------------------------------
        synthesis = decision.get("unified_synthesis", {})
        if synthesis:
            t_light = synthesis.get("traffic_light", "YELLOW LIGHT")
            verdict = synthesis.get("verdict_headline", "")
            comp_score = synthesis.get("composite_score", 0.0)
            dir_title = synthesis.get("direction_title", "")
            pillars = synthesis.get("pillars", {})
            action = synthesis.get("plain_dollar_action", {})

            lines.append("## Executive Finding")
            lines.append("")
            lines.append(f"### Status: **{t_light}** — {dir_title} ({comp_score:+.1f}/100)")
            lines.append(f"> **Verdict:** {verdict}")
            lines.append("")
            lines.append("#### Core Health Pillars:")
            lines.append("")
            lines.append("| Pillar | Status | Finding |")
            lines.append("| :--- | :--- | :--- |")
            for p_key, p_val in pillars.items():
                title = p_val.get("title", p_key)
                status = p_val.get("status", "N/A")
                expl = p_val.get("explanation", "")
                floor = f" (Floor: {p_val['safety_floor']})" if "safety_floor" in p_val else ""
                lines.append(f"| **{title}** | `{status}`{floor} | {expl} |")
            lines.append("")

            if action:
                lines.append("#### Action Plan:")
                lines.append(f"**{action.get('headline', '')}**")
                lines.append("")
                if "directive" in action:
                    lines.append(f"- **Directive:** `{action['directive']}`")
                    lines.append(f"- **Upfront Cash Income:** `+${action.get('cash_collected_dollars', 0):,}`")
                    lines.append(f"- **{action.get('rate_label', 'Return Rate')}:** `+{action.get('rate_val', 0.0):.1f}%`")
                    lines.append(f"- **{action.get('buffer_label', 'Buffer')}:** `{action.get('buffer_val', 0.0):.1f}%`")
                for step in action.get("steps", []):
                    lines.append(f"- {step}")
                lines.append(f"- *Summary:* {action.get('summary', '')}")
                lines.append("")

        # Optional Portfolio Overlay (Shares Held or Cash Collateral)
        if shares_held > 0 or cash_available > 0:
            lines.append("## Portfolio Positioning & Tailored Options Recommendations")
            lines.append("")
            if shares_held > 0:
                num_contracts = shares_held // 100
                remainder = shares_held % 100
                lines.append(
                    f"### Tailored Covered Call Strategy ({shares_held:,} Shares Held)"
                )
                if num_contracts > 0:
                    lines.append(
                        f"- **Covered Call Capacity:** `{num_contracts} contract(s)` (100 shares per contract). Remainder unhedged: `{remainder} shares`."
                    )
                    balanced_cc = cc_matrix.get("balanced", {})
                    cons_cc = cc_matrix.get("conservative", {})
                    agg_cc = cc_matrix.get("aggressive", {})

                    if balanced_cc:
                        mid_p = balanced_cc.get("mid", 0.0)
                        prem_total = mid_p * 100.0 * num_contracts
                        lines.append(
                            f"- **Recommended Strike:** `${balanced_cc.get('strike', 0.0):.2f}` ({balanced_cc.get('delta', 0.0):+.2f}Δ, ~{balanced_cc.get('otm_pct', 0.0):.1f}% OTM) expiring in `{balanced_cc.get('dte', 30)}d`."
                        )
                        lines.append(
                            f"- **Est. Income Generated:** `${prem_total:,.2f}` upfront cash premium (`+{balanced_cc.get('yield_unassigned', 0.0):.1f}%` annualized yield)."
                        )
                        lines.append(
                            f"- **If Called Away:** Total realized gain of `+${((balanced_cc.get('strike', price) - price + mid_p) * 100.0 * num_contracts):,.2f}` (`+{balanced_cc.get('return_called_away', 0.0):.1f}%`)."
                        )
                        lines.append(
                            f"- **Alternative Tiers:** Conservative Strike: `${cons_cc.get('strike', 0.0):.2f}` (`${cons_cc.get('mid', 0.0)*100*num_contracts:,.2f}` income) | Aggressive Strike: `${agg_cc.get('strike', 0.0):.2f}` (`${agg_cc.get('mid', 0.0)*100*num_contracts:,.2f}` income)."
                        )
                else:
                    lines.append(
                        f"- *Note:* Covered calls require increments of 100 shares per contract. You hold {shares_held} shares. Accumulate {100 - remainder} more shares to sell 1 covered call contract."
                    )
                lines.append("")

            if cash_available > 0:
                balanced_csp = csp_matrix.get("balanced", {})
                cons_csp = csp_matrix.get("conservative", {})
                agg_csp = csp_matrix.get("aggressive", {})

                strike = balanced_csp.get("strike", price * 0.95)
                req_per_contract = strike * 100.0
                num_csp = int(cash_available // req_per_contract)
                lines.append(
                    f"### Tailored Cash-Secured Put Strategy (${cash_available:,.2f} Cash Available)"
                )
                if num_csp > 0:
                    mid_p = balanced_csp.get("mid", 0.0)
                    prem_total = mid_p * 100.0 * num_csp
                    unused_cash = cash_available - (num_csp * req_per_contract)
                    lines.append(
                        f"- **Cash-Secured Put Capacity:** `{num_csp} contract(s)` at `${strike:.2f}` strike (Collateral utilized: `${num_csp * req_per_contract:,.2f}`, Unused cash: `${unused_cash:,.2f}`)."
                    )
                    lines.append(
                        f"- **Target Strike:** `${strike:.2f}` ({balanced_csp.get('delta', 0.0):+.2f}Δ, ~{balanced_csp.get('otm_pct', 0.0):.1f}% discount) expiring in `{balanced_csp.get('dte', 30)}d`."
                    )
                    lines.append(
                        f"- **Est. Cash Premium Harvest:** `+${prem_total:,.2f}` upfront credit (`+{balanced_csp.get('annualized_roc', 0.0):.1f}%` annualized ROC)."
                    )
                    lines.append(
                        f"- **Net Effective Purchase Price if Assigned:** `${balanced_csp.get('net_cost_basis', strike - mid_p):.2f}` (`{balanced_csp.get('discount_pct', 0.0):.1f}%` discount below current market price ${price:.2f})."
                    )
                    lines.append(
                        f"- **Alternative Tiers:** Conservative Strike: `${cons_csp.get('strike', 0.0):.2f}` ({int(cash_available // (cons_csp.get('strike', strike)*100))} contracts, `+{cons_csp.get('annualized_roc', 0.0):.1f}%` ROC) | Aggressive Strike: `${agg_csp.get('strike', 0.0):.2f}` (`+{agg_csp.get('annualized_roc', 0.0):.1f}%` ROC)."
                    )
                else:
                    lines.append(
                        f"- *Note:* 1 Cash-Secured Put contract at the balanced strike (${strike:.2f}) requires `${req_per_contract:,.2f}` in collateral. You have `${cash_available:,.2f}`."
                    )
                lines.append("")

        # ---------------------------------------------------------
        # 2. MACRO INDICATORS TABLE
        # ---------------------------------------------------------
        lines.append(f"## 1. Macro Cross-Asset Indicators ({len(indicators)} Ratios)")
        lines.append("")
        lines.append(
            "| Indicator | Ratio Tickers | Current Value | 50-MA Status | Trend | Interpretation |"
        )
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")

        for ind_id, ind in indicators.items():
            disp_name = ind.get("display_name", ind_id)
            ratio = ind.get("ratio_tickers", ind_id)
            val = ind.get("current_value", 0.0)
            ma_stat = ind.get("ma50_status", "N/A")
            trend = ind.get("trend_signal", "Flat")
            meaning = ind.get("market_meaning", "")
            lines.append(
                f"| **{disp_name}** | `{ratio}` | `{val}` | {ma_stat} | {trend} | {meaning} |"
            )

        lines.append("")

        # ---------------------------------------------------------
        # 3. MACRO DRIVERS & SENSITIVITY
        # ---------------------------------------------------------
        lines.append("## 2. Macro Drivers & Sensitivity Analysis")
        lines.append("")
        lines.append(
            f"- **Technical Health:** Price vs 50-MA: `{ticker_info.get('diff_ma50_pct', 0.0):+.2f}%` | 200-MA: `{ticker_info.get('diff_ma200_pct', 0.0):+.2f}%` | RSI(14): `{ticker_info.get('rsi_14', 50.0)}` | 30d Realized Vol: `{ticker_info.get('historical_vol_30d', 0.0)}%` | Beta: `{ticker_info.get('beta', 1.0)}`"
        )
        lines.append(f"- **Regime Context:** {macro_regime.get('summary', '')}")
        lines.append("")

        favorable = decision.get("favorable_forces", [])
        hostile = decision.get("hostile_forces", [])

        if favorable:
            lines.append("**Key Macro Tailwinds (Positive Drivers):**")
            for f in favorable:
                lines.append(
                    f"- **{f['indicator']} (`{f['ratio']}`)** is {f['trend']}: {f['meaning']}."
                )
        else:
            lines.append("- *No dominant macro tailwinds detected.*")

        lines.append("")
        if hostile:
            lines.append("**Key Macro Headwinds (Risk Factors):**")
            for h in hostile:
                lines.append(
                    f"- **{h['indicator']} (`{h['ratio']}`)** is {h['trend']}: {h['meaning']}."
                )
        else:
            lines.append("- *No major macro headwinds detected.*")

        lines.append("")

        # ---------------------------------------------------------
        # MARKET MICROSTRUCTURE & PRACTITIONER SIGNALS
        # ---------------------------------------------------------
        opt_data = ticker_info.get("options_data", {})
        lines.append("## 2b. Market Microstructure, Whale Order Flow & Practitioner Signals")
        lines.append("")
        lines.append("| Microstructure Metric | Observed Value | Strategic Interpretation |")
        lines.append("| :--- | :--- | :--- |")
        lines.append(
            f"| **Net Dealer Gamma (GEX)** | `{opt_data.get('net_gex_formatted', '$0M')}` | {opt_data.get('gamma_regime', 'Neutral')} |"
        )
        lines.append(
            f"| **Gamma Flip Safety Floor** | `${opt_data.get('gamma_flip_strike', price):.2f}` | Key institutional threshold: Above = shock absorber, Below = volatility cascade |"
        )
        lines.append(
            f"| **25-Delta Put/Call Skew** | `{opt_data.get('skew_25d', 2.0):+.1f}%` | {opt_data.get('skew_signal', 'Balanced')} |"
        )
        lines.append(
            f"| **Retail 5Δ Call Surge** | `{opt_data.get('lottery_call_ratio', 10.0):.1f}%` | {opt_data.get('lottery_call_signal', 'Normal')} |"
        )
        lines.append(
            f"| **Short Interest (% Float)** | `{ticker_info.get('short_float_pct', 2.0):.2f}%` | Days to Cover: `{ticker_info.get('days_to_cover', 2.5)}d` |"
        )
        lines.append(
            f"| **Dark Pool Volume Share** | `{ticker_info.get('dark_pool_ratio_pct', 43.0):.1f}%` | Real-world off-exchange institutional block execution |"
        )
        lines.append(
            f"| **Closing MOC Imbalance** | `{ticker_info.get('moc_imbalance', 'Balanced')}` | End-of-day institutional closing auction direction |"
        )
        lines.append("")

        # ---------------------------------------------------------
        # 4. OPTIONS VOLATILITY & KEY INDICATORS
        # ---------------------------------------------------------
        lines.append("## 3. Options Volatility & Market Indicators")
        lines.append("")
        lines.append("| Metric / Indicator | Value | Strategic Interpretation |")
        lines.append("| :--- | :--- | :--- |")
        lines.append(
            f"| **Implied Volatility (ATM)** | `{opt_analytics.get('iv_atm', 0.0)}%` | Pricing baseline for near-term option premium |"
        )
        lines.append(
            f"| **30-Day Realized Volatility** | `{opt_analytics.get('hv_30d', 0.0)}%` | Historical asset price dispersion |"
        )
        lines.append(
            f"| **IV vs RV Spread** | `{opt_analytics.get('iv_rv_spread', 0.0):+.1f}%` | {'Option premiums rich (favorable for selling)' if opt_analytics.get('iv_rv_spread', 0) >= 0 else 'Option premiums lean (conservative strike selection)'} |"
        )
        lines.append(
            f"| **IV Rank & Percentile** | `{opt_analytics.get('iv_rank', 0.0)}%` / `{opt_analytics.get('iv_percentile', 0.0)}%` | Relative IV positioning across 52-week envelope |"
        )
        lines.append(
            f"| **Put/Call Ratio (Vol / OI)** | `{opt_analytics.get('pcr_volume', 1.0)}` / `{opt_analytics.get('pcr_open_interest', 1.0)}` | Institutional hedging vs call speculation sentiment |"
        )
        lines.append(
            f"| **Max Pain Theory Strike** | `${opt_analytics.get('max_pain_strike', price):.2f}` | Strike where total option expiration value is minimized |"
        )
        lines.append(
            f"| **30-Day Expected Move (±1σ)** | `±${opt_analytics.get('expected_move_30d', 0.0):.2f} (±{opt_analytics.get('expected_move_pct', 0.0):.1f}%)` | Target range: `${opt_analytics.get('expected_move_lower', 0.0):.2f} – ${opt_analytics.get('expected_move_upper', 0.0):.2f}` |"
        )
        lines.append("")

        # ---------------------------------------------------------
        # 5. COVERED CALL & CASH-SECURED PUT SCREENER MATRICES
        # ---------------------------------------------------------
        lines.append("## 4. Options Selling Playbook: Covered Calls & Cash-Secured Puts")
        lines.append("")
        lines.append(
            f"### Recommended Primary Focus: **{tactical.get('strategy', 'Neutral Options Overlay')}**"
        )
        lines.append(f"*{tactical.get('rationale', '')}*")
        lines.append("")

        # Covered Call Screener Table
        lines.append("### A. Covered Call Screener Matrix (Long Stock + Sell Call)")
        lines.append(
            "| Tier | Target Δ | Strike | Mid Price | OTM % | Ann. Yield (Unassigned) | Total Return (Called) | Downside Buffer | DTE |"
        )
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for tier_key, tier_title in [
            ("conservative", "Conservative (0.20Δ)"),
            ("balanced", "Balanced (0.30Δ)"),
            ("aggressive", "Aggressive (0.40Δ)"),
        ]:
            c = cc_matrix.get(tier_key, {})
            if c:
                lines.append(
                    f"| **{tier_title}** | `{c.get('delta', 0.0):+.2f}` | `${c.get('strike', 0.0):.2f}` | `${c.get('mid', 0.0):.2f}` | `+{c.get('otm_pct', 0.0):.1f}%` | `+{c.get('yield_unassigned', 0.0):.1f}%` | `+{c.get('return_called_away', 0.0):.1f}%` | `+{c.get('downside_protection', 0.0):.1f}%` | `{c.get('dte', 30)}d` |"
                )
        lines.append("")

        # Cash-Secured Put Screener Table
        lines.append(
            "### B. Cash-Secured Put Screener Matrix (Sell Put + Cash Collateral)"
        )
        lines.append(
            "| Tier | Target Δ | Strike | Mid Price | OTM % | Required Collateral | Net Cost Basis | Discount vs Spot | Ann. ROC | DTE |"
        )
        lines.append(
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
        )
        for tier_key, tier_title in [
            ("conservative", "Conservative (0.20Δ)"),
            ("balanced", "Balanced (0.30Δ)"),
            ("aggressive", "Aggressive (0.40Δ)"),
        ]:
            p = csp_matrix.get(tier_key, {})
            if p:
                lines.append(
                    f"| **{tier_title}** | `{p.get('delta', 0.0):+.2f}` | `${p.get('strike', 0.0):.2f}` | `${p.get('mid', 0.0):.2f}` | `-{p.get('otm_pct', 0.0):.1f}%` | `${p.get('collateral_required', 0.0):,.0f}` | `${p.get('net_cost_basis', 0.0):.2f}` | `{p.get('discount_pct', 0.0):.1f}%` | `+{p.get('annualized_roc', 0.0):.1f}%` | `{p.get('dte', 30)}d` |"
                )
        lines.append("")

        # ---------------------------------------------------------
        # 6. UNUSUAL OPTION ACTIVITY
        # ---------------------------------------------------------
        if uoa_list:
            lines.append(
                "## 5. Unusual Option Activity & Institutional Flow Detection"
            )
            lines.append("")
            lines.append(
                "| Type | Strike | Volume | Open Int | Vol/OI | Est. Dollar Flow | Institutional Sentiment |"
            )
            lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
            for uoa in uoa_list:
                lines.append(
                    f"| **{uoa.get('option_type')}** | `${uoa.get('strike', 0.0):.2f}` | `{uoa.get('volume', 0):,}` | `{uoa.get('open_interest', 0):,}` | `{uoa.get('vol_oi_ratio', 0.0):.1f}x` | `${uoa.get('dollar_flow', 0.0):,.0f}` | {uoa.get('sentiment', 'Flow Sweep')} |"
                )
            lines.append("")

        # ---------------------------------------------------------
        # 7. RISK CONSIDERATIONS
        # ---------------------------------------------------------
        lines.append("## 6. Execution Rules & Risk Considerations")
        lines.append(
            f"- **Target DTE Window:** `{tactical.get('target_dte', '30-45 DTE')}` for optimal theta acceleration."
        )
        lines.append(
            f"- **Profit Target Rule:** Close position at `{tactical.get('profit_target', '50% of credit')}` captured."
        )
        lines.append(
            f"- **Stop Loss / Defensive Rule:** `{tactical.get('stop_loss_rule', '2x credit')}` or roll out in time upon test."
        )
        for w in warnings:
            lines.append(f"- {w}")

        lines.append("")
        lines.append("---")
        lines.append(
            "*Disclaimer: Macro Flow Stock Navigator is an analytical decision-support tool. Not personalized financial advice. Always verify live order book liquidity and portfolio margin before trading.*"
        )

        return "\n".join(lines)

    @classmethod
    def render_json(
        cls,
        ticker_info: Dict[str, Any],
        indicators: Dict[str, Dict[str, Any]],
        decision: Dict[str, Any],
    ) -> str:
        """
        Builds a structured JSON payload for programmatic consumption.
        """
        system_theme = detect_host_system_theme()
        payload = {
            "metadata": {
                "skill": "macro-flow-stock-navigator",
                "version": "2.0.0",
                "timestamp": datetime.now().isoformat(),
                "system_theme": system_theme,
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
                "unified_synthesis": decision.get("unified_synthesis"),
            },
            "macro_indicators": indicators,
            "options_playbook": decision.get("options_playbook"),
        }
        return json.dumps(payload, indent=2)

    @classmethod
    def render_html(
        cls,
        ticker_info: Dict[str, Any],
        indicators: Dict[str, Dict[str, Any]],
        decision: Dict[str, Any],
        shares_held: int = 0,
        cash_available: float = 0.0,
    ) -> str:
        """
        Builds a standalone, self-contained HTML5 dashboard strictly adhering to DESIGN.md:
        - Typography: DM Sans (UI), Instrument Serif (display headers), IBM Plex Mono (tabular-nums)
        - Flat solid surface tokens (#FAFAF9 / #FFFFFF / #E7E5E4 in Light Mode; #0D0E11 / #16171D / #292A30 in Dark Mode)
        - Single-level bento grid organization with thin 1px solid dividers
        - Three-Icon Theme Selector (#theme-btn-light, #theme-btn-dark, #theme-btn-system) with OS tracking
        - Semantic data visualization palette (#0D9488, #D97706, #4F46E5, #059669, #E11D48)
        - Interactive Relationship Node Map (SVG) & Structural Data Diagram (3D WebGL / software projection fallback)
        - Cross-Asset Concentration & Sensitivity Heatmap Matrix
        - Empirical Data Provenance, Validation Records, and Live SSE / incremental state updates
        """
        system_theme = detect_host_system_theme()
        ticker = ticker_info.get("ticker", "UNKNOWN")
        price = float(ticker_info.get("current_price", 0.0))
        chg = float(ticker_info.get("change_pct", 0.0))
        chg_str = f"+{chg:.2f}%" if chg >= 0 else f"{chg:.2f}%"
        chg_class = "state-positive" if chg >= 0 else "state-critical"
        last_trade_date = ticker_info.get(
            "last_trade_date", datetime.now().strftime("%Y-%m-%d")
        )

        action_badge = decision.get("signal_badge", "NEUTRAL")
        archetype_key = decision.get("archetype_key", "MEGA_CAP_TECH")
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

        price_history = ticker_info.get(
            "price_history", {"dates": [], "prices": [], "ma50": [], "ma200": []}
        )

        # Compute empirical dataset provenance & validation records
        options_source = ticker_info.get("options_data", {}).get(
            "source", "live_yahoo"
        )
        options_source_label = (
            "Yahoo Finance v7 Live Options Feed"
            if options_source == "live_yahoo"
            else "Black-Scholes Calibrated Model (Offline Fallback)"
        )
        history_len = len(price_history.get("dates", []))
        total_calls = len(opt_chain.get("calls", []))
        total_puts = len(opt_chain.get("puts", []))
        valid_indicators_count = sum(
            1
            for ind in indicators.values()
            if len(ind.get("history", [])) >= 5
            and ind.get("trend_signal") != "Insufficient Data"
        )
        num_indicators = len(indicators)

        checksum_payload = f"{ticker}:{price}:{last_trade_date}:{decision.get('alignment_score', 0.0)}:{valid_indicators_count}"
        dataset_checksum = hashlib.sha256(checksum_payload.encode("utf-8")).hexdigest()[
            :16
        ]
        generated_utc = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

        provenance_data = {
            "dataset_id": f"MFSN-{ticker}-{last_trade_date.replace('-', '')}",
            "sha256_prefix": dataset_checksum,
            "generated_utc": generated_utc,
            "last_session_close": last_trade_date,
            "equity_feed": f"Yahoo Finance v8 Chart API ({history_len} trading sessions)",
            "options_feed": options_source_label,
            "macro_ratios_validated": f"{valid_indicators_count} / {len(indicators)} Cross-Asset Pairs Verified",
            "contracts_indexed": f"{total_calls} Calls, {total_puts} Puts ({opt_chain.get('expiration', 'Near-Month')} / {opt_chain.get('dte', 30)} DTE)",
            "system_theme": system_theme,
        }

        # Serialize datasets for JS
        indicators_json = json.dumps(indicators)
        history_json = json.dumps(price_history)
        decision_json = json.dumps(decision)
        ticker_json = json.dumps(ticker_info)
        playbook_json = json.dumps(playbook)
        provenance_json = json.dumps(provenance_data)

        first_ind_key = list(indicators.keys())[0] if indicators else "NDX_SPX"
        first_ind = indicators.get(first_ind_key, {})
        first_name = first_ind.get("display_name", first_ind_key)
        first_ratio = first_ind.get("ratio_tickers", first_ind_key)
        first_val_str = f"{first_ind.get('current_value', 0.0)} ({first_ind.get('ma50_status', 'N/A')})"
        first_pctl_str = f"{first_ind.get('percentile_90d', 50.0):.1f}% ({first_ind.get('trend_signal', 'Neutral')})"
        first_meaning = (
            f"{first_name} ({first_ratio}): {first_ind.get('market_meaning', '')}"
        )
        first_trend = first_ind.get("trend_signal", "Neutral")
        first_status_class = (
            "trend-bullish"
            if "Above" in first_ind.get("ma50_status", "")
            or "Rising" in first_trend
            else (
                "trend-bearish"
                if "Below" in first_ind.get("ma50_status", "")
                or "Falling" in first_trend
                else "trend-neutral"
            )
        )

        # Build Tab 2 Indicator Cells, Tab 3 Sparkline Cells, and Focus Selector Pills
        ind_cards_html = []
        ind_chart_cards_html = []
        macro_pills_html = []
        validation_rows_html = []

        for ind_id, ind in indicators.items():
            name = ind.get("display_name", ind_id)
            ratio = ind.get("ratio_tickers", ind_id)
            val = ind.get("current_value", 0.0)
            ma50_val = ind.get("ma50", 0.0)
            diff_ma50 = ind.get("diff_ma50_pct", 0.0)
            ma_stat = ind.get("ma50_status", "N/A")
            trend = ind.get("trend_signal", "Flat")
            meaning = ind.get("market_meaning", "")
            percentile = float(ind.get("percentile_90d", 50.0))
            slope_pct = float(ind.get("slope_pct", 0.0))
            samples_n = len(ind.get("history", []))

            status_class = (
                "trend-bullish"
                if "Above" in ma_stat or "Rising" in trend
                else (
                    "trend-bearish"
                    if "Below" in ma_stat or "Falling" in trend
                    else "trend-neutral"
                )
            )
            bar_color = (
                "var(--viz-emerald)"
                if status_class == "trend-bullish"
                else (
                    "var(--viz-rose)"
                    if status_class == "trend-bearish"
                    else "var(--viz-teal)"
                )
            )

            ind_cards_html.append(
                f"""
            <div class="bento-pane ind-card" data-trend="{status_class}" data-ind-id="{ind_id}">
                <div class="pane-header">
                    <div>
                        <h3 class="pane-title-sm">{name}</h3>
                        <div class="font-mono text-muted-xs">{ratio}</div>
                    </div>
                    <span class="badge {status_class}">{trend}</span>
                </div>
                <div class="ind-metrics-list">
                    <div class="ind-metric-row">
                        <span class="label">Current Ratio</span>
                        <span class="val font-mono">{val:.4f}</span>
                    </div>
                    <div class="ind-metric-row">
                        <span class="label">50-MA Status</span>
                        <span class="val font-mono">{ma_stat}</span>
                    </div>
                    <div class="ind-metric-row">
                        <span class="label">15d Slope</span>
                        <span class="val font-mono">{slope_pct:+.3f}%</span>
                    </div>
                    <div class="ind-metric-row">
                        <span class="label">90d Percentile</span>
                        <span class="val font-mono">{percentile:.1f}%</span>
                    </div>
                    <div class="progress-track">
                        <div class="progress-bar" style="width: {min(100.0, max(0.0, percentile)):.1f}%; background-color: {bar_color};"></div>
                    </div>
                    <p class="ind-meaning">{meaning}</p>
                </div>
                <div class="pane-footer-row">
                    <span class="font-mono text-muted-xs">n={samples_n}d</span>
                    <button class="mini-inspect-btn" onclick="switchTab('charts'); selectFocusIndicator('{ind_id}');">
                        Inspect Series &rarr;
                    </button>
                </div>
            </div>
            """
            )

            ind_chart_cards_html.append(
                f"""
            <div class="bento-pane ind-chart-card">
                <div class="pane-header">
                    <div>
                        <h4 class="pane-title-sm">{name}</h4>
                        <div class="font-mono text-muted-xs">{ratio}</div>
                    </div>
                    <span class="badge {status_class}">{trend}</span>
                </div>
                <div class="compact-stat-strip font-mono">
                    <span>Val: <b>{val}</b></span>
                    <span>50-MA: <b>{ma50_val}</b> ({diff_ma50:+.2f}%)</span>
                    <span>Pctl: <b>{percentile:.1f}%</b></span>
                </div>
                <div class="chart-container-sm">
                    <canvas id="chart_{ind_id}"></canvas>
                </div>
                <div class="pane-footer-row">
                    <span class="text-muted-xs truncate-text" title="{meaning}">{meaning}</span>
                    <button class="mini-inspect-btn" onclick="selectFocusIndicator('{ind_id}'); document.getElementById('focusVisualizerCard').scrollIntoView({{behavior: 'smooth', block: 'nearest'}});">
                        Focus
                    </button>
                </div>
            </div>
            """
            )

            is_active_pill = "active" if ind_id == first_ind_key else ""
            macro_pills_html.append(
                f"""
            <button class="macro-pill-btn font-mono {is_active_pill}" data-key="{ind_id}" onclick="selectFocusIndicator('{ind_id}')">
                {ratio}
            </button>
            """
            )

            val_badge = "trend-bullish" if samples_n >= 20 else "trend-neutral"
            val_state_label = "VALIDATED" if samples_n >= 20 else "PARTIAL"
            validation_rows_html.append(
                f"""
            <tr>
                <td class="font-mono"><b>{ind_id}</b></td>
                <td>{name}</td>
                <td class="font-mono">{ratio}</td>
                <td class="font-mono">{samples_n} sessions</td>
                <td class="font-mono">{val:.4f}</td>
                <td class="font-mono">{ma50_val:.4f} ({diff_ma50:+.2f}%)</td>
                <td class="font-mono">{percentile:.1f}%</td>
                <td><span class="badge {val_badge}">{val_state_label}</span></td>
            </tr>
            """
            )

        ind_cards_rendered = "\n".join(ind_cards_html)
        ind_chart_cards_rendered = "\n".join(ind_chart_cards_html)
        macro_pill_buttons_rendered = "\n".join(macro_pills_html)
        validation_rows_rendered = "\n".join(validation_rows_html)

        # Covered Call Matrix Rows
        cc_rows_html = []
        for tier_key, tier_title in [
            ("conservative", "Conservative (0.20Δ)"),
            ("balanced", "Balanced (0.30Δ)"),
            ("aggressive", "Aggressive (0.40Δ)"),
        ]:
            c = cc_matrix.get(tier_key, {})
            if c:
                cc_rows_html.append(
                    f"""
                <tr>
                    <td><b>{tier_title}</b></td>
                    <td class="font-mono">${c.get('strike', 0.0):.2f}</td>
                    <td class="font-mono">${c.get('mid', 0.0):.2f}</td>
                    <td class="font-mono">{c.get('delta', 0.0):+.2f}</td>
                    <td class="font-mono">{c.get('theta', 0.0):.3f}</td>
                    <td class="font-mono">+{c.get('otm_pct', 0.0):.1f}%</td>
                    <td class="font-mono state-positive">+{c.get('yield_unassigned', 0.0):.1f}%</td>
                    <td class="font-mono state-nominal">+{c.get('return_called_away', 0.0):.1f}%</td>
                    <td class="font-mono">+{c.get('downside_protection', 0.0):.1f}%</td>
                    <td>
                        <button class="mini-inspect-btn" onclick="loadIntoSimulator('CC', {c.get('strike', 0.0)}, {c.get('mid', 0.0)}, {price})">
                            Simulate
                        </button>
                    </td>
                </tr>
                """
                )
        cc_rows_rendered = "\n".join(cc_rows_html)

        # Cash-Secured Put Matrix Rows
        csp_rows_html = []
        for tier_key, tier_title in [
            ("conservative", "Conservative (0.20Δ)"),
            ("balanced", "Balanced (0.30Δ)"),
            ("aggressive", "Aggressive (0.40Δ)"),
        ]:
            p = csp_matrix.get(tier_key, {})
            if p:
                csp_rows_html.append(
                    f"""
                <tr>
                    <td><b>{tier_title}</b></td>
                    <td class="font-mono">${p.get('strike', 0.0):.2f}</td>
                    <td class="font-mono">${p.get('mid', 0.0):.2f}</td>
                    <td class="font-mono">{p.get('delta', 0.0):+.2f}</td>
                    <td class="font-mono">{p.get('theta', 0.0):.3f}</td>
                    <td class="font-mono">-{p.get('otm_pct', 0.0):.1f}%</td>
                    <td class="font-mono">${p.get('collateral_required', 0.0):,.0f}</td>
                    <td class="font-mono">${p.get('net_cost_basis', 0.0):.2f}</td>
                    <td class="font-mono state-nominal">{p.get('discount_pct', 0.0):.1f}%</td>
                    <td class="font-mono state-positive">+{p.get('annualized_roc', 0.0):.1f}%</td>
                    <td>
                        <button class="mini-inspect-btn" onclick="loadIntoSimulator('CSP', {p.get('strike', 0.0)}, {p.get('mid', 0.0)}, {price})">
                            Simulate
                        </button>
                    </td>
                </tr>
                """
                )
        csp_rows_rendered = "\n".join(csp_rows_html)

        # Unusual Option Activity Rows
        uoa_rows_html = []
        for uoa in uoa_list:
            type_class = (
                "trend-bullish"
                if uoa.get("option_type") == "CALL"
                else "trend-bearish"
            )
            uoa_rows_html.append(
                f"""
            <tr>
                <td><span class="badge {type_class}">{uoa.get('option_type')}</span></td>
                <td class="font-mono">{uoa.get('contract', '')}</td>
                <td class="font-mono">${uoa.get('strike', 0.0):.2f}</td>
                <td class="font-mono">{uoa.get('volume', 0):,}</td>
                <td class="font-mono">{uoa.get('open_interest', 0):,}</td>
                <td class="font-mono state-warning">{uoa.get('vol_oi_ratio', 0.0):.1f}x</td>
                <td class="font-mono state-nominal">${uoa.get('dollar_flow', 0.0):,.0f}</td>
                <td>{uoa.get('sentiment', '')}</td>
            </tr>
            """
            )
        uoa_rows_rendered = (
            "\n".join(uoa_rows_html)
            if uoa_rows_html
            else "<tr><td colspan='8' class='text-muted-center'>No unusual option volume anomalies detected in active session.</td></tr>"
        )

        # Live Option Chain Rows
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
            strike = float(d.get("strike", 0.0))
            bid = float(d.get("bid", 0.0))
            ask = float(d.get("ask", 0.0))
            mid = float(d.get("mid", d.get("lastPrice", 0.0)))
            delta = float(d.get("delta", 0.0))
            theta = float(d.get("theta", 0.0))
            vol = int(d.get("volume", 0))
            oi = int(d.get("openInterest", 0))
            vol_oi = float(d.get("vol_oi_ratio", 0.0))
            iv = float(d.get("impliedVolatility", 0.0))
            itm = bool(d.get("inTheMoney", False))
            itm_str = "ITM" if itm else "OTM"
            itm_badge = (
                "trend-bearish"
                if (itm and t == "PUT") or (not itm and t == "CALL")
                else "trend-bullish"
            )
            t_badge = "trend-bullish" if t == "CALL" else "trend-bearish"
            near_pct = abs((strike - price) / price) * 100.0 if price > 0 else 0.0
            near_class = "chain-row-ntm" if near_pct <= 10.0 else ""
            strategy_mode = "CC" if t == "CALL" else "CSP"
            vol_oi_class = "state-warning" if vol_oi >= 1.5 else ""

            chain_rows_html.append(
                f"""
            <tr class="chain-row {near_class}" data-type="{t}" data-near="{'true' if near_pct <= 10.0 else 'false'}">
                <td><span class="badge {t_badge}">{t}</span></td>
                <td class="font-mono"><b>${strike:.2f}</b></td>
                <td class="font-mono">${bid:.2f}</td>
                <td class="font-mono">${ask:.2f}</td>
                <td class="font-mono state-nominal"><b>${mid:.2f}</b></td>
                <td class="font-mono">{delta:+.2f}</td>
                <td class="font-mono">{theta:.3f}</td>
                <td class="font-mono">{vol:,}</td>
                <td class="font-mono">{oi:,}</td>
                <td class="font-mono {vol_oi_class}">{vol_oi:.1f}x</td>
                <td class="font-mono">{iv:.1f}%</td>
                <td><span class="badge {itm_badge}">{itm_str}</span></td>
                <td>
                    <button class="mini-inspect-btn" onclick="loadIntoSimulator('{strategy_mode}', {strike}, {mid}, {price})">
                        Simulate
                    </button>
                </td>
            </tr>
            """
            )
        chain_rows_rendered = "\n".join(chain_rows_html)

        # Default simulator initial strike and premium
        init_cc = cc_matrix.get("balanced", {}) or cc_matrix.get("conservative", {})
        init_strike = float(init_cc.get("strike", round(price * 1.05, 1)))
        init_premium = float(init_cc.get("mid", round(price * 0.025, 2)))

        signal_badge_class = (
            "badge-signal-buy"
            if "BUY" in action_badge or "ACCUMULATE" in action_badge
            else (
                "badge-signal-sell"
                if "SELL" in action_badge or "REDUCE" in action_badge
                else "badge-signal-neutral"
            )
        )
        iv_rv_spread_val = float(opt_analytics.get("iv_rv_spread", 0.0))
        iv_rv_class = "state-positive" if iv_rv_spread_val >= 0 else "state-warning"

        tailwinds_html = (
            "".join(
                [
                    f'<div class="force-item"><span class="force-tag font-mono state-positive">{f["ratio"]}</span><div><div class="force-title">{f["indicator"]} <span class="font-mono text-muted-xs">({f["trend"]}, {f.get("impact_score", 0.0):+.2f})</span></div><div class="force-desc">{f["meaning"]}</div></div></div>'
                    for f in favorable
                ]
            )
            if favorable
            else '<div class="text-muted-xs">No dominant macro tailwinds active in current session.</div>'
        )

        headwinds_html = (
            "".join(
                [
                    f'<div class="force-item"><span class="force-tag font-mono state-critical">{h["ratio"]}</span><div><div class="force-title">{h["indicator"]} <span class="font-mono text-muted-xs">({h["trend"]}, {h.get("impact_score", 0.0):+.2f})</span></div><div class="force-desc">{h["meaning"]}</div></div></div>'
                    for h in hostile
                ]
            )
            if hostile
            else '<div class="text-muted-xs">No major macro headwinds active in current session.</div>'
        )

        warnings_html = "".join(
            [
                f'<div class="rule-row"><span class="font-mono state-warning">[RISK]</span><span>{w}</span></div>'
                for w in warnings
            ]
        )

        # Extract Executive Finding Synthesis
        synthesis = decision.get("unified_synthesis", {})
        traffic_light = synthesis.get("traffic_light", "YELLOW LIGHT")
        traffic_color = synthesis.get("traffic_color", "#D97706")
        composite_score = float(synthesis.get("composite_score", 0.0))
        direction_title = synthesis.get("direction_title", "Neutral / Sideways")
        verdict_headline = synthesis.get("verdict_headline", "Market conditions are balanced.")
        pillars = synthesis.get("pillars", {})
        p1 = pillars.get("real_economy", {})
        p2 = pillars.get("borrowing_health", {})
        p3 = pillars.get("crowd_mood", {})
        p4 = pillars.get("smart_money", {})
        action_data = synthesis.get("plain_dollar_action", {})
        action_headline = action_data.get("headline", "Disciplined Positioning")
        action_directive = action_data.get("directive", "Maintain disciplined posture")
        action_cash = action_data.get("cash_collected_dollars", 0)
        action_rate_val = action_data.get("rate_val", 0.0)
        action_rate_label = action_data.get("rate_label", "Annualized Return")
        action_buffer_val = action_data.get("buffer_val", 0.0)
        action_buffer_label = action_data.get("buffer_label", "Buffer")
        action_summary = action_data.get("summary", "")

        # Options Microstructure & Practitioner Fields
        opt_data = ticker_info.get("options_data", {})
        net_gex_str = opt_data.get("net_gex_formatted", "$0M")
        gamma_flip_str = f"${opt_data.get('gamma_flip_strike', price):.2f}"
        gamma_regime_str = opt_data.get("gamma_regime", "NEUTRAL")
        skew_25d_str = f"{opt_data.get('skew_25d', 2.0):+.1f}%"
        skew_signal_str = opt_data.get("skew_signal", "Balanced")
        lottery_ratio_str = f"{opt_data.get('lottery_call_ratio', 10.0):.1f}%"
        lottery_signal_str = opt_data.get("lottery_call_signal", "Normal Flow")
        short_float_str = f"{ticker_info.get('short_float_pct', 2.0):.2f}%"
        days_to_cover_str = f"{ticker_info.get('days_to_cover', 2.5):.1f}d"
        dark_pool_str = f"{ticker_info.get('dark_pool_ratio_pct', 43.0):.1f}%"
        moc_imbalance_str = ticker_info.get("moc_imbalance", "Balanced")

        html_doc = f"""<!DOCTYPE html>
<html lang="en" data-theme="{system_theme}" data-theme-mode="system">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Macro Flow Stock Navigator interactive cross-asset regime, options volatility, and structural network dashboard for {ticker}.">
    <title>Macro Flow Stock Navigator: {ticker}</title>
    <!-- Typography per DESIGN.md §1: Instrument Serif, DM Sans, IBM Plex Mono -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400..700;1,9..40,400..700&family=IBM+Plex+Mono:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
    <!-- Optional Chart.js with Zero-Dependency Native Canvas Fallback -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
        /* ============================================================================
           DESIGN.md §1, §3, §5 Tokens: Light Mode & Dark Mode Exact Specifications
           ============================================================================ */
        :root,
        [data-theme="light"] {{
            --bg-body: #FAFAF9;
            --bg-surface: #FFFFFF;
            --bg-subtle: #F5F5F4;
            --border-color: #E7E5E4;
            --text-primary: #1C1917;
            --text-secondary: #787774;
            --grid-line: #E7E5E4;

            /* Semantic Data Visualization Palette (DESIGN.md §5) */
            --viz-teal: #0D9488;
            --viz-amber: #D97706;
            --viz-indigo: #4F46E5;
            --viz-emerald: #059669;
            --viz-rose: #E11D48;

            /* Typography Hierarchy (DESIGN.md §1) */
            --font-sans: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-serif: 'Instrument Serif', Georgia, serif;
            --font-mono: 'IBM Plex Mono', monospace;
            --radius-pane: 6px;
        }}

        [data-theme="dark"] {{
            --bg-body: #0D0E11;
            --bg-surface: #16171D;
            --bg-subtle: #1D1E26;
            --border-color: #292A30;
            --text-primary: #ECE8E2;
            --text-secondary: #9A9895;
            --grid-line: #292A30;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background-color: var(--bg-body);
            color: var(--text-primary);
            font-family: var(--font-sans);
            font-size: 13.5px;
            line-height: 1.5;
            padding-bottom: 48px;
            -webkit-font-smoothing: antialiased;
        }}

        .font-mono {{
            font-family: var(--font-mono);
            font-variant-numeric: tabular-nums;
        }}

        .font-serif {{
            font-family: var(--font-serif);
        }}

        /* Semantic Status Signals (DESIGN.md §1 & §5) */
        .state-positive {{ color: var(--viz-emerald); }}
        .state-warning {{ color: var(--viz-amber); }}
        .state-critical {{ color: var(--viz-rose); }}
        .state-nominal {{ color: var(--viz-teal); }}
        .state-comparison {{ color: var(--viz-indigo); }}

        .text-muted-xs {{
            font-size: 11.5px;
            color: var(--text-secondary);
        }}

        .text-muted-center {{
            text-align: center;
            color: var(--text-secondary);
            padding: 18px;
        }}

        .truncate-text {{
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 220px;
        }}

        /* ============================================================================
           Top Navigation Header & Three-Icon Theme Selector (DESIGN.md §3)
           ============================================================================ */
        header {{
            background-color: var(--bg-surface);
            border-bottom: 1px solid var(--border-color);
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .brand {{
            display: flex;
            align-items: baseline;
            gap: 14px;
            flex-wrap: wrap;
        }}

        .brand-title {{
            font-family: var(--font-serif);
            font-size: 24px;
            font-weight: 400;
            letter-spacing: -0.01em;
            color: var(--text-primary);
            line-height: 1.1;
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

        .telemetry-status-pill {{
            font-family: var(--font-mono);
            font-variant-numeric: tabular-nums;
            font-size: 11px;
            padding: 5px 10px;
            border-radius: var(--radius-pane);
            background-color: var(--bg-body);
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            display: inline-flex;
            align-items: center;
            gap: 7px;
        }}

        .status-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background-color: var(--viz-emerald);
            display: inline-block;
        }}

        /* Three-Icon Segmented Theme Switcher (DESIGN.md §3) */
        .theme-segmented-control {{
            display: inline-flex;
            align-items: center;
            background-color: var(--bg-body);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-pane);
            padding: 2px;
            gap: 2px;
        }}

        .theme-icon-btn {{
            background: transparent;
            border: 1px solid transparent;
            color: var(--text-secondary);
            width: 30px;
            height: 28px;
            border-radius: 4px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease;
        }}

        .theme-icon-btn:hover {{
            color: var(--text-primary);
        }}

        .theme-icon-btn.active {{
            background-color: var(--bg-surface);
            color: var(--viz-teal);
            border-color: var(--border-color);
        }}

        .theme-icon-btn svg {{
            width: 15px;
            height: 15px;
            stroke: currentColor;
            fill: none;
            stroke-width: 1.8;
            stroke-linecap: round;
            stroke-linejoin: round;
        }}

        /* ============================================================================
           Single-Level Bento Container Layout (DESIGN.md §1 & §4)
           ============================================================================ */
        .container {{
            max-width: 1380px;
            margin: 0 auto;
            padding: 20px 24px;
        }}

        /* Executive Bento Strip */
        .executive-bento {{
            background-color: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-pane);
            display: grid;
            grid-template-columns: 1.3fr repeat(5, 1fr);
            margin-bottom: 18px;
            overflow: hidden;
        }}

        .exec-cell {{
            padding: 14px 16px;
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 4px;
        }}

        .exec-cell:last-child {{
            border-right: none;
        }}

        .ticker-profile {{
            display: flex;
            align-items: baseline;
            gap: 10px;
            flex-wrap: wrap;
        }}

        .ticker-symbol {{
            font-size: 24px;
            font-weight: 700;
            letter-spacing: -0.02em;
        }}

        .ticker-price {{
            font-size: 20px;
            font-weight: 600;
        }}

        .ticker-change {{
            font-size: 12.5px;
            font-weight: 600;
        }}

        .cell-label {{
            font-size: 11px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 4px;
        }}

        .cell-value {{
            font-size: 14px;
            font-weight: 600;
            color: var(--text-primary);
        }}

        /* High-Signal Badges (DESIGN.md §1) */
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-family: var(--font-mono);
            font-variant-numeric: tabular-nums;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            border: 1px solid var(--border-color);
            background-color: var(--bg-body);
            color: var(--text-secondary);
        }}

        .badge-signal-buy,
        .trend-bullish {{
            color: var(--viz-emerald);
            border-color: var(--viz-emerald);
            background-color: rgba(5, 150, 105, 0.08);
        }}

        .badge-signal-sell,
        .trend-bearish {{
            color: var(--viz-rose);
            border-color: var(--viz-rose);
            background-color: rgba(225, 29, 72, 0.08);
        }}

        .badge-signal-neutral {{
            color: var(--viz-amber);
            border-color: var(--viz-amber);
            background-color: rgba(217, 119, 6, 0.08);
        }}

        .trend-neutral {{
            color: var(--text-secondary);
            border-color: var(--border-color);
            background-color: var(--bg-body);
        }}

        /* Navigation Tabs */
        .tab-bar {{
            display: flex;
            gap: 4px;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 18px;
            overflow-x: auto;
        }}

        .tab-btn {{
            background: none;
            border: none;
            border-bottom: 2px solid transparent;
            padding: 10px 16px;
            color: var(--text-secondary);
            font-family: var(--font-sans);
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            white-space: nowrap;
        }}

        .tab-btn:hover {{
            color: var(--text-primary);
        }}

        .tab-btn.active {{
            color: var(--viz-teal);
            border-bottom-color: var(--viz-teal);
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        /* Single-Level Bento Grids & Flat Solid Panes */
        .grid-2 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
            gap: 16px;
            margin-bottom: 16px;
        }}

        .grid-3 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
            margin-bottom: 16px;
        }}

        .grid-4 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(270px, 1fr));
            gap: 16px;
            margin-bottom: 16px;
        }}

        .bento-pane,
        .card {{
            background-color: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-pane);
            padding: 18px;
            margin-bottom: 16px;
        }}

        .grid-2 > .bento-pane,
        .grid-2 > .card,
        .grid-3 > .bento-pane,
        .grid-4 > .bento-pane {{
            margin-bottom: 0;
        }}

        .pane-header,
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 12px;
            margin-bottom: 14px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border-color);
        }}

        .pane-title,
        .card-title {{
            font-family: var(--font-serif);
            font-size: 20px;
            font-weight: 400;
            letter-spacing: -0.01em;
            color: var(--text-primary);
            line-height: 1.2;
        }}

        .pane-title-sm {{
            font-family: var(--font-sans);
            font-size: 14px;
            font-weight: 600;
            color: var(--text-primary);
        }}

        .pane-desc,
        .card-desc {{
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 2px;
        }}

        /* Partitioned Flat Stat Dividers (Replaces nested card-in-card) */
        .partition-strip {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            border-top: 1px solid var(--border-color);
            border-bottom: 1px solid var(--border-color);
            margin: 14px -18px;
        }}

        .partition-strip.bottom-flush {{
            margin-bottom: -18px;
            border-bottom: none;
        }}

        .partition-cell {{
            padding: 12px 18px;
            border-right: 1px solid var(--border-color);
        }}

        .partition-cell:last-child {{
            border-right: none;
        }}

        .partition-cell .label {{
            font-size: 11px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            font-weight: 600;
        }}

        .partition-cell .val {{
            font-size: 14px;
            font-weight: 600;
            color: var(--text-primary);
            margin-top: 3px;
        }}

        .regime-callout {{
            padding: 12px 0;
            border-top: 1px solid var(--border-color);
            margin-top: 10px;
        }}

        /* Indicator Cards (Tab 2 & Tab 3) */
        .ind-card {{
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: 10px;
        }}

        .ind-metrics-list {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}

        .ind-metric-row {{
            display: flex;
            justify-content: space-between;
            font-size: 12px;
        }}

        .ind-metric-row .label {{
            color: var(--text-secondary);
        }}

        .ind-meaning {{
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 6px;
            line-height: 1.4;
        }}

        .pane-footer-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 10px;
            margin-top: 8px;
            border-top: 1px solid var(--border-color);
        }}

        .compact-stat-strip {{
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            color: var(--text-secondary);
            padding-bottom: 8px;
            margin-bottom: 8px;
            border-bottom: 1px solid var(--border-color);
        }}

        .progress-track {{
            width: 100%;
            height: 4px;
            background-color: var(--border-color);
            border-radius: 2px;
            overflow: hidden;
            margin: 4px 0;
        }}

        .progress-bar {{
            height: 100%;
            background-color: var(--viz-teal);
        }}

        /* Tables (DESIGN.md §4: IBM Plex Mono & tabular-nums with thin horizontal dividers) */
        .table-wrap {{
            overflow-x: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 12.5px;
            font-variant-numeric: tabular-nums;
        }}

        th {{
            background-color: var(--bg-body);
            padding: 9px 12px;
            font-size: 11px;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            border-top: 1px solid var(--border-color);
            border-bottom: 1px solid var(--border-color);
            white-space: nowrap;
        }}

        td {{
            padding: 10px 12px;
            border-bottom: 1px solid var(--border-color);
            white-space: nowrap;
        }}

        tr:hover td {{
            background-color: var(--bg-subtle);
        }}

        /* Forces & Rules Lists */
        .force-section-title {{
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
            color: var(--text-secondary);
        }}

        .force-item {{
            display: flex;
            align-items: flex-start;
            gap: 12px;
            padding: 8px 0;
            border-bottom: 1px solid var(--border-color);
            font-size: 12.5px;
        }}

        .force-item:last-child {{
            border-bottom: none;
        }}

        .force-tag {{
            font-weight: 600;
            min-width: 82px;
            font-size: 11.5px;
        }}

        .force-title {{
            font-weight: 600;
            color: var(--text-primary);
        }}

        .force-desc {{
            color: var(--text-secondary);
            font-size: 12px;
        }}

        .rule-row {{
            display: flex;
            gap: 10px;
            padding: 7px 0;
            border-bottom: 1px solid var(--border-color);
            font-size: 12.5px;
            color: var(--text-secondary);
        }}

        .rule-row:last-child {{
            border-bottom: none;
        }}

        /* Interactive Controls & Buttons */
        .filter-group,
        .macro-selector-bar,
        .strategy-mode-bar {{
            display: flex;
            gap: 6px;
            margin-bottom: 14px;
            flex-wrap: wrap;
        }}

        .filter-btn,
        .macro-pill-btn,
        .strategy-mode-btn {{
            background-color: var(--bg-surface);
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            padding: 6px 12px;
            border-radius: var(--radius-pane);
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: border-color 0.15s ease, color 0.15s ease, background-color 0.15s ease;
        }}

        .filter-btn:hover,
        .macro-pill-btn:hover,
        .strategy-mode-btn:hover {{
            color: var(--text-primary);
            border-color: var(--viz-teal);
        }}

        .filter-btn.active,
        .macro-pill-btn.active,
        .strategy-mode-btn.active {{
            background-color: var(--viz-teal);
            color: #FFFFFF;
            border-color: var(--viz-teal);
        }}

        .mini-inspect-btn {{
            background-color: transparent;
            border: 1px solid var(--border-color);
            color: var(--viz-teal);
            padding: 3px 9px;
            border-radius: 4px;
            font-family: var(--font-mono);
            font-size: 11px;
            font-weight: 500;
            cursor: pointer;
            white-space: nowrap;
        }}

        .mini-inspect-btn:hover {{
            background-color: var(--viz-teal);
            color: #FFFFFF;
            border-color: var(--viz-teal);
        }}

        .search-input {{
            background-color: var(--bg-body);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 6px 11px;
            border-radius: var(--radius-pane);
            font-size: 12.5px;
            outline: none;
        }}

        .search-input:focus {{
            border-color: var(--viz-teal);
        }}

        .slider-control {{
            display: flex;
            align-items: center;
            gap: 14px;
            margin: 14px 0;
            padding: 10px 0;
            border-top: 1px solid var(--border-color);
            border-bottom: 1px solid var(--border-color);
        }}

        .slider-control input[type="range"] {{
            flex-grow: 1;
            accent-color: var(--viz-teal);
            height: 5px;
        }}

        /* Chart & 3D/Network Viewports (DESIGN.md §1, §4, §5: Uncluttered solid surface backgrounds) */
        .chart-container {{
            position: relative;
            height: 300px;
            width: 100%;
            background: transparent;
        }}

        .chart-container-sm {{
            position: relative;
            height: 165px;
            width: 100%;
            background: transparent;
        }}

        .chart-container canvas,
        .chart-container-sm canvas {{
            display: block;
            width: 100%;
            height: 100%;
        }}

        .spatial-viewport {{
            position: relative;
            height: 340px;
            width: 100%;
            background-color: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-pane);
            overflow: hidden;
            user-select: none;
        }}

        .spatial-viewport svg,
        .spatial-viewport canvas {{
            display: block;
            width: 100%;
            height: 100%;
            cursor: grab;
        }}

        .spatial-viewport svg:active,
        .spatial-viewport canvas:active {{
            cursor: grabbing;
        }}

        .viewport-overlay-bar {{
            position: absolute;
            top: 10px;
            right: 10px;
            display: flex;
            gap: 6px;
            z-index: 5;
        }}

        .viewport-legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 14px;
            margin-top: 10px;
            font-size: 11.5px;
            color: var(--text-secondary);
        }}

        .legend-item {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}

        .legend-swatch {{
            width: 9px;
            height: 9px;
            border-radius: 2px;
            display: inline-block;
        }}

        /* Heatmap Matrix (DESIGN.md §5: Smooth transition Surface -> #0D9488 -> #4F46E5 -> #E11D48) */
        .heatmap-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
            gap: 6px;
            margin-top: 10px;
        }}

        .heatmap-cell {{
            border: 1px solid var(--border-color);
            border-radius: 4px;
            padding: 10px 8px;
            text-align: center;
            cursor: pointer;
            transition: transform 0.12s ease;
        }}

        .heatmap-cell:hover {{
            transform: translateY(-1px);
        }}

        .heatmap-gradient-bar {{
            height: 8px;
            border-radius: 4px;
            border: 1px solid var(--border-color);
            background: linear-gradient(90deg, var(--bg-surface) 0%, #0D9488 35%, #4F46E5 70%, #E11D48 100%);
            width: 180px;
            display: inline-block;
            vertical-align: middle;
            margin: 0 8px;
        }}


        footer {{
            margin-top: 36px;
            text-align: center;
            font-size: 12px;
            color: var(--text-secondary);
            padding: 18px 24px;
            border-top: 1px solid var(--border-color);
        }}

        /* Executive Finding Bento Pane (DESIGN.md §1 & §4) */
        .unified-pane {{
            background-color: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-pane);
            padding: 18px 20px;
            margin-bottom: 18px;
        }}

        .traffic-light-pill {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            border: 1px solid var(--border-color);
            background-color: var(--bg-body);
        }}

        .traffic-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
        }}

        .unified-headline {{
            font-family: var(--font-serif);
            font-size: 19px;
            line-height: 1.35;
            color: var(--text-primary);
            margin: 6px 0 16px 0;
        }}

        .summary-pillars-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-bottom: 14px;
        }}

        .summary-pillar-cell {{
            background-color: var(--bg-body);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-pane);
            padding: 12px 14px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}

        .summary-pillar-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 6px;
        }}

        .summary-pillar-name {{
            font-size: 11px;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        .summary-pillar-status {{
            font-family: var(--font-mono);
            font-size: 11px;
            font-weight: 700;
        }}

        .summary-pillar-detail {{
            font-size: 12px;
            line-height: 1.4;
            color: var(--text-primary);
        }}

        .action-strip {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            border: 1px solid var(--border-color);
            border-left: 4px solid var(--viz-teal);
            border-radius: var(--radius-pane);
            background-color: var(--bg-body);
            overflow: hidden;
            margin-bottom: 8px;
        }}

        .action-cell {{
            padding: 10px 14px;
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            gap: 3px;
        }}

        .action-cell:last-child {{
            border-right: none;
        }}

        .action-cell-label {{
            font-size: 10px;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        .action-cell-val {{
            font-size: 13.5px;
            font-weight: 700;
            color: var(--text-primary);
        }}

        .action-takeaway {{
            font-size: 11.5px;
            color: var(--text-secondary);
            padding: 0 4px;
        }}

        @media (max-width: 960px) {{
            .summary-pillars-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .action-strip {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .executive-bento {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .exec-cell {{
                border-bottom: 1px solid var(--border-color);
            }}
            .grid-2 {{
                grid-template-columns: 1fr;
            }}
            .heatmap-grid {{
                grid-template-columns: repeat(4, 1fr);
            }}
        }}
    </style>
</head>
<body>

    <header>
        <div class="brand">
            <h1 class="brand-title">Macro Flow Stock Navigator</h1>
        </div>
        <div class="header-actions">
            <div class="telemetry-status-pill" id="liveTelemetryPill">
                <span class="status-dot" id="sseStatusDot"></span>
                <span id="sessionDateBanner">Session: {last_trade_date}</span>
            </div>
            <!-- Three-Icon Theme Selector per DESIGN.md §3 -->
            <div class="theme-segmented-control" role="group" aria-label="Theme Mode Selector">
                <button id="theme-btn-light" class="theme-icon-btn" type="button" title="Light Theme" aria-label="Light Theme" data-theme-mode="light" aria-pressed="false" onclick="setThemeMode('light')">
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                        <circle cx="12" cy="12" r="4"></circle>
                        <line x1="12" y1="2" x2="12" y2="4"></line>
                        <line x1="12" y1="20" x2="12" y2="22"></line>
                        <line x1="4.93" y1="4.93" x2="6.34" y2="6.34"></line>
                        <line x1="17.66" y1="17.66" x2="19.07" y2="19.07"></line>
                        <line x1="2" y1="12" x2="4" y2="12"></line>
                        <line x1="20" y1="12" x2="22" y2="12"></line>
                        <line x1="4.93" y1="19.07" x2="6.34" y2="17.66"></line>
                        <line x1="17.66" y1="6.34" x2="19.07" y2="4.93"></line>
                    </svg>
                </button>
                <button id="theme-btn-dark" class="theme-icon-btn" type="button" title="Dark Theme" aria-label="Dark Theme" data-theme-mode="dark" aria-pressed="false" onclick="setThemeMode('dark')">
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                    </svg>
                </button>
                <button id="theme-btn-system" class="theme-icon-btn active" type="button" title="System Theme" aria-label="System Theme" data-theme-mode="system" aria-pressed="true" onclick="setThemeMode('system')">
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                        <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                        <line x1="8" y1="21" x2="16" y2="21"></line>
                        <line x1="12" y1="17" x2="12" y2="21"></line>
                    </svg>
                </button>
            </div>
        </div>
    </header>

    <main class="container">

        <!-- Single-Level Executive Bento Strip -->
        <section class="executive-bento" aria-label="Executive Ticker Summary">
            <div class="exec-cell">
                <div class="ticker-profile">
                    <span id="execTickerSymbol" class="ticker-symbol font-mono">{ticker}</span>
                    <span id="execTickerPrice" class="ticker-price font-mono">${price:.2f}</span>
                    <span id="execTickerChange" class="ticker-change {chg_class} font-mono">{chg_str}</span>
                </div>
            </div>
            <div class="exec-cell">
                <span class="cell-label">Macro Signal</span>
                <span class="cell-value">
                    <span id="execSignalBadge" class="badge {signal_badge_class}">{action_badge}</span>
                </span>
            </div>
            <div class="exec-cell">
                <span class="cell-label">Stock Archetype</span>
                <span id="execArchetypeName" class="cell-value">{archetype_name}</span>
            </div>
            <div class="exec-cell">
                <span class="cell-label">Macro Alignment</span>
                <span id="execAlignmentScore" class="cell-value font-mono">{decision.get('alignment_score', 0.0):+.1f} / 100</span>
            </div>
            <div class="exec-cell">
                <span class="cell-label">Macro Regime</span>
                <span id="execRegimeName" class="cell-value">{macro_regime.get('name', 'Balanced Rotation')}</span>
            </div>
            <div class="exec-cell">
                <span class="cell-label">IV vs 30d RV</span>
                <span id="execIvRvSpread" class="cell-value font-mono {iv_rv_class}">{iv_rv_spread_val:+.1f}%</span>
            </div>
        </section>

        <!-- Single-Level Bento Section: Executive Finding -->
        <section class="unified-pane" aria-label="Executive Finding">
            <div class="pane-header">
                <div>
                    <h2 class="pane-title">Executive Finding</h2>
                </div>
                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                    <span class="traffic-light-pill font-mono" style="color: {traffic_color}; border-color: {traffic_color};">
                        <span class="traffic-dot" style="background-color: {traffic_color};"></span>
                        {traffic_light} &bull; {direction_title}
                    </span>
                    <span class="badge font-mono">{composite_score:+.1f} / 100</span>
                </div>
            </div>
            <div class="unified-headline font-serif">
                "{verdict_headline}"
            </div>
            <div class="summary-pillars-grid">
                <div class="summary-pillar-cell">
                    <div class="summary-pillar-header">
                        <span class="summary-pillar-name">Real Economy</span>
                        <span class="summary-pillar-status font-mono" style="color: var(--viz-teal);">{p1.get('status', 'Steady')}</span>
                    </div>
                    <div class="summary-pillar-detail">{p1.get('explanation', '')}</div>
                </div>
                <div class="summary-pillar-cell">
                    <div class="summary-pillar-header">
                        <span class="summary-pillar-name">Credit Health</span>
                        <span class="summary-pillar-status font-mono" style="color: var(--viz-indigo);">{p2.get('status', 'Normal')}</span>
                    </div>
                    <div class="summary-pillar-detail">{p2.get('explanation', '')}</div>
                </div>
                <div class="summary-pillar-cell">
                    <div class="summary-pillar-header">
                        <span class="summary-pillar-name">Market Sentiment</span>
                        <span class="summary-pillar-status font-mono" style="color: var(--viz-amber);">{p3.get('status', 'Calm')}</span>
                    </div>
                    <div class="summary-pillar-detail">{p3.get('explanation', '')}</div>
                </div>
                <div class="summary-pillar-cell">
                    <div class="summary-pillar-header">
                        <span class="summary-pillar-name">Institutional Floor</span>
                        <span class="summary-pillar-status font-mono" style="color: var(--viz-emerald);">{p4.get('safety_floor', '$0.00')}</span>
                    </div>
                    <div class="summary-pillar-detail">{p4.get('explanation', '')}</div>
                </div>
            </div>
            <div class="action-strip">
                <div class="action-cell">
                    <div class="action-cell-label">Action Directive</div>
                    <div class="action-cell-val font-mono">{action_directive}</div>
                </div>
                <div class="action-cell">
                    <div class="action-cell-label">Upfront Cash Income</div>
                    <div class="action-cell-val font-mono state-positive">+${action_cash:,}</div>
                </div>
                <div class="action-cell">
                    <div class="action-cell-label">{action_rate_label}</div>
                    <div class="action-cell-val font-mono">+{action_rate_val:.1f}%</div>
                </div>
                <div class="action-cell">
                    <div class="action-cell-label">{action_buffer_label}</div>
                    <div class="action-cell-val font-mono">{action_buffer_val:+.1f}%</div>
                </div>
            </div>
            <div class="action-takeaway text-muted-xs font-mono">{action_summary}</div>
        </section>

        <!-- Navigation Tabs -->
        <nav class="tab-bar" aria-label="Dashboard Sections">
            <button class="tab-btn active" onclick="switchTab('overview')">Executive Overview &amp; Topology</button>
            <button class="tab-btn" onclick="switchTab('indicators')">Macro Indicators ({num_indicators})</button>
            <button class="tab-btn" onclick="switchTab('charts')">Trend &amp; Factor Charts</button>
            <button class="tab-btn" onclick="switchTab('playbook')">Options Playbook &amp; Simulator</button>
            <button class="tab-btn" onclick="switchTab('provenance')">Data Provenance &amp; Validation</button>
        </nav>

        <!-- ========================================================================
             TAB 1: EXECUTIVE OVERVIEW & 3D / NETWORK TOPOLOGY
             ======================================================================== -->
        <section id="tab-overview" class="tab-content active">
            <div class="grid-2">
                <!-- Archetype & Regime Alignment Pane -->
                <div class="bento-pane">
                    <div class="pane-header">
                        <div>
                            <h2 class="pane-title">Archetype Alignment Matrix</h2>
                            <div class="pane-desc">{archetype_name} ({archetype_key})</div>
                        </div>
                        <span class="badge font-mono">Conviction: {decision.get('conviction', 'Moderate')}</span>
                    </div>
                    <p style="color: var(--text-secondary); font-size: 13px; margin-bottom: 10px;">
                        {archetype_desc}
                    </p>
                    <div class="regime-callout">
                        <div style="font-weight: 600; font-size: 12.5px; margin-bottom: 3px;">
                            Regime Classification: <span class="state-nominal">{macro_regime.get('name', 'Balanced Rotation')}</span>
                        </div>
                        <div style="font-size: 12px; color: var(--text-secondary);">{macro_regime.get('summary', '')}</div>
                    </div>
                    <div class="partition-strip bottom-flush">
                        <div class="partition-cell">
                            <div class="label">50-Day MA</div>
                            <div class="val font-mono">${ticker_info.get('ma50', 0.0):.2f} ({ticker_info.get('diff_ma50_pct', 0.0):+.2f}%)</div>
                        </div>
                        <div class="partition-cell">
                            <div class="label">200-Day MA</div>
                            <div class="val font-mono">${ticker_info.get('ma200', 0.0):.2f} ({ticker_info.get('diff_ma200_pct', 0.0):+.2f}%)</div>
                        </div>
                        <div class="partition-cell">
                            <div class="label">Beta (vs SPY)</div>
                            <div class="val font-mono">{ticker_info.get('beta', 1.0):.2f}</div>
                        </div>
                        <div class="partition-cell">
                            <div class="label">30d Realized Vol</div>
                            <div class="val font-mono">{ticker_info.get('historical_vol_30d', 0.0):.1f}%</div>
                        </div>
                    </div>
                </div>

                <!-- Tailwinds vs Headwinds Pane -->
                <div class="bento-pane">
                    <div class="pane-header">
                        <div>
                            <h2 class="pane-title">Macro Drivers &amp; Sensitivity Forces</h2>
                            <div class="pane-desc">Weighted cross-asset tailwinds and headwinds acting on {ticker}</div>
                        </div>
                        <span class="font-mono text-muted-xs">{decision.get('alignment_gauge', '')}</span>
                    </div>
                    <div style="margin-bottom: 14px;">
                        <div class="force-section-title state-positive">Active Macro Tailwinds</div>
                        <div id="tailwindsList">{tailwinds_html}</div>
                    </div>
                    <div style="padding-top: 12px; border-top: 1px solid var(--border-color);">
                        <div class="force-section-title state-critical">Active Macro Headwinds</div>
                        <div id="headwindsList">{headwinds_html}</div>
                    </div>
                </div>
            </div>

            <!-- 3D and Network Visualizations per DESIGN.md §4 & §5 -->
            <div class="grid-2">
                <!-- Interactive Relationship Node Map (SVG Network Graph) -->
                <div class="bento-pane">
                    <div class="pane-header">
                        <div>
                            <h2 class="pane-title">Interactive Relationship Node Map</h2>
                            <div class="pane-desc">Cross-asset factor transmission network &amp; archetype coupling (drag to pan, scroll to zoom)</div>
                        </div>
                        <span id="nodeMapStatus" class="badge font-mono">12 Nodes &bull; Deterministic</span>
                    </div>
                    <div class="spatial-viewport" id="relationshipNodeMapViewport">
                        <div class="viewport-overlay-bar">
                            <button type="button" class="mini-inspect-btn" onclick="zoomNodeMap(1.15)">+</button>
                            <button type="button" class="mini-inspect-btn" onclick="zoomNodeMap(0.87)">&minus;</button>
                            <button type="button" class="mini-inspect-btn" onclick="resetNodeMapTransform()">Reset</button>
                        </div>
                        <svg id="relationshipNodeMapSvg" viewBox="0 0 640 340" aria-label="Interactive Relationship Node Map"></svg>
                    </div>
                    <div class="viewport-legend">
                        <span class="legend-item"><span class="legend-swatch" style="background:#0D9488;"></span>Target &amp; Nominal Nodes (#0D9488)</span>
                        <span class="legend-item"><span class="legend-swatch" style="background:#4F46E5;"></span>Archetype / Regime Hub (#4F46E5)</span>
                        <span class="legend-item"><span class="legend-swatch" style="background:#059669;"></span>Validated Tailwind (#059669)</span>
                        <span class="legend-item"><span class="legend-swatch" style="background:#E11D48;"></span>Critical Headwind (#E11D48)</span>
                        <span class="legend-item"><span class="legend-swatch" style="background:#D97706;"></span>Options Overlay (#D97706)</span>
                    </div>
                </div>

                <!-- Structural Data Diagram (Interactive 3D Volatility & Strike Lattice) -->
                <div class="bento-pane">
                    <div class="pane-header">
                        <div>
                            <h2 class="pane-title">Structural Data Diagram</h2>
                            <div class="pane-desc">3D strike moneyness, implied volatility &amp; yield geometry (drag to rotate, scroll to zoom)</div>
                        </div>
                        <span id="structuralRendererBadge" class="badge font-mono">3D Projection</span>
                    </div>
                    <div class="spatial-viewport" id="structuralDiagramViewport">
                        <div class="viewport-overlay-bar">
                            <button type="button" class="mini-inspect-btn" onclick="rotateStructuralView(-0.25, 0)">Yaw &larr;</button>
                            <button type="button" class="mini-inspect-btn" onclick="rotateStructuralView(0.25, 0)">Yaw &rarr;</button>
                            <button type="button" class="mini-inspect-btn" onclick="resetStructuralView()">Reset 3D</button>
                        </div>
                        <canvas id="structuralDiagramCanvas" aria-label="Structural Data Diagram"></canvas>
                    </div>
                    <div class="viewport-legend">
                        <span class="legend-item"><span class="legend-swatch" style="background:#0D9488;"></span>Call Surface Bonds (#0D9488)</span>
                        <span class="legend-item"><span class="legend-swatch" style="background:#4F46E5;"></span>Put Surface Bonds (#4F46E5)</span>
                        <span class="legend-item"><span class="legend-swatch" style="background:#059669;"></span>Optimal Tier Strikes (#059669)</span>
                        <span class="legend-item"><span class="legend-swatch" style="background:#D97706;"></span>Spot &amp; Max Pain Axis (#D97706)</span>
                    </div>
                </div>
            </div>

            <!-- Cross-Asset Concentration & Sensitivity Heatmap Matrix (DESIGN.md §5) -->
            <div class="bento-pane">
                <div class="pane-header">
                    <div>
                        <h2 class="pane-title">Cross-Asset Concentration &amp; Regime Heatmap Matrix</h2>
                        <div class="pane-desc">90-day factor percentile intensity across all {num_indicators} ratios (click any cell to inspect series)</div>
                    </div>
                    <div class="font-mono text-muted-xs">
                        0% <span class="heatmap-gradient-bar"></span> 100%
                    </div>
                </div>
                <div id="macroHeatmapMatrix" class="heatmap-grid"></div>
            </div>

            <!-- Recommended Tactical Playbook Summary (Flat Bento Surface, No Gradients) -->
            <div class="bento-pane">
                <div class="pane-header">
                    <div>
                        <h2 class="pane-title">Tactical Options Execution Blueprint</h2>
                        <div class="pane-desc">Primary prescribed strategy for {ticker} based on macro alignment &amp; implied volatility skew</div>
                    </div>
                    <span class="badge state-nominal font-mono">{tactical.get('strategy', 'Neutral Options Overlay')}</span>
                </div>
                <p style="font-size: 13px; color: var(--text-secondary);">{tactical.get('rationale', '')}</p>
                <div class="partition-strip bottom-flush">
                    <div class="partition-cell">
                        <div class="label">Target Strike</div>
                        <div class="val font-mono">{tactical.get('optimal_strike', 'N/A')}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Target Delta</div>
                        <div class="val font-mono">{tactical.get('recommended_delta', 'N/A')}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Target DTE</div>
                        <div class="val font-mono">{tactical.get('target_dte', '30-45 DTE')}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Est. Annualized Yield</div>
                        <div class="val font-mono state-positive">{tactical.get('estimated_annualized_yield', 'N/A')}</div>
                    </div>
                </div>
            </div>
        </section>

        <!-- ========================================================================
             TAB 2: MACRO INDICATORS ({num_indicators})
             ======================================================================== -->
        <section id="tab-indicators" class="tab-content">
            <div class="filter-group">
                <button class="filter-btn active" onclick="filterIndicators('all', this)">All Ratios ({num_indicators})</button>
                <button class="filter-btn" onclick="filterIndicators('trend-bullish', this)">Bullish / Rising</button>
                <button class="filter-btn" onclick="filterIndicators('trend-bearish', this)">Bearish / Falling</button>
                <button class="filter-btn" onclick="filterIndicators('trend-neutral', this)">Neutral / Consolidating</button>
            </div>
            <div class="grid-4" id="indicatorsGrid">
                {ind_cards_rendered}
            </div>
        </section>

        <!-- ========================================================================
             TAB 3: TREND & FACTOR CHARTS
             ======================================================================== -->
        <section id="tab-charts" class="tab-content">
            <div class="grid-2">
                <div class="bento-pane">
                    <div class="pane-header">
                        <div>
                            <h2 class="pane-title">{ticker} Price Trend &amp; Moving Averages</h2>
                            <div class="pane-desc">Daily Close vs 50-MA &amp; 200-MA (As of {last_trade_date} Close)</div>
                        </div>
                        <span class="font-mono text-muted-xs">${price:.2f}</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="priceChart"></canvas>
                    </div>
                </div>

                <div class="bento-pane">
                    <div class="pane-header">
                        <div>
                            <h2 class="pane-title">Macro Indicators Percentile Radar</h2>
                            <div class="pane-desc">90-Day Cross-Asset Percentile Distribution (All {num_indicators} Ratios)</div>
                        </div>
                        <span class="font-mono text-muted-xs">0–100% Scale</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="macroRadarChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Interactive Focus Visualizer -->
            <div class="bento-pane" id="focusVisualizerCard">
                <div class="pane-header">
                    <div>
                        <h2 class="pane-title">Macro Indicator Detailed Focus Visualizer</h2>
                        <div class="pane-desc">Dynamic ratio time-series, 50-day moving average, and regime trajectory</div>
                    </div>
                    <span id="focusBadge" class="badge {first_status_class}">{first_trend}</span>
                </div>

                <div class="macro-selector-bar" id="macroSelectorBar">
                    {macro_pill_buttons_rendered}
                </div>

                <div class="partition-strip">
                    <div class="partition-cell">
                        <div class="label">Indicator Name</div>
                        <div id="focusIndName" class="val">{first_name}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Ratio Tickers</div>
                        <div id="focusIndRatio" class="val font-mono">{first_ratio}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Current Ratio &amp; 50-MA</div>
                        <div id="focusIndValue" class="val font-mono">{first_val_str}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">90-Day Percentile Rank</div>
                        <div id="focusIndPercentile" class="val font-mono">{first_pctl_str}</div>
                    </div>
                </div>

                <div class="chart-container" style="height: 280px;">
                    <canvas id="focusIndicatorChart"></canvas>
                </div>

                <div id="focusIndMeaning" class="pane-footer-row text-muted-xs">
                    {first_meaning}
                </div>
            </div>

            <!-- All Macro Indicator Multi-Chart Grid -->
            <div class="bento-pane" style="margin-bottom: 12px; padding: 12px 18px;">
                <h2 class="pane-title">All {num_indicators} Macro Indicators Trend Matrix</h2>
                <div class="pane-desc">Simultaneous multi-factor ratio &amp; 50-MA coordinate plots</div>
            </div>

            <div class="grid-4" id="indicatorChartsGrid">
                {ind_chart_cards_rendered}
            </div>
        </section>

        <!-- ========================================================================
             TAB 4: OPTIONS PLAYBOOK & SIMULATOR
             ======================================================================== -->
        <section id="tab-playbook" class="tab-content">
            <!-- Strategy Specification Bento Pane -->
            <div class="bento-pane">
                <div class="pane-header">
                    <div>
                        <h2 class="pane-title">Strategic Options Specification: {tactical.get('strategy', 'Neutral Options Overlay')}</h2>
                        <div class="pane-desc">{tactical.get('rationale', '')}</div>
                    </div>
                    <span class="badge state-nominal font-mono">{opt_chain.get('expiration', 'Near-Month')} ({opt_chain.get('dte', 30)} DTE)</span>
                </div>
                <div class="partition-strip bottom-flush">
                    <div class="partition-cell">
                        <div class="label">Target Strike</div>
                        <div class="val font-mono">{tactical.get('optimal_strike', 'N/A')}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Target Delta</div>
                        <div class="val font-mono">{tactical.get('recommended_delta', 'N/A')}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Target DTE</div>
                        <div class="val font-mono">{tactical.get('target_dte', '30-45 DTE')}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Target Return</div>
                        <div class="val font-mono state-positive">{tactical.get('estimated_annualized_yield', 'N/A')}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Profit Target</div>
                        <div class="val font-mono">{tactical.get('profit_target', '50% of max')}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Stop Loss Rule</div>
                        <div class="val font-mono">{tactical.get('stop_loss_rule', '2x credit')}</div>
                    </div>
                </div>
            </div>

            <!-- Options Volatility Signals Strip -->
            <div class="bento-pane">
                <div class="pane-header">
                    <div>
                        <h2 class="pane-title">Options Volatility &amp; Market Indicator Signals</h2>
                        <div class="pane-desc">Implied volatility pricing, skew, Put/Call ratios, and Max Pain strike</div>
                    </div>
                </div>
                <div class="partition-strip bottom-flush">
                    <div class="partition-cell">
                        <div class="label">IV (ATM) vs 30d HV</div>
                        <div class="val font-mono">{opt_analytics.get('iv_atm', 0.0):.1f}% / {opt_analytics.get('hv_30d', 0.0):.1f}%</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">IV Rank / Percentile</div>
                        <div class="val font-mono">{opt_analytics.get('iv_rank', 0.0):.1f}% / {opt_analytics.get('iv_percentile', 0.0):.1f}%</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">IV - RV Spread</div>
                        <div class="val font-mono {iv_rv_class}">{iv_rv_spread_val:+.1f}%</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Put/Call Ratio (Vol/OI)</div>
                        <div class="val font-mono">{opt_analytics.get('pcr_volume', 1.0):.2f} / {opt_analytics.get('pcr_open_interest', 1.0):.2f}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Max Pain Strike</div>
                        <div class="val font-mono state-nominal">${opt_analytics.get('max_pain_strike', price):.2f}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">30d Expected Move (±1σ)</div>
                        <div class="val font-mono">±${opt_analytics.get('expected_move_30d', 0.0):.2f} [{opt_analytics.get('expected_move_lower', 0.0):.2f}–{opt_analytics.get('expected_move_upper', 0.0):.2f}]</div>
                    </div>
                </div>
            </div>

            <!-- Market Microstructure & Practitioner Signals Strip -->
            <div class="bento-pane">
                <div class="pane-header">
                    <div>
                        <h2 class="pane-title">Market Microstructure, Whale Gamma &amp; Practitioner Signals</h2>
                        <div class="pane-desc">Dealer Gamma Exposure (GEX), Flip Safety Floor, 25Δ Skew, Retail 5Δ Call Surge &amp; Dark Pool Flow</div>
                    </div>
                </div>
                <div class="partition-strip bottom-flush">
                    <div class="partition-cell">
                        <div class="label">Net Dealer GEX</div>
                        <div class="val font-mono">{net_gex_str}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Gamma Flip Floor</div>
                        <div class="val font-mono state-nominal">{gamma_flip_str}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">25Δ Put-Call Skew</div>
                        <div class="val font-mono">{skew_25d_str}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Retail 5Δ Call Surge</div>
                        <div class="val font-mono">{lottery_ratio_str}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Short Float / DTC</div>
                        <div class="val font-mono">{short_float_str} ({days_to_cover_str})</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Dark Pool &amp; MOC</div>
                        <div class="val font-mono">{dark_pool_str} ({moc_imbalance_str})</div>
                    </div>
                </div>
            </div>

            <!-- Dual Selling Screener Matrices -->
            <div class="grid-2">
                <div class="bento-pane">
                    <div class="pane-header">
                        <div>
                            <h2 class="pane-title">Selling Covered Calls Screener</h2>
                            <div class="pane-desc">Income &amp; downside cushion on long stock position (100 shares per contract)</div>
                        </div>
                    </div>
                    <div class="table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th>Tier</th>
                                    <th>Strike</th>
                                    <th>Mid</th>
                                    <th>Δ</th>
                                    <th>Θ</th>
                                    <th>OTM %</th>
                                    <th>Yield Unassigned</th>
                                    <th>Return Called</th>
                                    <th>Cushion</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {cc_rows_rendered}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="bento-pane">
                    <div class="pane-header">
                        <div>
                            <h2 class="pane-title">Selling Cash-Secured Puts Screener</h2>
                            <div class="pane-desc">Acquire shares at a discount basis or harvest collateral yield</div>
                        </div>
                    </div>
                    <div class="table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th>Tier</th>
                                    <th>Strike</th>
                                    <th>Mid</th>
                                    <th>Δ</th>
                                    <th>Θ</th>
                                    <th>OTM %</th>
                                    <th>Collateral</th>
                                    <th>Net Basis</th>
                                    <th>Discount</th>
                                    <th>Ann. ROC</th>
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

            <!-- Unusual Option Activity -->
            <div class="bento-pane">
                <div class="pane-header">
                    <div>
                        <h2 class="pane-title">Unusual Option Activity (UOA) &amp; Institutional Flow Tracker</h2>
                        <div class="pane-desc">Anomalous block trades &amp; sweeps where session volume exceeds 1.4x open interest</div>
                    </div>
                </div>
                <div class="table-wrap">
                    <table id="uoaTable">
                        <thead>
                            <tr>
                                <th>Type</th>
                                <th>Contract</th>
                                <th>Strike</th>
                                <th>Volume</th>
                                <th>Open Int</th>
                                <th>Vol / OI</th>
                                <th>Est. Dollar Flow</th>
                                <th>Institutional Flow Sentiment</th>
                            </tr>
                        </thead>
                        <tbody>
                            {uoa_rows_rendered}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Live Option Chain Explorer -->
            <div class="bento-pane">
                <div class="pane-header">
                    <div>
                        <h2 class="pane-title">Live Real-Time Option Chain Explorer</h2>
                        <div class="pane-desc">Expiration: <span class="font-mono state-nominal">{opt_chain.get('expiration', 'Near-Month')} ({opt_chain.get('dte', 30)} DTE)</span> &bull; Spot Price: <span class="font-mono">${price:.2f}</span></div>
                    </div>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 12px;">
                    <div class="filter-group" style="margin-bottom: 0;">
                        <button class="filter-btn active" onclick="filterOptionChain('all', this)">All Contracts</button>
                        <button class="filter-btn" onclick="filterOptionChain('calls', this)">Calls Only</button>
                        <button class="filter-btn" onclick="filterOptionChain('puts', this)">Puts Only</button>
                        <button class="filter-btn" onclick="filterOptionChain('ntm', this)">Near Money (±10%)</button>
                    </div>
                    <div>
                        <input type="text" id="chainSearchInput" class="search-input font-mono" placeholder="Filter strike or type..." oninput="searchOptionChain()">
                    </div>
                </div>

                <div class="table-wrap" style="max-height: 360px; overflow-y: auto;">
                    <table id="optionsChainTable">
                        <thead style="position: sticky; top: 0; z-index: 10;">
                            <tr>
                                <th>Type</th>
                                <th>Strike</th>
                                <th>Bid</th>
                                <th>Ask</th>
                                <th>Mid</th>
                                <th>Delta (Δ)</th>
                                <th>Theta (Θ)</th>
                                <th>Volume</th>
                                <th>Open Int</th>
                                <th>Vol / OI</th>
                                <th>IV %</th>
                                <th>Status</th>
                                <th>Simulate</th>
                            </tr>
                        </thead>
                        <tbody id="chainTableBody">
                            {chain_rows_rendered}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Interactive Dual Strategy Payoff Simulator -->
            <div class="bento-pane">
                <div class="pane-header">
                    <div>
                        <h2 class="pane-title">Interactive Options Payoff Simulator</h2>
                        <div class="pane-desc">Model expiration P&amp;L across underlying price shifts for Covered Calls vs Cash-Secured Puts</div>
                    </div>
                </div>

                <div class="strategy-mode-bar">
                    <button id="modeBtnCC" class="strategy-mode-btn active" onclick="setSimulatorStrategy('CC')">
                        Covered Call (Long 100 Shares + Short Call)
                    </button>
                    <button id="modeBtnCSP" class="strategy-mode-btn" onclick="setSimulatorStrategy('CSP')">
                        Cash-Secured Put (Short Put + Cash Collateral)
                    </button>
                </div>

                <div class="grid-3">
                    <div>
                        <label class="cell-label" for="simStockPriceInput">Stock Cost / Spot Price ($)</label>
                        <input type="number" id="simStockPriceInput" class="search-input font-mono" style="width: 100%; margin-top: 4px;" value="{price:.2f}" step="0.5" onchange="updateSimPayoff()">
                    </div>
                    <div>
                        <label class="cell-label" for="simStrikeInput">Short Strike Price ($)</label>
                        <input type="number" id="simStrikeInput" class="search-input font-mono" style="width: 100%; margin-top: 4px;" value="{init_strike:.2f}" step="0.5" onchange="updateSimPayoff()">
                    </div>
                    <div>
                        <label class="cell-label" for="simPremiumInput">Option Premium Received ($)</label>
                        <input type="number" id="simPremiumInput" class="search-input font-mono" style="width: 100%; margin-top: 4px;" value="{init_premium:.2f}" step="0.05" onchange="updateSimPayoff()">
                    </div>
                </div>

                <div class="slider-control">
                    <label for="priceSlider" style="font-weight: 600; min-width: 130px;">Simulated Spot:</label>
                    <input type="range" id="priceSlider" min="{max(1.0, round(price * 0.7, 1))}" max="{round(price * 1.3, 1)}" step="0.5" value="{round(price, 1)}" oninput="updateSimPayoff()">
                    <span id="sliderPriceDisplay" class="font-mono" style="font-size: 15px; font-weight: 700; min-width: 80px;">${price:.2f}</span>
                </div>

                <div class="partition-strip">
                    <div class="partition-cell">
                        <div class="label">Simulated Price Move</div>
                        <div id="simPriceMove" class="val font-mono">0.0%</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Simulated Net P&amp;L</div>
                        <div id="simDollarPnL" class="val font-mono state-positive">$0.00</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Return on Capital (ROC)</div>
                        <div id="simROCPct" class="val font-mono state-positive">0.0%</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Breakeven Price</div>
                        <div id="simBreakeven" class="val font-mono">${price * 0.95:.2f}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Position Status</div>
                        <div id="simPnLStatus" class="val font-mono state-positive">Max Profit Zone</div>
                    </div>
                </div>

                <div class="chart-container">
                    <canvas id="payoffChart"></canvas>
                </div>
            </div>

            <!-- Risk Considerations -->
            <div class="bento-pane">
                <div class="pane-header">
                    <div>
                        <h2 class="pane-title">Risk Considerations &amp; Trade Management Discipline</h2>
                        <div class="pane-desc">Systematic position management parameters</div>
                    </div>
                </div>
                <div>
                    <div class="rule-row"><span class="font-mono state-nominal">[RULE]</span><span><b>Delta Assignment Management:</b> If short option delta expands beyond ±0.70, evaluate rolling out in time to the next monthly cycle for net credit.</span></div>
                    <div class="rule-row"><span class="font-mono state-nominal">[RULE]</span><span><b>Profit Capture Discipline:</b> Close short option legs once 50% to 75% of initial credit is captured to release collateral and eliminate tail risk.</span></div>
                    {warnings_html}
                </div>
            </div>
        </section>

        <!-- ========================================================================
             TAB 5: DATA PROVENANCE, VALIDATION RECORDS & TELEMETRY (DESIGN.md §2 & §6)
             ======================================================================== -->
        <section id="tab-provenance" class="tab-content">
            <div class="bento-pane">
                <div class="pane-header">
                    <div>
                        <h2 class="pane-title">Workspace Data Provenance &amp; Telemetry Citations</h2>
                        <div class="pane-desc">Empirical dataset lineage, cryptographic verification digest, and live stream telemetry</div>
                    </div>
                    <span class="badge trend-bullish font-mono" id="provStatusBadge">EMPIRICAL DATASET VERIFIED</span>
                </div>
                <div class="partition-strip">
                    <div class="partition-cell">
                        <div class="label">Dataset Identifier</div>
                        <div id="provDatasetId" class="val font-mono">{provenance_data['dataset_id']}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">SHA-256 Digest Prefix</div>
                        <div id="provSha256" class="val font-mono">{provenance_data['sha256_prefix']}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Generated Timestamp</div>
                        <div id="provGeneratedUtc" class="val font-mono">{provenance_data['generated_utc']}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Host OS Theme Fallback</div>
                        <div id="provSystemTheme" class="val font-mono">{system_theme}</div>
                    </div>
                </div>
                <div class="partition-strip bottom-flush">
                    <div class="partition-cell">
                        <div class="label">Equity Time-Series Source</div>
                        <div id="provEquityFeed" class="val font-mono">{provenance_data['equity_feed']}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Options Chain Source</div>
                        <div id="provOptionsFeed" class="val font-mono">{provenance_data['options_feed']}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Cross-Asset Validation</div>
                        <div id="provMacroValidated" class="val font-mono state-positive">{provenance_data['macro_ratios_validated']}</div>
                    </div>
                    <div class="partition-cell">
                        <div class="label">Indexed Option Contracts</div>
                        <div id="provContractsIndexed" class="val font-mono">{provenance_data['contracts_indexed']}</div>
                    </div>
                </div>
            </div>

            <div class="bento-pane">
                <div class="pane-header">
                    <div>
                        <h2 class="pane-title">Macro Ratio Series Validation Records</h2>
                        <div class="pane-desc">Empirical sample counts, moving average convergence, and validation state per factor</div>
                    </div>
                </div>
                <div class="table-wrap">
                    <table id="validationRecordsTable">
                        <thead>
                            <tr>
                                <th>Factor ID</th>
                                <th>Indicator Domain</th>
                                <th>Ticker Pair</th>
                                <th>Sample Window</th>
                                <th>Latest Ratio</th>
                                <th>50-Day MA</th>
                                <th>90d Percentile</th>
                                <th>Validation Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {validation_rows_rendered}
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="bento-pane">
                <div class="pane-header">
                    <div>
                        <h2 class="pane-title">Live State &amp; Telemetry Event Log</h2>
                        <div class="pane-desc">Incremental state updates and Server-Sent Events (SSE) synchronization records</div>
                    </div>
                    <button type="button" class="mini-inspect-btn" onclick="triggerIncrementalStateRefresh()">Verify Incremental Refresh</button>
                </div>
                <div id="telemetryEventLog" class="font-mono" style="font-size: 11.5px; color: var(--text-secondary); display: flex; flex-direction: column; gap: 6px;">
                    <div>[{generated_utc}] [INIT] Loaded empirical dataset {provenance_data['dataset_id']} (SHA-256: {provenance_data['sha256_prefix']}).</div>
                    <div>[{generated_utc}] [VALIDATION] Verified {valid_indicators_count}/{num_indicators} cross-asset ratio series and {total_calls + total_puts} option contracts.</div>
                    <div>[{generated_utc}] [THEME] Host OS theme fallback detected as '{system_theme}'; matchMedia listener active.</div>
                </div>
            </div>
        </section>

    </main>

    <footer>
        Macro Flow Stock Navigator &bull; Dataset <span class="font-mono">{provenance_data['dataset_id']}</span> &bull; {last_trade_date}
    </footer>

    <script>
        // ============================================================================
        // Empirical Workspace Data Bundle
        // ============================================================================
        let CURRENT_PRICE = {price};
        let TICKER_INFO = {ticker_json};
        let INDICATORS_DATA = {indicators_json};
        let HISTORY_DATA = {history_json};
        let DECISION_DATA = {decision_json};
        let PLAYBOOK_DATA = {playbook_json};
        let PROVENANCE_DATA = {provenance_json};
        const SYSTEM_THEME_FALLBACK = "{system_theme}";

        // Semantic Data Visualization Palette (DESIGN.md §5)
        const VIZ_PALETTE = {{
            teal: "#0D9488",
            amber: "#D97706",
            indigo: "#4F46E5",
            emerald: "#059669",
            rose: "#E11D48"
        }};

        // Chart & Viewport State (Preserved across incremental state updates)
        let currentThemeMode = "system";
        let currentTheme = SYSTEM_THEME_FALLBACK;
        let priceChartInstance = null;
        let radarChartInstance = null;
        let focusIndicatorChartInstance = null;
        const indicatorChartInstances = {{}};
        let payoffChartInstance = null;
        let currentFocusKey = "{first_ind_key}";
        let currentSimStrategy = "CC";

        // Interactive Relationship Node Map Viewport State
        const nodeMapState = {{
            panX: 0,
            panY: 0,
            scale: 1.0,
            isDragging: false,
            startX: 0,
            startY: 0,
            selectedNodeId: null
        }};

        // Interactive 3D Structural Data Diagram Camera State
        const structuralCamera = {{
            yaw: -0.58,
            pitch: 0.42,
            zoom: 1.0,
            isDragging: false,
            lastX: 0,
            lastY: 0
        }};

        const hasChartJs = typeof Chart !== "undefined";

        // ============================================================================
        // Three-Icon Theme Selector & OS Preference Tracking (DESIGN.md §3)
        // ============================================================================
        const osDarkMatcher = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;

        function resolveSystemTheme() {{
            if (osDarkMatcher && typeof osDarkMatcher.matches === "boolean") {{
                return osDarkMatcher.matches ? "dark" : "light";
            }}
            return SYSTEM_THEME_FALLBACK || "dark";
        }}

        function getThemeTokens() {{
            const isDark = currentTheme === "dark";
            return {{
                isDark,
                bgBody: isDark ? "#0D0E11" : "#FAFAF9",
                bgSurface: isDark ? "#16171D" : "#FFFFFF",
                border: isDark ? "#292A30" : "#E7E5E4",
                textPrimary: isDark ? "#ECE8E2" : "#1C1917",
                textSecondary: isDark ? "#9A9895" : "#787774",
                gridLine: isDark ? "#292A30" : "#E7E5E4"
            }};
        }}

        function setThemeMode(mode) {{
            if (!["light", "dark", "system"].includes(mode)) mode = "system";
            currentThemeMode = mode;
            try {{
                localStorage.setItem("mf_theme_mode", mode);
                localStorage.setItem("mf_theme", mode === "system" ? resolveSystemTheme() : mode);
            }} catch (e) {{}}

            const resolved = mode === "system" ? resolveSystemTheme() : mode;
            applyResolvedTheme(resolved, mode);
        }}

        function applyResolvedTheme(resolvedTheme, mode) {{
            currentTheme = resolvedTheme === "light" ? "light" : "dark";
            document.documentElement.setAttribute("data-theme", currentTheme);
            document.documentElement.setAttribute("data-theme-mode", mode);

            const modes = ["light", "dark", "system"];
            modes.forEach(m => {{
                const btn = document.getElementById("theme-btn-" + m);
                if (btn) {{
                    const isActive = m === mode;
                    btn.classList.toggle("active", isActive);
                    btn.setAttribute("aria-pressed", isActive ? "true" : "false");
                }}
            }});

            // Re-render all visualizers cleanly without losing camera or viewport state
            renderHeatmapMatrix();
            renderRelationshipNodeMap();
            renderStructuralDiagram();
            if (hasChartJs) {{
                updateChartTheme();
            }} else {{
                renderAllNativeCharts();
            }}
            updateSimPayoff();
        }}

        function applyTheme(theme) {{
            setThemeMode(theme);
        }}

        function toggleTheme() {{
            const nextMode = currentTheme === "dark" ? "light" : "dark";
            setThemeMode(nextMode);
        }}

        if (osDarkMatcher) {{
            const handleOsThemeChange = () => {{
                if (currentThemeMode === "system") {{
                    applyResolvedTheme(resolveSystemTheme(), "system");
                    appendTelemetryLog("[THEME] OS appearance preference changed; updated system theme to '" + currentTheme + "'.");
                }}
            }};
            if (typeof osDarkMatcher.addEventListener === "function") {{
                osDarkMatcher.addEventListener("change", handleOsThemeChange);
            }} else if (typeof osDarkMatcher.addListener === "function") {{
                osDarkMatcher.addListener(handleOsThemeChange);
            }}
        }}

        // ============================================================================
        // Cross-Asset Concentration & Regime Heatmap Matrix (DESIGN.md §5)
        // Smoothly interpolates Surface -> Vibrant Teal (#0D9488) -> Vivid Indigo (#4F46E5) -> Deep Rose (#E11D48)
        // ============================================================================
        function hexToRgb(hex) {{
            const clean = hex.replace("#", "");
            return {{
                r: parseInt(clean.substring(0, 2), 16),
                g: parseInt(clean.substring(2, 4), 16),
                b: parseInt(clean.substring(4, 6), 16)
            }};
        }}

        function interpolateRgb(c1, c2, t) {{
            return {{
                r: Math.round(c1.r + (c2.r - c1.r) * t),
                g: Math.round(c1.g + (c2.g - c1.g) * t),
                b: Math.round(c1.b + (c2.b - c1.b) * t)
            }};
        }}

        function computeHeatmapColor(percentile) {{
            const tokens = getThemeTokens();
            const p = Math.max(0, Math.min(100, percentile)) / 100.0;
            const cSurface = hexToRgb(tokens.bgSurface);
            const cTeal = hexToRgb(VIZ_PALETTE.teal);
            const cIndigo = hexToRgb(VIZ_PALETTE.indigo);
            const cRose = hexToRgb(VIZ_PALETTE.rose);

            let rgb;
            if (p <= 0.35) {{
                rgb = interpolateRgb(cSurface, cTeal, p / 0.35);
            }} else if (p <= 0.70) {{
                rgb = interpolateRgb(cTeal, cIndigo, (p - 0.35) / 0.35);
            }} else {{
                rgb = interpolateRgb(cIndigo, cRose, (p - 0.70) / 0.30);
            }}
            return `rgb(${{rgb.r}}, ${{rgb.g}}, ${{rgb.b}})`;
        }}

        function renderHeatmapMatrix() {{
            const container = document.getElementById("macroHeatmapMatrix");
            if (!container) return;
            const keys = Object.keys(INDICATORS_DATA);
            const htmlParts = [];

            keys.forEach(key => {{
                const ind = INDICATORS_DATA[key];
                const pctl = parseFloat(ind.percentile_90d || 50.0);
                const bg = computeHeatmapColor(pctl);
                const highContrastText = pctl > 32 ? "#FFFFFF" : "var(--text-primary)";
                const subText = pctl > 32 ? "rgba(255,255,255,0.82)" : "var(--text-secondary)";
                htmlParts.push(`
                    <div class="heatmap-cell" style="background-color: ${{bg}};" onclick="switchTab('charts'); selectFocusIndicator('${{key}}');" title="${{ind.display_name}}: ${{ind.market_meaning}}">
                        <div class="font-mono" style="font-size: 11px; font-weight: 700; color: ${{highContrastText}};">${{ind.ratio_tickers}}</div>
                        <div class="font-mono" style="font-size: 15px; font-weight: 700; margin: 3px 0; color: ${{highContrastText}};">${{pctl.toFixed(1)}}%</div>
                        <div class="font-mono" style="font-size: 10px; color: ${{subText}};">${{ind.trend_signal}}</div>
                    </div>
                `);
            }});
            container.innerHTML = htmlParts.join("");
        }}

        // ============================================================================
        // Interactive Relationship Node Map (Deterministic SVG Network Graph - DESIGN.md §4 & §5)
        // ============================================================================
        function renderRelationshipNodeMap() {{
            const svg = document.getElementById("relationshipNodeMapSvg");
            if (!svg) return;
            const tokens = getThemeTokens();
            const width = 640;
            const height = 340;
            const cx = width / 2;
            const cy = height / 2;

            const favSet = new Set(((DECISION_DATA.favorable_forces) || []).map(f => f.ratio));
            const hostSet = new Set(((DECISION_DATA.hostile_forces) || []).map(h => h.ratio));

            const nodes = [];
            const edges = [];

            // Central Target Equity Node
            nodes.push({{
                id: "TICKER",
                label: TICKER_INFO.ticker || "TICKER",
                sub: "$" + (CURRENT_PRICE || 0).toFixed(2),
                x: cx,
                y: cy,
                r: 24,
                color: VIZ_PALETTE.teal
            }});

            // Structural Archetype Hub (Left Inner)
            const archX = cx - 105;
            const archY = cy - 55;
            nodes.push({{
                id: "ARCHETYPE",
                label: (DECISION_DATA.archetype_key || "ARCHETYPE").replace(/_/g, " "),
                sub: "Archetype",
                x: archX,
                y: archY,
                r: 17,
                color: VIZ_PALETTE.indigo
            }});
            edges.push({{ from: "ARCHETYPE", to: "TICKER", color: VIZ_PALETTE.indigo, weight: 2.2 }});

            // Macro Regime Hub (Right Inner)
            const regX = cx + 105;
            const regY = cy - 55;
            const regBadge = (DECISION_DATA.macro_regime && DECISION_DATA.macro_regime.badge) || "Regime";
            nodes.push({{
                id: "REGIME",
                label: regBadge.slice(0, 16),
                sub: "Macro Regime",
                x: regX,
                y: regY,
                r: 17,
                color: VIZ_PALETTE.indigo
            }});
            edges.push({{ from: "REGIME", to: "TICKER", color: VIZ_PALETTE.indigo, weight: 2.2 }});

            // Options Strategy Node (Bottom Inner)
            const optX = cx;
            const optY = cy + 92;
            const optStrat = (PLAYBOOK_DATA.tactical_execution && PLAYBOOK_DATA.tactical_execution.strategy) || "Options Overlay";
            nodes.push({{
                id: "OPTIONS",
                label: optStrat.split("/")[0].trim().slice(0, 18),
                sub: "IV " + ((PLAYBOOK_DATA.options_analytics && PLAYBOOK_DATA.options_analytics.iv_atm) || 25) + "%",
                x: optX,
                y: optY,
                r: 17,
                color: VIZ_PALETTE.amber
            }});
            edges.push({{ from: "TICKER", to: "OPTIONS", color: VIZ_PALETTE.amber, weight: 2.0 }});

            // Cross-Asset Macro Indicator Nodes on Outer Elliptical Ring
            const indKeys = Object.keys(INDICATORS_DATA);
            const rx = 248;
            const ry = 132;
            indKeys.forEach((k, idx) => {{
                const ind = INDICATORS_DATA[k];
                const angle = (idx / indKeys.length) * Math.PI * 2 - Math.PI / 2;
                const nx = cx + Math.cos(angle) * rx;
                const ny = cy + Math.sin(angle) * ry;
                const ratio = ind.ratio_tickers || k;

                let nodeColor = VIZ_PALETTE.teal;
                if (favSet.has(ratio) || (ind.trend_signal && ind.trend_signal.includes("Rising") && k !== "VIX_SPX" && k !== "GLD_SPX")) {{
                    nodeColor = VIZ_PALETTE.emerald;
                }} else if (hostSet.has(ratio) || (ind.trend_signal && ind.trend_signal.includes("Falling") && k !== "VIX_SPX" && k !== "GLD_SPX")) {{
                    nodeColor = VIZ_PALETTE.rose;
                }}

                nodes.push({{
                    id: k,
                    label: ratio,
                    sub: (ind.percentile_90d || 50).toFixed(0) + "p",
                    x: nx,
                    y: ny,
                    r: 15,
                    color: nodeColor
                }});

                edges.push({{
                    from: k,
                    to: "TICKER",
                    color: nodeColor,
                    weight: favSet.has(ratio) || hostSet.has(ratio) ? 2.0 : 1.2
                }});
            }});

            const nodeLookup = {{}};
            nodes.forEach(n => {{ nodeLookup[n.id] = n; }});

            const tx = nodeMapState.panX;
            const ty = nodeMapState.panY;
            const sc = nodeMapState.scale;

            let svgContent = `<g transform="translate(${{tx}}, ${{ty}}) scale(${{sc}})">`;

            // Render semi-transparent edges derived from connected node state
            edges.forEach(e => {{
                const n1 = nodeLookup[e.from];
                const n2 = nodeLookup[e.to];
                if (!n1 || !n2) return;
                svgContent += `<line x1="${{n1.x.toFixed(1)}}" y1="${{n1.y.toFixed(1)}}" x2="${{n2.x.toFixed(1)}}" y2="${{n2.y.toFixed(1)}}" stroke="${{e.color}}" stroke-opacity="0.45" stroke-width="${{e.weight}}" />`;
            }});

            // Render nodes
            nodes.forEach(n => {{
                const isSelected = nodeMapState.selectedNodeId === n.id;
                const strokeColor = isSelected ? tokens.textPrimary : tokens.bgSurface;
                const strokeW = isSelected ? 2.5 : 1.5;
                svgContent += `
                    <g class="network-node" style="cursor:pointer;" onclick="onNetworkNodeClick('${{n.id}}')">
                        <circle cx="${{n.x.toFixed(1)}}" cy="${{n.y.toFixed(1)}}" r="${{n.r}}" fill="${{n.color}}" fill-opacity="0.9" stroke="${{strokeColor}}" stroke-width="${{strokeW}}" />
                        <text x="${{n.x.toFixed(1)}}" y="${{(n.y - n.r - 5).toFixed(1)}}" text-anchor="middle" fill="${{tokens.textPrimary}}" font-family="IBM Plex Mono, monospace" font-size="10.5" font-weight="600">${{n.label}}</text>
                        <text x="${{n.x.toFixed(1)}}" y="${{(n.y + 3.5).toFixed(1)}}" text-anchor="middle" fill="#FFFFFF" font-family="IBM Plex Mono, monospace" font-size="9.5" font-weight="600">${{n.sub}}</text>
                    </g>
                `;
            }});

            svgContent += `</g>`;
            svg.innerHTML = svgContent;
        }}

        function onNetworkNodeClick(nodeId) {{
            nodeMapState.selectedNodeId = nodeId;
            renderRelationshipNodeMap();
            const statusEl = document.getElementById("nodeMapStatus");
            if (INDICATORS_DATA[nodeId]) {{
                const ind = INDICATORS_DATA[nodeId];
                if (statusEl) statusEl.innerText = `${{ind.ratio_tickers}}: ${{ind.current_value}} (${{ind.trend_signal}})`;
                selectFocusIndicator(nodeId);
            }} else if (statusEl) {{
                statusEl.innerText = `Selected Node: ${{nodeId}}`;
            }}
        }}

        function zoomNodeMap(factor) {{
            nodeMapState.scale = Math.max(0.6, Math.min(2.2, nodeMapState.scale * factor));
            renderRelationshipNodeMap();
        }}

        function resetNodeMapTransform() {{
            nodeMapState.panX = 0;
            nodeMapState.panY = 0;
            nodeMapState.scale = 1.0;
            nodeMapState.selectedNodeId = null;
            renderRelationshipNodeMap();
        }}

        function initNodeMapInteractions() {{
            const vp = document.getElementById("relationshipNodeMapViewport");
            if (!vp) return;
            vp.addEventListener("mousedown", e => {{
                if (e.target.tagName === "BUTTON") return;
                nodeMapState.isDragging = true;
                nodeMapState.startX = e.clientX - nodeMapState.panX;
                nodeMapState.startY = e.clientY - nodeMapState.panY;
            }});
            window.addEventListener("mousemove", e => {{
                if (!nodeMapState.isDragging) return;
                nodeMapState.panX = e.clientX - nodeMapState.startX;
                nodeMapState.panY = e.clientY - nodeMapState.startY;
                renderRelationshipNodeMap();
            }});
            window.addEventListener("mouseup", () => {{
                nodeMapState.isDragging = false;
            }});
            vp.addEventListener("wheel", e => {{
                e.preventDefault();
                const factor = e.deltaY < 0 ? 1.08 : 0.92;
                zoomNodeMap(factor);
            }}, {{ passive: false }});
        }}

        // ============================================================================
        // Structural Data Diagram (Interactive 3D Spatial Geometry with WebGL Check +
        // Deterministic Software Projection Fallback - DESIGN.md §4 & §5)
        // ============================================================================
        function project3DPoint(x, y, z, width, height, yaw, pitch, zoom) {{
            const cosY = Math.cos(yaw);
            const sinY = Math.sin(yaw);
            const cosP = Math.cos(pitch);
            const sinP = Math.sin(pitch);

            const x1 = x * cosY - z * sinY;
            const z1 = x * sinY + z * cosY;
            const y2 = y * cosP - z1 * sinP;
            const z2 = y * sinP + z1 * cosP;

            const fov = 360 * zoom;
            const viewerDist = 4.2;
            const scale = fov / (viewerDist + z2);
            return {{
                sx: width / 2 + x1 * scale,
                sy: height / 2 - y2 * scale,
                depth: z2
            }};
        }}

        function renderStructuralDiagram() {{
            const canvas = document.getElementById("structuralDiagramCanvas");
            if (!canvas) return;
            const setup = setupCanvasContext(canvas);
            if (!setup) return;
            const {{ ctx, width, height }} = setup;
            const tokens = getThemeTokens();

            ctx.clearRect(0, 0, width, height);

            const calls = (PLAYBOOK_DATA.options_chain && PLAYBOOK_DATA.options_chain.calls) || [];
            const puts = (PLAYBOOK_DATA.options_chain && PLAYBOOK_DATA.options_chain.puts) || [];
            const spot = CURRENT_PRICE || 100.0;

            const {{ yaw, pitch, zoom }} = structuralCamera;

            // Coordinate axes bounding frame (-1.2 to +1.2)
            const axes = [
                {{ from: [-1.2, -0.7, -1.0], to: [1.2, -0.7, -1.0], label: "Strike Moneyness (OTM %)" }},
                {{ from: [-1.2, -0.7, -1.0], to: [-1.2, 0.9, -1.0], label: "Implied Vol / Yield" }},
                {{ from: [-1.2, -0.7, -1.0], to: [-1.2, -0.7, 1.0], label: "Delta / Horizon" }}
            ];

            ctx.strokeStyle = tokens.gridLine;
            ctx.lineWidth = 1;
            ctx.font = "10px 'IBM Plex Mono', monospace";
            ctx.fillStyle = tokens.textSecondary;

            axes.forEach(ax => {{
                const p1 = project3DPoint(ax.from[0], ax.from[1], ax.from[2], width, height, yaw, pitch, zoom);
                const p2 = project3DPoint(ax.to[0], ax.to[1], ax.to[2], width, height, yaw, pitch, zoom);
                ctx.beginPath();
                ctx.moveTo(p1.sx, p1.sy);
                ctx.lineTo(p2.sx, p2.sy);
                ctx.stroke();
                ctx.fillText(ax.label, p2.sx + 4, p2.sy);
            }});

            // Build 3D structural lattice nodes from live Calls & Puts + Recommended Tiers
            const callPts = [];
            calls.slice(0, 12).forEach((c, idx) => {{
                const moneyness = Math.max(-1.1, Math.min(1.1, ((c.strike - spot) / spot) * 6.0));
                const ivNorm = Math.max(-0.6, Math.min(0.85, ((c.impliedVolatility || 25) - 25) / 30));
                const deltaZ = ((c.delta || 0.5) - 0.5) * 1.8;
                const proj = project3DPoint(moneyness, ivNorm, deltaZ, width, height, yaw, pitch, zoom);
                callPts.push({{ ...proj, strike: c.strike, iv: c.impliedVolatility, color: VIZ_PALETTE.teal, type: "CALL" }});
            }});

            const putPts = [];
            puts.slice(0, 12).forEach((p, idx) => {{
                const moneyness = Math.max(-1.1, Math.min(1.1, ((p.strike - spot) / spot) * 6.0));
                const ivNorm = Math.max(-0.6, Math.min(0.85, ((p.impliedVolatility || 25) - 25) / 30));
                const deltaZ = (Math.abs(p.delta || -0.5) - 0.5) * 1.8;
                const proj = project3DPoint(moneyness, ivNorm, deltaZ, width, height, yaw, pitch, zoom);
                putPts.push({{ ...proj, strike: p.strike, iv: p.impliedVolatility, color: VIZ_PALETTE.indigo, type: "PUT" }});
            }});

            // Connect structural bonds along Call and Put manifolds
            function drawManifold(pts, strokeHex) {{
                if (pts.length < 2) return;
                ctx.strokeStyle = strokeHex;
                ctx.lineWidth = 1.8;
                ctx.beginPath();
                pts.forEach((pt, i) => {{
                    if (i === 0) ctx.moveTo(pt.sx, pt.sy);
                    else ctx.lineTo(pt.sx, pt.sy);
                }});
                ctx.stroke();
            }}

            drawManifold(callPts, VIZ_PALETTE.teal);
            drawManifold(putPts, VIZ_PALETTE.indigo);

            // Cross-rungs linking matching strikes between Call and Put surfaces
            const rungCount = Math.min(callPts.length, putPts.length);
            ctx.strokeStyle = tokens.gridLine;
            ctx.lineWidth = 1;
            for (let i = 0; i < rungCount; i++) {{
                ctx.beginPath();
                ctx.moveTo(callPts[i].sx, callPts[i].sy);
                ctx.lineTo(putPts[i].sx, putPts[i].sy);
                ctx.stroke();
            }}

            // Spot & Max Pain Vertical Reference Pillar
            const spotTop = project3DPoint(0, 0.85, 0, width, height, yaw, pitch, zoom);
            const spotBot = project3DPoint(0, -0.7, 0, width, height, yaw, pitch, zoom);
            ctx.strokeStyle = VIZ_PALETTE.amber;
            ctx.setLineDash([3, 3]);
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(spotBot.sx, spotBot.sy);
            ctx.lineTo(spotTop.sx, spotTop.sy);
            ctx.stroke();
            ctx.setLineDash([]);
            ctx.fillStyle = VIZ_PALETTE.amber;
            ctx.fillText(`Spot $${{spot.toFixed(2)}}`, spotTop.sx - 28, spotTop.sy - 6);

            // Draw 3D vertices
            [...callPts, ...putPts].forEach(pt => {{
                ctx.fillStyle = pt.color;
                ctx.beginPath();
                ctx.arc(pt.sx, pt.sy, 4, 0, Math.PI * 2);
                ctx.fill();
            }});

            // Highlight Balanced Covered Call & Cash-Secured Put Optimal Tier Nodes in Functional Emerald
            const balCC = PLAYBOOK_DATA.covered_call_matrix && PLAYBOOK_DATA.covered_call_matrix.balanced;
            if (balCC && balCC.strike) {{
                const m = Math.max(-1.1, Math.min(1.1, ((balCC.strike - spot) / spot) * 6.0));
                const p = project3DPoint(m, 0.35, -0.35, width, height, yaw, pitch, zoom);
                ctx.fillStyle = VIZ_PALETTE.emerald;
                ctx.beginPath();
                ctx.arc(p.sx, p.sy, 6, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillText(`CC $${{balCC.strike}}`, p.sx + 8, p.sy + 3);
            }}

            const balCSP = PLAYBOOK_DATA.cash_secured_put_matrix && PLAYBOOK_DATA.cash_secured_put_matrix.balanced;
            if (balCSP && balCSP.strike) {{
                const m = Math.max(-1.1, Math.min(1.1, ((balCSP.strike - spot) / spot) * 6.0));
                const p = project3DPoint(m, 0.30, 0.35, width, height, yaw, pitch, zoom);
                ctx.fillStyle = VIZ_PALETTE.emerald;
                ctx.beginPath();
                ctx.arc(p.sx, p.sy, 6, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillText(`CSP $${{balCSP.strike}}`, p.sx + 8, p.sy + 3);
            }}
        }}

        function rotateStructuralView(dYaw, dPitch) {{
            structuralCamera.yaw += dYaw;
            structuralCamera.pitch = Math.max(-1.1, Math.min(1.1, structuralCamera.pitch + dPitch));
            renderStructuralDiagram();
        }}

        function resetStructuralView() {{
            structuralCamera.yaw = -0.58;
            structuralCamera.pitch = 0.42;
            structuralCamera.zoom = 1.0;
            renderStructuralDiagram();
        }}

        function initStructuralDiagramInteractions() {{
            const vp = document.getElementById("structuralDiagramViewport");
            const badge = document.getElementById("structuralRendererBadge");
            if (badge) {{
                let hasWebGL = false;
                try {{
                    const testCanvas = document.createElement("canvas");
                    hasWebGL = !!(window.WebGLRenderingContext && (testCanvas.getContext("webgl") || testCanvas.getContext("experimental-webgl")));
                }} catch (e) {{}}
                badge.innerText = hasWebGL ? "WebGL / 3D Lattice" : "Software 3D Projection";
            }}
            if (!vp) return;
            vp.addEventListener("mousedown", e => {{
                if (e.target.tagName === "BUTTON") return;
                structuralCamera.isDragging = true;
                structuralCamera.lastX = e.clientX;
                structuralCamera.lastY = e.clientY;
            }});
            window.addEventListener("mousemove", e => {{
                if (!structuralCamera.isDragging) return;
                const dx = e.clientX - structuralCamera.lastX;
                const dy = e.clientY - structuralCamera.lastY;
                structuralCamera.lastX = e.clientX;
                structuralCamera.lastY = e.clientY;
                structuralCamera.yaw += dx * 0.008;
                structuralCamera.pitch = Math.max(-1.1, Math.min(1.1, structuralCamera.pitch + dy * 0.008));
                renderStructuralDiagram();
            }});
            window.addEventListener("mouseup", () => {{
                structuralCamera.isDragging = false;
            }});
            vp.addEventListener("wheel", e => {{
                e.preventDefault();
                const factor = e.deltaY < 0 ? 1.08 : 0.92;
                structuralCamera.zoom = Math.max(0.65, Math.min(1.85, structuralCamera.zoom * factor));
                renderStructuralDiagram();
            }}, {{ passive: false }});
        }}

        // ============================================================================
        // High-DPI Native Canvas & Chart.js Renderers (DESIGN.md §5 Palette & Gridlines)
        // ============================================================================
        function setupCanvasContext(canvas) {{
            if (!canvas) return null;
            const dpr = window.devicePixelRatio || 1;
            const rect = canvas.getBoundingClientRect();
            const width = rect.width || (canvas.parentElement && canvas.parentElement.clientWidth) || 320;
            const height = rect.height || (canvas.parentElement && canvas.parentElement.clientHeight) || 180;

            canvas.width = Math.floor(width * dpr);
            canvas.height = Math.floor(height * dpr);

            const ctx = canvas.getContext("2d");
            if (ctx.resetTransform) ctx.resetTransform();
            ctx.scale(dpr, dpr);
            return {{ ctx, width, height }};
        }}

        function drawNativeLineChart(canvasId, datasets, xLabels, options = {{}}) {{
            const canvas = document.getElementById(canvasId);
            const setup = setupCanvasContext(canvas);
            if (!setup) return;
            const {{ ctx, width, height }} = setup;
            const tokens = getThemeTokens();

            const padLeft = options.padLeft !== undefined ? options.padLeft : 48;
            const padRight = options.padRight !== undefined ? options.padRight : 14;
            const padTop = options.padTop !== undefined ? options.padTop : 16;
            const padBottom = options.padBottom !== undefined ? options.padBottom : 24;
            const plotW = width - padLeft - padRight;
            const plotH = height - padTop - padBottom;

            if (plotW <= 10 || plotH <= 10) return;

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

            const yTicks = options.yTicks || 4;
            ctx.font = "10px 'IBM Plex Mono', monospace";
            ctx.textAlign = "right";
            ctx.textBaseline = "middle";

            for (let i = 0; i <= yTicks; i++) {{
                const y = padTop + (plotH / yTicks) * i;
                const v = maxVal - (range / yTicks) * i;

                ctx.strokeStyle = tokens.gridLine;
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(padLeft, y);
                ctx.lineTo(padLeft + plotW, y);
                ctx.stroke();

                ctx.fillStyle = tokens.textSecondary;
                const fmtVal = Math.abs(v) < 10 ? v.toFixed(3) : v.toFixed(1);
                ctx.fillText(options.yPrefix ? options.yPrefix + fmtVal : fmtVal, padLeft - 6, y);
            }}

            datasets.forEach(ds => {{
                const pts = ds.data || [];
                if (pts.length < 2) return;
                const stepX = plotW / (pts.length - 1);

                if (ds.fill && ds.fillColor) {{
                    ctx.fillStyle = ds.fillColor;
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

                ctx.strokeStyle = ds.color || VIZ_PALETTE.teal;
                ctx.lineWidth = ds.lineWidth || 2;
                ctx.setLineDash(ds.dash || []);

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

            if (xLabels && xLabels.length > 0) {{
                ctx.fillStyle = tokens.textSecondary;
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
            const tokens = getThemeTokens();

            const cx = width / 2;
            const cy = height / 2;
            const radius = Math.min(cx, cy) - 36;
            if (radius <= 10) return;

            const keys = Object.keys(indicators);
            const numPoints = keys.length || 8;
            const angleStep = (Math.PI * 2) / numPoints;

            const rings = 4;
            for (let r = 1; r <= rings; r++) {{
                const ringRadius = (radius / rings) * r;
                ctx.strokeStyle = tokens.gridLine;
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

            ctx.font = "10.5px 'IBM Plex Mono', monospace";
            keys.forEach((k, i) => {{
                const ind = indicators[k];
                const label = ind.ratio_tickers || ind.display_name || k;
                const a = i * angleStep - Math.PI / 2;

                ctx.strokeStyle = tokens.gridLine;
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(cx, cy);
                ctx.lineTo(cx + Math.cos(a) * radius, cy + Math.sin(a) * radius);
                ctx.stroke();

                const lx = cx + Math.cos(a) * (radius + 16);
                const ly = cy + Math.sin(a) * (radius + 16);
                ctx.fillStyle = tokens.textSecondary;
                ctx.textAlign = Math.abs(Math.cos(a)) < 0.2 ? "center" : (Math.cos(a) > 0 ? "left" : "right");
                ctx.textBaseline = "middle";
                ctx.fillText(label, lx, ly);
            }});

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
                ctx.fillStyle = "rgba(13, 148, 136, 0.18)";
                ctx.strokeStyle = VIZ_PALETTE.teal;
                ctx.lineWidth = 2;
                ctx.beginPath();
                dataCoords.forEach((pt, i) => {{
                    if (i === 0) ctx.moveTo(pt.x, pt.y);
                    else ctx.lineTo(pt.x, pt.y);
                }});
                ctx.closePath();
                ctx.fill();
                ctx.stroke();

                ctx.fillStyle = VIZ_PALETTE.indigo;
                dataCoords.forEach(pt => {{
                    ctx.beginPath();
                    ctx.arc(pt.x, pt.y, 3.5, 0, Math.PI * 2);
                    ctx.fill();
                }});
            }}
        }}

        // Tab Switching (Preserves scroll/viewport state)
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

            requestAnimationFrame(() => {{
                setTimeout(() => {{
                    if (tabId === "overview") {{
                        renderRelationshipNodeMap();
                        renderStructuralDiagram();
                    }} else if (tabId === "charts") {{
                        initCharts();
                    }} else if (tabId === "playbook") {{
                        initPayoffChart();
                    }}
                }}, 30);
            }});
        }}

        function filterIndicators(filterType, btn) {{
            document.querySelectorAll("#tab-indicators .filter-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            document.querySelectorAll(".ind-card").forEach(card => {{
                if (filterType === "all" || card.getAttribute("data-trend") === filterType) {{
                    card.style.display = "flex";
                }} else {{
                    card.style.display = "none";
                }}
            }});
        }}

        function selectFocusIndicator(key) {{
            if (!INDICATORS_DATA[key]) return;
            currentFocusKey = key;
            const ind = INDICATORS_DATA[key];

            document.querySelectorAll(".macro-pill-btn").forEach(btn => {{
                btn.classList.toggle("active", btn.getAttribute("data-key") === key);
            }});

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
                const statusClass = ind.ma50_status.includes("Above") || ind.trend_signal.includes("Rising")
                    ? "trend-bullish"
                    : (ind.ma50_status.includes("Below") || ind.trend_signal.includes("Falling") ? "trend-bearish" : "trend-neutral");
                badgeEl.className = "badge " + statusClass;
            }}

            renderFocusChart(key);
        }}

        function renderFocusChart(key) {{
            const ind = INDICATORS_DATA[key];
            if (!ind) return;

            const dates = (ind.history_dates && ind.history_dates.length > 0)
                ? ind.history_dates
                : (HISTORY_DATA.dates || Array.from({{length: (ind.history || []).length}}, (_, i) => `D-${{ind.history.length - i}}`));
            const values = ind.history || [];
            const ma50 = ind.history_ma50 || [];

            const isBullish = ind.ma50_status.includes("Above") || ind.trend_signal.includes("Rising");
            const isBearish = ind.ma50_status.includes("Below") || ind.trend_signal.includes("Falling");
            const lineColor = isBullish ? VIZ_PALETTE.emerald : (isBearish ? VIZ_PALETTE.rose : VIZ_PALETTE.teal);
            const fillColor = isBullish ? "rgba(5, 150, 105, 0.10)" : (isBearish ? "rgba(225, 29, 72, 0.10)" : "rgba(13, 148, 136, 0.10)");

            if (hasChartJs) {{
                try {{
                    const tokens = getThemeTokens();
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
                                    tension: 0.12
                                }},
                                {{
                                    label: "50-Day MA",
                                    data: ma50.length > 0 ? ma50 : Array(values.length).fill(ind.ma50),
                                    borderColor: VIZ_PALETTE.amber,
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
                                x: {{ grid: {{ color: tokens.gridLine }}, ticks: {{ color: tokens.textSecondary, maxTicksLimit: 8 }} }},
                                y: {{ grid: {{ color: tokens.gridLine }}, ticks: {{ color: tokens.textSecondary }} }}
                            }},
                            plugins: {{
                                legend: {{ labels: {{ color: tokens.textSecondary }} }}
                            }}
                        }}
                    }});
                    return;
                }} catch (e) {{}}
            }}

            drawNativeLineChart("focusIndicatorChart", [
                {{ data: values, color: lineColor, fillColor: fillColor, fill: true, lineWidth: 2.2 }},
                {{ data: ma50, color: VIZ_PALETTE.amber, dash: [4, 4], lineWidth: 1.5 }}
            ], dates, {{ padLeft: 55, yTicks: 4 }});
        }}

        function initCharts() {{
            if (hasChartJs) {{
                try {{
                    initChartJsTrendCharts();
                    return;
                }} catch (e) {{}}
            }}
            renderAllNativeCharts();
        }}

        function renderAllNativeCharts() {{
            if (HISTORY_DATA.prices && HISTORY_DATA.prices.length > 0) {{
                drawNativeLineChart("priceChart", [
                    {{ data: HISTORY_DATA.prices, color: VIZ_PALETTE.teal, fillColor: "rgba(13, 148, 136, 0.12)", fill: true, lineWidth: 2 }},
                    {{ data: HISTORY_DATA.ma50, color: VIZ_PALETTE.indigo, lineWidth: 1.5 }},
                    {{ data: HISTORY_DATA.ma200, color: VIZ_PALETTE.amber, dash: [4, 4], lineWidth: 1.5 }}
                ], HISTORY_DATA.dates, {{ padLeft: 55, yPrefix: "$", yTicks: 5 }});
            }}

            drawNativeRadarChart("macroRadarChart", INDICATORS_DATA);
            renderFocusChart(currentFocusKey);

            for (const key in INDICATORS_DATA) {{
                const ind = INDICATORS_DATA[key];
                const isBullish = ind.ma50_status.includes("Above") || ind.trend_signal.includes("Rising");
                const isBearish = ind.ma50_status.includes("Below") || ind.trend_signal.includes("Falling");
                const lineColor = isBullish ? VIZ_PALETTE.emerald : (isBearish ? VIZ_PALETTE.rose : VIZ_PALETTE.teal);
                const fillColor = isBullish ? "rgba(5, 150, 105, 0.08)" : (isBearish ? "rgba(225, 29, 72, 0.08)" : "rgba(13, 148, 136, 0.08)");

                drawNativeLineChart(`chart_${{key}}`, [
                    {{ data: ind.history || [], color: lineColor, fillColor: fillColor, fill: true, lineWidth: 1.5 }},
                    {{ data: ind.history_ma50 || [], color: VIZ_PALETTE.amber, dash: [3, 3], lineWidth: 1 }}
                ], [], {{ padLeft: 38, padRight: 10, padTop: 10, padBottom: 10, yTicks: 3 }});
            }}
        }}

        function initChartJsTrendCharts() {{
            const tokens = getThemeTokens();

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
                                        borderColor: VIZ_PALETTE.teal,
                                        backgroundColor: "rgba(13, 148, 136, 0.10)",
                                        borderWidth: 2,
                                        fill: true,
                                        tension: 0.1
                                    }},
                                    {{
                                        label: "50-Day MA",
                                        data: HISTORY_DATA.ma50,
                                        borderColor: VIZ_PALETTE.indigo,
                                        borderWidth: 1.5,
                                        borderDash: [4, 4],
                                        fill: false
                                    }},
                                    {{
                                        label: "200-Day MA",
                                        data: HISTORY_DATA.ma200,
                                        borderColor: VIZ_PALETTE.amber,
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
                                    x: {{ grid: {{ color: tokens.gridLine }}, ticks: {{ color: tokens.textSecondary, maxTicksLimit: 8 }} }},
                                    y: {{ grid: {{ color: tokens.gridLine }}, ticks: {{ color: tokens.textSecondary }} }}
                                }},
                                plugins: {{
                                    legend: {{ labels: {{ color: tokens.textSecondary }} }}
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
                                backgroundColor: "rgba(13, 148, 136, 0.18)",
                                borderColor: VIZ_PALETTE.teal,
                                pointBackgroundColor: VIZ_PALETTE.indigo,
                                pointBorderColor: tokens.bgSurface,
                                pointHoverBackgroundColor: tokens.bgSurface,
                                pointHoverBorderColor: VIZ_PALETTE.teal
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {{
                                r: {{
                                    min: 0,
                                    max: 100,
                                    angleLines: {{ color: tokens.gridLine }},
                                    grid: {{ color: tokens.gridLine }},
                                    pointLabels: {{ color: tokens.textSecondary, font: {{ size: 10 }} }},
                                    ticks: {{ color: tokens.textSecondary, backdropColor: "transparent", stepSize: 25 }}
                                }}
                            }},
                            plugins: {{
                                legend: {{ labels: {{ color: tokens.textSecondary }} }}
                            }}
                        }}
                    }});
                }} else {{
                    radarChartInstance.resize();
                    radarChartInstance.update();
                }}
            }}

            if (!focusIndicatorChartInstance) {{
                renderFocusChart(currentFocusKey);
            }} else {{
                focusIndicatorChartInstance.resize();
                focusIndicatorChartInstance.update();
            }}

            initMacroIndicatorGridCharts(tokens);
        }}

        function initMacroIndicatorGridCharts(tokens) {{
            for (const key in INDICATORS_DATA) {{
                const ind = INDICATORS_DATA[key];
                const canvas = document.getElementById(`chart_${{key}}`);
                if (!canvas) continue;

                if (indicatorChartInstances[key]) {{
                    indicatorChartInstances[key].resize();
                    indicatorChartInstances[key].update();
                    continue;
                }}

                const dates = (ind.history_dates && ind.history_dates.length > 0)
                    ? ind.history_dates
                    : Array.from({{length: (ind.history || []).length}}, (_, i) => `${{i + 1}}`);
                const values = ind.history || [];
                const ma50 = ind.history_ma50 || [];

                const isBullish = ind.ma50_status.includes("Above") || ind.trend_signal.includes("Rising");
                const isBearish = ind.ma50_status.includes("Below") || ind.trend_signal.includes("Falling");
                const lineColor = isBullish ? VIZ_PALETTE.emerald : (isBearish ? VIZ_PALETTE.rose : VIZ_PALETTE.teal);
                const fillColor = isBullish ? "rgba(5, 150, 105, 0.08)" : (isBearish ? "rgba(225, 29, 72, 0.08)" : "rgba(13, 148, 136, 0.08)");

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
                                borderColor: VIZ_PALETTE.amber,
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
                                grid: {{ color: tokens.gridLine }},
                                ticks: {{ color: tokens.textSecondary, font: {{ size: 9 }}, maxTicksLimit: 4 }}
                            }}
                        }},
                        plugins: {{
                            legend: {{ display: false }}
                        }}
                    }}
                }});
            }}
        }}

        // Option Chain Filtering
        function filterOptionChain(filterType, btn) {{
            document.querySelectorAll("#tab-playbook .filter-btn").forEach(b => b.classList.remove("active"));
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

        // Options Payoff Simulator
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
                }} catch (e) {{}}
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

            const tokens = getThemeTokens();
            const ctx = canvas.getContext("2d");
            payoffChartInstance = new Chart(ctx, {{
                type: "line",
                data: {{
                    labels: [],
                    datasets: [
                        {{
                            label: "Strategy Net P&L ($)",
                            data: [],
                            borderColor: VIZ_PALETTE.emerald,
                            backgroundColor: "rgba(5, 150, 105, 0.12)",
                            borderWidth: 2.2,
                            fill: true,
                            tension: 0.1
                        }},
                        {{
                            label: "Zero Breakeven Line",
                            data: [],
                            borderColor: tokens.textSecondary,
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
                            title: {{ display: true, text: "Underlying Stock Price at Expiration ($)", color: tokens.textSecondary }},
                            grid: {{ color: tokens.gridLine }},
                            ticks: {{ color: tokens.textSecondary, maxTicksLimit: 12 }}
                        }},
                        y: {{
                            title: {{ display: true, text: "Strategy Total P&L ($ per contract)", color: tokens.textSecondary }},
                            grid: {{ color: tokens.gridLine }},
                            ticks: {{ color: tokens.textSecondary }}
                        }}
                    }},
                    plugins: {{
                        legend: {{ labels: {{ color: tokens.textSecondary }} }}
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
            let statusColor = VIZ_PALETTE.emerald;
            let rocPct = 0;

            if (currentSimStrategy === "CC") {{
                breakeven = stockCost - premium;
                if (simPrice >= strike) {{
                    dollarPnL = (strike - stockCost + premium) * 100.0;
                    statusText = "Max Profit (Called Away at Strike)";
                    statusColor = VIZ_PALETTE.emerald;
                }} else {{
                    dollarPnL = (simPrice - stockCost + premium) * 100.0;
                    if (simPrice >= breakeven) {{
                        statusText = "Profitable (Cushioned by Premium)";
                        statusColor = VIZ_PALETTE.teal;
                    }} else {{
                        statusText = "Downside Loss (Cushioned vs Stock)";
                        statusColor = VIZ_PALETTE.rose;
                    }}
                }}
                rocPct = (dollarPnL / (stockCost * 100.0)) * 100.0;
            }} else {{
                breakeven = strike - premium;
                if (simPrice >= strike) {{
                    dollarPnL = premium * 100.0;
                    statusText = "Max Profit (Unassigned, Credit Kept)";
                    statusColor = VIZ_PALETTE.emerald;
                }} else {{
                    dollarPnL = (premium - (strike - simPrice)) * 100.0;
                    if (simPrice >= breakeven) {{
                        statusText = "Profitable (Assigned Below Spot)";
                        statusColor = VIZ_PALETTE.teal;
                    }} else {{
                        statusText = "Assigned Below Net Breakeven";
                        statusColor = VIZ_PALETTE.rose;
                    }}
                }}
                rocPct = (dollarPnL / (strike * 100.0)) * 100.0;
            }}

            const pnlSign = dollarPnL >= 0 ? "+$" : "-$";
            const pnlEl = document.getElementById("simDollarPnL");
            pnlEl.innerText = pnlSign + Math.abs(dollarPnL).toFixed(2);
            pnlEl.style.color = dollarPnL >= 0 ? VIZ_PALETTE.emerald : VIZ_PALETTE.rose;

            const rocSign = rocPct >= 0 ? "+" : "";
            const rocEl = document.getElementById("simROCPct");
            rocEl.innerText = rocSign + rocPct.toFixed(2) + "%";
            rocEl.style.color = rocPct >= 0 ? VIZ_PALETTE.emerald : VIZ_PALETTE.rose;

            document.getElementById("simBreakeven").innerText = "$" + breakeven.toFixed(2);
            const statusEl = document.getElementById("simPnLStatus");
            statusEl.innerText = statusText;
            statusEl.style.color = statusColor;

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
                    pnl = p >= strike ? (strike - stockCost + premium) * 100.0 : (p - stockCost + premium) * 100.0;
                }} else {{
                    pnl = p >= strike ? premium * 100.0 : (premium - (strike - p)) * 100.0;
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
                    {{ data: pnlValues.map(v => parseFloat(v)), color: VIZ_PALETTE.emerald, fillColor: "rgba(5, 150, 105, 0.14)", fill: true, lineWidth: 2.2 }},
                    {{ data: zeroLine, color: VIZ_PALETTE.amber, dash: [4, 4], lineWidth: 1 }}
                ], prices, {{ padLeft: 60, yPrefix: "$", yTicks: 5 }});
            }}
        }}

        function updateChartTheme() {{
            const tokens = getThemeTokens();
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
                        if (chart.options.scales.x && chart.options.scales.x.grid) chart.options.scales.x.grid.color = tokens.gridLine;
                        if (chart.options.scales.x && chart.options.scales.x.ticks) chart.options.scales.x.ticks.color = tokens.textSecondary;
                        if (chart.options.scales.y && chart.options.scales.y.grid) chart.options.scales.y.grid.color = tokens.gridLine;
                        if (chart.options.scales.y && chart.options.scales.y.ticks) chart.options.scales.y.ticks.color = tokens.textSecondary;
                        if (chart.options.scales.r) {{
                            if (chart.options.scales.r.angleLines) chart.options.scales.r.angleLines.color = tokens.gridLine;
                            if (chart.options.scales.r.grid) chart.options.scales.r.grid.color = tokens.gridLine;
                            if (chart.options.scales.r.pointLabels) chart.options.scales.r.pointLabels.color = tokens.textSecondary;
                            if (chart.options.scales.r.ticks) chart.options.scales.r.ticks.color = tokens.textSecondary;
                        }}
                    }}
                    if (chart.options.plugins && chart.options.plugins.legend && chart.options.plugins.legend.labels) {{
                        chart.options.plugins.legend.labels.color = tokens.textSecondary;
                    }}
                    chart.update();
                }}
            }});
        }}

        // ============================================================================
        // Dynamic State Updates & Server-Sent Events (SSE) Support (DESIGN.md §2 & §6)
        // Updates data in-place without resetting scroll position, active tab, or camera state
        // ============================================================================
        function appendTelemetryLog(message) {{
            const logEl = document.getElementById("telemetryEventLog");
            if (!logEl) return;
            const nowStr = new Date().toISOString().replace("T", " ").slice(0, 19) + " UTC";
            const row = document.createElement("div");
            row.innerText = `[${{nowStr}}] ${{message}}`;
            logEl.prepend(row);
        }}

        window.updateDashboardData = function(payload) {{
            if (!payload || typeof payload !== "object") return;
            if (payload.ticker_info) {{
                TICKER_INFO = {{ ...TICKER_INFO, ...payload.ticker_info }};
                CURRENT_PRICE = parseFloat(TICKER_INFO.current_price || CURRENT_PRICE);
                if (TICKER_INFO.price_history) HISTORY_DATA = TICKER_INFO.price_history;
            }}
            if (payload.macro_indicators) {{
                INDICATORS_DATA = {{ ...INDICATORS_DATA, ...payload.macro_indicators }};
            }}
            if (payload.decision) {{
                DECISION_DATA = {{ ...DECISION_DATA, ...payload.decision }};
            }}
            if (payload.options_playbook) {{
                PLAYBOOK_DATA = {{ ...PLAYBOOK_DATA, ...payload.options_playbook }};
            }}

            // Update Executive Bento DOM in-place
            const symEl = document.getElementById("execTickerSymbol");
            if (symEl && TICKER_INFO.ticker) symEl.innerText = TICKER_INFO.ticker;
            const prEl = document.getElementById("execTickerPrice");
            if (prEl) prEl.innerText = "$" + CURRENT_PRICE.toFixed(2);
            const chgEl = document.getElementById("execTickerChange");
            if (chgEl && TICKER_INFO.change_pct !== undefined) {{
                const chg = parseFloat(TICKER_INFO.change_pct);
                chgEl.innerText = (chg >= 0 ? "+" : "") + chg.toFixed(2) + "%";
                chgEl.className = "ticker-change font-mono " + (chg >= 0 ? "state-positive" : "state-critical");
            }}
            const alignEl = document.getElementById("execAlignmentScore");
            if (alignEl && DECISION_DATA.alignment_score !== undefined) {{
                const sc = parseFloat(DECISION_DATA.alignment_score);
                alignEl.innerText = (sc >= 0 ? "+" : "") + sc.toFixed(1) + " / 100";
            }}

            // Re-render visualizers without resetting scroll or camera state
            renderHeatmapMatrix();
            renderRelationshipNodeMap();
            renderStructuralDiagram();
            if (hasChartJs) {{
                if (priceChartInstance && HISTORY_DATA.prices) {{
                    priceChartInstance.data.labels = HISTORY_DATA.dates;
                    priceChartInstance.data.datasets[0].data = HISTORY_DATA.prices;
                    priceChartInstance.data.datasets[1].data = HISTORY_DATA.ma50;
                    priceChartInstance.data.datasets[2].data = HISTORY_DATA.ma200;
                    priceChartInstance.update("none");
                }}
                renderFocusChart(currentFocusKey);
            }} else {{
                renderAllNativeCharts();
            }}
            updateSimPayoff();
            appendTelemetryLog(`[LIVE-UPDATE] Incremental state refresh applied for ${{TICKER_INFO.ticker || 'equity'}} @ $${{CURRENT_PRICE.toFixed(2)}} (viewport & camera preserved).`);
        }};

        function triggerIncrementalStateRefresh() {{
            window.updateDashboardData({{
                ticker_info: {{
                    current_price: CURRENT_PRICE,
                    change_pct: TICKER_INFO.change_pct
                }}
            }});
        }}

        function initLiveSSEStream() {{
            if (typeof EventSource === "undefined" || window.location.protocol === "file:") return;
            try {{
                const sseUrl = new URLSearchParams(window.location.search).get("sse") || "/events";
                const es = new EventSource(sseUrl);
                es.onopen = () => {{
                    appendTelemetryLog(`[SSE] Connected to live telemetry stream (${{sseUrl}}).`);
                }};
                es.onmessage = evt => {{
                    try {{
                        const data = JSON.parse(evt.data);
                        window.updateDashboardData(data);
                    }} catch (err) {{}}
                }};
                es.onerror = () => {{
                    es.close();
                }};
            }} catch (e) {{}}
        }}

        // Window Resize Observer
        window.addEventListener("resize", () => {{
            renderStructuralDiagram();
            if (hasChartJs) {{
                [priceChartInstance, radarChartInstance, focusIndicatorChartInstance, payoffChartInstance, ...Object.values(indicatorChartInstances)].forEach(chart => {{
                    if (chart) chart.resize();
                }});
            }} else {{
                renderAllNativeCharts();
            }}
        }});

        // Initialize Dashboard on DOM Ready
        document.addEventListener("DOMContentLoaded", () => {{
            let savedMode = "system";
            try {{
                savedMode = localStorage.getItem("mf_theme_mode") || "system";
            }} catch (e) {{}}
            setThemeMode(savedMode);
            initNodeMapInteractions();
            initStructuralDiagramInteractions();
            initLiveSSEStream();
            setTimeout(() => {{
                renderHeatmapMatrix();
                renderRelationshipNodeMap();
                renderStructuralDiagram();
                if (!hasChartJs) renderAllNativeCharts();
            }}, 40);
        }});
    </script>
</body>
</html>"""
        return html_doc
