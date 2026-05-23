#!/usr/bin/env python3
"""Validate the MVP-52 real runtime kernel pass."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

required_files = [
    ROOT / "supabase" / "migrations" / "20260522_mvp52_runtime_kernel.sql",
    ROOT / "netlify" / "functions" / "runtime-request-create.js",
    ROOT / "netlify" / "functions" / "runtime-request-list.js",
    ROOT / "netlify" / "functions" / "runtime-request-decision.js",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "runtime-kernel.html",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "assets" / "runtime-kernel.js",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "index.html",
    ROOT / "09_exports" / "mvp_product_track" / "mvp52_real_runtime_kernel_report.md",
    ROOT / "09_exports" / "runtime_kernel_mvp52" / "mvp52_real_runtime_kernel_scope.md",
]

required_strings = {
    "migration": [
        "create table",
        "runtime_requests",
        "runtime_audit_events",
        "runtime_approval_queue",
        "runtime_kernel_config",
        "execution_enabled boolean not null default false",
        "runtime_activation_started",
        "live_runtime_agents_enabled",
        "command_execution_enabled",
        "automation_enabled",
        "rollback_execution_enabled",
        "false",
    ],
    "functions": [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "runtime_requests",
        "runtime_audit_events",
        "runtime_approval_queue",
        "execution_enabled",
        "false",
        "REQUEST_SUBMITTED",
        "RISK_CLASSIFIED",
        "APPROVAL_QUEUE_CREATED",
        "REQUEST_BLOCKED",
        "APPROVAL_APPROVED",
        "APPROVAL_DENIED",
    ],
    "ui": [
        "Runtime Kernel",
        "MVP-52 Real Runtime Kernel",
        "Submit Real Runtime Request",
        "Backend persistence: Supabase",
        "Runtime activation: not started",
        "Live runtime agents enabled: 0",
        "Command execution: disabled",
        "Automation: disabled",
        "Approval is not execution",
        "Backend functions are wired, but persistence requires Netlify Supabase environment variables. Nothing is executing from this page. Missing backend configuration is not runtime failure.",
    ],
    "js_fetch": [
        "/.netlify/functions/runtime-request-create",
        "/.netlify/functions/runtime-request-list",
        "/.netlify/functions/runtime-request-decision",
    ],
}

forbidden_strings = [
    "child_process",
    "exec(",
    "spawn(",
    "eval(",
    "new Function",
    "SUPABASE_SERVICE_ROLE_KEY",
    "execution_enabled true",
    "runtime_activation_started true",
    "live_runtime_agents_enabled greater than 0",
    "command execution enabled",
    "automation enabled",
    "rollback execution enabled",
    "alert sending enabled",
    "arbitrary SQL endpoint",
    "arbitrary command endpoint",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def fail(message: str) -> None:
    print("MVP52_REAL_RUNTIME_KERNEL_VALIDATION_FAIL")
    print(f"  - {message}")
    sys.exit(1)


for path in required_files:
    if not path.exists():
        fail(f"Missing required file: {path.relative_to(ROOT)}")

migration_text = read(required_files[0])
for needle in required_strings["migration"]:
    if needle not in migration_text:
        fail(f"Migration missing required string: {needle}")

function_text = migration_text + "\n" + "\n".join(read(path) for path in required_files[1:4])
for needle in required_strings["functions"]:
    if needle not in function_text:
        fail(f"Function layer missing required string: {needle}")

ui_text = read(required_files[4]) + "\n" + read(required_files[6])
for needle in required_strings["ui"]:
    if needle not in ui_text:
        fail(f"UI missing required string: {needle}")

js_text = read(required_files[5])
for needle in required_strings["js_fetch"]:
    if needle not in js_text:
        fail(f"Client JS missing required fetch target: {needle}")

for needle in forbidden_strings:
    if needle in js_text:
        fail(f"Forbidden string present in client JS: {needle}")

if "SUPABASE_SERVICE_ROLE_KEY" in js_text:
    fail("Browser JS references service role key")

print("MVP52_REAL_RUNTIME_KERNEL_VALIDATION_PASS")
