import json
from datetime import datetime, timezone

from safenergy.core.config import settings
from safenergy.ingest.satellite import (
    SatelliteDiscoveryRequest,
    SatelliteUnavailable,
    discover_satellite_data,
)


def test_discover_satellite_data_fallback_to_fixture(tmp_path, monkeypatch):
    """Test that discovery falls back to reading the fixture when live is unconfigured."""
    # 1. Setup a dummy fixture
    fixture_dir = tmp_path / "satellite"
    fixture_dir.mkdir(parents=True)
    fixture_file = fixture_dir / "sample_discovery.json"

    dummy_data = {
        "items": [
            {
                "id": "dummy_id",
                "provider": "copernicus_dataspace",
                "valid_time": "2023-06-01T16:38:49Z",
                "issue_time": "2023-06-01T21:08:50Z",
                "footprint": {
                    "type": "Polygon",
                    "coordinates": [[[-98.0, 30.0], [-97.0, 30.0], [-97.0, 31.0], [-98.0, 31.0], [-98.0, 30.0]]]
                },
                "crs": "EPSG:4326",
                "cloud_cover": 12.5,
                "cache_key": "sat_copernicus_dummy"
            }
        ]
    }
    with open(fixture_file, "w") as f:
        json.dump(dummy_data, f)

    # 2. Mock settings to point to the tmp_path for fixtures and remove live credentials
    monkeypatch.setattr(settings, "EE_PROJECT", "")
    monkeypatch.setattr(settings, "COPERNICUS_USERNAME", "")
    monkeypatch.setattr(settings, "SAFENERGY_FIXTURE_DATA_DIR", str(tmp_path))

    # 3. Create request
    request = SatelliteDiscoveryRequest(
        region_geojson={"type": "Polygon", "coordinates": [[[-98.0, 30.0], [-97.0, 30.0], [-97.0, 31.0], [-98.0, 31.0], [-98.0, 30.0]]]},
        time_start=datetime(2023, 6, 1, 0, 0, 0, tzinfo=timezone.utc),
        time_end=datetime(2023, 6, 2, 0, 0, 0, tzinfo=timezone.utc),
        provider="auto"
    )

    # 4. Execute
    result = discover_satellite_data(request)

    # 5. Verify
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].id == "dummy_id"
    assert result[0].cloud_cover == 12.5
    assert result[0].valid_time.year == 2023


def test_discover_satellite_data_unavailable(tmp_path, monkeypatch):
    """Test that discovery returns an unavailable result when no live config and no fixture exist."""
    # 1. Mock settings to point to the tmp_path for fixtures (which has no fixture in this test)
    monkeypatch.setattr(settings, "EE_PROJECT", "")
    monkeypatch.setattr(settings, "COPERNICUS_USERNAME", "")
    monkeypatch.setattr(settings, "SAFENERGY_FIXTURE_DATA_DIR", str(tmp_path))

    # 2. Create request
    request = SatelliteDiscoveryRequest(
        region_geojson={"type": "Polygon", "coordinates": [[[-98.0, 30.0], [-97.0, 30.0], [-97.0, 31.0], [-98.0, 31.0], [-98.0, 30.0]]]},
        time_start=datetime(2023, 6, 1, 0, 0, 0, tzinfo=timezone.utc),
        time_end=datetime(2023, 6, 2, 0, 0, 0, tzinfo=timezone.utc),
        provider="auto"
    )

    # 3. Execute
    result = discover_satellite_data(request)

    # 4. Verify
    assert isinstance(result, SatelliteUnavailable)
    assert "no fixture data" in result.reason.lower()
    assert result.is_transient is False
