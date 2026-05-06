#!/usr/bin/env python3
import runpy
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "scripts" / "validate_station_chief_runtime_v4_7.py"

def main() -> None:
    # Validate v4.8 specific checks before delegating
    from pathlib import Path
    import json
    import hashlib
    
    # Check version
    RUNTIME = REPO_ROOT / "10_runtime/station_chief_runtime.py"
    with open(RUNTIME, "r") as f:
        content = f.read()
        if 'STATION_CHIEF_RUNTIME_VERSION = "4.8.0"' not in content:
            raise AssertionError("Version mismatch in runtime.py")

    # Delegate to v4.7
    sys.exit(runpy.run_path(str(TARGET), run_name="__main__").get("main", lambda: 0)())

if __name__ == "__main__":
    main()
