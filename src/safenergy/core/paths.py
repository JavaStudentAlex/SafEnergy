from pathlib import Path

from safenergy.core.config import settings


def get_data_dir() -> Path:
    p = Path(settings.SAFENERGY_DATA_DIR)
    p.mkdir(parents=True, exist_ok=True)
    return p

def get_cache_dir() -> Path:
    p = Path(settings.SAFENERGY_CACHE_DIR)
    p.mkdir(parents=True, exist_ok=True)
    return p

def get_fixture_dir() -> Path:
    p = Path(settings.SAFENERGY_FIXTURE_DATA_DIR)
    p.mkdir(parents=True, exist_ok=True)
    return p
