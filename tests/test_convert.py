from pathlib import Path

import pytest

from conftest import BJERRUM_AGV, BJERRUM_NEN, DATA, KOPPEJAN_VEEN, SOILS_CSV, UNKNOWN_SOIL
from settlement.convert import (
    FORMATS,
    ConversionError,
    bjerrum_to_koppejan,
    equivalent_age,
    koppejan_to_bjerrum,
    output_path,
)
from settlement.sli import SliFile
from settlement.soils import COLUMNS, read_soils


@pytest.fixture(scope="module")
def soils():
    return read_soils(SOILS_CSV)


def soil_values(sli: SliFile, keys) -> dict[str, dict[str, str]]:
    return {s.name: {k: sli.get_soil_value(s, k) for k in keys} for s in sli.soils}


@pytest.mark.parametrize("name", [BJERRUM_NEN, BJERRUM_AGV])
def test_equivalent_age_matches_d_settlement(name):
    sli = SliFile.read(DATA / name)
    for soil in sli.soils:
        value = lambda key: float(sli.get_soil_value(soil, key))
        age = equivalent_age(value("SoilOCR"), value("SoilRRatio"), value("SoilCRatio"), value("SoilCa"))
        assert FORMATS["SoilEquivalentAge"].format(age) == sli.get_soil_value(soil, "SoilEquivalentAge")


def test_equivalent_age_without_creep():
    assert equivalent_age(ocr=1.3, rr=0.001, cr=0.003, calpha=0.0) == 1.0


@pytest.mark.parametrize(
    "name, suffix, expected",
    [
        ("a.sli", "bj", "a.bj.sli"),
        ("a.kj.sli", "bj", "a.bj.sli"),
        ("a.bj.sli", "kj", "a.kj.sli"),
        ("a.KJ.sli", "bj", "a.bj.sli"),
        ("a.b.sli", "kj", "a.b.kj.sli"),
        ("Proevenverzameling 2019 (x).sli", "bj", "Proevenverzameling 2019 (x).bj.sli"),
    ],
)
def test_output_path(name, suffix, expected):
    assert output_path(Path("dir") / name, suffix) == Path("dir") / expected


def test_koppejan_to_bjerrum_matches_reference(soils):
    sli = SliFile.read(DATA / KOPPEJAN_VEEN)
    notices = koppejan_to_bjerrum(sli, soils)
    reference = SliFile.read(DATA / BJERRUM_NEN)

    for option in ("Model", "Calculation type", "Strain type"):
        assert sli.get_model_option(option) == reference.get_model_option(option)
    assert len(notices) == 2

    # the reference still has the placeholder permeability, k is checked separately
    keys = [k for k in COLUMNS.values() if k != "SoilPermeabilityVer"] + ["SoilEquivalentAge"]
    assert soil_values(sli, keys) == soil_values(reference, keys)


def test_all_csv_values_are_written(soils):
    sli = SliFile.read(DATA / KOPPEJAN_VEEN)
    koppejan_to_bjerrum(sli, soils)
    for soil in sli.soils:
        for column, key in COLUMNS.items():
            assert float(sli.get_soil_value(soil, key)) == pytest.approx(soils[soil.name][column], rel=1e-2)


def test_koppejan_to_bjerrum_keeps_ap_as(soils):
    sli = SliFile.read(DATA / KOPPEJAN_VEEN)
    keys = ["SoilApAsApproximationByCpCs", "SoilAp", "SoilAsec"]
    before = soil_values(sli, keys)
    koppejan_to_bjerrum(sli, soils)
    assert soil_values(sli, keys) == before


def test_koppejan_to_bjerrum_with_darcy_and_linear_has_no_notices(soils):
    sli = SliFile.read(DATA / KOPPEJAN_VEEN)
    sli.set_model_option("Calculation type", 0, "Darcy")
    sli.set_model_option("Strain type", 0, "Linear")
    assert koppejan_to_bjerrum(sli, soils) == []


def test_bjerrum_to_koppejan(soils):
    sli = SliFile.read(DATA / BJERRUM_AGV)
    before = soil_values(sli, ["SoilAp", "SoilAsec"])
    notices = bjerrum_to_koppejan(sli, soils)

    assert sli.get_model_option("Model") == "NEN - Koppejan"
    assert sli.get_model_option("Calculation type") == "Darcy"
    assert sli.get_model_option("Strain type") == "Linear"
    assert notices == []
    assert all(sli.get_soil_value(s, "SoilApAsApproximationByCpCs") == "1" for s in sli.soils)
    assert soil_values(sli, ["SoilAp", "SoilAsec"]) == before
    # the Bjerrum parameters now come from the NEN values in soils.csv
    assert sli.get_soil_value(sli.soils[0], "SoilCa") == "0.0160000"


def test_bjerrum_to_koppejan_warns_about_terzaghi(soils):
    sli = SliFile.read(DATA / BJERRUM_NEN)
    sli.set_model_option("Calculation type", 1, "Terzaghi")
    notices = bjerrum_to_koppejan(sli, soils)
    assert sli.get_model_option("Calculation type") == "Terzaghi"
    assert len(notices) == 1 and "Darcy is preferred" in notices[0]


@pytest.mark.parametrize(
    "convert, name", [(koppejan_to_bjerrum, BJERRUM_NEN), (bjerrum_to_koppejan, KOPPEJAN_VEEN)]
)
def test_wrong_input_model_is_refused(convert, name, soils):
    sli = SliFile.read(DATA / name)
    before = list(sli.lines)
    with pytest.raises(ConversionError, match="expected a"):
        convert(sli, soils)
    assert sli.lines == before


def test_missing_soils_are_listed(soils):
    sli = SliFile.read(DATA / UNKNOWN_SOIL)
    with pytest.raises(ConversionError) as e:
        koppejan_to_bjerrum(sli, soils)
    assert e.value.problems == ["1 soil(s) not found in the soils file:", "  - V [10,0 - 10,8] <300"]


def test_equivalent_age_overflow_is_reported(soils):
    sli = SliFile.read(DATA / KOPPEJAN_VEEN)
    extreme = {code: dict(values) for code, values in soils.items()}
    extreme["K [<13,5]"]["calpha"] = 1e-6
    with pytest.raises(ConversionError, match="'K \\[<13,5\\]': equivalent age too large"):
        koppejan_to_bjerrum(sli, extreme)
