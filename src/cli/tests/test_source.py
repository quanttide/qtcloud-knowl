"""测试 source 命令 — 下载、列出、清理源文档"""

from unittest.mock import patch

from typer.testing import CliRunner


def _setup(monkeypatch, source_home):
    monkeypatch.setenv("QTCLOUD_KNOWL_SOURCE_HOME", str(source_home))
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
        (tmp_path / "test-source").mkdir(parents=True)
        runner = CliRunner()
        result = runner.invoke(app, ["source", "list"])
        assert "test-source" in result.output

    def test_list_nonexistent_dir(self, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_SOURCE_HOME", "/nonexistent/path")
        import importlib
        from app import config
        importlib.reload(config)
        import app.source as src_mod
        importlib.reload(src_mod)
        assert src_mod.list_sources() == []


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

    def test_download_already_exists(self, tmp_path, monkeypatch):
        app = _setup(monkeypatch, tmp_path)
        (tmp_path / "qtcloud-bylaw").mkdir(parents=True)
        runner = CliRunner()
        result = runner.invoke(app, ["source", "download", "--name", "qtcloud-bylaw"])
        assert "已存在" in result.output

    def test_download_all(self, tmp_path, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_SOURCE_HOME", str(tmp_path))
        import importlib
        from app import config
        importlib.reload(config)
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stderr = ""
            import app.source as src_mod
            importlib.reload(src_mod)
            results = src_mod.download_all()
            assert len(results) == 3
            assert "已下载" in results[0]

    def test_download_failure(self, tmp_path, monkeypatch):
        monkeypatch.setenv("QTCLOUD_KNOWL_SOURCE_HOME", str(tmp_path))
        import importlib
        from app import config
        importlib.reload(config)
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "error"
            import app.source as src_mod
            importlib.reload(src_mod)
            result = src_mod.download("qtcloud-bylaw")
            assert "下载失败" in result


class TestSourceRemove:
    def test_remove_existing(self, tmp_path, monkeypatch):
        app = _setup(monkeypatch, tmp_path)
        (tmp_path / "test-source").mkdir(parents=True)
        runner = CliRunner()
        result = runner.invoke(app, ["source", "remove", "--name", "test-source"])
        assert "已删除" in result.output

    def test_remove_nonexistent(self, tmp_path, monkeypatch):
        app = _setup(monkeypatch, tmp_path)
        runner = CliRunner()
        result = runner.invoke(app, ["source", "remove", "--name", "nonexistent"])
        assert "不存在" in result.output

    def test_remove_all(self, tmp_path, monkeypatch):
        app = _setup(monkeypatch, tmp_path)
        (tmp_path / "src-a").mkdir(parents=True)
        (tmp_path / "src-b").mkdir(parents=True)
        runner = CliRunner()
        result = runner.invoke(app, ["source", "remove"])
        assert "已删除" in result.output
        assert not (tmp_path / "src-a").exists()

