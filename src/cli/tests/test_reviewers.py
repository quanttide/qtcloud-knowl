"""测试评审工具 — data 层、ui 层、__init__ 视图函数"""

import json
from pathlib import Path

import pytest

from app.reviewers import data, ui, show_overview, view_review_summary


class TestData:
    def test_load_reviews_returns_dict_when_no_file(self, tmp_path, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(tmp_path))
        import importlib
        from app import config
        config.settings.reload_from_env()
        importlib.reload(data)
        reviews = data.load_reviews()
        assert reviews == {}

    def test_save_and_load_reviews(self, tmp_path, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(tmp_path))
        import importlib
        from app import config
        config.settings.reload_from_env()
        importlib.reload(data)
        reviews = {"k1": {"status": "通过", "comment": "ok"}}
        data.save_reviews(reviews)
        assert (tmp_path / ".review.json").exists()
        loaded = data.load_reviews()
        assert loaded == reviews

    def test_get_review_status_default(self, tmp_path, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(tmp_path))
        import importlib
        from app import config
        config.settings.reload_from_env()
        importlib.reload(data)
        s, c = data.get_review_status({}, "nonexistent")
        assert s == "待评审"
        assert c == ""

    def test_get_review_status_existing(self, tmp_path, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(tmp_path))
        import importlib
        from app import config
        config.settings.reload_from_env()
        importlib.reload(data)
        reviews = {"k1": {"status": "通过", "comment": "good"}}
        s, c = data.get_review_status(reviews, "k1")
        assert s == "通过"
        assert c == "good"

    def test_set_review_status(self, tmp_path, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(tmp_path))
        import importlib
        from app import config
        config.settings.reload_from_env()
        importlib.reload(data)
        reviews = {}
        data.set_review_status(reviews, "k1", "需修改", "有问题")
        assert reviews["k1"]["status"] == "需修改"
        assert reviews["k1"]["comment"] == "有问题"
        assert "updated" in reviews["k1"]

    def test_load_domains_empty_dir(self, tmp_path, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(tmp_path))
        import importlib
        from app import config
        config.settings.reload_from_env()
        importlib.reload(data)
        domains = data.load_domains()
        assert domains == []

    def test_load_domains_with_data(self, tmp_path, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(tmp_path))
        import importlib
        from app import config
        config.settings.reload_from_env()
        importlib.reload(data)
        domain_dir = tmp_path / "test-domain"
        domain_dir.mkdir()
        for name, content in [
            ("domain.json", '{"id": "test-domain", "name": "test", "vocabulary": []}'),
            ("ontologies.json", '{"ontologies": [{"id": "o1", "name": "o1"}]}'),
            ("instances.json", '{"instances": []}'),
            ("relations.json", '{"relations": []}'),
        ]:
            (domain_dir / name).write_text(content, encoding="utf-8")
        domains = data.load_domains()
        assert len(domains) == 1
        assert domains[0]["dir"] == "test-domain"


class TestUI:
    def test_t_applies_escape_code(self):
        result = ui.t("32", "hello")
        assert result == "\033[32mhello\033[0m"

    def test_bold(self):
        assert ui.bold("x") == "\033[1mx\033[0m"

    def test_dim(self):
        assert ui.dim("x") == "\033[2mx\033[0m"

    def test_green(self):
        assert ui.green("x") == "\033[32mx\033[0m"

    def test_yellow(self):
        assert ui.yellow("x") == "\033[33mx\033[0m"

    def test_cyan(self):
        assert ui.cyan("x") == "\033[36mx\033[0m"

    def test_red(self):
        assert ui.red("x") == "\033[31mx\033[0m"

    def test_badge_known_statuses(self):
        assert "待评审" in ui.badge("待评审")
        assert "通过" in ui.badge("通过")
        assert "需修改" in ui.badge("需修改")

    def test_badge_fallback(self):
        assert ui.badge("unknown") == "unknown"

    def test_header_prints(self, capsys):
        ui.header("Test Title")
        captured = capsys.readouterr()
        assert "Test Title" in captured.out

    def test_subheader_prints(self, capsys):
        ui.subheader("Sub")
        captured = capsys.readouterr()
        assert "Sub" in captured.out


class TestShowOverview:
    def test_show_overview_with_domains(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(tmp_path))
        import importlib
        from app import config
        config.settings.reload_from_env()
        domains = [
            {
                "dir": "test-domain",
                "info": {"files": ["a.md"]},
                "ontologies": [{"id": "o1"}],
                "instances": [{"id": "i1"}],
                "relations": [{"id": "r1"}],
            }
        ]
        show_overview(domains, {})
        captured = capsys.readouterr()
        assert "test-domain" in captured.out
        assert "知识库评审" in captured.out

    def test_show_overview_shows_review_progress(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(tmp_path))
        import importlib
        from app import config
        config.settings.reload_from_env()
        domains = [
            {
                "dir": "d1",
                "info": {"files": []},
                "ontologies": [{"id": "o1"}],
                "instances": [],
                "relations": [],
            }
        ]
        reviews = {"d1:ontology:o1": {"status": "通过"}}
        show_overview(domains, reviews)
        captured = capsys.readouterr()
        assert "评审进度" in captured.out


class TestViewReviewSummary:
    def test_view_summary_prints_domain(self, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", lambda prompt="": "")
        domains = [
            {
                "dir": "d1",
                "info": {},
                "ontologies": [{"id": "o1", "name": "o1"}],
                "instances": [],
                "relations": [],
            }
        ]
        view_review_summary(domains, {})
        captured = capsys.readouterr()
        assert "d1" in captured.out
