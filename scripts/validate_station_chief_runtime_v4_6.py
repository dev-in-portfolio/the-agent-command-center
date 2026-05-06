#!/usr/bin/env python3
import runpy
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "scripts" / "validate_station_chief_runtime_v4_7.py"

def main() -> None:
    sys.exit(runpy.run_path(str(TARGET), run_name="__main__").get("main", lambda: 0)())

if __name__ == "__main__":
    main()
