"""audit 集成测试 — 真实数据链路：审计 fixtures/output/ 的 4 个领域。mode 分支由单元测试覆盖。"""

from typer.testing import CliRunner
from conftest import setup_env


class TestAudit:
    def test_with_fixture_data(self, real_knowledge_base, monkeypatch):
        app = setup_env(monkeypatch, data_home=real_knowledge_base)
        runner = CliRunner()
        result = runner.invoke(app, ["audit"])
        assert result.exit_code == 0
        assert "审计目标" in result.output
