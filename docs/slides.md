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
  - Two methods: 4-week baseline vs. seasonal trend adjustment.
  - Simulates 8-week replay to measure lost sales and leftover stock.
- **Speaker Notes**: "We don't use black-box AI for numbers. We use proven statistical methods and prove them via replay."

# Slide 3: Results & Limits
- **Title**: Measured Outcomes
- **Bullets**:
  - Forecast error: Baseline 0.5166 vs. Seasonal 0.6395.
  - Lost units: Seasonal reduced lost units to 26,933 ($34,438.94) vs. Baseline 29,722 ($39,922.05).
  - Leftover value: Baseline $268.19 vs. Seasonal $398.40.
  - Limit: Uses simulated stock and historical data.
- **Speaker Notes**: "Here are the actual numbers from our eval: the baseline achieved lower forecast error (0.5166 vs 0.6395), but the seasonal method reduced lost units by 2,789 in peak season simulation. We are honest about trade-offs and simulated stock."

# Slide 4: AMD Usage & Next Steps
- **Title**: AI for Explanation, Not Prediction
- **Bullets**:
  - AMD Token Factory translates actions into plain English.
  - The language model NEVER forecasts or alters numbers.
  - Next: Real-time supplier lead times and multi-location support.
- **Speaker Notes**: "AI's best role here is as a translator, making data actionable for the human buyer."
