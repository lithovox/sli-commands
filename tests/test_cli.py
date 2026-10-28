import sys
import tomllib

import pytest

from conftest import BJERRUM, KOPPEJAN, ROOT, SOILS_CSV, UNKNOWN_SOIL
from settlement import cli
from settlement.sli import SliFile


def run(monkeypatch, command, *args) -> int:
    monkeypatch.setattr(sys, "argv", [command.__name__, *map(str, args)])
    return command()


def test_kj2bj_writes_output(monkeypatch, capsys, copy_sli):
    source = copy_sli(KOPPEJAN)
    assert run(monkeypatch, cli.kj2bj, source, SOILS_CSV) == 0

    target = source.with_name("koppejan.bj.sli")
    assert target.is_file()
    assert SliFile.read(target).get_model_option("Model") == "NEN - Bjerrum"
    assert f"FILENAME   : {target.resolve()}" in SliFile.read(target).lines

    out, err = capsys.readouterr()
    assert str(target) in out
    assert err.count("kj2bj: warning:") == 2


def test_output_keeps_crlf_line_endings(monkeypatch, copy_sli):
    source = copy_sli(KOPPEJAN)
    run(monkeypatch, cli.kj2bj, source, SOILS_CSV)
    data = source.with_name("koppejan.bj.sli").read_bytes()
    assert data.count(b"\n") == data.count(b"\r\n")


def test_bj2kj_writes_output(monkeypatch, capsys, copy_sli):
    source = copy_sli(BJERRUM)
    assert run(monkeypatch, cli.bj2kj, source, SOILS_CSV) == 0
    target = source.with_name("bjerrum.kj.sli")
    assert SliFile.read(target).get_model_option("Model") == "NEN - Koppejan"
    assert capsys.readouterr().err == ""


def test_existing_output_is_overwritten(monkeypatch, copy_sli):
    source = copy_sli(KOPPEJAN)
    target = source.with_name("koppejan.bj.sli")
    target.write_text("old")
    assert run(monkeypatch, cli.kj2bj, source, SOILS_CSV) == 0
    assert target.read_text(encoding="latin-1").startswith("INPUT FILE FOR D-SETTLEMENT")


def test_wrong_model_writes_nothing(monkeypatch, capsys, copy_sli):
    source = copy_sli(BJERRUM)
    assert run(monkeypatch, cli.kj2bj, source, SOILS_CSV) == 1
    assert list(source.parent.glob("*.bj.sli")) == []
    assert "kj2bj: error: expected a NEN - Koppejan calculation" in capsys.readouterr().err


def test_missing_soils_write_nothing(monkeypatch, capsys, unknown_soil_sli):
    assert run(monkeypatch, cli.kj2bj, unknown_soil_sli, SOILS_CSV) == 1
    assert list(unknown_soil_sli.parent.glob("*.bj.sli")) == []
    assert f"  - {UNKNOWN_SOIL}" in capsys.readouterr().err


def test_invalid_soils_file(monkeypatch, capsys, copy_sli, write_csv):
    source = copy_sli(KOPPEJAN)
    assert run(monkeypatch, cli.kj2bj, source, write_csv("code;yd\n")) == 1
    assert "missing column(s): ys" in capsys.readouterr().err


@pytest.mark.parametrize("missing", ["calculation", "soils"])
def test_file_not_found(monkeypatch, capsys, copy_sli, tmp_path, missing):
    source = copy_sli(KOPPEJAN)
    args = {"calculation": (tmp_path / "nope.sli", SOILS_CSV), "soils": (source, tmp_path / "nope.csv")}
    assert run(monkeypatch, cli.kj2bj, *args[missing]) == 1
    assert "file not found" in capsys.readouterr().err


@pytest.mark.parametrize("command", [cli.kj2bj, cli.bj2kj])
def test_version(monkeypatch, capsys, command):
    expected = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    with pytest.raises(SystemExit) as e:
        run(monkeypatch, command, "--version")
    assert e.value.code == 0
    assert capsys.readouterr().out == f"{command.__name__} {expected}\n"


def test_wrong_number_of_arguments(monkeypatch, capsys):
    with pytest.raises(SystemExit) as e:
        run(monkeypatch, cli.bj2kj, "only_one.sli")
    assert e.value.code == 2
    assert "usage: bj2kj" in capsys.readouterr().err
