import pytest
from src.decision_engine import AlignmentDecisionEngine
from src.data_fetcher import MarketDataFetcher

def test_archetype_lookup_and_heuristics():
    fetcher = MarketDataFetcher()
    assert fetcher._classify_archetype("GOOG", 1.2, 25.0) == "MEGA_CAP_TECH"
    assert fetcher._classify_archetype("SOFI", 1.9, 45.0) == "HIGH_BETA_GROWTH"
    assert fetcher._classify_archetype("JNJ", 0.6, 15.0) == "DEFENSIVE_VALUE"
    assert fetcher._classify_archetype("CAT", 1.2, 25.0) == "CYCLICAL_INDUSTRIAL"

    # Dynamic heuristics for unlisted tickers
    assert fetcher._classify_archetype("RANDOM_SPECULATIVE", 2.2, 55.0) == "HIGH_BETA_GROWTH"
    assert fetcher._classify_archetype("RANDOM_DEFENSIVE", 0.5, 14.0) == "DEFENSIVE_VALUE"

def test_evaluate_decision_engine():
    ticker_info = {
        "ticker": "GOOG",
        "current_price": 180.0,
        "change_pct": 1.5,
        "ma50": 172.0,
        "diff_ma50_pct": 4.65,
        "ma200": 160.0,
        "diff_ma200_pct": 12.5,
        "rsi_14": 62.0,
        "historical_vol_30d": 24.0,
        "beta": 1.25,
        "archetype_key": "MEGA_CAP_TECH",
        "archetype_name": "Mega-Cap Tech / High Quality Growth",
        "archetype_desc": "Dominant market leaders"
    }

    mock_indicators = {
        "NDX_SPX": {"display_name": "Tech Momentum", "ratio_tickers": "NDX/SPX", "raw_sentiment_score": 1.5, "trend_signal": "STRONG RISING ↗️", "market_meaning": "Tech leading"},
        "RSP_SPY": {"display_name": "Breadth", "ratio_tickers": "RSP/SPY", "raw_sentiment_score": -1.0, "trend_signal": "FALLING ↘️", "market_meaning": "Concentration"},
        "GLD_SPX": {"display_name": "Gold/SPX", "ratio_tickers": "GLD/SPX", "raw_sentiment_score": -1.0, "trend_signal": "FALLING ↘️", "market_meaning": "Risk on"},
        "SPHB_SPLV": {"display_name": "High Beta", "ratio_tickers": "SPHB/SPLV", "raw_sentiment_score": 1.0, "trend_signal": "RISING ↗️", "market_meaning": "Risk appetite"},
        "VIX_SPX": {"display_name": "VIX/SPX", "ratio_tickers": "VIX/SPX", "raw_sentiment_score": -1.5, "trend_signal": "FALLING ↘️", "market_meaning": "Low fear"},
    }

    decision = AlignmentDecisionEngine.evaluate(ticker_info, mock_indicators)

    assert decision["ticker"] == "GOOG"
    assert "stock_signal" in decision
    assert "signal_badge" in decision
    assert "alignment_score" in decision
    assert "options_playbook" in decision
    assert "tactical_execution" in decision["options_playbook"]
    assert "recommended_delta" in decision["options_playbook"]["tactical_execution"]
    assert "optimal_strike" in decision["options_playbook"]["tactical_execution"]
