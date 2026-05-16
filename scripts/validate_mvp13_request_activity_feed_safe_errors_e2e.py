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
        "python3 scripts/validate_mvp13_request_activity_feed_safe_errors.py",
        "python3 scripts/validate_mvp12_controlled_lifecycle_event_creation.py",
        "python3 scripts/validate_mvp11_token_aware_workspace_polish.py",
        "python3 scripts/validate_mvp10_operator_request_workspace_ui.py",
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

    # Final secret/token-storage/safe-error/write-scope scan
    stdout, stderr, code = run("python3 - <<'PY'\nfrom pathlib import Path\nscan_roots = [Path('14_backend/product_runtime'), Path('netlify/functions'), Path('13_web_dashboard'), Path('09_exports/mvp_product_track')]\nfor root in scan_roots:\n if not root.exists(): continue\n for path in root.rglob('*'):\n  if not path.is_file(): continue\n  if '__pycache__' in path.parts: continue\n  if path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico'}: continue\n  text = path.read_text(encoding='utf-8', errors='replace')\n  lower = text.lower()\n  if 'sb_secret_' in text: raise SystemExit(f'SECRET_KEY_LEAK: {path}')\n  if 'postgresql://postgres:' in text: raise SystemExit(f'POSTGRES_CONNECTION_STRING_LEAK: {path}')\n  if 'SUPABASE_SERVICE_ROLE_KEY=sb_' in text: raise SystemExit(f'SERVICE_ROLE_VALUE_LEAK: {path}')\n  if not any(x in str(path) for x in ['scripts/validate_', '09_exports/', 'dashboard_renderer.py', '13_web_dashboard/dist/']):\n   for item in ['localstorage', 'sessionstorage', 'document.cookie', 'indexeddb', 'console.log(token', 'console.error(token']:\n    if item in lower: raise SystemExit(f'FORBIDDEN_PATTERN {item}: {path}')\n  if path.name == 'requests.js':\n   if 'err.message' in text: raise SystemExit('RAW_ERR_MESSAGE_IN_REQUESTS_JS')\n   for forbidden in ['method: \"PATCH\"', 'method: \\'PATCH\\'', 'method: \"PUT\"', 'method: \\'PUT\\'', 'method: \"DELETE\"', 'method: \\'DELETE\\'', '/rpc/']:\n    if forbidden in text: raise SystemExit(f'FORBIDDEN_REQUESTS_WRITE_PATTERN: {forbidden}')\nprint('MVP13_SAFETY_SCAN_PASS')\nPY")
    if code != 0:
        fail(f"Safety scan failed: {stdout}")

    print("MVP13_REQUEST_ACTIVITY_FEED_SAFE_ERRORS_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    main()
