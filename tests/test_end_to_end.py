import pytest
from scripts.run_analysis import run_navigator

def test_end_to_end_markdown():
    output = run_navigator(ticker="GOOG", lookback_days=60, output_format="markdown")
    assert "# Macro Flow Stock Navigator: GOOG" in output
    assert "Recommended Action" in output
    assert "Macro Cross-Asset Indicators" in output
    assert "Options Volatility & Market Indicators" in output
    assert "Options Selling Playbook: Covered Calls & Cash-Secured Puts" in output
    assert "Covered Call Screener Matrix" in output
    assert "Cash-Secured Put Screener Matrix" in output
    assert "Conservative (0.20Δ)" in output
    assert "Balanced (0.30Δ)" in output
    assert "Aggressive (0.40Δ)" in output

def test_end_to_end_json():
    import json
    output_json = run_navigator(ticker="SOFI", lookback_days=60, output_format="json")
    data_dict = json.loads(output_json)
    assert data_dict["metadata"]["skill"] == "macro-flow-stock-navigator"
    assert data_dict["ticker_info"]["ticker"] == "SOFI"
    assert "decision" in data_dict
    assert "macro_indicators" in data_dict
    
    # Options Playbook validation
    playbook = data_dict["options_playbook"]
    assert "covered_call_matrix" in playbook
    assert "cash_secured_put_matrix" in playbook
    assert "options_analytics" in playbook
    assert "unusual_activity" in playbook
    assert "options_chain" in playbook
    
    analytics = playbook["options_analytics"]
    assert "iv_atm" in analytics
    assert "hv_30d" in analytics
    assert "iv_rv_spread" in analytics
    assert "max_pain_strike" in analytics
    assert "expected_move_30d" in analytics

def test_end_to_end_html():
    output_html = run_navigator(ticker="GOOG", lookback_days=60, output_format="html")
    assert "<!DOCTYPE html>" in output_html
    assert "Macro Flow Stock Navigator: GOOG" in output_html
    assert "toggleTheme" in output_html
    assert "data-theme=" in output_html
    assert "priceChart" in output_html
    assert "payoffChart" in output_html
    assert "macroRadarChart" in output_html
    assert "focusIndicatorChart" in output_html
    assert "focusVisualizerCard" in output_html
    assert "indicatorChartsGrid" in output_html
    assert "Selling Covered Calls Screener" in output_html
    assert "Selling Cash-Secured Puts Screener" in output_html
    assert "uoaTable" in output_html
    assert "optionsChainTable" in output_html
    assert "setSimulatorStrategy" in output_html
    assert "loadIntoSimulator" in output_html
    
    # Verify all 8 Macro Indicators have chart canvases in HTML
    macro_keys = [
        "chart_RSP_SPY",
        "chart_GLD_SPX",
        "chart_NDX_SPX",
        "chart_IWM_SPY",
        "chart_SPX_GDP",
        "chart_SPHB_SPLV",
        "chart_XLY_XLP",
        "chart_VIX_SPX"
    ]
    for key in macro_keys:
        assert key in output_html


