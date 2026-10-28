import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
SOILS_CSV = ROOT / "assets" / "soils.csv"

KOPPEJAN_VEEN = "Proevenverzameling 2019 Koppejan veen.sli"
KOPPEJAN_DARCY = "Proevenverzameling 2019 Koppejan.sli"
BJERRUM_NEN = "Proevenverzameling 2019 NEN Bjerrum veen (NEN waarden).sli"
BJERRUM_AGV = "Proevenverzameling 2019 NEN Bjerrum veen (voorstel AGV).sli"
# contains soil 'V [10,0 - 10,8] <300' which is not in soils.csv
UNKNOWN_SOIL = "Proevenverzameling 2019.sli"

SLI_FILES = sorted(DATA.glob("*.sli"))


@pytest.fixture
def copy_sli(tmp_path):
    """Copies a data file to tmp_path so the tests never write in data/."""

    def copy(name: str) -> Path:
        return Path(shutil.copy(DATA / name, tmp_path / name))

    return copy


@pytest.fixture
def write_csv(tmp_path):
    def write(text: str, name: str = "soils.csv", encoding: str = "utf-8") -> Path:
        path = tmp_path / name
        path.write_text(text, encoding=encoding)
        return path

    return write
