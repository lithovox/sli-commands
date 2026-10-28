from pathlib import Path

import pytest

from conftest import BJERRUM_NEN, DATA, KOPPEJAN_VEEN, SLI_FILES
from settlement.sli import SliError, SliFile

SOIL_NAMES = [
    "V [11,0 - 12,0] <300",
    "V [10,0 - 10,8] 300-500",
    "V [10,0 - 10,8] >500",
    "K [<13,5]",
    "K [13,5 - 15,0]",
    "K [15,0 - 17,0]",
    "K [>17,0]",
    "Z [18,0]",
    "PL [19,0]",
]


@pytest.mark.parametrize("path", SLI_FILES, ids=lambda p: p.name)
def test_roundtrip_is_byte_identical(path, tmp_path):
    out = tmp_path / "out.sli"
    SliFile.read(path).write(out)
    assert out.read_bytes() == path.read_bytes()


def test_soils_are_parsed_in_order():
    sli = SliFile.read(DATA / KOPPEJAN_VEEN)
    assert [s.name for s in sli.soils] == SOIL_NAMES


def test_get_soil_value():
    sli = SliFile.read(DATA / BJERRUM_NEN)
    assert sli.get_soil_value(sli.soils[0], "SoilCa") == "0.0160000"
    assert sli.get_soil_value(sli.soils[0], "SoilEquivalentAge") == "1.25E+05"


def test_set_soil_value_only_changes_that_line():
    sli = SliFile.read(DATA / KOPPEJAN_VEEN)
    before = list(sli.lines)
    sli.set_soil_value(sli.soils[3], "SoilOCR", "2.00")
    changed = [i for i, (a, b) in enumerate(zip(before, sli.lines)) if a != b]
    assert changed == [sli.soils[3].keys["SoilOCR"]]
    assert sli.lines[changed[0]] == "SoilOCR=2.00"


def test_unknown_soil_parameter_raises():
    sli = SliFile.read(DATA / KOPPEJAN_VEEN)
    with pytest.raises(SliError, match="SoilDoesNotExist"):
        sli.get_soil_value(sli.soils[0], "SoilDoesNotExist")


def test_model_options():
    sli = SliFile.read(DATA / KOPPEJAN_VEEN)
    assert sli.get_model_option("Model") == "NEN - Koppejan"
    assert sli.get_model_option("Calculation type") == "Terzaghi"
    assert sli.get_model_option("Strain type") == "Natural"

    sli.set_model_option("Model", 1, "NEN - Bjerrum")
    assert sli.get_model_option("Model") == "NEN - Bjerrum"
    assert "1 : Model = NEN - Bjerrum" in sli.lines


def test_unknown_model_option_raises():
    sli = SliFile.read(DATA / KOPPEJAN_VEEN)
    with pytest.raises(SliError, match="Nonsense"):
        sli.get_model_option("Nonsense")


def test_set_filename():
    sli = SliFile.read(DATA / KOPPEJAN_VEEN)
    sli.set_filename(Path("/some/dir/out.bj.sli"))
    assert "FILENAME   : /some/dir/out.bj.sli" in sli.lines


def test_missing_soil_collection_raises():
    with pytest.raises(SliError, match="SOIL COLLECTION"):
        SliFile(["[MODEL]", "[END OF MODEL]"])
