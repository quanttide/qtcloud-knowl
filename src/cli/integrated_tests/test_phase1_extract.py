"""
OCL 阶段一测试：知识源准备 → AI 粗提取

验证用户能从源文档创建知识库骨架，并调用 LLM 看到候选本体。
"""

from unittest.mock import patch

from typer.testing import CliRunner


class FakeResponse:
    def __init__(self, content):
        self.content = content


def _setup(monkeypatch, sample_dir, data_home, api_key="test-key"):
    """统一环境设置，避免各测试重复 reload 逻辑。"""
    monkeypatch.setenv("QTCLOUD_KNOWL_SAMPLE_HOME", str(sample_dir))
    monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(data_home))
    monkeypatch.setenv("QTCLOUD_KNOWL_LLM_API_KEY", api_key)
    import importlib
    from app import config
    importlib.reload(config)
    import app.reviewers.data as rdata
    import app.review as rmod
    importlib.reload(rdata)
    importlib.reload(rmod)
    import app.cli as cli_mod
    importlib.reload(cli_mod)
    return cli_mod.app


class TestExtractSkeleton:
    """extract 骨架创建（无 LLM）"""

    def test_creates_skeleton_from_samples(self, sample_doc, knowledge_base, monkeypatch):
        app = _setup(monkeypatch, sample_doc.parent, knowledge_base)
        runner = CliRunner()
        result = runner.invoke(app, ["extract"])
        assert result.exit_code == 0
        assert "抽取完成" in result.output

    def test_no_md_files_returns_message(self, tmp_path, monkeypatch):
        app = _setup(monkeypatch, tmp_path, tmp_path)
        runner = CliRunner()
        result = runner.invoke(app, ["extract", str(tmp_path)])
        assert "没有 .md 文件" in result.output


class TestExtractLLM:
    """extract --llm 语义抽取"""

    def test_returns_llm_output(self, sample_doc, knowledge_base, monkeypatch):
        app = _setup(monkeypatch, sample_doc.parent, knowledge_base, api_key="test-key")
        with patch("quanttide_agent.LLM") as MockLLM:
            mock = MockLLM.return_value
            mock.complete.return_value = FakeResponse(
                '{"concepts": [{"name": "数据治理委员会", "type": "职务"}]}'
            )
            runner = CliRunner()
            result = runner.invoke(app, ["extract", "--llm", str(sample_doc)])
            assert result.exit_code == 0
            assert "数据治理委员会" in result.output

    def test_requires_api_key(self, sample_doc, knowledge_base, monkeypatch):
        app = _setup(monkeypatch, sample_doc.parent, knowledge_base, api_key="")
        runner = CliRunner()
        result = runner.invoke(app, ["extract", "--llm", str(sample_doc)])
        assert result.exit_code == 1
        assert "未设置" in result.output

    def test_nonexistent_file(self, tmp_path, monkeypatch):
        app = _setup(monkeypatch, tmp_path, tmp_path)
        runner = CliRunner()
        result = runner.invoke(app, ["extract", "--llm", str(tmp_path / "nope.md")])
        assert "不存在" in result.output
