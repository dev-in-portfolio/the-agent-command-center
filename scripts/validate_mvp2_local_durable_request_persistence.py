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
        ROOT / "14_backend/product_runtime/persistence/__init__.py",
        ROOT / "14_backend/product_runtime/persistence/sqlite_adapter.py",
        ROOT / "14_backend/product_runtime/persistence/request_repository.py",
        ROOT / "14_backend/product_runtime/persistence/status_model.json",
        ROOT / "14_backend/product_runtime/persistence/apply_local_migrations.py",
        ROOT / "14_backend/product_runtime/persistence/local_persistence_demo.py",
        ROOT / "14_backend/product_runtime/request_lifecycle.py",
        ROOT / "13_web_dashboard/build_mvp2_local_persistence.py",
        ROOT / "13_web_dashboard/dist/mvp2_local_persistence_model.json",
        ROOT / "09_exports/mvp_product_track/mvp2_local_durable_request_persistence_report.md",
        ROOT / "09_exports/mvp_product_track/mvp2_sqlite_adapter_report.md",
        ROOT / "09_exports/mvp_product_track/mvp2_request_repository_report.md",
        ROOT / "09_exports/mvp_product_track/mvp2_local_migration_runner_report.md",
        ROOT / "09_exports/mvp_product_track/mvp2_lifecycle_persistence_demo_report.md",
        ROOT / "09_exports/mvp_product_track/mvp2_production_persistence_gap_report.md",
        ROOT / "09_exports/mvp_product_track/mvp2_safety_report.md",
        ROOT / "09_exports/mvp_product_track/mvp2_acceptance_report.md",
    ]
    for path in required_files:
        ensure_exists(path)

    index = read_text(ROOT / "13_web_dashboard/dist/index.html")
    required_strings = [
        "MVP-2",
        "LOCAL DURABLE REQUEST PERSISTENCE",
        "SQLITE LOCAL DEV ADAPTER",
        "REQUEST REPOSITORY",
        "LOCAL MIGRATION RUNNER",
        "LIFECYCLE EVENT PERSISTENCE",
        "PRODUCTION PERSISTENCE NOT CONFIGURED",
        "REAL AUTH PROVIDER REQUIRED",
        "LOCAL DEV ONLY",
        "NO EXTERNAL MUTATION",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_CHOOSE_PRODUCTION_POSTGRES_AND_AUTH_PROVIDER",
        "Local Persistence Status Panel",
        "SQLite Adapter Panel",
        "Request Repository Panel",
        "Local Migration Runner Panel",
        "Lifecycle Persistence Demo Panel",
        "Production Persistence Gap Panel",
        "Next Product Decision Panel",
        "Copy MVP-2 local persistence summary",
        "Copy SQLite adapter contract",
        "Copy request repository contract",
        "Copy local migration instructions",
        "Copy production persistence gap checklist",
        "Copy next provider decision checklist",
        "Copy MVP-2 validation checklist",
    ]
    for text in required_strings:
        if text not in index:
            fail(f"Missing from index.html: {text}")

    for match in re.finditer(r'(<button[^>]*>)([^<]+)(</button>)', index):
        label = match.group(2).strip().lower()
        if label.startswith("copy ") or label.startswith("load ") or label.startswith("open "):
            continue
        if any(term in label for term in [
            "connect production database",
            "apply production migration",
            "read database_url",
            "login",
            "execute request",
            "deploy",
            "merge",
            "push",
            "create pr",
            "start automation",
        ]):
            fail(f"Forbidden button label present: {match.group(2).strip()}")

    model = json.loads(read_text(ROOT / "13_web_dashboard/dist/mvp2_local_persistence_model.json"))
    for text in [
        "LOCAL_PERSISTENCE_READY_FOR_DEV_TESTING",
        "PRODUCTION_PERSISTENCE_PROVIDER_REQUIRED",
        "REAL_AUTH_PROVIDER_REQUIRED",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "NEXT_STEP_CHOOSE_PRODUCTION_POSTGRES_AND_AUTH_PROVIDER",
    ]:
        if text not in json.dumps(model):
            fail(f"Missing MVP-2 model marker: {text}")

    acceptance = read_text(ROOT / "09_exports/mvp_product_track/mvp2_acceptance_report.md")
    for text in [
        "LOCAL_DURABLE_PERSISTENCE_READY_FOR_DEV_ONLY",
        "PASS_WITH_HIGH_CONFIDENCE",
        "PRODUCTION_PERSISTENCE_PROVIDER_REQUIRED",
        "REAL_AUTH_PROVIDER_REQUIRED",
        "NOT_READY_FOR_REAL_AUTOMATION",
    ]:
        if text not in acceptance:
            fail(f"Acceptance report missing marker: {text}")

    runtime_code = read_text(ROOT / "14_backend/product_runtime/request_lifecycle.py")
    sqlite_adapter = read_text(ROOT / "14_backend/product_runtime/persistence/sqlite_adapter.py")
    repository_code = read_text(ROOT / "14_backend/product_runtime/persistence/request_repository.py")
    migration_runner = read_text(ROOT / "14_backend/product_runtime/persistence/apply_local_migrations.py")
    demo_code = read_text(ROOT / "14_backend/product_runtime/persistence/local_persistence_demo.py")
    model_json = read_text(ROOT / "13_web_dashboard/dist/mvp2_local_persistence_model.json")
    dashboard_renderer = read_text(ROOT / "13_web_dashboard/dashboard_renderer.py")
    build_script = read_text(ROOT / "13_web_dashboard/build_mvp2_local_persistence.py")

    forbidden_patterns = [
        "process.env",
        "os.environ",
        "requests.",
        "urllib",
        "import subprocess",
        "subprocess.run",
        "subprocess.Popen",
        "subprocess.call",
        "subprocess.check_output",
        "subprocess.check_call",
        "os.system",
        "shell=True",
        "exec(",
        "spawn(",
        "api.github.com",
        "api.netlify.com",
        "localStorage",
        "sessionStorage",
        "indexeddb",
        "document.cookie",
        "set-cookie",
        "github_token",
        "netlify_auth_token",
    ]

    for source_name, source_text in [
        ("request_lifecycle.py", runtime_code),
        ("sqlite_adapter.py", sqlite_adapter),
        ("request_repository.py", repository_code),
        ("apply_local_migrations.py", migration_runner),
        ("local_persistence_demo.py", demo_code),
        ("build_mvp2_local_persistence.py", build_script),
        ("dashboard_renderer.py", dashboard_renderer),
        ("mvp2_local_persistence_model.json", model_json),
    ]:
        lowered = source_text.lower()
        for pattern in forbidden_patterns:
            if pattern.lower() in lowered:
                fail(f"Forbidden pattern in {source_name}: {pattern}")

        if re.search(r"\bdatabase_url\b", lowered):
            fail(f"Forbidden database URL reference in {source_name}")

    if "persistence_adapter=None" not in runtime_code:
        fail("request_lifecycle.py missing optional persistence adapter hook")
    if "local_persistence_enabled" not in runtime_code:
        fail("request_lifecycle.py missing local persistence result marker")

    sqlite_mentions = re.findall(r"sqlite3", runtime_code + "\n" + repository_code + "\n" + demo_code + "\n" + migration_runner + "\n" + sqlite_adapter)
    if len(sqlite_mentions) == 0:
        fail("Expected sqlite3 usage in MVP-2 local persistence files")

    outside_sqlite_files = (
        runtime_code + "\n" + build_script + "\n" + dashboard_renderer + "\n" + model_json
    ).lower()
    if re.search(r"\bimport\s+sqlite3\b", outside_sqlite_files) or re.search(r"\bsqlite3\.", outside_sqlite_files):
        fail("sqlite3 usage leaked outside local persistence files")

    print("MVP2_LOCAL_DURABLE_REQUEST_PERSISTENCE_VALIDATION_PASS")


if __name__ == "__main__":
    main()
