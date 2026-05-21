"""
OCL 阶段五测试：结构完整性检查 — audit

验证用户能运行质量审计，查看检测报告。
"""

from typer.testing import CliRunner


def _setup(monkeypatch, data_home):
    monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(data_home))
    import importlib
    from app import config
    importlib.reload(config)
    import app.reviewers.data as rdata
    import app.review as rmod
    importlib.reload(rdata)
    importlib.reload(rmod)
    import app.cli as cli_mod
    importlib.reload(cli_mod)
    return cli_mod.app


class TestAudit:
    def test_audit_empty_kb(self, tmp_path, monkeypatch):
        app = _setup(monkeypatch, tmp_path)
        runner = CliRunner()
        result = runner.invoke(app, ["audit"])
        assert result.exit_code == 0
        assert "审计" in result.output

    def test_audit_with_fixture_data(self, knowledge_base, monkeypatch):
        app = _setup(monkeypatch, knowledge_base)
        runner = CliRunner()
        result = runner.invoke(app, ["audit"])
        assert result.exit_code == 0
        assert "审计目标" in result.output

    def test_audit_simple_mode(self, knowledge_base, monkeypatch):
        app = _setup(monkeypatch, knowledge_base)
        runner = CliRunner()
        result = runner.invoke(app, ["audit", "--mode", "simple"])
        assert result.exit_code == 0

    def test_audit_invalid_mode(self, knowledge_base, monkeypatch):
        app = _setup(monkeypatch, knowledge_base)
        runner = CliRunner()
        result = runner.invoke(app, ["audit", "--mode", "bogus"])
        assert result.exit_code != 0
