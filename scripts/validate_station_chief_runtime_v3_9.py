#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("validate_station_chief_runtime_v4_0.py")), run_name="__main__")
