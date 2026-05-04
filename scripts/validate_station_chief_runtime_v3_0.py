import runpy
import sys
import os

if __name__ == "__main__":
    # Delegate to the latest validator
    v3_1_validator = os.path.join(os.path.dirname(__file__), "validate_station_chief_runtime_v3_1.py")
    runpy.run_path(v3_1_validator, run_name="__main__")
