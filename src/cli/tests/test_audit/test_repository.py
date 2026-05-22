import json
from pathlib import Path
from app.audit.models import AuditMode, AuditIssue, KnowledgeBaseStats, AuditReport as AuditIssues
from app.audit.report import Report, ReportRepository


class TestReportRepository:
    def _repo(self, tmp_path):
        return ReportRepository(tmp_path)

    def test_save_and_load_state(self, tmp_path):
        repo = self._repo(tmp_path)
        stats = KnowledgeBaseStats(data_dir=tmp_path, domains=[], ontology_count=0, instance_count=0)
        issues = AuditIssues.from_raw(
            [AuditIssue("need_confirm", "g", "l")], [], [], AuditMode.FULL
        )
        report = Report(mode=AuditMode.FULL, stats=stats, issues=issues)
        repo.save_report(report)
        assert (tmp_path / "audit.json").exists()
        loaded = repo.load_previous_state()
        assert loaded is not None
        assert loaded.mode == AuditMode.FULL
        assert len(loaded.issues) == 1

    def test_load_nonexistent(self, tmp_path):
        repo = self._repo(tmp_path)
        assert repo.load_previous_state() is None

    def test_load_corrupted(self, tmp_path):
        repo = self._repo(tmp_path)
        (tmp_path / "audit.json").write_text("{invalid}", encoding="utf-8")
        assert repo.load_previous_state() is None

    def test_load_mode_mismatch(self, tmp_path):
        repo = self._repo(tmp_path)
        stats = KnowledgeBaseStats(data_dir=tmp_path, domains=[], ontology_count=0, instance_count=0)
        issues = AuditIssues.from_raw([], [], [], AuditMode.FULL)
        report = Report(mode=AuditMode.FULL, stats=stats, issues=issues)
        repo.save_report(report)
        result = repo.load_previous_state(mode=AuditMode.SIMPLE)
        assert result is None

    def test_load_action_fallback(self, tmp_path):
        repo = self._repo(tmp_path)
        (tmp_path / "audit.json").write_text(
            json.dumps({
                "mode": "full",
                "timestamp": "2025-01-01",
                "issues": [{"category": "a", "group": "x", "label": "l"}],
            }),
            encoding="utf-8",
        )
        loaded = repo.load_previous_state()
        assert loaded.issues[0].action == ""

    def test_save_creates_parent_dir(self, tmp_path):
        nested = tmp_path / "sub" / "dir"
        repo = ReportRepository(nested)
        stats = KnowledgeBaseStats(data_dir=nested, domains=[], ontology_count=0, instance_count=0)
        issues = AuditIssues.from_raw([], [], [], AuditMode.FULL)
        report = Report(mode=AuditMode.FULL, stats=stats, issues=issues)
        repo.save_report(report)
        assert (nested / "audit.json").exists()
