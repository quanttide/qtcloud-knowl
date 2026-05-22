"""测试全量审计命令"""

import json
from datetime import datetime
from tests.conftest import FIXTURE_DIR, SAMPLE_DIR
from app.audit import _collect_issues, _compute_diff, _load_audit_state, _save_audit_state


class TestAuditState:
    def _setup_state(self, monkeypatch, tmp_path):
        from app import config
        monkeypatch.setattr(config.settings, "state_home", tmp_path)

    def test_collect_issues_flattens_all_categories(self):
        issues = _collect_issues(
            [("g1", [("l1", "a1")])],
            [("g2", [("l2", "a2")])],
            [("g3", [("l3", "a3")])],
        )
        assert len(issues) == 3
        assert issues[0]["category"] == "need_confirm"
        assert issues[1]["category"] == "auto_fixable"
        assert issues[2]["category"] == "suggestions"

    def test_compute_diff_uses_hash(self):
        prev = [{"category": "a", "group": "x", "label": "l1"}, {"category": "a", "group": "x", "label": "l2"}]
        curr = [{"category": "a", "group": "x", "label": "l2"}, {"category": "a", "group": "x", "label": "l3"}]
        fixed, new, pending, _, _ = _compute_diff(prev, curr)
        assert "a|x|l1" in fixed
        assert "a|x|l3" in new
        assert "a|x|l2" in pending

    def test_save_and_load_audit_state(self, monkeypatch, tmp_path):
        self._setup_state(monkeypatch, tmp_path)
        issues = [{"category": "need_confirm", "group": "t", "label": "l"}]
        _save_audit_state(issues, "full")
        state = _load_audit_state()
        assert state is not None
        assert state["mode"] == "full"
        assert len(state["issues"]) == 1

    def test_load_nonexistent_returns_none(self, monkeypatch, tmp_path):
        self._setup_state(monkeypatch, tmp_path)
        assert _load_audit_state() is None

    def test_load_corrupted_returns_none(self, monkeypatch, tmp_path):
        self._setup_state(monkeypatch, tmp_path)
        (tmp_path / "audit.json").write_text("{invalid}", encoding="utf-8")
        assert _load_audit_state() is None


class TestAudit:
    def _setup_state(self, monkeypatch, tmp_path):
        from app import config
        monkeypatch.setattr(config.settings, "state_home", tmp_path)

    def test_audit_with_fixtures(self, monkeypatch, tmp_path, capsys):
        self._setup_state(monkeypatch, tmp_path)
        from app.audit import run
        ret = run(data_dir=str(FIXTURE_DIR))
        captured = capsys.readouterr()
        assert "知识库概览" in captured.out
        assert "检测结果" in captured.out

    def test_audit_empty_dir(self, monkeypatch, tmp_path, capsys):
        self._setup_state(monkeypatch, tmp_path)
        from app.audit import run
        empty = tmp_path / "empty"
        empty.mkdir()
        ret = run(data_dir=str(empty))
        captured = capsys.readouterr()
        assert "领域数量: 0" in captured.out
        assert ret == 0

    def test_audit_with_json_error(self, monkeypatch, tmp_path, capsys):
        self._setup_state(monkeypatch, tmp_path)
        from app.audit import run
        domain_dir = tmp_path / "bad-domain"
        domain_dir.mkdir()
        (domain_dir / "domain.json").write_text("{invalid}", encoding="utf-8")
        (domain_dir / "ontologies.json").write_text("{}", encoding="utf-8")
        (domain_dir / "instances.json").write_text("{}", encoding="utf-8")
        (domain_dir / "relations.json").write_text("{}", encoding="utf-8")
        ret = run(data_dir=str(tmp_path))
        captured = capsys.readouterr()
        assert "JSON 格式错误" in captured.out

    def test_audit_mode_simple_shows_label(self, monkeypatch, tmp_path, capsys):
        self._setup_state(monkeypatch, tmp_path)
        from app.audit import run
        ret = run(data_dir=str(FIXTURE_DIR), mode="simple")
        captured = capsys.readouterr()
        assert "知识库概览" in captured.out
        assert "检测结果" in captured.out

    def test_audit_mode_full_shows_label(self, monkeypatch, tmp_path, capsys):
        self._setup_state(monkeypatch, tmp_path)
        from app.audit import run
        ret = run(data_dir=str(FIXTURE_DIR), mode="full")
        captured = capsys.readouterr()
        assert "知识库概览" in captured.out
        assert "检测结果" in captured.out

    def test_audit_invalid_mode(self, monkeypatch, tmp_path, capsys):
        self._setup_state(monkeypatch, tmp_path)
        from app.audit import run
        ret = run(data_dir=str(FIXTURE_DIR), mode="invalid")
        captured = capsys.readouterr()
        assert "不支持的审计模式" in captured.out
        assert ret == 1

    def test_audit_nonexistent_dir(self, monkeypatch, tmp_path, capsys):
        self._setup_state(monkeypatch, tmp_path)
        from app.audit import run
        ret = run(data_dir="/nonexistent/path")
        captured = capsys.readouterr()
        assert "数据目录不存在" in captured.out
        assert ret == 1

    def test_audit_with_print_diff(self, monkeypatch, tmp_path, capsys):
        self._setup_state(monkeypatch, tmp_path)
        from app.audit import run, _save_audit_state, _collect_issues
        previous_issues = [{"category": "a", "group": "x", "label": "l1"}]
        _save_audit_state(previous_issues, "full")
        ret = run(data_dir=str(FIXTURE_DIR))
        captured = capsys.readouterr()
        assert "相比上次审计" in captured.out

    def test_audit_with_identical_state(self, monkeypatch, tmp_path, capsys):
        self._setup_state(monkeypatch, tmp_path)
        from app.audit import run, _save_audit_state
        from app.knowl_loader import load_all_domains
        _save_audit_state([], "full")
        ret = run(data_dir=str(FIXTURE_DIR))
        captured = capsys.readouterr()
        assert "无新增问题" in captured.out


class TestAuditUnit:
    """Direct unit tests for internal audit functions."""

    def test_parse_miss_with_domain(self):
        from app.audit import _parse_miss
        result = _parse_miss("[MISS] ontologies.json", "org-gov", "/data")
        assert result is not None
        assert "缺少文件" in result[0]
        assert "ontologies.json" in result[0]

    def test_parse_miss_without_domain(self):
        from app.audit import _parse_miss
        result = _parse_miss("[MISS] ontologies.json", None, None)
        assert result is not None
        assert "auto-fix" in result[1]

    def test_parse_miss_no_match(self):
        from app.audit import _parse_miss
        assert _parse_miss("[OK] domain.json", None, None) is None

    def test_parse_fail_with_domain(self):
        from app.audit import _parse_fail
        result = _parse_fail("[FAIL] domain.json - format error", "org-gov", "/data")
        assert result is not None
        assert "JSON 格式错误" in result[0]

    def test_parse_fail_without_domain(self):
        from app.audit import _parse_fail
        result = _parse_fail("[FAIL] domain.json - format error", None, None)
        assert result is not None

    def test_parse_fail_no_match(self):
        from app.audit import _parse_fail
        assert _parse_fail("[OK] domain.json", None, None) is None

    def test_parse_term_matches(self):
        from app.audit import _parse_term
        result = _parse_term("使用了术语 项目经理", None, None)
        assert result is not None
        assert "术语" in result[1]

    def test_parse_term_no_match(self):
        from app.audit import _parse_term
        assert _parse_term("正常文本", None, None) is None

    def test_parse_confirm_matches(self):
        from app.audit import _parse_confirm
        result = _parse_confirm("【需人确认】请检查此引用", None, None)
        assert result is not None
        assert "请检查此引用" in result[0]

    def test_parse_confirm_no_match(self):
        from app.audit import _parse_confirm
        assert _parse_confirm("正常文本", None, None) is None

    def test_parse_abstraction_with_domain(self):
        from app.audit import _parse_abstraction
        result = _parse_abstraction("[检测到] onto1: [具体角色名]", "org-gov", "/data")
        assert result is not None
        assert "onto1" in result[0]

    def test_parse_abstraction_without_domain(self):
        from app.audit import _parse_abstraction
        result = _parse_abstraction("[检测到] onto1: [信号]", None, None)
        assert result is not None

    def test_parse_abstraction_no_match(self):
        from app.audit import _parse_abstraction
        assert _parse_abstraction("[OK] onto1", None, None) is None

    def test_validate_args_nonexistent_dir(self):
        from pathlib import Path
        from app.audit import _validate_args
        assert not _validate_args(Path("/nonexistent"), "full")

    def test_validate_args_invalid_mode(self):
        from pathlib import Path
        from app.audit import _validate_args
        assert not _validate_args(Path("/tmp"), "badmode")


class TestAuditCollectStats:
    _DOMAIN_UUID = "00000000-0000-0000-0000-000000000001"
    _ONTO_UUID = "00000000-0000-0000-0000-000000000010"
    _INST_UUID = "00000000-0000-0000-0000-000000000020"

    def _valid_domain_dir(self, tmp_path, name="test-domain"):
        dd = tmp_path / name
        dd.mkdir()
        (dd / "domain.json").write_text(
            f'{{"id": "{self._DOMAIN_UUID}", "name": "test", "label": "测试", "description": ""}}',
            encoding="utf-8",
        )
        (dd / "ontologies.json").write_text(
            f'{{"ontologies": [{{"id": "{self._ONTO_UUID}", "name": "o1", "label": "本体1", "description": ""}}]}}',
            encoding="utf-8",
        )
        (dd / "instances.json").write_text(
            f'{{"instances": [{{"id": "{self._INST_UUID}", "name": "i1", "label": "实例1", "description": ""}}]}}',
            encoding="utf-8",
        )
        (dd / "relations.json").write_text('{"relations": []}', encoding="utf-8")
        return dd

    def test_collect_stats_with_valid_domain(self, tmp_path):
        self._valid_domain_dir(tmp_path)
        from app.audit import _collect_stats
        domains, ont_count, inst_count = _collect_stats(tmp_path)
        assert len(domains) == 1
        assert ont_count == 1
        assert inst_count == 1

    def test_collect_stats_empty_dir(self, tmp_path):
        from app.audit import _collect_stats
        empty = tmp_path / "empty"
        empty.mkdir()
        domains, _, _ = _collect_stats(empty)
        assert len(domains) == 0

    def test_collect_stats_catches_json_exception(self, tmp_path):
        from app.audit import _collect_stats
        domain_dir = tmp_path / "test-domain"
        domain_dir.mkdir()
        (domain_dir / "domain.json").write_text("{invalid}", encoding="utf-8")
        domains, _, _ = _collect_stats(tmp_path)
        assert len(domains) == 0

    def test_collect_stats_catches_validation_exception(self, tmp_path):
        from app.audit import _collect_stats
        domain_dir = tmp_path / "bad-domain"
        domain_dir.mkdir()
        (domain_dir / "domain.json").write_text(
            '{"id": "not-a-uuid", "name": "bad"}', encoding="utf-8"
        )
        (domain_dir / "ontologies.json").write_text('{"ontologies": []}', encoding="utf-8")
        (domain_dir / "instances.json").write_text('{"instances": []}', encoding="utf-8")
        from app.audit import _collect_stats
        domains, _, _ = _collect_stats(tmp_path)
        assert len(domains) == 0


class TestAuditPrintDiff:
    def test_print_diff_with_changes(self, capsys):
        from app.audit import _print_diff
        previous = {
            "issues": [{"category": "a", "group": "x", "label": "l1"}],
            "timestamp": "2025-01-01T00:00:00",
        }
        current = [
            {"category": "b", "group": "y", "label": "l2"},
        ]
        _print_diff(previous, current)
        captured = capsys.readouterr()
        assert "相比上次审计" in captured.out

    def test_print_diff_with_pending(self, capsys):
        from app.audit import _print_diff
        previous = {
            "issues": [{"category": "a", "group": "x", "label": "l1"}],
            "timestamp": "2025-01-01T00:00:00",
        }
        current = [{"category": "a", "group": "x", "label": "l1"}]
        _print_diff(previous, current)
        captured = capsys.readouterr()
        assert "待处理" in captured.out

    def test_print_diff_identical(self, capsys):
        from app.audit import _print_diff
        previous = {
            "issues": [],
            "timestamp": "2025-01-01T00:00:00",
        }
        _print_diff(previous, [])
        captured = capsys.readouterr()
        assert "无新增问题" in captured.out


class TestAuditPrintReport:
    def test_print_report_need_confirm_full(self, capsys):
        from app.audit import _print_report
        need_confirm = [("组1", [("问题1", "操作1")])]
        _print_report(need_confirm, [], [], mode="full")
        captured = capsys.readouterr()
        assert "需要你确认的问题" in captured.out

    def test_print_report_need_confirm_simple(self, capsys):
        from app.audit import _print_report
        need_confirm = [("组1", [("问题1", "操作1")])]
        _print_report(need_confirm, [], [], mode="simple")
        captured = capsys.readouterr()
        assert "建议关注" in captured.out

    def test_print_report_suggestions_full(self, capsys):
        from app.audit import _print_report
        suggestions = [("组1", [("建议1", "操作1")])]
        _print_report([], [], suggestions, mode="full")
        captured = capsys.readouterr()
        assert "全面审计" in captured.out

    def test_print_report_suggestions_simple(self, capsys):
        from app.audit import _print_report
        suggestions = [("组1", [("建议1", "操作1")])]
        _print_report([], [], suggestions, mode="simple")
        captured = capsys.readouterr()
        assert "快速模式" in captured.out

    def test_print_report_summary_simple_with_issues(self, capsys):
        from app.audit import _print_report
        _print_report([("g", [("l", "a")])], [], [], mode="simple")
        captured = capsys.readouterr()
        assert "快速检查模式" in captured.out

    def test_print_report_summary_with_need_confirm(self, capsys):
        from app.audit import _print_report
        _print_report([("g", [("l", "a")])], [], [], mode="full")
        captured = capsys.readouterr()
        assert "需要你确认的问题" in captured.out
        assert "请先处理" in captured.out


class TestAuditPrintSection:
    def test_print_section_empty_groups(self, capsys):
        from app.audit import _print_section
        _print_section("标题", "描述", [])
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_print_section_with_groups(self, capsys):
        from app.audit import _print_section
        _print_section("标题", "描述", [("组1", [("标签1", "操作1")])])
        captured = capsys.readouterr()
        assert "标题" in captured.out
        assert "组1" in captured.out


class TestAuditRunTools:
    def test_run_tools_has_issue_fallback(self, monkeypatch, capsys):
        from unittest.mock import MagicMock
        from app.audit import _run_tools
        mock_tool = MagicMock()
        mock_tool.name = "validate"
        mock_tool.execute.return_value = "=== [检测到] hidden ===\n其他行\n"
        monkeypatch.setattr("app.audit.all_detection_tools", lambda mode: [mock_tool])
        from pathlib import Path
        need_confirm, auto_fixable, suggestions = _run_tools(Path("/tmp"), "full")
        assert len(need_confirm) > 0 or len(auto_fixable) > 0 or len(suggestions) > 0


class TestAuditPrintStats:
    def test_print_stats_with_domains(self, monkeypatch, capsys, tmp_path):
        from app.audit import _print_stats
        from pathlib import Path
        from qtcloud_knowl.models import Domain
        d = Domain(id="test-domain", name="Test")
        _print_stats(Path("/data"), [d], 5, 10)
        captured = capsys.readouterr()
        assert "领域清单" in captured.out
        assert "test-domain" in captured.out
        assert "Test" in captured.out


class TestAuditLoadState:
    def test_load_state_mode_mismatch(self, monkeypatch, tmp_path):
        from app import config
        monkeypatch.setattr(config.settings, "state_home", tmp_path)
        from app.audit import _save_audit_state, _load_audit_state
        _save_audit_state([], "full")
        result = _load_audit_state(mode="simple")
        assert result is None
