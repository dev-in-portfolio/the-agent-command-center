#!/usr/bin/env python3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def fail(message):
    raise SystemExit(f"FAIL: {message}")


def run(cmd):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=ROOT)
        return res.stdout, res.stderr, res.returncode
    except Exception as exc:
        fail(f"Execution error for {cmd}: {exc}")


def main():
    validators = [
        "python3 scripts/validate_mvp9_request_detail_lifecycle_timeline.py",
        "python3 scripts/validate_mvp8_controlled_authenticated_request_create.py",
        "python3 scripts/validate_mvp7_real_authenticated_supabase_reads.py",
        "python3 scripts/validate_mvp6_controlled_migration_authenticated_reads.py",
        "python3 scripts/validate_mvp5_migration_readiness_authenticated_reads.py",
        "python3 scripts/validate_mvp4_supabase_auth_rls_request_api.py",
        "python3 scripts/validate_mvp3_supabase_provider_request_api.py",
        "python3 scripts/validate_mvp2_local_durable_request_persistence.py",
        "python3 scripts/validate_mvp1_request_lifecycle_runtime.py",
        "python3 scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "python3 scripts/validate_phase5_plus1_master_validator_wall.py",
    ]

    for v in validators:
        stdout, stderr, code = run(v)
        if code != 0:
            fail(f"Validator {v} failed:\nSTDOUT: {stdout}\nSTDERR: {stderr}")

    # Final secret scan
    stdout, stderr, code = run("python3 - <<'PY'\nfrom pathlib import Path\nscan_roots = [Path('14_backend/product_runtime'), Path('netlify/functions'), Path('13_web_dashboard/dist'), Path('09_exports/mvp_product_track')]\nfor root in scan_roots:\n if not root.exists(): continue\n for path in root.rglob('*'):\n  if not path.is_file(): continue\n  text = path.read_text(encoding='utf-8', errors='replace')\n  if 'sb_secret_' in text: raise SystemExit(f'SECRET_KEY_LEAK: {path}')\n  if 'postgresql://postgres:' in text: raise SystemExit(f'POSTGRES_CONNECTION_STRING_LEAK: {path}')\n  if 'SUPABASE_SERVICE_ROLE_KEY=sb_' in text: raise SystemExit(f'SERVICE_ROLE_VALUE_LEAK: {path}')\nprint('MVP9_SECRET_SCAN_PASS')\nPY")
    if code != 0:
        fail(f"Secret scan failed: {stdout}")

    print("MVP9_REQUEST_DETAIL_LIFECYCLE_TIMELINE_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    main()
