#!/usr/bin/env python3
import runpy
import sys

def main():
    try:
        runpy.run_path("scripts/validate_station_chief_runtime_v3_4.py", run_name="__main__")
    except Exception as e:
        print(f"FAIL: Delegate validator failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
