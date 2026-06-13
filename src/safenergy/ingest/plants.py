from typing import Any, Dict, List, Optional

# Canonical stable demo PV plants
DEMO_PLANTS = [
    {
        "plant_id": "pv-texas-01",
        "name": "Texas Solar 1",
        "latitude": 31.9686,
        "longitude": -99.9018,
        "timezone": "US/Central",
        "capacity_mw": 150.0,
        "status": "active",
        "battery_capacity_mwh": 50.0,
        "metadata_dict": {
            "surface_tilt": 20.0,
            "surface_azimuth": 180.0
        }
    },
    {
        "plant_id": "pv-texas-02",
        "name": "Texas Solar 2",
        "latitude": 30.2672,
        "longitude": -97.7431,
        "timezone": "US/Central",
        "capacity_mw": 200.0,
        "status": "maintenance",
        "battery_capacity_mwh": 0.0,
        "metadata_dict": {
            "surface_tilt": 25.0,
            "surface_azimuth": 185.0
        }
    }
]


def get_all_plants() -> List[Dict[str, Any]]:
    """
    Returns the list of all demo PV plants.
    """
    return DEMO_PLANTS


def get_plant_by_id(plant_id: str) -> Optional[Dict[str, Any]]:
    """
    Returns metadata for a specific plant by its identifier.
    Returns None if the plant_id is not found.
    """
    for plant in DEMO_PLANTS:
        if plant["plant_id"] == plant_id:
            return plant
    return None
