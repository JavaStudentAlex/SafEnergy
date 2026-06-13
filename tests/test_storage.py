from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

from safenergy.storage.client import StorageClient


@pytest.fixture
def storage_client(tmp_path: Path):
    db_path = str(tmp_path / "test_cache_metadata.duckdb")
    data_dir = str(tmp_path / "cache")
    client = StorageClient(db_path=db_path, data_dir=data_dir)
    yield client
    client.close()



def test_save_and_load_dataframe(storage_client):
    # Create a dummy dataframe
    df = pd.DataFrame({
        "timestamp": pd.date_range("2023-01-01", periods=3, freq="h", tz="UTC"),
        "value": [10.5, 11.2, 12.0]
    })
    df.set_index("timestamp", inplace=True)

    cache_key = "test_data_v1"
    dataset_type = "test"
    provider = "test_provider"
    issue_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
    valid_time_start = datetime(2023, 1, 1, tzinfo=timezone.utc)
    valid_time_end = datetime(2023, 1, 1, 3, tzinfo=timezone.utc)
    crs = "EPSG:4326"
    footprint = {"type": "Polygon", "coordinates": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]}
    quality = {"cloud_cover": 10.5, "staleness_hours": 0.5}

    # Save the dataframe
    file_path = storage_client.save_dataframe(
        df=df,
        cache_key=cache_key,
        dataset_type=dataset_type,
        provider=provider,
        issue_time=issue_time,
        valid_time_start=valid_time_start,
        valid_time_end=valid_time_end,
        crs=crs,
        footprint=footprint,
        quality=quality
    )

    # Check if the file exists
    assert Path(file_path).exists()

    # Retrieve metadata
    metadata = storage_client.get_metadata(cache_key)
    assert metadata is not None
    assert metadata["cache_key"] == cache_key
    assert metadata["dataset_type"] == dataset_type
    assert metadata["file_path"] == file_path
    assert metadata["provider"] == provider
    assert metadata["issue_time"] == issue_time
    assert metadata["valid_time_start"] == valid_time_start
    assert metadata["valid_time_end"] == valid_time_end
    assert metadata["crs"] == crs
    assert metadata["footprint"] == footprint
    assert metadata["quality"] == quality

    # Load the dataframe
    loaded_df = storage_client.load_dataframe(cache_key)
    assert loaded_df is not None
    pd.testing.assert_frame_equal(df, loaded_df)

def test_load_non_existent_key(storage_client):
    loaded_df = storage_client.load_dataframe("non_existent_key")
    assert loaded_df is None
