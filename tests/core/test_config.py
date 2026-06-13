
from safenergy.core.config import Settings
from safenergy.core.paths import get_cache_dir, get_data_dir, get_fixture_dir


def test_settings_defaults():
    settings = Settings()
    # If not set in env, it defaults to empty string or default value
    assert settings.SAFENERGY_DATA_DIR == "data"
    assert settings.SAFENERGY_CACHE_DIR == "data/cache"
    assert settings.SAFENERGY_FIXTURE_DATA_DIR == "data/fixtures"

def test_paths_creation(tmp_path, monkeypatch):
    monkeypatch.setenv("SAFENERGY_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("SAFENERGY_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("SAFENERGY_FIXTURE_DATA_DIR", str(tmp_path / "fixtures"))

    # Reload settings with new env vars
    from safenergy.core.config import Settings
    temp_settings = Settings()

    # Patch settings in paths module
    import safenergy.core.paths
    monkeypatch.setattr(safenergy.core.paths, "settings", temp_settings)

    data_dir = get_data_dir()
    assert data_dir.exists()
    assert str(data_dir).endswith("data")

    cache_dir = get_cache_dir()
    assert cache_dir.exists()
    assert str(cache_dir).endswith("cache")

    fixture_dir = get_fixture_dir()
    assert fixture_dir.exists()
    assert str(fixture_dir).endswith("fixtures")
