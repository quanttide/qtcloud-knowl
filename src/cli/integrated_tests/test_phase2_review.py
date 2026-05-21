"""
OCL 阶段三测试：认知对齐 — review CLI

验证用户能批量评审知识条目，状态变更后持久化到文件。
"""

from typer.testing import CliRunner


def _setup(monkeypatch, data_home):
    monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(data_home))
    import importlib
    from app import config
    importlib.reload(config)
    import app.reviewers.data as rdata
    import app.review as rmod
    import app.cli as cli_mod
    importlib.reload(rdata)
    importlib.reload(rmod)
    importlib.reload(cli_mod)
    return cli_mod.app


class TestReviewList:
    def test_list_shows_items(self, real_knowledge_base, monkeypatch):
        app = _setup(monkeypatch, real_knowledge_base)
        runner = CliRunner()
        result = runner.invoke(app, ["review", "list"])
        assert result.exit_code == 0
        assert "org-gov" in result.output
        assert "biz-ops" in result.output

    def test_list_pending_only(self, real_knowledge_base, monkeypatch):
        app = _setup(monkeypatch, real_knowledge_base)
        runner = CliRunner()
        result = runner.invoke(app, ["review", "list", "--pending"])
        assert result.exit_code == 0
        assert "待评审" in result.output

    def test_list_empty_dir(self, tmp_path, monkeypatch):
        app = _setup(monkeypatch, tmp_path)
        runner = CliRunner()
        result = runner.invoke(app, ["review", "list"])
        assert "没有符合条件的条目" in result.output


class TestReviewApprove:
    def test_approve_all(self, real_knowledge_base, monkeypatch):
        app = _setup(monkeypatch, real_knowledge_base)
        runner = CliRunner()
        result = runner.invoke(app, ["review", "approve"])
        assert result.exit_code == 0
        assert "已全部通过" in result.output

    def test_approve_one_shows_fewer_pending(self, real_knowledge_base, monkeypatch):
        app = _setup(monkeypatch, real_knowledge_base)
        runner = CliRunner()
        runner.invoke(app, ["review", "approve", "--id", "org-gov:ontology:authority-responsibility"])
        result = runner.invoke(app, ["review", "list", "--pending"])
        assert "authority-responsibility" not in result.output


class TestReviewReject:
    def test_reject_with_reason(self, real_knowledge_base, monkeypatch):
        app = _setup(monkeypatch, real_knowledge_base)
        runner = CliRunner()
        result = runner.invoke(app, ["review", "reject", "--id", "org-gov:ontology:authority-responsibility", "--reason", "需要精修"])
        assert result.exit_code == 0
        assert "已拒绝" in result.output

    def test_reject_without_id_errors(self, real_knowledge_base, monkeypatch):
        app = _setup(monkeypatch, real_knowledge_base)
        runner = CliRunner()
        result = runner.invoke(app, ["review", "reject"])
        assert result.exit_code == 1


class TestReviewReset:
    def test_reset_clears(self, real_knowledge_base, monkeypatch):
        app = _setup(monkeypatch, real_knowledge_base)
        runner = CliRunner()
        runner.invoke(app, ["review", "approve"])
        result = runner.invoke(app, ["review", "reset"])
        assert "已重置" in result.output
