from datetime import datetime, timezone

from safenergy.features.satellite import extract_satellite_features
from safenergy.ingest.satellite import DiscoveredSatelliteItem


def test_extract_satellite_features():
    """Test extracting feature seeds from discovered satellite items."""
    # 1. Setup mock data
    item1 = DiscoveredSatelliteItem(
        id="test_id_1",
        provider="test",
        valid_time=datetime(2023, 6, 1, 12, 0, 0, tzinfo=timezone.utc),
        footprint={"type": "Polygon", "coordinates": []},
        crs="EPSG:4326",
        cloud_cover=15.0,
        cache_key="test1"
    )

    item2 = DiscoveredSatelliteItem(
        id="test_id_2",
        provider="test",
        valid_time=datetime(2023, 6, 1, 11, 0, 0, tzinfo=timezone.utc),
        footprint={"type": "Polygon", "coordinates": []},
        crs="EPSG:4326",
        cloud_cover=None,  # Missing cloud cover
        cache_key="test2"
    )

    items = [item1, item2]

    # Extract time is 12:30 (so item1 is 30 mins old, item2 is 90 mins old)
    extract_time = datetime(2023, 6, 1, 12, 30, 0, tzinfo=timezone.utc)

    # 2. Execute
    features = extract_satellite_features(items, extract_time=extract_time)

    # 3. Verify
    assert len(features) == 2

    feat1 = features[0]
    assert feat1.cloud_cover_proxy == 15.0
    assert feat1.scene_age_minutes == 30.0
    assert feat1.is_stale is False
    assert feat1.spatial_coverage_ratio == 1.0

    feat2 = features[1]
    assert feat2.cloud_cover_proxy == 0.0  # Fallback
    assert feat2.scene_age_minutes == 90.0
    assert feat2.is_stale is True
