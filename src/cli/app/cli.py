from __future__ import annotations

import argparse
import sys
from app.config import settings


def cmd_summary(args):
    from app.reporters.summary import run
    return run(settings.data_home) or 0


def cmd_validate(args):
    from app.validators.validate import run
    return 0 if run(settings.data_home) else 1


def cmd_find_undefined_terms(args):
    from app.validators.find_undefined import run
    run(settings.sample_home, settings.data_home)
    return 0


def cmd_fusion_check(args):
    from app.validators.fusion_check import run
    return run(settings.data_home, settings.sample_home) or 0


def cmd_check_abstraction(args):
    from app.reporters.abstraction import run
    run(settings.data_home)
    return 0


def cmd_auto_fix(args):
    from app.validators.auto_fix import run
    return run(settings.data_home) or 0


def cmd_cross_domain_report(args):
    from app.reporters.cross_domain import run
    return run(settings.data_home) or 0


def cmd_detect_domain(args):
    from app.detectors.detect_domain import run
    return run(args.filepath, settings.data_home) or 0


def cmd_init_domain(args):
    from app.detectors.init_domain import run
    run(args.domain_name, from_detect_file=args.from_detect)
    return 0


def cmd_audit(args):
    from app.agents.audit import run
    return run(args.data_dir, args.sample_dir, args.mode) or 0


def cmd_source(args):
    from app.source import SOURCES, download, download_all, list_sources, remove, remove_all

    if args.action == "list":
        downloaded = list_sources()
        if not downloaded:
            print("未下载任何源文档。可用:")
            for k, v in SOURCES.items():
                print(f"  {k}: {v['desc']}")
            print("\n运行 qtcloud-knowl source download --name <名称> 下载")
            return 0
        print("已下载的源文档:")
        for d in downloaded:
            print(f"  {d}")
        print(f"\n共 {len(downloaded)} 项")

    elif args.action == "download":
        if args.name:
            result = download(args.name)
            print(result)
        else:
            print("可用源文档:")
            for k, v in SOURCES.items():
                print(f"  {k}: {v['desc']}")
            print("\n指定名称下载: qtcloud-knowl source download --name qtcloud-bylaw")

    elif args.action == "remove":
        if args.name:
            result = remove(args.name)
            print(result)
        else:
            results = remove_all()
            for r in results:
                print(r)
    return 0


def cmd_review(args):
    from app.review import list_items, approve_item, approve_all, reject_item, reset_reviews

    if args.action == "list":
        items = list_items(domain_filter=args.domain, pending_only=args.pending)
        if not items:
            print("没有符合条件的条目。")
            return 0
        print(f"{'领域':<12} {'类型':<8} {'ID/名称':<24} {'状态':<8} {'备注'}")
        print(f"{'─'*12} {'─'*8} {'─'*24} {'─'*8} {'─'*20}")
        for item in items:
            print(f"{item['domain']:<12} {item['type']:<8} {item['label'][:24]:<24} {item['status']:<8} {item['comment']}")
        total = len(items)
        pending_count = sum(1 for i in items if i["status"] == "待评审")
        print(f"\n共 {total} 项，{pending_count} 项待评审")

    elif args.action == "approve":
        if args.id:
            approve_item(args.id)
            print(f"已通过：{args.id}")
        else:
            n = approve_all()
            print(f"已全部通过：{n} 项")

    elif args.action == "reject":
        if not args.id:
            print("错误：--id 为必填（如 --id biz-ops:ontology:o1）")
            sys.exit(1)
        reject_item(args.id, args.reason)
        print(f"已拒绝：{args.id}" + (f" 原因：{args.reason}" if args.reason else ""))

    elif args.action == "reset":
        reset_reviews()
        print("评审记录已重置。")
    return 0


def cmd_extract(args):
    from app.agents.extract import extract_with_llm, run

    if args.llm:
        if not settings.llm_api_key:
            print("错误: 未设置 QTCLOUD_KNOWL_LLM_API_KEY")
            sys.exit(1)
        result = extract_with_llm(args.llm)
        print(result)
        return 0

    return run(args.sample_dir, args.data_dir, args.verbose) or 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qtcloud-knowl", description="知识工程智能体 — 统一 CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("summary", help="领域概况统计")
    p.set_defaults(func=cmd_summary)

    p = sub.add_parser("validate", help="领域目录结构完整性验证")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("find-undefined-terms", help="扫描源文档中未定义术语")
    p.set_defaults(func=cmd_find_undefined_terms)

    p = sub.add_parser("fusion-check", help="跨领域融合检测")
    p.set_defaults(func=cmd_fusion_check)

    p = sub.add_parser("check-abstraction", help="本体抽象度检测")
    p.set_defaults(func=cmd_check_abstraction)

    p = sub.add_parser("auto-fix", help="骨架文件自动补全")
    p.set_defaults(func=cmd_auto_fix)

    p = sub.add_parser("cross-domain-report", help="跨领域关系覆盖率报告")
    p.set_defaults(func=cmd_cross_domain_report)

    p = sub.add_parser("detect-domain", help="推荐所属领域")
    p.add_argument("filepath", help="要检测的文件路径")
    p.set_defaults(func=cmd_detect_domain)

    p = sub.add_parser("init-domain", help="初始化新领域目录和骨架文件")
    p.add_argument("domain_name", help="新领域名称")
    p.add_argument("--from-detect", help="从检测结果文件初始化")
    p.set_defaults(func=cmd_init_domain)

    p = sub.add_parser("audit", help="全量质量审计")
    p.add_argument("data_dir", nargs="?", default=None, help="数据目录路径")
    p.add_argument("--sample-dir", default=None, help="源文件目录路径")
    p.add_argument("--mode", default="full", choices=("simple", "full"), help="审计模式")
    p.set_defaults(func=cmd_audit)

    p = sub.add_parser("source", help="管理源文档")
    p.add_argument("action", nargs="?", default="list", choices=("list", "download", "remove"), help="操作")
    p.add_argument("--name", "-n", default=None, help="源文档名称")
    p.set_defaults(func=cmd_source)

    p = sub.add_parser("review", help="评审知识条目")
    p.add_argument("action", nargs="?", default="list", choices=("list", "approve", "reject", "reset"), help="操作")
    p.add_argument("--id", default=None, help="条目 ID")
    p.add_argument("--domain", default=None, help="按领域过滤")
    p.add_argument("--reason", default="", help="拒绝原因")
    p.add_argument("--pending", action="store_true", help="仅显示待审项")
    p.set_defaults(func=cmd_review)

    p = sub.add_parser("extract", help="知识抽取")
    p.add_argument("sample_dir", nargs="?", default=None, help="源文档目录路径")
    p.add_argument("--data-dir", default=None, help="数据目录路径")
    p.add_argument("--verbose", "-v", action="store_true", help="显示详细匹配信息")
    p.add_argument("--llm", default=None, help="对指定文档运行 LLM 抽取")
    p.set_defaults(func=cmd_extract)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
