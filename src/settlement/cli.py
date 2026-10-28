"""Command line entry point slicmd."""

import argparse
import glob
import sys
from collections.abc import Callable
from pathlib import Path

from settlement import __version__
from settlement.convert import (
    ConversionError,
    bjerrum_to_koppejan,
    koppejan_to_bjerrum,
    output_path,
)
from settlement.sld import SldError, read_time_settlement
from settlement.sli import SliError, SliFile
from settlement.soils import SoilsFileError, read_soils, soil_parameters

Soils = dict[str, dict[str, float]]

PROG = "slicmd"

# action -> (conversion, suffix of the output files, help text)
ACTIONS = {
    "kj2bj": (koppejan_to_bjerrum, "bj", "convert NEN-Koppejan calculations to NEN-Bjerrum (.bj.sli)"),
    "bj2kj": (bjerrum_to_koppejan, "kj", "convert NEN-Bjerrum calculations to NEN-Koppejan (.kj.sli)"),
}

GLOB_CHARACTERS = "*?["


def _expand(patterns: list[str]) -> tuple[list[Path], list[str]]:
    """Expands wildcards, returns the files and the patterns that matched nothing.

    Shells on Linux and macOS expand wildcards themselves, cmd and PowerShell
    on Windows do not, so patterns are expanded here as well.
    """
    files: dict[Path, Path] = {}
    unmatched = []
    for pattern in patterns:
        path = Path(pattern)
        if path.is_file():
            matches = [path]
        elif any(c in pattern for c in GLOB_CHARACTERS):
            matches = [Path(p) for p in sorted(glob.glob(pattern, recursive=True)) if Path(p).is_file()]
        else:
            matches = []
        if not matches:
            unmatched.append(pattern)
        for match in matches:
            files.setdefault(match.resolve(), match)
    return list(files.values()), unmatched


def _convert_file(source: Path, soils: Soils, convert: Callable[[SliFile, Soils], list[str]], suffix: str) -> bool:
    try:
        sli = SliFile.read(source)
        notices = convert(sli, soils)
        target = output_path(source, suffix)
        sli.set_filename(target.resolve())
        sli.write(target)
    except (SliError, ConversionError, OSError) as e:
        print(f"{PROG}: error: {source}: {e}", file=sys.stderr)
        return False

    for notice in notices:
        print(f"{PROG}: warning: {source}: {notice}", file=sys.stderr)
    print(f"written {target}", flush=True)
    return True


def _info(sld: Path, vertical: int) -> int:
    if not sld.is_file():
        print(f"{PROG}: error: file not found: {sld}", file=sys.stderr)
        return 1
    try:
        series = read_time_settlement(sld, vertical)
    except (SldError, OSError) as e:
        print(f"{PROG}: error: {sld}: {e}", file=sys.stderr)
        return 1

    print("time [days]\tsettlement [m]")
    for time, settlement in series:
        print(f"{time:.7f}\t{settlement:.7f}")
    return 0


def _parameters(sli_path: Path) -> int:
    """Prints the soils of a calculation in the format of the soils file."""
    if not sli_path.is_file():
        print(f"{PROG}: error: file not found: {sli_path}", file=sys.stderr)
        return 1
    try:
        rows = soil_parameters(SliFile.read(sli_path))
    except (SliError, OSError) as e:
        print(f"{PROG}: error: {sli_path}: {e}", file=sys.stderr)
        return 1

    for row in rows:
        print(";".join(row))
    return 0


def _convert(patterns: list[str], soilsfile: Path, action: str) -> int:
    convert, suffix, _ = ACTIONS[action]

    if not soilsfile.is_file():
        print(f"{PROG}: error: file not found: {soilsfile}", file=sys.stderr)
        return 1
    try:
        soils = read_soils(soilsfile)
    except (SoilsFileError, OSError) as e:
        print(f"{PROG}: error: {e}", file=sys.stderr)
        return 1

    files, unmatched = _expand(patterns)
    for pattern in unmatched:
        print(f"{PROG}: error: file not found: {pattern}", file=sys.stderr)

    converted = failed = 0
    for source in files:
        # earlier output of this command, e.g. picked up again by *.sli
        if source.name.lower().endswith(f".{suffix}.sli"):
            print(f"{PROG}: skipped {source}, this is already a converted file", flush=True)
            continue
        if _convert_file(source, soils, convert, suffix):
            converted += 1
        else:
            failed += 1

    if len(files) > 1 or unmatched:
        print(f"{PROG}: {converted} file(s) converted, {failed + len(unmatched)} failed")
    return 1 if failed or unmatched or not converted else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Convert D-Settlement calculations (.sli) between NEN-Koppejan and NEN-Bjerrum, "
        "show the soil parameters of a calculation, or the time-settlement curve of a vertical (.sld).",
        # otherwise -kj2bj could be read as an abbreviation
        allow_abbrev=False,
    )
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    actions = parser.add_mutually_exclusive_group(required=True)
    for name, (_, _, help) in ACTIONS.items():
        actions.add_argument(f"-{name}", f"--{name}", dest="action", action="store_const", const=name, help=help)
    actions.add_argument(
        "-i", "--info", type=Path, metavar="SLD", help="show time and settlement of a vertical from a .sld file"
    )
    actions.add_argument(
        "-p",
        "--parameters",
        type=Path,
        metavar="SLI",
        help="show the soil parameters of a .sli file in the format of the soils file",
    )
    parser.add_argument(
        "-vt", "--vertical", type=int, help="vertical number for -i, the first vertical is 1 (default 1)"
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="file",
        help="for -kj2bj and -bj2kj: the D-Settlement input files (.sli), wildcards like *.sli "
        "or **/*.sli are allowed, followed by the soils file (.csv, ';' separated)",
    )
    args = parser.parse_args()

    if args.info:
        if args.files:
            parser.error("-i takes a single .sld file")
        return _info(args.info, args.vertical or 1)

    if args.vertical is not None:
        parser.error("-vt can only be used with -i")

    if args.parameters:
        if args.files:
            parser.error("-p takes a single .sli file")
        return _parameters(args.parameters)

    if len(args.files) < 2:
        parser.error(f"-{args.action} needs one or more calculation files followed by a soils file")
    return _convert(args.files[:-1], Path(args.files[-1]), args.action)
