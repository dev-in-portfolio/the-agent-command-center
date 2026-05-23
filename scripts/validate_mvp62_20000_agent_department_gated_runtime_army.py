#!/usr/bin/env python3
"""Validate MVP-62 20,000-agent department-gated runtime army."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def read_text(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.is_file():
      raise AssertionError(f"Missing required file: {relative_path}")
    return path.read_text(encoding="utf-8", errors="replace")


def assert_contains(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing required string in {label}: {needle}")


def assert_not_contains(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"Forbidden string in {label}: {needle}")


def run_prereq_validator() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/validate_mvp61_5000_agent_department_gated_runtime_corps.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            "MVP-61 prerequisite validator failed before MVP-62 validation.\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    if "MVP61_5000_AGENT_DEPARTMENT_GATED_RUNTIME_CORPS_VALIDATION_PASS" not in result.stdout:
        raise AssertionError("MVP-61 prerequisite validator did not emit the expected pass string.")


def main() -> None:
    run_prereq_validator()

    migration_path = "supabase/migrations/20260522_mvp62_20000_agent_department_gated_runtime_army.sql"
    helper_path = "netlify/functions/_shared/runtime_army_helpers.js"
    list_fn = "netlify/functions/list-runtime-army.js"
    rollup_fn = "netlify/functions/runtime-army-rollup.js"
    unlock_fn = "netlify/functions/unlock-runtime-army-stage.js"
    activate_fn = "netlify/functions/activate-runtime-army-cohort.js"
    deactivate_fn = "netlify/functions/deactivate-runtime-army-cohort.js"
    activate_department_fn = "netlify/functions/activate-approved-department-army-cohort.js"
    deactivate_department_fn = "netlify/functions/deactivate-approved-department-army-cohort.js"
    heartbeat_fn = "netlify/functions/runtime-army-heartbeat.js"
    note_fn = "netlify/functions/create-runtime-army-readiness-note.js"
    breaker_fn = "netlify/functions/runtime-army-circuit-breaker.js"
    ui_path = "13_web_dashboard/dist/demo/runtime-army.html"
    js_path = "13_web_dashboard/dist/demo/assets/runtime-army.js"
    demo_index = "13_web_dashboard/dist/demo/index.html"
    root_index = "13_web_dashboard/dist/index.html"
    report_path = "09_exports/mvp_product_track/mvp62_20000_agent_department_gated_runtime_army_report.md"

    for path in [
        migration_path,
        helper_path,
        list_fn,
        rollup_fn,
        unlock_fn,
        activate_fn,
        deactivate_fn,
        activate_department_fn,
        deactivate_department_fn,
        heartbeat_fn,
        note_fn,
        breaker_fn,
        ui_path,
        js_path,
        demo_index,
        root_index,
        report_path,
    ]:
        if not (ROOT / path).exists():
            raise AssertionError(f"Missing required file: {path}")

    migration = read_text(migration_path)
    helper = read_text(helper_path)
    browser_js = read_text(js_path)
    ui = read_text(ui_path)
    demo = read_text(demo_index)
    root = read_text(root_index)
    report = read_text(report_path)
    list_text = read_text(list_fn)
    rollup_text = read_text(rollup_fn)
    unlock_text = read_text(unlock_fn)
    activate_text = read_text(activate_fn)
    deactivate_text = read_text(deactivate_fn)
    activate_department_text = read_text(activate_department_fn)
    deactivate_department_text = read_text(deactivate_department_fn)
    heartbeat_text = read_text(heartbeat_fn)
    note_text = read_text(note_fn)
    breaker_text = read_text(breaker_fn)

    for needle in [
        "runtime_army_limits",
        "runtime_army_stages",
        "runtime_army_cohorts",
        "runtime_army_circuit_breakers",
        "runtime_army_health_rollups",
        "runtime_army_events",
        "mvp62_global_live_agent_cap",
        "20000",
        "max_cohort_activation_size",
        "1000",
        "max_operation_chunk_size",
        "500",
        "staged_activation_required",
        "circuit_breaker_required",
        "department_gated_activation_required",
        "full_47979_activation_blocked",
        "command_execution_enabled",
        "deploy_execution_enabled",
        "rollback_execution_enabled",
        "alert_sending_enabled",
        "create or replace function unlock_runtime_army_stage",
        "create or replace function runtime_army_activate_department_cohort",
        "create or replace function runtime_army_deactivate_cohort",
        "create or replace function deactivate_approved_department_army_cohorts",
        "create or replace function runtime_army_trigger_circuit_breaker",
        "create or replace function runtime_army_clear_circuit_breaker",
        "create or replace function runtime_army_record_heartbeat",
        "create or replace function runtime_army_create_readiness_note",
        "Stage 1",
        "Stage 2",
        "Stage 3",
        "Stage 4",
        "5,000",
        "10,000",
        "15,000",
        "20,000",
        "20,000 is a cap, not an automatic activation",
        "Department-gated activation is required",
        "Staged unlocks are required",
        "Circuit breakers pause further activation",
        "Raw fleet activation is blocked",
    ]:
        assert_contains(migration, needle, "mvp62 migration")

    for needle in [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "GLOBAL_LIVE_AGENT_CAP = 20000",
        "MAX_COHORT_ACTIVATION_SIZE = 1000",
        "MAX_DEPARTMENT_ACTIVATION_CAP = 500",
        "MAX_OPERATION_CHUNK_SIZE = 500",
        "buildArmyRollup",
        "mergeArmyGateRecords",
    ]:
        assert_contains(helper, needle, "runtime army helper")

    for text, label in [
        (list_text, list_fn),
        (rollup_text, rollup_fn),
        (unlock_text, unlock_fn),
        (activate_text, activate_fn),
        (deactivate_text, deactivate_fn),
        (activate_department_text, activate_department_fn),
        (deactivate_department_text, deactivate_department_fn),
        (heartbeat_text, heartbeat_fn),
        (note_text, note_fn),
        (breaker_text, breaker_fn),
    ]:
        assert_contains(text, "runtime_army", label)

    for endpoint in [
        "/.netlify/functions/list-runtime-army",
        "/.netlify/functions/runtime-army-rollup",
        "/.netlify/functions/unlock-runtime-army-stage",
        "/.netlify/functions/activate-runtime-army-cohort",
        "/.netlify/functions/deactivate-runtime-army-cohort",
        "/.netlify/functions/activate-approved-department-army-cohort",
        "/.netlify/functions/deactivate-approved-department-army-cohort",
        "/.netlify/functions/runtime-army-heartbeat",
        "/.netlify/functions/create-runtime-army-readiness-note",
        "/.netlify/functions/runtime-army-circuit-breaker",
    ]:
        assert_contains(browser_js, endpoint, "runtime-army.js")

    actual_endpoints = set()
    for line in browser_js.splitlines():
        if "/.netlify/functions/" not in line:
            continue
        for endpoint in [
            "/.netlify/functions/list-runtime-army",
            "/.netlify/functions/runtime-army-rollup",
            "/.netlify/functions/unlock-runtime-army-stage",
            "/.netlify/functions/activate-runtime-army-cohort",
            "/.netlify/functions/deactivate-runtime-army-cohort",
            "/.netlify/functions/activate-approved-department-army-cohort",
            "/.netlify/functions/deactivate-approved-department-army-cohort",
            "/.netlify/functions/runtime-army-heartbeat",
            "/.netlify/functions/create-runtime-army-readiness-note",
            "/.netlify/functions/runtime-army-circuit-breaker",
        ]:
            if endpoint in line:
                actual_endpoints.add(endpoint)
    expected_endpoints = {
        "/.netlify/functions/list-runtime-army",
        "/.netlify/functions/runtime-army-rollup",
        "/.netlify/functions/unlock-runtime-army-stage",
        "/.netlify/functions/activate-runtime-army-cohort",
        "/.netlify/functions/deactivate-runtime-army-cohort",
        "/.netlify/functions/activate-approved-department-army-cohort",
        "/.netlify/functions/deactivate-approved-department-army-cohort",
        "/.netlify/functions/runtime-army-heartbeat",
        "/.netlify/functions/create-runtime-army-readiness-note",
        "/.netlify/functions/runtime-army-circuit-breaker",
    }
    if actual_endpoints != expected_endpoints:
        raise AssertionError(f"Browser JS endpoints do not match approved set: {sorted(actual_endpoints)}")

    for needle in [
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
        "arbitrary SQL endpoint",
        "arbitrary command endpoint",
    ]:
        assert_not_contains(browser_js + ui + demo + root, needle, "runtime army surface")

    for needle in [
        "20,000-Agent Department-Gated Runtime Army",
        "20,000 is a cap, not an automatic activation.",
        "Department-gated activation is required.",
        "Staged unlocks are required.",
        "Circuit breakers pause further activation.",
        "Raw fleet activation is blocked.",
        "Full 47,979 activation remains blocked.",
    ]:
        assert_contains(ui, needle, "runtime-army.html")

    for needle in [
        "20,000-Agent Runtime Army",
        "./runtime-army.html",
    ]:
        assert_contains(demo, needle, "demo index")

    for needle in [
        "20,000-Agent Runtime Army",
        "./demo/runtime-army.html",
    ]:
        assert_contains(root, needle, "root index")

    for needle in [
        "MVP62_20000_AGENT_DEPARTMENT_GATED_RUNTIME_ARMY_COMPLETE",
        "MVP61_PREREQUISITE_PASSED",
        "GLOBAL_LIVE_AGENT_CAP_20000",
        "MAX_COHORT_SIZE_1000",
        "MAX_OPERATION_CHUNK_SIZE_500",
        "STAGED_ACTIVATION_REQUIRED",
        "CIRCUIT_BREAKER_REQUIRED",
        "DEPARTMENT_GATED_ACTIVATION_REQUIRED",
        "RAW_20000_AGENT_ACTIVATION_BLOCKED",
        "FULL_47979_ACTIVATION_BLOCKED",
        "RUNTIME_ARMY_LIMITS_ADDED",
        "RUNTIME_ARMY_STAGES_ADDED",
        "RUNTIME_ARMY_COHORTS_ADDED",
        "RUNTIME_ARMY_CIRCUIT_BREAKERS_ADDED",
        "RUNTIME_ARMY_HEALTH_ROLLUPS_ADDED",
        "RUNTIME_ARMY_EVENTS_ADDED",
        "RUNTIME_ARMY_FUNCTIONS_ADDED",
        "RUNTIME_ARMY_UI_ADDED",
        "DEMO_HUB_LINK_ADDED",
        "TWENTY_THOUSAND_IS_CAP_NOT_AUTOMATIC_COPY_ADDED",
        "STAGED_UNLOCK_COPY_ADDED",
        "CIRCUIT_BREAKER_COPY_ADDED",
        "COMMAND_EXECUTION_DISABLED",
        "DEPLOY_EXECUTION_DISABLED",
        "ROLLBACK_EXECUTION_DISABLED",
        "ALERT_SENDING_DISABLED",
        "SERVICE_ROLE_SERVER_SIDE_ONLY",
        "NO_SERVICE_ROLE_IN_BROWSER",
        "NO_ARBITRARY_SQL_ENDPOINT_ADDED",
        "NO_ARBITRARY_COMMAND_ENDPOINT_ADDED",
    ]:
        assert_contains(report, needle, "runtime army report")

    print("MVP62_20000_AGENT_DEPARTMENT_GATED_RUNTIME_ARMY_VALIDATION_PASS")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
