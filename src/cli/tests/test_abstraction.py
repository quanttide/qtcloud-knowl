from app.config import FIXTURE_DIR
from app.reporters.abstraction import run


class TestAbstraction:
    def test_all_ontologies_pass_abstraction(self, capsys):
        result = run(FIXTURE_DIR)
        captured = capsys.readouterr()
        assert result == 0
        assert "所有本体 pattern 通过抽象度检测" in captured.out

    def test_each_ontology_marked_pass(self, capsys):
        result = run(FIXTURE_DIR)
        captured = capsys.readouterr()
        assert result == 0
        assert "[通过]" in captured.out

    def test_all_fourteen_ontologies_checked(self, capsys):
        result = run(FIXTURE_DIR)
        captured = capsys.readouterr()
        assert result == 0
        assert captured.out.count("[通过]") == 14
