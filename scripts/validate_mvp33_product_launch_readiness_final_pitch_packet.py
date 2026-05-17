#!/usr/bin/env python3

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "13_web_dashboard" / "dist"
REPORTS = ROOT / "09_exports" / "mvp_product_track"
EXPORTS = ROOT / "09_exports" / "release_package"
MODELS = ROOT / "14_backend" / "product_runtime" / "ui_models"

errors = []

def check(condition, message):
    if not condition:
        errors.append(message)

def file_contains(path, text):
    return path.exists() and text in path.read_text(encoding="utf-8", errors="replace")

# -- Models --
check(
    (MODELS / "product_launch_readiness_console_model.json").exists(),
    "missing product_launch_readiness_console_model.json",
)
check(
    (MODELS / "release_candidate_scorecard_model.json").exists(),
    "missing release_candidate_scorecard_model.json",
)
check(
    (MODELS / "final_pitch_packet_builder_model.json").exists(),
    "missing final_pitch_packet_builder_model.json",
)
check(
    (MODELS / "stakeholder_pitch_variant_model.json").exists(),
    "missing stakeholder_pitch_variant_model.json",
)
check(
    (MODELS / "operator_launch_decision_panel_model.json").exists(),
    "missing operator_launch_decision_panel_model.json",
)
check(
    (DIST / "mvp33_product_launch_readiness_final_pitch_packet_model.json").exists(),
    "missing mvp33_product_launch_readiness_final_pitch_packet_model.json",
)

for model_path in [
    MODELS / "product_launch_readiness_console_model.json",
    MODELS / "release_candidate_scorecard_model.json",
    MODELS / "final_pitch_packet_builder_model.json",
    MODELS / "stakeholder_pitch_variant_model.json",
    MODELS / "operator_launch_decision_panel_model.json",
    DIST / "mvp33_product_launch_readiness_final_pitch_packet_model.json",
]:
    if model_path.exists():
        data = json.loads(model_path.read_text(encoding="utf-8", errors="replace"))
        check(data.get("mvp") == "33", f"{model_path.name} mvp != 33")
        check(data.get("posture", {}).get("safe_launch_review_only") is True, f"{model_path.name} missing safe_launch_review_only")
        check(data.get("posture", {}).get("no_fake_launch_status") is True, f"{model_path.name} missing no_fake_launch_status")
        check(data.get("posture", {}).get("no_deploy_controls") is True, f"{model_path.name} missing no_deploy_controls")
        check(data.get("posture", {}).get("service_role_used") is False, f"{model_path.name} service_role_used is True")

# -- Reports --
report_checks = [
    ("mvp33_product_launch_readiness_console_report.md", "PRODUCT_LAUNCH_READINESS_CONSOLE_READY"),
    ("mvp33_final_pitch_packet_report.md", "FINAL_PITCH_PACKET_READY"),
    ("mvp33_release_candidate_scorecard_report.md", "RELEASE_CANDIDATE_SCORECARD_READY"),
    ("mvp33_stakeholder_pitch_variants_report.md", "STAKEHOLDER_PITCH_VARIANTS_READY"),
    ("mvp33_operator_launch_decision_panel_report.md", "OPERATOR_LAUNCH_DECISION_PANEL_READY"),
    ("mvp33_safety_readiness_one_pager_report.md", "SAFETY_READINESS_ONE_PAGER_READY"),
    ("mvp33_security_boundary_report.md", "SECURITY_BOUNDARY_INTACT"),
    ("mvp33_next_product_step_report.md", "NEXT_STEP_REVIEW_FINAL_PITCH_PACKET_AND_PREPARE_RELEASE_CANDIDATE"),
    ("mvp33_validator_quality_report.md", "PASS_WITH_SAFE_LAUNCH_REVIEW_ONLY"),
    ("mvp33_acceptance_report.md", "PRODUCT_LAUNCH_READINESS_FINAL_PITCH_PACKET_READY"),
    ("mvp33_validator_wall_review.md", "MVP-33 Wall Coverage Added"),
]
for filename, marker in report_checks:
    path = REPORTS / filename
    check(path.exists(), f"missing report: {filename}")
    if path.exists():
        check(marker in path.read_text(encoding="utf-8", errors="replace"), f"report missing marker: {filename} ({marker})")

# -- Release exports --
export_files = [
    "mvp33_final_pitch_packet.md",
    "mvp33_launch_readiness_console_summary.md",
    "mvp33_release_candidate_scorecard.md",
    "mvp33_founder_pitch_variant.md",
    "mvp33_recruiter_pitch_variant.md",
    "mvp33_technical_reviewer_pitch_variant.md",
    "mvp33_operator_demo_script.md",
    "mvp33_safety_readiness_one_pager.md",
    "mvp33_final_launch_review_packet.md",
    "mvp33_final_pitch_manifest.json",
]
for fname in export_files:
    check((EXPORTS / fname).exists(), f"missing release export: {fname}")

# -- Dashboard markers --
index_html = DIST / "index.html"
check(index_html.exists(), "missing index.html")
if index_html.exists():
    html = index_html.read_text(encoding="utf-8", errors="replace")
    check("MVP-33" in html, "index.html missing MVP-33")
    check("PRODUCT LAUNCH READINESS CONSOLE" in html, "index.html missing PRODUCT LAUNCH READINESS CONSOLE")
    check("RELEASE CANDIDATE SCORECARD" in html, "index.html missing RELEASE CANDIDATE SCORECARD")
    check("STAKEHOLDER PITCH VARIANTS" in html, "index.html missing STAKEHOLDER PITCH VARIANTS")
    check("OPERATOR LAUNCH DECISION PANEL" in html, "index.html missing OPERATOR LAUNCH DECISION PANEL")
    check("SAFE LAUNCH REVIEW ONLY" in html, "index.html missing SAFE LAUNCH REVIEW ONLY")
    check("NO FAKE LAUNCH STATUS" in html, "index.html missing NO FAKE LAUNCH STATUS")
    check("NO DEPLOY CONTROLS" in html, "index.html missing NO DEPLOY CONTROLS")
    check("NEXT_STEP_REVIEW_FINAL_PITCH_PACKET_AND_PREPARE_RELEASE_CANDIDATE" in html, "index.html missing next step marker")
    check("NOT_READY_FOR_REAL_AUTOMATION" in html, "index.html missing NOT_READY_FOR_REAL_AUTOMATION")

# -- Runtime patterns --
for js_path in [DIST / "static" / "dashboard.js", ROOT / "13_web_dashboard" / "static" / "dashboard.js"]:
    if js_path.exists():
        text = js_path.read_text(encoding="utf-8", errors="replace")
        check("initMvp33" in text, f"{js_path.name} missing initMvp33")
        check("mvp33-copy-launch-readiness-console" in text, f"{js_path.name} missing copy button binding")

# -- No fake buttons --
allowed_buttons = [
    "mvp33-copy-launch-readiness-console",
    "mvp33-copy-scorecard",
    "mvp33-copy-pitch-packet",
    "mvp33-copy-pitch-variants",
    "mvp33-copy-decision-panel",
]
forbidden_buttons = [
    "mvp33-launch",
    "mvp33-deploy",
    "mvp33-approve",
    "mvp33-execute",
    "mvp33-submit",
    "mvp33-send",
]
for js_path in [DIST / "static" / "dashboard.js", ROOT / "13_web_dashboard" / "static" / "dashboard.js"]:
    if js_path.exists():
        text = js_path.read_text(encoding="utf-8", errors="replace")
        for btn in forbidden_buttons:
            check(btn not in text, f"{js_path.name} contains forbidden button: {btn}")

# -- Safety posture checks --
for js_path in [DIST / "static" / "dashboard.js", ROOT / "13_web_dashboard" / "static" / "dashboard.js"]:
    if js_path.exists():
        text = js_path.read_text(encoding="utf-8", errors="replace")
        for token in [
            "serviceWorker",
            "sendBeacon",
        ]:
            check(token not in text, f"{js_path.name} contains forbidden token: {token}")

if errors:
    print("VALIDATION_FAIL")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)

print("MVP33_PRODUCT_LAUNCH_READINESS_FINAL_PITCH_PACKET_VALIDATION_PASS")
