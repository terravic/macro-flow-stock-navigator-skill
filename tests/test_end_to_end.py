import pytest
from scripts.run_analysis import run_navigator

def test_end_to_end_markdown():
    output = run_navigator(ticker="GOOG", lookback_days=60, output_format="markdown")
    assert "# Macro Flow Stock Navigator: GOOG" in output
    assert "Recommended Action" in output
    assert "Macro Cross-Asset Indicators" in output
    assert "Strategic Options Playbook" in output
    assert "Target Delta" in output

def test_end_to_end_json():
    import json
    output_json = run_navigator(ticker="SOFI", lookback_days=60, output_format="json")
    data_dict = json.loads(output_json)
    assert data_dict["metadata"]["skill"] == "macro-flow-stock-navigator"
    assert data_dict["ticker_info"]["ticker"] == "SOFI"
    assert "decision" in data_dict
    assert "macro_indicators" in data_dict
    assert "options_playbook" in data_dict

def test_end_to_end_html():
    output_html = run_navigator(ticker="GOOG", lookback_days=60, output_format="html")
    assert "<!DOCTYPE html>" in output_html
    assert "Macro Flow Stock Navigator: GOOG" in output_html
    assert "toggleTheme" in output_html
    assert "data-theme=" in output_html
    assert "priceChart" in output_html
    assert "payoffChart" in output_html
    assert "macroRadarChart" in output_html

