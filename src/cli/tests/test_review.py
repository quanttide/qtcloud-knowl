"""测试 review CLI — list / approve / reject / reset"""

import importlib
import json
from pathlib import Path

import pytest

from app.review import list_items, approve_item, reject_item, reset_reviews
from app.reviewers.data import load_domains, load_reviews, save_reviews


def _invoke(monkeypatch, capsys, *args):
    import sys
    monkeypatch.setattr(sys, "argv", ["qtcloud-knowl", *args])
    from app.cli import main
    try:
        code = main() or 0
    except SystemExit as e:
        code = e.code or 0
    return code, capsys.readouterr().out


@pytest.fixture
def review_env(tmp_path, monkeypatch):
    """设置含一个领域、一个本体、一个实例、一个关系的测试环境。"""
    monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(tmp_path))
    import importlib
    from app import config
    config.settings.reload_from_env()

    domain_dir = tmp_path / "test-domain"
    domain_dir.mkdir()

    (domain_dir / "domain.json").write_text(
        json.dumps({"id": "test-domain", "name": "测试领域", "vocabulary": []}, ensure_ascii=False),
        encoding="utf-8",
    )
    (domain_dir / "ontologies.json").write_text(
        json.dumps({"ontologies": [{"id": "o1", "name": "onto1", "label": "本体1"}]}, ensure_ascii=False),
        encoding="utf-8",
    )
    (domain_dir / "instances.json").write_text(
        json.dumps({"instances": [{"id": "i1", "subject": "实例1", "ontology": "o1", "source": "doc.md", "article": "第1条"}]}, ensure_ascii=False),
        encoding="utf-8",
    )
    (domain_dir / "relations.json").write_text(
        json.dumps({"relations": [{"id": "r1", "source_ontology": "o1", "target_ontology": "o2", "relation": "depends", "description": "依赖"}]}, ensure_ascii=False),
        encoding="utf-8",
    )

    import app.reviewers.data as rdata
    import app.review as rmod
    importlib.reload(rdata)
    importlib.reload(rmod)


class TestListItems:
    def test_list_all(self, review_env):
        items = list_items()
        assert len(items) == 3

    def test_list_types(self, review_env):
        items = list_items()
        types = {i["type"] for i in items}
        assert types == {"ontology", "instance", "relation"}

    def test_list_pending_only(self, review_env):
        items = list_items(pending_only=True)
        assert len(items) == 3

        save_reviews({"test-domain:ontology:o1": {"status": "通过", "comment": ""}})
        import app.review as rmod
        importlib.reload(rmod)
        items = rmod.list_items(pending_only=True)
        assert len(items) == 2

    def test_list_domain_filter(self, review_env):
        items = list_items(domain_filter="nonexistent")
        assert items == []

    def test_list_empty_dir(self, tmp_path, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(tmp_path))
        from app import config
        config.settings.reload_from_env()
        import app.reviewers.data as rdata
        import app.review as rmod
        importlib.reload(rdata)
        importlib.reload(rmod)
        items = rmod.list_items()
        assert items == []


class TestApproveItem:
    def test_approve_single(self, review_env):
        approve_item("test-domain:ontology:o1")
        reviews = load_reviews()
        assert reviews["test-domain:ontology:o1"]["status"] == "通过"

    def test_approve_all(self, review_env):
        from app.review import approve_all
        n = approve_all()
        assert n == 3
        import app.review as rmod
        importlib.reload(rmod)
        items = rmod.list_items(pending_only=True)
        assert len(items) == 0

    def test_approve_changes_status(self, review_env):
        items = list_items(pending_only=True)
        assert len(items) == 3
        approve_item("test-domain:ontology:o1")
        import app.review as rmod
        importlib.reload(rmod)
        items = rmod.list_items(pending_only=True)
        assert len(items) == 2


class TestRejectItem:
    def test_reject_with_reason(self, review_env):
        reject_item("test-domain:ontology:o1", "需要修改")
        reviews = load_reviews()
        assert reviews["test-domain:ontology:o1"]["status"] == "需修改"
        assert reviews["test-domain:ontology:o1"]["comment"] == "需要修改"


class TestResetReviews:
    def test_reset_clears_reviews(self, review_env):
        save_reviews({"k1": {"status": "通过"}})
        assert load_reviews() != {}
        reset_reviews()
        assert load_reviews() == {}


class TestCliCommands:
    def test_list_via_cli(self, review_env, monkeypatch, capsys):
        code, out = _invoke(monkeypatch, capsys, "review", "list")
        assert code == 0
        assert "测试领域" in out or "本体" in out

    def test_approve_via_cli(self, review_env, monkeypatch, capsys):
        code, out = _invoke(monkeypatch, capsys, "review", "approve", "--id", "test-domain:ontology:o1")
        assert code == 0
        assert "已通过" in out

    def test_approve_all_via_cli(self, review_env, monkeypatch, capsys):
        code, out = _invoke(monkeypatch, capsys, "review", "approve")
        assert code == 0
        assert "已全部通过" in out

    def test_list_shows_count(self, review_env, monkeypatch, capsys):
        code, out = _invoke(monkeypatch, capsys, "review", "list")
        assert "待评审" in out

    def test_reject_via_cli(self, review_env, monkeypatch, capsys):
        code, out = _invoke(monkeypatch, capsys, "review", "reject", "--id", "test-domain:ontology:o1", "--reason", "不完整")
        assert code == 0
        assert "已拒绝" in out

    def test_reject_without_id_errors(self, review_env, monkeypatch, capsys):
        code, out = _invoke(monkeypatch, capsys, "review", "reject")
        assert code == 1

    def test_reset_via_cli(self, review_env, monkeypatch, capsys):
        code, out = _invoke(monkeypatch, capsys, "review", "reset")
        assert code == 0
        assert "已重置" in out

    def test_list_pending_via_cli(self, review_env, monkeypatch, capsys):
        code, out = _invoke(monkeypatch, capsys, "review", "list", "--pending")
        assert code == 0
