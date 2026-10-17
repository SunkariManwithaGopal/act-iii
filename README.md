# Restock Copilot Lite

**What it does**  
Restock Copilot Lite tells a small shop what to reorder and why. It uses historical sales data to forecast demand, simulates inventory outcomes, and uses an AMD-hosted language model to explain the recommended actions in plain English.

**How to run locally**  
1. `python -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`)
2. `pip install -r requirements-api.txt`
3. Copy `.env.example` to `.env` and add your AMD Token Factory credentials.
4. `uvicorn app.main:app --reload`
5. Open `http://127.0.0.1:8000`

**Architecture**  
`data/` (UCI Dataset) → `forecasting/` (Pandas baseline/seasonal models) → `eval/` (Replay simulation results) → `app/` (FastAPI backend) → `llm/` (AMD Token Factory explanation).

**Data**  
UCI Online Retail II (CC BY 4.0). Cleaned to top 30 products, weekly aggregation, removing cancellations and non-products.

**Replay Results**  
Tested on the last 8 weeks (peak season). Baseline error: `[BASELINE_ERROR]`. Seasonal error: `[SEASONAL_ERROR]`. Lost units: Baseline `[BASELINE_LOST]`, Seasonal `[SEASONAL_LOST]`.

**AMD Usage**  
We use an AMD Token Factory model (OpenAI-compatible API) strictly to generate plain-English explanations for the reorder actions. **The language model does not forecast.** All numbers come from `eval/results.json`.

**Limits & Assumptions**  
Public sales data, simulated stock, 1-week delivery, 1.2x buffer. Price is used as a cost stand-in. 

**Team**  
P1: Data & Forecasting | P2: Backend & Deploy | P3: Replay & Docs (Lead)
