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
    mode: str = typer.Option("full", "--mode", help="审计模式：simple（快速检查）/ full（全面审计）"),
):
    """全量质量审计 — 串行执行全部检测并聚合报告"""
    from app.agents.audit import run
    return run(data_dir, sample_dir, mode)


@app.command()
def source(
    action: str = typer.Argument("list", help="操作：download / list / remove"),
    name: str = typer.Option(None, "--name", "-n", help="源文档名称（download / remove 时必填）"),
):
    """管理源文档 — 下载、列出、清理"""
    from app.source import SOURCES, download, download_all, list_sources, remove, remove_all

    if action == "list":
        downloaded = list_sources()
        if not downloaded:
            print("未下载任何源文档。可用:")
            for k, v in SOURCES.items():
                print(f"  {k}: {v['desc']}")
            print("\n运行 qtcloud-knowl source download --name <名称> 下载")
            return
        print("已下载的源文档:")
        for d in downloaded:
            print(f"  {d}")
        print(f"\n共 {len(downloaded)} 项")

    elif action == "download":
        if name:
            result = download(name)
            print(result)
        else:
            print("可用源文档:")
            for k, v in SOURCES.items():
                print(f"  {k}: {v['desc']}")
            print("\n指定名称下载: qtcloud-knowl source download --name qtcloud-bylaw")

    elif action == "remove":
        if name:
            result = remove(name)
            print(result)
        else:
            results = remove_all()
            for r in results:
                print(r)


@app.command()
def review(
    action: str = typer.Argument("list", help="操作：list / approve / reject / reset"),
    item_id: str = typer.Option(None, "--id", help="条目 ID（如 biz-ops:ontology:o1）"),
    domain: str = typer.Option(None, "--domain", help="按领域过滤"),
    reason: str = typer.Option("", "--reason", help="拒绝原因（仅 reject）"),
    pending: bool = typer.Option(False, "--pending", help="仅显示待审项（仅 list）"),
):
    """评审知识条目 — 批量通过/拒绝，查看评审状态"""
    from app.review import list_items, approve_item, approve_all, reject_item, reset_reviews

    if action == "list":
        items = list_items(domain_filter=domain, pending_only=pending)
        if not items:
            print("没有符合条件的条目。")
            return
        print(f"{'领域':<12} {'类型':<8} {'ID/名称':<24} {'状态':<8} {'备注'}")
        print(f"{'─'*12} {'─'*8} {'─'*24} {'─'*8} {'─'*20}")
        for item in items:
            print(f"{item['domain']:<12} {item['type']:<8} {item['label'][:24]:<24} {item['status']:<8} {item['comment']}")
        total = len(items)
        pending_count = sum(1 for i in items if i["status"] == "待评审")
        print(f"\n共 {total} 项，{pending_count} 项待评审")

    elif action == "approve":
        if item_id:
            approve_item(item_id)
            print(f"已通过：{item_id}")
        else:
            n = approve_all()
            print(f"已全部通过：{n} 项")

    elif action == "reject":
        if not item_id:
            print("错误：--id 为必填（如 --id biz-ops:ontology:o1）")
            raise typer.Exit(1)
        reject_item(item_id, reason)
        print(f"已拒绝：{item_id}" + (f" 原因：{reason}" if reason else ""))

    elif action == "reset":
        reset_reviews()
        print("评审记录已重置。")


@app.command()
def extract(
    sample_dir: str = typer.Argument(None, help="源文档目录路径（默认从 settings 读取）"),
    data_dir: str = typer.Option(None, "--data-dir", help="数据目录路径"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="显示详细匹配信息"),
    llm: str = typer.Option(None, "--llm", help="对指定文档运行 LLM 抽取（传文件路径）"),
):
    """知识抽取 — 从源文件自动创建知识库骨架"""
    from app.agents.extract import extract_with_llm, run

    if llm:
        if not settings.llm_api_key:
            print("错误: 未设置 QTCLOUD_KNOWL_LLM_API_KEY")
            raise typer.Exit(code=1)
        result = extract_with_llm(llm)
        print(result)
        return

    return run(sample_dir, data_dir, verbose)


def main():
    return app()

if __name__ == "__main__":
    exit(main())
