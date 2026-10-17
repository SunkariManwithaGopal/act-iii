# Methodology: Restock Copilot Lite

**Data & Cleaning**  
We use the public UCI Online Retail II dataset. We filtered out canceled invoices (starting with "C"), non-positive quantities/prices, and non-product stock codes. We aggregated weekly sales per product, keeping the top 30 products with at least 52 weeks of sales history.

**Forecasting Methods**  
We use two non-language-model methods to predict weekly units:
1. **Baseline**: Simple average of the previous 4 weeks.
2. **Seasonal**: Exponential weighted mean of recent trends, adjusted by the ratio of the same week last year (clipped to 0.5x–2.0x to prevent extreme outliers).

**Replay Simulation**  
We simulated the last 8 weeks of operations. Both methods started with identical stock (1.2x the 4-week average). Each week, we fulfilled demand, recorded lost sales and leftover stock, and ordered `max(0, 1.2 * next_week_forecast - current_stock)`, arriving the following week.

**Results**  
- **Baseline**: Forecast error of `[BASELINE_ERROR]`, `[BASELINE_LOST]` lost units, average leftover value of `$[BASELINE_VALUE]`.
- **Seasonal**: Forecast error of `[SEASONAL_ERROR]`, `[SEASONAL_LOST]` lost units, average leftover value of `$[SEASONAL_VALUE]`.

**Honest Limits**  
This is a simulation using public historical data and simulated stock. The language model (AMD Token Factory) *only* explains the actions in plain English; it **does not** forecast or influence the numbers.
