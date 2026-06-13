from safenergy.ingest.plants import get_all_plants, get_plant_by_id


def test_get_all_plants():
    plants = get_all_plants()
    assert len(plants) == 2
    assert plants[0]["plant_id"] == "pv-texas-01"

def test_get_plant_by_id():
    plant = get_plant_by_id("pv-texas-01")
    assert plant is not None
    assert plant["plant_id"] == "pv-texas-01"

def test_get_plant_by_id_not_found():
    plant = get_plant_by_id("non-existent")
    assert plant is None
