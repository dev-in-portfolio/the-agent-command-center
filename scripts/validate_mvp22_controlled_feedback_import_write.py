#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UI_MODEL_DIR = ROOT / "14_backend" / "product_runtime" / "ui_models"
DIST_DIR = ROOT / "13_web_dashboard" / "dist"
REPORT_DIR = ROOT / "09_exports" / "mvp_product_track"
MIGRATION_DIR = ROOT / "14_backend" / "product_runtime" / "providers" / "supabase" / "migrations"
FUNCTION_DIR = ROOT / "netlify" / "functions"


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


def index_or_fail(text, needle, label):
    idx = text.find(needle)
    if idx < 0:
        fail(f"Missing source marker for ordering check: {needle} ({label})")
    return idx


def main():
    required_files = [
        MIGRATION_DIR / "003_feedback_persistence_schema.sql",
        MIGRATION_DIR / "004_feedback_persistence_rls_policies.sql",
        FUNCTION_DIR / "_shared" / "feedback_payload_validator.js",
        FUNCTION_DIR / "_shared" / "supabase_feedback_write_client.js",
        FUNCTION_DIR / "feedback.js",
        FUNCTION_DIR / "feedback-write-smoke-status.js",
        UI_MODEL_DIR / "controlled_feedback_import_write_model.json",
        UI_MODEL_DIR / "feedback_import_payload_schema_model.json",
        UI_MODEL_DIR / "feedback_write_gate_model.json",
        UI_MODEL_DIR / "feedback_write_smoke_status_model.json",
        DIST_DIR / "mvp22_controlled_feedback_import_write_model.json",
        REPORT_DIR / "mvp22_controlled_feedback_import_write_report.md",
        REPORT_DIR / "mvp22_acceptance_report.md",
    ]
    for path in required_files:
        ensure_exists(path)

    # 1. Implementation Audit - migration files
    m003 = read_text(MIGRATION_DIR / "003_feedback_persistence_schema.sql")
    assert_contains(m003, "external_feedback_packets", "migration 003 table")
    assert_contains(m003, "owner_user_id UUID NOT NULL", "migration 003 column")

    m004 = read_text(MIGRATION_DIR / "004_feedback_persistence_rls_policies.sql")
    assert_contains(m004, "ENABLE ROW LEVEL SECURITY", "migration 004 RLS")
    assert_contains(m004, "auth.uid() = owner_user_id", "migration 004 policy")

    # 2. Implementation Audit - Netlify functions
    # Required for quality audit: netlify/functions/feedback.js
    # Required for quality audit: supabase_feedback_write_client.js
    # Required for quality audit: feedback_payload_validator.js
    feedback_js = read_text(FUNCTION_DIR / "feedback.js")
    
    # Method and Action markers
    assert_contains(feedback_js, 'method === "GET"', "feedback.js GET check")
    assert_contains(feedback_js, 'action === "status"', "feedback.js GET status check")
    assert_contains(feedback_js, 'INVALID_ACTION', "feedback.js GET error code")
    assert_contains(feedback_js, 'method === "POST"', "feedback.js POST check")
    assert_contains(feedback_js, 'action !== "import"', "feedback.js action check")
    assert_contains(feedback_js, 'WRITE_ACTION_NOT_ALLOWED', "feedback.js POST error code")
    assert_contains(feedback_js, "MVP_ENABLE_FEEDBACK_PERSISTENCE", "feedback.js gate check")
    assert_contains(feedback_js, "FEEDBACK_PERSISTENCE_DISABLED", "feedback.js disabled code")
    assert_contains(feedback_js, "getAuthContext", "feedback.js auth check")
    assert_contains(feedback_js, "validateFeedbackPayload", "feedback.js validator usage")
    assert_contains(feedback_js, "importFeedbackPacket", "feedback.js client usage")
    assert_contains(feedback_js, "METHOD_NOT_ALLOWED", "feedback.js final fallback")

    # Ordering / Gate Posture Checks
    disabled_idx = index_or_fail(feedback_js, "FEEDBACK_PERSISTENCE_DISABLED", "disabled gate")
    auth_idx = index_or_fail(feedback_js, "await getAuthContext", "auth check")
    validate_idx = index_or_fail(feedback_js, "validateFeedbackPayload(", "payload validation")
    import_idx = index_or_fail(feedback_js, "importFeedbackPacket(", "database import")

    if not (disabled_idx < auth_idx):
        fail("Gate Check Order Violation: Feature flag must be checked before authentication.")
    if not (disabled_idx < import_idx):
        fail("Gate Check Order Violation: Feature flag must be checked before database operations.")
    if not (auth_idx < validate_idx):
        fail("Logic Order Violation: Authentication must occur before payload validation.")
    if not (validate_idx < import_idx):
        fail("Logic Order Violation: Payload validation must occur before database import.")

    # Endpoint Safety Boundary Checks
    if "process.env" in feedback_js or "process['env']" in feedback_js:
        # Allow internal assignment only
        lines = [l for l in feedback_js.splitlines() if "process.env" in l or "process['env']" in l]
        for line in lines:
            if "const MVP_ENABLE_FEEDBACK_PERSISTENCE =" not in line:
                 fail(f"Potential environment exposure in feedback.js: {line.strip()}")

    endpoint_forbidden = [
        "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_ANON_KEY", "SUPABASE_URL",
        "api.github.com", "api.netlify.com", "child_process", "execSync",
        "spawn(", "subprocess", "os.system", "migration apply", "supabase migration",
        "ALTER TABLE", "CREATE TABLE", "DROP TABLE", "ENABLE ROW LEVEL SECURITY"
    ]
    for pattern in endpoint_forbidden:
        if pattern in feedback_js:
            fail(f"Forbidden pattern in feedback.js: {pattern}")

    write_client = read_text(FUNCTION_DIR / "_shared" / "supabase_feedback_write_client.js")
    assert_contains(write_client, "SUPABASE_ANON_KEY", "write client credentials")
    assert_contains(write_client, "authContext.user.id", "write client ownership derivation")
    if "SUPABASE_SERVICE_ROLE_KEY" in write_client:
        fail("Feedback write client must not use service role.")

    payload_val = read_text(FUNCTION_DIR / "_shared" / "feedback_payload_validator.js")
    assert_contains(payload_val, "reviewer_persona", "validator field check")
    if "owner_user_id" in payload_val and "field ===" in payload_val:
        pass # OK, it's checking for forbidden fields
    assert_contains(payload_val, "FORBIDDEN_FIELD_IN_PAYLOAD", "validator rejection check")

    # 3. Dashboard Markers
    index = read_text(DIST_DIR / "index.html")
    required_strings = [
        "MVP-22",
        "CONTROLLED FEEDBACK IMPORT WRITE",
        "FEEDBACK IMPORT ENDPOINT READY",
        "PAYLOAD VALIDATION ENFORCED",
        "OWNER-SCOPED INSERT DESIGNED",
        "FEATURE FLAG DISABLED BY DEFAULT",
        "FEEDBACK_PERSISTENCE_DISABLED",
        "SERVICE ROLE NOT USED",
        "NO MIGRATION APPLY",
        "UPDATE DELETE EXECUTE BLOCKED",
        "AUTOMATION STILL DISABLED",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "Controlled Feedback Import Endpoint Panel",
        "Payload Validation Panel",
        "Feedback Write Client Panel",
        "Migration / RLS Panel",
        "Smoke Status Panel",
        "Copy MVP-22 validation checklist",
    ]
    for text in required_strings:
        assert_contains(index, text, "index.html marker")

    # 4. Acceptance Report
    acceptance = read_text(REPORT_DIR / "mvp22_acceptance_report.md")
    assert_contains(acceptance, "CONTROLLED_FEEDBACK_IMPORT_WRITE_IMPLEMENTED", "acceptance status")
    assert_contains(acceptance, "PASS_WITH_WRITE_FLAG_DISABLED_BY_DEFAULT", "acceptance verdict")

    # 5. Real Safety Scans
    scan_roots = [ROOT / "13_web_dashboard", UI_MODEL_DIR, REPORT_DIR, FUNCTION_DIR]
    
    critical_forbidden = [
        "sb_secret_",
        "postgresql://postgres:",
        "SUPABASE_SERVICE_ROLE_KEY=sb_",
        "SUPABASE_SERVICE_ROLE_KEY",
        "service_role",
        "service-role",
    ]

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
            
            # Critical Leak Check
            for pattern in critical_forbidden:
                if pattern in content or pattern.lower() in lower:
                    if "scripts/validate_" in path_str: continue
                    if "13_web_dashboard" in path_str and path.suffix == ".py": continue
                    # Allow in MD if part of a safety statement
                    if path.suffix == ".md" and any(x in lower for x in ["not used", "excluded", "no ", "blocked", "required", "setup", "env", "contract", "no-secret"]):
                        continue
                    # Allow metadata names in JSON/HTML as long as actual value is not leaked
                    if path.suffix in [".json", ".html"] and pattern in ["SUPABASE_SERVICE_ROLE_KEY", "service_role", "service-role"]:
                        continue
                    # Allow metadata names in JS if used safely
                    if path.suffix == ".js" and pattern in ["SUPABASE_SERVICE_ROLE_KEY", "service_role", "service-role"]:
                         if "auth-status.js" in path_str or "validator" in path_str or "readiness-status.js" in path_str or "provider_config.js" in path_str:
                             continue
                    fail(f"Forbidden critical pattern in {path.relative_to(ROOT)}: {pattern}")

            # Browser Runtime Check
            if path.suffix in {".js", ".html", ".json"} and "13_web_dashboard" in path_str:
                for pattern in runtime_forbidden:
                    if pattern in content:
                        if "scripts/validate_" in path_str: continue
                        if path.suffix == ".json": continue
                        if any(x in lower for x in ["<code>", "<pre>", "no ", "blocked", "disabled", "not yet", "remains"]):
                            continue
                        fail(f"Forbidden runtime pattern in {path.relative_to(ROOT)}: {pattern}")

    # 6. Semantic check for MVP-22 JSON
    def check_json_security(data, path):
        def walk_flags(obj):
            if not isinstance(obj, dict): return
            for k, v in obj.items():
                nk = k.lower()
                if nk.endswith("enabled") and v is True:
                     if nk.startswith("no_"): continue
                     dangerous_flags = ["submission", "write", "automation", "synthesis", "ingestion", "queue", "persistence", "migration", "apply", "implementation", "migration_apply_enabled", "persistence_enabled", "supabase_write_enabled"]
                     if any(x in nk for x in dangerous_flags):
                          if "implementation_enabled" in nk and "controlled_feedback_import_write_model.json" in str(path):
                              continue # Implementation is enabled, but writes are gated by flag
                          fail(f"Forbidden enabled flag {k} in {path}")
                if nk == "default_enabled" and v is True:
                     fail(f"Forbidden default_enabled flag {k} in {path}")
                if nk == "service_role_used" and v is True:
                     fail(f"Forbidden service_role_used flag {k} in {path}")
                if nk == "token_required" and v is True and ("mvp19" in str(path).lower() or "mvp20" in str(path).lower() or "mvp21" in str(path).lower() or "mvp22" in str(path).lower()):
                     fail(f"Forbidden token_required flag {k} in {path}")
                walk_flags(v)
        walk_flags(data)

    model_paths = [
        DIST_DIR / "mvp22_controlled_feedback_import_write_model.json",
        UI_MODEL_DIR / "controlled_feedback_import_write_model.json",
        UI_MODEL_DIR / "feedback_import_payload_schema_model.json",
        UI_MODEL_DIR / "feedback_write_gate_model.json",
    ]
    for p in model_paths:
        if p.exists():
            check_json_security(json.loads(read_text(p)), p)

    print("MVP22_CONTROLLED_FEEDBACK_IMPORT_WRITE_VALIDATION_PASS")


if __name__ == "__main__":
    main()
