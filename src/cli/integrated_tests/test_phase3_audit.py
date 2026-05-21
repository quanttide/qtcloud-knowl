"""
OCL 阶段五测试：结构完整性检查 — audit
"""

from typer.testing import CliRunner
from conftest import setup_env


class TestAudit:
    def test_audit_empty_kb(self, tmp_path, monkeypatch):
        app = setup_env(monkeypatch, data_home=tmp_path)
        runner = CliRunner()
        result = runner.invoke(app, ["audit"])
        assert result.exit_code == 0
        assert "审计" in result.output

    def test_audit_with_fixture_data(self, real_knowledge_base, monkeypatch):
        app = setup_env(monkeypatch, data_home=real_knowledge_base)
        runner = CliRunner()
        result = runner.invoke(app, ["audit"])
        assert result.exit_code == 0
        assert "审计目标" in result.output

    def test_audit_simple_mode(self, real_knowledge_base, monkeypatch):
        app = setup_env(monkeypatch, data_home=real_knowledge_base)
        runner = CliRunner()
        result = runner.invoke(app, ["audit", "--mode", "simple"])
        assert result.exit_code == 0

    def test_audit_invalid_mode(self, real_knowledge_base, monkeypatch):
        app = setup_env(monkeypatch, data_home=real_knowledge_base)
        runner = CliRunner()
        result = runner.invoke(app, ["audit", "--mode", "bogus"])
        assert result.exit_code != 0
