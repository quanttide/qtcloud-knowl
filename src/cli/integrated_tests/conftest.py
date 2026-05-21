"""集成测试共享夹具 — 使用 tests/fixtures/ 的真实数据。"""

import importlib
import shutil
from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "output"
SAMPLE_DIR = Path(__file__).resolve().parent / "fixtures" / "input"


def setup_env(monkeypatch, *, data_home, sample_dir=None, api_key="", state_home=None):
    """统一环境设置：设环境变量 → 重载模块 → 返回 app。

    所有集成测试使用此函数而非各自定义 _setup。
    """
    if state_home is None:
        state_home = data_home

    monkeypatch.setenv("QTCLOUD_KNOWL_DATA_HOME", str(data_home))
    monkeypatch.setenv("QTCLOUD_KNOWL_STATE_HOME", str(state_home))
    if sample_dir is not None:
        monkeypatch.setenv("QTCLOUD_KNOWL_SAMPLE_HOME", str(sample_dir))
    if api_key:
        monkeypatch.setenv("QTCLOUD_KNOWL_LLM_API_KEY", api_key)

    from app import config
    importlib.reload(config)
    import app.reviewers.data as rdata
    import app.review as rmod
    importlib.reload(rdata)
    importlib.reload(rmod)
    import app.cli as cli_mod
    importlib.reload(cli_mod)
    return cli_mod.app


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
