# Stock Archetype Taxonomy & Sensitivity Weights

Stocks do not react uniformly to macroeconomic forces. The **Macro Flow Stock Navigator** categorizes equities into 5 archetypes, each mapped with specific sensitivity weights across the 8 macro indicators.

---

## 1. Mega-Cap Tech / High Quality Growth
- **Archetype Code:** `MEGA_CAP_TECH`
- **Key Characteristics:** Multi-billion/trillion market cap, secular growth drivers (Cloud, AI, Mobile), fortress cash balance sheets.
- **Examples:** `GOOG`, `GOOGL`, `MSFT`, `AAPL`, `NVDA`, `META`, `AMZN`, `TSLA`, `AVGO`, `AMD`, `ORCL`, `CRM`
- **Core Sensitivities:**
  - `NDX_SPX` (+2.5): Heavily rewarded when Tech leads broad indices.
  - `RSP_SPY` (-1.5): Outperforms when index concentration favors mega-caps over equal-weight.
  - `SPHB_SPLV` (+1.5): Positive on healthy risk appetite.
  - `VIX_SPX` (-1.5): Sensitive to systemic volatility shocks.

---

## 2. High-Beta Speculative Growth / Small-Mid Cap
- **Archetype Code:** `HIGH_BETA_GROWTH`
- **Key Characteristics:** Emerging technologies, fintech, high beta (>1.5), sensitive to discount rates and financial liquidity.
- **Examples:** `SOFI`, `PLTR`, `ROKU`, `AFRM`, `COIN`, `UPST`, `RBLX`, `PATH`, `HOOD`, `SHOP`, `SQ`, `IONQ`
- **Core Sensitivities:**
  - `IWM_SPY` (+2.5): Requires small-cap liquidity expansion and loose credit.
  - `SPHB_SPLV` (+2.5): Dependent on aggressive speculative market sentiment.
  - `GLD_SPX` (-2.0): Severely penalized during risk-off flight to safe havens.
  - `VIX_SPX` (-2.5): Crushed by volatility spikes and widening spreads.

---

## 3. Cyclical / Industrial / Discretionary
- **Archetype Code:** `CYCLICAL_INDUSTRIAL`
- **Key Characteristics:** Earnings directly tied to economic cycles, capex, manufacturing, and consumer spending.
- **Examples:** `CAT`, `DE`, `GM`, `F`, `NKE`, `DAL`, `UAL`, `URI`, `FCX`, `XOM`, `CVX`, `BA`
- **Core Sensitivities:**
  - `XLY_XLP` (+2.5): Primary indicator of discretionary consumer and business confidence.
  - `RSP_SPY` (+2.0): Thrives when market breadth widens into industrial sectors.
  - `IWM_SPY` (+1.5): Reflects domestic business activity.

---

## 4. Defensive / Value / Low Volatility
- **Archetype Code:** `DEFENSIVE_VALUE`
- **Key Characteristics:** Inelastic consumer demand, reliable dividends, low beta (<0.8), safe-haven profile.
- **Examples:** `JNJ`, `PG`, `KO`, `PEP`, `MCD`, `WMT`, `UNH`, `PFE`, `NEE`, `SO`, `DUK`, `CL`
- **Core Sensitivities:**
  - `SPHB_SPLV` (-2.0): Outperforms when Low Volatility (SPLV) dominates high beta.
  - `GLD_SPX` (+1.5): Positive relative strength during stagflation or risk-off regimes.
  - `NDX_SPX` (-1.5): Gains market share during tech profit-taking.

---

## 5. Financials & Banking
- **Archetype Code:** `FINANCIAL_BANKING`
- **Key Characteristics:** Interest rate margin sensitivity, credit cycle exposure, capital market volumes.
- **Examples:** `JPM`, `BAC`, `GS`, `MS`, `C`, `WFC`, `BLK`, `SCHW`, `AXP`, `V`, `MA`
- **Core Sensitivities:**
  - `RSP_SPY` (+1.5): Strong breadth supports loan growth.
  - `IWM_SPY` (+1.5): Regional credit health indicator.
  - `XLY_XLP` (+1.5): Consumer transactional health.
