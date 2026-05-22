"""测试评审工具 — data 层、ui 层、review 函数、主菜单"""
import importlib
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from app.reviewers import data, ui, show_overview, view_review_summary


class TestData:
    def test_load_reviews_returns_dict_when_no_file(self, tmp_path, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(tmp_path))
        import importlib
        from app import config
        importlib.reload(config)
        importlib.reload(data)
        reviews = data.load_reviews()
        assert reviews == {}

    def test_save_and_load_reviews(self, tmp_path, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(tmp_path))
        import importlib
        from app import config
        importlib.reload(config)
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
        importlib.reload(config)
        importlib.reload(data)
        s, c = data.get_review_status({}, "nonexistent")
        assert s == "待评审"
        assert c == ""

    def test_get_review_status_existing(self, tmp_path, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(tmp_path))
        import importlib
        from app import config
        importlib.reload(config)
        importlib.reload(data)
        reviews = {"k1": {"status": "通过", "comment": "good"}}
        s, c = data.get_review_status(reviews, "k1")
        assert s == "通过"
        assert c == "good"

    def test_set_review_status(self, tmp_path, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(tmp_path))
        import importlib
        from app import config
        importlib.reload(config)
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
        importlib.reload(config)
        importlib.reload(data)
        domains = data.load_domains()
        assert domains == []

    def test_load_domains_with_data(self, tmp_path, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(tmp_path))
        import importlib
        from app import config
        importlib.reload(config)
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
        importlib.reload(config)
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
        importlib.reload(config)
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

    def test_view_summary_with_instances_and_relations(self, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", lambda prompt="": "")
        domains = [
            {
                "dir": "d1",
                "info": {},
                "ontologies": [],
                "instances": [{"id": "i1", "subject": "测试实例", "ontology": "o1"}],
                "relations": [{"id": "r1", "relation": "depends", "source_ontology": "o1", "target_ontology": "o2"}],
            }
        ]
        view_review_summary(domains, {})
        captured = capsys.readouterr()
        assert "测试实例" in captured.out or "d1" in captured.out


class TestDataFlatten:
    def test_flatten_removes_data_key(self):
        d = {"id": "i1", "data": {"principle": "test"}, "extra": "val"}
        result = data._flatten(d)
        assert "data" not in result
        assert result["principle"] == "test"
        assert result["extra"] == "val"


class TestUIAdditional:
    def test_confirm_yes(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "y")
        assert ui.confirm("确认?") is True

    def test_confirm_no(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "n")
        assert ui.confirm("确认?") is False

    def test_ask_comment_returns_input(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "好")
        assert ui.ask_comment() == "好"

    def test_ask_comment_empty(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt="": "")
        assert ui.ask_comment() == ""


class TestRunDetection:
    def test_run_detection_nonzero_result(self, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", lambda prompt="": "")
        import app.config
        monkeypatch.setattr(app.config.settings, "data_home", Path("/nonexistent_path_12345"))
        from app.reviewers import run_detection
        run_detection("app.validators.validate", "测试退出码")
        captured = capsys.readouterr()
        assert "退出码" in captured.out

    def test_run_detection_success(self, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", lambda prompt="": "")
        from app.reviewers import run_detection
        run_detection("app.reporters.summary", "测试")
        captured = capsys.readouterr()
        assert "测试" in captured.out

    def test_run_detection_error(self, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", lambda prompt="": "")
        from app.reviewers import run_detection
        run_detection("nonexistent.module", "错误")
        captured = capsys.readouterr()
        assert "错误" in captured.out


class TestSelectDomain:
    def _make_domain(self):
        return {
            "dir": "test",
            "info": {},
            "ontologies": [{"id": "o1"}],
            "instances": [],
            "relations": [],
        }

    def test_select_domain_zero_returns(self, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", lambda prompt="": "0")
        from app.reviewers import select_domain
        select_domain([self._make_domain()], "本体", lambda d: None)
        captured = capsys.readouterr()
        assert "选择领域" in captured.out

    def test_select_domain_valid_choice(self, monkeypatch, capsys):
        inputs = iter(["1", "q"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
        from app.reviewers import select_domain
        reviewed = []

        def fake_review(d):
            reviewed.append(d)

        select_domain([self._make_domain()], "本体", fake_review)
        assert len(reviewed) == 1


class TestReviewFunctions:
    def _setup_env(self, monkeypatch, tmp_path):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(tmp_path))
        import app.config
        importlib.reload(app.config)
        import app.reviewers.data
        importlib.reload(app.reviewers.data)
        domain_dir = tmp_path / "test-domain"
        domain_dir.mkdir()
        for name, content in [
            ("domain.json", json.dumps({"id": "test-domain", "name": "测试", "vocabulary": []})),
            ("ontologies.json", json.dumps({"ontologies": [{"id": "o1", "name": "onto1", "label": "本体1", "perspective": "测试", "description": "描述", "pattern": "模式"}]})),
            ("instances.json", json.dumps({"instances": [{"id": "i1", "subject": "实例1", "ontology": "o1", "source": "doc.md", "article": "第1条"}]})),
            ("relations.json", json.dumps({"relations": [{"id": "r1", "source_ontology": "o1", "target_ontology": "o2", "relation": "depends", "description": "依赖"}]})),
        ]:
            (domain_dir / name).write_text(content, encoding="utf-8")

    def _make_domain(self, tmp_path):
        return {
            "dir": "test-domain",
            "info": {"id": "test-domain", "name": "测试"},
            "ontologies": [{"id": "o1", "name": "onto1", "label": "本体1", "perspective": "测试", "pattern": "模式"}],
            "instances": [{"id": "i1", "subject": "实例1", "ontology": "o1", "source": "doc.md", "article": "第1条", "authority": "审批", "description": "说明"}],
            "relations": [{"id": "r1", "source_ontology": "o1", "target_ontology": "o2", "relation": "depends", "description": "依赖", "detail": "详情"}],
        }

    # ontology_review
    def test_ontology_review_approve(self, monkeypatch, tmp_path):
        self._setup_env(monkeypatch, tmp_path)
        monkeypatch.setattr("builtins.input", lambda prompt="": "a")
        from app.reviewers.ontology_review import run
        run(self._make_domain(tmp_path))
        reviews = importlib.import_module("app.reviewers.data").load_reviews()
        assert "test-domain:ontology:o1" in reviews

    def test_ontology_review_quit(self, monkeypatch, tmp_path):
        self._setup_env(monkeypatch, tmp_path)
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")
        from app.reviewers.ontology_review import run
        run(self._make_domain(tmp_path))

    def test_ontology_review_skip(self, monkeypatch, tmp_path):
        self._setup_env(monkeypatch, tmp_path)
        monkeypatch.setattr("builtins.input", lambda prompt="": "p")
        from app.reviewers.ontology_review import run
        run(self._make_domain(tmp_path))

    def test_ontology_review_already_reviewed(self, monkeypatch, tmp_path):
        self._setup_env(monkeypatch, tmp_path)
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")
        from app.reviewers.ontology_review import run
        run(self._make_domain(tmp_path))

    # instance_review
    def test_instance_review_approve(self, monkeypatch, tmp_path):
        self._setup_env(monkeypatch, tmp_path)
        monkeypatch.setattr("builtins.input", lambda prompt="": "a")
        from app.reviewers.instance_review import run
        run(self._make_domain(tmp_path))

    def test_instance_review_needs_change(self, monkeypatch, tmp_path):
        self._setup_env(monkeypatch, tmp_path)
        inputs = iter(["s", "请修改"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
        from app.reviewers.instance_review import run
        run(self._make_domain(tmp_path))
        reviews = importlib.import_module("app.reviewers.data").load_reviews()
        assert "test-domain:instance:i1" in reviews

    def test_instance_review_quit(self, monkeypatch, tmp_path):
        self._setup_env(monkeypatch, tmp_path)
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")
        from app.reviewers.instance_review import run
        run(self._make_domain(tmp_path))

    def test_instance_review_with_list_val(self, monkeypatch, tmp_path, capsys):
        self._setup_env(monkeypatch, tmp_path)
        monkeypatch.setattr("builtins.input", lambda prompt="": "a")
        domain = self._make_domain(tmp_path)
        del domain["instances"][0]["authority"]
        domain["instances"][0]["stages"] = ["阶段1", "阶段2"]
        domain["instances"][0]["levels"] = [{"level": "L1", "title": "初级"}]
        domain["instances"][0]["risks"] = ["风险1"]
        from app.reviewers.instance_review import run
        run(domain)
        captured = capsys.readouterr()
        assert "阶段1" in captured.out

    def test_instance_review_dict_in_list(self, monkeypatch, tmp_path, capsys):
        self._setup_env(monkeypatch, tmp_path)
        monkeypatch.setattr("builtins.input", lambda prompt="": "a")
        domain = self._make_domain(tmp_path)
        del domain["instances"][0]["authority"]
        del domain["instances"][0]["description"]
        domain["instances"][0]["stages"] = [{"stage": "S1", "name": "阶段一"}]
        from app.reviewers.instance_review import run
        run(domain)
        captured = capsys.readouterr()
        assert "stage" in captured.out

    def test_instance_review_other_fields(self, monkeypatch, tmp_path):
        self._setup_env(monkeypatch, tmp_path)
        monkeypatch.setattr("builtins.input", lambda prompt="": "a")
        domain = self._make_domain(tmp_path)
        domain["instances"][0]["custom_field"] = "custom_val"
        from app.reviewers.instance_review import run
        run(domain)

    # relation_review
    def test_relation_review_approve(self, monkeypatch, tmp_path):
        self._setup_env(monkeypatch, tmp_path)
        monkeypatch.setattr("builtins.input", lambda prompt="": "a")
        from app.reviewers.relation_review import run
        run(self._make_domain(tmp_path))

    def test_relation_review_needs_change(self, monkeypatch, tmp_path):
        self._setup_env(monkeypatch, tmp_path)
        inputs = iter(["s", "有问题"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
        from app.reviewers.relation_review import run
        run(self._make_domain(tmp_path))
        reviews = importlib.import_module("app.reviewers.data").load_reviews()
        assert "test-domain:relation:r1" in reviews

    def test_relation_review_quit(self, monkeypatch, tmp_path):
        self._setup_env(monkeypatch, tmp_path)
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")
        from app.reviewers.relation_review import run
        run(self._make_domain(tmp_path))

    def test_ontology_review_source_files(self, monkeypatch, tmp_path, capsys):
        self._setup_env(monkeypatch, tmp_path)
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")
        domain = self._make_domain(tmp_path)
        domain["ontologies"][0]["source_files"] = ["file1.md", "file2.md"]
        from app.reviewers.ontology_review import run
        run(domain)
        captured = capsys.readouterr()
        assert "来源文件" in captured.out

    def test_ontology_review_needs_change(self, monkeypatch, tmp_path):
        self._setup_env(monkeypatch, tmp_path)
        inputs = iter(["s", "有问题"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
        from app.reviewers.ontology_review import run
        run(self._make_domain(tmp_path))

    def test_ontology_review_already_reviewed(self, monkeypatch, tmp_path):
        self._setup_env(monkeypatch, tmp_path)
        from app.reviewers.data import save_reviews, load_reviews
        reviews = load_reviews()
        reviews["test-domain:ontology:o1"] = {"status": "通过", "comment": ""}
        save_reviews(reviews)
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")
        from app.reviewers.ontology_review import run
        run(self._make_domain(tmp_path))

    def test_instance_review_already_reviewed(self, monkeypatch, tmp_path):
        self._setup_env(monkeypatch, tmp_path)
        from app.reviewers.data import save_reviews, load_reviews
        reviews = load_reviews()
        reviews["test-domain:instance:i1"] = {"status": "通过", "comment": ""}
        save_reviews(reviews)
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")
        from app.reviewers.instance_review import run
        run(self._make_domain(tmp_path))

    def test_instance_review_other_list(self, monkeypatch, tmp_path):
        self._setup_env(monkeypatch, tmp_path)
        monkeypatch.setattr("builtins.input", lambda prompt="": "a")
        domain = self._make_domain(tmp_path)
        domain["instances"][0]["tags"] = ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6"]
        from app.reviewers.instance_review import run
        run(domain)

    def test_instance_review_other_dict(self, monkeypatch, tmp_path):
        self._setup_env(monkeypatch, tmp_path)
        monkeypatch.setattr("builtins.input", lambda prompt="": "a")
        domain = self._make_domain(tmp_path)
        domain["instances"][0]["meta"] = {"version": 1, "author": "test"}
        from app.reviewers.instance_review import run
        run(domain)

    def test_relation_review_already_reviewed(self, monkeypatch, tmp_path):
        self._setup_env(monkeypatch, tmp_path)
        from app.reviewers.data import save_reviews, load_reviews
        reviews = load_reviews()
        reviews["test-domain:relation:r1"] = {"status": "通过", "comment": ""}
        save_reviews(reviews)
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")
        from app.reviewers.relation_review import run
        run(self._make_domain(tmp_path))

    def test_relation_review_with_detail(self, monkeypatch, tmp_path):
        self._setup_env(monkeypatch, tmp_path)
        monkeypatch.setattr("builtins.input", lambda prompt="": "q")
        from app.reviewers.relation_review import run
        run(self._make_domain(tmp_path))


class TestMainMenu:
    def test_main_empty_domains(self, monkeypatch, capsys):
        import app.config
        monkeypatch.setattr(app.config.settings, "data_home", Path("/nonexistent"))
        import app.reviewers.data
        importlib.reload(app.reviewers.data)
        from app.reviewers import main
        main()
        captured = capsys.readouterr()
        assert "未找到领域数据" in captured.out

    def test_main_menu_exit(self, monkeypatch, tmp_path):
        monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(tmp_path))
        domain_dir = tmp_path / "test-domain"
        domain_dir.mkdir()
        for name, content in [
            ("domain.json", json.dumps({"id": "test-domain", "name": "测试"})),
            ("ontologies.json", json.dumps({"ontologies": [{"id": "o1", "name": "o1"}]})),
            ("instances.json", json.dumps({"instances": []})),
            ("relations.json", json.dumps({"relations": []})),
        ]:
            (domain_dir / name).write_text(content, encoding="utf-8")
        import app.config
        importlib.reload(app.config)
        import app.reviewers.data
        importlib.reload(app.reviewers.data)
        monkeypatch.setattr("builtins.input", lambda prompt="": "0")
        import app.reviewers
        importlib.reload(app.reviewers)
        from app.reviewers import main
        main()

    def test_main_menu_run_find_undefined(self, monkeypatch, tmp_path, capsys):
        import app.config
        monkeypatch.setattr(app.config.settings, "data_home", tmp_path)
        domain_dir = tmp_path / "d1"
        domain_dir.mkdir()
        for name, content in [
            ("domain.json", json.dumps({"id": "d1", "name": "d1"})),
            ("ontologies.json", json.dumps({"ontologies": []})),
            ("instances.json", json.dumps({"instances": []})),
            ("relations.json", json.dumps({"relations": []})),
        ]:
            (domain_dir / name).write_text(content, encoding="utf-8")
        import app.reviewers.data
        importlib.reload(app.reviewers.data)
        inputs = iter(["7", "", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
        import app.reviewers
        importlib.reload(app.reviewers)
        from app.reviewers import main
        main()

    def test_main_menu_reset_reviews_no_file(self, monkeypatch, tmp_path, capsys):
        import app.config
        monkeypatch.setattr(app.config.settings, "data_home", tmp_path)
        domain_dir = tmp_path / "d1"
        domain_dir.mkdir()
        for name, content in [
            ("domain.json", json.dumps({"id": "d1", "name": "d1"})),
            ("ontologies.json", json.dumps({"ontologies": []})),
            ("instances.json", json.dumps({"instances": []})),
            ("relations.json", json.dumps({"relations": []})),
        ]:
            (domain_dir / name).write_text(content, encoding="utf-8")
        import app.reviewers.data
        importlib.reload(app.reviewers.data)
        inputs = iter(["5", "y", "", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
        import app.reviewers
        importlib.reload(app.reviewers)
        from app.reviewers import main
        main()

    def test_main_menu_reset_reviews(self, monkeypatch, tmp_path, capsys):
        import app.config
        monkeypatch.setattr(app.config.settings, "data_home", tmp_path)
        domain_dir = tmp_path / "d1"
        domain_dir.mkdir()
        for name, content in [
            ("domain.json", json.dumps({"id": "d1", "name": "d1"})),
            ("ontologies.json", json.dumps({"ontologies": []})),
            ("instances.json", json.dumps({"instances": []})),
            ("relations.json", json.dumps({"relations": []})),
        ]:
            (domain_dir / name).write_text(content, encoding="utf-8")
        import app.reviewers.data
        importlib.reload(app.reviewers.data)
        app.reviewers.data.save_reviews({"d1:ontology:o1": {"status": "通过"}})
        inputs = iter(["5", "y", "", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
        import app.reviewers
        importlib.reload(app.reviewers)
        from app.reviewers import main
        main()

    def test_main_menu_ontology_review(self, monkeypatch, tmp_path, capsys):
        import app.config
        monkeypatch.setattr(app.config.settings, "data_home", tmp_path)
        domain_dir = tmp_path / "d1"
        domain_dir.mkdir()
        for name, content in [
            ("domain.json", json.dumps({"id": "d1", "name": "d1"})),
            ("ontologies.json", json.dumps({"ontologies": [{"id": "o1", "name": "o1"}]})),
            ("instances.json", json.dumps({"instances": []})),
            ("relations.json", json.dumps({"relations": []})),
        ]:
            (domain_dir / name).write_text(content, encoding="utf-8")
        import app.reviewers.data
        importlib.reload(app.reviewers.data)
        inputs = iter(["1", "1", "q", "", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
        import app.reviewers
        importlib.reload(app.reviewers)
        from app.reviewers import main
        main()

    def test_main_menu_instance_review(self, monkeypatch, tmp_path, capsys):
        import app.config
        monkeypatch.setattr(app.config.settings, "data_home", tmp_path)
        domain_dir = tmp_path / "d1"
        domain_dir.mkdir()
        for name, content in [
            ("domain.json", json.dumps({"id": "d1", "name": "d1"})),
            ("ontologies.json", json.dumps({"ontologies": [{"id": "o1", "name": "o1"}]})),
            ("instances.json", json.dumps({"instances": [{"id": "i1", "subject": "实例", "ontology": "o1"}]})),
            ("relations.json", json.dumps({"relations": []})),
        ]:
            (domain_dir / name).write_text(content, encoding="utf-8")
        import app.reviewers.data
        importlib.reload(app.reviewers.data)
        inputs = iter(["2", "1", "q", "", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
        import app.reviewers
        importlib.reload(app.reviewers)
        from app.reviewers import main
        main()

    def test_main_menu_relation_review(self, monkeypatch, tmp_path, capsys):
        import app.config
        monkeypatch.setattr(app.config.settings, "data_home", tmp_path)
        domain_dir = tmp_path / "d1"
        domain_dir.mkdir()
        for name, content in [
            ("domain.json", json.dumps({"id": "d1", "name": "d1"})),
            ("ontologies.json", json.dumps({"ontologies": []})),
            ("instances.json", json.dumps({"instances": []})),
            ("relations.json", json.dumps({"relations": [{"id": "r1", "source_ontology": "o1", "target_ontology": "o2", "relation": "depends"}]})),
        ]:
            (domain_dir / name).write_text(content, encoding="utf-8")
        import app.reviewers.data
        importlib.reload(app.reviewers.data)
        inputs = iter(["3", "1", "q", "", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
        import app.reviewers
        importlib.reload(app.reviewers)
        from app.reviewers import main
        main()

    def test_main_menu_view_summary(self, monkeypatch, tmp_path, capsys):
        import app.config
        monkeypatch.setattr(app.config.settings, "data_home", tmp_path)
        domain_dir = tmp_path / "d1"
        domain_dir.mkdir()
        for name, content in [
            ("domain.json", json.dumps({"id": "d1", "name": "d1"})),
            ("ontologies.json", json.dumps({"ontologies": [{"id": "o1", "name": "o1"}]})),
            ("instances.json", json.dumps({"instances": []})),
            ("relations.json", json.dumps({"relations": []})),
        ]:
            (domain_dir / name).write_text(content, encoding="utf-8")
        import app.reviewers.data
        importlib.reload(app.reviewers.data)
        inputs = iter(["4", "", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
        import app.reviewers
        importlib.reload(app.reviewers)
        from app.reviewers import main
        main()

    def test_main_menu_run_fusion_check(self, monkeypatch, tmp_path, capsys):
        import app.config
        monkeypatch.setattr(app.config.settings, "data_home", tmp_path)
        domain_dir = tmp_path / "d1"
        domain_dir.mkdir()
        for name, content in [
            ("domain.json", json.dumps({"id": "d1", "name": "d1"})),
            ("ontologies.json", json.dumps({"ontologies": []})),
            ("instances.json", json.dumps({"instances": []})),
            ("relations.json", json.dumps({"relations": []})),
        ]:
            (domain_dir / name).write_text(content, encoding="utf-8")
        import app.reviewers.data
        importlib.reload(app.reviewers.data)
        inputs = iter(["6", "", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
        import app.reviewers
        importlib.reload(app.reviewers)
        from app.reviewers import main
        main()
