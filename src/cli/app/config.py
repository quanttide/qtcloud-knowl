import os
from pathlib import Path

from quanttide import LocalStorage

BASE_DIR = Path(__file__).resolve().parent.parent

_env_data_dir = os.environ.get("KNOWL_DATA_DIR")
if _env_data_dir:
    DATA_DIR = Path(_env_data_dir)
else:
    DATA_DIR = LocalStorage("qtcloud-knowl", vendor="quanttide").data_dir

FIXTURE_DIR = BASE_DIR / "tests" / "fixtures" / "output"
SAMPLE_DIR = BASE_DIR / "tests" / "fixtures" / "input"
