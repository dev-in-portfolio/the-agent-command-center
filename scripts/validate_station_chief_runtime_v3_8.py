#!/usr/bin/env python3
from __future__ import annotations

import runpy
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET = REPO_ROOT / "scripts" / "validate_station_chief_runtime_v4_6.py"


def main() -> None:
    sys.path.insert(0, str(REPO_ROOT))
    runpy.run_path(str(TARGET), run_name="__main__")


if __name__ == "__main__":
    main()
