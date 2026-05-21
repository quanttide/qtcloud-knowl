"""集成测试共享夹具 — 使用 tests/fixtures/ 的真实数据。"""

import shutil
import sys
from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "output"
SAMPLE_DIR = Path(__file__).resolve().parent / "fixtures" / "input"


def setup_env(monkeypatch, *, data_home, sample_dir=None, api_key="", state_home=None):
    """设置环境变量 → 创建 Settings → 注入所有已加载 app 模块。

    不重载模块，只替换模块的 .settings 属性（from app.config import settings
    在 consumer 模块中创建了 module.settings 引用，直接替换即可）。
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

    new_settings = config.Settings()
    config.settings = new_settings
    for mod_name in list(sys.modules.keys()):
        if mod_name.startswith("app."):
            sys.modules[mod_name].settings = new_settings

    import app.cli as cli_mod
    return cli_mod.app


@pytest.fixture
def real_sample_dir():
    return SAMPLE_DIR


@pytest.fixture
def real_knowledge_base(tmp_path):
    dest = tmp_path / "kbase"
    shutil.copytree(FIXTURE_DIR, dest)
    return dest
