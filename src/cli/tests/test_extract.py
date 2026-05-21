"""测试知识抽取命令"""

import json
from pathlib import Path
from unittest.mock import patch

from tests.conftest import SAMPLE_DIR, FIXTURE_DIR


class FakeChatResponse:
    def __init__(self, content):
        self.content = content


def _invoke(monkeypatch, capsys, *args):
    import sys
    monkeypatch.setattr(sys, "argv", ["qtcloud-knowl", *args])
    from app.cli import main
    try:
        code = main() or 0
    except SystemExit as e:
        code = e.code or 0
    return code, capsys.readouterr().out


class TestExtract:
    def test_extract_empty_dir(self, tmp_path, monkeypatch, capsys):
        empty = tmp_path / "empty"
        empty.mkdir()
        code, out = _invoke(monkeypatch, capsys, "extract", str(empty))
        assert code == 0
        assert "没有 .md 文件" in out

    def test_extract_runs_without_api_key(self, monkeypatch, capsys):
        monkeypatch.setattr("app.config.settings.data_home", FIXTURE_DIR)
        monkeypatch.setattr("app.config.settings.sample_home", SAMPLE_DIR)
        code, out = _invoke(monkeypatch, capsys, "extract", str(SAMPLE_DIR))
        assert code == 0
        assert "抽取完成" in out

    def test_extract_nonexistent_dir(self, monkeypatch, capsys):
        monkeypatch.setattr("app.config.settings.data_home", FIXTURE_DIR)
        monkeypatch.setattr("app.config.settings.sample_home", SAMPLE_DIR)
        code, out = _invoke(monkeypatch, capsys, "extract", "/nonexistent")
        assert "不存在" in out
        assert "确认目录路径" in out

    def test_extract_llm_no_api_key(self, tmp_path, monkeypatch, capsys):
        doc = tmp_path / "test.md"
        doc.write_text("测试内容", encoding="utf-8")
        monkeypatch.setattr("app.config.settings.data_home", FIXTURE_DIR)
        monkeypatch.setattr("app.config.settings.sample_home", SAMPLE_DIR)
        code, out = _invoke(monkeypatch, capsys, "extract", "--llm", str(doc))
        assert code == 1
        assert "未设置" in out

    def test_extract_llm_calls_llm(self, tmp_path, monkeypatch):
        monkeypatch.setattr("app.config.settings.llm_api_key", "test-key")
        from app.agents.extract import extract_with_llm

        doc = tmp_path / "test.md"
        doc.write_text("这是一份章程，涉及董事会和股东会。", encoding="utf-8")

        with patch("quanttide_agent.LLM") as MockLLM:
            mock_llm = MockLLM.return_value
            mock_llm.chat.return_value = FakeChatResponse(
                json.dumps({"concepts": [{"name": "董事会", "type": "职务"}]}, ensure_ascii=False)
            )
            result = extract_with_llm(str(doc))
            data = json.loads(result)
            assert data["concepts"][0]["name"] == "董事会"

    def test_extract_llm_nonexistent_file(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr("app.config.settings.llm_api_key", "test-key")
        monkeypatch.setattr("app.config.settings.data_home", FIXTURE_DIR)
        monkeypatch.setattr("app.config.settings.sample_home", SAMPLE_DIR)
        doc = tmp_path / "nope.md"
        code, out = _invoke(monkeypatch, capsys, "extract", "--llm", str(doc))
        assert "不存在" in out

    def test_extract_llm_prompt_not_found(self, tmp_path, monkeypatch):
        monkeypatch.setattr("app.config.settings.llm_api_key", "test-key")
        from app.agents.extract import extract_with_llm
        doc = tmp_path / "test.md"
        doc.write_text("内容", encoding="utf-8")
        result = extract_with_llm(str(doc), prompt_name="nonexistent.txt")
        assert "不存在" in result

    def test_extract_llm_missing_prompt_name(self):
        from app.agents.extract import _load_prompt
        assert _load_prompt("nonexistent.txt") is None

    def test_extract_creates_skeleton(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr("app.config.settings.data_home", FIXTURE_DIR)
        monkeypatch.setattr("app.config.settings.sample_home", SAMPLE_DIR)
        sample = tmp_path / "samples"
        sample.mkdir()
        (sample / "test.md").write_text(
            "这是一份公司治理章程，涉及董事会和股东会。", encoding="utf-8"
        )
        out = tmp_path / "out"
        code, out_text = _invoke(monkeypatch, capsys, "extract", str(sample), "--data-dir", str(out))
        assert code == 0
        assert "抽取完成" in out_text
