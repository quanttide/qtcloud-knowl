"""测试 source 命令 — 下载、列出、清理源文档"""

from typer.testing import CliRunner


def _setup(monkeypatch, data_home):
    monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(data_home))
    import importlib
    from app import config
    importlib.reload(config)
    import app.source as src_mod
    import app.cli as cli_mod
    importlib.reload(src_mod)
    importlib.reload(cli_mod)
    return cli_mod.app


class TestSourceList:
    def test_list_empty(self, tmp_path, monkeypatch):
        app = _setup(monkeypatch, tmp_path)
        runner = CliRunner()
        result = runner.invoke(app, ["source", "list"])
        assert "未下载" in result.output

    def test_list_with_data(self, tmp_path, monkeypatch):
        app = _setup(monkeypatch, tmp_path)
        (tmp_path / "samples" / "test-source").mkdir(parents=True)
        runner = CliRunner()
        result = runner.invoke(app, ["source", "list"])
        assert "test-source" in result.output


class TestSourceDownload:
    def test_download_unknown(self, tmp_path, monkeypatch):
        app = _setup(monkeypatch, tmp_path)
        runner = CliRunner()
        result = runner.invoke(app, ["source", "download", "--name", "nonexistent"])
        assert "未知" in result.output

    def test_download_shows_available(self, tmp_path, monkeypatch):
        app = _setup(monkeypatch, tmp_path)
        runner = CliRunner()
        result = runner.invoke(app, ["source", "download"])
        assert "qtcloud-bylaw" in result.output


class TestSourceRemove:
    def test_remove_existing(self, tmp_path, monkeypatch):
        app = _setup(monkeypatch, tmp_path)
        (tmp_path / "samples" / "test-source").mkdir(parents=True)
        runner = CliRunner()
        result = runner.invoke(app, ["source", "remove", "--name", "test-source"])
        assert "已删除" in result.output

    def test_remove_nonexistent(self, tmp_path, monkeypatch):
        app = _setup(monkeypatch, tmp_path)
        runner = CliRunner()
        result = runner.invoke(app, ["source", "remove", "--name", "nonexistent"])
        assert "不存在" in result.output
