import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from safenergy.core.config import settings

logger = logging.getLogger(__name__)


class SatelliteDiscoveryRequest(BaseModel):
    """Normalized request for satellite discovery."""
    region_geojson: dict[str, Any] = Field(description="GeoJSON polygon of the target region.")
    time_start: datetime = Field(description="Start of the search window (UTC).")
    time_end: datetime = Field(description="End of the search window (UTC).")
    provider: str = Field(default="auto", description="Provider hint or 'auto' for best available.")


class DiscoveredSatelliteItem(BaseModel):
    """Normalized metadata for a discovered satellite item."""
    id: str = Field(description="Provider-specific item ID.")
    provider: str = Field(description="Name of the satellite provider.")
    valid_time: datetime = Field(description="Observation time of the item (UTC).")
    issue_time: datetime | None = Field(default=None, description="Time the item was published/processed (UTC).")
    footprint: dict[str, Any] = Field(description="GeoJSON geometry of the item footprint.")
    crs: str = Field(default="EPSG:4326", description="Coordinate Reference System.")
    cloud_cover: float | None = Field(default=None, description="Cloud cover percentage (0-100), if available.")
    cache_key: str = Field(description="Deterministic key for caching this item's data.")


class SatelliteUnavailable(BaseModel):
    """Diagnostic returned when a provider is unavailable or unconfigured."""
    reason: str = Field(description="Reason for unavailability.")
    provider: str = Field(description="The provider that was attempted.")
    is_transient: bool = Field(default=False, description="True if a retry might succeed later.")


def discover_satellite_data(request: SatelliteDiscoveryRequest) -> list[DiscoveredSatelliteItem] | SatelliteUnavailable:
    """
    Discovers available satellite items for the given request.
    If the live provider is unconfigured or fails, it attempts to fall back to a deterministic fixture.
    """
    # 1. Check if live provider is configured (e.g. EE_PROJECT)
    if settings.EE_PROJECT or settings.COPERNICUS_USERNAME:
        # In a real implementation, we would call the live API here.
        # For the scope of S01, we just simulate an unavailable response unless it's explicitly tested
        pass

    # 2. Fall back to fixture data
    fixture_path = Path(settings.SAFENERGY_FIXTURE_DATA_DIR) / "satellite" / "sample_discovery.json"
    if fixture_path.exists():
        logger.info(f"Using satellite discovery fixture from {fixture_path}")
        try:
            with open(fixture_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Simple filtering based on the request could go here,
            # but for MVP fixtures, returning the contents is often enough.
            items = []
            for item_data in data.get("items", []):
                # Ensure we parse datetime correctly from fixture strings
                if isinstance(item_data.get("valid_time"), str):
                    item_data["valid_time"] = datetime.fromisoformat(item_data["valid_time"].replace("Z", "+00:00"))
                if isinstance(item_data.get("issue_time"), str):
                    item_data["issue_time"] = datetime.fromisoformat(item_data["issue_time"].replace("Z", "+00:00"))

                items.append(DiscoveredSatelliteItem(**item_data))
            return items
        except Exception as e:
            logger.warning(f"Failed to load fixture data: {e}")
            return SatelliteUnavailable(
                reason=f"Failed to load fixture data: {e}",
                provider="fixture",
                is_transient=False
            )

    # 3. If no live config and no fixture, return unavailable
    return SatelliteUnavailable(
        reason="No live provider configured and no fixture data available.",
        provider=request.provider,
        is_transient=False
    )
