"""
Configuration settings, archetypes taxonomy, and indicator parameters
for Macro Flow Stock Navigator.
"""

from typing import Dict, List, Any

# ---------------------------------------------------------
# Default Macro Indicator Tickers
# ---------------------------------------------------------
INDICATOR_TICKERS = {
    "RSP": "RSP",     # Invesco S&P 500 Equal Weight ETF
    "SPY": "SPY",     # SPDR S&P 500 ETF Trust
    "GLD": "GLD",     # SPDR Gold Shares
    "QQQ": "QQQ",     # Invesco QQQ Trust (Nasdaq 100 proxy for NDX)
    "IWM": "IWM",     # iShares Russell 2000 ETF
    "SPHB": "SPHB",   # Invesco S&P 500 High Beta ETF
    "SPLV": "SPLV",   # Invesco S&P 500 Low Volatility ETF
    "XLY": "XLY",     # Consumer Discretionary Select Sector SPDR Fund
    "XLP": "XLP",     # Consumer Staples Select Sector SPDR Fund
    "VIX": "^VIX",    # CBOE Volatility Index
    "SPX": "^GSPC",   # S&P 500 Index
}

# ---------------------------------------------------------
# Long-Term GDP Benchmark (in Trillions USD)
# Nominal US GDP estimate (updated quarterly)
# ---------------------------------------------------------
DEFAULT_NOMINAL_GDP_TRILLIONS = 29.5  # Approx US Nominal GDP (Trillion USD)

# ---------------------------------------------------------
# Stock Archetype Taxonomy & Known Mappings
# ---------------------------------------------------------
STOCK_ARCHETYPES = {
    "MEGA_CAP_TECH": {
        "name": "Mega-Cap Tech / High Quality Growth",
        "description": "Dominant market leaders with strong balance sheets, high free cash flow, and secular AI/cloud tailwinds.",
        "examples": ["GOOG", "GOOGL", "MSFT", "AAPL", "NVDA", "META", "AMZN", "TSLA"],
        "default_beta": 1.25,
        "indicator_weights": {
            "NDX_SPX": 2.5,     # Very bullish when tech leads
            "RSP_SPY": -1.5,    # Outperforms when mega-caps lead over equal-weight
            "SPHB_SPLV": 1.5,   # Favorable when risk appetite is healthy
            "GLD_SPX": -1.0,    # Slightly negative on aggressive flight to safety
            "IWM_SPY": 0.5,     # Neutral to slightly positive
            "XLY_XLP": 1.0,     # Favorable on consumer/cyclical strength
            "VIX_SPX": -1.5,    # Sensitive to volatility spikes
            "SPX_GDP": -0.5,    # Moderate valuation sensitivity
        }
    },
    "HIGH_BETA_GROWTH": {
        "name": "High-Beta Speculative Growth / Small-Mid Cap",
        "description": "High-growth, speculative, non-profitable or emerging tech/fintech companies sensitive to interest rates and liquidity.",
        "examples": ["SOFI", "PLTR", "ROKU", "AFRM", "COIN", "UPST", "RBLX", "PATH", "HOOD", "SHOP", "SQ", "IONQ"],
        "default_beta": 1.85,
        "indicator_weights": {
            "IWM_SPY": 2.5,     # Highly sensitive to small-cap liquidity & breadth
            "SPHB_SPLV": 2.5,   # High beta dominance is essential
            "GLD_SPX": -2.0,    # Strongly penalized by macro flight-to-safety/risk-off
            "NDX_SPX": 1.5,     # Bullish when tech sentiment is positive
            "RSP_SPY": 1.5,     # Requires healthy breadth and broad market participation
            "XLY_XLP": 1.5,     # Thrives in cyclical economic optimism
            "VIX_SPX": -2.5,    # Heavily crushed by rising VIX & panic
            "SPX_GDP": -1.0,    # Sensitive to broader equity multiple contraction
        }
    },
    "CYCLICAL_INDUSTRIAL": {
        "name": "Cyclical / Industrial / Discretionary",
        "description": "Companies directly tied to economic cycles, manufacturing, infrastructure, and discretionary spending.",
        "examples": ["CAT", "DE", "GM", "F", "NKE", "DAL", "UAL", "URI", "FCX", "XOM", "CVX"],
        "default_beta": 1.20,
        "indicator_weights": {
            "XLY_XLP": 2.5,     # Key indicator: consumer & economic expansion
            "RSP_SPY": 2.0,     # Equal weight strength indicates broad economic cycle
            "IWM_SPY": 1.5,     # Domestic economic pulse
            "SPHB_SPLV": 1.0,   # Pro-risk environment
            "GLD_SPX": -1.0,    # Commodity/macro risk
            "NDX_SPX": -0.5,    # Capital rotation away from tech often helps cyclicals
            "VIX_SPX": -1.5,    # Volatility drag
            "SPX_GDP": -0.5,    # Valuation drag
        }
    },
    "DEFENSIVE_VALUE": {
        "name": "Defensive / Value / Low Volatility",
        "description": "Stable cash flow, dividend-yielding, consumer staples, healthcare, and utility giants.",
        "examples": ["JNJ", "PG", "KO", "PEP", "MCD", "WMT", "UNH", "PFE", "NEE", "SO", "DUK", "CL"],
        "default_beta": 0.65,
        "indicator_weights": {
            "SPHB_SPLV": -2.0,   # Outperforms when Low Volatility (SPLV) leads
            "GLD_SPX": 1.5,     # Holds up well in flight-to-safety & stagflation
            "RSP_SPY": 0.5,     # Neutral to positive
            "NDX_SPX": -1.5,    # Outperforms during tech de-risking
            "XLY_XLP": -1.5,    # Staples (XLP) outperformance is bullish for defensives
            "IWM_SPY": -1.0,    # Small cap lag usually coincides with defensive flight
            "VIX_SPX": 1.0,     # Relatively insulated from VIX spikes
            "SPX_GDP": -0.5,    # Valuation consideration
        }
    },
    "FINANCIAL_BANKING": {
        "name": "Financials & Banking",
        "description": "Commercial banks, investment houses, payments, and asset managers sensitive to yield curve and credit.",
        "examples": ["JPM", "BAC", "GS", "MS", "C", "WFC", "BLK", "SCHW", "AXP", "V", "MA"],
        "default_beta": 1.10,
        "indicator_weights": {
            "RSP_SPY": 1.5,     # Broad market participation
            "IWM_SPY": 1.5,     # Regional health and domestic credit
            "XLY_XLP": 1.5,     # Economic vitality
            "SPHB_SPLV": 1.0,   # Risk tolerance
            "GLD_SPX": -1.0,    # Negative on systemic fear
            "NDX_SPX": 0.0,     # Tech neutral
            "VIX_SPX": -1.5,    # Volatility drag
            "SPX_GDP": -0.5,    # Valuation
        }
    }
}

# ---------------------------------------------------------
# Known Ticker to Archetype Lookup
# ---------------------------------------------------------
TICKER_ARCHETYPE_LOOKUP = {
    # Mega-Cap Tech
    "GOOG": "MEGA_CAP_TECH",
    "GOOGL": "MEGA_CAP_TECH",
    "MSFT": "MEGA_CAP_TECH",
    "AAPL": "MEGA_CAP_TECH",
    "NVDA": "MEGA_CAP_TECH",
    "META": "MEGA_CAP_TECH",
    "AMZN": "MEGA_CAP_TECH",
    "TSLA": "MEGA_CAP_TECH",
    "AVGO": "MEGA_CAP_TECH",
    "AMD": "MEGA_CAP_TECH",
    "ORCL": "MEGA_CAP_TECH",
    "CRM": "MEGA_CAP_TECH",
    
    # High Beta Growth / Speculative
    "SOFI": "HIGH_BETA_GROWTH",
    "PLTR": "HIGH_BETA_GROWTH",
    "ROKU": "HIGH_BETA_GROWTH",
    "AFRM": "HIGH_BETA_GROWTH",
    "COIN": "HIGH_BETA_GROWTH",
    "UPST": "HIGH_BETA_GROWTH",
    "RBLX": "HIGH_BETA_GROWTH",
    "PATH": "HIGH_BETA_GROWTH",
    "HOOD": "HIGH_BETA_GROWTH",
    "SHOP": "HIGH_BETA_GROWTH",
    "SQ": "HIGH_BETA_GROWTH",
    "IONQ": "HIGH_BETA_GROWTH",
    "DKNG": "HIGH_BETA_GROWTH",
    "SMCI": "HIGH_BETA_GROWTH",
    "MARA": "HIGH_BETA_GROWTH",
    "RIOT": "HIGH_BETA_GROWTH",
    
    # Cyclical & Industrial
    "CAT": "CYCLICAL_INDUSTRIAL",
    "DE": "CYCLICAL_INDUSTRIAL",
    "GM": "CYCLICAL_INDUSTRIAL",
    "F": "CYCLICAL_INDUSTRIAL",
    "NKE": "CYCLICAL_INDUSTRIAL",
    "DAL": "CYCLICAL_INDUSTRIAL",
    "UAL": "CYCLICAL_INDUSTRIAL",
    "URI": "CYCLICAL_INDUSTRIAL",
    "FCX": "CYCLICAL_INDUSTRIAL",
    "XOM": "CYCLICAL_INDUSTRIAL",
    "CVX": "CYCLICAL_INDUSTRIAL",
    "BA": "CYCLICAL_INDUSTRIAL",
    
    # Defensive & Value
    "JNJ": "DEFENSIVE_VALUE",
    "PG": "DEFENSIVE_VALUE",
    "KO": "DEFENSIVE_VALUE",
    "PEP": "DEFENSIVE_VALUE",
    "MCD": "DEFENSIVE_VALUE",
    "WMT": "DEFENSIVE_VALUE",
    "UNH": "DEFENSIVE_VALUE",
    "PFE": "DEFENSIVE_VALUE",
    "NEE": "DEFENSIVE_VALUE",
    "SO": "DEFENSIVE_VALUE",
    "DUK": "DEFENSIVE_VALUE",
    "CL": "DEFENSIVE_VALUE",
    "COST": "DEFENSIVE_VALUE",
    
    # Financials
    "JPM": "FINANCIAL_BANKING",
    "BAC": "FINANCIAL_BANKING",
    "GS": "FINANCIAL_BANKING",
    "MS": "FINANCIAL_BANKING",
    "C": "FINANCIAL_BANKING",
    "WFC": "FINANCIAL_BANKING",
    "BLK": "FINANCIAL_BANKING",
    "SCHW": "FINANCIAL_BANKING",
    "AXP": "FINANCIAL_BANKING",
    "V": "FINANCIAL_BANKING",
    "MA": "FINANCIAL_BANKING",
}

# ---------------------------------------------------------
# Decision Engine Thresholds
# ---------------------------------------------------------
ALIGNMENT_THRESHOLDS = {
    "STRONG_BUY": 45.0,
    "ACCUMULATE": 18.0,
    "NEUTRAL_HIGH": 18.0,
    "NEUTRAL_LOW": -15.0,
    "REDUCE": -35.0,
    "STRONG_SELL": -100.0,
}

# ---------------------------------------------------------
# Options Strategy Rules
# ---------------------------------------------------------
OPTIONS_RULES = {
    "CASH_SECURED_PUTS": {
        "name": "Cash-Secured Puts (CSP) / Bull Put Spread",
        "description": "Sell out-of-the-money puts to generate premium income and establish long exposure at a steep discount.",
        "target_delta": "0.20 - 0.28 Delta (~75-80% Probability of Profit)",
        "strike_offset_pct": "7% - 12% Out-of-the-Money (below major 50-MA or swing low support)",
        "target_dte": "30 - 45 DTE (optimal theta decay curve)",
        "profit_target": "50% - 65% of max credit",
        "stop_loss": "200% - 250% of credit received or breach of 200-MA",
        "ideal_condition": "Macro Alignment is Positive/Neutral + IV Rank is Elevated (>35) or stock is near structural support."
    },
    "COVERED_CALLS": {
        "name": "Covered Calls / Bull Collar",
        "description": "Sell out-of-the-money calls against long stock to monetize range-bound or moderate upward momentum.",
        "target_delta": "0.25 - 0.35 Delta",
        "strike_offset_pct": "5% - 10% Out-of-the-Money (above immediate resistance)",
        "target_dte": "21 - 35 DTE",
        "profit_target": "75% - 85% of max credit",
        "stop_loss": "Roll up and out if stock breaches strike with heavy volume",
        "ideal_condition": "Macro Alignment is Neutral / Ranging or Mildly Positive + IV is moderate."
    },
    "BULL_CALL_DEBIT_SPREAD": {
        "name": "Bull Call Debit Spread / Long Calls",
        "description": "Defined-risk directional play to capture high-velocity upside with limited capital outlay.",
        "target_delta": "Long 0.60-0.70 Delta / Short 0.30 Delta",
        "strike_offset_pct": "ATM to 5% OTM Long, 10-15% OTM Short",
        "target_dte": "45 - 75 DTE",
        "profit_target": "75% - 100% ROI on spread debit",
        "stop_loss": "50% loss of initial debit paid",
        "ideal_condition": "Macro Alignment is Strongly Bullish + IV Rank is Low (<30) + Breakout setup."
    },
    "BEAR_PUT_SPREAD": {
        "name": "Bear Put Spread / Protective Long Puts",
        "description": "Hedge downside risk or capitalize on severe macro headwind with defined-risk put spreads.",
        "target_delta": "Long 0.50 Delta (ATM) / Short 0.25 Delta (OTM)",
        "strike_offset_pct": "ATM Long, 8-12% OTM Short",
        "target_dte": "30 - 60 DTE",
        "profit_target": "80% - 120% ROI on debit",
        "stop_loss": "50% loss of debit",
        "ideal_condition": "Macro Alignment is Hostile / Risk-Off + Ticker shows technical breakdown."
    },
    "IRON_CONDOR": {
        "name": "Iron Condor / Neutral Range Selling",
        "description": "Sell both OTM Call and OTM Put spreads to harvest theta decay in a low-volatility, non-trending market.",
        "target_delta": "Short 0.15 Delta Call / Short 0.15 Delta Put",
        "strike_offset_pct": "±10% - 15% OTM Wings",
        "target_dte": "30 - 45 DTE",
        "profit_target": "50% of total credit",
        "stop_loss": "150% of credit per tested wing",
        "ideal_condition": "Macro Alignment is Neutral / Low Trend + IV Rank > 40."
    }
}
