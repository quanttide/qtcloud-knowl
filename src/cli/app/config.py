from pathlib import Path

from pydantic_settings import BaseSettings
from quanttide import LocalStorage

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = {"env_prefix": "QTCLOUD_KNOWL_"}

    data_home: Path = LocalStorage("qtcloud-knowl", vendor="quanttide").data_dir


settings = Settings()
SAMPLE_DIR = BASE_DIR / "tests" / "fixtures" / "input"
