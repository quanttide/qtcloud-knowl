"""
OCL 全链路集成测试：文档 → 抽取 → 审核 → 质检
"""

from unittest.mock import patch
from pathlib import Path

from typer.testing import CliRunner
from conftest import setup_env


class FakeResponse:
    def __init__(self, content):
        self.content = content


class TestPipeline:
    """完整 OCL 工作流：骨架创建 → LLM 抽取 → 评审 → 审计"""

    def test_skeleton_then_audit(self, real_sample_dir, real_knowledge_base, monkeypatch):
        app = setup_env(monkeypatch, sample_dir=real_sample_dir, data_home=real_knowledge_base)
        runner = CliRunner()

        assert (real_knowledge_base / "org-gov" / "domain.json").exists()

        result_audit = runner.invoke(app, ["audit"])
        assert result_audit.exit_code == 0
        assert "审计" in result_audit.output

    def test_audit_incremental_diff(self, real_sample_dir, real_knowledge_base, monkeypatch):
        state_dir = real_knowledge_base / ".audit-state"
        state_dir.mkdir(exist_ok=True)
        app = setup_env(monkeypatch, sample_dir=real_sample_dir, data_home=real_knowledge_base, state_home=state_dir)
        runner = CliRunner()

        result_first = runner.invoke(app, ["audit"])
        assert result_first.exit_code == 0

        result_second = runner.invoke(app, ["audit"])
        assert result_second.exit_code == 0
        assert "与上次审计一致" in result_second.output

    def test_audit_mode_simple_vs_full(self, real_sample_dir, real_knowledge_base, monkeypatch):
        app = setup_env(monkeypatch, sample_dir=real_sample_dir, data_home=real_knowledge_base)
        runner = CliRunner()

        result_full = runner.invoke(app, ["audit", "--mode", "full"])
        result_simple = runner.invoke(app, ["audit", "--mode", "simple"])

        assert result_full.exit_code == 0
        assert result_simple.exit_code == 0
        assert len(result_full.output) > len(result_simple.output)

    def test_review_reduces_audit_issues(self, real_sample_dir, real_knowledge_base, monkeypatch):
        state_dir = real_knowledge_base / ".audit-state"
        state_dir.mkdir(exist_ok=True)
        app = setup_env(monkeypatch, sample_dir=real_sample_dir, data_home=real_knowledge_base, state_home=state_dir)
        runner = CliRunner()

        result_before = runner.invoke(app, ["audit"])
        assert result_before.exit_code == 0

        runner.invoke(app, ["review", "approve"])

        result_after = runner.invoke(app, ["audit"])
        assert result_after.exit_code == 0
        assert "与上次审计一致" in result_after.output

    def test_review_then_audit(self, real_sample_dir, real_knowledge_base, monkeypatch):
        app = setup_env(monkeypatch, sample_dir=real_sample_dir, data_home=real_knowledge_base)
        runner = CliRunner()

        result_review = runner.invoke(app, ["review", "approve"])
        assert "已全部通过" in result_review.output

        result_audit = runner.invoke(app, ["audit"])
        assert result_audit.exit_code == 0

    def test_extract_llm_then_review(self, real_sample_dir, real_knowledge_base, monkeypatch):
        app = setup_env(monkeypatch, sample_dir=real_sample_dir, data_home=real_knowledge_base, api_key="test-key")

        with patch("quanttide_agent.LLM") as MockLLM:
            mock = MockLLM.return_value
            mock.complete.return_value = FakeResponse(
                '{"concepts": [{"name": "数据治理委员会", "type": "职务"}]}'
            )
            runner = CliRunner()
            result_llm = runner.invoke(app, ["extract", "--llm", str(real_sample_dir / "basic-charter.md")])
            assert result_llm.exit_code == 0
            assert "数据治理委员会" in result_llm.output

    def test_full_pipeline_no_llm_key(self, real_sample_dir, real_knowledge_base, monkeypatch):
        app = setup_env(monkeypatch, sample_dir=real_sample_dir, data_home=real_knowledge_base, api_key="")
        runner = CliRunner()

        result_extract = runner.invoke(app, ["extract"])
        assert result_extract.exit_code == 0

        result_audit = runner.invoke(app, ["audit", "--mode", "simple"])
        assert result_audit.exit_code == 0

    def test_full_pipeline_multiple_domains(self, tmp_path, monkeypatch):
        kbase = tmp_path / "kbase"
        for domain_id in ["a", "b"]:
            d = kbase / domain_id
            d.mkdir(parents=True)
            (d / "domain.json").write_text(f'{{"id":"{domain_id}","name":"{domain_id}域"}}', encoding="utf-8")
            (d / "ontologies.json").write_text('{"ontologies":[{"id":"o1","name":"onto1","label":"本体1"}]}', encoding="utf-8")
            (d / "instances.json").write_text('{"instances":[]}', encoding="utf-8")
            (d / "relations.json").write_text('{"relations":[]}', encoding="utf-8")

        app = setup_env(monkeypatch, data_home=kbase, api_key="")
        runner = CliRunner()

        result_review = runner.invoke(app, ["review", "list"])
        assert result_review.exit_code == 0
        assert "a" in result_review.output
        assert "b" in result_review.output

        result_audit = runner.invoke(app, ["audit"])
        assert result_audit.exit_code == 0
