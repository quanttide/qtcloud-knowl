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


class TestFusionCheckEdgePaths:
    def test_name_conflict_detected(self, tmp_path, capsys):
        from app.validators.fusion_check import check_name_conflict
        d1 = tmp_path / "domain-a"
        d1.mkdir()
        (d1 / "domain.json").write_text(
            '{"id": "domain-a", "name": "A", "vocabulary": []}', encoding="utf-8"
        )
        (d1 / "ontologies.json").write_text(
            '{"ontologies": [{"id": "o1", "name": "o1", "label": "相同标签"}]}',
            encoding="utf-8",
        )
        (d1 / "instances.json").write_text('{"instances": []}', encoding="utf-8")
        (d1 / "relations.json").write_text('{"relations": []}', encoding="utf-8")
        d2 = tmp_path / "domain-b"
        d2.mkdir()
        (d2 / "domain.json").write_text(
            '{"id": "domain-b", "name": "B", "vocabulary": []}', encoding="utf-8"
        )
        (d2 / "ontologies.json").write_text(
            '{"ontologies": [{"id": "o2", "name": "o2", "label": "相同标签"}]}',
            encoding="utf-8",
        )
        (d2 / "instances.json").write_text('{"instances": []}', encoding="utf-8")
        (d2 / "relations.json").write_text('{"relations": []}', encoding="utf-8")
        check_name_conflict(tmp_path)
        captured = capsys.readouterr()
        assert "出现" in captured.out

    def test_broken_reference_missing_expected_file(self, tmp_path, capsys):
        from app.validators.fusion_check import check_broken_references
        (tmp_path / "test.md").write_text(
            "本文引用《量潮科技基本章程》相关内容", encoding="utf-8"
        )
        check_broken_references(tmp_path)
        captured = capsys.readouterr()
        assert "不存在" in captured.out

    def test_broken_reference_fuzzy_match(self, tmp_path, capsys):
        from app.validators.fusion_check import check_broken_references
        (tmp_path / "test.md").write_text(
            "本文引用《customRef相关内容》", encoding="utf-8"
        )
        (tmp_path / "customRef.md").write_text("内容", encoding="utf-8")
        check_broken_references(tmp_path)
        captured = capsys.readouterr()
        assert "全部可追溯" in captured.out

    def test_multiple_effectiveness_bodies(self, tmp_path, capsys):
        from app.validators.fusion_check import check_effectiveness_consistency
        (tmp_path / "章程一.md").write_text(
            "**第六条 章程效力**\n本章程经公司股东会审议通过，自发布之日起生效。",
            encoding="utf-8",
        )
        (tmp_path / "章程二.md").write_text(
            "**章程效力**\n本章程经公司董事会修订，自2024年1月1日起生效。",
            encoding="utf-8",
        )
        check_effectiveness_consistency(tmp_path)
        captured = capsys.readouterr()
        assert "不同" in captured.out or "⚠" in captured.out
