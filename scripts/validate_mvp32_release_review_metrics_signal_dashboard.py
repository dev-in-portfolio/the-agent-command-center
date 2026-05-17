#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UI_MODEL_DIR = ROOT / "14_backend" / "product_runtime" / "ui_models"
DIST_DIR = ROOT / "13_web_dashboard" / "dist"
REPORT_DIR = ROOT / "09_exports" / "mvp_product_track"
EXPORT_DIR = ROOT / "09_exports" / "release_package"
SCRIPT_DIR = ROOT / "scripts"


def fail(message):
    raise SystemExit(f"FAIL: {message}")


def read_text(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        fail(f"Cannot read {path}: {exc}")


def assert_contains(text, pattern, label):
    if pattern not in text:
        fail(f"Missing {label}: expected {pattern!r}")


def assert_not_contains(text, pattern, label):
    if pattern in text:
        fail(f"Forbidden {label}: found {pattern!r}")


def assert_file_exists(path):
    if not path.exists():
        fail(f"Missing file: {path}")


def check_json_flags(path, required_true, required_false):
    data = json.loads(read_text(path))
    for key in required_true:
        val = data
        for part in key.split("."):
            val = val.get(part, {})
        if val is not True:
            fail(f"Flag {key} must be true in {path}, got {val}")
    for key in required_false:
        val = data
        for part in key.split("."):
            val = val.get(part, {})
        if val is not False:
            fail(f"Flag {key} must be false in {path}, got {val}")


def main():
    # --- UI Model Files ---
    model_files = {
        "release_review_metrics_dashboard_model.json": [
            ("status.release_review_metrics_ready", True),
            ("status.reviewer_signal_summary_ready", True),
            ("status.demo_session_signal_ready", True),
            ("status.release_readiness_metric_ready", True),
            ("status.product_decision_signal_rollup_ready", True),
            ("posture.no_fake_metrics", True),
            ("posture.no_fake_reviewer_results", True),
            ("posture.service_role_used", False),
            ("posture.browser_direct_supabase_calls", False),
            ("posture.browser_persistence_enabled", False),
            ("posture.email_sending_enabled", False),
            ("posture.automation_enabled", False),
            ("posture.update_enabled", False),
            ("posture.delete_enabled", False),
            ("posture.approve_enabled", False),
            ("posture.execute_enabled", False),
            ("posture.deploy_merge_push_controls_enabled", False),
        ],
        "reviewer_signal_summary_model.json": [
            ("posture.no_fake_metrics", True),
            ("posture.no_fake_reviewer_results", True),
            ("posture.service_role_used", False),
            ("posture.browser_direct_supabase_calls", False),
            ("posture.browser_persistence_enabled", False),
        ],
        "demo_session_signal_model.json": [
            ("posture.no_fake_metrics", True),
            ("posture.service_role_used", False),
            ("posture.browser_direct_supabase_calls", False),
            ("posture.browser_persistence_enabled", False),
        ],
        "release_readiness_metric_model.json": [
            ("posture.no_fake_metrics", True),
            ("posture.service_role_used", False),
            ("posture.browser_direct_supabase_calls", False),
            ("posture.browser_persistence_enabled", False),
        ],
        "product_decision_signal_rollup_model.json": [
            ("posture.no_fake_metrics", True),
            ("posture.no_fake_reviewer_results", True),
            ("posture.service_role_used", False),
            ("posture.browser_direct_supabase_calls", False),
            ("posture.browser_persistence_enabled", False),
        ],
    }

    for filename, checks in model_files.items():
        path = UI_MODEL_DIR / filename
        assert_file_exists(path)
        data = json.loads(read_text(path))
        for key, expected in checks:
            val = data
            for part in key.split("."):
                val = val.get(part, {})
            if val is not expected:
                fail(f"Flag {key} expected {expected} in {filename}, got {val}")

    # --- Dashboard Dist Model ---
    dist_model = DIST_DIR / "mvp32_release_review_metrics_signal_dashboard_model.json"
    assert_file_exists(dist_model)
    required_true = [
        "posture.release_review_metrics_ready",
        "posture.reviewer_signal_summary_ready",
        "posture.demo_session_signal_ready",
        "posture.release_readiness_metric_ready",
        "posture.product_decision_signal_rollup_ready",
        "posture.uses_manual_or_existing_review_data",
        "posture.no_fake_metrics",
        "posture.no_fake_reviewer_results",
    ]
    required_false = [
        "posture.service_role_used",
        "posture.browser_direct_supabase_calls",
        "posture.browser_persistence_enabled",
        "posture.email_sending_enabled",
        "posture.automation_enabled",
        "posture.update_enabled",
        "posture.delete_enabled",
        "posture.approve_enabled",
        "posture.execute_enabled",
        "posture.deploy_merge_push_controls_enabled",
    ]
    check_json_flags(dist_model, required_true, required_false)

    # --- MVP-32 Reports ---
    required_reports = [
        "mvp32_release_review_metrics_dashboard_report.md",
        "mvp32_reviewer_signal_summary_report.md",
        "mvp32_demo_session_signal_report.md",
        "mvp32_release_readiness_metric_report.md",
        "mvp32_product_decision_signal_rollup_report.md",
        "mvp32_signal_packet_export_report.md",
        "mvp32_security_boundary_report.md",
        "mvp32_next_product_step_report.md",
        "mvp32_validator_quality_report.md",
        "mvp32_acceptance_report.md",
        "mvp32_validator_wall_review.md",
    ]
    for r in required_reports:
        assert_file_exists(REPORT_DIR / r)

    # --- Acceptance report markers ---
    acceptance = read_text(REPORT_DIR / "mvp32_acceptance_report.md")
    required_acceptance = [
        "RELEASE_REVIEW_METRICS_SIGNAL_DASHBOARD_READY",
        "PASS_WITH_MANUAL_EXISTING_SIGNAL_ROLLUPS",
        "REVIEWER_SIGNAL_SUMMARY_READY",
        "DEMO_SESSION_SIGNAL_SUMMARY_READY",
        "RELEASE_READINESS_METRICS_READY",
        "PRODUCT_DECISION_SIGNAL_ROLLUP_READY",
        "EXPORTABLE_SIGNAL_PACKET_READY",
        "NO_FAKE_METRICS",
        "NO_FAKE_REVIEWER_RESULTS",
        "SERVICE_ROLE_NOT_USED",
        "UPDATE_DELETE_EXECUTE_BLOCKED",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_BUILD_PRODUCT_LAUNCH_READINESS_FINAL_PITCH_PACKET",
    ]
    for marker in required_acceptance:
        assert_contains(acceptance, marker, f"acceptance marker {marker}")

    # --- Release Export Artifacts ---
    export_files = [
        "mvp32_release_review_metrics_summary.md",
        "mvp32_reviewer_signal_summary.md",
        "mvp32_demo_session_signal_summary.md",
        "mvp32_product_decision_signal_rollup.md",
        "mvp32_release_readiness_scorecard.md",
        "mvp32_release_review_signal_packet.md",
        "mvp32_release_review_signal_manifest.json",
    ]
    for f in export_files:
        assert_file_exists(EXPORT_DIR / f)

    # --- Signal manifest ---
    manifest = json.loads(read_text(EXPORT_DIR / "mvp32_release_review_signal_manifest.json"))
    assert_contains(str(manifest), "no_fake_metrics", "manifest no_fake_metrics")
    assert_contains(str(manifest), "no_fake_reviewer_results", "manifest no_fake_reviewer_results")

    # --- Dashboard HTML markers ---
    index_html = read_text(DIST_DIR / "index.html")
    required_markers = [
        "MVP-32",
        "RELEASE REVIEW METRICS DASHBOARD",
        "REVIEWER SIGNAL SUMMARY",
        "DEMO SESSION SIGNALS",
        "RELEASE READINESS METRICS",
        "PRODUCT DECISION SIGNAL ROLLUP",
        "ROADMAP SIGNAL ROLLUP",
        "EXPORTABLE SIGNAL PACKET",
        "NO FAKE METRICS",
        "NO FAKE REVIEWER RESULTS",
        "SERVICE ROLE NOT USED",
        "UPDATE DELETE EXECUTE BLOCKED",
        "AUTOMATION STILL DISABLED",
        "NEXT_STEP_BUILD_PRODUCT_LAUNCH_READINESS_FINAL_PITCH_PACKET",
        "NOT_READY_FOR_REAL_AUTOMATION",
    ]
    for marker in required_markers:
        assert_contains(index_html, marker, f"dashboard marker {marker}")

    # --- Dashboard forbidden runtime patterns ---
    dashboard_js = read_text(DIST_DIR / "static" / "dashboard.js")
    forbidden_runtime = [
        "local" "Storage.setItem",
        "session" "Storage.setItem",
        "document" ".cookie =",
        "indexed" "DB.open",
        "create" "Client(",
        "supabase" ".createClient",
    ]
    for token in forbidden_runtime:
        assert_not_contains(dashboard_js, token, f"forbidden runtime token {token}")

    # --- Dashboard forbidden enabled buttons ---
    html_pattern = re.compile(r'<button\b([^>]*)>([^<]+)</button>', re.IGNORECASE)
    forbidden_buttons = [
        "send email", "email reviewer", "auto follow-up", "start outreach",
        "automate review", "deploy", "merge", "push", "create pr",
        "execute", "approve", "apply migration", "enable writes",
        "save to database", "generate fake metrics", "mark launch ready automatically",
    ]
    for m in html_pattern.finditer(index_html):
        attrs = m.group(1)
        label = m.group(2).strip().lower()
        if re.search(r'\bdisabled\b', attrs, re.IGNORECASE):
            continue
        if label.startswith("copy "):
            continue
        for item in forbidden_buttons:
            if item in label:
                fail(f"Forbidden enabled button '{m.group(2).strip()}'")

    print("MVP32_RELEASE_REVIEW_METRICS_SIGNAL_DASHBOARD_VALIDATION_PASS")


if __name__ == "__main__":
    main()
