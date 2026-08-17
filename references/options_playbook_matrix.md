# Strategic Options Playbook Matrix & Execution Mechanics

This document describes how the **Macro Flow Stock Navigator** pairs macroeconomic indicators, volatility conditions, and technical structure to select optimal derivative strategies.

---

## Strategy Selection Matrix

| Macro Alignment | Realized/Implied Volatility | Stock Technical Structure | Primary Option Strategy | Secondary / Alternative |
| :--- | :--- | :--- | :--- | :--- |
| **Bullish (> +20)** | **High / Elevated (IV > 35%)** | Above 50-MA or Testing Support | **Cash-Secured Puts (CSP)** | Bull Put Credit Spread |
| **Bullish (> +20)** | **Low / Compressed (IV < 30%)** | Clean Breakout above 50-MA | **Bull Call Debit Spread** | Long ATM Calls (60-90 DTE) |
| **Neutral (-15 to +20)** | **High / Elevated (IV > 35%)** | Range-Bound / Consolidating | **Iron Condor / Short Strangle** | Strangle Swap |
| **Neutral (-15 to +20)** | **Moderate (IV 20% - 35%)** | Range-Bound / Moderate Uptrend | **Covered Calls (30 DTE)** | Cash-Secured Put (Distant OTM) |
| **Bearish (< -20)** | **Moderate / Elevated** | Below 50-MA / Breakdown | **Bear Put Debit Spread** | Long Protective Puts |
| **Severe Risk-Off (< -40)**| **Spike / Extreme Volatility** | Testing 200-MA Breakdown | **Collars / Cash Conversion** | Protective Put Spreads |

---

## Tactical Execution Parameters

### 1. Cash-Secured Puts (CSP) & Bull Put Spreads
- **Target Delta:** `0.20 - 0.28 Delta` (~75% - 80% Probability of Expiring Worthless).
- **Strike Selection:** 7% - 12% Out-of-the-Money (OTM), strictly below the 50-day Moving Average or major horizontal swing low.
- **Days to Expiration (DTE):** `30 - 45 DTE` (captures the steepest slope of the theta decay curve).
- **Profit Target:** Close / buy back at `50% - 65%` of maximum credit received.
- **Stop Loss:** Exit or roll down/out if position loses `200% - 250%` of original premium received or if price closes below the 200-day Moving Average.

### 2. Covered Calls / Cash Flow Overlay
- **Target Delta:** `0.25 - 0.35 Delta`.
- **Strike Selection:** 5% - 10% OTM, aligned with major technical resistance.
- **Days to Expiration (DTE):** `21 - 35 DTE`.
- **Profit Target:** `75% - 85%` of max credit.
- **Management:** If stock approaches the short call strike on strong volume, roll up and out to a higher strike for a net credit.

### 3. Bull Call Debit Spreads
- **Target Delta:** Buy `0.60 - 0.70 Delta` (ATM/ITM), Sell `0.30 Delta` (OTM).
- **Target DTE:** `45 - 75 DTE`.
- **Profit Target:** `75% - 100%` ROI on debit paid.
- **Stop Loss:** Close at `50%` loss of debit paid.

### 4. Bear Put Debit Spreads
- **Target Delta:** Buy `0.50 Delta` (ATM), Sell `0.25 Delta` (OTM).
- **Target DTE:** `30 - 60 DTE`.
- **Profit Target:** `80% - 120%` ROI on debit paid.
- **Stop Loss:** Close at `50%` loss of debit paid.
