#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "13_web_dashboard" / "dist"
WORKBENCH = DIST / "demo" / "runtime-workbench.html"
DEMO_INDEX = DIST / "demo" / "index.html"

REQUIRED_FILES = [
    WORKBENCH,
    DEMO_INDEX,
]

REQUIRED_STRINGS = [
    "Runtime Workbench",
    "static in-browser prototype",
    "No backend writes. No real execution.",
    "Request builder",
    "Static action registry",
    "Risk classifier",
    "Dry-run preview",
    "Approval queue",
    "Audit timeline",
    "Export JSON report",
    "Reset demo",
]

FORBIDDEN_STRINGS = [
    "fetch(",
    "XMLHttpRequest",
    "WebSocket",
    "localStorage",
    "sessionStorage",
    "document.cookie",
    "indexedDB",
    "Runtime activation started",
    "live runtime enabled",
    "execution enabled true",
    "automation enabled",
]

ALLOWED_CHANGED_PATHS = {
    "13_web_dashboard/dist/demo/runtime-workbench.html",
    "13_web_dashboard/dist/demo/index.html",
    "scripts/validate_mvp52_runtime_workbench.py",
}


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
        if path not in ALLOWED_CHANGED_PATHS:
            errors.append(f"Unexpected changed path: {path}")

    texts: dict[Path, str] = {}
    for path in REQUIRED_FILES:
        if path.exists():
            texts[path] = read(path)

    all_text = "\n".join(texts.values())
    for token in REQUIRED_STRINGS:
        if token not in all_text:
            errors.append(f"Missing required string: {token}")
    for token in FORBIDDEN_STRINGS:
        if token in all_text:
            errors.append(f"Forbidden string present: {token}")

    workbench_text = texts.get(WORKBENCH, "")
    required_page_text = [
        "Runtime Workbench - static in-browser prototype. No backend writes. No real execution.",
        "Request builder",
        "Static action registry",
        "Risk classifier",
        "Dry-run preview",
        "Approval queue",
        "Approve request",
        "Deny request",
        "Audit timeline",
        "Export JSON report",
        "Reset demo",
    ]
    for phrase in required_page_text:
        if phrase not in workbench_text:
            errors.append(f"Missing required workbench phrase: {phrase}")

    for token in ["fetch(", "XMLHttpRequest", "WebSocket", "localStorage", "sessionStorage", "document.cookie", "indexedDB"]:
        if token in workbench_text:
            errors.append(f"Workbench references forbidden browser API: {token}")

    if "No backend writes. No real execution." not in workbench_text:
        errors.append("Workbench missing no-backend/no-execution statement")

    demo_text = texts.get(DEMO_INDEX, "")
    if "./runtime-workbench.html" not in demo_text or "Runtime Workbench" not in demo_text:
        errors.append("Demo hub missing Runtime Workbench link/card")

    if errors:
        fail(errors)

    print("MVP52_RUNTIME_WORKBENCH_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
