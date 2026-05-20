"""测试 CLI 命令执行 — 覆盖 Typer 命令的 run() 调用"""

from pathlib import Path
import pytest
from typer.testing import CliRunner
from tests.conftest import FIXTURE_DIR, SAMPLE_DIR


class TestCliCommands:
    def _invoke(self, monkeypatch, *args):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(FIXTURE_DIR))
        monkeypatch.setenv("QTCLOUD_KNOWL_SAMPLE_HOME", str(SAMPLE_DIR))
        import importlib
        from app import config
        importlib.reload(config)
        from app.cli import app
        return CliRunner().invoke(app, list(args))

    def test_summary(self, monkeypatch):
        result = self._invoke(monkeypatch, "summary")
        assert result.exit_code == 0
        assert "领域" in result.output

    def test_validate(self, monkeypatch):
        result = self._invoke(monkeypatch, "validate")
        assert result.exit_code == 0
        assert "[OK]" in result.output

    def test_find_undefined_terms(self, monkeypatch):
        result = self._invoke(monkeypatch, "find-undefined-terms")
        assert result.exit_code == 0
        assert "全部术语已有定义" in result.output or "未定义" in result.output

    def test_fusion_check(self, monkeypatch):
        result = self._invoke(monkeypatch, "fusion-check")
        assert result.exit_code == 0

    def test_check_abstraction(self, monkeypatch):
        result = self._invoke(monkeypatch, "check-abstraction")
        assert result.exit_code == 0
        assert "所有本体" in result.output or "[通过]" in result.output

    def test_auto_fix(self, monkeypatch):
        result = self._invoke(monkeypatch, "auto-fix")
        assert result.exit_code == 0
        assert "[OK]" in result.output

    def test_cross_domain_report(self, monkeypatch):
        result = self._invoke(monkeypatch, "cross-domain-report")
        assert result.exit_code == 0
        assert "跨领域关系覆盖率报告" in result.output

    def test_detect_domain(self, monkeypatch):
        sample = SAMPLE_DIR / "basic-charter.md"
        result = self._invoke(monkeypatch, "detect-domain", str(sample))
        assert result.exit_code == 0
        assert "basic-charter.md" in result.output


class TestCliMain:
    def test_main_function(self, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(FIXTURE_DIR))
        import importlib
        from app import config
        importlib.reload(config)
        from app.cli import main
        import sys
        monkeypatch.setattr(sys, "argv", ["qtcloud-knowl", "summary"])
        with pytest.raises(SystemExit):
            main()

    def test_main_exit_code_zero(self, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(FIXTURE_DIR))
        import importlib
        from app import config
        importlib.reload(config)
        from app.cli import main
        import sys
        monkeypatch.setattr(sys, "argv", ["qtcloud-knowl", "summary"])
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0


class TestCliCommandInitDomain:
    def test_init_domain(self, monkeypatch, tmp_path):
        monkeypatch.setattr("app.detectors.init_domain.settings.data_home", tmp_path)
        from app.cli import app
        result = CliRunner().invoke(app, ["init-domain", "test-domain"])
        assert result.exit_code == 0
        assert (tmp_path / "test-domain" / "domain.json").exists()
