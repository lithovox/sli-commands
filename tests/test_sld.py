import re

import pytest

from conftest import FIXTURES
from settlement.sld import SldError, read_time_settlement

# the synthetic fixtures hold the same invented curves for Terzaghi and Darcy
CURVES = {
    1: [(0.0, 0.0), (0.1, 0.0123456), (1.0, 0.05), (10.0, 0.12), (100.0, 0.15)],
    2: [(0.0, 0.0), (0.1, 0.02), (1.0, 0.08), (10.0, 0.2), (100.0, 0.25)],
}


@pytest.mark.parametrize("name", ["terzaghi.sld", "darcy.sld"])
@pytest.mark.parametrize("vertical", [1, 2])
def test_time_settlement(name, vertical):
    assert read_time_settlement(FIXTURES / name, vertical) == CURVES[vertical]


def test_matches_time_settlement_per_load():
    """For Terzaghi the result equals the last column of [Time-Settlement per Load]."""
    lines = (FIXTURES / "terzaghi.sld").read_text(encoding="latin-1").splitlines()
    start = lines.index("[Time-Settlement per Load]") + 3
    end = lines.index("[End of Time-Settlement per Load]")
    expected = [(float(line.split()[0]), float(line.split()[-1])) for line in lines[start:end]]
    assert read_time_settlement(FIXTURES / "terzaghi.sld", 1) == expected


def test_settlement_column_is_looked_up(tmp_path):
    text = (FIXTURES / "darcy.sld").read_text(encoding="latin-1")
    # swap the first two columns, the settlement is then read from the second
    # read_text turns the CRLF line endings into \n
    assert "Settlement\nEffective stress vertical" in text
    text = text.replace("Settlement\nEffective stress vertical", "Effective stress vertical\nSettlement")
    text, swapped = re.subn(r"(?m)^\s+([\d.]+)\s+1\.0000000\s+0\.5000000$", r"   1.0000000    \1    0.5000000", text)
    assert swapped == 30  # 2 verticals x 5 times x 3 depths
    path = tmp_path / "swapped.sld"
    path.write_text(text, encoding="latin-1")
    assert read_time_settlement(path, 2) == CURVES[2]


def test_several_verticals_in_one_block(tmp_path):
    text = (FIXTURES / "darcy.sld").read_text(encoding="latin-1")
    combined = text.replace("[End of Vertical]\n[Vertical]\n      2     =  Vertical count", "      2     =  Vertical count")
    assert combined != text
    path = tmp_path / "combined.sld"
    path.write_text(combined, encoding="latin-1")
    assert read_time_settlement(path, 1) == CURVES[1]
    assert read_time_settlement(path, 2) == CURVES[2]


def test_unknown_vertical():
    with pytest.raises(SldError, match="vertical 3 not found, available vertical\\(s\\): 1, 2"):
        read_time_settlement(FIXTURES / "darcy.sld", 3)


def test_file_without_results(tmp_path):
    path = tmp_path / "input_only.sld"
    path.write_text("[INPUT DATA]\n[END OF INPUT DATA]\n")
    with pytest.raises(SldError, match="no results found"):
        read_time_settlement(path, 1)


def test_vertical_without_time_dependent_data(tmp_path):
    path = tmp_path / "empty.sld"
    path.write_text("[Vertical]\n      1     =  Vertical count\n[End of Vertical]\n")
    with pytest.raises(SldError, match="no time-dependent data found for vertical 1"):
        read_time_settlement(path, 1)
