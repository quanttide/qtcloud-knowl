"""测试 CLI 命令执行 — 直接调用底层函数"""

from pathlib import Path
from unittest.mock import MagicMock
from tests.conftest import FIXTURE_DIR, SAMPLE_DIR


class TestCliCommands:
    """直接调用各模块的 run() 函数，绕过 Typer CLI"""

    def test_summary(self, monkeypatch, capsys):
        monkeypatch.setattr("app.config.settings.data_home", FIXTURE_DIR)
        from app.reporters.summary import run
        result = run(data_dir=FIXTURE_DIR)
        captured = capsys.readouterr()
        assert result == 0
        assert "领域" in captured.out

    def test_validate(self, monkeypatch, capsys):
        monkeypatch.setattr("app.config.settings.data_home", FIXTURE_DIR)
        from app.validators.validate import run
        run(data_dir=FIXTURE_DIR)
        captured = capsys.readouterr()
        assert "[OK]" in captured.out

    def test_find_undefined_terms(self, monkeypatch, capsys):
        monkeypatch.setattr("app.config.settings.data_home", FIXTURE_DIR)
        monkeypatch.setattr("app.config.settings.sample_home", SAMPLE_DIR)
        from app.validators.find_undefined import run
        result = run(data_dir=FIXTURE_DIR, sample_dir=SAMPLE_DIR)
        captured = capsys.readouterr()
        assert result == 0
        assert "全部术语已有定义" in captured.out or "未定义" in captured.out

    def test_fusion_check(self, monkeypatch, capsys):
        monkeypatch.setattr("app.config.settings.data_home", FIXTURE_DIR)
        monkeypatch.setattr("app.config.settings.sample_home", SAMPLE_DIR)
        from app.validators.fusion_check import run
        result = run(data_dir=FIXTURE_DIR, sample_dir=SAMPLE_DIR)
        assert result == 0

    def test_check_abstraction(self, monkeypatch, capsys):
        monkeypatch.setattr("app.config.settings.data_home", FIXTURE_DIR)
        from app.reporters.abstraction import run
        result = run(data_dir=FIXTURE_DIR)
        captured = capsys.readouterr()
        assert result in (0, 1)

    def test_auto_fix(self, monkeypatch, capsys):
        monkeypatch.setattr("app.config.settings.data_home", FIXTURE_DIR)
        from app.validators.auto_fix import run
        run(data_dir=FIXTURE_DIR)
        captured = capsys.readouterr()
        assert "[OK]" in captured.out

    def test_cross_domain_report(self, monkeypatch, capsys):
        monkeypatch.setattr("app.config.settings.data_home", FIXTURE_DIR)
        from app.reporters.cross_domain import run
        result = run(data_dir=FIXTURE_DIR)
        captured = capsys.readouterr()
        assert result == 0
        assert "跨领域关系覆盖率报告" in captured.out

    def test_detect_domain(self, monkeypatch, capsys):
        monkeypatch.setattr("app.config.settings.data_home", FIXTURE_DIR)
        from app.detectors.detect_domain import run
        sample = SAMPLE_DIR / "basic-charter.md"
        result = run(filepath=str(sample), data_dir=FIXTURE_DIR)
        captured = capsys.readouterr()
        assert result == 0
        assert "basic-charter.md" in captured.out


class TestCliMain:
    """测试 app.cli.main() 入口函数"""

    def test_main_function(self, monkeypatch):
        mock_app = MagicMock()
        monkeypatch.setattr("app.cli.app", mock_app)
        from app.cli import main
        main()
        mock_app.assert_called_once()

    def test_main_exit_code_zero(self, monkeypatch):
        mock_app = MagicMock(return_value=0)
        monkeypatch.setattr("app.cli.app", mock_app)
        from app.cli import main
        result = main()
        assert result == 0


class TestCliCommandAudit:
    def test_audit_cli_via_runner(self):
        from typer.testing import CliRunner
        from app.cli import app
        runner = CliRunner()
        result = runner.invoke(app, ["audit", str(FIXTURE_DIR)])
        assert "知识库概览" in result.output


class TestCliCommandInitDomain:
    def test_init_domain(self, tmp_path):
        from app.detectors.init_domain import run
        result = run("test-domain", data_dir=tmp_path)
        assert result == 0
        assert (tmp_path / "test-domain" / "domain.json").exists()
