from pathlib import Path

import pytest

from conftest import BJERRUM, FIXTURES, KOPPEJAN, SLI_FILES
from settlement.sli import SliError, SliFile

SOIL_NAMES = [
    "Peat A",
    "Peat B",
    "Peat C",
    "Clay A",
    "Clay, silty",
    "Clay, sandy",
    "Clay [D]",
    "Sand",
    "Sand, deep",
]


@pytest.mark.parametrize("path", SLI_FILES, ids=lambda p: p.name)
def test_roundtrip_is_byte_identical(path, tmp_path):
    out = tmp_path / "out.sli"
    SliFile.read(path).write(out)
    assert out.read_bytes() == path.read_bytes()


def test_soils_are_parsed_in_order():
    sli = SliFile.read(FIXTURES / KOPPEJAN)
    assert [s.name for s in sli.soils] == SOIL_NAMES


def test_get_soil_value():
    sli = SliFile.read(FIXTURES / BJERRUM)
    assert sli.get_soil_value(sli.soils[0], "SoilCa") == "0.0170000"
    assert sli.get_soil_value(sli.soils[0], "SoilOCR") == "2.00"


def test_set_soil_value_only_changes_that_line():
    sli = SliFile.read(FIXTURES / KOPPEJAN)
    before = list(sli.lines)
    sli.set_soil_value(sli.soils[3], "SoilOCR", "2.00")
    changed = [i for i, (a, b) in enumerate(zip(before, sli.lines)) if a != b]
    assert changed == [sli.soils[3].keys["SoilOCR"]]
    assert sli.lines[changed[0]] == "SoilOCR=2.00"


def test_unknown_soil_parameter_raises():
    sli = SliFile.read(FIXTURES / KOPPEJAN)
    with pytest.raises(SliError, match="SoilDoesNotExist"):
        sli.get_soil_value(sli.soils[0], "SoilDoesNotExist")


def test_model_options():
    sli = SliFile.read(FIXTURES / KOPPEJAN)
    assert sli.get_model_option("Model") == "NEN - Koppejan"
    assert sli.get_model_option("Calculation type") == "Terzaghi"
    assert sli.get_model_option("Strain type") == "Natural"

    sli.set_model_option("Model", 1, "NEN - Bjerrum")
    assert sli.get_model_option("Model") == "NEN - Bjerrum"
    assert "1 : Model = NEN - Bjerrum" in sli.lines


def test_unknown_model_option_raises():
    sli = SliFile.read(FIXTURES / KOPPEJAN)
    with pytest.raises(SliError, match="Nonsense"):
        sli.get_model_option("Nonsense")


def test_set_filename():
    sli = SliFile.read(FIXTURES / KOPPEJAN)
    sli.set_filename(Path("/some/dir/out.bj.sli"))
    assert "FILENAME   : /some/dir/out.bj.sli" in sli.lines


def test_missing_soil_collection_raises():
    with pytest.raises(SliError, match="SOIL COLLECTION"):
        SliFile(["[MODEL]", "[END OF MODEL]"])
