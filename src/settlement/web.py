"""Functions for the web application.

The browser runs this package with Pyodide and has no file paths, so these
functions work on file contents (bytes). dispatch() is the single entry point:
it returns JSON for the result and, for a converted calculation, the bytes of
the new file separately.
"""

import csv
import io
import json
from pathlib import Path

from settlement.convert import (
    BJERRUM,
    KOPPEJAN,
    ConversionError,
    bjerrum_to_koppejan,
    koppejan_to_bjerrum,
    output_path,
)
from settlement.sld import SldError, time_settlement, verticals
from settlement.sli import SliError, SliFile
from settlement.soils import CODE_COLUMN, COLUMNS, SoilsFileError, parse_soils, soil_parameters

# model -> (action, conversion, suffix of the output file)
CONVERSIONS = {
    KOPPEJAN: ("kj2bj", koppejan_to_bjerrum, "bj"),
    BJERRUM: ("bj2kj", bjerrum_to_koppejan, "kj"),
}

# columns that hold the D-Settlement placeholder 1.0 until the Bjerrum parameters are filled in
BJERRUM_COLUMNS = ("rr", "cr", "calpha")


def inspect_calculation(data: bytes) -> dict:
    sli = SliFile.from_bytes(data)
    model = sli.get_model_option("Model")
    return {
        "model": model,
        "action": CONVERSIONS[model][0] if model in CONVERSIONS else None,
        "calculation_type": sli.get_model_option("Calculation type"),
        "strain_type": sli.get_model_option("Strain type"),
        "soils": [soil.name for soil in sli.soils],
    }


def soils_table(soils_csv: bytes) -> dict:
    """The rows of a soils file as written, for editing, and the problems that stop a conversion.

    Unlike parse_soils this also returns rows with invalid values, so they can be corrected.
    """
    rows = list(csv.reader(io.StringIO(soils_csv.decode("utf-8-sig"), newline=""), delimiter=";"))
    header = [h.strip() for h in rows[0]] if rows else []
    columns = [CODE_COLUMN, *COLUMNS]
    missing = [c for c in columns if c not in header]
    if missing:
        raise SoilsFileError("soils file", [f"missing column(s): {', '.join(missing)}"])
    positions = [header.index(c) for c in columns]
    table = [
        [row[i].strip() if i < len(row) else "" for i in positions]
        for row in rows[1:]
        if any(cell.strip() for cell in row)
    ]
    try:
        parse_soils(soils_csv)
        problems = []
    except SoilsFileError as e:
        problems = e.problems
    return {"header": columns, "rows": table, "problems": problems}


def convert_calculation(name: str, data: bytes, soils_csv: bytes) -> dict:
    """Converts to the other model, the new file is returned under "data"."""
    sli = SliFile.from_bytes(data)
    model = sli.get_model_option("Model")
    if model not in CONVERSIONS:
        raise ConversionError([f"model {model} cannot be converted"])
    action, convert, suffix = CONVERSIONS[model]
    notices = convert(sli, parse_soils(soils_csv))
    target = output_path(Path(name), suffix).name
    # there is no local path in the browser, the header gets the file name only
    sli.set_filename(Path(target))
    return {"action": action, "name": target, "notices": notices, "data": sli.to_bytes()}


def parameters(data: bytes) -> dict:
    rows = soil_parameters(SliFile.from_bytes(data))
    header = rows[0]
    placeholders = [
        [r, header.index(column)]
        for r, row in enumerate(rows[1:])
        for column in BJERRUM_COLUMNS
        if float(row[header.index(column)]) == 1.0
    ]
    return {
        "header": header,
        "rows": rows[1:],
        "placeholders": placeholders,
        "csv": "".join(";".join(row) + "\n" for row in rows),
    }


def results(data: bytes) -> dict:
    """The time-settlement curve of every vertical in a .sld file."""
    return {
        "verticals": [
            {"number": number, "x": x, "z": z, "series": time_settlement(data, number)}
            for number, x, z in verticals(data)
        ]
    }


FUNCTIONS = {
    "inspect_calculation": inspect_calculation,
    "soils_table": soils_table,
    "convert_calculation": convert_calculation,
    "parameters": parameters,
    "results": results,
}

KNOWN_ERRORS = (SliError, SoilsFileError, ConversionError, SldError, UnicodeDecodeError)


def dispatch(function: str, args: list, files: list[bytes]) -> tuple[str, bytes | None]:
    """Calls FUNCTIONS[function](*args, *files).

    Returns the JSON {"ok": true, "result": ...} or {"ok": false, "error": ..., "problems": [...]}
    and the bytes of a converted file, if any.
    """
    try:
        result = FUNCTIONS[function](*args, *files)
    except KNOWN_ERRORS as e:
        problems = getattr(e, "problems", None)
        return json.dumps({"ok": False, "error": str(e), "problems": problems}), None
    data = result.pop("data", None) if isinstance(result, dict) else None
    return json.dumps({"ok": True, "result": result}), data
