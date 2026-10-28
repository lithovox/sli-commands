"""Command line entry points kj2bj and bj2kj."""

import argparse
import sys
from collections.abc import Callable
from pathlib import Path

from settlement.convert import (
    ConversionError,
    bjerrum_to_koppejan,
    koppejan_to_bjerrum,
    output_path,
)
from settlement.sli import SliError, SliFile
from settlement.soils import SoilsFileError, read_soils


def _run(
    prog: str,
    description: str,
    convert: Callable[[SliFile, dict[str, dict[str, float]]], list[str]],
    suffix: str,
) -> int:
    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.add_argument("calculationfile", type=Path, help="D-Settlement input file (.sli)")
    parser.add_argument("soilsfile", type=Path, help="soil parameters (.csv, ';' separated)")
    args = parser.parse_args()

    for path in (args.calculationfile, args.soilsfile):
        if not path.is_file():
            print(f"{prog}: error: file not found: {path}", file=sys.stderr)
            return 1

    try:
        sli = SliFile.read(args.calculationfile)
        soils = read_soils(args.soilsfile)
        notices = convert(sli, soils)
        target = output_path(args.calculationfile, suffix)
        sli.set_filename(target.resolve())
        sli.write(target)
    except (SliError, SoilsFileError, ConversionError, OSError) as e:
        print(f"{prog}: error: {e}", file=sys.stderr)
        return 1

    for notice in notices:
        print(f"{prog}: warning: {notice}", file=sys.stderr)
    print(f"written {target}")
    return 0


def kj2bj() -> int:
    return _run(
        "kj2bj",
        "Convert a NEN-Koppejan D-Settlement calculation to NEN-Bjerrum.",
        koppejan_to_bjerrum,
        "bj",
    )


def bj2kj() -> int:
    return _run(
        "bj2kj",
        "Convert a NEN-Bjerrum D-Settlement calculation to NEN-Koppejan.",
        bjerrum_to_koppejan,
        "kj",
    )
