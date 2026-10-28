"""PyInstaller entry script for the slicmd executable."""

import sys

from settlement.cli import main

sys.exit(main())
