# Product Requirement Document (PRD)
# Macro Flow Stock Navigator

**Document Version:** 1.0.0  
**Status:** Approved / Active  
**License:** Apache 2.0  
**Specification Compliance:** `SKILL.md`, `DESIGN.md`  

---

## 1. Product Overview & Vision

### 1.1 Executive Summary
Macro Flow Stock Navigator is an algorithmic decision-support engine and analytical agent skill designed to bridge macroeconomic market regimes with single-stock equity positioning and quantitative options execution. By evaluating 14 real-time cross-asset ratio indicators, classifying equities into structural market archetypes, and analyzing options microstructure (dealer gamma exposure, skew, and institutional flow), the engine computes a multi-factor macro alignment score (-100 to +100) and formulates an actionable options selling playbook (Covered Calls and Cash-Secured Puts).

Outputs are delivered in two standardized formats:
1. An executive Markdown report featuring a structured **Executive Finding** summary, core health pillars, and an options execution plan.
2. A standalone, interactive HTML dashboard adhering strictly to `DESIGN.md`, supporting light, dark, and operating-system theme modes, native canvas visualization fallbacks, and real-time state updates.

### 1.2 Core Objectives
- **Macro-Informed Stock Rating:** Evaluate whether broad market liquidity, credit, volatility, and sector flows are acting as tailwinds or headwinds for a specific equity ticker.
- **Microstructure-Aware Execution:** Quantify institutional positioning, dealer gamma exposure (GEX), volatility risk premiums (IV vs. RV), and option skew before recommending strikes.
- **Systematic Income Generation:** Recommend delta-targeted options strategies (0.20Δ, 0.30Δ, 0.40Δ) tailored to user-specified shares held or available cash capital.
- **Accessible Executive Synthesis:** Provide clear, high-contrast visual findings that communicate direct conclusions without decorative noise or unnecessary jargon.

---

## 2. Target Users & Personas

| User Persona | Primary Need | Platform Interaction |
|---|---|---|
| **Quantitative Investor / Trader** | Macro relative strength analysis, dealer gamma flip levels, volatility risk premium (IV vs. RV), and systematic options strike selection. | CLI commands (`scripts/run_analysis.py`), JSON output for automated ingestion. |
| **Long-Term Shareholder** | Determining optimal strike prices, expiration dates, and cash premiums for covered call overlays on existing equity positions. | Markdown dashboard and interactive HTML payoff simulator. |
| **Cash Capital Deployer** | Calculating discount entry levels, collateral requirements, and annualized Return on Capital (ROC) via cash-secured puts. | CLI `--cash` parameter, options screener tables. |
| **Autonomous AI Agent** | Automated evaluation of equity tickers, risk checks before portfolio rebalancing, and structured JSON decision consumption. | `SKILL.md` execution interface. |

---

## 3. Functional Requirements

### 3.1 Module 1: Cross-Asset Macroeconomic Engine (14 Indicators)
The engine must fetch public daily market data across 14 cross-asset pairs spanning 5 macroeconomic dimensions:

1. **Market Breadth:**
   - `RSP / SPY`: Equal-Weight S&P 500 vs. Cap-Weight S&P 500.
2. **Macro Risk Sentiment:**
   - `GLD / SPX`: Gold vs. S&P 500 Index.
   - `SPHB / SPLV`: High Beta vs. Low Volatility S&P.
   - `XLY / XLP`: Consumer Discretionary vs. Consumer Staples.
3. **Valuation & Technology Leadership:**
   - `NDX / SPX`: Nasdaq 100 vs. S&P 500 Index.
   - `SPX / GDP`: Total Market Capitalization to Nominal GDP (Buffett Indicator).
4. **Liquidity & Growth Vitality:**
   - `IWM / SPY`: Russell 2000 vs. S&P 500 Index.
   - `XBI / XLV`: Biotechnology Innovation vs. Mature Pharmaceuticals.
   - `PKG / SPY`: Packaging Corp of America vs. S&P 500 (Cardboard box shipping volume).
5. **Credit Solvency & Volatility Structure:**
   - `COPX / GLD`: Copper Miners vs. Gold (Physical industrial demand vs. monetary fear).
   - `HYG / LQD`: High-Yield Corporate Debt vs. Investment-Grade Corporate Debt.
   - `TIP / IEF`: TIPS vs. 7-10 Year Treasuries (Real interest rates / cost of capital).
   - `VIX / SPX`: Normalized CBOE Volatility Index.
   - `VIX9D / VIX`: 9-Day Volatility vs. 30-Day Volatility (Term structure inversion / panic).

#### Mathematical Specifications per Indicator
For each indicator ratio $R_t = P_{A,t} / P_{B,t}$:
- **50-Day Moving Average:** $MA50_t = \frac{1}{50}\sum_{i=0}^{49} R_{t-i}$.
- **Trend Slope (15-Day Normalized):** Normalized linear regression slope:
  $$\beta = \frac{\sum (x_i - \bar{x})(R_i - \bar{R})}{\sum (x_i - \bar{x})^2}, \quad \text{Slope}_{\%} = \frac{\beta}{\bar{R}} \times 100$$
- **90-Day Percentile Rank:** Empirical percentile of $R_t$ within its 90-day historical window $[R_{t-89}, R_t]$.
- **Trend Classification:** Evaluated as `Bullish / Strong Uptrend`, `Moderate Uptrend`, `Neutral / Ranging`, `Moderate Downtrend`, or `Bearish / Breakdown`.

---

### 3.2 Module 2: Stock Archetype Taxonomy & Sensitivity Weighting
Equities must be mapped to one of 5 distinct structural archetypes to determine sensitivity weights $W_j$:

1. **Mega-Cap Tech / High Quality Growth** (`MEGA_TECH`): Heavy sensitivity to `NDX/SPX`, `RSP/SPY`, and `TIP/IEF`. Examples: GOOG, MSFT, AAPL, NVDA.
2. **High-Beta Speculative Growth / Small-Mid Cap** (`HIGH_BETA_GROWTH`): High sensitivity to `IWM/SPY`, `SPHB/SPLV`, `HYG/LQD`, and `VIX9D/VIX`. Examples: SOFI, PLTR, AFRM, ROKU.
3. **Cyclical / Industrial / Discretionary** (`CYCLICAL`): High sensitivity to `PKG/SPY`, `COPX/GLD`, `XLY/XLP`, and `RSP/SPY`. Examples: CAT, DE, GM, URI.
4. **Defensive / Value / Low Volatility** (`DEFENSIVE`): Negative sensitivity to risk-on indicators; positive sensitivity to `SPLV`, `GLD/SPX`, and stable credit. Examples: JNJ, PG, KO, WMT.
5. **Financials / Banking / Credit-Sensitive** (`FINANCIALS`): Sensitivity to yield curve structure, `HYG/LQD`, and credit spreads. Examples: JPM, BAC, GS, MS.

---

### 3.3 Module 3: Macro Alignment Scoring & Decision Engine
- **Alignment Score Calculation:**
  $$\text{Alignment Score} = \sum_{j=1}^{14} W_j \cdot S_j \in [-100, +100]$$
  where $W_j$ is the normalized archetype weight and $S_j \in [-100, +100]$ is the indicator signal strength.
- **Directional Postures:**
  - `STRONG BUY`: Score $\ge +35.0$ and Price $> MA50$.
  - `ACCUMULATE`: Score between $+15.0$ and $+34.9$.
  - `NEUTRAL / RANGING`: Score between $-15.0$ and $+14.9$.
  - `REDUCE / TRIM`: Score between $-34.9$ and $-15.1$.
  - `PROTECT / SELL`: Score $\le -35.0$ or severe negative macro divergence.

---

### 3.4 Module 4: Options Microstructure & Practitioner Signals
The engine must fetch and calculate market microstructure metrics:
- **Net Dealer Gamma (GEX):** Quantifies dollar delta hedging requirement per 1% underlying price move:
  $$\text{GEX} = \sum (\text{OI}_{\text{call}} \times \Gamma_{\text{call}} - \text{OI}_{\text{put}} \times \Gamma_{\text{put}}) \times S^2 \times 100 \times 0.01$$
- **Gamma Flip Safety Floor:** Price strike where dealer positioning shifts from positive gamma (volatility stabilizing) to negative gamma (volatility accelerating).
- **25-Delta Put-Call Skew:** Implied volatility differential between 25Δ puts and 25Δ calls ($\text{IV}_{\text{put,25}\Delta} - \text{IV}_{\text{call,25}\Delta}$).
- **Retail 5Δ Call Surge:** Percentage of call volume concentrated in deep OTM (5-delta) contracts.
- **Short Float % & Days-to-Cover (DTC):** Short interest metrics.
- **Dark Pool Ratio & MOC Imbalances:** Off-exchange institutional volume percentage and closing auction tilt.

---

### 3.5 Module 5: Strategic Options Selling Playbook
- **Covered Calls (CC) Screener:** 3 risk tiers (Conservative 0.20Δ, Balanced 0.30Δ, Aggressive 0.40Δ) detailing Strike, Mid Premium, Delta, Theta, OTM %, Downside Cushion, and Annualized Return.
- **Cash-Secured Puts (CSP) Screener:** 3 risk tiers detailing Strike, Mid Premium, Delta, Theta, Collateral Required, Net Cost Basis, Discount %, and Annualized Return on Capital (ROC).
- **Tailored Position Sizing:**
  - When `--shares <N>` is provided: Computes exact covered call contracts ($\lfloor N / 100 \rfloor$), upfront cash income, and assigned return.
  - When `--cash <D>` is provided: Computes cash-secured put contracts ($\lfloor D / (\text{Strike} \times 100) \rfloor$), collateral deployed, and net discount basis.

---

### 3.6 Module 6: Executive Finding Bento Section
The primary decision summary must be rendered as a single-level bento pane adhering to `DESIGN.md §1 & §4`:
- **Visual Contrast:** Dedicated subtle darker background (`#EEEDE9` in Light Mode, `#111217` in Dark Mode) with crisp white/surface inner cards.
- **Traffic Light Status:** `GREEN LIGHT`, `YELLOW LIGHT`, or `RED LIGHT` pill with status dot.
- **Verdict Headline:** Single-sentence conclusion rendered in `Instrument Serif`.
- **4 Core Health Pillars:**
  1. *Real Economy:* Factory activity, shipping boxes, consumer demand.
  2. *Credit Health:* Corporate debt borrowing costs and credit spreads.
  3. *Market Sentiment:* Volatility term structure and risk appetite.
  4. *Institutional Floor:* Gamma flip strike and dealer support zone.
- **Quantitative Action Strip:** 4-cell metric bar displaying Action Directive, Upfront Cash Income, Annualized Return, and Buffer.

---

### 3.7 Module 7: Standalone Interactive HTML Dashboard
The standalone `dashboard.html` must comply with all requirements in `DESIGN.md`:
- **Self-Contained Execution:** Operates completely offline without external web servers or paid third-party dependencies.
- **Three-Icon Theme Selector:** Compact segmented control with Light (Sun), Dark (Moon), and System (Monitor) SVG buttons. Automatically tracks host OS theme preference via `window.matchMedia`.
- **Zero-Dependency Native Canvas Fallback:** Complete built-in 2D HTML5 canvas chart rendering engine for line charts, radar charts, and payoff diagrams if external libraries fail to load.
- **Standard Mouse Pointers:** Standard default mouse pointers across all panes, cells, and metric titles; zero tooltip clipping or help cursor changes.
- **Live Telemetry & Incremental Updates:** Built-in `window.updateDashboardData()` function and optional Server-Sent Events (SSE) listener (`/events`) that refresh DOM elements in place without resetting scroll position or active tabs.

---

## 4. Technical & Architectural Requirements

### 4.1 System Architecture

```text
macro-flow-stock-navigator-skill/
├── scripts/
│   ├── run_analysis.py       # Main CLI entry point
│   └── test_skill.py         # End-to-end automated test runner
├── src/
│   ├── config.py             # Macro indicators, archetypes, and weights
│   ├── data_fetcher.py       # Market data fetcher & microstructure calculations
│   ├── decision_engine.py    # Multi-factor alignment & playbook logic
│   ├── indicators.py         # 14-ratio calculation & regression engine
│   └── renderer.py           # Markdown, JSON, and HTML dashboard formatters
├── templates/
│   └── dashboard_template.html # Master standalone dashboard template
└── tests/
    ├── test_decision_engine.py
    ├── test_end_to_end.py
    └── test_indicators.py
```

### 4.2 Data Sourcing & Latency
- Primary data source: Public financial market feeds (`yfinance`, public option chains).
- Fallback mechanics: Mathematical simulation model for offline testing and deterministic test suite execution.
- Execution speed: End-to-end CLI analysis must complete in under 15 seconds.

### 4.3 Environment & System Portability
- Platform Independence: Operates in any standard Python 3.10+ Linux or macOS environment with zero proprietary infrastructure dependencies.
- Portable Path Hierarchy: Uses relative workspace pathing throughout configuration, scripts, and documentation (`./`).
- Standardized Output Formatting: Generates clean, standard ASCII and Unicode text formatting across Markdown, JSON, and Web UI HTML interfaces without decorative embellishments or marketing hyperbole.

---

## 5. Verification & Acceptance Criteria

| Requirement Area | Acceptance Criteria | Verification Method |
|---|---|---|
| **Indicator Calculations** | All 14 ratios compute accurately with 50-MA, slope, and 90-day percentile ranks. | `pytest tests/test_indicators.py` |
| **Decision Logic** | Archetype sensitivity weights, alignment scores, and playbook screeners compute deterministically. | `pytest tests/test_decision_engine.py` |
| **Output Formats** | Generates valid Markdown, structured JSON, and self-contained HTML dashboards. | `pytest tests/test_end_to_end.py` |
| **Live Multi-Archetype Execution** | Runs successfully across Mega-Cap Tech, Speculative Growth, Industrial Cyclical, and Defensive Value. | `python3 scripts/test_skill.py` |
| **Codebase Portability** | Operates strictly via standard library and open-source packages without machine-specific absolute paths. | Automated test suite execution |
| **Dashboard Aesthetics** | Adheres strictly to `DESIGN.md`; Executive Finding pane displays with `#EEEDE9` (light) / `#111217` (dark) background. | Manual browser inspection |

