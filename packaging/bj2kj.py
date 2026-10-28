"""PyInstaller entry script for the bj2kj executable."""

import sys

from settlement.cli import bj2kj

sys.exit(bj2kj())
