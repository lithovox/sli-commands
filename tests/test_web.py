import json

import pytest

from conftest import BJERRUM, FIXTURES, KOPPEJAN, SOILS_CSV
from settlement.sli import SliFile
from settlement.web import dispatch


def call(function, *args, files=()):
    result, data = dispatch(function, list(args), [*files])
    return json.loads(result), data


def read(name):
    return (FIXTURES / name).read_bytes()


def test_inspect_calculation():
    result, data = call("inspect_calculation", files=[read(KOPPEJAN)])
    assert result["ok"] and data is None
    assert result["result"]["model"] == "NEN - Koppejan"
    assert result["result"]["action"] == "kj2bj"
    assert result["result"]["calculation_type"] == "Terzaghi"
    assert result["result"]["soils"][:2] == ["Peat A", "Peat B"]


def test_soils_table():
    result, _ = call("soils_table", files=[SOILS_CSV.read_bytes()])
    table = result["result"]
    assert table["header"] == ["code", "yd", "ys", "cp", "cap", "cs", "cas", "rr", "cr", "calpha", "pop", "ocr", "cv", "k"]
    assert len(table["rows"]) == 9
    # values as written in the file
    assert table["rows"][0][:3] == ["Peat A", "10.5", "10.5"]
    assert table["problems"] == []


def test_soils_table_in_another_column_order():
    csv = b"k;code;yd;ys;cp;cap;cs;cas;rr;cr;calpha;pop;ocr;cv\n1E-3;Sand ;18;20;1;1;1;1;0.1;0.3;0;0;1;1\n"
    table = call("soils_table", files=[csv])[0]["result"]
    assert table["rows"] == [["Sand", "18", "20", "1", "1", "1", "1", "0.1", "0.3", "0", "0", "1", "1", "1E-3"]]


def test_soils_table_keeps_rows_with_problems():
    csv = SOILS_CSV.read_bytes().replace(b";0.017;", b";abc;")
    result, _ = call("soils_table", files=[csv])
    assert result["ok"]
    assert len(result["result"]["rows"]) == 9
    assert result["result"]["rows"][0][9] == "abc"
    assert result["result"]["problems"] == ["'Peat A': invalid value 'abc' for column 'calpha'"]


@pytest.mark.parametrize("name, action, target", [(KOPPEJAN, "kj2bj", "koppejan.bj.sli"), (BJERRUM, "bj2kj", "bjerrum.kj.sli")])
def test_convert_detects_the_direction(name, action, target):
    result, data = call("convert_calculation", name, files=[read(name), SOILS_CSV.read_bytes()])
    assert result["ok"]
    assert result["result"]["action"] == action
    assert result["result"]["name"] == target
    assert "data" not in result["result"]
    assert f"FILENAME   : {target}" in SliFile.from_bytes(data).lines


def test_convert_gives_the_same_file_as_the_command_line(monkeypatch, copy_sli):
    from settlement import cli

    source = copy_sli(KOPPEJAN)
    monkeypatch.setattr("sys.argv", ["slicmd", "-kj2bj", str(source), str(SOILS_CSV)])
    cli.main()
    expected = SliFile.read(source.with_name("koppejan.bj.sli"))

    _, data = call("convert_calculation", KOPPEJAN, files=[read(KOPPEJAN), SOILS_CSV.read_bytes()])
    converted = SliFile.from_bytes(data)
    # only the FILENAME line differs, the command line writes the full path
    differences = [(a, b) for a, b in zip(converted.lines, expected.lines) if a != b]
    assert len(converted.lines) == len(expected.lines)
    assert [a for a, _ in differences] == ["FILENAME   : koppejan.bj.sli"]


def test_convert_with_missing_soil_returns_the_problems():
    csv = SOILS_CSV.read_bytes().replace(b"Peat A;", b"Other;")
    result, data = call("convert_calculation", KOPPEJAN, files=[read(KOPPEJAN), csv])
    assert not result["ok"] and data is None
    assert result["problems"] == ["1 soil(s) not found in the soils file:", "  - Peat A"]


def test_invalid_soils_file_returns_the_problems():
    result, _ = call("soils_table", files=[b"code;yd\n"])
    assert not result["ok"]
    assert result["problems"][0].startswith("missing column(s): ys")


def test_parameters():
    result, _ = call("parameters", files=[read(KOPPEJAN)])
    parameters = result["result"]
    assert parameters["header"][:3] == ["code", "yd", "ys"]
    assert parameters["rows"][0][0] == "Peat A"
    assert parameters["csv"].splitlines()[0] == "code;yd;ys;cp;cap;cs;cas;rr;cr;calpha;pop;ocr;cv;k"
    # Koppejan calculation: rr, cr and calpha hold the placeholder 1.0 for all 9 soils
    assert len(parameters["placeholders"]) == 27
    assert [0, parameters["header"].index("rr")] in parameters["placeholders"]


def test_parameters_without_placeholders():
    result, _ = call("parameters", files=[read(BJERRUM)])
    assert result["result"]["placeholders"] == []


def test_results():
    result, _ = call("results", files=[read("terzaghi.sld")])
    verticals = result["result"]["verticals"]
    assert [(v["number"], v["x"], v["z"]) for v in verticals] == [(1, 5.0, 0.0), (2, 15.0, 0.0)]
    assert verticals[1]["series"][1] == [0.1, 0.02]


def test_results_of_an_input_file():
    result, _ = call("results", files=[read(KOPPEJAN)])
    assert not result["ok"]
    assert "no results found" in result["error"]


def test_not_a_calculation():
    result, _ = call("inspect_calculation", files=[b"just some text"])
    assert not result["ok"]
    assert result["error"] == "section [SOIL COLLECTION] not found"
