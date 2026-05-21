"""
OCL 阶段一测试：知识源准备 → AI 粗提取

保留：仅真实数据链路测试。条件分支（空目录、缺 key、文件不存在）由单元测试覆盖。
"""

from typer.testing import CliRunner
from conftest import setup_env


class TestExtractSkeleton:
    def test_creates_skeleton_from_samples(self, real_sample_dir, real_knowledge_base, monkeypatch):
        app = setup_env(monkeypatch, sample_dir=real_sample_dir, data_home=real_knowledge_base)
        runner = CliRunner()
        result = runner.invoke(app, ["extract"])
        assert result.exit_code == 0
        assert "抽取完成" in result.output
