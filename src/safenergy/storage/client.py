import json
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

        # Ensure new columns exist for provenance and geospatial metadata
        columns_info = self.conn.execute("PRAGMA table_info('cache_metadata')").fetchall()
        existing_columns = {col[1] for col in columns_info}

        expected_columns = {
            "provider": "VARCHAR",
            "issue_time": "TIMESTAMP WITH TIME ZONE",
            "valid_time_start": "TIMESTAMP WITH TIME ZONE",
            "valid_time_end": "TIMESTAMP WITH TIME ZONE",
            "crs": "VARCHAR",
            "footprint": "JSON",
            "quality": "JSON"
        }

        for col_name, col_type in expected_columns.items():
            if col_name not in existing_columns:
                self.conn.execute(f"ALTER TABLE cache_metadata ADD COLUMN {col_name} {col_type}")

    def save_dataframe(
        self,
        df: pd.DataFrame,
        cache_key: str,
        dataset_type: str,
        provider: Optional[str] = None,
        issue_time: Optional[datetime] = None,
        valid_time_start: Optional[datetime] = None,
        valid_time_end: Optional[datetime] = None,
        crs: Optional[str] = None,
        footprint: Optional[Dict[str, Any]] = None,
        quality: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save a DataFrame to a Parquet file and register it in DuckDB.

        Args:
            df: The pandas DataFrame to save.
            cache_key: Unique identifier for this cached item.
            dataset_type: Type/category of the dataset (e.g., 'weather', 'forecast').
            provider: Provider name.
            issue_time: Time the data was issued (UTC).
            valid_time_start: Start of the valid time range (UTC).
            valid_time_end: End of the valid time range (UTC).
            crs: Coordinate Reference System.
            footprint: GeoJSON footprint as a dictionary.
            quality: Quality or staleness diagnostics as a dictionary.

        Returns:
            The file path where the Parquet file was saved.
        """
        file_path = self.data_dir / f"{cache_key}.parquet"

        # Save DataFrame to Parquet
        df.to_parquet(file_path, engine="pyarrow")

        # Insert or update metadata in DuckDB
        now = datetime.now(timezone.utc)
        footprint_str = json.dumps(footprint) if footprint is not None else None
        quality_str = json.dumps(quality) if quality is not None else None

        self.conn.execute("""
            INSERT INTO cache_metadata (
                cache_key, created_at, dataset_type, file_path,
                provider, issue_time, valid_time_start, valid_time_end, crs, footprint, quality
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (cache_key) DO UPDATE SET
                created_at = excluded.created_at,
                dataset_type = excluded.dataset_type,
                file_path = excluded.file_path,
                provider = excluded.provider,
                issue_time = excluded.issue_time,
                valid_time_start = excluded.valid_time_start,
                valid_time_end = excluded.valid_time_end,
                crs = excluded.crs,
                footprint = excluded.footprint,
                quality = excluded.quality
        """, (
            cache_key, now, dataset_type, str(file_path),
            provider, issue_time, valid_time_start, valid_time_end, crs, footprint_str, quality_str
        ))

        logging.info(f"Saved dataset '{cache_key}' to {file_path}")
        return str(file_path)

    def get_metadata(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve metadata for a given cache_key.
        """
        result = self.conn.execute(
            """
            SELECT cache_key, created_at, dataset_type, file_path,
                   provider, issue_time, valid_time_start, valid_time_end, crs, footprint, quality
            FROM cache_metadata WHERE cache_key = ?
            """,
            (cache_key,)
        ).fetchone()

        if result:
            meta = {
                "cache_key": result[0],
                "created_at": result[1],
                "dataset_type": result[2],
                "file_path": result[3],
                "provider": result[4],
                "issue_time": result[5],
                "valid_time_start": result[6],
                "valid_time_end": result[7],
                "crs": result[8],
                "footprint": None,
                "quality": None
            }
            if result[9]:
                try:
                    meta["footprint"] = json.loads(result[9])
                except json.JSONDecodeError:
                    logging.warning(f"Failed to decode footprint JSON for cache_key '{cache_key}'")
            if result[10]:
                try:
                    meta["quality"] = json.loads(result[10])
                except json.JSONDecodeError:
                    logging.warning(f"Failed to decode quality JSON for cache_key '{cache_key}'")
            return meta
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
