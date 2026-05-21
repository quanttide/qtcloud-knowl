from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


_PREFIX = "QTCLOUD_KNOWL_"


def _env_path(key: str, default: Path | None = None) -> Path | None:
    v = os.environ.get(key)
    return Path(v) if v else default


@dataclass
class Settings:
    data_home: Path | None = None
    state_home: Path | None = None
    sample_home: Path | None = None
    source_home: Path | None = None
    llm_api_key: str = ""
    llm_model: str = "deepseek-chat"
    llm_base_url: str = ""

    def __post_init__(self):
        self.reload_from_env()

    def reload_from_env(self):
        self.data_home = _env_path(_PREFIX + "DATA_HOME") or Path.home() / ".local/share/quanttide/qtcloud-knowl"
        self.state_home = _env_path(_PREFIX + "STATE_HOME") or Path.home() / ".local/state/quanttide/qtcloud-knowl"
        self.sample_home = _env_path(_PREFIX + "SAMPLE_HOME") or self.data_home / "samples"
        self.source_home = _env_path(_PREFIX + "SOURCE_HOME") or self.data_home / "sources"
        self.llm_api_key = os.environ.get(_PREFIX + "LLM_API_KEY", "")
        self.llm_model = os.environ.get(_PREFIX + "LLM_MODEL", "deepseek-chat")
        self.llm_base_url = os.environ.get(_PREFIX + "LLM_BASE_URL", "")


settings = Settings()
