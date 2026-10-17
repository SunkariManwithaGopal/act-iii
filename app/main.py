"""
Restock Copilot Lite - FastAPI Backend
Author: P2 (Backend & AMD Integration)

Endpoints:
  GET  /api/actions       - Returns inventory actions (data/actions.json or sample fallback)
  GET  /api/results       - Returns replay test results (eval/results.json or sample fallback)
  POST /api/explain/{sku} - Calls AMD LLM or falls back to saved/stub explanation
  GET  /                  - Serves static frontend from app/static/
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from llm.explain import explain, generate_fallback_stub

# Base project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
EVAL_DIR = BASE_DIR / "eval"
STATIC_DIR = BASE_DIR / "app" / "static"

app = FastAPI(
    title="Restock Copilot Lite API",
    description="Backend service for shop reordering recommendations powered by AMD Token Factory",
    version="1.0.0"
)

# Enable CORS for local development and hosted frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_actions_data() -> Dict[str, Any]:
    """Loads production actions.json if present, otherwise falls back to sample."""
    prod_actions = DATA_DIR / "actions.json"
    sample_actions = DATA_DIR / "sample" / "actions.json"

    if prod_actions.exists():
        with open(prod_actions, "r", encoding="utf-8") as f:
            return json.load(f)
    elif sample_actions.exists():
        with open(sample_actions, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"sample": True, "actions": []}


def _load_results_data() -> Dict[str, Any]:
    """Loads production results.json if present, otherwise falls back to sample."""
    prod_results = EVAL_DIR / "results.json"
    sample_results = DATA_DIR / "sample" / "results.json"

    if prod_results.exists():
        with open(prod_results, "r", encoding="utf-8") as f:
            return json.load(f)
    elif sample_results.exists():
        with open(sample_results, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"sample": True, "error": "Results not yet generated"}


def _load_saved_explanations() -> Dict[str, str]:
    """Loads pre-saved explanations for offline or fallback mode."""
    saved_file = DATA_DIR / "saved_explanations.json"
    if saved_file.exists():
        try:
            with open(saved_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


@app.get("/api/actions")
def get_actions():
    """Returns the list of inventory actions and reorder recommendations."""
    return _load_actions_data()


@app.get("/api/results")
def get_results():
    """Returns 8-week replay test results comparing baseline vs seasonal forecast."""
    return _load_results_data()


@app.post("/api/explain/{sku}")
def explain_action(sku: str):
    """
    Generates a 3-sentence plain English explanation for a given SKU.
    Tries calling AMD Token Factory live; falls back to saved explanations on error.
    """
    actions_data = _load_actions_data()
    if isinstance(actions_data, list):
        actions_list = actions_data
    elif isinstance(actions_data, dict):
        actions_list = actions_data.get("actions", [])
    else:
        actions_list = []

    # Find the matching action for the requested SKU
    target_action = None
    for item in actions_list:
        if str(item.get("sku")) == str(sku):
            target_action = item
            break

    # If action not found in list, fabricate minimal action context from SKU
    if not target_action:
        target_action = {"sku": sku, "action": "reorder", "quantity": 0, "forecast": 0, "stock": 0}

    # 1. Attempt live AMD LLM call
    try:
        live_explanation = explain(target_action)
        return {
            "sku": sku,
            "text": live_explanation,
            "source": "live"
        }
    except Exception as e:
        # 2. On error, fallback to pre-saved explanation from data/saved_explanations.json
        saved = _load_saved_explanations()
        if sku in saved:
            entry = saved[sku]
            if isinstance(entry, dict):
                return {
                    "sku": sku,
                    "text": entry.get("text", "Explanation not available."),
                    "source": entry.get("source", "saved")
                }
            return {
                "sku": sku,
                "text": str(entry),
                "source": "saved"
            }
        
        # 3. Fallback to deterministic rule-based template or default message
        fallback_text = generate_fallback_stub(target_action) if target_action else "Explanation not available."
        return {
            "sku": sku,
            "text": fallback_text,
            "source": "saved"
        }


# Ensure static directory exists
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files LAST so /api routes take priority
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
