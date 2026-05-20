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
from app.config import settings

app = typer.Typer()


@app.command()
def summary():
    """领域概况统计"""
    from app.reporters.summary import run
    return run(settings.data_home)


@app.command()
def validate():
    """领域目录结构完整性验证"""
    from app.validators.validate import run
    return run(settings.data_home)


@app.command(name="find-undefined-terms")
def find_undefined_terms():
    """扫描源文档中出现的术语是否已定义"""
    from app.validators.find_undefined import run
    return run(settings.sample_home, settings.data_home)


@app.command(name="fusion-check")
def fusion_check():
    """跨领域融合检测（名称冲突、引用断裂、效力声明）"""
    from app.validators.fusion_check import run
    return run(settings.data_home, settings.sample_home)


@app.command(name="check-abstraction")
def check_abstraction():
    """本体抽象度检测"""
    from app.reporters.abstraction import run
    return run(settings.data_home)


@app.command(name="auto-fix")
def auto_fix():
    """骨架文件自动补全"""
    from app.validators.auto_fix import run
    return run(settings.data_home)


@app.command(name="cross-domain-report")
def cross_domain_report():
    """跨领域关系覆盖率报告"""
    from app.reporters.cross_domain import run
    return run(settings.data_home)


@app.command()
def detect_domain(
    filepath: str = typer.Argument(..., help="要检测的文件路径"),
):
    """推荐所属领域"""
    from app.detectors.detect_domain import run
    return run(filepath, settings.data_home)


@app.command(name="init-domain")
def init_domain(
    domain_name: str = typer.Argument(..., help="新领域名称"),
    from_detect: str = typer.Option(None, "--from-detect", help="从检测结果文件初始化"),
):
    """初始化新领域目录和骨架文件"""
    from app.detectors.init_domain import run
    return run(domain_name, from_detect_file=from_detect)


def main():
    return app()

if __name__ == "__main__":
    exit(main())
