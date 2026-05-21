"""测试 CLI 命令执行 — 覆盖 argparse 命令的 func 调用"""

from pathlib import Path
from tests.conftest import FIXTURE_DIR, SAMPLE_DIR


class TestCliCommands:
    def _run(self, monkeypatch, *args):
        monkeypatch.setattr("app.config.settings.data_home", FIXTURE_DIR)
        monkeypatch.setattr("app.config.settings.sample_home", SAMPLE_DIR)
        import sys
        monkeypatch.setattr(sys, "argv", ["qtcloud-knowl", *args])
        from app.cli import main
        return main()

    def test_summary(self, monkeypatch):
        assert self._run(monkeypatch, "summary") == 0

    def test_validate(self, monkeypatch):
        assert self._run(monkeypatch, "validate") == 0

    def test_find_undefined_terms(self, monkeypatch):
        self._run(monkeypatch, "find-undefined-terms")

    def test_fusion_check(self, monkeypatch):
        assert self._run(monkeypatch, "fusion-check") == 0

    def test_check_abstraction(self, monkeypatch):
        self._run(monkeypatch, "check-abstraction")

    def test_auto_fix(self, monkeypatch):
        self._run(monkeypatch, "auto-fix")

    def test_cross_domain_report(self, monkeypatch):
        assert self._run(monkeypatch, "cross-domain-report") == 0

    def test_detect_domain(self, monkeypatch):
        sample = SAMPLE_DIR / "basic-charter.md"
        assert self._run(monkeypatch, "detect-domain", str(sample)) == 0


class TestCliMain:
    def _run(self, monkeypatch, *args):
        import importlib
        import app.config
        import app.cli
        importlib.reload(app.config)
        importlib.reload(app.cli)
        monkeypatch.setattr("app.config.settings.data_home", FIXTURE_DIR)
        import sys
        monkeypatch.setattr(sys, "argv", ["qtcloud-knowl", *args])
        from app.cli import main
        return main()

    def test_main_function(self, monkeypatch):
        assert self._run(monkeypatch, "summary") == 0

    def test_main_exit_code_zero(self, monkeypatch):
        assert self._run(monkeypatch, "summary") == 0


class TestCliCommandInitDomain:
    def test_init_domain(self, monkeypatch, tmp_path):
        monkeypatch.setattr("app.config.settings.data_home", tmp_path)
        monkeypatch.setattr("app.detectors.init_domain.settings.data_home", tmp_path)
        from app.cli import main
        import sys
        monkeypatch.setattr(sys, "argv", ["qtcloud-knowl", "init-domain", "test-domain"])
        main()
        assert (tmp_path / "test-domain" / "domain.json").exists()
