"""工具定义 — 将 CLI 命令封装为可调用工具。"""

from pathlib import Path
from app.config import settings
from app.loader import load_all_domains


def run_validate(data_dir=None):
    from app.validators.validate import run
    return run(data_dir)


def run_fusion_check(data_dir=None, sample_dir=None):
    from app.validators.fusion_check import run
    return run(data_dir or settings.data_home, sample_dir or settings.sample_home)


def run_find_undefined(sample_dir=None, data_dir=None):
    from app.validators.find_undefined import run
    return run(sample_dir or settings.sample_home, data_dir or settings.data_home)


def run_check_abstraction(data_dir=None):
    from app.reporters.abstraction import run
    return run(data_dir)


def run_cross_domain_report(data_dir=None):
    from app.reporters.cross_domain import run
    return run(data_dir)


def run_summary(data_dir=None):
    from app.reporters.summary import run
    return run(data_dir)


def run_auto_fix(data_dir=None):
    from app.validators.auto_fix import run
    return run(data_dir)


def run_detect_domain(filepath, data_dir=None):
    from app.detectors.detect_domain import run
    return run(filepath, data_dir or settings.data_home)


def run_init_domain(domain_name, from_detect_file=None):
    from app.detectors.init_domain import run
    return run(domain_name, from_detect_file)


STRUCTURAL_TOOLS = [
    ("validate", "领域目录结构完整性验证", run_validate),
    ("find-undefined-terms", "扫描源文档中未定义术语", run_find_undefined),
    ("fusion-check", "跨领域融合检测（名称冲突、引用断裂）", run_fusion_check),
]
QUALITY_TOOLS = [
    ("check-abstraction", "本体抽象度检测", run_check_abstraction),
    ("cross-domain-report", "跨领域关系覆盖率报告", run_cross_domain_report),
]


def all_detection_tools(mode="full"):
    tools = list(STRUCTURAL_TOOLS)
    if mode == "full":
        tools += QUALITY_TOOLS
    return tools
