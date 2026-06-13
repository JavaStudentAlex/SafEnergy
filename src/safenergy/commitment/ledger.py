import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel

from safenergy.core.config import settings


class AcceptedAction(BaseModel):
    action_id: str
    plant_id: str
    action_type: str
    timestamp: datetime
    commitment_gap_mwh: float
    battery_discharge_mwh: float
    market_buy_mwh: float
    estimated_cost_eur: float
    avoided_imbalance_cost_eur: float

class ActionLedger:
    def __init__(self, ledger_file: Optional[str] = None):
        self.data_dir = Path(settings.SAFENERGY_CACHE_DIR)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.ledger_file = Path(ledger_file) if ledger_file else self.data_dir / "accepted_actions.json"
        self._actions: List[AcceptedAction] = []
        self._load()

    def _load(self):
        if self.ledger_file.exists():
            try:
                with open(self.ledger_file, 'r') as f:
                    data = json.load(f)
                    self._actions = [AcceptedAction.model_validate(item) for item in data]
            except Exception as e:
                logging.error(f"Failed to load ledger: {e}")
                self._actions = []

    def _save(self):
        try:
            with open(self.ledger_file, 'w') as f:
                json.dump([action.model_dump(mode='json') for action in self._actions], f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save ledger: {e}")

    def record_action(self, action: AcceptedAction):
        self._actions.append(action)
        self._save()

    def get_actions(self, plant_id: Optional[str] = None) -> List[AcceptedAction]:
        if plant_id:
            return [a for a in self._actions if a.plant_id == plant_id]
        return self._actions
