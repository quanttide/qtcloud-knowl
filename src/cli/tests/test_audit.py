"""测试全量审计命令"""

import json
from typer.testing import CliRunner
from tests.conftest import FIXTURE_DIR, SAMPLE_DIR


class TestAudit:
    def _invoke(self, data_dir, sample_dir=None):
        from app.cli import app
        args = ["audit", str(data_dir)]
        if sample_dir:
            args.extend(["--sample-dir", str(sample_dir)])
        return CliRunner().invoke(app, args)

    def test_audit_with_fixtures(self):
        result = self._invoke(FIXTURE_DIR, SAMPLE_DIR)
        assert result.exit_code == 0
        assert "知识库质量审计报告" in result.output
        assert "全部检测通过" in result.output

    def test_audit_lists_all_tools(self):
        result = self._invoke(FIXTURE_DIR, SAMPLE_DIR)
        for tool in ("validate", "find-undefined-terms", "fusion-check",
                     "check-abstraction", "cross-domain-report"):
            assert tool in result.output

    def test_audit_empty_dir(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        result = self._invoke(empty)
        assert "领域数量: 0" in result.output

    def test_audit_with_json_error(self, tmp_path):
        domain_dir = tmp_path / "bad-domain"
        domain_dir.mkdir()
        (domain_dir / "domain.json").write_text("{invalid}", encoding="utf-8")
        (domain_dir / "ontologies.json").write_text("{}", encoding="utf-8")
        (domain_dir / "instances.json").write_text("{}", encoding="utf-8")
        (domain_dir / "relations.json").write_text("{}", encoding="utf-8")
        result = self._invoke(tmp_path)
        assert result.exit_code == 0 or result.exit_code == 1
