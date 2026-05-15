#!/usr/bin/env python3
import contextlib
import io
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def fail(message):
    raise SystemExit(f"FAIL: {message}")


def run_validator(rel_path):
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
            runpy.run_path(str(ROOT / rel_path), run_name="__main__")
    except SystemExit as exc:
        output = buffer.getvalue()
        if exc.code not in (0, None):
            fail(f"{rel_path} failed\n{output}")
    output = buffer.getvalue()
    return output


def main():
    validators = [
        "scripts/validate_mvp5_migration_readiness_authenticated_reads.py",
        "scripts/validate_mvp4_supabase_auth_rls_request_api.py",
        "scripts/validate_mvp3_supabase_provider_request_api.py",
        "scripts/validate_mvp2_local_durable_request_persistence.py",
        "scripts/validate_mvp1_request_lifecycle_runtime.py",
        "scripts/validate_original_plus2e_server_side_dry_run_engine.py",
        "scripts/validate_phase5_plus1_master_validator_wall.py",
    ]
    expected = {
        "scripts/validate_mvp5_migration_readiness_authenticated_reads.py": "MVP5_MIGRATION_READINESS_AUTHENTICATED_READS_VALIDATION_PASS",
        "scripts/validate_mvp4_supabase_auth_rls_request_api.py": "MVP4_SUPABASE_AUTH_RLS_REQUEST_API_VALIDATION_PASS",
        "scripts/validate_mvp3_supabase_provider_request_api.py": "MVP3_SUPABASE_PROVIDER_REQUEST_API_VALIDATION_PASS",
        "scripts/validate_mvp2_local_durable_request_persistence.py": "MVP2_LOCAL_DURABLE_REQUEST_PERSISTENCE_VALIDATION_PASS",
        "scripts/validate_mvp1_request_lifecycle_runtime.py": "MVP1_REQUEST_LIFECYCLE_RUNTIME_VALIDATION_PASS",
        "scripts/validate_original_plus2e_server_side_dry_run_engine.py": "ORIGINAL_PLUS2E_SERVER_SIDE_DRY_RUN_ENGINE_VALIDATION_PASS",
        "scripts/validate_phase5_plus1_master_validator_wall.py": "PHASE5_PLUS1_MASTER_VALIDATOR_WALL_PASS",
    }

    for rel_path in validators:
        output = run_validator(rel_path)
        if expected[rel_path] not in output:
            fail(f"{rel_path} missing pass string")

    import subprocess
    result = subprocess.run(
        ["git", "diff", "--name-only", "origin/master..HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    changed_paths = [line for line in result.stdout.splitlines() if line.strip()]
    allowed_prefixes = [
        "14_backend/product_runtime/",
        "netlify/functions/_shared/provider_config.js",
        "netlify/functions/_shared/auth_context.js",
        "netlify/functions/provider-status.js",
        "netlify/functions/auth-status.js",
        "netlify/functions/requests.js",
        "netlify/functions/request-readiness-status.js",
        "netlify/functions/backend-manifest.js",
        "13_web_dashboard/",
        "09_exports/mvp_product_track/",
        "scripts/validate_mvp5_migration_readiness_authenticated_reads.py",
        "scripts/validate_mvp5_migration_readiness_authenticated_reads_e2e.py",
        "scripts/validate_mvp4_supabase_auth_rls_request_api.py",
        "scripts/validate_mvp4_supabase_auth_rls_request_api_e2e.py",
        "scripts/validate_phase5_plus1_master_validator_wall.py",
    ]
    forbidden_prefixes = [
        "09_exports/interface_phase_1/",
        "09_exports/interface_phase_2/",
        "09_exports/interface_phase_3/",
        "09_exports/interface_phase_4/",
        "11_interface/",
        "12_tui/",
        "10_runtime/",
    ]

    for path in changed_paths:
        for prefix in forbidden_prefixes:
            if path.startswith(prefix):
                fail(f"Forbidden changed path: {path}")
        if not any(path.startswith(prefix) for prefix in allowed_prefixes):
            fail(f"Unexpected changed path: {path}")

    print("MVP5_MIGRATION_READINESS_AUTHENTICATED_READS_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    main()
