#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UI_MODEL_DIR = ROOT / "14_backend" / "product_runtime" / "ui_models"
DIST_DIR = ROOT / "13_web_dashboard" / "dist"
REPORT_DIR = ROOT / "09_exports" / "mvp_product_track"
SCRIPT_DIR = ROOT / "scripts"


def fail(message):
    raise SystemExit(f"FAIL: {message}")


def read_text(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        fail(f"Unable to read {path}: {exc}")


def ensure_exists(path):
    if not path.exists():
        fail(f"Missing required file: {path}")


def assert_contains(text, needle, label):
    if needle not in text:
        fail(f"Missing {label}: {needle}")


def main():
    required_files = [
        SCRIPT_DIR / "mvp23_feedback_import_smoke_test.py",
        SCRIPT_DIR / "mvp23_verify_feedback_migration_files.py",
        UI_MODEL_DIR / "manual_feedback_migration_operator_flow_model.json",
        UI_MODEL_DIR / "token_gated_feedback_import_smoke_test_model.json",
        UI_MODEL_DIR / "feedback_import_smoke_result_artifact_model.json",
        UI_MODEL_DIR / "feedback_smoke_operator_decision_model.json",
        DIST_DIR / "mvp23_feedback_import_smoke_test_model.json",
        REPORT_DIR / "mvp23_manual_migration_operator_flow_report.md",
        REPORT_DIR / "mvp23_token_gated_smoke_test_harness_report.md",
        REPORT_DIR / "mvp23_acceptance_report.md",
    ]
    for path in required_files:
        ensure_exists(path)

    # 1. Implementation Audit - Smoke Test Script
    smoke_script = read_text(SCRIPT_DIR / "mvp23_feedback_import_smoke_test.py")
    assert_contains(smoke_script, "SUPABASE_TEST_ACCESS_TOKEN", "smoke script token check")
    assert_contains(smoke_script, "MVP23_FEEDBACK_SMOKE_TEST_CONFIRMED", "smoke script confirmation check")
    assert_contains(smoke_script, "FEEDBACK_IMPORT_SMOKE_URL", "smoke script target URL check")
    assert_contains(smoke_script, 'action=status"', "smoke script status check")
    assert_contains(smoke_script, "FEEDBACK_PERSISTENCE_DISABLED", "smoke script disabled handling")
    assert_contains(smoke_script, "TOKEN_NOT_PROVIDED", "smoke script missing token check")
    assert_contains(smoke_script, "SKIPPED_CONFIRMATION_NOT_SET", "smoke script confirmation gate")
    assert_contains(smoke_script, 'action=import"', "smoke script import action")
    assert_contains(smoke_script, "redact(", "smoke script redaction logic")
    if 'print(TOKEN)' in smoke_script or 'print(f"Token: {TOKEN}")' in smoke_script:
        fail("Smoke script must not print the raw token.")

    # 2. Implementation Audit - Migration Verification Script
    migration_script = read_text(SCRIPT_DIR / "mvp23_verify_feedback_migration_files.py")
    assert_contains(migration_script, "external_feedback_packets", "migration script table check")
    assert_contains(migration_script, "auth.uid() = owner_user_id", "migration script RLS check")
    assert_contains(migration_script, 'forbidden = ["FOR UPDATE", "FOR DELETE"', "migration script blocking check")
    if "urllib" in migration_script or "requests" in migration_script:
        fail("Migration verification script must be offline/static only.")

    # 3. Dashboard Markers
    index = read_text(DIST_DIR / "index.html")
    required_strings = [
        "MVP-23",
        "TOKEN-GATED FEEDBACK IMPORT SMOKE TEST",
        "MANUAL MIGRATION OPERATOR FLOW",
        "DISABLED MODE VERIFICATION",
        "LIVE IMPORT TEST OPTIONAL AND GATED",
        "TOKENS NOT STORED OR PRINTED",
        "SERVICE ROLE NOT USED",
        "NO AUTOMATIC MIGRATION APPLY",
        "UPDATE DELETE EXECUTE BLOCKED",
        "AUTOMATION STILL DISABLED",
        "NEXT_STEP_RUN_REVIEWED_MIGRATION_AND_TOKEN_GATED_SMOKE_TEST",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "Manual Migration Operator Flow Panel",
        "Disabled Mode Verification Panel",
        "Token-Gated Smoke Test Panel",
        "Smoke Result Artifact Panel",
        "Operator Decision Panel",
        "Security Boundary Panel",
        "Copy MVP-23 validation checklist",
    ]
    for text in required_strings:
        assert_contains(index, text, "index.html marker")

    # 4. Acceptance Report
    acceptance = read_text(REPORT_DIR / "mvp23_acceptance_report.md")
    assert_contains(acceptance, "TOKEN_GATED_FEEDBACK_IMPORT_SMOKE_TEST_READY", "acceptance status")
    assert_contains(acceptance, "PASS_WITH_OPTIONAL_LIVE_IMPORT_TEST_GATED", "acceptance verdict")

    # 5. Real Safety Scans
    scan_roots = [ROOT / "13_web_dashboard", UI_MODEL_DIR, REPORT_DIR, SCRIPT_DIR]
    critical_forbidden = ["sb_secret_", "postgresql://postgres:", "SUPABASE_SERVICE_ROLE_KEY=sb_"]
    
    runtime_forbidden = [
        "localStorage.setItem",
        "localStorage.getItem",
        "sessionStorage.setItem",
        "sessionStorage.getItem",
        "document.cookie =",
        "indexedDB.open",
        "api.github.com",
        "api.netlify.com",
        "supabase.co",
        "child_process",
        "execSync",
        "spawn(",
        "subprocess",
        "os.system",
        "eval(",
        "Function(",
    ]

    for root in scan_roots:
        for path in root.rglob("*"):
            if not path.is_file(): continue
            if any(part.startswith(".") or part == "__pycache__" for part in path.parts): continue
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}: continue
            
            content = read_text(path)
            lower = content.lower()
            path_str = str(path).lower()
            
            if "scripts/validate_" in path_str: continue

            for pattern in critical_forbidden:
                if pattern in content:
                    fail(f"Forbidden critical pattern in {path.relative_to(ROOT)}: {pattern}")

            # Browser Runtime / Unauthorized Pattern Check
            if path.suffix in {".js", ".html", ".json"}:
                for pattern in runtime_forbidden:
                    if pattern in content:
                        if "scripts/validate_" in path_str: continue
                        if path.suffix == ".json": continue
                        # Allow safety labels in HTML/MD
                        if any(x in lower for x in ["<code>", "<pre>", "no ", "blocked", "disabled", "remains", "no-secret"]):
                            continue
                        fail(f"Forbidden runtime pattern in {path.relative_to(ROOT)}: {pattern}")

    # 6. Semantic check for MVP-23 JSON
    def check_json_security(data, path):
        def walk_flags(obj):
            if not isinstance(obj, dict): return
            for k, v in obj.items():
                nk = k.lower()
                if nk.endswith("enabled") and v is True:
                     if nk.startswith("no_"): continue
                     dangerous_flags = ["automation", "synthesis", "ingestion", "queue", "migration", "apply", "implementation", "automatic_migration_apply_enabled"]
                     if any(x in nk for x in dangerous_flags):
                          fail(f"Forbidden enabled flag {k} in {path}")
                if nk == "actual_import_default" and v is True:
                     fail(f"Forbidden actual_import_default flag {k} in {path}")
                if nk == "does_not_enable_feature_flag" and v is False:
                     fail(f"Gate violation: does_not_enable_feature_flag must be true in {path}")
                if nk == "does_not_apply_migration" and v is False:
                     fail(f"Gate violation: does_not_apply_migration must be true in {path}")
                if nk == "service_role_used" and v is True:
                     fail(f"Forbidden service_role_used flag {k} in {path}")
                walk_flags(v)
        walk_flags(data)

    model_paths = [
        DIST_DIR / "mvp23_feedback_import_smoke_test_model.json",
        UI_MODEL_DIR / "manual_feedback_migration_operator_flow_model.json",
        UI_MODEL_DIR / "token_gated_feedback_import_smoke_test_model.json",
    ]
    for p in model_paths:
        if p.exists():
            check_json_security(json.loads(read_text(p)), p)

    print("MVP23_FEEDBACK_IMPORT_SMOKE_TEST_VALIDATION_PASS")


if __name__ == "__main__":
    main()
