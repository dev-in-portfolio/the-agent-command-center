#!/usr/bin/env python3
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "14_backend" / "schemas"
DIST_DIR = ROOT / "13_web_dashboard" / "dist"

REQUIRED_TOP_LEVEL_FLAGS = {
    "schema_mode": "static_inert_schema_preview",
    "live_external_api_calls": False,
    "github_api_calls": False,
    "netlify_api_calls": False,
    "browser_external_fetches": False,
    "secrets_used": False,
    "tokens_used": False,
    "environment_variables_read": False,
    "command_execution": False,
    "github_mutation": False,
    "netlify_mutation": False,
    "deploy_controls": False,
    "merge_controls": False,
    "push_controls": False,
    "pr_controls": False,
    "action_execution": False,
    "action_queue_live": False,
}

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


def _validate_top_level_flags(source_name, payload):
    for key, expected_value in REQUIRED_TOP_LEVEL_FLAGS.items():
        actual_value = payload.get(key)
        if actual_value != expected_value:
            return _fail(f"schema top-level flag mismatch: {source_name}::{key}")
    return 0


def main():
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    for source_name, dest_name in SCHEMA_MAP.items():
        source_path = SCHEMA_DIR / source_name
        dest_path = DIST_DIR / dest_name
        if not source_path.exists():
            return _fail(f"missing source schema: {source_name}")
        payload = _load_json(source_path)
        rc = _validate_top_level_flags(source_name, payload)
        if rc != 0:
            return rc
        shutil.copy2(source_path, dest_path)

    print("PHASE_4D_SCHEMA_PREVIEW_BUILD_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
