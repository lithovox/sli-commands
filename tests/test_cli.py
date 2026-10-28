import shutil
import sys
import tomllib
from pathlib import Path

import pytest

from conftest import BJERRUM, FIXTURES, KOPPEJAN, ROOT, SOILS_CSV, UNKNOWN_SOIL
from settlement import cli
from settlement.sli import SliFile


def run(monkeypatch, *args) -> int:
    monkeypatch.setattr(sys, "argv", ["slicmd", *map(str, args)])
    return cli.main()


def test_kj2bj_writes_output(monkeypatch, capsys, copy_sli):
    source = copy_sli(KOPPEJAN)
    assert run(monkeypatch, "-kj2bj", source, SOILS_CSV) == 0

    target = source.with_name("koppejan.bj.sli")
    assert target.is_file()
    assert SliFile.read(target).get_model_option("Model") == "NEN - Bjerrum"
    assert f"FILENAME   : {target.resolve()}" in SliFile.read(target).lines

    out, err = capsys.readouterr()
    assert str(target) in out
    assert err.count("slicmd: warning:") == 2


def test_output_keeps_crlf_line_endings(monkeypatch, copy_sli):
    source = copy_sli(KOPPEJAN)
    run(monkeypatch, "-kj2bj", source, SOILS_CSV)
    data = source.with_name("koppejan.bj.sli").read_bytes()
    assert data.count(b"\n") == data.count(b"\r\n")


def test_bj2kj_writes_output(monkeypatch, capsys, copy_sli):
    source = copy_sli(BJERRUM)
    assert run(monkeypatch, "-bj2kj", source, SOILS_CSV) == 0
    target = source.with_name("bjerrum.kj.sli")
    assert SliFile.read(target).get_model_option("Model") == "NEN - Koppejan"
    assert capsys.readouterr().err == ""


def test_existing_output_is_overwritten(monkeypatch, copy_sli):
    source = copy_sli(KOPPEJAN)
    target = source.with_name("koppejan.bj.sli")
    target.write_text("old")
    assert run(monkeypatch, "-kj2bj", source, SOILS_CSV) == 0
    assert target.read_text(encoding="latin-1").startswith("INPUT FILE FOR D-SETTLEMENT")


def test_wrong_model_writes_nothing(monkeypatch, capsys, copy_sli):
    source = copy_sli(BJERRUM)
    assert run(monkeypatch, "-kj2bj", source, SOILS_CSV) == 1
    assert list(source.parent.glob("*.bj.sli")) == []
    assert f"slicmd: error: {source}: expected a NEN - Koppejan calculation" in capsys.readouterr().err


def test_missing_soils_write_nothing(monkeypatch, capsys, unknown_soil_sli):
    assert run(monkeypatch, "-kj2bj", unknown_soil_sli, SOILS_CSV) == 1
    assert list(unknown_soil_sli.parent.glob("*.bj.sli")) == []
    assert f"  - {UNKNOWN_SOIL}" in capsys.readouterr().err


def test_invalid_soils_file(monkeypatch, capsys, copy_sli, write_csv):
    source = copy_sli(KOPPEJAN)
    assert run(monkeypatch, "-kj2bj", source, write_csv("code;yd\n")) == 1
    assert "missing column(s): ys" in capsys.readouterr().err


@pytest.mark.parametrize("missing", ["calculation", "soils"])
def test_file_not_found(monkeypatch, capsys, copy_sli, tmp_path, missing):
    source = copy_sli(KOPPEJAN)
    args = {"calculation": (tmp_path / "nope.sli", SOILS_CSV), "soils": (source, tmp_path / "nope.csv")}
    assert run(monkeypatch, "-kj2bj", *args[missing]) == 1
    assert "file not found" in capsys.readouterr().err


@pytest.mark.parametrize("flag", ["-v", "--version"])
def test_version(monkeypatch, capsys, flag):
    expected = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    with pytest.raises(SystemExit) as e:
        run(monkeypatch, flag)
    assert e.value.code == 0
    assert capsys.readouterr().out == f"slicmd {expected}\n"


def test_double_dash_action(monkeypatch, copy_sli):
    source = copy_sli(KOPPEJAN)
    assert run(monkeypatch, "--kj2bj", source, SOILS_CSV) == 0
    assert source.with_name("koppejan.bj.sli").is_file()


@pytest.mark.parametrize("actions", [[], ["-kj2bj", "-bj2kj"]], ids=["none", "both"])
def test_exactly_one_action_is_required(monkeypatch, capsys, copy_sli, actions):
    source = copy_sli(KOPPEJAN)
    with pytest.raises(SystemExit) as e:
        run(monkeypatch, *actions, source, SOILS_CSV)
    assert e.value.code == 2
    assert "-kj2bj" in capsys.readouterr().err
    assert list(source.parent.glob("*.bj.sli")) == []


def test_wrong_number_of_arguments(monkeypatch, capsys):
    with pytest.raises(SystemExit) as e:
        run(monkeypatch, "-bj2kj", "only_one.sli")
    assert e.value.code == 2
    assert "usage: slicmd" in capsys.readouterr().err


@pytest.fixture
def batch_dir(tmp_path):
    """A folder with two Koppejan calculations, one Bjerrum calculation and a subfolder."""
    folder = tmp_path / "batch"
    (folder / "sub").mkdir(parents=True)
    for name, fixture in [("a.sli", KOPPEJAN), ("b.sli", KOPPEJAN), ("c.sli", BJERRUM), ("sub/d.sli", KOPPEJAN)]:
        shutil.copy(FIXTURES / fixture, folder / name)
    return folder


def test_wildcard(monkeypatch, capsys, batch_dir):
    assert run(monkeypatch, "-kj2bj", batch_dir / "*.sli", SOILS_CSV) == 1
    assert sorted(p.name for p in batch_dir.glob("*.bj.sli")) == ["a.bj.sli", "b.bj.sli"]

    out, err = capsys.readouterr()
    assert f"slicmd: error: {batch_dir / 'c.sli'}: expected a NEN - Koppejan calculation" in err
    assert "slicmd: 2 file(s) converted, 1 failed" in out


def test_wildcard_skips_earlier_output(monkeypatch, capsys, batch_dir):
    pattern = batch_dir / "[ab].sli"
    assert run(monkeypatch, "-kj2bj", pattern, SOILS_CSV) == 0
    capsys.readouterr()

    assert run(monkeypatch, "-kj2bj", batch_dir / "[ab]*.sli", SOILS_CSV) == 0
    out = capsys.readouterr().out
    assert f"slicmd: skipped {batch_dir / 'a.bj.sli'}" in out
    assert "slicmd: 2 file(s) converted, 0 failed" in out


def test_recursive_wildcard(monkeypatch, batch_dir):
    assert run(monkeypatch, "-kj2bj", batch_dir / "**" / "d.sli", SOILS_CSV) == 0
    assert (batch_dir / "sub" / "d.bj.sli").is_file()


def test_several_files_as_expanded_by_the_shell(monkeypatch, capsys, batch_dir):
    files = [batch_dir / "a.sli", batch_dir / "b.sli", batch_dir / "a.sli"]
    assert run(monkeypatch, "-kj2bj", *files, SOILS_CSV) == 0
    # a.sli is given twice but converted once
    assert capsys.readouterr().out.count("written") == 2


def test_wildcard_without_matches(monkeypatch, capsys, batch_dir):
    pattern = batch_dir / "*.nothing"
    assert run(monkeypatch, "-kj2bj", pattern, batch_dir / "a.sli", SOILS_CSV) == 1
    out, err = capsys.readouterr()
    assert f"file not found: {pattern}" in err
    assert (batch_dir / "a.bj.sli").is_file()
    assert "slicmd: 1 file(s) converted, 1 failed" in out


def test_file_name_with_brackets_is_taken_literally(monkeypatch, tmp_path):
    source = Path(shutil.copy(FIXTURES / KOPPEJAN, tmp_path / "calc [1].sli"))
    assert run(monkeypatch, "-kj2bj", source, SOILS_CSV) == 0
    assert (tmp_path / "calc [1].bj.sli").is_file()


def test_invalid_soils_file_stops_the_batch(monkeypatch, batch_dir, write_csv):
    assert run(monkeypatch, "-kj2bj", batch_dir / "*.sli", write_csv("code;yd\n")) == 1
    assert list(batch_dir.glob("*.bj.sli")) == []


@pytest.mark.parametrize("flag", ["-vt", "--vertical"])
def test_info(monkeypatch, capsys, flag):
    assert run(monkeypatch, "-i", FIXTURES / "terzaghi.sld", flag, 2) == 0
    assert capsys.readouterr().out.splitlines() == [
        "time [days]\tsettlement [m]",
        "0.0000000\t0.0000000",
        "0.1000000\t0.0200000",
        "1.0000000\t0.0800000",
        "10.0000000\t0.2000000",
        "100.0000000\t0.2500000",
    ]


def test_info_uses_first_vertical_by_default(monkeypatch, capsys):
    assert run(monkeypatch, "--info", FIXTURES / "darcy.sld") == 0
    assert "0.1000000\t0.0123456" in capsys.readouterr().out


def test_info_unknown_vertical(monkeypatch, capsys):
    source = FIXTURES / "darcy.sld"
    assert run(monkeypatch, "-i", source, "-vt", 5) == 1
    assert f"slicmd: error: {source}: vertical 5 not found" in capsys.readouterr().err


def test_info_file_not_found(monkeypatch, capsys, tmp_path):
    assert run(monkeypatch, "-i", tmp_path / "nope.sld") == 1
    assert "file not found" in capsys.readouterr().err


@pytest.mark.parametrize(
    "args, message",
    [
        (["-i", "a.sld", "b.sli"], "-i takes a single .sld file"),
        (["-kj2bj", "-vt", "2", "a.sli", "b.csv"], "-vt can only be used with -i"),
        (["-kj2bj", "a.sli"], "-kj2bj needs one or more calculation files followed by a soils file"),
        (["-i", "a.sld", "-kj2bj"], "not allowed with argument"),
        (["-i", "a.sld", "-vt", "x"], "invalid int value"),
    ],
)
def test_invalid_arguments(monkeypatch, capsys, args, message):
    with pytest.raises(SystemExit) as e:
        run(monkeypatch, *args)
    assert e.value.code == 2
    assert message in capsys.readouterr().err
