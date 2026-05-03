#!/usr/bin/env python3
import runpy
import sys
import os

# Delegate to the latest validator (v2.6.0)
script_dir = os.path.dirname(os.path.realpath(__file__))
latest_validator = os.path.join(script_dir, "validate_station_chief_runtime_v2_6.py")
runpy.run_path(latest_validator, run_name="__main__")
