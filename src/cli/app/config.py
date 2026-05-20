from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from quanttide import LocalStorage


class Settings(BaseSettings):
    model_config = {"env_prefix": "QTCLOUD_KNOWL_"}

    data_home: Path = LocalStorage("qtcloud-knowl", vendor="quanttide").data_dir
    sample_home: Optional[Path] = None


settings = Settings()
