"""
OCL 阶段三测试：认知对齐 — review CLI
"""

from typer.testing import CliRunner
from conftest import setup_env


class TestReviewList:
    def test_list_shows_items(self, real_knowledge_base, monkeypatch):
        app = setup_env(monkeypatch, data_home=real_knowledge_base)
        runner = CliRunner()
        result = runner.invoke(app, ["review", "list"])
        assert result.exit_code == 0
        assert "org-gov" in result.output
        assert "biz-ops" in result.output

    def test_list_pending_only(self, real_knowledge_base, monkeypatch):
        app = setup_env(monkeypatch, data_home=real_knowledge_base)
        runner = CliRunner()
        result = runner.invoke(app, ["review", "list", "--pending"])
        assert result.exit_code == 0
        assert "待评审" in result.output

    def test_list_empty_dir(self, tmp_path, monkeypatch):
        app = setup_env(monkeypatch, data_home=tmp_path)
        runner = CliRunner()
        result = runner.invoke(app, ["review", "list"])
        assert "没有符合条件的条目" in result.output


class TestReviewApprove:
    def test_approve_all(self, real_knowledge_base, monkeypatch):
        app = setup_env(monkeypatch, data_home=real_knowledge_base)
        runner = CliRunner()
        result = runner.invoke(app, ["review", "approve"])
        assert result.exit_code == 0
        assert "已全部通过" in result.output

    def test_approve_one_shows_fewer_pending(self, real_knowledge_base, monkeypatch):
        app = setup_env(monkeypatch, data_home=real_knowledge_base)
        runner = CliRunner()
        runner.invoke(app, ["review", "approve", "--id", "org-gov:ontology:authority-responsibility"])
        result = runner.invoke(app, ["review", "list", "--pending"])
        assert "authority-responsibility" not in result.output


class TestReviewReject:
    def test_reject_with_reason(self, real_knowledge_base, monkeypatch):
        app = setup_env(monkeypatch, data_home=real_knowledge_base)
        runner = CliRunner()
        result = runner.invoke(app, ["review", "reject", "--id", "org-gov:ontology:authority-responsibility", "--reason", "需要精修"])
        assert result.exit_code == 0
        assert "已拒绝" in result.output

    def test_reject_without_id_errors(self, real_knowledge_base, monkeypatch):
        app = setup_env(monkeypatch, data_home=real_knowledge_base)
        runner = CliRunner()
        result = runner.invoke(app, ["review", "reject"])
        assert result.exit_code == 1


class TestReviewReset:
    def test_reset_clears(self, real_knowledge_base, monkeypatch):
        app = setup_env(monkeypatch, data_home=real_knowledge_base)
        runner = CliRunner()
        runner.invoke(app, ["review", "approve"])
        result = runner.invoke(app, ["review", "reset"])
        assert "已重置" in result.output
