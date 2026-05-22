from pathlib import Path
from app.audit.models import (
    AuditMode, AuditIssue, AuditDiff, AuditReport,
    KnowledgeBaseStats, IssueGroup,
)


class TestAuditMode:
    def test_simple_value(self):
        assert AuditMode.SIMPLE.value == "simple"

    def test_full_value(self):
        assert AuditMode.FULL.value == "full"

    def test_construct_from_string(self):
        assert AuditMode("simple") == AuditMode.SIMPLE
        assert AuditMode("full") == AuditMode.FULL


class TestAuditIssue:
    def test_create(self):
        issue = AuditIssue(category="need_confirm", group="g", label="l", action="a")
        assert issue.category == "need_confirm"
        assert issue.group == "g"
        assert issue.label == "l"
        assert issue.action == "a"

    def test_issue_key(self):
        issue = AuditIssue(category="a", group="x", label="l1")
        assert issue.issue_key() == "a|x|l1"

    def test_default_action(self):
        issue = AuditIssue(category="a", group="g", label="l")
        assert issue.action == ""


class TestAuditDiff:
    def test_compute_with_changes(self):
        prev = [AuditIssue(category="a", group="x", label="l1"), AuditIssue(category="a", group="x", label="l2")]
        curr = [AuditIssue(category="a", group="x", label="l2"), AuditIssue(category="a", group="x", label="l3")]
        diff = AuditDiff.compute(prev, curr)
        assert "a|x|l1" in diff.fixed
        assert "a|x|l3" in diff.new
        assert "a|x|l2" in diff.pending

    def test_compute_identical(self):
        prev = [AuditIssue(category="a", group="x", label="l1")]
        curr = [AuditIssue(category="a", group="x", label="l1")]
        diff = AuditDiff.compute(prev, curr)
        assert not diff.fixed
        assert not diff.new
        assert diff.pending == frozenset({"a|x|l1"})

    def test_has_changes(self):
        diff = AuditDiff(fixed=frozenset({"a"}), new=frozenset(), pending=frozenset())
        assert diff.has_changes
        assert not diff.is_identical

    def test_no_changes(self):
        diff = AuditDiff(fixed=frozenset(), new=frozenset(), pending=frozenset())
        assert not diff.has_changes
        assert diff.is_identical

    def test_with_timestamp(self):
        prev = [AuditIssue(category="a", group="x", label="l1")]
        curr = []
        diff = AuditDiff.compute(prev, curr, prev_timestamp="2025-01-01T00:00:00")
        assert diff.previous_timestamp == "2025-01-01T00:00:00"


class TestIssueGroup:
    def test_from_issues_groups_by_group_field(self):
        issues = [
            AuditIssue(category="a", group="g1", label="l1"),
            AuditIssue(category="a", group="g1", label="l2"),
            AuditIssue(category="b", group="g2", label="l3"),
        ]
        groups = IssueGroup.from_issues(issues)
        assert len(groups) == 2
        assert groups[0].group_name in ("g1", "g2")
        assert len([g for g in groups if g.group_name == "g1"][0].issues) == 2

    def test_from_issues_empty(self):
        assert IssueGroup.from_issues([]) == []


class TestAuditReport:
    def test_create(self):
        report = AuditReport(need_confirm=[], auto_fixable=[], suggestions=[], mode=AuditMode.FULL)
        assert report.mode == AuditMode.FULL
        assert report.need_confirm == []
        assert report.auto_fixable == []
        assert report.suggestions == []

    def test_with_issues(self):
        issue = AuditIssue(category="need_confirm", group="g", label="l")
        report = AuditReport(need_confirm=[issue], auto_fixable=[], suggestions=[], mode=AuditMode.SIMPLE)
        assert len(report.need_confirm) == 1

    def test_from_raw_full(self):
        report = AuditReport.from_raw(["a"], ["b"], ["c"], AuditMode.FULL)
        assert report.need_confirm == ["a"]
        assert report.auto_fixable == ["b"]
        assert report.suggestions == ["c"]

    def test_from_raw_simple_reclassifies(self):
        report = AuditReport.from_raw(["confirm"], ["fixable"], ["suggest"], AuditMode.SIMPLE)
        assert report.need_confirm == ["fixable"]
        assert report.auto_fixable == []
        assert report.suggestions == ["confirm", "suggest"]

    def test_from_raw_simple_empty(self):
        report = AuditReport.from_raw([], [], [], AuditMode.SIMPLE)
        assert report.need_confirm == []
        assert report.auto_fixable == []

    def test_is_clean_true(self):
        report = AuditReport.from_raw([], [], [], AuditMode.FULL)
        assert report.is_clean

    def test_is_clean_false(self):
        report = AuditReport.from_raw(["issue"], [], [], AuditMode.FULL)
        assert not report.is_clean

    def test_is_clean_ignores_suggestions(self):
        report = AuditReport.from_raw([], [], ["suggestion"], AuditMode.FULL)
        assert report.is_clean

    def test_exit_code_clean(self):
        report = AuditReport.from_raw([], [], [], AuditMode.FULL)
        assert report.exit_code == 0

    def test_exit_code_dirty(self):
        report = AuditReport.from_raw(["issue"], [], [], AuditMode.FULL)
        assert report.exit_code == 1

    def test_exit_code_ignores_suggestions(self):
        report = AuditReport.from_raw([], [], ["s"], AuditMode.FULL)
        assert report.exit_code == 0


class TestKnowledgeBaseStats:
    def test_create(self):
        stats = KnowledgeBaseStats(data_dir=Path("/data"), domains=[], ontology_count=0, instance_count=0)
        assert stats.domain_count == 0
        assert not stats.has_domains

    def test_with_domains(self):
        stats = KnowledgeBaseStats(data_dir=Path("/data"), domains=["d1"], ontology_count=5, instance_count=10)
        assert stats.domain_count == 1
        assert stats.has_domains
        assert stats.ontology_count == 5
        assert stats.instance_count == 10



