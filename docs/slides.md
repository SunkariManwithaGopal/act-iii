# Slide 1: Problem & User
- **Title**: The Small Shop Inventory Dilemma
- **Bullets**:
  - Overstocking ties up cash; understocking loses sales.
  - Shop owners lack time for complex data analysis.
  - Need: Simple, actionable reorder advice.
- **Speaker Notes**: "Small retailers lose money to bad inventory guesses. They need clarity, not complex dashboards."

# Slide 2: Solution & Forecast
- **Title**: Transparent, Rule-Based Forecasting
- **Bullets**:
  - Uses public historical sales data (UCI Online Retail II).
  - Evaluated three methods: 4-week baseline, seasonal ratio, and smoothed trend (alpha 0.2).
  - Smoothed chosen on two pre-test validation windows (error 0.5796 vs baseline 0.6063).
- **Speaker Notes**: "We evaluated three methods without black-box prediction: a 4-week baseline, a seasonal ratio (which added error on two years of data), and a smoothed exponential average (alpha 0.2). Smoothed had lower error on pre-test validation, so by pre-fixed rule it drives orders."

# Slide 3: Results & Limits
- **Title**: Measured Outcomes
- **Bullets**:
  - Forecast error: Smoothed 0.5077 vs. Baseline 0.5166 vs. Seasonal 0.6395 (margin is small, not claimed significant).
  - Lost units & leftover stock: Smoothed 32,728 lost units (£46,977.69 total) / 180.19 leftover units (£218.08/wk); Baseline 29,722 lost (£39,922.05) / 209.03 leftover (£268.19/wk); Seasonal 26,933 lost (£34,438.94) / 339.33 leftover (£398.40/wk).
  - Limits: No holding cost, margin or lead-time data; 30 products and 8 weeks; stock is simulated; price is cost stand-in; test window is 8-week pre-Christmas build-up starting 2011-10-10.
- **Speaker Notes**: "Results are mixed: smoothed had lowest forecast error, but left the most demand unmet (23.6% vs baseline 21.5% and seasonal 19.4%). Smoothed won the pre-fixed lowest-error rule to drive orders, but we do not say it is better for the business. Lost value is an 8-week total and leftover value is a weekly snapshot—they cannot be subtracted, and no method is a net win."

## How the explanations work and next steps
- Offline CPU generation using Qwen2.5-1.5B (checked by scripts).
- Next step: deploy a larger model on AMD GPU hardware once access exists.
