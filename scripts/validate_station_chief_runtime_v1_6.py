#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import runpy


if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("validate_station_chief_runtime_v3_3.py")), run_name="__main__")
