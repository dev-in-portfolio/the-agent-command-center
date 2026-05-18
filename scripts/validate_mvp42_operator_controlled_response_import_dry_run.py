#!/usr/bin/env python3
# MVP42_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

# MVP42_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT
# MVP42_NO_PUBLIC_ENDPOINT_CHECK
# MVP42_NO_LIVE_INTAKE_CHECK
# MVP42_NO_PUBLIC_RESPONSE_SUBMISSION_CHECK
# MVP42_NO_REVIEWER_RESPONSE_WRITES_CHECK
# MVP42_NO_RESPONSE_CAPTURE_ENABLED_CHECK
# MVP42_NO_RESPONSE_PERSISTENCE_ENABLED_CHECK
# MVP42_NO_REAL_IMPORT_CHECK
# MVP42_NO_AUTOMATIC_IMPORT_CHECK
# MVP42_NO_EMAIL_SENDING_CHECK
# MVP42_NO_REVIEWER_CONTACT_CHECK
# MVP42_NO_AUTOMATED_OUTREACH_CHECK
# MVP42_NO_LIVE_WRITES_CHECK
# MVP42_NO_PUBLIC_WRITES_CHECK
# MVP42_NO_TOKEN_INPUT_CHECK
# MVP42_NO_SECRETS_EXPOSED_CHECK
# MVP42_NO_SERVICE_ROLE_CHECK
# MVP42_NO_BROWSER_PERSISTENCE_CHECK
# MVP42_NO_DIRECT_SUPABASE_CHECK
# MVP42_NO_UPDATE_DELETE_APPROVE_EXECUTE_CHECK
# MVP42_OPERATOR_CONTROLLED_RESPONSE_IMPORT_DRY_RUN_EXPORT_ARTIFACTS_CHECK
# MVP42_NO_WHOLE_FILE_SAFETY_LABEL_SKIP

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.validation_helpers_control_scan import scan_text_for_dangerous_controls

FAILURES: list[str] = []

COMMON_FALSE_KEYS = [
    "public_endpoint_enabled",
    "live_intake_enabled",
    "public_response_submission_enabled",
    "reviewer_response_write_enabled",
    "response_capture_enabled",
    "response_persistence_enabled",
    "real_import_enabled",
    "automatic_import_enabled",
    "email_sending_enabled",
    "reviewer_contact_enabled",
    "automated_outreach_enabled",
    "contact_automation_enabled",
    "live_write_enabled",
    "public_write_enabled",
    "token_input_enabled",
    "secrets_exposed",
    "service_role_used",
    "browser_direct_supabase_calls",
    "browser_persistence_enabled",
    "automation_enabled",
    "deploy_controls_enabled",
    "launch_automation_enabled",
    "update_enabled",
    "delete_enabled",
    "approve_enabled",
    "execute_enabled",
    "deploy_merge_push_controls_enabled",
]

MODEL_REQUIREMENTS = [
    ("14_backend/product_runtime/ui_models/operator_controlled_response_import_dry_run_model.json", "operator_controlled_response_import_dry_run_ready"),
    ("14_backend/product_runtime/ui_models/dry_run_response_import_packet_model.json", "dry_run_response_import_packet_ready"),
    ("14_backend/product_runtime/ui_models/operator_import_preview_queue_model.json", "operator_import_preview_queue_ready"),
    ("14_backend/product_runtime/ui_models/dry_run_validation_result_model.json", "dry_run_validation_result_ready"),
    ("14_backend/product_runtime/ui_models/response_normalization_preview_model.json", "response_normalization_preview_ready"),
    ("14_backend/product_runtime/ui_models/response_to_feedback_conversion_preview_model.json", "response_to_feedback_conversion_preview_ready"),
    ("14_backend/product_runtime/ui_models/dry_run_audit_rollback_blueprint_model.json", "dry_run_audit_rollback_blueprint_ready"),
    ("13_web_dashboard/dist/mvp42_operator_controlled_response_import_dry_run_model.json", "operator_controlled_response_import_dry_run_ready"),
]

RELEASE_REQUIREMENTS = [
    "09_exports/release_package/mvp42_operator_controlled_response_import_dry_run.md",
    "09_exports/release_package/mvp42_dry_run_response_import_packet.md",
    "09_exports/release_package/mvp42_operator_import_preview_queue.md",
    "09_exports/release_package/mvp42_dry_run_validation_results.md",
    "09_exports/release_package/mvp42_response_normalization_preview.md",
    "09_exports/release_package/mvp42_response_to_feedback_conversion_preview.md",
    "09_exports/release_package/mvp42_dry_run_audit_rollback_blueprint.md",
    "09_exports/release_package/mvp42_operator_controlled_response_import_dry_run_manifest.json",
]

REPORT_REQUIREMENTS = [
    ("09_exports/mvp_product_track/mvp42_operator_controlled_response_import_dry_run_report.md", "OPERATOR_CONTROLLED_RESPONSE_IMPORT_DRY_RUN_READY"),
    ("09_exports/mvp_product_track/mvp42_dry_run_response_import_packet_report.md", "DRY_RUN_RESPONSE_IMPORT_PACKET_READY"),
    ("09_exports/mvp_product_track/mvp42_operator_import_preview_queue_report.md", "OPERATOR_IMPORT_PREVIEW_QUEUE_READY"),
    ("09_exports/mvp_product_track/mvp42_dry_run_validation_result_report.md", "DRY_RUN_VALIDATION_RESULT_READY"),
    ("09_exports/mvp_product_track/mvp42_response_normalization_preview_report.md", "RESPONSE_NORMALIZATION_PREVIEW_READY"),
    ("09_exports/mvp_product_track/mvp42_response_to_feedback_conversion_preview_report.md", "RESPONSE_TO_FEEDBACK_CONVERSION_PREVIEW_READY"),
    ("09_exports/mvp_product_track/mvp42_dry_run_audit_rollback_blueprint_report.md", "DRY_RUN_AUDIT_ROLLBACK_BLUEPRINT_READY"),
    ("09_exports/mvp_product_track/mvp42_security_boundary_report.md", "PASS"),
    ("09_exports/mvp_product_track/mvp42_next_product_step_report.md", "NEXT_STEP_BUILD_OPERATOR_RESPONSE_IMPORT_REVIEW_QUEUE_DRY_RUN"),
    ("09_exports/mvp_product_track/mvp42_validator_quality_report.md", "PASS"),
    ("09_exports/mvp_product_track/mvp42_acceptance_report.md", "OPERATOR_CONTROLLED_RESPONSE_IMPORT_DRY_RUN_READY"),
    ("09_exports/mvp_product_track/mvp42_validator_wall_review.md", "PASS"),
]

INDEX_MARKERS = [
    "MVP-42",
    "OPERATOR CONTROLLED RESPONSE IMPORT DRY RUN",
    "DRY RUN RESPONSE IMPORT PACKET",
    "OPERATOR IMPORT PREVIEW QUEUE",
    "DRY RUN VALIDATION RESULT",
    "RESPONSE NORMALIZATION PREVIEW",
    "RESPONSE TO FEEDBACK CONVERSION PREVIEW",
    "DRY RUN AUDIT ROLLBACK BLUEPRINT",
    "OPERATOR REVIEW ONLY",
    "DRY RUN ONLY",
    "PREVIEW ONLY",
    "FUTURE IMPLEMENTATION ONLY",
    "NO PUBLIC ENDPOINT",
    "NO LIVE INTAKE",
    "NO PUBLIC RESPONSE SUBMISSION",
    "NO REVIEWER RESPONSE WRITES",
    "NO RESPONSE CAPTURE ENABLED",
    "NO RESPONSE PERSISTENCE ENABLED",
    "NO REAL IMPORT",
    "NO AUTOMATIC IMPORT",
    "NO EMAIL SENDING",
    "NO REVIEWER CONTACT",
    "NO AUTOMATED OUTREACH",
    "NO LIVE WRITES",
    "NO PUBLIC WRITES",
    "NO TOKEN INPUT",
    "NO SECRETS EXPOSED",
    "SERVICE ROLE NOT USED",
    "UPDATE DELETE EXECUTE BLOCKED",
    "AUTOMATION STILL DISABLED",
    "NEXT_STEP_BUILD_OPERATOR_RESPONSE_IMPORT_REVIEW_QUEUE_DRY_RUN",
]

COPY_BUTTON_BINDINGS = [
    "mvp42-copy-import-dry-run",
    "mvp42-copy-import-packet",
    "mvp42-copy-preview-queue",
    "mvp42-copy-validation-results",
    "mvp42-copy-normalization-preview",
    "mvp42-copy-feedback-preview",
    "mvp42-copy-audit-rollback-blueprint",
]

FORBIDDEN_BUTTON_LABELS = [
    "submit",
    "save",
    "send",
    "capture response",
    "submit response",
    "save response",
    "persist response",
    "import response",
    "auto import",
    "run import",
    "execute import",
    "commit import",
    "send email",
    "email reviewer",
    "contact reviewer",
    "start outreach",
    "automate outreach",
    "automate review",
    "sync",
    "auto sync",
    "update roadmap",
    "create request",
    "create live request",
    "apply recommendation",
    "approve release",
    "execute release",
    "mark approved",
    "deploy",
    "merge",
    "push",
    "create pr",
    "launch",
    "publish",
    "execute",
    "approve",
    "apply migration",
    "enable writes",
    "token",
    "login",
    "connect supabase",
]

SAFE_BUTTON_LABELS = {
    "mvp-23 token-gated smoke test",
    "use token in memory",
    "clear token",
    "submit feedback packet manually",
}


def fail(message: str) -> None:
    FAILURES.append(message)
    print(f"  [FAIL] {message}")


def check(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def load_json(path: Path, label: str):
    if not path.is_file():
        fail(f"{label}: missing {path}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{label}: invalid JSON - {exc}")
        return None


def scan_text(path: Path, text: str) -> None:
    findings = scan_text_for_dangerous_controls(str(path.relative_to(ROOT)), text)
    if findings:
        fail(f"{path.relative_to(ROOT)}: {findings}")


def validate_model(path_str: str, ready_key: str) -> None:
    path = ROOT / path_str
    data = load_json(path, f"Model {path.name}")
    if data is None:
        return
    check(data.get("mvp") == 42, f"{path.name}: mvp is not 42")
    check(data.get("operator_review_only") is True, f"{path.name}: operator_review_only is not true")
    check(data.get("dry_run_only") is True, f"{path.name}: dry_run_only is not true")
    check(data.get("preview_only") is True, f"{path.name}: preview_only is not true")
    check(data.get("future_implementation_only") is True, f"{path.name}: future_implementation_only is not true")
    check(data.get(ready_key) is True, f"{path.name}: {ready_key} is not true")
    check(data.get("next_step") == "NEXT_STEP_BUILD_OPERATOR_RESPONSE_IMPORT_REVIEW_QUEUE_DRY_RUN", f"{path.name}: next_step mismatch")
    check(data.get("posture") == "dry-run-only", f"{path.name}: posture mismatch")
    for key in COMMON_FALSE_KEYS:
        check(key in data, f"{path.name}: missing {key}")
        check(data.get(key) is False, f"{path.name}: {key} is not false")
    scan_text(path, path.read_text(encoding="utf-8", errors="replace"))


def validate_release(path_str: str) -> None:
    path = ROOT / path_str
    check(path.is_file(), f"missing release artifact: {path_str}")
    text = path.read_text(encoding="utf-8", errors="replace")
    scan_text(path, text)


def validate_report(path_str: str, marker: str) -> None:
    path = ROOT / path_str
    check(path.is_file(), f"missing report: {path_str}")
    text = path.read_text(encoding="utf-8", errors="replace")
    check(marker in text, f"{path.name}: missing marker {marker}")
    scan_text(path, text)


def validate_dashboard() -> None:
    index_path = ROOT / "13_web_dashboard" / "dist" / "index.html"
    index = index_path.read_text(encoding="utf-8", errors="replace")
    scan_text(index_path, index)
    for marker in INDEX_MARKERS:
        check(marker in index, f"index.html missing marker: {marker}")

    forbidden_labels = [label.lower() for label in FORBIDDEN_BUTTON_LABELS]
    for match in re.finditer(r"(<button[^>]*>)([^<]+)(</button>)", index, re.IGNORECASE | re.DOTALL):
        tag, button_label, _closing = match.groups()
        if "disabled" in tag.lower() or 'aria-disabled="true"' in tag.lower():
            continue
        label = button_label.strip().lower()
        if label in SAFE_BUTTON_LABELS:
            continue
        if label.startswith("copy ") or label.startswith("load ") or label.startswith("phase ") or label.startswith("original +"):
            continue
        for forbidden in forbidden_labels:
            if forbidden in label:
                fail(f"index.html has forbidden enabled button label: {button_label.strip()}")
                break

    for path_name in [
        "13_web_dashboard/dist/print.html",
        "13_web_dashboard/dist/static/dashboard.js",
        "13_web_dashboard/static/dashboard.js",
        "13_web_dashboard/dashboard_renderer.py",
        "13_web_dashboard/dist/dashboard_data.json",
        "13_web_dashboard/dist/status_snapshot.json",
        "13_web_dashboard/dist/mvp42_operator_controlled_response_import_dry_run_model.json",
    ]:
        path = ROOT / path_name
        check(path.is_file(), f"missing dashboard file: {path_name}")
        scan_text(path, path.read_text(encoding="utf-8", errors="replace"))

    dashboard_js = (ROOT / "13_web_dashboard" / "static" / "dashboard.js").read_text(encoding="utf-8", errors="replace")
    dist_dashboard_js = (ROOT / "13_web_dashboard" / "dist" / "static" / "dashboard.js").read_text(encoding="utf-8", errors="replace")
    for binding in COPY_BUTTON_BINDINGS:
        check(binding in index, f"index.html missing MVP-42 copy button: {binding}")
        check(binding in dashboard_js, f"static dashboard.js missing MVP-42 copy binding: {binding}")
        check(binding in dist_dashboard_js, f"dist dashboard.js missing MVP-42 copy binding: {binding}")


def validate_manifest() -> None:
    path = ROOT / "09_exports" / "release_package" / "mvp42_operator_controlled_response_import_dry_run_manifest.json"
    data = load_json(path, "MVP-42 manifest")
    if data is None:
        return
    check(data.get("mvp") == 42, "manifest: mvp mismatch")
    check(data.get("package") == "mvp42_operator_controlled_response_import_dry_run", "manifest: package mismatch")
    check(data.get("status") == "dry-run-only", "manifest: status mismatch")
    check(data.get("next_step") == "NEXT_STEP_BUILD_OPERATOR_RESPONSE_IMPORT_REVIEW_QUEUE_DRY_RUN", "manifest: next_step mismatch")
    for key in ["operator_controlled_response_import_dry_run_ready", "dry_run_response_import_packet_ready", "operator_import_preview_queue_ready", "dry_run_validation_result_ready", "response_normalization_preview_ready", "response_to_feedback_conversion_preview_ready", "dry_run_audit_rollback_blueprint_ready"]:
        check(data.get(key) is True, f"manifest: {key} is not true")
    for key in COMMON_FALSE_KEYS:
        check(data.get(key) is False, f"manifest: {key} is not false")
    scan_text(path, path.read_text(encoding="utf-8", errors="replace"))


def main() -> None:
    for path_str, ready_key in MODEL_REQUIREMENTS:
        validate_model(path_str, ready_key)

    for path_str in RELEASE_REQUIREMENTS:
        validate_release(path_str)

    validate_manifest()
    validate_dashboard()

    for path_str, marker in REPORT_REQUIREMENTS:
        validate_report(path_str, marker)

    if FAILURES:
        print("MVP42_OPERATOR_CONTROLLED_RESPONSE_IMPORT_DRY_RUN_VALIDATION_FAIL")
        for failure in FAILURES:
            print(f"  - {failure}")
        raise SystemExit(1)

    print("MVP42_OPERATOR_CONTROLLED_RESPONSE_IMPORT_DRY_RUN_VALIDATION_PASS")


if __name__ == "__main__":
    main()
