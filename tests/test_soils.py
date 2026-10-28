import pytest

from conftest import SOILS_CSV
from settlement.soils import COLUMNS, SoilsFileError, read_soils

HEADER = "code;" + ";".join(COLUMNS)
ROW = "Clay, silty;14.50;14.50;5.00E+01;1.10E+01;4.00E+02;1.20E+02;0.06;0.2;0.01;10.00;1.80;5.00E-07;1.00E-03"


def test_read_example_soils_csv():
    soils = read_soils(SOILS_CSV)
    assert len(soils) == 9
    peat = soils["Peat A"]
    assert set(peat) == set(COLUMNS)
    assert peat["calpha"] == 0.017
    assert peat["ocr"] == 2.0
    assert peat["k"] == 0.01


def test_code_with_commas_and_whitespace(write_csv):
    soils = read_soils(write_csv(f"{HEADER}\n  {ROW.replace(';', ' ;', 1)}\n"))
    assert list(soils) == ["Clay, silty"]


def test_decimal_comma(write_csv):
    soils = read_soils(write_csv(f"{HEADER}\n{ROW.replace(';0.06;', ';0,06;')}\n"))
    assert soils["Clay, silty"]["rr"] == 0.06


def test_byte_order_mark(write_csv):
    soils = read_soils(write_csv(f"{HEADER}\n{ROW}\n", encoding="utf-8-sig"))
    assert "Clay, silty" in soils


def test_empty_lines_are_skipped(write_csv):
    soils = read_soils(write_csv(f"{HEADER}\n{ROW}\n;\n\n"))
    assert len(soils) == 1


def test_missing_column(write_csv):
    header = HEADER.replace(";k", "")
    with pytest.raises(SoilsFileError) as e:
        read_soils(write_csv(f"{header}\n{ROW}\n"))
    assert e.value.problems == ["missing column(s): k"]


def test_all_value_problems_are_reported(write_csv):
    bad_empty = ROW.replace(";5.00E+01;", ";;")
    bad_text = ROW.replace("Clay, silty", "Sand").replace(";0.01;", ";abc;")
    with pytest.raises(SoilsFileError) as e:
        read_soils(write_csv(f"{HEADER}\n{bad_empty}\n{bad_text}\n{ROW}\n"))
    assert e.value.problems == [
        "'Clay, silty': invalid value '' for column 'cp'",
        "'Sand': invalid value 'abc' for column 'calpha'",
        "duplicate soil code 'Clay, silty'",
    ]
