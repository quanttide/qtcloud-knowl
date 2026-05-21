from quanttide_agent import Tool
import io
import sys
from typing import Callable


def _capture(fn: Callable[[], None]) -> str:
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        fn()
    except Exception as e:
        buf.write(f"执行错误: {e}")
    finally:
        sys.stdout = old
    return buf.getvalue()


def _validate(inp: dict) -> str:
    from app.validators.validate import run
    return _capture(lambda: run(inp.get("data_dir")))


def _fusion_check(inp: dict) -> str:
    from app.validators.fusion_check import run
    return _capture(lambda: run(inp.get("data_dir"), inp.get("sample_dir")))


def _find_undefined(inp: dict) -> str:
    from app.validators.find_undefined import run
    return _capture(lambda: run(inp.get("sample_dir"), inp.get("data_dir")))


def _check_abstraction(inp: dict) -> str:
    from app.reporters.abstraction import run
    return _capture(lambda: run(inp.get("data_dir")))


def _cross_domain_report(inp: dict) -> str:
    from app.reporters.cross_domain import run
    return _capture(lambda: run(inp.get("data_dir")))


STRUCTURAL_TOOLS = [
    Tool(name="validate", description="领域目录结构完整性验证", executor=_validate),
    Tool(name="find-undefined-terms", description="扫描源文档中未定义术语", executor=_find_undefined),
    Tool(name="fusion-check", description="跨领域融合检测（名称冲突、引用断裂）", executor=_fusion_check),
]

QUALITY_TOOLS = [
    Tool(name="check-abstraction", description="本体抽象度检测", executor=_check_abstraction),
    Tool(name="cross-domain-report", description="跨领域关系覆盖率报告", executor=_cross_domain_report),
]


def all_detection_tools(mode: str = "full") -> list[Tool]:
    tools = list(STRUCTURAL_TOOLS)
    if mode == "full":
        tools += QUALITY_TOOLS
    return tools
