import pytest
from scripts.run_analysis import run_navigator

def test_end_to_end_spark_markdown():
    output = run_navigator(ticker="GOOG", lookback_days=60, mode="synthetic", output_format="spark")
    assert "# Macro Flow Stock Navigator: GOOG" in output
    assert "Recommended Action" in output
    assert "Macro Cross-Asset Indicators" in output
    assert "Strategic Options Playbook" in output
    assert "Target Delta" in output

def test_end_to_end_json():
    import json
    output_json = run_navigator(ticker="SOFI", lookback_days=60, mode="synthetic", output_format="json")
    data = json.loads(output_json)
    assert data["metadata"]["skill"] == "macro-flow-stock-navigator"
    assert data["ticker_info"]["ticker"] == "SOFI"
    assert "decision" in data
    assert "macro_indicators" in data
    assert "options_playbook" in data
