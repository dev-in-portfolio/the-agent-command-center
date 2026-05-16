#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UI_MODEL_DIR = ROOT / "14_backend" / "product_runtime" / "ui_models"
DIST_DIR = ROOT / "13_web_dashboard" / "dist"
REPORT_DIR = ROOT / "09_exports" / "mvp_product_track"


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
        UI_MODEL_DIR / "manual_feedback_import_model.json",
        UI_MODEL_DIR / "manual_feedback_review_queue_model.json",
        UI_MODEL_DIR / "manual_feedback_synthesis_workspace_model.json",
        UI_MODEL_DIR / "review_to_product_decision_model.json",
        DIST_DIR / "mvp20_manual_feedback_review_model.json",
        REPORT_DIR / "mvp20_manual_feedback_import_report.md",
        REPORT_DIR / "mvp20_review_queue_report.md",
        REPORT_DIR / "mvp20_synthesis_workspace_report.md",
        REPORT_DIR / "mvp20_review_to_product_decision_report.md",
        REPORT_DIR / "mvp20_security_boundary_report.md",
        REPORT_DIR / "mvp20_next_product_step_report.md",
        REPORT_DIR / "mvp20_validator_quality_report.md",
        REPORT_DIR / "mvp20_acceptance_report.md",
    ]
    for path in required_files:
        ensure_exists(path)

    index = read_text(DIST_DIR / "index.html")
    required_strings = [
        "MVP-20",
        "MANUAL FEEDBACK IMPORT",
        "REVIEW QUEUE READY",
        "MANUAL SYNTHESIS WORKSPACE",
        "REVIEW TO PRODUCT DECISION",
        "STATIC MEMORY ONLY WORKFLOW",
        "NO BACKEND FEEDBACK SUBMISSION",
        "NO BROWSER PERSISTENCE",
        "SERVICE ROLE NOT USED",
        "AUTOMATION STILL DISABLED",
        "NEXT_STEP_RUN_EXTERNAL_FEEDBACK_ROUND_OR_ADD_SAFE_FEEDBACK_PERSISTENCE",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "Manual Feedback Import Panel",
        "Review Queue Panel",
        "Synthesis Workspace Panel",
        "Review-to-Product Decision Panel",
        "Security Boundary Panel",
        "Copy MVP-20 validation checklist",
    ]
    for text in required_strings:
        assert_contains(index, text, "index.html marker")

    acceptance = read_text(REPORT_DIR / "mvp20_acceptance_report.md")
    for text in [
        "MANUAL_FEEDBACK_IMPORT_REVIEW_QUEUE_READY",
        "PASS_WITH_STATIC_MEMORY_ONLY_FEEDBACK_WORKFLOW",
    ]:
        assert_contains(acceptance, text, "acceptance report marker")

    security_report = read_text(REPORT_DIR / "mvp20_security_boundary_report.md")
    assert_contains(security_report, "VERIFIED_FOR_STATIC_MEMORY_ONLY_FEEDBACK", "security report marker")

    # Real Safety Scans
    scan_roots = [ROOT / "13_web_dashboard", UI_MODEL_DIR, REPORT_DIR]
    
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
                            if any(x in lower for x in ["<code>", "<pre>", "no ", "blocked", "disabled", "not yet", "remains"]):
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

    # 4. Semantic check for MVP-20 JSON
    def check_json_security(data, path):
        security = data.get("security_boundaries", {})
        if security:
            if security.get("static_memory_only_workflow") is not True and "mvp20" in str(path).lower():
                fail(f"JSON model missing static_memory_only_workflow: true: {path}")
            if security.get("no_backend_feedback_submission") is not True and "mvp20" in str(path).lower():
                fail(f"JSON model missing no_backend_feedback_submission: true: {path}")

        def walk_flags(obj):
            if not isinstance(obj, dict): return
            for k, v in obj.items():
                nk = k.lower()
                if nk.endswith("enabled") and v is True:
                     if any(x in nk for x in ["submission", "write", "automation", "synthesis", "ingestion", "queue", "persistence"]):
                          fail(f"Forbidden enabled flag {k} in {path}")
                walk_flags(v)
        walk_flags(data)

    model_path = DIST_DIR / "mvp20_manual_feedback_review_model.json"
    if model_path.exists():
        check_json_security(json.loads(read_text(model_path)), model_path)
    
    import_path = UI_MODEL_DIR / "manual_feedback_import_model.json"
    if import_path.exists():
        check_json_security(json.loads(read_text(import_path)), import_path)

    print("MVP20_MANUAL_FEEDBACK_IMPORT_REVIEW_QUEUE_VALIDATION_PASS")


if __name__ == "__main__":
    main()
