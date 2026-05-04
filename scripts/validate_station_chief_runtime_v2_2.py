import runpy
import sys
import os

if __name__ == "__main__":
    # Delegate to the latest validator
    v3_2_validator = os.path.join(os.path.dirname(__file__), "validate_station_chief_runtime_v3_2.py")
    runpy.run_path(v3_2_validator, run_name="__main__")
