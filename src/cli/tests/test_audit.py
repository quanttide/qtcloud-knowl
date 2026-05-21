"""测试全量审计命令"""

import json
from datetime import datetime
from tests.conftest import FIXTURE_DIR, SAMPLE_DIR
from app.agents.audit import _collect_issues, _compute_diff, _load_audit_state, _save_audit_state


def _invoke(monkeypatch, capsys, *args):
    import sys
    monkeypatch.setattr(sys, "argv", ["qtcloud-knowl", *args])
    from app.cli import main
    try:
        code = main() or 0
    except SystemExit as e:
        code = e.code or 0
    return code, capsys.readouterr().out


class TestAuditState:
    def _setup_state(self, monkeypatch, tmp_path):
        from app import config
        monkeypatch.setattr(config.settings, "state_home", tmp_path)

    def test_collect_issues_flattens_all_categories(self):
        issues = _collect_issues(
            [("g1", [("l1", "a1")])],
            [("g2", [("l2", "a2")])],
            [("g3", [("l3", "a3")])],
        )
        assert len(issues) == 3
        assert issues[0]["category"] == "need_confirm"
        assert issues[1]["category"] == "auto_fixable"
        assert issues[2]["category"] == "suggestions"

    def test_compute_diff_uses_hash(self):
        prev = [{"category": "a", "group": "x", "label": "l1"}, {"category": "a", "group": "x", "label": "l2"}]
        curr = [{"category": "a", "group": "x", "label": "l2"}, {"category": "a", "group": "x", "label": "l3"}]
        fixed, new, pending, _, _ = _compute_diff(prev, curr)
        assert "a|x|l1" in fixed
        assert "a|x|l3" in new
        assert "a|x|l2" in pending

    def test_save_and_load_audit_state(self, monkeypatch, tmp_path):
        self._setup_state(monkeypatch, tmp_path)
        issues = [{"category": "need_confirm", "group": "t", "label": "l"}]
        _save_audit_state(issues, "full")
        state = _load_audit_state()
        assert state is not None
        assert state["mode"] == "full"
        assert len(state["issues"]) == 1

    def test_load_nonexistent_returns_none(self, monkeypatch, tmp_path):
        self._setup_state(monkeypatch, tmp_path)
        assert _load_audit_state() is None

    def test_load_corrupted_returns_none(self, monkeypatch, tmp_path):
        self._setup_state(monkeypatch, tmp_path)
        (tmp_path / "audit.json").write_text("{invalid}", encoding="utf-8")
        assert _load_audit_state() is None


class TestAudit:
    def _invoke_audit(self, monkeypatch, capsys, data_dir, sample_dir=None, mode=None):
        import app.agents.audit
        monkeypatch.setattr(app.agents.audit.settings, "state_home", data_dir)
        args = ["audit", str(data_dir)]
        if sample_dir:
            args.extend(["--sample-dir", str(sample_dir)])
        if mode:
            args.extend(["--mode", mode])
        return _invoke(monkeypatch, capsys, *args)

    def test_audit_with_fixtures(self, monkeypatch, capsys):
        code, out = self._invoke_audit(monkeypatch, capsys, FIXTURE_DIR, SAMPLE_DIR)
        assert "知识库质量审计报告" in out
        assert "需要你确认的问题" in out or "未发现问题" in out

    def test_audit_empty_dir(self, monkeypatch, capsys, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        code, out = self._invoke_audit(monkeypatch, capsys, empty)
        assert "领域数量: 0" in out

    def test_audit_with_json_error(self, monkeypatch, capsys, tmp_path):
        domain_dir = tmp_path / "bad-domain"
        domain_dir.mkdir()
        (domain_dir / "domain.json").write_text("{invalid}", encoding="utf-8")
        (domain_dir / "ontologies.json").write_text("{}", encoding="utf-8")
        (domain_dir / "instances.json").write_text("{}", encoding="utf-8")
        (domain_dir / "relations.json").write_text("{}", encoding="utf-8")
        code, out = self._invoke_audit(monkeypatch, capsys, tmp_path)
        assert "平台发现的问题" in out or "需要你确认" in out or "未发现问题" in out

    def test_audit_mode_simple_shows_label(self, monkeypatch, capsys):
        code, out = self._invoke_audit(monkeypatch, capsys, FIXTURE_DIR, SAMPLE_DIR, mode="simple")
        assert "快速检查模式" in out
        assert "当前为快速检查模式" in out

    def test_audit_mode_full_shows_label(self, monkeypatch, capsys):
        code, out = self._invoke_audit(monkeypatch, capsys, FIXTURE_DIR, SAMPLE_DIR, mode="full")
        assert "全面审计模式" in out

    def test_audit_invalid_mode(self, monkeypatch):
        from app.cli import main
        import sys
        monkeypatch.setattr(sys, "argv", ["qtcloud-knowl", "audit", str(FIXTURE_DIR), "--mode", "invalid"])
        try:
            main()
        except SystemExit as e:
            assert e.code == 2
