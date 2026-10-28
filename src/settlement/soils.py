"""Reading the soils parameter list (.csv, ';' separated)."""

import csv
from pathlib import Path

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

    def __init__(self, path: Path, problems: list[str]):
        self.problems = problems
        super().__init__(
            f"invalid soils file '{path}':\n" + "\n".join(f"  - {p}" for p in problems)
        )


def read_soils(path: Path) -> dict[str, dict[str, float]]:
    """Returns soil code -> {csv column: value}."""
    # utf-8-sig handles the byte order mark Excel adds
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        header = [h.strip() for h in reader.fieldnames or []]
        missing = [c for c in [CODE_COLUMN, *COLUMNS] if c not in header]
        if missing:
            raise SoilsFileError(path, [f"missing column(s): {', '.join(missing)}"])
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
        raise SoilsFileError(path, problems)
    return soils
