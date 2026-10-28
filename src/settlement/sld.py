"""Reading results from D-Settlement output files (.sld).

The time-settlement curve of a vertical is read from the [Vertical Data at Time]
blocks. Terzaghi and Darcy calculations both write these, while
[Time-Settlement per Load] only exists for Terzaghi. The settlement of the
vertical is the settlement of its top node, the first row of each block.
"""

import re
from pathlib import Path

# each vertical in the [Vertical] block starts with a line like "      1     =  Vertical count"
VERTICAL_START = re.compile(r"^\s*(\d+)\s*=\s*Vertical count\s*$")


class SldError(Exception):
    """Raised when the requested data cannot be read from a .sld file."""


def _verticals(lines: list[str]) -> dict[int, list[str]]:
    """Vertical number -> the lines of that vertical.

    Each vertical normally has its own [Vertical] block, the number in its
    "Vertical count" line identifies it.
    """
    verticals: dict[int, list[str]] = {}
    current = None
    in_vertical = False
    for line in lines:
        if line == "[Vertical]":
            in_vertical, current = True, None
        elif line == "[End of Vertical]":
            in_vertical = False
        elif in_vertical:
            match = VERTICAL_START.match(line)
            if match:
                current = verticals.setdefault(int(match.group(1)), [])
            elif current is not None:
                current.append(line)
    if not verticals:
        raise SldError("no results found, run the calculation in D-Settlement first")
    return verticals


def _settlement_column(lines: list[str], index: int) -> int:
    """Index of the Settlement column in the [Column Indication] before lines[index]."""
    try:
        start = max(i for i in range(index) if lines[i] == "[Column Indication]")
        end = lines.index("[End of Column Indication]", start)
        return [c.strip() for c in lines[start + 1 : end]].index("Settlement")
    except ValueError:
        raise SldError("no Settlement column found for the time-dependent data") from None


def read_time_settlement(path: Path, vertical: int) -> list[tuple[float, float]]:
    """Returns (time [days], settlement [m]) for each calculation time of a vertical."""
    lines = path.read_text(encoding="latin-1").replace("\r\n", "\n").split("\n")
    verticals = _verticals(lines)
    if vertical not in verticals:
        available = ", ".join(str(v) for v in sorted(verticals)) or "none"
        raise SldError(f"vertical {vertical} not found, available vertical(s): {available}")

    data = verticals[vertical]
    starts = [i for i, line in enumerate(data) if line == "[Vertical Data at Time]"]
    if not starts:
        raise SldError(f"no time-dependent data found for vertical {vertical}")
    column = _settlement_column(data, starts[0])

    result = []
    for i in starts:
        # "   0.100000000000    =  Time in days", followed by one row per depth, top first
        time = float(data[i + 1].split("=")[0])
        settlement = float(data[i + 2].split()[column])
        result.append((time, settlement))
    return result
