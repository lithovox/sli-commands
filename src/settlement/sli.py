"""Line based reading and writing of D-Settlement input files (.sli).

Only the lines that are changed are touched, every other line is written back
exactly as it was read.
"""

from dataclasses import dataclass, field
from pathlib import Path

NEWLINE = "\r\n"


class SliError(Exception):
    """Raised when a .sli file does not have the expected structure."""


@dataclass
class Soil:
    name: str
    # parameter key (e.g. "SoilCa") -> index of its line in SliFile.lines
    keys: dict[str, int] = field(default_factory=dict)


class SliFile:
    def __init__(self, lines: list[str]):
        self.lines = lines
        self.soils = self._parse_soils()

    @classmethod
    def read(cls, path: Path) -> "SliFile":
        return cls.from_bytes(path.read_bytes())

    @classmethod
    def from_bytes(cls, data: bytes) -> "SliFile":
        return cls(data.decode("latin-1").replace("\r\n", "\n").split("\n"))

    def write(self, path: Path) -> None:
        path.write_bytes(self.to_bytes())

    def to_bytes(self) -> bytes:
        return NEWLINE.join(self.lines).encode("latin-1")

    def _section(self, name: str) -> range:
        """Line indices between [name] and [END OF name], exclusive."""
        try:
            start = self.lines.index(f"[{name}]")
            end = self.lines.index(f"[END OF {name}]", start)
        except ValueError:
            raise SliError(f"section [{name}] not found") from None
        return range(start + 1, end)

    def _parse_soils(self) -> list[Soil]:
        soils = []
        current = None
        for i in self._section("SOIL COLLECTION"):
            line = self.lines[i]
            if line == "[SOIL]":
                current = Soil(name=self.lines[i + 1].strip())
                soils.append(current)
            elif line == "[END OF SOIL]":
                current = None
            elif current is not None and "=" in line:
                key = line.split("=", 1)[0]
                current.keys[key] = i
        return soils

    def get_soil_value(self, soil: Soil, key: str) -> str:
        return self.lines[self._soil_line(soil, key)].split("=", 1)[1]

    def set_soil_value(self, soil: Soil, key: str, value: str) -> None:
        self.lines[self._soil_line(soil, key)] = f"{key}={value}"

    def _soil_line(self, soil: Soil, key: str) -> int:
        try:
            return soil.keys[key]
        except KeyError:
            raise SliError(f"soil '{soil.name}' has no parameter {key}") from None

    def _model_line(self, option: str) -> int:
        for i in self._section("MODEL"):
            # lines look like "0 : Model = NEN - Koppejan"
            parts = self.lines[i].split(":", 1)
            if len(parts) == 2 and parts[1].split("=", 1)[0].strip() == option:
                return i
        raise SliError(f"model option '{option}' not found in [MODEL]")

    def get_model_option(self, option: str) -> str:
        return self.lines[self._model_line(option)].split("=", 1)[1].strip()

    def set_model_option(self, option: str, index: int, value: str) -> None:
        self.lines[self._model_line(option)] = f"{index} : {option} = {value}"

    def set_filename(self, path: Path) -> None:
        for i, line in enumerate(self.lines):
            if line.startswith("FILENAME"):
                self.lines[i] = f"{line.split(':', 1)[0]}: {path}"
                return
