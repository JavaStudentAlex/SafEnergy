import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import duckdb
import pandas as pd

from safenergy.core.config import settings


class StorageClient:
    """
    Handles storage and retrieval of DataFrames as Parquet files,
    using DuckDB to store metadata (like cache_key, creation time, etc).
    """

    def __init__(self, db_path: Optional[str] = None, data_dir: Optional[str] = None):
        """
        Initialize the StorageClient.
        """
        self.data_dir = Path(data_dir or settings.SAFENERGY_CACHE_DIR)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        db_file = db_path or str(self.data_dir / "cache_metadata.duckdb")
        self.conn = duckdb.connect(db_file)
        self._init_db()

    def _init_db(self) -> None:
        """Create the necessary table for cache metadata if it doesn't exist."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS cache_metadata (
                cache_key VARCHAR PRIMARY KEY,
                created_at TIMESTAMP WITH TIME ZONE,
                dataset_type VARCHAR,
                file_path VARCHAR
            )
        """)

    def save_dataframe(self, df: pd.DataFrame, cache_key: str, dataset_type: str) -> str:
        """
        Save a DataFrame to a Parquet file and register it in DuckDB.

        Args:
            df: The pandas DataFrame to save.
            cache_key: Unique identifier for this cached item.
            dataset_type: Type/category of the dataset (e.g., 'weather', 'forecast').

        Returns:
            The file path where the Parquet file was saved.
        """
        file_path = self.data_dir / f"{cache_key}.parquet"

        # Save DataFrame to Parquet
        df.to_parquet(file_path, engine="pyarrow")

        # Insert or update metadata in DuckDB
        now = datetime.now(timezone.utc)

        self.conn.execute("""
            INSERT INTO cache_metadata (cache_key, created_at, dataset_type, file_path)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (cache_key) DO UPDATE SET
                created_at = excluded.created_at,
                dataset_type = excluded.dataset_type,
                file_path = excluded.file_path
        """, (cache_key, now, dataset_type, str(file_path)))

        logging.info(f"Saved dataset '{cache_key}' to {file_path}")
        return str(file_path)

    def get_metadata(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve metadata for a given cache_key.
        """
        result = self.conn.execute(
            "SELECT cache_key, created_at, dataset_type, file_path FROM cache_metadata WHERE cache_key = ?",
            (cache_key,)
        ).fetchone()

        if result:
            return {
                "cache_key": result[0],
                "created_at": result[1],
                "dataset_type": result[2],
                "file_path": result[3]
            }
        return None

    def load_dataframe(self, cache_key: str) -> Optional[pd.DataFrame]:
        """
        Load a DataFrame from a Parquet file using its cache_key.
        """
        metadata = self.get_metadata(cache_key)
        if not metadata:
            logging.info(f"Cache key '{cache_key}' not found.")
            return None

        file_path = Path(metadata["file_path"])
        if not file_path.exists():
            logging.warning(f"File for cache key '{cache_key}' missing at {file_path}.")
            return None

        return pd.read_parquet(file_path, engine="pyarrow")

    def close(self) -> None:
        """Close the DuckDB connection."""
        self.conn.close()
