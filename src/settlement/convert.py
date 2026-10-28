"""Conversion between the NEN-Koppejan and NEN-Bjerrum models of D-Settlement."""

import re
from pathlib import Path

from settlement.sli import SliFile
from settlement.soils import COLUMNS

KOPPEJAN = "NEN - Koppejan"
BJERRUM = "NEN - Bjerrum"

# option values and their index as used in the [MODEL] section
MODELS = {KOPPEJAN: 0, BJERRUM: 1}
DARCY, TERZAGHI = "Darcy", "Terzaghi"
CALCULATION_TYPES = {DARCY: 0, TERZAGHI: 1}
LINEAR, NATURAL = "Linear", "Natural"
STRAIN_TYPES = {LINEAR: 0, NATURAL: 1}

# number format per parameter, matching the format D-Settlement writes
FORMATS = {
    "SoilGamDry": "{:.2f}",
    "SoilGamWet": "{:.2f}",
    "SoilCp": "{:.2E}",
    "SoilCp1": "{:.2E}",
    "SoilCs": "{:.2E}",
    "SoilCs1": "{:.2E}",
    "SoilRRatio": "{:.7f}",
    "SoilCRatio": "{:.7f}",
    "SoilCa": "{:.7f}",
    "SoilPOP": "{:.2f}",
    "SoilOCR": "{:.2f}",
    "SoilCv": "{:.2E}",
    "SoilPermeabilityVer": "{:.3E}",
    "SoilEquivalentAge": "{:.2E}",
}


class ConversionError(Exception):
    """Raised when a file cannot be converted, holds all problems found."""

    def __init__(self, problems: list[str]):
        self.problems = problems
        super().__init__("\n".join(problems))


def equivalent_age(ocr: float, rr: float, cr: float, calpha: float) -> float:
    """Equivalent age [days] as D-Settlement derives it for NEN-Bjerrum."""
    if calpha == 0:
        return 1.0
    return ocr ** ((cr - rr) / calpha)


def output_path(path: Path, suffix: str) -> Path:
    """'a.sli' or 'a.kj.sli' -> 'a.<suffix>.sli'."""
    stem = re.sub(r"\.(kj|bj)$", "", path.stem, flags=re.IGNORECASE)
    return path.with_name(f"{stem}.{suffix}.sli")


def _check_model(sli: SliFile, expected: str) -> None:
    model = sli.get_model_option("Model")
    if model != expected:
        raise ConversionError([f"expected a {expected} calculation but the model is {model}"])


def _apply_soil_parameters(sli: SliFile, soils: dict[str, dict[str, float]]) -> None:
    missing = [soil.name for soil in sli.soils if soil.name not in soils]
    if missing:
        raise ConversionError(
            [f"{len(missing)} soil(s) not found in the soils file:"]
            + [f"  - {name}" for name in missing]
        )

    problems = []
    for soil in sli.soils:
        values = soils[soil.name]
        for column, key in COLUMNS.items():
            sli.set_soil_value(soil, key, FORMATS[key].format(values[column]))
        try:
            age = equivalent_age(values["ocr"], values["rr"], values["cr"], values["calpha"])
        except OverflowError:
            problems.append(f"'{soil.name}': equivalent age too large, check ocr, rr, cr and calpha")
            continue
        sli.set_soil_value(soil, "SoilEquivalentAge", FORMATS["SoilEquivalentAge"].format(age))
    if problems:
        raise ConversionError(problems)


def koppejan_to_bjerrum(sli: SliFile, soils: dict[str, dict[str, float]]) -> list[str]:
    """Converts in place, returns notices for the user."""
    _check_model(sli, KOPPEJAN)
    _apply_soil_parameters(sli, soils)

    notices = []
    sli.set_model_option("Model", MODELS[BJERRUM], BJERRUM)
    if sli.get_model_option("Calculation type") != DARCY:
        sli.set_model_option("Calculation type", CALCULATION_TYPES[DARCY], DARCY)
        notices.append("calculation type changed from Terzaghi to Darcy (required for NEN-Bjerrum)")
    if sli.get_model_option("Strain type") != LINEAR:
        sli.set_model_option("Strain type", STRAIN_TYPES[LINEAR], LINEAR)
        notices.append("strain type changed from Natural to Linear (required for NEN-Bjerrum)")
    return notices


def bjerrum_to_koppejan(sli: SliFile, soils: dict[str, dict[str, float]]) -> list[str]:
    """Converts in place, returns notices for the user."""
    _check_model(sli, BJERRUM)
    _apply_soil_parameters(sli, soils)

    sli.set_model_option("Model", MODELS[KOPPEJAN], KOPPEJAN)
    for soil in sli.soils:
        sli.set_soil_value(soil, "SoilApAsApproximationByCpCs", "1")

    notices = []
    if sli.get_model_option("Calculation type") == TERZAGHI:
        notices.append("the calculation uses Terzaghi, Darcy is preferred")
    return notices
