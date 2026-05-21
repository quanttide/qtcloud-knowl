"""测试自动修复 — 骨架文件补全循环"""

import json

from tests.conftest import FIXTURE_DIR
from app.validators.auto_fix import run, SKELETONS, REQUIRED_FILES, MAX_ITER


class TestAutoFix:
    def test_fixtures_pass_without_fix(self, capsys):
        result = run(FIXTURE_DIR)
        captured = capsys.readouterr()
        assert "全部通过" in captured.out
        assert "全部验证通过" in result

    def test_fills_missing_skeleton_files(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(tmp_path))
        import importlib
        from app import config
        config.settings.reload_from_env()
        domain_dir = tmp_path / "test-domain"
        domain_dir.mkdir()
        (domain_dir / "domain.json").write_text(
            '{"id": "test", "name": "test", "vocabulary": []}', encoding="utf-8"
        )
        result = run(tmp_path)
        captured = capsys.readouterr()
        for name in REQUIRED_FILES:
            assert (domain_dir / name).exists(), f"Missing {name}"
        assert "全部验证通过" in result

    def test_does_not_overwrite_existing_files(self, tmp_path, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(tmp_path))
        import importlib
        from app import config
        config.settings.reload_from_env()
        domain_dir = tmp_path / "test-domain"
        domain_dir.mkdir()
        for name, content in [
            ("domain.json", '{"id": "test", "name": "test", "vocabulary": []}'),
            ("ontologies.json", '{"ontologies": [{"id": "o1"}]}'),
            ("instances.json", '{"instances": [{"id": "i1"}]}'),
            ("relations.json", '{"relations": [{"id": "r1"}]}'),
        ]:
            (domain_dir / name).write_text(content, encoding="utf-8")
        run(tmp_path)
        ont = json.loads((domain_dir / "ontologies.json").read_text(encoding="utf-8"))
        assert ont["ontologies"] == [{"id": "o1"}]

    def test_reports_json_errors(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(tmp_path))
        import importlib
        from app import config
        config.settings.reload_from_env()
        domain_dir = tmp_path / "bad-domain"
        domain_dir.mkdir()
        (domain_dir / "domain.json").write_text("{invalid json}", encoding="utf-8")
        (domain_dir / "ontologies.json").write_text("{}", encoding="utf-8")
        (domain_dir / "instances.json").write_text("{}", encoding="utf-8")
        (domain_dir / "relations.json").write_text("{}", encoding="utf-8")
        run(tmp_path)
        captured = capsys.readouterr()
        assert "JSON 格式错误" in captured.out

    def test_max_iter_constant(self):
        assert MAX_ITER == 10

    def test_required_files_defined(self):
        assert "ontologies.json" in REQUIRED_FILES
        assert "instances.json" in REQUIRED_FILES
        assert "relations.json" in REQUIRED_FILES

    def test_missing_data_dir_returns_error(self, capsys):
        result = run("/nonexistent")
        captured = capsys.readouterr()
        assert "数据目录不存在" in captured.out
