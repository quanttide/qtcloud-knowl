import importlib
from pathlib import Path

import pytest
from app import config


class _FakeLocalStorage:
    def __init__(self, app_name, vendor=None):
        self.data_dir = Path.home() / ".local" / "share" / vendor / app_name


@pytest.fixture(autouse=True)
def reset_config():
    yield
    importlib.reload(config)


class TestConfig:
    def test_data_dir_fallback(self, monkeypatch):
        monkeypatch.delenv("QTCLOUD_KNOWL_DATA_HOME", raising=False)
        import quanttide
        monkeypatch.setattr(quanttide, "LocalStorage", _FakeLocalStorage)
        importlib.reload(config)
        assert config.settings.data_home == Path.home() / ".local" / "share" / "quanttide" / "qtcloud-knowl"

    def test_data_dir_from_env(self, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", "/tmp/custom-data")
        importlib.reload(config)
        assert config.settings.data_home == Path("/tmp/custom-data")

    def test_sample_dir_points_to_input(self):
        assert "input" in str(config.SAMPLE_DIR)
        assert config.SAMPLE_DIR.exists()

    def test_production_data_dir_works_end_to_end(self, monkeypatch, tmp_path):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(tmp_path))
        importlib.reload(config)
        assert config.settings.data_home == tmp_path
        domain_dir = tmp_path / "test-domain"
        domain_dir.mkdir()
        for fname, content in [
            ("domain.json", '{"id": "test", "name": "test", "vocabulary": []}'),
            ("ontologies.json", '{"ontologies": []}'),
            ("instances.json", '{"instances": []}'),
            ("relations.json", '{"relations": []}'),
        ]:
            (domain_dir / fname).write_text(content, encoding="utf-8")
        from app.validators.validate import run as validate_run
        from app.reporters.summary import run as summary_run
        assert validate_run(tmp_path) == 0
        assert summary_run(tmp_path) == 0
