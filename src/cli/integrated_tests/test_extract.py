"""extract 集成测试 — 真实数据链路：从 fixtures/input/ 创建骨架。条件分支由单元测试覆盖。"""

from typer.testing import CliRunner
from conftest import setup_env


class TestExtract:
    def test_creates_skeleton_from_samples(self, real_sample_dir, real_knowledge_base, monkeypatch):
        app = setup_env(monkeypatch, sample_dir=real_sample_dir, data_home=real_knowledge_base)
        runner = CliRunner()
        result = runner.invoke(app, ["extract"])
        assert result.exit_code == 0
        assert "抽取完成" in result.output
