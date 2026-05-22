from app.audit.models import AuditMode, AuditIssue, AuditDiff, AuditState, AuditReport


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


class TestAuditState:
    def test_create(self):
        state = AuditState(mode=AuditMode.FULL, issues=[])
        assert state.mode == AuditMode.FULL
        assert state.issues == []
        assert state.timestamp is not None

    def test_with_issues(self):
        issues = [AuditIssue(category="a", group="x", label="l1")]
        state = AuditState(mode=AuditMode.SIMPLE, issues=issues)
        assert len(state.issues) == 1

    def test_mutable_issues(self):
        state = AuditState(mode=AuditMode.FULL, issues=[])
        state.issues.append(AuditIssue(category="a", group="x", label="l1"))
        assert len(state.issues) == 1


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
