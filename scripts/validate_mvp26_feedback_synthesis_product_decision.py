#!/usr/bin/env python3
import json
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
        UI_MODEL_DIR / "feedback_synthesis_workspace_model.json",
        UI_MODEL_DIR / "feedback_theme_cluster_model.json",
        UI_MODEL_DIR / "product_decision_card_model.json",
        UI_MODEL_DIR / "feedback_to_product_signal_model.json",
        DIST_DIR / "mvp26_feedback_synthesis_product_decision_model.json",
        REPORT_DIR / "mvp26_feedback_synthesis_workspace_report.md",
        REPORT_DIR / "mvp26_theme_clustering_report.md",
        REPORT_DIR / "mvp26_product_decision_cards_report.md",
        REPORT_DIR / "mvp26_signal_strength_report.md",
        REPORT_DIR / "mvp26_security_boundary_report.md",
        REPORT_DIR / "mvp26_next_product_step_report.md",
        REPORT_DIR / "mvp26_validator_quality_report.md",
        REPORT_DIR / "mvp26_acceptance_report.md",
        REPORT_DIR / "mvp26_validator_wall_review.md",
    ]
    for path in required_files:
        ensure_exists(path)

    acceptance = read_text(REPORT_DIR / "mvp26_acceptance_report.md")
    for marker in [
        "FEEDBACK_SYNTHESIS_PRODUCT_DECISION_WORKFLOW_READY",
        "PASS_WITH_READ_ONLY_MANUAL_SYNTHESIS",
        "FEEDBACK_SYNTHESIS_WORKSPACE_READY",
        "THEME_CLUSTERING_READY",
        "PRODUCT_DECISION_CARDS_READY",
        "SIGNAL_STRENGTH_SCORING_READY",
        "OWNER_SCOPED_FEEDBACK_READS",
        "SERVICE_ROLE_NOT_USED",
        "UPDATE_DELETE_EXECUTE_BLOCKED",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_BUILD_FEEDBACK_TO_REQUEST_CONVERSION_WORKSPACE",
    ]:
        assert_contains(acceptance, marker, f"acceptance marker {marker}")

    index = read_text(DIST_DIR / "index.html")
    for marker in [
        "MVP-26",
        "FEEDBACK SYNTHESIS WORKSPACE",
        "THEME CLUSTERING",
        "PRODUCT DECISION CARDS",
        "SIGNAL STRENGTH SCORING",
        "READ ONLY SYNTHESIS QUEUE",
        "OWNER-SCOPED FEEDBACK READS",
        "SERVICE ROLE NOT USED",
        "UPDATE DELETE EXECUTE BLOCKED",
        "AUTOMATION STILL DISABLED",
        "NEXT_STEP_BUILD_FEEDBACK_TO_REQUEST_CONVERSION_WORKSPACE",
        "NOT_READY_FOR_REAL_AUTOMATION",
    ]:
        assert_contains(index, marker, f"index marker {marker}")

    model_paths = [
        UI_MODEL_DIR / "feedback_synthesis_workspace_model.json",
        UI_MODEL_DIR / "feedback_theme_cluster_model.json",
        UI_MODEL_DIR / "product_decision_card_model.json",
        UI_MODEL_DIR / "feedback_to_product_signal_model.json",
        DIST_DIR / "mvp26_feedback_synthesis_product_decision_model.json",
    ]
    for path in model_paths:
        data = json.loads(read_text(path))
        for key in [
            "feedback_synthesis_workspace_ready",
            "theme_clustering_ready",
            "product_decision_cards_ready",
            "signal_strength_scoring_ready",
            "read_only_synthesis_queue",
            "owner_scoped_feedback_reads",
        ]:
            if key in data and data[key] is not True:
                fail(f"{path.name} gate not true: {key}")
        for key in [
            "service_role_used",
            "browser_direct_supabase_calls",
            "update_enabled",
            "delete_enabled",
            "automation_enabled",
        ]:
            if key in data and data[key] is not False:
                fail(f"{path.name} forbidden flag not false: {key}")
        for key in [
            "does_not_enable_feature_flag",
            "does_not_apply_migration",
            "does_not_store_token",
            "does_not_print_token",
        ]:
            if key in data and data[key] is not True:
                fail(f"{path.name} gate not true: {key}")

    # Dashboard/runtime safety scan
    scan_roots = [ROOT / "13_web_dashboard", UI_MODEL_DIR, REPORT_DIR, SCRIPT_DIR, ROOT / "netlify" / "functions"]
    forbidden_tokens = [
        "localStorage.setItem",
        "localStorage.getItem",
        "sessionStorage.setItem",
        "sessionStorage.getItem",
        "document.cookie =",
        "indexedDB.open",
        "api.github.com",
        "api.netlify.com",
        "child_process",
        "execSync",
        "spawn(",
        "os.system",
        "eval(",
        "Function(",
        "createClient(",
        "supabase.createClient",
        'fetch("https://',
        "fetch('https://",
        "fetch(`https://",
        "axios.get(",
        "axios.post(",
        "XMLHttpRequest",
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
            path_str = str(path).lower()
            if "scripts/validate_" in path_str:
                continue
            if "sb_secret_" in content or "postgresql://postgres:" in content or "SUPABASE_SERVICE_ROLE_KEY=sb_" in content:
                fail(f"Forbidden secret pattern in {path}")

            if path.suffix in {".js", ".html"} and "13_web_dashboard" in path_str:
                for token in forbidden_tokens:
                    if token in content:
                        fail(f"Forbidden dashboard/runtime token in {path}: {token}")

            if path.suffix == ".json" and "mvp26" in path_str:
                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    continue

                def walk(obj):
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            lower = key.lower()
                            if lower == "service_role_used" and value is True:
                                fail(f"Forbidden service_role_used flag in {path}")
                            if lower == "browser_direct_supabase_calls" and value is True:
                                fail(f"Forbidden browser_direct_supabase_calls flag in {path}")
                            if lower == "update_enabled" and value is True:
                                fail(f"Forbidden update_enabled flag in {path}")
                            if lower == "delete_enabled" and value is True:
                                fail(f"Forbidden delete_enabled flag in {path}")
                            if lower == "automation_enabled" and value is True:
                                fail(f"Forbidden automation_enabled flag in {path}")
                            walk(value)
                    elif isinstance(obj, list):
                        for value in obj:
                            walk(value)

                walk(data)

    print("MVP26_FEEDBACK_SYNTHESIS_PRODUCT_DECISION_VALIDATION_PASS")


if __name__ == "__main__":
    main()
