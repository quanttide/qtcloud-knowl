#!/usr/bin/env python3
"""领域概况统计"""

import argparse
from pathlib import Path
from app.config import settings
from qtcloud_knowl.loader import load_all_domains


def run(data_dir=None):
    base = Path(data_dir) if data_dir else settings.data_home
    domains = load_all_domains(base)
    if not domains:
        print("未找到领域数据")
        return 1

    print(f"{'领域':<24} {'本体':<10} {'实例':<10} {'关系':<10} {'文件数':<10}")
    print("-" * 64)
    for d, domain, ontologies, instances, relations in domains:
        n_ont = len(ontologies)
        n_inst = len(instances)
        n_rel = len(relations)
        n_files = len(domain.files)
        print(f"{domain.id:<24} {n_ont:<10} {n_inst:<10} {n_rel:<10} {n_files:<10}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="领域概况统计")
    parser.add_argument("data_dir", nargs="?", default=settings.data_home, help="data 目录路径")
    args = parser.parse_args()
    exit(run(args.data_dir))


if __name__ == "__main__":  # pragma: no cover
    main()
