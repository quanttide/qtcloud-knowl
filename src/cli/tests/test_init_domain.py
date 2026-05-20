"""测试领域初始化 — 骨架文件创建"""

import json

import pytest

from app.detectors.init_domain import run, SKELETONS


class TestInitDomain:
    def test_creates_domain_directory(self, tmp_path, monkeypatch):
        monkeypatch.setattr("app.detectors.init_domain.settings.data_home", tmp_path)
        run("test-domain")
        domain_dir = tmp_path / "test-domain"
        assert domain_dir.exists()

    def test_creates_domain_json(self, tmp_path, monkeypatch):
        monkeypatch.setattr("app.detectors.init_domain.settings.data_home", tmp_path)
        run("test-domain")
        fpath = tmp_path / "test-domain" / "domain.json"
        assert fpath.exists()
        data = json.loads(fpath.read_text(encoding="utf-8"))
        assert data["id"] == "test-domain"

    def test_creates_skeleton_files(self, tmp_path, monkeypatch):
        monkeypatch.setattr("app.detectors.init_domain.settings.data_home", tmp_path)
        run("test-domain")
        for name in SKELETONS:
            fpath = tmp_path / "test-domain" / name
            assert fpath.exists(), f"Missing {name}"
            data = json.loads(fpath.read_text(encoding="utf-8"))
            assert data == SKELETONS[name]

    def test_from_detect_file_sets_file_ref(self, tmp_path, monkeypatch):
        monkeypatch.setattr("app.detectors.init_domain.settings.data_home", tmp_path)
        run("test-domain", from_detect_file="input/basic-charter.md")
        fpath = tmp_path / "test-domain" / "domain.json"
        data = json.loads(fpath.read_text(encoding="utf-8"))
        assert data["files"] == ["tests/fixtures/input/basic-charter.md"]

    def test_idempotent_when_domain_exists(self, tmp_path, monkeypatch):
        monkeypatch.setattr("app.detectors.init_domain.settings.data_home", tmp_path)
        run("test-domain")
        run("test-domain")
        domain_dir = tmp_path / "test-domain"
        assert domain_dir.exists()
        for name in list(SKELETONS) + ["domain.json"]:
            assert (domain_dir / name).exists()

    def test_return_zero(self, tmp_path, monkeypatch):
        monkeypatch.setattr("app.detectors.init_domain.settings.data_home", tmp_path)
        result = run("test-domain")
        assert result == 0
