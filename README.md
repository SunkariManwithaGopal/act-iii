# Restock Copilot Lite

**What it does**  
Restock Copilot Lite tells a small shop what to reorder and why. It uses historical sales data to forecast demand, simulates inventory outcomes, and uses a language model via Plain-language explanations were generated offline by the open model Qwen/Qwen2.5-1.5B-Instruct (Apache-2.0) on the CPU of an AMD Ryzen 7 7735HS laptop (PyTorch / Transformers, no network calls at generation time), then saved and served by the hosted app. The hosted app does not call a model and does not run on AMD hardware. 29 of 30 explanations came from the model and passed automatic checks; 1 uses a fixed factual template. to explain the recommended actions in plain English.

**How to run locally**  
1. `python -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`)
2. `pip install -r requirements-api.txt`
3. `uvicorn app.main:app --reload`
4. Open `http://127.0.0.1:8000`

**Architecture**  
`data/` (UCI Dataset) → `forecasting/` (Pandas forecasting methods) → `eval/` (Replay simulation results) → `app/` (FastAPI backend) → `llm/` (Plain-language explanations were generated offline by the open model Qwen/Qwen2.5-1.5B-Instruct (Apache-2.0) on the CPU of an AMD Ryzen 7 7735HS laptop (PyTorch / Transformers, no network calls at generation time), then saved and served by the hosted app. The hosted app does not call a model and does not run on AMD hardware. 29 of 30 explanations came from the model and passed automatic checks; 1 uses a fixed factual template. explanation).

**Data**  
UCI Online Retail II (CC BY 4.0). Cleaned to top 30 products, weekly aggregation, removing cancellations and non-products.

**Forecasting Methods**  
We evaluated three methods:
1. **Baseline**: Average of the last 4 weeks.
2. **Seasonal**: Exponential average times last year's same-week ratio; this adds error because we only have two years of data.
3. **Smoothed**: Exponential average (alpha 0.2, "smoothed trend", no seasonal ratio).

Smoothed was chosen on two validation windows before the test window, after the first test results had been seen. Validation error went from 0.6063 (baseline) to 0.5796; on the test window the gain was smaller (0.5077 vs 0.5166). The forecast-error margin of smoothed over baseline is small and we do not claim it is significant.

**Replay Results (8-week pre-Christmas build-up starting 2011-10-10)**  
- **Baseline**: Forecast error 0.5166, lost sales 29,722 units (£39,922.05 lost value), average leftover stock 209.03 units/week (£268.19 leftover value).
- **Seasonal**: Forecast error 0.6395, lost sales 26,933 units (£34,438.94 lost value), average leftover stock 339.33 units/week (£398.40 leftover value).
- **Smoothed**: Forecast error 0.5077, lost sales 32,728 units (£46,977.69 lost value), average leftover stock 180.19 units/week (£218.08 leftover value).

The rule fixed before we saw the test results was "lowest forecast error", and smoothed won, so smoothed drives the suggested orders. We do not say it is better for the business. The most accurate method on forecast error (smoothed, 0.5077) also leaves the most demand unmet (about 23.6% of 138,538 units), baseline about 21.5%, seasonal about 19.4%. The results are mixed.

Note that `lost_value` is an 8-week total revenue at risk, while `leftover_value` is an average weekly snapshot of unsold stock value. They must never be subtracted from one another, and we never call either method a net win. No method is called better except on forecast error, and that is the only sense.


**Limits & Assumptions**  
No holding cost, margin or lead-time data; 30 products and 8 weeks; stock is simulated; price is a stand-in for cost; 1-week delivery; 1.2x buffer; the test window is the 8-week pre-Christmas build-up starting 2011-10-10.

**Team**  
P1: Data & Forecasting | P2: Backend & Deploy | P3: Replay & Docs (Lead)
