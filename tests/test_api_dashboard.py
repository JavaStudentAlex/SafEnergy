from fastapi.testclient import TestClient

from safenergy.api.main import app

client = TestClient(app)

def test_get_dashboard_overview():
    response = client.get("/dashboard/overview")
    assert response.status_code == 200
    data = response.json()
    assert "portfolio_metrics" in data
    assert "market_prices" in data
    assert "recent_actions" in data
    assert "plants" in data
    assert isinstance(data["plants"], list)

    # Check that at least the structure is correct
    if len(data["plants"]) > 0:
        plant_ov = data["plants"][0]
        assert "plant" in plant_ov
        assert "health" in plant_ov

    metrics = data["portfolio_metrics"]
    assert "total_shortfall_mwh" in metrics
    assert "total_estimated_cost_eur" in metrics
    assert "total_avoided_cost_eur" in metrics
