"""测试 abstract 模块边缘路径 — 未抽象本体检测"""

import json
from app.reporters.abstraction import run


class TestAbstractionEdge:
    def test_detects_unabstracted_ontology(self, tmp_path, capsys):
        domain_dir = tmp_path / "test-domain"
        domain_dir.mkdir()
        (domain_dir / "domain.json").write_text(
            '{"id": "test", "name": "test", "perspective": "test", "vocabulary": [], "files": []}',
            encoding="utf-8",
        )
        (domain_dir / "ontologies.json").write_text(
            json.dumps({
                "ontologies": [
                    {
                        "id": "bad-onto",
                        "name": "bad-onto",
                        "label": "Bad Ontology",
                        "perspective": "test",
                        "description": "A bad ontology",
                        "pattern": "项目经理负责项目管理",
                    }
                ]
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (domain_dir / "instances.json").write_text('{"instances": []}', encoding="utf-8")
        (domain_dir / "relations.json").write_text('{"relations": []}', encoding="utf-8")
        result = run(tmp_path)
        captured = capsys.readouterr()
        assert result == 1
        assert "[检测到]" in captured.out
        assert "共检测到" in captured.out

    def test_detects_book_title_signal(self, tmp_path, capsys):
        domain_dir = tmp_path / "test-domain"
        domain_dir.mkdir()
        (domain_dir / "domain.json").write_text(
            '{"id": "test", "name": "test", "perspective": "test", "vocabulary": [], "files": []}',
            encoding="utf-8",
        )
        (domain_dir / "ontologies.json").write_text(
            json.dumps({
                "ontologies": [
                    {
                        "id": "book-ref",
                        "name": "book-ref",
                        "label": "Book Ref",
                        "perspective": "test",
                        "description": "Has book reference",
                        "pattern": "见《公司章程》相关规定",
                    }
                ]
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (domain_dir / "instances.json").write_text('{"instances": []}', encoding="utf-8")
        (domain_dir / "relations.json").write_text('{"relations": []}', encoding="utf-8")
        run(tmp_path)
        captured = capsys.readouterr()
        assert "书名号引用" in captured.out
