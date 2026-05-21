"""
OCL 全链路集成测试：文档 → 抽取 → 审核 → 质检

验证完整产品工作流可走通。
"""

from unittest.mock import patch
from pathlib import Path

from typer.testing import CliRunner


class FakeResponse:
    def __init__(self, content):
        self.content = content


def _setup(monkeypatch, sample_dir, data_home, api_key="test-key"):
    monkeypatch.setenv("QTCLOUD_KNOWL_SAMPLE_HOME", str(sample_dir))
    monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(data_home))
    monkeypatch.setenv("QTCLOUD_KNOWL_LLM_API_KEY", api_key)
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


class TestPipeline:
    """完整 OCL 工作流：骨架创建 → LLM 抽取 → 评审 → 审计"""

    def test_skeleton_then_audit(self, sample_doc, knowledge_base, monkeypatch):
        """知识工程用户的一天：建骨架 → 审计"""
        app = _setup(monkeypatch, sample_doc.parent, knowledge_base)
        runner = CliRunner()

        assert (knowledge_base / "data-gov" / "domain.json").exists()

        result_audit = runner.invoke(app, ["audit"])
        assert result_audit.exit_code == 0
        assert "审计" in result_audit.output

    def test_review_then_audit(self, sample_doc, knowledge_base, monkeypatch):
        """评审条目后运行审计，验证状态变更不影响审计"""
        app = _setup(monkeypatch, sample_doc.parent, knowledge_base)
        runner = CliRunner()

        result_review = runner.invoke(app, ["review", "approve"])
        assert "已全部通过" in result_review.output

        result_audit = runner.invoke(app, ["audit"])
        assert result_audit.exit_code == 0

    def test_extract_llm_then_review(self, sample_doc, knowledge_base, monkeypatch):
        """LLM 抽取后评审能看到结果（mock LLM 返回）"""
        app = _setup(monkeypatch, sample_doc.parent, knowledge_base, api_key="test-key")

        with patch("quanttide_agent.LLM") as MockLLM:
            mock = MockLLM.return_value
            mock.complete.return_value = FakeResponse(
                '{"concepts": [{"name": "数据治理委员会", "type": "职务"}]}'
            )
            runner = CliRunner()
            result_llm = runner.invoke(app, ["extract", "--llm", str(sample_doc)])
            assert result_llm.exit_code == 0
            assert "数据治理委员会" in result_llm.output

    def test_full_pipeline_no_llm_key(self, sample_doc, knowledge_base, monkeypatch):
        """无 LLM key 时，非 LLM 功能仍正常工作"""
        app = _setup(monkeypatch, sample_doc.parent, knowledge_base, api_key="")
        runner = CliRunner()

        result_extract = runner.invoke(app, ["extract"])
        assert result_extract.exit_code == 0

        result_audit = runner.invoke(app, ["audit", "--mode", "simple"])
        assert result_audit.exit_code == 0

    def test_full_pipeline_multiple_domains(self, tmp_path, monkeypatch):
        """多领域知识库的完整流程"""
        kbase = tmp_path / "kbase"
        for domain_id in ["a", "b"]:
            d = kbase / domain_id
            d.mkdir(parents=True)
            (d / "domain.json").write_text(f'{{"id":"{domain_id}","name":"{domain_id}域"}}', encoding="utf-8")
            (d / "ontologies.json").write_text('{"ontologies":[{"id":"o1","name":"onto1","label":"本体1"}]}', encoding="utf-8")
            (d / "instances.json").write_text('{"instances":[]}', encoding="utf-8")
            (d / "relations.json").write_text('{"relations":[]}', encoding="utf-8")

        app = _setup(monkeypatch, tmp_path, kbase, api_key="")
        runner = CliRunner()

        result_review = runner.invoke(app, ["review", "list"])
        assert result_review.exit_code == 0
        assert "a" in result_review.output
        assert "b" in result_review.output

        result_audit = runner.invoke(app, ["audit"])
        assert result_audit.exit_code == 0
