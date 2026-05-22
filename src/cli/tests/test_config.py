import importlib
from pathlib import Path

import pytest
from app import config


class TestConfigEdge:
    def test_vault_unavailable_path(self, monkeypatch):
        import builtins
        _orig_import = builtins.__import__

        def _mock_import(name, *args, **kwargs):
            if name == "pydantic_vault":
                raise ImportError(f"No module named '{name}'")
            return _orig_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _mock_import)
        import importlib
        importlib.reload(config)
        assert config.settings is not None

    def test_field_validator_non_empty_string(self, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", "/custom/nonempty/path")
        import importlib
        importlib.reload(config)
        assert str(config.settings.data_home) == "/custom/nonempty/path"

    def test_empty_str_to_none_direct_call(self):
        from app.config import Settings
        assert Settings._empty_str_to_none("") is None
        assert Settings._empty_str_to_none("/path") == "/path"
        assert Settings._empty_str_to_none(None) is None


@pytest.fixture(autouse=True)
def reset_config():
    yield
    importlib.reload(config)


class TestConfig:
    def test_data_dir_fallback(self, monkeypatch):
        monkeypatch.delenv("QTCLOUD_KNOWL_DATA_HOME", raising=False)
        importlib.reload(config)
        assert config.settings.data_home == Path.cwd() / "data"

    def test_data_dir_from_env(self, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", "/tmp/custom-data")
        importlib.reload(config)
        assert config.settings.data_home == Path("/tmp/custom-data")

    def test_sample_home_defaults_to_data_home_samples(self):
        assert config.settings.sample_home is not None
        assert config.settings.sample_home.name == "samples"

    def test_sample_home_from_env(self, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_SAMPLE_HOME", "/tmp/my-sources")
        importlib.reload(config)
        assert config.settings.sample_home == Path("/tmp/my-sources")

    def test_production_data_dir_works_end_to_end(self, monkeypatch, tmp_path):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(tmp_path))
        importlib.reload(config)
        assert config.settings.data_home == tmp_path
