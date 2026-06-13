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

    # Save the dataframe
    file_path = storage_client.save_dataframe(df, cache_key, dataset_type)

    # Check if the file exists
    assert Path(file_path).exists()

    # Retrieve metadata
    metadata = storage_client.get_metadata(cache_key)
    assert metadata is not None
    assert metadata["cache_key"] == cache_key
    assert metadata["dataset_type"] == dataset_type
    assert metadata["file_path"] == file_path

    # Load the dataframe
    loaded_df = storage_client.load_dataframe(cache_key)
    assert loaded_df is not None
    pd.testing.assert_frame_equal(df, loaded_df)

def test_load_non_existent_key(storage_client):
    loaded_df = storage_client.load_dataframe("non_existent_key")
    assert loaded_df is None
