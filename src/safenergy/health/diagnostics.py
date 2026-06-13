from datetime import datetime, timezone

from safenergy.api.schemas import AnomalyDiagnostic, PlantHealthResponse
from safenergy.ingest.plants import get_plant_by_id


def get_plant_health(plant_id: str) -> PlantHealthResponse:
    plant = get_plant_by_id(plant_id)
    if not plant:
        return None

    now = datetime.now(timezone.utc)
    anomalies = []
    status = plant.get("status", "ok")

    if status == "maintenance":
        anomalies.append(
            AnomalyDiagnostic(
                category="inverter_outage",
                severity="critical",
                description="Plant is scheduled for maintenance. Inverter outage expected."
            )
        )
    elif plant_id == "pv-texas-01":
        # Rule based demo data
        status = "degraded"
        anomalies.append(
            AnomalyDiagnostic(
                category="weather_derating",
                severity="warning",
                description="High temperature causing minor efficiency loss."
            )
        )
    else:
        status = "ok"

    return PlantHealthResponse(
        plant_id=plant_id,
        status=status,
        last_updated=now,
        anomalies=anomalies
    )
