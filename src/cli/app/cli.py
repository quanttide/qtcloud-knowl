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


@app.command(hidden=True)
def summary():
    """领域概况统计"""
    from app.reporters.summary import run
    return run(settings.data_home)


@app.command(hidden=True)
def validate():
    """领域目录结构完整性验证"""
    from app.validators.validate import run
    return run(settings.data_home)


@app.command(name="find-undefined-terms", hidden=True)
def find_undefined_terms():
    """扫描源文档中出现的术语是否已定义"""
    from app.validators.find_undefined import run
    return run(settings.sample_home, settings.data_home)


@app.command(name="fusion-check", hidden=True)
def fusion_check():
    """跨领域融合检测（名称冲突、引用断裂、效力声明）"""
    from app.validators.fusion_check import run
    return run(settings.data_home, settings.sample_home)


@app.command(name="check-abstraction", hidden=True)
def check_abstraction():
    """本体抽象度检测"""
    from app.reporters.abstraction import run
    return run(settings.data_home)


@app.command(name="auto-fix", hidden=True)
def auto_fix():
    """骨架文件自动补全"""
    from app.validators.auto_fix import run
    return run(settings.data_home)


@app.command(name="cross-domain-report", hidden=True)
def cross_domain_report():
    """跨领域关系覆盖率报告"""
    from app.reporters.cross_domain import run
    return run(settings.data_home)


@app.command(hidden=True)
def detect_domain(
    filepath: str = typer.Argument(..., help="要检测的文件路径"),
):
    """推荐所属领域"""
    from app.detectors.detect_domain import run
    return run(filepath, settings.data_home)


@app.command(name="init-domain", hidden=True)
def init_domain(
    domain_name: str = typer.Argument(..., help="新领域名称"),
    from_detect: str = typer.Option(None, "--from-detect", help="从检测结果文件初始化"),
):
    """初始化新领域目录和骨架文件"""
    from app.detectors.init_domain import run
    return run(domain_name, from_detect_file=from_detect)


@app.command()
def audit(
    data_dir: str = typer.Argument(None, help="数据目录路径（默认从 settings 读取）"),
    sample_dir: str = typer.Option(None, "--sample-dir", help="源文件目录路径"),
    mode: str = typer.Option("full", "--mode", help="审计模式：simple（仅结构检查）/ full（含质量检测）"),
):
    """全量质量审计 — 串行执行全部检测并聚合报告"""
    from app.agents.audit import run
    return run(data_dir, sample_dir, mode)


@app.command()
def extract(
    sample_dir: str = typer.Argument(None, help="源文档目录路径（默认从 settings 读取）"),
    data_dir: str = typer.Option(None, "--data-dir", help="数据目录路径"),
):
    """知识抽取 — 从源文件自动抽取知识到知识库"""
    from app.agents.extract import run
    return run(sample_dir, data_dir)


def main():
    return app()

if __name__ == "__main__":
    exit(main())
