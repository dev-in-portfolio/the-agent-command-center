#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_text(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def assert_exists(rel_path: str) -> None:
    if not (ROOT / rel_path).exists():
        raise AssertionError(f"missing file: {rel_path}")


def assert_contains(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"missing {label}: {needle}")


def main() -> None:
    required_files = [
        "supabase/migrations/20260523_continual_harness_operator_mode.sql",
        "netlify/functions/_shared/continual_harness_operator_helpers.js",
        "netlify/functions/continual-harness-operator-status.js",
        "netlify/functions/continual-harness-create-run-plan.js",
        "netlify/functions/continual-harness-validate-run-plan.js",
        "netlify/functions/continual-harness-execute-allowlisted-operation.js",
        "netlify/functions/continual-harness-stop.js",
        "13_web_dashboard/dist/demo/continual-harness-operator.html",
        "13_web_dashboard/dist/demo/assets/continual-harness-operator.js",
        "scripts/validate_continual_harness_operator_mode.py",
        "09_exports/mvp_product_track/continual_harness_operator_mode_report.md",
    ]
    for rel_path in required_files:
        assert_exists(rel_path)

    migration = read_text("supabase/migrations/20260523_continual_harness_operator_mode.sql")
    for needle, label in [
        ("continual_harness_sessions", "session table"),
        ("continual_harness_permissions", "permissions table"),
        ("continual_harness_run_plans", "run plans table"),
        ("continual_harness_allowlisted_operations", "allowlisted operations table"),
        ("continual_harness_operator_events", "operator events table"),
        ("shell:execute", "blocked shell scope"),
        ("sql:arbitrary", "blocked sql scope"),
        ("deploy:execute", "blocked deploy scope"),
        ("rollback:execute", "blocked rollback scope"),
        ("alerts:send", "blocked alerts scope"),
        ("agents:activate_all", "blocked full fleet scope"),
        ("agents:activate_47979", "blocked 47979 scope"),
    ]:
        assert_contains(migration, needle, label)

    helper = read_text("netlify/functions/_shared/continual_harness_operator_helpers.js")
    assert_contains(helper, "ALLOWED_PERMISSION_SCOPES", "allowed permission scopes")
    assert_contains(helper, "BLOCKED_PERMISSION_SCOPES", "blocked permission scopes")
    assert_contains(helper, "ALLOWLISTED_OPERATIONS", "allowlisted operations")
    assert_contains(helper, "isDangerousPayload", "dangerous payload scan")

    status_fn = read_text("netlify/functions/continual-harness-operator-status.js")
    create_fn = read_text("netlify/functions/continual-harness-create-run-plan.js")
    validate_fn = read_text("netlify/functions/continual-harness-validate-run-plan.js")
    execute_fn = read_text("netlify/functions/continual-harness-execute-allowlisted-operation.js")
    stop_fn = read_text("netlify/functions/continual-harness-stop.js")
    html = read_text("13_web_dashboard/dist/demo/continual-harness-operator.html")
    demo_hub = read_text("13_web_dashboard/dist/demo/index.html")
    root_index = read_text("13_web_dashboard/dist/index.html")
    browser_js = read_text("13_web_dashboard/dist/demo/assets/continual-harness-operator.js")

    for fn_text, label in [
        (status_fn, "status function"),
        (create_fn, "create run plan function"),
        (validate_fn, "validate run plan function"),
        (execute_fn, "execute allowlisted operation function"),
        (stop_fn, "stop function"),
    ]:
        assert_contains(fn_text, "exports.handler", label)

    assert_contains(html, "Continual Harness Operator Mode", "operator ui title")
    assert_contains(html, "Operator Mode is powerful, but not free range.", "operator copy")
    assert_contains(html, "Arbitrary shell commands, arbitrary SQL, deploys, rollbacks, alerts, and full fleet activation remain blocked.", "blocked copy")
    assert_contains(demo_hub, "Continual Harness Operator Mode", "demo hub card")
    assert_contains(demo_hub, "./continual-harness-operator.html", "demo hub link")
    assert_contains(root_index, "Continual Harness Operator Mode", "root card")
    assert_contains(root_index, "./demo/continual-harness-operator.html", "root link")
    assert_contains(browser_js, "/.netlify/functions/continual-harness-operator-status", "browser status endpoint")
    assert_contains(browser_js, "/.netlify/functions/continual-harness-create-run-plan", "browser create endpoint")
    assert_contains(browser_js, "/.netlify/functions/continual-harness-validate-run-plan", "browser validate endpoint")
    assert_contains(browser_js, "/.netlify/functions/continual-harness-execute-allowlisted-operation", "browser execute endpoint")
    assert_contains(browser_js, "/.netlify/functions/continual-harness-stop", "browser stop endpoint")

    for forbidden in [
        "child_process",
        "exec(",
        "spawn(",
        "eval(",
        "new Function",
        "arbitrary SQL endpoint",
        "arbitrary command endpoint",
        "activate-all route",
        "activate-47979 route",
        "SUPABASE_SERVICE_ROLE_KEY",
        "localStorage",
        "sessionStorage",
        "document.cookie",
        "indexedDB",
    ]:
        if forbidden in browser_js:
            raise AssertionError(f"browser JS contains forbidden string: {forbidden}")

    print("CONTINUAL_HARNESS_OPERATOR_MODE_VALIDATION_PASS")


if __name__ == "__main__":
    main()
