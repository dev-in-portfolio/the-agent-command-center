#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET = REPO_ROOT / "scripts" / "validate_station_chief_runtime_v3_9.py"

if __name__ == "__main__":
    runpy.run_path(str(TARGET), run_name="__main__")
