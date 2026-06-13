from datetime import datetime, timezone

from fastapi.testclient import TestClient

from safenergy.api.main import app
from safenergy.commitment.ledger import AcceptedAction, ActionLedger


def test_ledger_persistence(tmp_path):
    ledger_file = tmp_path / "actions.json"
    ledger = ActionLedger(str(ledger_file))

    action = AcceptedAction(
        action_id="1",
        plant_id="test_plant",
        action_type="HOLD",
        timestamp=datetime.now(timezone.utc),
        commitment_gap_mwh=0.0,
        battery_discharge_mwh=0.0,
        market_buy_mwh=0.0,
        estimated_cost_eur=0.0,
        avoided_imbalance_cost_eur=0.0
    )
    ledger.record_action(action)

    ledger2 = ActionLedger(str(ledger_file))
    actions = ledger2.get_actions()
    assert len(actions) == 1
    assert actions[0].action_id == "1"

client = TestClient(app)

def test_accept_action_endpoint(tmp_path, monkeypatch):
    ledger_file = tmp_path / "actions.json"
    ledger = ActionLedger(str(ledger_file))

    from safenergy.api import routes
    monkeypatch.setattr(routes, "get_action_ledger", lambda: ledger, raising=False)

    payload = {
        "action_id": "test_123",
        "plant_id": "plant_1",
        "action_type": "DISCHARGE_BATTERY",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "commitment_gap_mwh": 10.0,
        "battery_discharge_mwh": 10.0,
        "market_buy_mwh": 0.0,
        "estimated_cost_eur": 0.0,
        "avoided_imbalance_cost_eur": 500.0
    }

    # Needs to implement this endpoint
    response = client.post("/commitment/actions/accept", json=payload)
    assert response.status_code == 200

    actions = ledger.get_actions("plant_1")
    assert len(actions) == 1
    assert actions[0].action_id == "test_123"

def test_get_actions_endpoint(tmp_path, monkeypatch):
    ledger_file = tmp_path / "actions.json"
    ledger = ActionLedger(str(ledger_file))

    from safenergy.api import routes
    monkeypatch.setattr(routes, "get_action_ledger", lambda: ledger, raising=False)

    action1 = AcceptedAction(
        action_id="test_1",
        plant_id="plant_1",
        action_type="HOLD",
        timestamp=datetime.now(timezone.utc),
        commitment_gap_mwh=0.0,
        battery_discharge_mwh=0.0,
        market_buy_mwh=0.0,
        estimated_cost_eur=0.0,
        avoided_imbalance_cost_eur=0.0
    )
    action2 = AcceptedAction(
        action_id="test_2",
        plant_id="plant_2",
        action_type="DISCHARGE_BATTERY",
        timestamp=datetime.now(timezone.utc),
        commitment_gap_mwh=5.0,
        battery_discharge_mwh=5.0,
        market_buy_mwh=0.0,
        estimated_cost_eur=0.0,
        avoided_imbalance_cost_eur=250.0
    )
    ledger.record_action(action1)
    ledger.record_action(action2)

    response = client.get("/commitment/actions")
    assert response.status_code == 200
    assert len(response.json()) == 2

    response_plant_1 = client.get("/commitment/actions?plant_id=plant_1")
    assert response_plant_1.status_code == 200
    assert len(response_plant_1.json()) == 1
    assert response_plant_1.json()[0]["action_id"] == "test_1"
