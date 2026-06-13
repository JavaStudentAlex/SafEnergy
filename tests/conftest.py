import pytest


@pytest.fixture
def test_data_dir(tmp_path):
    return tmp_path
