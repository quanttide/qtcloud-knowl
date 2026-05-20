import importlib
from pathlib import Path

import pytest
from app import config


@pytest.fixture(autouse=True)
def reset_config():
    yield
    importlib.reload(config)


class TestConfig:
    def test_data_dir_fallback(self, monkeypatch):
        monkeypatch.delenv("KNOWL_DATA_DIR", raising=False)
        importlib.reload(config)
        expected = Path.home() / ".local" / "share" / "qtcloud-knowl"
        assert config.DATA_DIR == expected

    def test_data_dir_from_env(self, monkeypatch):
        monkeypatch.setenv("KNOWL_DATA_DIR", "/tmp/custom-data")
        importlib.reload(config)
        assert config.DATA_DIR == Path("/tmp/custom-data")

    def test_fixture_dir_points_to_tests(self):
        assert "tests" in str(config.FIXTURE_DIR)
        assert config.FIXTURE_DIR.exists()

    def test_sample_dir_points_to_input(self):
        assert "input" in str(config.SAMPLE_DIR)
        assert config.SAMPLE_DIR.exists()
