#!/usr/bin/env python3
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "13_web_dashboard" / "dist"
DEMO = DIST / "demo"


REQUIRED_FILES = [
    DIST / "index.html",
    DEMO / "index.html",
    DEMO / "simulator.html",
    DEMO / "presentation.html",
    DEMO / "system-story.html",
    DEMO / "system-scale.html",
    DEMO / "agent-hierarchy.html",
    DEMO / "operating-model.html",
    DEMO / "validator-safety-map.html",
    DEMO / "safety-boundaries.html",
    DEMO / "technical-appendix.html",
    DEMO / "objections.html",
    DEMO / "review.html",
]


ROOT_REQUIRED = [
    "Command Center Launchpad",
    "Premium Stakeholder Demo",
    "Open Premium Demo Hub",
    "Runnable Static Simulator",
    "Open Static Simulator",
    "Current Status / Readiness Overview",
    "Original Full Audit Dashboard",
    "Open Full Audit / Archive",
    "Safety Posture",
    "Latest Verified MVP",
    "Backend/Supabase readiness architecture exists",
    "Live backend runtime is disabled",
    "MVP-50",
    "MVP-51 not started",
]

ROOT_RAW_REQUIRED = [
    "./demo/",
    "./demo/simulator.html",
]


DEMO_REQUIRED = [
    "Stakeholder Demo Hub",
    "Production verified through MVP-50",
    "Simulator",
    "Command Center Sandbox Simulator",
    "Launch Live Dashboard",
    "NOT_READY_FOR_REAL_AUTOMATION",
]

DEMO_RAW_REQUIRED = [
    "./simulator.html",
    "../index.html",
]


SIM_REQUIRED = [
    "Command Center Sandbox Simulator",
    "Safe content-review request",
    "High-risk deploy request",
    "Incident rollback request",
    "Approval denied request",
    "Auth",
    "Storage",
    "Audit",
    "Approval",
    "Dry Run",
    "Queue",
    "Human Review",
    "Monitoring Readiness",
    "STATIC SANDBOX",
    "BACKEND/SUPABASE READINESS PRESENT",
    "LIVE BACKEND RUNTIME DISABLED",
]


FORBIDDEN_VISIBLE = [
    r"\n",
    "{_list(",
    "{_stat(",
    "{_badge(",
    "{_",
    "Next milestone: 51 (In Progress)",
    "MVP-51 in progress",
    "backend integration is planned",
    "Backend integration: planned",
    "no backend integration",
    "backend missing",
    "backend does not exist",
]


FORBIDDEN_SIM_PATTERNS = [
    "fetch(",
    "XMLHttpRequest",
    "WebSocket",
    "EventSource",
    "localStorage",
    "sessionStorage",
    "document.cookie",
    "indexedDB",
    "navigator.sendBeacon",
    "serviceWorker",
    "eval(",
    "new Function",
]


def fail(message: str) -> None:
    print(message)
    raise SystemExit(1)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def visible_text(html: str) -> str:
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    html = re.sub(r"<script\b.*?</script>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<style\b.*?</style>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    html = html.replace("\xa0", " ")
    html = re.sub(r"\s+", " ", html)
    return html.strip()


def check_contains(path: Path, required: list[str]) -> None:
    text = visible_text(read(path))
    missing = [item for item in required if item not in text]
    if missing:
        fail(f"MISSING_REQUIRED_TEXT {path}: {missing}")


def check_raw_contains(path: Path, required: list[str]) -> None:
    text = read(path)
    missing = [item for item in required if item not in text]
    if missing:
        fail(f"MISSING_REQUIRED_RAW_TEXT {path}: {missing}")


def check_forbidden_visible(path: Path) -> None:
    text = visible_text(read(path))
    found = [item for item in FORBIDDEN_VISIBLE if item in text]
    if found:
        fail(f"FORBIDDEN_VISIBLE_TEXT {path}: {found}")


def check_simulator_js(path: Path) -> None:
    text = read(path)
    found = [item for item in FORBIDDEN_SIM_PATTERNS if item in text]
    if found:
        fail(f"FORBIDDEN_SIMULATOR_PATTERN {path}: {found}")


def main() -> None:
    for file_path in REQUIRED_FILES:
        if not file_path.exists():
            fail(f"MISSING_REQUIRED_FILE {file_path}")

    check_contains(DIST / "index.html", ROOT_REQUIRED)
    check_raw_contains(DIST / "index.html", ROOT_RAW_REQUIRED)
    check_contains(DEMO / "index.html", DEMO_REQUIRED)
    check_raw_contains(DEMO / "index.html", DEMO_RAW_REQUIRED)
    check_contains(DEMO / "simulator.html", SIM_REQUIRED)

    for path in [
        DIST / "index.html",
        DEMO / "index.html",
        DEMO / "simulator.html",
        DEMO / "presentation.html",
        DEMO / "system-story.html",
        DEMO / "system-scale.html",
        DEMO / "agent-hierarchy.html",
        DEMO / "operating-model.html",
        DEMO / "validator-safety-map.html",
        DEMO / "safety-boundaries.html",
        DEMO / "technical-appendix.html",
        DEMO / "objections.html",
        DEMO / "review.html",
    ]:
        check_forbidden_visible(path)

    check_simulator_js(DEMO / "simulator.html")

    demo_package = DEMO / "demo-package.json"
    if not demo_package.exists():
        fail(f"MISSING_REQUIRED_FILE {demo_package}")
    package_text = read(demo_package)
    for item in [
        '"simulator_page": "simulator.html"',
        '"simulator_type": "static_in_memory_sandbox"',
        '"runtime_activation_started": false',
        '"backend_runtime_enabled": false',
        '"supabase_writes_enabled": false',
        '"public_writes_enabled": false',
        '"command_execution_enabled": false',
        '"action_execution_enabled": false',
        '"automation_enabled": false',
    ]:
        if item not in package_text:
            fail(f"MISSING_DEMO_PACKAGE_FIELD {item}")

    print("POST_DEPLOY_DEMO_DASHBOARD_VISIBILITY_AFTER_MVP50_VALIDATION_PASS")


if __name__ == "__main__":
    main()
