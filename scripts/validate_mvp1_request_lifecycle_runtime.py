#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def fail(message):
    raise SystemExit(f"FAIL: {message}")


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        fail(f"Unable to read {path}: {exc}")


def ensure_exists(path):
    if not path.exists():
        fail(f"Missing required file: {path}")


def main():
    required_files = [
        ROOT / "14_backend/product_runtime/request_lifecycle.py",
        ROOT / "14_backend/product_runtime/state_model.json",
        ROOT / "14_backend/product_runtime/runtime_result_schema.json",
        ROOT / "14_backend/product_runtime/persistence_adapter_strategy.json",
        ROOT / "14_backend/product_runtime/migrations/001_mvp_request_lifecycle.sql",
        ROOT / "14_backend/product_runtime/demo_fixture.json",
        ROOT / "14_backend/product_runtime/demo_runner.py",
        ROOT / "13_web_dashboard/build_mvp1_product_runtime.py",
        ROOT / "13_web_dashboard/dist/mvp1_product_runtime_model.json",
        ROOT / "netlify/functions/product-runtime-status.js",
        ROOT / "netlify/functions/_shared/models/product_runtime_status.json",
        ROOT / "09_exports/mvp_product_track/mvp1_request_lifecycle_runtime_report.md",
        ROOT / "09_exports/mvp_product_track/mvp1_persistence_adapter_strategy_report.md",
        ROOT / "09_exports/mvp_product_track/mvp1_database_migration_scaffold_report.md",
        ROOT / "09_exports/mvp_product_track/mvp1_demo_runtime_scenario_report.md",
        ROOT / "09_exports/mvp_product_track/mvp1_product_gap_report.md",
        ROOT / "09_exports/mvp_product_track/mvp1_safety_report.md",
        ROOT / "09_exports/mvp_product_track/mvp1_acceptance_report.md",
    ]
    for path in required_files:
        ensure_exists(path)

    index = read_text(ROOT / "13_web_dashboard/dist/index.html")
    required_strings = [
        "MVP-1",
        "MVP PRODUCT TRACK",
        "REQUEST LIFECYCLE RUNTIME",
        "PERSISTENCE ADAPTER SCAFFOLD",
        "DATABASE MIGRATION SCAFFOLD",
        "REAL PRODUCT PATH",
        "STORAGE PROVIDER DECISION REQUIRED",
        "AUTH PROVIDER DECISION REQUIRED",
        "RUNTIME EXECUTION DISABLED",
        "EXTERNAL MUTATION DISABLED",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_SELECT_STORAGE_PROVIDER_AND_AUTH_PROVIDER",
        "Product Runtime Status Panel",
        "Request Lifecycle Runtime Panel",
        "Runtime Result Schema Panel",
        "Persistence Adapter Strategy Panel",
        "Database Migration Scaffold Panel",
        "Demo Runtime Scenario Panel",
        "Product Gap Panel",
        "Next Product Decision Panel",
        "Copy MVP runtime summary",
        "Copy lifecycle model",
        "Copy persistence adapter strategy",
        "Copy database migration scaffold summary",
        "Copy product gap checklist",
        "Copy next provider decision checklist",
        "Copy MVP-1 validation checklist",
    ]
    for text in required_strings:
        if text not in index:
            fail(f"Missing from index.html: {text}")

    for match in re.finditer(r'(<button[^>]*>)([^<]+)(</button>)', index):
        label = match.group(2).strip().lower()
        if label.startswith("copy ") or label.startswith("load ") or label.startswith("open "):
            continue
        if any(term in label for term in [
            "run automation",
            "execute request",
            "deploy",
            "merge",
            "push",
            "create pr",
            "connect database",
            "apply migration",
            "login",
            "start queue",
            "trigger workflow",
        ]):
            fail(f"Forbidden button label present: {match.group(2).strip()}")

    model = json.loads(read_text(ROOT / "13_web_dashboard/dist/mvp1_product_runtime_model.json"))
    for text in [
        "MVP_RUNTIME_SCAFFOLD_READY",
        "PERSISTENCE_PROVIDER_DECISION_REQUIRED",
        "REAL_AUTH_PROVIDER_DECISION_REQUIRED",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_SELECT_STORAGE_PROVIDER_AND_AUTH_PROVIDER",
    ]:
        if text not in json.dumps(model):
            fail(f"Missing MVP runtime model marker: {text}")

    acc_report = read_text(ROOT / "09_exports/mvp_product_track/mvp1_acceptance_report.md")
    for text in [
        "PRODUCT_RUNTIME_SCAFFOLD_ONLY",
        "PASS_WITH_HIGH_CONFIDENCE",
        "PERSISTENCE_PROVIDER_DECISION_REQUIRED",
        "REAL_AUTH_PROVIDER_DECISION_REQUIRED",
        "NOT_READY_FOR_REAL_AUTOMATION",
    ]:
        if text not in acc_report:
            fail(f"Acceptance report missing marker: {text}")

    runtime_code = read_text(ROOT / "14_backend/product_runtime/request_lifecycle.py")
    runner_code = read_text(ROOT / "14_backend/product_runtime/demo_runner.py")
    endpoint_code = read_text(ROOT / "netlify/functions/product-runtime-status.js")

    forbidden_patterns = [
        "import subprocess",
        "subprocess.run",
        "subprocess.Popen",
        "subprocess.call",
        "subprocess.check_output",
        "subprocess.check_call",
        "os.system",
        "shell=True",
        "process.env",
        "os.environ",
        "DATABASE_URL",
        "api.github.com",
        "api.netlify.com",
        "requests.",
        "urllib",
        "write_text(",
        "unlink(",
        "mkdir(",
        "exec(",
        "spawn(",
    ]

    for source_name, source_text in [
        ("request_lifecycle.py", runtime_code),
        ("demo_runner.py", runner_code),
        ("product-runtime-status.js", endpoint_code),
    ]:
        lowered = source_text.lower()
        for pattern in forbidden_patterns:
            if pattern.lower() in lowered:
                fail(f"Forbidden pattern in {source_name}: {pattern}")

    migration_sql = read_text(ROOT / "14_backend/product_runtime/migrations/001_mvp_request_lifecycle.sql")
    for text in [
        "CREATE TABLE IF NOT EXISTS users",
        "CREATE TABLE IF NOT EXISTS roles",
        "CREATE TABLE IF NOT EXISTS requests",
        "CREATE TABLE IF NOT EXISTS request_lifecycle_events",
        "CREATE TABLE IF NOT EXISTS approvals",
        "CREATE TABLE IF NOT EXISTS audit_events",
        "CREATE TABLE IF NOT EXISTS dry_run_results",
        "CREATE TABLE IF NOT EXISTS no_go_flags",
    ]:
        if text not in migration_sql:
            fail(f"Migration scaffold missing table definition: {text}")

    print("MVP1_REQUEST_LIFECYCLE_RUNTIME_VALIDATION_PASS")


if __name__ == "__main__":
    main()
