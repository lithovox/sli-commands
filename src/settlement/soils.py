"""Reading and writing the soils parameter list (.csv, ';' separated)."""

import csv
import io
from pathlib import Path

from settlement.sli import SliError, SliFile

CODE_COLUMN = "code"

# csv column -> D-Settlement soil parameter
COLUMNS = {
    "yd": "SoilGamDry",
    "ys": "SoilGamWet",
    "cp": "SoilCp",
    "cap": "SoilCp1",
    "cs": "SoilCs",
    "cas": "SoilCs1",
    "rr": "SoilRRatio",
    "cr": "SoilCRatio",
    "calpha": "SoilCa",
    "pop": "SoilPOP",
    "ocr": "SoilOCR",
    "cv": "SoilCv",
    "k": "SoilPermeabilityVer",
}


class SoilsFileError(Exception):
    """Raised when the soils file is invalid, holds all problems found."""

    def __init__(self, name: str | Path, problems: list[str]):
        self.problems = problems
        super().__init__(
            f"invalid soils file '{name}':\n" + "\n".join(f"  - {p}" for p in problems)
        )


def read_soils(path: Path) -> dict[str, dict[str, float]]:
    """Returns soil code -> {csv column: value}."""
    return parse_soils(path.read_bytes(), path)


def parse_soils(data: bytes, name: str | Path = "soils file") -> dict[str, dict[str, float]]:
    """Like read_soils, for the contents of the file, name is only used in errors."""
    # utf-8-sig handles the byte order mark Excel adds
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""), delimiter=";")
    header = [h.strip() for h in reader.fieldnames or []]
    missing = [c for c in [CODE_COLUMN, *COLUMNS] if c not in header]
    if missing:
        raise SoilsFileError(name, [f"missing column(s): {', '.join(missing)}"])
    reader.fieldnames = header

    soils = {}
    problems = []
    for row in reader:
        code = (row[CODE_COLUMN] or "").strip()
        if not code:
            continue
        if code in soils:
            problems.append(f"duplicate soil code '{code}'")
            continue
        values = {}
        for column in COLUMNS:
            raw = (row[column] or "").strip()
            try:
                values[column] = float(raw.replace(",", "."))
            except ValueError:
                problems.append(f"'{code}': invalid value '{raw}' for column '{column}'")
        soils[code] = values

    if problems:
        raise SoilsFileError(name, problems)
    return soils


def soil_parameters(sli: SliFile) -> list[list[str]]:
    """The soils of a calculation as rows of the soils file, header first, values as written in the file."""
    rows = [[CODE_COLUMN, *COLUMNS]]
    for soil in sli.soils:
        if ";" in soil.name:
            raise SliError(f"soil name '{soil.name}' contains ';', the separator of the soils file")
        rows.append([soil.name, *(sli.get_soil_value(soil, key) for key in COLUMNS.values())])
    return rows
