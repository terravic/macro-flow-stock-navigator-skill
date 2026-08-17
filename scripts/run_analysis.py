#!/usr/bin/env python3
"""
Main Execution Script for Macro Flow Stock Navigator.
Retrieves market indicators, executes decision engine, and outputs
Gemini Spark UI Markdown or structured JSON.
"""

import sys
import os
import argparse
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_fetcher import MarketDataFetcher
from src.indicators import MacroIndicatorCalculator
from src.decision_engine import AlignmentDecisionEngine
from src.renderer import SparkDashboardRenderer
from src.config import DEFAULT_NOMINAL_GDP_TRILLIONS

def run_navigator(
    ticker: str = "GOOG",
    lookback_days: int = 90,
    mode: str = "auto",
    output_format: str = "spark",
    output_file: str = None,
    nominal_gdp: float = DEFAULT_NOMINAL_GDP_TRILLIONS
) -> str:
    """
    Executes the macro alignment workflow and returns rendered output.
    """
    ticker = ticker.upper().strip()
    fetcher = MarketDataFetcher()
    
    # 1. Fetch Market & Ticker Time Series
    prices_dict, ticker_info, is_synthetic = fetcher.fetch_market_and_ticker_data(
        ticker=ticker,
        lookback_days=lookback_days,
        mode=mode
    )

    # 2. Compute 8 Core Macro Indicators
    indicators = MacroIndicatorCalculator.compute_all_indicators(
        price_data=prices_dict,
        nominal_gdp=nominal_gdp
    )

    # 3. Execute Decision Alignment Engine
    decision = AlignmentDecisionEngine.evaluate(
        ticker_info=ticker_info,
        indicators=indicators
    )

    # 4. Render Desired Output Format
    if output_format == "json":
        rendered = SparkDashboardRenderer.render_json(
            ticker_info=ticker_info,
            indicators=indicators,
            decision=decision,
            is_synthetic=is_synthetic
        )
    elif output_format == "summary":
        rendered = (
            f"[{decision['signal_badge']}] {ticker} (${ticker_info['current_price']:.2f}) | "
            f"Archetype: {decision['archetype_name']} | "
            f"Alignment: {decision['alignment_score']:+.1f}/100 | "
            f"Playbook: {decision['options_playbook']['tactical_execution']['strategy']}"
        )
    else: # "spark" or "markdown"
        rendered = SparkDashboardRenderer.render_markdown(
            ticker_info=ticker_info,
            indicators=indicators,
            decision=decision,
            is_synthetic=is_synthetic
        )

    # 5. Save to file if requested
    if output_file:
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        with open(output_file, "w") as f:
            f.write(rendered)
        print(f"[OUTPUT] Output saved to: {output_file}", file=sys.stderr)

    return rendered

def main():
    parser = argparse.ArgumentParser(
        description="Macro Flow Stock Navigator - Enterprise Decision Engine"
    )
    parser.add_argument(
        "--ticker", "-t",
        type=str,
        default="GOOG",
        help="Stock ticker symbol to analyze (e.g. GOOG, SOFI, NVDA, AAPL)"
    )
    parser.add_argument(
        "--lookback", "-l",
        type=int,
        default=90,
        help="Lookback period in trading days (default: 90)"
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["auto", "live", "synthetic"],
        default="auto",
        help="Data retrieval mode: 'auto' (tries live, falls back to synthetic), 'live', or 'synthetic'"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["spark", "markdown", "json", "summary"],
        default="spark",
        help="Output format: 'spark' (Markdown dashboard), 'json', or 'summary'"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Optional file path to save output"
    )
    parser.add_argument(
        "--gdp",
        type=float,
        default=DEFAULT_NOMINAL_GDP_TRILLIONS,
        help="Nominal US GDP in Trillions for SPX/GDP Buffett Indicator (default: 29.5)"
    )

    args = parser.parse_args()

    output = run_navigator(
        ticker=args.ticker,
        lookback_days=args.lookback,
        mode=args.mode,
        output_format=args.format,
        output_file=args.output,
        nominal_gdp=args.gdp
    )

    print(output)

if __name__ == "__main__":
    main()
