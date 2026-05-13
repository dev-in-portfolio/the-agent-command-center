#!/usr/bin/env python3
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "14_backend" / "schemas"
DIST_DIR = ROOT / "13_web_dashboard" / "dist"

SCHEMA_MAP = {
    "phase4d_identity_schema.json": "phase4d_identity_schema.json",
    "phase4d_action_schema.json": "phase4d_action_schema.json",
    "phase4d_audit_schema.json": "phase4d_audit_schema.json",
    "phase4d_approval_schema.json": "phase4d_approval_schema.json",
    "phase4d_risk_model.json": "phase4d_risk_model.json",
}


def _fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def _load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_false_flags(payload, found=None):
    if found is None:
        found = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key.endswith("_implemented") or key.endswith("_added") or key.endswith("_read"):
                if isinstance(value, dict) and "const" in value:
                    found.append((key, value.get("const")))
                else:
                    found.append((key, value))
            _assert_false_flags(value, found)
    elif isinstance(payload, list):
        for item in payload:
            _assert_false_flags(item, found)
    return found


def main():
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    for source_name, dest_name in SCHEMA_MAP.items():
        source_path = SCHEMA_DIR / source_name
        dest_path = DIST_DIR / dest_name
        if not source_path.exists():
            return _fail(f"missing source schema: {source_name}")
        payload = _load_json(source_path)
        false_flags = _assert_false_flags(payload)
        for key, value in false_flags:
            if value is not False:
                return _fail(f"schema flag must be false: {source_name}::{key}")
        shutil.copy2(source_path, dest_path)

    print("PHASE_4D_SCHEMA_PREVIEW_BUILD_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
