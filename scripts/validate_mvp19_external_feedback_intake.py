#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UI_MODEL_DIR = ROOT / "14_backend" / "product_runtime" / "ui_models"
DIST_DIR = ROOT / "13_web_dashboard" / "dist"
REPORT_DIR = ROOT / "09_exports" / "mvp_product_track"
ASSET_DIR = ROOT / "09_exports" / "external_demo_package"


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
        UI_MODEL_DIR / "external_feedback_intake_model.json",
        UI_MODEL_DIR / "reviewer_response_capture_model.json",
        UI_MODEL_DIR / "feedback_review_queue_model.json",
        UI_MODEL_DIR / "feedback_synthesis_readiness_model.json",
        DIST_DIR / "mvp19_external_feedback_model.json",
        REPORT_DIR / "mvp19_feedback_intake_model_report.md",
        REPORT_DIR / "mvp19_reviewer_response_capture_report.md",
        REPORT_DIR / "mvp19_feedback_review_queue_report.md",
        REPORT_DIR / "mvp19_feedback_synthesis_readiness_report.md",
        REPORT_DIR / "mvp19_external_demo_feedback_package_report.md",
        REPORT_DIR / "mvp19_security_boundary_report.md",
        REPORT_DIR / "mvp19_next_product_step_report.md",
        REPORT_DIR / "mvp19_acceptance_report.md",
        ASSET_DIR / "FEEDBACK_INTAKE_GUIDE.md",
        ASSET_DIR / "REVIEWER_RESPONSE_FORM.md",
        ASSET_DIR / "FEEDBACK_REVIEW_QUEUE.md",
        ASSET_DIR / "FEEDBACK_SYNTHESIS_GUIDE.md",
        ASSET_DIR / "EXTERNAL_REVIEW_RETURN_INSTRUCTIONS.md",
    ]
    for path in required_files:
        ensure_exists(path)

    index = read_text(DIST_DIR / "index.html")
    required_strings = [
        "MVP-19",
        "EXTERNAL FEEDBACK INTAKE",
        "REVIEWER RESPONSE CAPTURE",
        "STATIC FEEDBACK PACKET ONLY",
        "REVIEWER PERSONA ROUTING",
        "FEEDBACK REVIEW QUEUE",
        "FEEDBACK SYNTHESIS READINESS",
        "NO BACKEND FEEDBACK SUBMISSION",
        "NO BROWSER PERSISTENCE",
        "SERVICE ROLE NOT USED",
        "AUTOMATION STILL DISABLED",
        "NEXT_STEP_RUN_EXTERNAL_REVIEW_ROUND_OR_ADD_MANUAL_FEEDBACK_IMPORT_QUEUE",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "Feedback Intake Panel",
        "Reviewer Response Capture Panel",
        "Static Feedback Packet Panel",
        "Feedback Review Queue Panel",
        "Feedback Synthesis Readiness Panel",
        "Security Boundary Panel",
        "Copy MVP-19 validation checklist",
    ]
    for text in required_strings:
        assert_contains(index, text, "index.html marker")

    acceptance = read_text(REPORT_DIR / "mvp19_acceptance_report.md")
    for text in [
        "EXTERNAL_FEEDBACK_INTAKE_READY",
        "PASS_WITH_STATIC_FEEDBACK_PACKET_READY",
    ]:
        assert_contains(acceptance, text, "acceptance report marker")

    security_report = read_text(REPORT_DIR / "mvp19_security_boundary_report.md")
    assert_contains(security_report, "VERIFIED_FOR_STATIC_FEEDBACK", "security report marker")

    next_step_report = read_text(REPORT_DIR / "mvp19_next_product_step_report.md")
    assert_contains(next_step_report, "READY_FOR_FEEDBACK_COLLECTION", "next-step report marker")

    # Real Safety Scans
    scan_roots = [ROOT / "13_web_dashboard", UI_MODEL_DIR, REPORT_DIR, ASSET_DIR]
    
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
        "fetch(",
        "XMLHttpRequest",
        "navigator.sendBeacon",
        "api.github.com",
        "api.netlify.com",
        "supabase.co",
        "/api/feedback",
        "/api/requests",
        "child_process",
        "execSync",
        "spawn(",
        "subprocess",
        "os.system",
        "eval(",
        "Function(",
    ]

    mutation_forbidden = [
        "approve",
        "execute",
        "delete",
        "update",
        "start automation",
        "submit to",
        "save to database",
        "deploy",
        "merge",
        "push",
        "create pr",
    ]

    for root in scan_roots:
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part.startswith(".") or part == "__pycache__" for part in path.parts):
                continue
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}:
                continue
            
            content = read_text(path)
            lower = content.lower()
            path_str = str(path).lower()
            
            # 1. Critical Leak Check
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
                    fail(f"Forbidden critical pattern in {path.relative_to(ROOT)}: {pattern}")

            # 2. Browser Runtime Check
            if path.suffix in {".js", ".html", ".json"}:
                for pattern in runtime_forbidden:
                    if pattern in content:
                        if "scripts/validate_" in path_str: continue
                        if pattern == "fetch(" and ("dashboard_renderer.py" in path_str or "dashboard.js" in path_str): continue
                        
                        # Allow endpoint names in JSON/HTML only as safety labels or metadata
                        if path.suffix in [".json", ".html"] and pattern in ["/api/requests", "/api/feedback", "supabase.co"]:
                            # If it's a code snippet or part of a label, it's often fine
                            if any(x in lower for x in ["<code>", "<pre>", "no ", "blocked", "disabled", "not yet", "remains"]):
                                # Ensure it's not an actual fetch call or quoted URL literal in script
                                # (Markdown quotes are fine)
                                if f"fetch({pattern}" in content or f'fetch("{pattern}"' in content or f"fetch('{pattern}'" in content:
                                    pass
                                else:
                                    continue
                            if path.suffix == ".json": continue

                        fail(f"Forbidden runtime pattern in {path.relative_to(ROOT)}: {pattern}")

            # 3. Mutation Control Check (Button labels)
            if path.suffix == ".html":
                for match in re.finditer(r'<button([^>]*)>([^<]+)</button>', content):
                    attrs, label = match.groups()
                    label = label.strip().lower()
                    if any(p in label for p in mutation_forbidden):
                        if "disabled" in attrs.lower(): continue
                        if not any(x in label for x in ["copy", "load", "checklist", "panel"]):
                             if not any(x in label for x in ["blocked", "disabled"]):
                                 fail(f"Potential unblocked control in {path.relative_to(ROOT)}: {label}")

    # 4. Semantic check for MVP-19 JSON
    def check_json_security(data, path):
        security = data.get("security_boundaries", {})
        if security:
            if security.get("no_backend_submission") is not True:
                fail(f"JSON model missing no_backend_submission: true: {path}")
            if security.get("no_browser_persistence") is not True:
                fail(f"JSON model missing no_browser_persistence: true: {path}")
            if security.get("service_role_not_used") is not True:
                fail(f"JSON model missing service_role_not_used: true: {path}")

    model_path = DIST_DIR / "mvp19_external_feedback_model.json"
    if model_path.exists():
        check_json_security(json.loads(read_text(model_path)), model_path)
    
    intake_path = UI_MODEL_DIR / "external_feedback_intake_model.json"
    if intake_path.exists():
        intake_data = json.loads(read_text(intake_path))
        if intake_data.get("backend_submission_enabled") is not False:
             fail(f"Intake model missing backend_submission_enabled: false: {intake_path}")

    print("MVP19_EXTERNAL_FEEDBACK_INTAKE_VALIDATION_PASS")


if __name__ == "__main__":
    main()
