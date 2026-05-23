#!/usr/bin/env python3
"""Validate MVP-61 5,000-agent department-gated runtime corps."""

from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent

errors = []


def check(condition, message):
    if not condition:
        errors.append(message)


def read(path):
    return path.read_text(encoding="utf-8", errors="replace")


def contains(path, *needles):
    text = read(path)
    for needle in needles:
      if needle not in text:
        errors.append(f"Missing string in {path.relative_to(ROOT)}: {needle}")


def missing(path):
    check(path.exists(), f"Missing file: {path.relative_to(ROOT)}")


def run_prerequisite():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_mvp60_department_gated_runtime_expansion.py")],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or "MVP60_DEPARTMENT_GATED_RUNTIME_EXPANSION_VALIDATION_PASS" not in result.stdout:
        errors.append("MVP-60 prerequisite did not pass.")


def main():
    run_prerequisite()

    migration = ROOT / "supabase" / "migrations" / "20260522_mvp61_5000_agent_department_gated_runtime_corps.sql"
    helper = ROOT / "netlify" / "functions" / "_shared" / "runtime_corps_helpers.js"
    list_fn = ROOT / "netlify" / "functions" / "list-runtime-corps.js"
    rollup_fn = ROOT / "netlify" / "functions" / "runtime-corps-rollup.js"
    activate_fn = ROOT / "netlify" / "functions" / "activate-runtime-corps-cohort.js"
    deactivate_fn = ROOT / "netlify" / "functions" / "deactivate-runtime-corps-cohort.js"
    activate_approved_fn = ROOT / "netlify" / "functions" / "activate-approved-department-cohort.js"
    deactivate_approved_fn = ROOT / "netlify" / "functions" / "deactivate-approved-department-cohort.js"
    heartbeat_fn = ROOT / "netlify" / "functions" / "runtime-corps-heartbeat.js"
    note_fn = ROOT / "netlify" / "functions" / "create-runtime-corps-readiness-note.js"
    ui = ROOT / "13_web_dashboard" / "dist" / "demo" / "runtime-corps.html"
    js = ROOT / "13_web_dashboard" / "dist" / "demo" / "assets" / "runtime-corps.js"
    demo_index = ROOT / "13_web_dashboard" / "dist" / "demo" / "index.html"
    root_index = ROOT / "13_web_dashboard" / "dist" / "index.html"
    report = ROOT / "09_exports" / "mvp_product_track" / "mvp61_5000_agent_department_gated_runtime_corps_report.md"

    for path in [migration, helper, list_fn, rollup_fn, activate_fn, deactivate_fn, activate_approved_fn, deactivate_approved_fn, heartbeat_fn, note_fn, ui, js, demo_index, root_index, report]:
        missing(path)

    if migration.exists():
      contains(
        migration,
        "runtime_corps_limits",
        "runtime_corps_cohorts",
        "runtime_corps_cohort_chunks",
        "runtime_corps_events",
        "runtime_corps_rollups",
        "mvp61_global_live_agent_cap",
        "max_cohort_activation_size",
        "max_operation_chunk_size",
        "department_gated_activation_required",
        "full_47979_activation_blocked",
        "command_execution_enabled",
        "deploy_execution_enabled",
        "rollback_execution_enabled",
        "alert_sending_enabled",
        "activate_runtime_corps_cohort",
        "deactivate_runtime_corps_cohort",
        "activate_approved_department_cohort",
        "deactivate_approved_department_cohort",
        "5,000 is a cap, not an automatic activation",
      )

    if helper.exists():
      contains(
        helper,
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "GLOBAL_LIVE_AGENT_CAP = 5000",
        "MAX_COHORT_ACTIVATION_SIZE = 500",
        "MAX_OPERATION_CHUNK_SIZE = 250",
        "buildCorpsRollup",
        "mergeCorpsGateRecords",
      )

    for path in [list_fn, rollup_fn, activate_fn, deactivate_fn, activate_approved_fn, deactivate_approved_fn, heartbeat_fn, note_fn]:
      contains(
        path,
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "runtime_corps",
      )

    contains(
      ui,
      "5,000-Agent Department-Gated Runtime Corps",
      "5,000 is a cap, not an automatic activation.",
      "Department-gated activation is required.",
      "Raw fleet activation is blocked.",
      "No department can run commands, deploys, rollbacks, alerts, or arbitrary actions from this page.",
      "Full 47,979-agent activation remains blocked.",
    )

    contains(
      js,
      "/.netlify/functions/list-runtime-corps",
      "/.netlify/functions/runtime-corps-rollup",
      "/.netlify/functions/activate-runtime-corps-cohort",
      "/.netlify/functions/deactivate-runtime-corps-cohort",
      "/.netlify/functions/activate-approved-department-cohort",
      "/.netlify/functions/deactivate-approved-department-cohort",
      "/.netlify/functions/runtime-corps-heartbeat",
      "/.netlify/functions/create-runtime-corps-readiness-note",
    )

    forbidden_js_tokens = [
      "SUPABASE_SERVICE_ROLE_KEY",
      "localStorage",
      "sessionStorage",
      "document.cookie",
      "indexedDB",
      "eval(",
      "new Function",
      "child_process",
      "exec(",
      "spawn(",
      "activate-all",
      "activate-47979",
      "/.netlify/functions/activate-all",
      "/.netlify/functions/activate-47979",
      "arbitrary SQL endpoint",
      "arbitrary command endpoint",
    ]
    js_text = read(js)
    for token in forbidden_js_tokens:
        check(token not in js_text, f"Forbidden browser JS token found: {token}")

    contains(
      demo_index,
      "5,000-Agent Runtime Corps",
      "./runtime-corps.html",
    )
    contains(
      root_index,
      "5,000-Agent Runtime Corps",
      "./demo/runtime-corps.html",
    )

    if report.exists():
      contains(
        report,
        "MVP61_5000_AGENT_DEPARTMENT_GATED_RUNTIME_CORPS_COMPLETE",
        "MVP60_PREREQUISITE_PASSED",
        "GLOBAL_LIVE_AGENT_CAP_5000",
        "MAX_COHORT_SIZE_500",
        "MAX_OPERATION_CHUNK_SIZE_250",
        "DEPARTMENT_GATED_ACTIVATION_REQUIRED",
        "RAW_5000_AGENT_ACTIVATION_BLOCKED",
        "FULL_47979_ACTIVATION_BLOCKED",
        "RUNTIME_CORPS_LIMITS_ADDED",
        "RUNTIME_CORPS_COHORTS_ADDED",
        "RUNTIME_CORPS_EVENTS_ADDED",
        "RUNTIME_CORPS_ROLLUPS_ADDED",
        "RUNTIME_CORPS_FUNCTIONS_ADDED",
        "RUNTIME_CORPS_UI_ADDED",
        "DEMO_HUB_LINK_ADDED",
        "FIVE_THOUSAND_IS_CAP_NOT_AUTOMATIC_COPY_ADDED",
        "DEPARTMENT_GATED_ACTIVATION_COPY_ADDED",
        "COMMAND_EXECUTION_DISABLED",
        "DEPLOY_EXECUTION_DISABLED",
        "ROLLBACK_EXECUTION_DISABLED",
        "ALERT_SENDING_DISABLED",
        "SERVICE_ROLE_SERVER_SIDE_ONLY",
        "NO_SERVICE_ROLE_IN_BROWSER",
        "NO_ARBITRARY_SQL_ENDPOINT_ADDED",
        "NO_ARBITRARY_COMMAND_ENDPOINT_ADDED",
      )

    if errors:
        for error in errors:
            print(f"VALIDATION_FAIL: {error}")
        sys.exit(1)

    print("MVP61_5000_AGENT_DEPARTMENT_GATED_RUNTIME_CORPS_VALIDATION_PASS")


if __name__ == "__main__":
    main()
