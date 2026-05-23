#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def assert_contains(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing required string in {label}: {needle}")


def assert_not_contains(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"Forbidden string in {label}: {needle}")


def run_prereq_validator() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/validate_mvp59_1777_department_runtime_mapping.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            "MVP-59 prerequisite validator failed before MVP-60 validation.\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    if "MVP59_1777_DEPARTMENT_RUNTIME_MAPPING_VALIDATION_PASS" not in result.stdout:
        raise AssertionError("MVP-59 prerequisite validator did not emit the expected pass string.")


def main() -> None:
    run_prereq_validator()

    migration = read_text("supabase/migrations/20260522_mvp60_department_gated_runtime_expansion.sql")
    list_fn = read_text("netlify/functions/list-department-runtime-gates.js")
    approve_fn = read_text("netlify/functions/approve-department-runtime-gate.js")
    block_fn = read_text("netlify/functions/block-department-runtime-gate.js")
    activate_fn = read_text("netlify/functions/activate-department-runtime.js")
    deactivate_fn = read_text("netlify/functions/deactivate-department-runtime.js")
    rollup_fn = read_text("netlify/functions/department-gated-runtime-rollup.js")
    helper_fn = read_text("netlify/functions/_shared/runtime_department_gate_helpers.js")
    page = read_text("13_web_dashboard/dist/demo/department-gated-runtime.html")
    browser_js = read_text("13_web_dashboard/dist/demo/assets/department-gated-runtime.js")
    demo_index = read_text("13_web_dashboard/dist/demo/index.html")
    root_index = read_text("13_web_dashboard/dist/index.html")

    for path in [
        "supabase/migrations/20260522_mvp60_department_gated_runtime_expansion.sql",
        "netlify/functions/list-department-runtime-gates.js",
        "netlify/functions/activate-department-runtime.js",
        "netlify/functions/deactivate-department-runtime.js",
        "netlify/functions/approve-department-runtime-gate.js",
        "netlify/functions/block-department-runtime-gate.js",
        "netlify/functions/department-gated-runtime-rollup.js",
        "13_web_dashboard/dist/demo/department-gated-runtime.html",
        "13_web_dashboard/dist/demo/assets/department-gated-runtime.js",
        "13_web_dashboard/dist/demo/index.html",
        "13_web_dashboard/dist/index.html",
        "09_exports/mvp_product_track/mvp60_department_gated_runtime_expansion_report.md",
    ]:
        if not (ROOT / path).exists():
            raise AssertionError(f"Missing required file: {path}")

    migration_required = [
        "department_runtime_gates",
        "department_runtime_activations",
        "department_runtime_gate_events",
        "department_runtime_global_limits",
        "mvp60_global_live_agent_cap",
        "2500",
        "max_department_activation_cap",
        "250",
        "full_47979_activation_blocked",
        "department_gated_expansion_enabled",
        "command_execution_enabled",
        "deploy_execution_enabled",
        "rollback_execution_enabled",
        "alert_sending_enabled",
        "create or replace function approve_department_runtime_gate",
        "create or replace function block_department_runtime_gate",
        "create or replace function activate_department_runtime",
        "create or replace function deactivate_department_runtime",
        "department_runtime_sync_limits",
    ]
    for needle in migration_required:
        assert_contains(migration, needle, "mvp60 migration")

    for needle in [
        "command_execution_enabled boolean not null default false",
        "deploy_execution_enabled boolean not null default false",
        "rollback_execution_enabled boolean not null default false",
        "alert_sending_enabled boolean not null default false",
        "gate_status in ('closed', 'pending_review', 'approved', 'active', 'blocked', 'disabled')",
        "activation_cap >= 0 and activation_cap <= 250",
        "currently_active_agents >= 0 and currently_active_agents <= activation_cap",
        "requested_agent_count >= 0 and requested_agent_count <= 250",
        "activation_status in ('requested', 'approved', 'active', 'partially_active', 'deactivated', 'denied', 'blocked')",
        "full 47,979-agent activation remains blocked",
    ]:
        assert_contains(migration, needle, "mvp60 migration")

    for needle in [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "department_runtime_gates",
        "department_runtime_activations",
        "department_runtime_gate_events",
        "department_runtime_global_limits",
        "approve_department_runtime_gate",
        "block_department_runtime_gate",
        "activate_department_runtime",
        "deactivate_department_runtime",
    ]:
        assert_contains(helper_fn, needle, "mvp60 gate helper")

    list_required = [
        "Department-gated runtime backend is not configured.",
        "backend_status",
        "global_limits",
        "departments",
        "gates",
        "gate_events",
        "readiness_notes",
        "department_events",
        "approved_gates",
        "active_gates",
        "blocked_gates",
    ]
    for needle in list_required:
        assert_contains(list_fn, needle, "list-department-runtime-gates")

    for fn_text, label, required in [
        (
            approve_fn,
            "approve-department-runtime-gate",
            ["activation_cap must be between 1 and 250", "reason is required", "DEPARTMENT_GATED_EXECUTION_DISABLED"],
        ),
        (
            block_fn,
            "block-department-runtime-gate",
            ["DEPARTMENT_GATED_EXECUTION_DISABLED", "block-department-runtime-gate"],
        ),
        (
            activate_fn,
            "activate-department-runtime",
            ["requested_agent_count must be between 1 and 250", "reason is required", "DEPARTMENT_GATED_EXECUTION_DISABLED"],
        ),
        (
            deactivate_fn,
            "deactivate-department-runtime",
            ["DEPARTMENT_GATED_EXECUTION_DISABLED", "deactivate-department-runtime"],
        ),
        (
            rollup_fn,
            "department-gated-runtime-rollup",
            ["global_live_agent_cap", "current_live_runtime_agents", "approved_gates", "active_gates", "blocked_gates"],
        ),
    ]:
        for needle in required:
            assert_contains(fn_text, needle, label)

    page_required = [
        "Department-Gated Runtime Expansion",
        "Department approval is not command execution.",
        "Activation means supervised runtime capacity only.",
        "No department can run shell commands, deploys, rollbacks, alerts, or arbitrary actions from this page.",
        "Full 47,979 activation remains blocked.",
        "Global MVP-60 live runtime cap: 2,500",
        "Max per-department cap: 250",
        "data-collapsible-menu",
        "data-action=\"toggle-menu\"",
        "aria-expanded=\"false\"",
        "data-menu-panel",
        "hidden",
    ]
    for needle in page_required:
        assert_contains(page, needle, "department-gated-runtime.html")

    js_allowed_endpoints = {
        "/.netlify/functions/list-department-runtime-gates",
        "/.netlify/functions/department-gated-runtime-rollup",
        "/.netlify/functions/approve-department-runtime-gate",
        "/.netlify/functions/block-department-runtime-gate",
        "/.netlify/functions/activate-department-runtime",
        "/.netlify/functions/deactivate-department-runtime",
    }
    for endpoint in js_allowed_endpoints:
        assert_contains(browser_js, endpoint, "department-gated-runtime.js")

    endpoint_occurrences = [line.strip() for line in browser_js.splitlines() if "/.netlify/functions/" in line]
    actual_endpoints = set()
    for line in endpoint_occurrences:
        if "/.netlify/functions/" not in line:
            continue
        for endpoint in js_allowed_endpoints:
            if endpoint in line:
                actual_endpoints.add(endpoint)
    if actual_endpoints != js_allowed_endpoints:
        raise AssertionError(f"Browser JS endpoints do not match the approved set: {sorted(actual_endpoints)}")

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
    ]:
        assert_not_contains(browser_js, needle, "department-gated-runtime.js")

    for needle in [
        "activate-all",
        "activate-47979",
        "arbitrary SQL endpoint",
        "arbitrary command endpoint",
    ]:
        assert_not_contains(browser_js + page + demo_index + root_index, needle, "department-gated runtime surface")

    for needle in [
        "Department-Gated Runtime Expansion",
        "Open Department-Gated Runtime Expansion",
    ]:
        assert_contains(demo_index, needle, "demo index")
        assert_contains(root_index, needle, "root index")

    if "SUPABASE_SERVICE_ROLE_KEY" in browser_js:
        raise AssertionError("Browser JS must not contain the Supabase service role key.")

    if "command_execution_enabled true" in browser_js.lower() or "deploy_execution_enabled true" in browser_js.lower() or "rollback_execution_enabled true" in browser_js.lower() or "alert_sending_enabled true" in browser_js.lower():
        raise AssertionError("Browser JS must not enable execution flags.")

    print("MVP60_DEPARTMENT_GATED_RUNTIME_EXPANSION_VALIDATION_PASS")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
