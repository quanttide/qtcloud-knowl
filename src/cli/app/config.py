from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings
from quanttide import LocalStorage

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    data_dir: Path = Field(
        default=LocalStorage("qtcloud-knowl", vendor="quanttide").data_dir,
        alias="QTCLOUD_KNOWL_DATA_HOME",
    )


settings = Settings()
DATA_DIR = settings.data_dir

FIXTURE_DIR = BASE_DIR / "tests" / "fixtures" / "output"
SAMPLE_DIR = BASE_DIR / "tests" / "fixtures" / "input"
