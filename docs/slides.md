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
  - Seasonal method achieved `[SEASONAL_ERROR]` forecast error.
  - Reduced lost units to `[SEASONAL_LOST]` in peak season simulation.
  - Limit: Uses simulated stock and historical data.
- **Speaker Notes**: "Here are the actual numbers from our eval. We are honest about what is simulated."

# Slide 4: AMD Usage & Next Steps
- **Title**: AI for Explanation, Not Prediction
- **Bullets**:
  - AMD Token Factory translates actions into plain English.
  - The language model NEVER forecasts or alters numbers.
  - Next: Real-time supplier lead times and multi-location support.
- **Speaker Notes**: "AI's best role here is as a translator, making data actionable for the human buyer."
