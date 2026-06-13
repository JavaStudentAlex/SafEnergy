import logging
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from safenergy.ingest.satellite import DiscoveredSatelliteItem

logger = logging.getLogger(__name__)


class SatelliteFeatureSeed(BaseModel):
    """Minimal deterministic feature representation of a satellite observation."""
    valid_time: datetime = Field(description="Observation time of the item (UTC).")
    cloud_cover_proxy: float = Field(description="Proxy value for cloud cover percentage (0-100).")
    scene_age_minutes: float = Field(description="Age of the scene in minutes at feature extraction time.")
    spatial_coverage_ratio: float = Field(default=1.0, description="Ratio of footprint to requested region (simplified for MVP).")
    is_stale: bool = Field(description="Flag indicating if the scene is older than 60 minutes.")


def extract_satellite_features(items: list[DiscoveredSatelliteItem], extract_time: datetime | None = None) -> list[SatelliteFeatureSeed]:
    """
    Converts raw discovered items into lightweight feature seeds.
    Does not require raster manipulation, acting as the deterministic baseline.
    """
    if extract_time is None:
        extract_time = datetime.now(timezone.utc)

    features = []
    for item in items:
        # Calculate age
        age_delta = extract_time - item.valid_time
        age_minutes = age_delta.total_seconds() / 60.0

        # Determine cloud proxy
        # If real cloud cover is missing, assume clear (0.0) as MVP baseline assumption,
        # but in real usage this would need a more sophisticated missing-data strategy.
        cloud_proxy = item.cloud_cover if item.cloud_cover is not None else 0.0

        feature = SatelliteFeatureSeed(
            valid_time=item.valid_time,
            cloud_cover_proxy=cloud_proxy,
            scene_age_minutes=age_minutes,
            spatial_coverage_ratio=1.0,  # Simplification for MVP (assumes footprint covers requested region)
            is_stale=age_minutes > 60.0
        )
        features.append(feature)

    return features
