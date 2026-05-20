from pathlib import Path
from tests.conftest import SAMPLE_DIR, FIXTURE_DIR
from app.validators.find_undefined import run, IGNORED_TERMS, IGNORED_CHAPTER_RE


class TestFindUndefined:
    def test_all_terms_defined(self, capsys):
        result = run(SAMPLE_DIR, FIXTURE_DIR)
        captured = capsys.readouterr()
        assert result == 0
        assert "全部术语已有定义" in captured.out

    def test_ignored_terms_exist(self):
        assert len(IGNORED_TERMS) > 0

    def test_chapter_re_matches_template(self):
        assert IGNORED_CHAPTER_RE.match("第X条 制定依据")
        assert IGNORED_CHAPTER_RE.match("第X条 定义")
        assert IGNORED_CHAPTER_RE.match("第X章 总则")

    def test_chapter_re_matches_chinese_numerals(self):
        assert IGNORED_CHAPTER_RE.match("第一条 制定依据")
        assert IGNORED_CHAPTER_RE.match("第二条 目的")
        assert IGNORED_CHAPTER_RE.match("第十章 附则")

    def test_chapter_re_matches_arabic_numerals(self):
        assert IGNORED_CHAPTER_RE.match("第1条 制定依据")
        assert IGNORED_CHAPTER_RE.match("第10条 定义")
        assert IGNORED_CHAPTER_RE.match("第2章 总则")

    def test_chapter_re_does_not_match_real_term(self):
        assert not IGNORED_CHAPTER_RE.match("公司治理机构")
        assert not IGNORED_CHAPTER_RE.match("项目经理")
        assert not IGNORED_CHAPTER_RE.match("知识产权")

    def test_detects_undefined_term(self, tmp_path, capsys):
        sample = tmp_path / "samples"
        sample.mkdir()
        (sample / "test.md").write_text(
            "本文包含一个 **未知术语XYZ** 应该被检测到", encoding="utf-8"
        )
        data = tmp_path / "data"
        data.mkdir()
        domain_dir = data / "test-domain"
        domain_dir.mkdir()
        for name, content in [
            ("domain.json", '{"id": "test", "name": "test", "vocabulary": [], "files": []}'),
            ("ontologies.json", '{"ontologies": []}'),
            ("instances.json", '{"instances": []}'),
            ("relations.json", '{"relations": []}'),
        ]:
            (domain_dir / name).write_text(content, encoding="utf-8")
        result = run(sample, data)
        captured = capsys.readouterr()
        assert "未知术语XYZ" in captured.out

    def test_ignores_single_char_terms(self, tmp_path, capsys):
        sample = tmp_path / "samples"
        sample.mkdir()
        (sample / "test.md").write_text(
            "短术语 **a** 和 **x** 应被忽略", encoding="utf-8"
        )
        data = tmp_path / "data"
        data.mkdir()
        domain_dir = data / "test-domain"
        domain_dir.mkdir()
        for name, content in [
            ("domain.json", '{"id": "test", "name": "test", "vocabulary": [], "files": []}'),
            ("ontologies.json", '{"ontologies": []}'),
            ("instances.json", '{"instances": []}'),
            ("relations.json", '{"relations": []}'),
        ]:
            (domain_dir / name).write_text(content, encoding="utf-8")
        result = run(sample, data)
        captured = capsys.readouterr()
        assert "全部术语已有定义" in captured.out
