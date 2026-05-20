"""配置管理。

通过 `Settings` 读取环境变量，提供运行时路径。

    >>> from app.config import settings
    >>> isinstance(settings.data_home, Path)
    True
"""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from quanttide import LocalStorage


class Settings(BaseSettings):
    model_config = {"env_prefix": "QTCLOUD_KNOWL_"}

    data_home: Path = LocalStorage("qtcloud-knowl", vendor="quanttide").data_dir
    sample_home: Optional[Path] = None


settings = Settings()
