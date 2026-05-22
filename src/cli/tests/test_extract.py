"""测试知识抽取命令"""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from typer.testing import CliRunner
from app.cli import app
from tests.conftest import SAMPLE_DIR


SAMPLE_LLM_DATA = {
    "domain": {"id": "test-domain", "name": "test-domain", "label": "测试领域", "description": ""},
    "ontologies": [
        {"id": "test-onto-1", "name": "test-onto-1", "label": "测试本体", "description": "测试本体"},
    ],
    "instances": [
        {"id": "test-inst-1", "name": "test-inst-1", "label": "测试实例", "description": "测试实例"},
    ],
}

SAMPLE_LLM_RESPONSE = json.dumps(SAMPLE_LLM_DATA, ensure_ascii=False)


class TestExtract:
    """知识抽取命令测试"""

    # === CLI 集成测试 ===

    def test_extract_empty_dir(self, tmp_path):
        from app.cli import app
        empty = tmp_path / "empty"
        empty.mkdir()
        result = CliRunner().invoke(app, ["--source", str(empty)])
        assert result.exit_code == 1
        assert "没有 .md 文件" in result.output

    def test_extract_nonexistent_dir(self):
        from app.cli import app
        result = CliRunner().invoke(app, ["--source", "/nonexistent"])
        assert result.exit_code == 1
        assert "不存在" in result.output

    def test_extract_missing_api_key(self):
        from app.cli import app
        result = CliRunner().invoke(app, ["--source", str(SAMPLE_DIR)])
        assert result.exit_code == 1
        assert "未设置 LLM API Key" in result.output

    def test_extract_creates_skeleton(self, tmp_path):
        from app.cli import app
        sample = tmp_path / "samples"
        sample.mkdir()
        (sample / "test.md").write_text("这是一份公司治理章程。", encoding="utf-8")
        out = tmp_path / "out"

        fake_domain = {"id": "org-gov", "name": "org-gov", "label": "组织治理", "description": ""}
        fake_ontologies = [{"id": "onto-1", "name": "onto-1", "label": "权责", "description": ""}]
        fake_instances = [{"id": "inst-1", "name": "inst-1", "label": "董事会", "description": ""}]

        with patch("app.agents.extract._extract_dir", return_value=(
            {"org-gov": fake_domain},
            fake_ontologies,
            fake_instances,
        )):
            result = CliRunner().invoke(
                app, ["--source", str(sample), "--data-dir", str(out)]
            )

        assert result.exit_code == 0
        assert "抽取完成" in result.output
        assert (out / "org-gov" / "domain.json").exists()
        with open(out / "org-gov" / "domain.json") as f:
            assert json.load(f)["label"] == "组织治理"

    # === _extract_dir 函数测试 ===

    def test_extract_dir_no_md_files(self, tmp_path):
        from app.agents.extract import _extract_dir
        d = tmp_path / "empty"
        d.mkdir()
        result = _extract_dir(d)
        assert "没有 .md 文件" in result

    def test_extract_dir_missing_prompt(self, tmp_path):
        from app.agents.extract import _extract_dir
        d = tmp_path / "docs"
        d.mkdir()
        (d / "test.md").write_text("内容", encoding="utf-8")
        result = _extract_dir(d, prompt_template="nonexistent.txt")
        assert "prompt 模板不存在" in result

    def test_extract_dir_no_api_key(self, tmp_path):
        from app.agents.extract import _extract_dir
        d = tmp_path / "docs"
        d.mkdir()
        (d / "test.md").write_text("内容", encoding="utf-8")
        result = _extract_dir(d)
        assert "未设置 LLM API Key" in result

    def test_extract_dir_calls_llm(self, tmp_path):
        """Mock LLM 验证 _extract_dir 正确调用 LLM 并返回结构化数据。"""
        from app.agents.extract import _extract_dir

        d = tmp_path / "docs"
        d.mkdir()
        (d / "test.md").write_text("关于董事会与股东会的治理章程", encoding="utf-8")

        mock_resp = MagicMock()
        mock_resp.content = SAMPLE_LLM_RESPONSE

        with patch("quanttide_agent.LLM") as MockLLM:
            MockLLM.return_value.complete.return_value = mock_resp
            from app.agents.extract import settings
            old = settings.llm_api_key
            settings.llm_api_key = "test-key"
            try:
                result = _extract_dir(d)
            finally:
                settings.llm_api_key = old

        domains, ontologies, instances = result
        assert "test-domain" in domains
        assert domains["test-domain"]["label"] == "测试领域"
        assert len(ontologies) == 1
        assert ontologies[0]["label"] == "测试本体"
        assert len(instances) == 1
        assert instances[0]["label"] == "测试实例"

    def test_extract_dir_llm_json_error(self, tmp_path):
        """LLM 返回非法 JSON 时跳过该文件，返回空结构。"""
        from app.agents.extract import _extract_dir

        d = tmp_path / "docs"
        d.mkdir()
        (d / "test.md").write_text("内容", encoding="utf-8")

        mock_resp = MagicMock()
        mock_resp.content = "这不是 JSON"

        with patch("quanttide_agent.LLM") as MockLLM:
            MockLLM.return_value.complete.return_value = mock_resp
            from app.agents.extract import settings
            old = settings.llm_api_key
            settings.llm_api_key = "test-key"
            try:
                domains, ontologies, instances = _extract_dir(d)
            finally:
                settings.llm_api_key = old

        assert len(domains) == 0
        assert len(ontologies) == 0
        assert len(instances) == 0

    def test_extract_dir_multiple_files(self, tmp_path):
        """多个 .md 文件的结果应合并到同一 domain。"""
        from app.agents.extract import _extract_dir

        d = tmp_path / "docs"
        d.mkdir()
        data_a = dict(SAMPLE_LLM_DATA)
        data_b = {
            "domain": {"id": "test-domain", "name": "test-domain", "label": "测试领域", "description": ""},
            "ontologies": [
                {"id": "test-onto-2", "name": "test-onto-2", "label": "流程", "description": ""},
            ],
            "instances": [
                {"id": "inst-2", "name": "inst-2", "label": "股东会", "description": ""},
            ],
        }
        (d / "a.md").write_text("文档A", encoding="utf-8")
        (d / "b.md").write_text("文档B", encoding="utf-8")

        mock_resp_a = MagicMock()
        mock_resp_a.content = json.dumps(data_a, ensure_ascii=False)
        mock_resp_b = MagicMock()
        mock_resp_b.content = json.dumps(data_b, ensure_ascii=False)

        with patch("quanttide_agent.LLM") as MockLLM:
            mock_llm = MockLLM.return_value
            mock_llm.complete.side_effect = [mock_resp_a, mock_resp_b]
            from app.agents.extract import settings
            old = settings.llm_api_key
            settings.llm_api_key = "test-key"
            try:
                domains, ontologies, instances = _extract_dir(d)
            finally:
                settings.llm_api_key = old

        assert len(domains) == 1
        assert "test-domain" in domains
        assert len(ontologies) == 2
        assert len(instances) == 2

    # === _load_prompt 函数测试 ===

    def test_load_prompt_missing(self):
        from app.agents.extract import _load_prompt
        assert _load_prompt("nonexistent.txt") is None

    def test_load_prompt_found(self):
        from app.agents.extract import _load_prompt
        content = _load_prompt("full_extraction.txt")
        assert content is not None
        assert "{document}" in content

    # === run() 函数边缘路径 ===

    def test_run_no_source(self):
        from app.agents.extract import run
        import typer
        try:
            run(source=None)
            assert False, "should have raised"
        except typer.Exit as e:
            assert e.exit_code == 1

    def test_run_verbose_mode(self, tmp_path):
        from unittest.mock import patch
        from app.agents.extract import run
        sdir = tmp_path / "samples"
        sdir.mkdir()
        (sdir / "test.md").write_text("content", encoding="utf-8")
        fake_domain = {"id": "test", "name": "test", "label": "test", "description": ""}
        with patch("app.agents.extract._extract_dir", return_value=(
            {"test": fake_domain}, [], []
        )):
            result = run(source=str(sdir), data_dir=str(tmp_path / "out"), verbose=True)
        assert result == 0

    def test_run_skips_empty_domain_id(self, tmp_path):
        from unittest.mock import patch
        from app.agents.extract import run
        sdir = tmp_path / "samples"
        sdir.mkdir()
        (sdir / "test.md").write_text("content", encoding="utf-8")
        fake_domain = {"id": "", "name": "", "label": "", "description": ""}
        with patch("app.agents.extract._extract_dir", return_value=(
            {"": fake_domain}, [], []
        )):
            result = run(source=str(sdir), data_dir=str(tmp_path / "out"), verbose=True)
        assert result == 0

    # === _extract_dir 代码栅栏剥离 ===

    def test_extract_dir_strips_code_fences(self, tmp_path):
        from unittest.mock import patch, MagicMock
        from app.agents.extract import _extract_dir
        d = tmp_path / "docs"
        d.mkdir()
        (d / "test.md").write_text("content", encoding="utf-8")
        wrapped = "```json\n" + '{"domain": {"id": "d1"}, "ontologies": [], "instances": []}\n' + "```"
        mock_resp = MagicMock()
        mock_resp.content = wrapped
        with patch("quanttide_agent.LLM") as MockLLM:
            MockLLM.return_value.complete.return_value = mock_resp
            from app.agents.extract import settings
            old = settings.llm_api_key
            settings.llm_api_key = "test-key"
            settings.llm_base_url = "http://localhost:8000"
            try:
                domains, _, _ = _extract_dir(d)
            finally:
                settings.llm_api_key = old
                settings.llm_base_url = ""
        assert "d1" in domains

    def test_extract_dir_strips_leading_trailing_fences(self, tmp_path):
        from unittest.mock import patch, MagicMock
        from app.agents.extract import _extract_dir
        d = tmp_path / "docs2"
        d.mkdir()
        (d / "test.md").write_text("content", encoding="utf-8")
        wrapped = "```\n" + '{"domain": {"id": "d2"}, "ontologies": [], "instances": []}\n' + "```"
        mock_resp = MagicMock()
        mock_resp.content = wrapped
        with patch("quanttide_agent.LLM") as MockLLM:
            MockLLM.return_value.complete.return_value = mock_resp
            from app.agents.extract import settings
            old = settings.llm_api_key
            settings.llm_api_key = "test-key"
            try:
                domains, _, _ = _extract_dir(d)
            finally:
                settings.llm_api_key = old
        assert "d2" in domains

    def test_extract_dir_only_leading_fence(self, tmp_path):
        from unittest.mock import patch, MagicMock
        from app.agents.extract import _extract_dir
        d = tmp_path / "docs3"
        d.mkdir()
        (d / "test.md").write_text("content", encoding="utf-8")
        wrapped = "```\n" + '{"domain": {"id": "d3"}, "ontologies": [], "instances": []}'
        mock_resp = MagicMock()
        mock_resp.content = wrapped
        with patch("quanttide_agent.LLM") as MockLLM:
            MockLLM.return_value.complete.return_value = mock_resp
            from app.agents.extract import settings
            old = settings.llm_api_key
            settings.llm_api_key = "test-key"
            try:
                domains, _, _ = _extract_dir(d)
            finally:
                settings.llm_api_key = old
        assert "d3" in domains
