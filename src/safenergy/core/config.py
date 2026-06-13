from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """SafEnergy configuration, populated from environment variables."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Required Google Earth Engine project
    EE_PROJECT: str = Field(
        default="",
        description="Google Earth Engine project ID, required for MVP satellite ingestion."
    )
    GOOGLE_APPLICATION_CREDENTIALS: str | None = Field(
        default=None,
        description="Optional absolute path to Google service account JSON."
    )

    # Optional fallback Copernicus
    COPERNICUS_USERNAME: str = ""
    COPERNICUS_PASSWORD: str = ""

    # Optional Sentinel Hub
    SENTINELHUB_CLIENT_ID: str = ""
    SENTINELHUB_CLIENT_SECRET: str = ""

    # Optional EUMETSAT
    EUMETSAT_CONSUMER_KEY: str = ""
    EUMETSAT_CONSUMER_SECRET: str = ""

    # Optional Market
    ENTSOE_API_TOKEN: str = ""
    EIA_API_KEY: str = ""

    # Path overrides
    SAFENERGY_DATA_DIR: str = Field(default="data")
    SAFENERGY_CACHE_DIR: str = Field(default="data/cache")
    SAFENERGY_FIXTURE_DATA_DIR: str = Field(default="data/fixtures")

settings = Settings()
