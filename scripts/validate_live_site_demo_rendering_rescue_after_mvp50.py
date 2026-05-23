#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "13_web_dashboard" / "dist"
DEMO = DIST / "demo"
INDEX = DIST / "index.html"
DEMO_INDEX = DEMO / "index.html"
SIMULATOR = DEMO / "simulator.html"
DEMO_PACKAGE = DEMO / "demo-package.json"
REPORT = ROOT / "09_exports" / "mvp_product_track" / "live_site_demo_rendering_rescue_after_mvp50_report.md"


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self.text_parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data):
        if not self._skip_depth and data:
            self.text_parts.append(data)

    def text(self) -> str:
        return "\n".join(self.text_parts)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def visible_text(path: Path) -> str:
    parser = VisibleTextParser()
    parser.feed(read(path))
    return parser.text()


def assert_contains(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"Missing {label}: {needle}")


def assert_not_contains(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise SystemExit(f"Forbidden {label}: {needle}")


def assert_page_clean(path: Path) -> None:
    text = visible_text(path)
    for needle in [
        "\\n",
        "{_list(",
        "{_stat(",
        "{_badge(",
        "{_",
        "Next milestone: 51 (In Progress)",
        "MVP-51 in progress",
        "backend integration is planned",
        "no backend integration",
        "backend missing",
        "backend does not exist",
    ]:
        assert_not_contains(text, needle, f"{path.name} visible text")


def main() -> int:
    required_files = [
        INDEX,
        DEMO_INDEX,
        SIMULATOR,
        DEMO_PACKAGE,
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
    for path in required_files:
        if not path.exists():
            raise SystemExit(f"Missing required file: {path}")

    index_text = visible_text(INDEX)
    demo_index_text = visible_text(DEMO_INDEX)
    simulator_text = visible_text(SIMULATOR)
    simulator_source = read(SIMULATOR)
    index_source = read(INDEX)
    demo_index_source = read(DEMO_INDEX)

    for path in [INDEX, DEMO_INDEX] + [p for p in DEMO.glob("*.html") if p.name != "simulator.html"]:
        assert_page_clean(path)
    assert_page_clean(SIMULATOR)

    for needle in [
        "MVP-50",
        "Premium Stakeholder Demo",
        "View Stakeholder Demo Hub",
        "Runnable Static Simulator",
        "/demo/",
        "/demo/simulator.html",
        "Backend/Supabase readiness architecture exists",
        "Live backend runtime is disabled",
    ]:
        assert_contains(index_source, needle, "main dashboard copy")

    for needle in [
        "Stakeholder Demo Hub",
        "Production verified through MVP-62 plus Continual Harness Operator Mode. Full-fleet MVP-63 through MVP-68 surfaces are not yet merged into this branch.",
        "System Story",
        "System Scale",
        "Agent / Department Hierarchy",
        "Operating Model",
        "Validator and Safety Gate Map",
        "Command Center Sandbox Simulator",
        "simulator.html",
        "NOT_READY_FOR_REAL_AUTOMATION",
    ]:
        assert_contains(demo_index_source, needle, "demo hub copy")

    for needle in [
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
        "NOT_READY_FOR_REAL_AUTOMATION",
        "The Agent Command Center includes backend/Supabase readiness architecture, but the live demo runs in static read-only mode.",
    ]:
        assert_contains(simulator_source, needle, "simulator copy")

    for needle in [
        "no backend",
        "backend does not exist",
        "backend missing",
        "no backend integration",
        "backend integration is planned",
        "backend integration remains a later phase",
        "MVP-51 in progress",
        "Next milestone: 51 (In Progress)",
    ]:
        assert_not_contains(index_text.lower(), needle, "main dashboard visible text")
        assert_not_contains(demo_index_text.lower(), needle, "demo hub visible text")
        assert_not_contains(simulator_text.lower(), needle, "simulator visible text")

    for needle in [
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
    ]:
        assert_not_contains(simulator_source, needle, "simulator JS")

    if index_text.count("View Stakeholder Demo Hub") < 1:
        raise SystemExit("Main dashboard link missing in visible text")
    if index_text.count("Runnable Static Simulator") < 1:
        raise SystemExit("Main dashboard simulator link missing in visible text")
    if demo_index_text.count("Command Center Sandbox Simulator") < 1:
        raise SystemExit("Demo index simulator card missing in visible text")
    if simulator_text.count("Safe content-review request") < 1:
        raise SystemExit("Simulator visible text missing scenario label")

    package = json.loads(DEMO_PACKAGE.read_text(encoding="utf-8"))
    assert package.get("runtime_activation_started") is False
    assert package.get("backend_runtime_enabled") is False
    assert package.get("supabase_writes_enabled") is False
    assert package.get("public_writes_enabled") is False
    assert package.get("command_execution_enabled") is False
    assert package.get("action_execution_enabled") is False
    assert package.get("automation_enabled") is False
    assert package.get("simulator_page") == "simulator.html"
    assert package.get("simulator_type") == "static_in_memory_sandbox"
    assert "simulator.html" in package.get("viewable_pages", [])

    report_text = read(REPORT)
    for marker in [
        "LIVE_SITE_DEMO_RENDERING_RESCUE_AFTER_MVP50_COMPLETE",
        "PREMIUM_DEMO_MATERIAL_PRESENT_IN_DIST",
        "SIMULATOR_PAGE_PRESENT_IN_DIST",
        "MAIN_DASHBOARD_LINKS_TO_DEMO",
        "MAIN_DASHBOARD_LINKS_TO_SIMULATOR",
        "LITERAL_NEWLINE_ARTIFACTS_REMOVED",
        "RAW_TEMPLATE_FRAGMENT_ARTIFACTS_REMOVED",
        "BACKEND_SUPABASE_LANGUAGE_CORRECTED",
        "BACKEND_SUPABASE_READINESS_ACKNOWLEDGED",
        "LIVE_BACKEND_RUNTIME_DISABLED",
        "SUPABASE_WRITES_DISABLED",
        "PUBLIC_WRITES_DISABLED",
        "SERVICE_ROLE_NOT_EXPOSED",
        "MVP51_NOT_STARTED",
        "RUNTIME_ACTIVATION_NOT_STARTED",
        "STATIC_READ_ONLY_DEMO_CONFIRMED",
        "RUNNABLE_STATIC_SIMULATOR_CONFIRMED",
        "NO_ENDPOINTS_ADDED",
        "NO_NETLIFY_FUNCTIONS_ADDED",
        "NO_DATABASE_WRITES_ADDED",
        "NO_SUPABASE_WRITES_ADDED",
        "NO_COMMAND_EXECUTION_ADDED",
        "NO_ACTION_EXECUTION_ADDED",
        "NO_AUTOMATION_ADDED",
        "NO_ALERT_SENDING_ADDED",
        "NO_INCIDENT_MUTATION_ADDED",
        "NO_ROLLBACK_EXECUTION_ADDED",
    ]:
        assert_contains(report_text, marker, "rescue report")

    print("LIVE_SITE_DEMO_RENDERING_RESCUE_AFTER_MVP50_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
