"""
Integration Tests for FastAPI Backend Endpoints
Tests /api/actions, /api/results, /api/explain/{sku} with mocked AMD LLM calls.
"""

from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_actions():
    """Verify GET /api/actions returns 200 and a list of actions."""
    response = client.get("/api/actions")
    assert response.status_code == 200
    data = response.json()
    actions = data if isinstance(data, list) else data.get("actions", [])
    assert len(actions) > 0
    first = actions[0]
    assert "sku" in first
    assert "action" in first
    assert "quantity" in first


def test_get_results():
    """Verify GET /api/results returns 200 and replay comparison data."""
    response = client.get("/api/results")
    assert response.status_code == 200
    data = response.json()
    assert "baseline" in data
    assert "seasonal" in data
    assert "lost_units" in data["baseline"]
    assert "lost_units" in data["seasonal"]


@patch("app.main.explain")
def test_explain_live_success(mock_explain):
    """Verify POST /api/explain/{sku} returns source='live' when AMD call succeeds."""
    mock_explain.return_value = "Expected demand is 145 units. Reordering 120 units satisfies the 1.2 buffer. This prevents lost sales next week."

    response = client.post("/api/explain/21212")
    assert response.status_code == 200
    data = response.json()
    assert data["sku"] == "21212"
    assert data["source"] == "live"
    assert "145 units" in data["text"]


@patch("app.main.explain")
def test_explain_fallback_on_error(mock_explain):
    """Verify POST /api/explain/{sku} gracefully falls back to saved explanation on error."""
    mock_explain.side_effect = Exception("AMD Token Factory network timeout")

    response = client.post("/api/explain/21212")
    assert response.status_code == 200
    data = response.json()
    assert data["sku"] == "21212"
    assert data["source"] == "saved"
    assert len(data["text"]) > 10


def test_static_index_served():
    """Verify GET / serves the static dashboard HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Restock Copilot" in response.text
