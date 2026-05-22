#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "13_web_dashboard" / "dist"
BLUEPRINT_DIR = ROOT / "09_exports" / "runtime_foundation_mvp51"

REQUIRED_FILES = [
    BLUEPRINT_DIR / "runtime_activation_blueprint.md",
    BLUEPRINT_DIR / "schemas" / "user_role.schema.json",
    BLUEPRINT_DIR / "schemas" / "tenant_workspace.schema.json",
    BLUEPRINT_DIR / "schemas" / "action_registry.schema.json",
    BLUEPRINT_DIR / "schemas" / "approval_gate.schema.json",
    BLUEPRINT_DIR / "schemas" / "audit_event.schema.json",
    BLUEPRINT_DIR / "schemas" / "dry_run_result.schema.json",
    BLUEPRINT_DIR / "schemas" / "runtime_activation_gate.schema.json",
    BLUEPRINT_DIR / "contracts" / "runtime_non_execution_contract.md",
    BLUEPRINT_DIR / "contracts" / "dry_run_before_execution_contract.md",
    BLUEPRINT_DIR / "contracts" / "human_approval_contract.md",
    BLUEPRINT_DIR / "contracts" / "audit_everything_contract.md",
    BLUEPRINT_DIR / "checklists" / "runtime_activation_prerequisite_checklist.md",
    BLUEPRINT_DIR / "checklists" / "enterprise_runtime_review_checklist.md",
    DIST / "demo" / "runtime-foundation.html",
    DIST / "demo" / "index.html",
    DIST / "index.html",
    ROOT / "09_exports" / "mvp_product_track" / "mvp51_runtime_foundation_blueprint_report.md",
]

REQUIRED_STRINGS = [
    "MVP-51",
    "Runtime Foundation",
    "Runtime activation has not started",
    "Live runtime agents enabled: 0",
    "does not enable runtime",
    "does not execute commands",
    "does not write to Supabase",
    "dry-run before execution",
    "human approval",
    "audit event",
    "action registry",
    "approval gate",
    "tenant workspace",
    "execution_enabled false",
    "runtime_enabled false",
    "execution_allowed false",
]

FORBIDDEN_STRINGS = [
    "Runtime activation started",
    "live runtime enabled",
    "execution enabled true",
    "execution_allowed true",
    "runtime_enabled true",
    "command execution enabled",
    "automation enabled",
]

FORBIDDEN_PATH_PREFIXES = [
    "netlify/functions/",
    "14_backend/",
    "10_runtime/",
    "supabase/.temp",
]

ALLOWED_CHANGED_PREFIXES = [
    "09_exports/runtime_foundation_mvp51/",
    "09_exports/mvp_product_track/mvp51_runtime_foundation_blueprint_report.md",
    "13_web_dashboard/dist/demo/runtime-foundation.html",
    "13_web_dashboard/dist/demo/index.html",
    "13_web_dashboard/dist/index.html",
    "scripts/validate_mvp51_runtime_foundation_blueprint.py",
]


def fail(messages: list[str]) -> None:
    for message in messages:
        print(message, file=sys.stderr)
    raise SystemExit(1)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []

    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.exists()]
    if missing:
        errors.append("Missing required files:")
        errors.extend(f"  - {item}" for item in missing)

    diff_paths = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    for path in diff_paths:
        if any(path.startswith(prefix) for prefix in FORBIDDEN_PATH_PREFIXES):
            errors.append(f"Forbidden changed path: {path}")
        if not (
            path.startswith("09_exports/runtime_foundation_mvp51/")
            or path == "09_exports/mvp_product_track/mvp51_runtime_foundation_blueprint_report.md"
            or path == "13_web_dashboard/dist/demo/runtime-foundation.html"
            or path == "13_web_dashboard/dist/demo/index.html"
            or path == "13_web_dashboard/dist/index.html"
            or path == "scripts/validate_phase5_plus1_master_validator_wall.py"
            or path == "scripts/validate_mvp51_runtime_foundation_blueprint.py"
        ):
            errors.append(f"Unexpected changed path: {path}")

    texts: dict[Path, str] = {}
    for path in REQUIRED_FILES:
        if not path.exists():
            continue
        try:
            texts[path] = read(path)
        except UnicodeDecodeError:
            continue

    all_text = "\n".join(texts.values())
    for token in REQUIRED_STRINGS:
        if token not in all_text:
            errors.append(f"Missing required string '{token}' in runtime foundation materials")
    for token in FORBIDDEN_STRINGS:
        if token in all_text:
            errors.append(f"Forbidden string '{token}' in runtime foundation materials")

    runtime_page = DIST / "demo" / "runtime-foundation.html"
    if runtime_page.exists():
        text = texts.get(runtime_page, read(runtime_page))
        for phrase in [
            "Runtime Foundation",
            "MVP-51",
            "Runtime activation has not started.",
            "Live runtime agents enabled: 0.",
            "No commands execute from this page.",
            "No backend writes are enabled.",
            "No Supabase mutations are enabled.",
            "No automation is enabled.",
            "No rollback execution is enabled.",
            "No Netlify functions or endpoints are added.",
        ]:
            if phrase not in text:
                errors.append(f"Missing required runtime-page phrase: {phrase}")

    demo_index = DIST / "demo" / "index.html"
    if demo_index.exists():
        text = read(demo_index)
        if "./runtime-foundation.html" not in text or "Runtime Foundation" not in text:
            errors.append("Demo hub missing Runtime Foundation link/card")

    root_index = DIST / "index.html"
    if root_index.exists():
        text = read(root_index)
        if "./demo/runtime-foundation.html" not in text or "Runtime Foundation" not in text:
            errors.append("Root launchpad missing Runtime Foundation link/card")

    if errors:
        fail(errors)

    print("MVP51_RUNTIME_FOUNDATION_BLUEPRINT_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
