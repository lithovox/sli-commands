"""PyInstaller entry script for the kj2bj executable."""

import sys

from settlement.cli import kj2bj

sys.exit(kj2bj())
