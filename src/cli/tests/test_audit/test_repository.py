import json
from pathlib import Path

from app.audit.models import AuditMode, AuditIssue, AuditState
from app.audit.repository import AuditStateRepository


class TestAuditStateRepository:
    def _make_repo(self, tmp_path):
        return AuditStateRepository(tmp_path)

    def test_save_and_load(self, tmp_path):
        repo = self._make_repo(tmp_path)
        issues = [AuditIssue(category="need_confirm", group="t", label="l")]
        state = AuditState(mode=AuditMode.FULL, issues=issues)
        repo.save(state)
        assert (tmp_path / "audit.json").exists()
        loaded = repo.load()
        assert loaded is not None
        assert loaded.mode == AuditMode.FULL
        assert len(loaded.issues) == 1
        assert loaded.issues[0].category == "need_confirm"

    def test_load_nonexistent(self, tmp_path):
        repo = self._make_repo(tmp_path)
        assert repo.load() is None

    def test_load_corrupted(self, tmp_path):
        repo = self._make_repo(tmp_path)
        (tmp_path / "audit.json").write_text("{invalid}", encoding="utf-8")
        assert repo.load() is None

    def test_load_mode_mismatch(self, tmp_path):
        repo = self._make_repo(tmp_path)
        state = AuditState(mode=AuditMode.FULL, issues=[])
        repo.save(state)
        result = repo.load(mode=AuditMode.SIMPLE)
        assert result is None

    def test_load_action_fallback(self, tmp_path):
        repo = self._make_repo(tmp_path)
        (tmp_path / "audit.json").write_text(
            json.dumps({
                "mode": "full",
                "timestamp": "2025-01-01",
                "issues": [{"category": "a", "group": "x", "label": "l"}],
            }),
            encoding="utf-8",
        )
        loaded = repo.load()
        assert loaded.issues[0].action == ""

    def test_save_creates_parent_dir(self, tmp_path):
        nested = tmp_path / "sub" / "dir"
        repo = AuditStateRepository(nested)
        repo.save(AuditState(mode=AuditMode.FULL, issues=[]))
        assert (nested / "audit.json").exists()
