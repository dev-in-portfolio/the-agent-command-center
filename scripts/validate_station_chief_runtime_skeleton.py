#!/usr/bin/env python3
from __future__ import annotations

import runpy
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET = REPO_ROOT / "scripts" / "validate_station_chief_runtime_v4_3.py"


def main() -> None:
    old_sys_path = sys.path[:]
    sys.path.insert(0, str(REPO_ROOT / "10_runtime"))
    sys.path.insert(0, str(REPO_ROOT))
    try:
        runpy.run_path(str(TARGET), run_name="__main__")
    finally:
        sys.path[:] = old_sys_path


if __name__ == "__main__":
    main()
