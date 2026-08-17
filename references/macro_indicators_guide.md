# Macro Indicators Guide & Ratio Methodology

This reference document outlines the mathematical formulas, market dynamics, and regime interpretation for the 8 core macro ratio indicators computed by the **Macro Flow Stock Navigator**.

---

## 1. RSP / SPY (Equal-Weight vs. Cap-Weight S&P 500)
- **Ratio Formula:** `Price(RSP) / Price(SPY)`
- **Constituents:**
  - `RSP`: Invesco S&P 500 Equal Weight ETF (~0.2% weight per constituent)
  - `SPY`: SPDR S&P 500 ETF Trust (Market-cap weighted; top 7 stocks make up ~30%+)
- **Market Dynamics:**
  - **Rising (RSP > SPY):** Indicates healthy market breadth. Mid-cap and broad-market S&P components are participating in the rally. Favorable for cyclicals, financials, and broad equity participation.
  - **Falling (RSP < SPY):** Indicates narrow mega-cap leadership ("Magnificent 7" dominance). While bullish for mega-cap tech giants (GOOG, MSFT, NVDA), it signals a fragile foundation for broad equities.
- **Decision Engine Impact:** Bullish for broad market & high-beta when rising; favors Mega-Cap Tech when falling.

---

## 2. GLD / SPX (Gold vs. S&P 500 Index)
- **Ratio Formula:** `Price(GLD) / Price(SPX)`
- **Constituents:**
  - `GLD`: SPDR Gold Trust
  - `SPX`: S&P 500 Index (^GSPC or SPY)
- **Market Dynamics:**
  - **Rising (Gold Outperforming Equities):** Macro Risk-Off regime. Capital is demanding flight-to-safety, stagflation protection, or hedging currency debasement and geopolitical uncertainty. Severe headwind for speculative high-beta growth.
  - **Falling (Equities Outperforming Gold):** Macro Risk-On regime. Investors favor productive corporate earnings and economic expansion over static safe-haven metals.
- **Decision Engine Impact:** Heavy penalty for speculative growth when rising; supports defensive value and hedging plays.

---

## 3. NDX / SPX (Nasdaq 100 vs. S&P 500 Index)
- **Ratio Formula:** `Price(QQQ) / Price(SPY)`
- **Constituents:**
  - `QQQ`: Invesco QQQ Trust (Nasdaq 100 benchmark)
  - `SPY`: S&P 500 Index ETF
- **Market Dynamics:**
  - **Rising (Tech Leading):** Growth and secular tech multiple expansion are in full swing. Investors are willing to pay a premium for forward earnings and innovation.
  - **Falling (Tech Lagging):** Rotation into value, energy, industrials, or cash. Tech multiples compress under higher discount rates or profit-taking.
- **Decision Engine Impact:** High positive weighting for Mega-Cap Tech (GOOG, AAPL, NVDA) and SaaS/growth assets.

---

## 4. IWM / SPY (Russell 2000 vs. S&P 500 Index)
- **Ratio Formula:** `Price(IWM) / Price(SPY)`
- **Constituents:**
  - `IWM`: iShares Russell 2000 Small-Cap ETF
  - `SPY`: S&P 500 Large-Cap ETF
- **Market Dynamics:**
  - **Rising (Small-Caps Leading):** Domestic economic acceleration, credit easing, and high risk tolerance. Small caps have higher floating-rate debt; outperformance signals robust financial liquidity.
  - **Falling (Small-Caps Lagging):** Credit tightening, economic slowdown fears, or retreat into mega-cap cash-rich fortresses.
- **Decision Engine Impact:** Vital catalyst for High-Beta Speculative Growth (SOFI, PLTR, AFRM).

---

## 5. SPX / GDP (The Buffett Indicator)
- **Ratio Formula:** `(Total US Equity Market Cap / Nominal US GDP) * 100%`
- **Benchmark Series:**
  - `Total Equity Cap`: Proxy via scaled S&P 500 Index level
  - `US Nominal GDP`: Quarterly benchmark (e.g. ~$29.5 Trillion USD)
- **Valuation Bands:**
  - `> 180%`: **Significantly Overvalued** (Caution on long-term multiple expansion; favors options premium selling over naked long holding).
  - `140% - 180%`: **Modestly Overvalued** (Typical late-stage bull market condition).
  - `100% - 140%`: **Fairly Valued** (Balanced risk-reward).
  - `< 100%`: **Undervalued** (Historic accumulation opportunity).
- **Decision Engine Impact:** Controls systemic long bias and adjusts stop-loss / profit-taking aggression.

---

## 6. SPHB / SPLV (High Beta vs. Low Volatility)
- **Ratio Formula:** `Price(SPHB) / Price(SPLV)`
- **Constituents:**
  - `SPHB`: Invesco S&P 500 High Beta ETF (100 highest beta stocks)
  - `SPLV`: Invesco S&P 500 Low Volatility ETF (100 lowest realized volatility stocks)
- **Market Dynamics:**
  - **Rising (High Beta Dominating):** Aggressive speculative risk appetite. Traders are seeking maximum market exposure and chasing upside momentum.
  - **Falling (Low Volatility Dominating):** Capital preservation and defensiveness. Institutional accounts are rotating into utilities, consumer staples, and healthcare.
- **Decision Engine Impact:** Strong positive coefficient for high-beta / growth stocks; negative coefficient for defensives.

---

## 7. XLY / XLP (Consumer Discretionary vs. Consumer Staples)
- **Ratio Formula:** `Price(XLY) / Price(XLP)`
- **Constituents:**
  - `XLY`: Consumer Discretionary Select Sector SPDR (Amazon, Tesla, retail, travel)
  - `XLP`: Consumer Staples Select Sector SPDR (Procter & Gamble, Walmart, Coca-Cola)
- **Market Dynamics:**
  - **Rising (Discretionary Leading):** Consumer optimism and spending power are robust. Cyclical expansion is underway.
  - **Falling (Staples Leading):** Consumer caution and household belt-tightening. Typical leading indicator of economic slowdown or recessionary risk.
- **Decision Engine Impact:** Core driver for Cyclical, Retail, and Consumer-facing equities.

---

## 8. VIX / SPX Ratio (Fear Index Normalized vs. Index Trend)
- **Ratio Formula:** `Price(^VIX) / (Price(SPY) / 10)`
- **Constituents:**
  - `^VIX`: CBOE Volatility Index (30-day forward implied volatility)
  - `SPY`: S&P 500 Index Price
- **Market Dynamics:**
  - **Elevated / Spiking (> 90th percentile):** Volatility shock or panic selling. Creates high option implied volatility (rich credit for option sellers).
  - **Compressing / Low (< 20th percentile):** Complacency or calm trending bull market. Cheap option premiums make debit spreads attractive.
- **Decision Engine Impact:** Guides the Options Playbook between Credit Selling (CSPs / Credit Spreads) and Debit Spreads / Collars.
