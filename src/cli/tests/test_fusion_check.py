from pathlib import Path
from tests.conftest import FIXTURE_DIR, SAMPLE_DIR
from app.validators.fusion_check import (
    run, check_term_overlap, check_broken_references,
    HUMAN_CONFIRM_TERMS, HUMAN_CONFIRM_REFS, IGNORE_LIST, NAME_MAP,
)


class TestFusionCheck:
    def test_run_passes(self):
        result = run(FIXTURE_DIR, SAMPLE_DIR)
        assert result == 0

    def test_no_name_conflict(self, capsys):
        from app.validators.fusion_check import check_name_conflict
        check_name_conflict(FIXTURE_DIR)
        captured = capsys.readouterr()
        assert "（无冲突）" in captured.out

    def test_term_overlap_detected_without_human_confirm(self, capsys):
        check_term_overlap(FIXTURE_DIR)
        captured = capsys.readouterr()
        assert "交接" in captured.out
        assert "【需人确认】" not in captured.out

    def test_broken_references_has_human_confirm(self, capsys):
        check_broken_references(SAMPLE_DIR)
        captured = capsys.readouterr()
        assert "【需人确认】" in captured.out

    def test_human_confirm_terms_empty(self):
        assert not HUMAN_CONFIRM_TERMS

    def test_human_confirm_refs_defined(self):
        assert "量潮数据项目岗位权责章程" in HUMAN_CONFIRM_REFS

    def test_known_refs_resolve(self):
        for ref, expected in NAME_MAP.items():
            expected_file = SAMPLE_DIR / f"{expected}.md"
            assert expected_file.exists(), f"{ref} → {expected}.md not found"
