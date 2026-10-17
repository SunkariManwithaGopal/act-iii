# Methodology: Restock Copilot Lite

**Data & Cleaning**  
We use the public UCI Online Retail II dataset. We filtered out canceled invoices (starting with "C"), non-positive quantities/prices, and non-product stock codes. We aggregated weekly sales per product, keeping the top 30 products with at least 52 weeks of sales history.

**Forecasting Methods**  
We evaluated three non-language-model methods to predict weekly units:
1. **Baseline**: Average of the last 4 weeks.
2. **Seasonal**: Exponential average times last year's same-week ratio; this adds error because we only have two years of data.
3. **Smoothed**: Exponential average (alpha 0.2, "smoothed trend", no seasonal ratio).

The smoothed method was chosen on two validation windows before the test window, after the first test results had been seen. Validation error went from 0.6063 (baseline) to 0.5796; on the test window the gain was smaller (0.5077 vs 0.5166). The forecast-error margin of smoothed over baseline is small and we do not claim it is significant.

**Replay Simulation**  
We simulated the 8-week pre-Christmas build-up starting 2011-10-10 across 30 products. All methods started with identical stock (1.2x the 4-week average). Each week, we fulfilled demand, recorded lost sales and leftover stock, and ordered `max(0, 1.2 * next_week_forecast - current_stock)`, arriving the following week.

**Results**  
- **Baseline**: Forecast error 0.5166, 29,722 lost units (£39,922.05 lost value), average leftover value £268.19 (209.03 average leftover units per week).
- **Seasonal**: Forecast error 0.6395, 26,933 lost units (£34,438.94 lost value), average leftover value £398.40 (339.33 average leftover units per week).
- **Smoothed**: Forecast error 0.5077, 32,728 lost units (£46,977.69 lost value), average leftover value £218.08 (180.19 average leftover units per week).

The decision rule fixed before seeing test results was "lowest forecast error", and smoothed won, so smoothed drives the suggested orders. We do not say it is better for the business. In fact, the most accurate method on forecast error (smoothed, 0.5077) leaves the most demand unmet (about 23.6% of 138,538 total units), baseline about 21.5%, and seasonal about 19.4%. The results are mixed.

*Metric Definition Note*: `lost_value` is an 8-week total revenue at risk, while `leftover_value` is a weekly snapshot of stock sitting unsold. They must never be subtracted from one another, and no method is called a net win. No method is called better except on forecast error, and that is the only sense.

**Honest Limits**  
No holding cost, margin or lead-time data; 30 products and 8 weeks; stock is simulated; price is a stand-in for cost; the test window is the 8-week pre-Christmas build-up starting 2011-10-10. The language model via [AMD_SERVING] *only* explains the actions in plain English; it **does not** forecast or influence the numbers.
