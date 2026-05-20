from pathlib import Path

from quanttide import LocalStorage

BASE_DIR = Path(__file__).resolve().parent.parent

store = LocalStorage("qtcloud-knowl", vendor="quanttide")
DATA_DIR = store.data_dir

FIXTURE_DIR = BASE_DIR / "tests" / "fixtures" / "output"
SAMPLE_DIR = BASE_DIR / "tests" / "fixtures" / "input"
