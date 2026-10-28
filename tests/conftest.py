import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
FIXTURES = Path(__file__).parent / "fixtures"
SOILS_CSV = ROOT / "examples" / "soils.csv"

# anonymised dummy calculations, bjerrum.sli is koppejan.sli converted by hand
KOPPEJAN = "koppejan.sli"
BJERRUM = "bjerrum.sli"
UNKNOWN_SOIL = "Unknown soil"

SLI_FILES = sorted(FIXTURES.glob("*.sli"))


@pytest.fixture
def copy_sli(tmp_path):
    """Copies a fixture to tmp_path so the tests never write in tests/fixtures."""

    def copy(name: str) -> Path:
        return Path(shutil.copy(FIXTURES / name, tmp_path / name))

    return copy


@pytest.fixture
def unknown_soil_sli(tmp_path):
    """koppejan.sli with its first soil renamed to a code that is not in soils.csv."""
    text = (FIXTURES / KOPPEJAN).read_bytes().decode("latin-1")
    path = tmp_path / "unknown.sli"
    path.write_bytes(text.replace("[SOIL]\r\nPeat A\r\n", f"[SOIL]\r\n{UNKNOWN_SOIL}\r\n").encode("latin-1"))
    return path


@pytest.fixture
def write_csv(tmp_path):
    def write(text: str, name: str = "soils.csv", encoding: str = "utf-8") -> Path:
        path = tmp_path / name
        path.write_text(text, encoding=encoding)
        return path

    return write
