#!/usr/bin/env python3
"""知识工程智能体 — 统一 CLI 入口"""

import typer
from app.config import settings

app = typer.Typer()


@app.command()
def summary():
    """领域概况统计"""
    from app.reporters.summary import run
    return run(settings.data_home)


@app.command()
def validate(
    undefined: bool = typer.Option(False, "--undefined", help="扫描源文档未定义术语"),
    fusion: bool = typer.Option(False, "--fusion", help="跨领域融合检测"),
    abstraction: bool = typer.Option(False, "--abstraction", help="本体抽象度检测"),
):
    """领域目录完整性验证，可组合子检测"""
    result = 0
    from app.validators.validate import run as validate_run
    result |= validate_run(settings.data_home)

    if undefined:
        from app.validators.find_undefined import run as find_run
        result |= find_run(settings.sample_home, settings.data_home)

    if fusion:
        from app.validators.fusion_check import run as fusion_run
        result |= fusion_run(settings.data_home, settings.sample_home)

    if abstraction:
        from app.reporters.abstraction import run as abstraction_run
        result |= abstraction_run(settings.data_home)

    return result


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
