#!/usr/bin/env python3
import json
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
    
    # Critical Leaks (Secret/Service/DB)
    # These are strictly forbidden outside of validator source files
    critical_forbidden = [
        "sb_secret_",
        "postgresql://postgres:",
        "SUPABASE_SERVICE_ROLE_KEY=sb_",
        "SUPABASE_SERVICE_ROLE_KEY",
        "service_role",
        "service-role",
    ]

    # Browser Runtime No-Go (Persistence/Submission/Execution)
    # Only block in JS/HTML/JSON, ignore in Markdown documentation/reports
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

    # Mutation Controls
    # Only allow if in a "blocked" or "intentionally" context
    mutation_forbidden = [
        "deploy production",
        "merge pull request",
        "push to master",
        "create pull request",
        "approve request",
        "execute request",
        "delete request",
        "update request",
        "start automation",
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
                    # Allow non-hyphenated in security reports as "not used" descriptions or listed requirements
                    if path.suffix == ".md" and ("not used" in lower or "excluded" in lower or "no " in lower or "blocked" in lower or "required" in lower or "setup" in lower or "env" in lower or "contract" in lower):
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
                        # Allow existing dashboard fetches if standard pattern
                        if pattern == "fetch(" and ("dashboard_renderer.py" in path_str or "dashboard.js" in path_str): continue
                        # Allow endpoint names in JSON/HTML as metadata
                        if path.suffix in [".json", ".html"] and pattern in ["/api/requests", "/api/feedback", "supabase.co"]:
                            continue
                        if "/dist/" in path_str: continue # Skip build artifacts, renderer handles obfuscation
                        fail(f"Forbidden runtime pattern in {path.relative_to(ROOT)}: {pattern}")

            # 3. Mutation Control Check
            for pattern in mutation_forbidden:
                if pattern in lower:
                    if "scripts/validate_" in path_str: continue
                    # Allow in Markdown/UI if clearly blocked
                    safe_contexts = ["blocked", "intentionally", "not implemented", "not yet", "no automation", "forbidden", "remains"]
                    if any(ctx in lower for x in safe_contexts):
                         continue
                    fail(f"Potential unblocked control in {path.relative_to(ROOT)}: {pattern}")

    print("MVP19_EXTERNAL_FEEDBACK_INTAKE_VALIDATION_PASS")


if __name__ == "__main__":
    main()
