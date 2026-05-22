#!/usr/bin/env python3
"""知识工程智能体 — 统一 CLI 入口。

所有命令从 `settings` 读取路径，不接受位置参数。

    >>> from app.cli import app
    >>> from typer.testing import CliRunner
    >>> runner = CliRunner()
    >>> result = runner.invoke(app, ["--help"])
    >>> result.exit_code
    0
"""

import typer

app = typer.Typer()


@app.command()
def extract(
    source: str = typer.Option(None, "--source", "-s", help="源文档目录路径"),
    data_dir: str = typer.Option(None, "--data-dir", help="数据目录路径"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="显示详细匹配信息"),
):
    """知识抽取 — 从源文件自动创建知识库骨架"""
    from app.extract import run

    return run(source, data_dir, verbose)


def main():
    return app()


if __name__ == "__main__":  # pragma: no cover
    exit(main())
