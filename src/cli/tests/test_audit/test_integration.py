"""测试 audit 包集成 — run() 编排、展示打印"""

from pathlib import Path
from app.audit import run
from app.audit.models import AuditMode, AuditIssue, AuditDiff, AuditReport, AuditState, KnowledgeBaseStats, IssueGroup
from app.audit.repository import AuditStateRepository
from app.audit.renderer import print_stats, print_report, print_diff
from app.audit.parser import ToolOutputParser
from tests.conftest import FIXTURE_DIR


class TestAuditRun:
    def _setup_state(self, monkeypatch, tmp_path):
        from app import config
        monkeypatch.setattr(config.settings, "state_home", tmp_path)

    def test_audit_with_fixtures(self, monkeypatch, tmp_path, capsys):
        self._setup_state(monkeypatch, tmp_path)
        ret = run(data_dir=str(FIXTURE_DIR))
        captured = capsys.readouterr()
        assert "知识库概览" in captured.out
        assert "检测结果" in captured.out

    def test_audit_empty_dir(self, monkeypatch, tmp_path, capsys):
        self._setup_state(monkeypatch, tmp_path)
        empty = tmp_path / "empty"
        empty.mkdir()
        ret = run(data_dir=str(empty))
        captured = capsys.readouterr()
        assert "领域数量: 0" in captured.out
        assert ret == 0

    def test_audit_with_json_error(self, monkeypatch, tmp_path, capsys):
        self._setup_state(monkeypatch, tmp_path)
        import json
        domain_dir = tmp_path / "bad-domain"
        domain_dir.mkdir()
        for name in ["domain.json", "ontologies.json", "instances.json", "relations.json"]:
            (domain_dir / name).write_text("{invalid}", encoding="utf-8")
        ret = run(data_dir=str(tmp_path))
        captured = capsys.readouterr()
        assert "JSON 格式错误" in captured.out

    def test_audit_mode_simple(self, monkeypatch, tmp_path, capsys):
        self._setup_state(monkeypatch, tmp_path)
        ret = run(data_dir=str(FIXTURE_DIR), mode="simple")
        captured = capsys.readouterr()
        assert "知识库概览" in captured.out

    def test_audit_mode_full(self, monkeypatch, tmp_path, capsys):
        self._setup_state(monkeypatch, tmp_path)
        ret = run(data_dir=str(FIXTURE_DIR), mode="full")
        captured = capsys.readouterr()
        assert "知识库概览" in captured.out

    def test_audit_invalid_mode(self, monkeypatch, tmp_path, capsys):
        self._setup_state(monkeypatch, tmp_path)
        ret = run(data_dir=str(FIXTURE_DIR), mode="invalid")
        captured = capsys.readouterr()
        assert "不支持的审计模式" in captured.out
        assert ret == 1

    def test_audit_nonexistent_dir(self, monkeypatch, tmp_path, capsys):
        self._setup_state(monkeypatch, tmp_path)
        ret = run(data_dir="/nonexistent/path")
        captured = capsys.readouterr()
        assert "数据目录不存在" in captured.out
        assert ret == 1

    def test_audit_with_print_diff(self, monkeypatch, tmp_path, capsys):
        self._setup_state(monkeypatch, tmp_path)
        repo = AuditStateRepository(tmp_path)
        previous_issues = [AuditIssue(category="a", group="x", label="l1")]
        repo.save(AuditState(mode=AuditMode.FULL, issues=previous_issues))
        ret = run(data_dir=str(FIXTURE_DIR))
        captured = capsys.readouterr()
        assert "相比上次审计" in captured.out

    def test_audit_with_identical_state(self, monkeypatch, tmp_path, capsys):
        self._setup_state(monkeypatch, tmp_path)
        repo = AuditStateRepository(tmp_path)
        repo.save(AuditState(mode=AuditMode.FULL, issues=[]))
        ret = run(data_dir=str(FIXTURE_DIR))
        captured = capsys.readouterr()
        assert "无新增问题" in captured.out


class TestAuditPrintDiff:
    def test_print_diff_with_changes(self, capsys):
        diff = AuditDiff(
            fixed=frozenset({"a|x|l1"}),
            new=frozenset({"b|y|l2"}),
            pending=frozenset(),
            previous_timestamp="2025-01-01T00:00:00",
        )
        print_diff(diff)
        captured = capsys.readouterr()
        assert "相比上次审计" in captured.out

    def test_print_diff_with_pending(self, capsys):
        diff = AuditDiff(
            fixed=frozenset(),
            new=frozenset(),
            pending=frozenset({"a|x|l1"}),
            previous_timestamp="2025-01-01T00:00:00",
        )
        print_diff(diff)
        captured = capsys.readouterr()
        assert "待处理" in captured.out

    def test_print_diff_identical(self, capsys):
        diff = AuditDiff(
            fixed=frozenset(),
            new=frozenset(),
            pending=frozenset(),
            previous_timestamp="2025-01-01T00:00:00",
        )
        print_diff(diff)
        captured = capsys.readouterr()
        assert "无新增问题" in captured.out


class TestAuditPrintReport:
    def test_print_report_need_confirm_full(self, capsys):
        issue = AuditIssue(category="need_confirm", group="组1", label="问题1", action="操作1")
        report = AuditReport(need_confirm=[issue], auto_fixable=[], suggestions=[], mode=AuditMode.FULL)
        print_report(report)
        captured = capsys.readouterr()
        assert "需要你确认的问题" in captured.out

    def test_print_report_need_confirm_simple(self, capsys):
        issue = AuditIssue(category="need_confirm", group="组1", label="问题1", action="操作1")
        report = AuditReport(need_confirm=[issue], auto_fixable=[], suggestions=[], mode=AuditMode.SIMPLE)
        print_report(report)
        captured = capsys.readouterr()
        assert "建议关注" in captured.out

    def test_print_report_suggestions_full(self, capsys):
        issue = AuditIssue(category="suggestions", group="组1", label="建议1", action="操作1")
        report = AuditReport(need_confirm=[], auto_fixable=[], suggestions=[issue], mode=AuditMode.FULL)
        print_report(report)
        captured = capsys.readouterr()
        assert "全面审计" in captured.out

    def test_print_report_suggestions_simple(self, capsys):
        issue = AuditIssue(category="suggestions", group="组1", label="建议1", action="操作1")
        report = AuditReport(need_confirm=[], auto_fixable=[], suggestions=[issue], mode=AuditMode.SIMPLE)
        print_report(report)
        captured = capsys.readouterr()
        assert "快速模式" in captured.out

    def test_print_report_no_issues(self, capsys):
        report = AuditReport(need_confirm=[], auto_fixable=[], suggestions=[], mode=AuditMode.FULL)
        print_report(report)
        captured = capsys.readouterr()
        assert "未发现问题" in captured.out

    def test_print_report_mixed_section_order(self, capsys):
        issue = AuditIssue(category="auto_fixable", group="组1", label="可修复", action="修复")
        report = AuditReport(need_confirm=[], auto_fixable=[issue], suggestions=[], mode=AuditMode.FULL)
        print_report(report)
        captured = capsys.readouterr()
        assert "平台发现的问题" in captured.out


class TestAuditPrintStats:
    def test_print_stats_with_domains(self, capsys):
        from qtcloud_knowl.models import Domain
        d = Domain(id="test-domain", name="Test")
        stats = KnowledgeBaseStats(data_dir=Path("/data"), domains=[d], ontology_count=5, instance_count=10)
        print_stats(stats)
        captured = capsys.readouterr()
        assert "领域清单" in captured.out
        assert "test-domain" in captured.out

    def test_print_stats_without_domains(self, capsys):
        stats = KnowledgeBaseStats(data_dir=Path("/data"), domains=[], ontology_count=0, instance_count=0)
        print_stats(stats)
        captured = capsys.readouterr()
        assert "领域数量: 0" in captured.out


class TestAuditParser:
    def test_parse_issues(self):
        parser = ToolOutputParser()
        output = "=== org-gov ===\n[MISS] ontologies.json\n[FAIL] instances.json\n"
        issues = parser.parse(output, "/data")
        assert len(issues) == 2

    def test_has_issue_fallback(self):
        parser = ToolOutputParser()
        assert parser.has_issue("[MISS] x")
        assert parser.has_issue("[FAIL] x")
        assert not parser.has_issue("正常文本")


class TestAuditPrintSection:
    def test_print_section_empty_groups(self, capsys):
        from app.audit.renderer import _print_section
        _print_section("标题", "描述", [])
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_print_section_with_multiple_groups(self, capsys):
        from app.audit.renderer import _print_section
        issues_a = [AuditIssue(category="a", group="组A", label="标签1", action="操作1")]
        issues_b = [AuditIssue(category="a", group="组B", label="标签2")]
        groups = [
            IssueGroup(group_name="组A", issues=issues_a),
            IssueGroup(group_name="组B", issues=issues_b),
        ]
        _print_section("标题", "描述", groups)
        captured = capsys.readouterr()
        assert "组A" in captured.out
        assert "组B" in captured.out


class TestAuditCollectStats:
    _DOMAIN_UUID = "00000000-0000-0000-0000-000000000001"
    _ONTO_UUID = "00000000-0000-0000-0000-000000000010"
    _INST_UUID = "00000000-0000-0000-0000-000000000020"

    def _valid_domain_dir(self, tmp_path, name="test-domain"):
        import json
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

    def test_collect_stats_with_valid_domain(self, tmp_path):
        self._valid_domain_dir(tmp_path)
        from app.audit.service import _collect_stats
        stats = _collect_stats(tmp_path)
        assert stats.domain_count == 1
        assert stats.ontology_count == 1
        assert stats.instance_count == 1

    def test_collect_stats_empty_dir(self, tmp_path):
        from app.audit.service import _collect_stats
        empty = tmp_path / "empty"
        empty.mkdir()
        stats = _collect_stats(empty)
        assert stats.domain_count == 0

    def test_collect_stats_catches_exception(self, tmp_path):
        from app.audit.service import _collect_stats
        stats = _collect_stats(tmp_path / "nonexistent")
        assert stats.domain_count == 0

    def test_collect_stats_data_dir_path(self, tmp_path):
        from app.audit.service import _collect_stats
        stats = _collect_stats(tmp_path)
        assert stats.data_dir == tmp_path


class TestAuditInternal:
    def test_collect_stats_exception(self, tmp_path):
        from app.audit.service import _collect_stats
        stats = _collect_stats(tmp_path / "nonexistent")
        assert stats.domain_count == 0
        assert stats.ontology_count == 0
        assert stats.instance_count == 0

    def test_run_tools_fallback_issue(self, monkeypatch):
        from unittest.mock import MagicMock
        from app.audit.service import _run_tools
        from app.audit.models import AuditMode
        mock_tool = MagicMock()
        mock_tool.name = "validate"
        mock_tool.execute.return_value = "=== [检测到] hidden ===\n其他行\n"
        monkeypatch.setattr("app.audit.service.all_detection_tools", lambda mode: [mock_tool])
        need_confirm, auto_fixable, suggestions = _run_tools(Path("/tmp"), AuditMode.FULL)
        assert len(need_confirm) > 0 or len(auto_fixable) > 0 or len(suggestions) > 0


class TestAuditPrintGroup:
    def test_print_group_with_action(self, capsys):
        from app.audit.renderer import _print_group
        issue = AuditIssue(category="a", group="g", label="l", action="a")
        _print_group("标题", [issue])
        captured = capsys.readouterr()
        assert "→ a" in captured.out

    def test_print_group_without_action(self, capsys):
        from app.audit.renderer import _print_group
        issue = AuditIssue(category="a", group="g", label="l")
        _print_group("标题", [issue])
        captured = capsys.readouterr()
        assert "l" in captured.out
