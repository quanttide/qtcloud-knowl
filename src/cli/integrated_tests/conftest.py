"""集成测试共享夹具 — 使用真实 LLM API 和 gallery fixture 数据。"""

import sys
from pathlib import Path

import pytest

# 确保 app 模块可导入（integrated_tests/ 是 cli/ 的子目录）
CLI_ROOT = Path(__file__).resolve().parent.parent
if str(CLI_ROOT) not in sys.path:
    sys.path.insert(0, str(CLI_ROOT))

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def info_path():
    return FIXTURE_DIR / "information" / "code-refactor.md"


@pytest.fixture
def knowledge_path():
    return FIXTURE_DIR / "knowledge" / "code-refactor.json"
