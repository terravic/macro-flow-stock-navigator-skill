"""
UI Dashboard Renderer.
Renders concise, executive Markdown dashboards and structured JSON payloads.
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
        decision: Dict[str, Any]
    ) -> str:
        """
        Builds a concise, business-like Markdown response.
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
        warnings = playbook.get("risk_warnings", [])
        
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
        lines.append(f"| **Macro Regime** | {macro_regime.get('name', 'Balanced Rotation')} | **Timestamp** | {timestamp_str} |")
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
            lines.append(f"- {w}")

        lines.append("")
        lines.append("---")
        lines.append("*Disclaimer: Macro Flow Stock Navigator is an analytical decision-support tool. Not personalized financial or investment advice. Always evaluate position sizing and liquidity before executing trades.*")

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
        decision: Dict[str, Any]
    ) -> str:
        """
        Builds a rich, interactive HTML/JS/CSS Canvas Dashboard.
        Includes light/dark theme toggle, interactive charts, metric filters,
        and an options payoff simulator.
        """
        ticker = ticker_info.get("ticker", "UNKNOWN")
        price = ticker_info.get("current_price", 0.0)
        chg = ticker_info.get("change_pct", 0.0)
        chg_str = f"+{chg:.2f}%" if chg >= 0 else f"{chg:.2f}%"
        chg_class = "positive" if chg >= 0 else "negative"
        
        action_badge = decision.get("signal_badge", "NEUTRAL")
        signal_key = decision.get("stock_signal", "NEUTRAL")
        archetype_name = decision.get("archetype_name", "General Stock")
        archetype_desc = ticker_info.get("archetype_desc", "")
        alignment_score = decision.get("alignment_score", 0.0)
        conviction = decision.get("conviction", "MODERATE")
        macro_regime = decision.get("macro_regime", {})
        playbook = decision.get("options_playbook", {})
        tactical = playbook.get("tactical_execution", {})
        warnings = playbook.get("risk_warnings", [])
        
        favorable = decision.get("favorable_forces", [])
        hostile = decision.get("hostile_forces", [])
        
        price_history = ticker_info.get("price_history", {
            "dates": [],
            "prices": [],
            "ma50": [],
            "ma200": []
        })

        # Format indicator data for JS injection
        indicators_json = json.dumps(indicators)
        history_json = json.dumps(price_history)
        decision_json = json.dumps(decision)
        ticker_json = json.dumps(ticker_info)

        # Indicator cards HTML
        ind_cards_html = []
        for ind_id, ind in indicators.items():
            name = ind.get("display_name", ind_id)
            ratio = ind.get("ratio_tickers", ind_id)
            val = ind.get("current_value", 0.0)
            ma_stat = ind.get("ma50_status", "N/A")
            trend = ind.get("trend_signal", "Flat")
            meaning = ind.get("market_meaning", "")
            percentile = ind.get("percentile_90d", 50.0)
            status_class = "trend-bullish" if "Above" in ma_stat or "Rising" in trend else ("trend-bearish" if "Below" in ma_stat or "Falling" in trend else "trend-neutral")
            
            ind_cards_html.append(f"""
            <div class="ind-card" data-trend="{status_class}">
                <div class="ind-card-header">
                    <div>
                        <div class="ind-card-title">{name}</div>
                        <div class="ind-card-ratio">{ratio}</div>
                    </div>
                    <span class="badge {status_class}">{trend}</span>
                </div>
                <div class="ind-card-body">
                    <div class="ind-metric-row">
                        <span class="label">Current Value</span>
                        <span class="val font-mono">{val:.4f}</span>
                    </div>
                    <div class="ind-metric-row">
                        <span class="label">50-MA Status</span>
                        <span class="val">{ma_stat}</span>
                    </div>
                    <div class="ind-metric-row">
                        <span class="label">90d Percentile</span>
                        <span class="val">{percentile:.1f}%</span>
                    </div>
                    <div class="progress-track">
                        <div class="progress-bar" style="width: {min(100, max(0, percentile))}%;"></div>
                    </div>
                    <div class="ind-meaning">{meaning}</div>
                </div>
            </div>
            """)

        ind_cards_rendered = "\n".join(ind_cards_html)

        # HTML template
        html_doc = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Macro Flow Stock Navigator: {ticker}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
            max-width: 1280px;
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
        }}

        td {{
            padding: 12px 14px;
            border-bottom: 1px solid var(--border-color);
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
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
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

        /* Filters */
        .filter-group {{
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
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
            <button id="themeToggleBtn" class="theme-toggle-btn" onclick="toggleTheme()">
                <span id="themeLabel">Theme: Dark</span>
            </button>
        </div>
    </header>

    <div class="container">
        
        <!-- Executive Banner -->
        <div class="executive-banner">
            <div>
                <div class="ticker-profile">
                    <span class="ticker-symbol">{ticker}</span>
                    <span class="ticker-price">${price:.2f}</span>
                    <span class="ticker-change {chg_class}">{chg_str}</span>
                </div>
                <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">
                    {archetype_name} &bull; {macro_regime.get('name', 'Balanced Rotation')}
                </div>
            </div>

            <div class="banner-metrics">
                <div class="metric-pill">
                    <span class="label">Action Signal</span>
                    <span class="badge badge-signal-{('buy' if 'BUY' in signal_key or 'ACCUMULATE' in signal_key else ('sell' if 'SELL' in signal_key or 'TRIM' in signal_key else 'neutral'))}">
                        {action_badge}
                    </span>
                </div>

                <div class="metric-pill">
                    <span class="label">Macro Alignment</span>
                    <span class="val font-mono" style="color: {( 'var(--accent-green)' if alignment_score > 10 else ('var(--accent-red)' if alignment_score < -10 else 'var(--accent-amber)') )};">
                        {alignment_score:+.1f} / 100
                    </span>
                </div>

                <div class="metric-pill">
                    <span class="label">Conviction</span>
                    <span class="val">{conviction}</span>
                </div>

                <div class="metric-pill">
                    <span class="label">RSI (14)</span>
                    <span class="val font-mono">{ticker_info.get('rsi_14', 50.0)}</span>
                </div>

                <div class="metric-pill">
                    <span class="label">30d Volatility</span>
                    <span class="val font-mono">{ticker_info.get('historical_vol_30d', 0.0)}%</span>
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
                        <div class="tactical-cell">
                            <div class="label">50-Day MA</div>
                            <div class="val font-mono">${ticker_info.get('ma50', 0.0):.2f} ({ticker_info.get('diff_ma50_pct', 0.0):+.2f}%)</div>
                        </div>
                        <div class="tactical-cell">
                            <div class="label">200-Day MA</div>
                            <div class="val font-mono">${ticker_info.get('ma200', 0.0):.2f} ({ticker_info.get('diff_ma200_pct', 0.0):+.2f}%)</div>
                        </div>
                        <div class="tactical-cell">
                            <div class="label">Beta (vs SPY)</div>
                            <div class="val font-mono">{ticker_info.get('beta', 1.0)}</div>
                        </div>
                        <div class="tactical-cell">
                            <div class="label">30d Realized Vol</div>
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

            <!-- Quick Playbook Summary -->
            <div class="playbook-hero">
                <div style="font-size: 12px; color: var(--accent-blue); font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">
                    Recommended Options Strategy
                </div>
                <div class="playbook-strategy-name">{tactical.get('strategy', 'Neutral Options Overlay')}</div>
                <div class="playbook-rationale">{tactical.get('rationale', '')}</div>
                <div class="tactical-grid">
                    <div class="tactical-cell">
                        <div class="label">Target Strike</div>
                        <div class="val font-mono">{tactical.get('optimal_strike', 'N/A')}</div>
                    </div>
                    <div class="tactical-cell">
                        <div class="label">Target Delta</div>
                        <div class="val font-mono">{tactical.get('recommended_delta', 'N/A')}</div>
                    </div>
                    <div class="tactical-cell">
                        <div class="label">Target DTE</div>
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

        <!-- TAB 3: CHARTS & TRENDS -->
        <div id="tab-charts" class="tab-content">
            <div class="grid-2">
                <div class="card">
                    <div class="card-header">
                        <div>
                            <div class="card-title">{ticker} Price Trend & Moving Averages</div>
                            <div class="card-desc">Daily Close vs 50-MA & 200-MA</div>
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
                            <div class="card-desc">90-Day Cross-Asset Percentile Distribution</div>
                        </div>
                    </div>
                    <div class="chart-container">
                        <canvas id="macroRadarChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 4: OPTIONS PLAYBOOK & SIMULATOR -->
        <div id="tab-playbook" class="tab-content">
            <div class="playbook-hero">
                <div style="font-size: 12px; color: var(--accent-blue); font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">
                    Strategic Options Specification
                </div>
                <div class="playbook-strategy-name">{tactical.get('strategy', 'Neutral Options Overlay')}</div>
                <div class="playbook-rationale">{tactical.get('rationale', '')}</div>
                
                <div class="tactical-grid" style="margin-top: 16px;">
                    <div class="tactical-cell">
                        <div class="label">Target Strike</div>
                        <div class="val font-mono">{tactical.get('optimal_strike', 'N/A')}</div>
                    </div>
                    <div class="tactical-cell">
                        <div class="label">Target Delta</div>
                        <div class="val font-mono">{tactical.get('recommended_delta', 'N/A')}</div>
                    </div>
                    <div class="tactical-cell">
                        <div class="label">Target DTE</div>
                        <div class="val font-mono">{tactical.get('target_dte', '30-45 DTE')}</div>
                    </div>
                    <div class="tactical-cell">
                        <div class="label">Target Return</div>
                        <div class="val font-mono">{tactical.get('estimated_annualized_yield', 'N/A')}</div>
                    </div>
                    <div class="tactical-cell">
                        <div class="label">Profit Target</div>
                        <div class="val font-mono">{tactical.get('profit_target', '50% of max')}</div>
                    </div>
                    <div class="tactical-cell">
                        <div class="label">Stop Loss Rule</div>
                        <div class="val font-mono">{tactical.get('stop_loss_rule', '2x credit')}</div>
                    </div>
                </div>
            </div>

            <!-- Interactive Payoff Simulator -->
            <div class="card">
                <div class="card-header">
                    <div>
                        <div class="card-title">Interactive Strategy Payoff Simulator</div>
                        <div class="card-desc">Simulate trade performance at expiration based on simulated price changes</div>
                    </div>
                </div>

                <div class="slider-control">
                    <label for="priceSlider" style="font-weight: 600; min-width: 140px;">Simulated Price:</label>
                    <input type="range" id="priceSlider" min="{max(1.0, round(price * 0.7, 1))}" max="{round(price * 1.3, 1)}" step="0.5" value="{round(price, 1)}" oninput="updateSimPayoff()">
                    <span id="sliderPriceDisplay" class="font-mono" style="font-size: 16px; font-weight: 700; min-width: 80px;">${price:.2f}</span>
                </div>

                <div class="tactical-grid" style="margin-bottom: 20px;">
                    <div class="tactical-cell">
                        <div class="label">Simulated Move</div>
                        <div id="simPriceMove" class="val font-mono">0.0%</div>
                    </div>
                    <div class="tactical-cell">
                        <div class="label">Simulated P&L Status</div>
                        <div id="simPnLStatus" class="val font-mono">Max Profit</div>
                    </div>
                    <div class="tactical-cell">
                        <div class="label">Breakeven Price</div>
                        <div id="simBreakeven" class="val font-mono">${price * 0.95:.2f}</div>
                    </div>
                </div>

                <div class="chart-container">
                    <canvas id="payoffChart"></canvas>
                </div>
            </div>

            <!-- Risk Warnings -->
            <div class="card" style="margin-top: 20px;">
                <div class="card-header">
                    <div class="card-title">Risk Considerations & Trade Management</div>
                </div>
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    {''.join([f'<div style="font-size: 13px; color: var(--text-secondary);">&bull; {w}</div>' for w in warnings])}
                </div>
            </div>
        </div>

    </div>

    <footer>
        Macro Flow Stock Navigator &bull; Analytical decision-support tool &bull; Real-time public market data feeds
    </footer>

    <script>
        // Global Datasets
        const CURRENT_PRICE = {price};
        const TICKER_INFO = {ticker_json};
        const INDICATORS_DATA = {indicators_json};
        const HISTORY_DATA = {history_json};
        const DECISION_DATA = {decision_json};
        
        let currentTheme = localStorage.getItem("mf_theme") || "dark";
        let priceChartInstance = null;
        let radarChartInstance = null;
        let payoffChartInstance = null;

        // Theme Toggle
        function applyTheme(theme) {{
            currentTheme = theme;
            document.documentElement.setAttribute("data-theme", theme);
            document.getElementById("themeLabel").innerText = theme === "dark" ? "Theme: Dark" : "Theme: Light";
            localStorage.setItem("mf_theme", theme);
            updateChartTheme();
        }}

        function toggleTheme() {{
            applyTheme(currentTheme === "dark" ? "light" : "dark");
        }}

        // Tab Switching
        function switchTab(tabId) {{
            document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach(content => content.classList.remove("active"));
            
            const activeBtn = Array.from(document.querySelectorAll(".tab-btn")).find(btn => btn.getAttribute("onclick").includes(tabId));
            if (activeBtn) activeBtn.classList.add("active");
            
            const activeContent = document.getElementById("tab-" + tabId);
            if (activeContent) activeContent.classList.add("active");

            if (tabId === "charts") {{
                initCharts();
            }} else if (tabId === "playbook") {{
                initPayoffChart();
            }}
        }}

        // Indicator Card Filtering
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

        // Initialize Price & Macro Charts
        function initCharts() {{
            if (typeof Chart === "undefined") return;

            const isDark = currentTheme === "dark";
            const textColor = isDark ? "#94a3b8" : "#475569";
            const gridColor = isDark ? "#243046" : "#e2e8f0";

            // 1. Price Chart
            if (!priceChartInstance && HISTORY_DATA.dates && HISTORY_DATA.dates.length > 0) {{
                const ctxPrice = document.getElementById("priceChart").getContext("2d");
                priceChartInstance = new Chart(ctxPrice, {{
                    type: "line",
                    data: {{
                        labels: HISTORY_DATA.dates,
                        datasets: [
                            {{
                                label: "Close Price",
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
            }}

            // 2. Macro Radar Chart
            if (!radarChartInstance) {{
                const ctxRadar = document.getElementById("macroRadarChart").getContext("2d");
                const labels = [];
                const percentiles = [];
                for (const k in INDICATORS_DATA) {{
                    labels.push(INDICATORS_DATA[k].display_name);
                    percentiles.push(INDICATORS_DATA[k].percentile_90d);
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
                                angleLines: {{ color: gridColor }},
                                grid: {{ color: gridColor }},
                                pointLabels: {{ color: textColor, font: {{ size: 11 }} }},
                                ticks: {{ color: textColor, backdropColor: "transparent", min: 0, max: 100 }}
                            }}
                        }},
                        plugins: {{
                            legend: {{ labels: {{ color: textColor }} }}
                        }}
                    }}
                }});
            }}
        }}

        // Payoff Chart
        function initPayoffChart() {{
            if (typeof Chart === "undefined" || payoffChartInstance) return;

            const isDark = currentTheme === "dark";
            const textColor = isDark ? "#94a3b8" : "#475569";
            const gridColor = isDark ? "#243046" : "#e2e8f0";

            const low = CURRENT_PRICE * 0.75;
            const high = CURRENT_PRICE * 1.25;
            const step = (high - low) / 30;
            const prices = [];
            const pnl = [];
            const strike = CURRENT_PRICE * 0.94;
            const premium = CURRENT_PRICE * 0.025;

            for (let p = low; p <= high; p += step) {{
                prices.push(p.toFixed(2));
                let profit = 0;
                // Default Cash-Secured Put simulation
                if (p >= strike) {{
                    profit = premium;
                }} else {{
                    profit = premium - (strike - p);
                }}
                pnl.push((profit * 100).toFixed(2));
            }}

            const ctx = document.getElementById("payoffChart").getContext("2d");
            payoffChartInstance = new Chart(ctx, {{
                type: "line",
                data: {{
                    labels: prices,
                    datasets: [{{
                        label: "Option Strategy P&L ($ per contract)",
                        data: pnl,
                        borderColor: "#10b981",
                        backgroundColor: "rgba(16, 185, 129, 0.1)",
                        fill: true,
                        tension: 0.1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        x: {{
                            title: {{ display: true, text: "Stock Price at Expiration ($)", color: textColor }},
                            grid: {{ color: gridColor }},
                            ticks: {{ color: textColor, maxTicksLimit: 10 }}
                        }},
                        y: {{
                            title: {{ display: true, text: "P&L ($)", color: textColor }},
                            grid: {{ color: gridColor }},
                            ticks: {{ color: textColor }}
                        }}
                    }},
                    plugins: {{
                        legend: {{ labels: {{ color: textColor }} }}
                    }}
                }}
            }});
        }}

        function updateSimPayoff() {{
            const slider = document.getElementById("priceSlider");
            const simPrice = parseFloat(slider.value);
            document.getElementById("sliderPriceDisplay").innerText = "$" + simPrice.toFixed(2);
            
            const pctChange = ((simPrice - CURRENT_PRICE) / CURRENT_PRICE) * 100;
            const sign = pctChange >= 0 ? "+" : "";
            document.getElementById("simPriceMove").innerText = sign + pctChange.toFixed(2) + "%";
            
            const strike = CURRENT_PRICE * 0.94;
            const breakeven = strike - (CURRENT_PRICE * 0.025);
            document.getElementById("simBreakeven").innerText = "$" + breakeven.toFixed(2);
            
            if (simPrice >= strike) {{
                document.getElementById("simPnLStatus").innerText = "Max Profit (100% Retained)";
                document.getElementById("simPnLStatus").style.color = "var(--accent-green)";
            }} else if (simPrice >= breakeven) {{
                document.getElementById("simPnLStatus").innerText = "Profitable / Breakeven Zone";
                document.getElementById("simPnLStatus").style.color = "var(--accent-amber)";
            }} else {{
                document.getElementById("simPnLStatus").innerText = "Assignment / Hedged Zone";
                document.getElementById("simPnLStatus").style.color = "var(--accent-red)";
            }}
        }}

        function updateChartTheme() {{
            const isDark = currentTheme === "dark";
            const textColor = isDark ? "#94a3b8" : "#475569";
            const gridColor = isDark ? "#243046" : "#e2e8f0";

            [priceChartInstance, radarChartInstance, payoffChartInstance].forEach(chart => {{
                if (chart) {{
                    if (chart.options.scales.x) {{
                        chart.options.scales.x.grid.color = gridColor;
                        chart.options.scales.x.ticks.color = textColor;
                    }}
                    if (chart.options.scales.y) {{
                        chart.options.scales.y.grid.color = gridColor;
                        chart.options.scales.y.ticks.color = textColor;
                    }}
                    if (chart.options.scales.r) {{
                        chart.options.scales.r.angleLines.color = gridColor;
                        chart.options.scales.r.grid.color = gridColor;
                        chart.options.scales.r.pointLabels.color = textColor;
                        chart.options.scales.r.ticks.color = textColor;
                    }}
                    if (chart.options.plugins && chart.options.plugins.legend) {{
                        chart.options.plugins.legend.labels.color = textColor;
                    }}
                    chart.update();
                }}
            }});
        }}

        // Initialize on load
        document.addEventListener("DOMContentLoaded", () => {{
            applyTheme(currentTheme);
        }});
    </script>
</body>
</html>"""
        return html_doc

