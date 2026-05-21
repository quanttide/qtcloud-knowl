"""全链路集成测试 — 跨模块协作 + 文件状态持久化。单模块行为由单元测试覆盖。"""

from typer.testing import CliRunner
from conftest import setup_env


class TestMain:
    def test_skeleton_then_audit(self, real_sample_dir, real_knowledge_base, monkeypatch):
        app = setup_env(monkeypatch, sample_dir=real_sample_dir, data_home=real_knowledge_base)
        runner = CliRunner()
        assert (real_knowledge_base / "org-gov" / "domain.json").exists()
        result = runner.invoke(app, ["audit"])
        assert result.exit_code == 0
        assert "审计" in result.output

    def test_audit_incremental_diff(self, tmp_path, real_sample_dir, real_knowledge_base, monkeypatch):
        state_dir = tmp_path / "audit-state"
        state_dir.mkdir(exist_ok=True)
        app = setup_env(monkeypatch, sample_dir=real_sample_dir, data_home=real_knowledge_base, state_home=state_dir)
        runner = CliRunner()
        runner.invoke(app, ["audit"])
        result = runner.invoke(app, ["audit"])
        assert "相比上次审计" in result.output

    def test_review_reduces_audit_issues(self, tmp_path, real_sample_dir, real_knowledge_base, monkeypatch):
        state_dir = tmp_path / "audit-state"
        state_dir.mkdir(exist_ok=True)
        app = setup_env(monkeypatch, sample_dir=real_sample_dir, data_home=real_knowledge_base, state_home=state_dir)
        runner = CliRunner()
        result_first = runner.invoke(app, ["audit"])
        assert "需要你确认" in result_first.output
        result_approve = runner.invoke(app, ["review", "approve"])
        assert result_approve.exit_code == 0
        assert "已全部通过" in result_approve.output
        result_second = runner.invoke(app, ["audit"])
        assert "相比上次审计" in result_second.output

    def test_full_pipeline_no_llm_key(self, real_sample_dir, real_knowledge_base, monkeypatch):
        app = setup_env(monkeypatch, sample_dir=real_sample_dir, data_home=real_knowledge_base, api_key="")
        runner = CliRunner()
        result_extract = runner.invoke(app, ["extract"])
        assert result_extract.exit_code == 0
        result_audit = runner.invoke(app, ["audit", "--mode", "simple"])
        assert result_audit.exit_code == 0
