"""测试 CLI 命令执行 — 直接调用底层函数"""

from unittest.mock import MagicMock


class TestCliMain:
    """测试 app.cli.main() 入口函数"""

    def test_main_function(self, monkeypatch):
        mock_app = MagicMock()
        monkeypatch.setattr("app.cli.app", mock_app)
        from app.cli import main
        main()
        mock_app.assert_called_once()

    def test_main_exit_code_zero(self, monkeypatch):
        mock_app = MagicMock(return_value=0)
        monkeypatch.setattr("app.cli.app", mock_app)
        from app.cli import main
        result = main()
        assert result == 0
