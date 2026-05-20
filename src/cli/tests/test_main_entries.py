"""测试各模块 __main__ 入口 — 覆盖 argparse main() 函数"""

from pathlib import Path
import pytest
from tests.conftest import FIXTURE_DIR


class TestDetectDomainMain:
    def test_main_function(self, monkeypatch, capsys):
        import sys
        monkeypatch.setattr(sys, "argv", ["detect_domain.py", str(FIXTURE_DIR / ".." / "input" / "basic-charter.md")])
        from app.detectors.detect_domain import main
        with pytest.raises(SystemExit):
            main()
        captured = capsys.readouterr()
        assert "basic-charter.md" in captured.out


class TestInitDomainMain:
    def test_main_function(self, monkeypatch, capsys, tmp_path):
        monkeypatch.setattr("app.detectors.init_domain.settings.data_home", tmp_path)
        import sys
        monkeypatch.setattr(sys, "argv", ["init_domain.py", "test-domain"])
        from app.detectors.init_domain import main
        with pytest.raises(SystemExit):
            main()
        assert (tmp_path / "test-domain" / "domain.json").exists()


class TestCrossDomainMain:
    def test_main_function(self, monkeypatch, capsys):
        import sys
        monkeypatch.setattr(sys, "argv", ["cross_domain.py", str(FIXTURE_DIR)])
        from app.reporters.cross_domain import main
        with pytest.raises(SystemExit):
            main()
        captured = capsys.readouterr()
        assert "跨领域关系覆盖率报告" in captured.out


class TestAutoFixMain:
    def test_main_function(self, monkeypatch, capsys):
        import sys
        monkeypatch.setattr(sys, "argv", ["auto_fix.py", str(FIXTURE_DIR)])
        from app.validators.auto_fix import main
        with pytest.raises(SystemExit):
            main()
        captured = capsys.readouterr()
        assert "全部验证通过" in captured.out or "骨架文件" in captured.out


class TestValidateMain:
    def test_main_function(self, monkeypatch, capsys):
        import sys
        monkeypatch.setattr(sys, "argv", ["validate.py", str(FIXTURE_DIR)])
        from app.validators.validate import main
        with pytest.raises(SystemExit):
            main()
        captured = capsys.readouterr()
        assert "[OK]" in captured.out
