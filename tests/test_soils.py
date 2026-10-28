import pytest

from conftest import SOILS_CSV
from settlement.soils import COLUMNS, SoilsFileError, read_soils

HEADER = "code;" + ";".join(COLUMNS)
ROW = "K [<13,5];13.00;13.00;4.02E+01;9.58E+00;2.87E+02;6.98E+01;0.102;0.307;0.015;10.00;2.00;1.02E-06;4.00E-03"


def test_read_assets_soils_csv():
    soils = read_soils(SOILS_CSV)
    assert len(soils) == 9
    peat = soils["V [11,0 - 12,0] <300"]
    assert set(peat) == set(COLUMNS)
    assert peat["calpha"] == 0.016
    assert peat["ocr"] == 2.5
    assert peat["k"] == 0.015


def test_code_with_commas_and_whitespace(write_csv):
    soils = read_soils(write_csv(f"{HEADER}\n  {ROW.replace(';', ' ;', 1)}\n"))
    assert list(soils) == ["K [<13,5]"]


def test_decimal_comma(write_csv):
    soils = read_soils(write_csv(f"{HEADER}\n{ROW.replace('0.102', '0,102')}\n"))
    assert soils["K [<13,5]"]["rr"] == 0.102


def test_byte_order_mark(write_csv):
    soils = read_soils(write_csv(f"{HEADER}\n{ROW}\n", encoding="utf-8-sig"))
    assert "K [<13,5]" in soils


def test_empty_lines_are_skipped(write_csv):
    soils = read_soils(write_csv(f"{HEADER}\n{ROW}\n;\n\n"))
    assert len(soils) == 1


def test_missing_column(write_csv):
    header = HEADER.replace(";k", "")
    with pytest.raises(SoilsFileError) as e:
        read_soils(write_csv(f"{header}\n{ROW}\n"))
    assert e.value.problems == ["missing column(s): k"]


def test_all_value_problems_are_reported(write_csv):
    bad_empty = ROW.replace(";4.02E+01;", ";;")
    bad_text = ROW.replace("K [<13,5]", "Z [18,0]").replace(";0.015;", ";abc;")
    with pytest.raises(SoilsFileError) as e:
        read_soils(write_csv(f"{HEADER}\n{bad_empty}\n{bad_text}\n{ROW}\n"))
    assert e.value.problems == [
        "'K [<13,5]': invalid value '' for column 'cp'",
        "'Z [18,0]': invalid value 'abc' for column 'calpha'",
        "duplicate soil code 'K [<13,5]'",
    ]
