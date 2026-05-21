"""集成测试共享夹具 — 使用 tests/fixtures/ 的真实数据。"""

import shutil
from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "output"
SAMPLE_DIR = Path(__file__).resolve().parent / "fixtures" / "input"


@pytest.fixture
def real_sample_dir():
    """返回 tests/fixtures/input/，包含 10 份真实样本文档。"""
    return SAMPLE_DIR


@pytest.fixture
def real_knowledge_base(tmp_path):
    """复制真实领域数据到临时目录，避免测试写操作污染原 fixture。"""
    dest = tmp_path / "kbase"
    shutil.copytree(FIXTURE_DIR, dest)
    return dest
