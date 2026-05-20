#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "13_web_dashboard" / "dist"

REQUIRED_FILES = [
    DIST / "index.html",
    DIST / "demo" / "index.html",
    DIST / "demo" / "simulator.html",
    DIST / "demo" / "system-scale.html",
    DIST / "demo" / "agent-hierarchy.html",
    DIST / "demo" / "agent-registry.html",
    DIST / "demo" / "operating-model.html",
    DIST / "demo" / "validator-safety-map.html",
    DIST / "demo" / "safety-boundaries.html",
    DIST / "demo" / "review.html",
    DIST / "_redirects",
    DIST / "_headers",
    DIST / "demo" / "assets" / "demo.css",
    DIST / "demo" / "assets" / "demo.js",
    ROOT / "09_exports" / "system_registry" / "agent_department_registry_summary.json",
]

ROOT_REQUIRED_STRINGS = [
    "Command Center Launchpad",
    "Premium Stakeholder Demo",
    "Runnable Static Simulator",
    "Exact agent count: 47,979",
    "Exact department count: 1,777",
    "Live runtime agents enabled: 0",
    "Backend/Supabase readiness exists",
    "MVP-50 Production Verified",
    "MVP-51 not started",
    "For Recruiters / Hiring Managers",
    "Why this matters",
    "Skills demonstrated",
    "System at a Glance",
    "Registered vs Runtime",
    "11 Operational Domains",
]

DEMO_REQUIRED_STRINGS = [
    "Stakeholder Demo Hub",
    "Production verified through MVP-50",
    "Command Center Sandbox Simulator",
    "Agent Registry",
    "System Scale",
    "Launch Live Dashboard",
    "NOT_READY_FOR_REAL_AUTOMATION",
]

SIM_REQUIRED_STRINGS = [
    "Command Center Sandbox Simulator",
    "Safe content-review request",
    "High-risk deploy request",
    "Incident rollback request",
    "Approval denied request",
    "READY_FOR_HUMAN_REVIEW_SIMULATION_ONLY",
    "BLOCKED_BY_DEPLOY_CONTROL_BOUNDARY",
    "ROLLBACK_READINESS_PREVIEW_ONLY",
    "STOPPED_AT_APPROVAL_GATE",
    "No backend calls",
    "No writes",
    "No execution",
    "No automation",
    "No Supabase mutation",
    "No rollback execution",
    "Mock log",
    "progress",
]

REGISTRY_STRINGS = [
    "Exact agent count: 47,979",
    "Exact department count: 1,777",
    "Exact unit count: 5,331",
    "Exact family count: 175",
    "Live runtime agents enabled: 0",
    "org_chart_export.json",
    "registered command-center operating units",
]

NAV_STRINGS = [
    "Home",
    "Demo Hub",
    "Simulator",
    "System Scale",
    "Agent Registry",
    "Safety Boundaries",
    "Review",
    "Full Audit Dashboard",
]

GLOSSARY_STRINGS = [
    "Registered agent",
    "Live runtime agent",
    "Runtime activation",
    "Static simulator",
    "Backend/Supabase readiness",
    "Validator",
    "Safety gate",
]

FORBIDDEN_PUBLIC_STRINGS = [
    "Current build: static preview",
    "Backend integration: planned",
    "backend integration is planned",
    "agent count unknown",
    "UNKNOWN_NOT_CURRENTLY_DECLARED",
    "about 47,000",
    "roughly",
    "approximate agent",
    "MVP-51 in progress",
    "Next milestone: 51 (In Progress)",
    "{_list(",
    "{_stat(",
    "{_badge(",
    "literal \\n",
]

FORBIDDEN_SIMULATOR_PATTERNS = [
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

REDIRECT_LINES = [
    "/simulator.html /demo/simulator.html 200",
    "/presentation.html /demo/presentation.html 200",
    "/system-scale.html /demo/system-scale.html 200",
    "/agent-registry.html /demo/agent-registry.html 200",
]

HTML_FILES = [
    DIST / "index.html",
    DIST / "demo" / "index.html",
    DIST / "demo" / "simulator.html",
    DIST / "demo" / "system-story.html",
    DIST / "demo" / "system-scale.html",
    DIST / "demo" / "agent-hierarchy.html",
    DIST / "demo" / "agent-registry.html",
    DIST / "demo" / "operating-model.html",
    DIST / "demo" / "validator-safety-map.html",
    DIST / "demo" / "safety-boundaries.html",
    DIST / "demo" / "technical-appendix.html",
    DIST / "demo" / "objections.html",
    DIST / "demo" / "review.html",
    DIST / "demo" / "review-qa.html",
    DIST / "demo" / "presentation.html",
]


def fail(message: str) -> None:
    raise SystemExit(message)


def read_text(path: Path) -> str:
    if not path.exists():
      fail(f"missing file: {path}")
    return path.read_text(encoding="utf-8")


def assert_contains(text: str, needle: str, context: str) -> None:
    if needle not in text:
        fail(f"missing string in {context}: {needle}")


def assert_not_contains(text: str, needle: str, context: str) -> None:
    if needle in text:
        fail(f"forbidden string in {context}: {needle}")


def normalize_target(page: Path, href: str) -> Path | None:
    if not href or href.startswith("#"):
        return None
    parsed = urlparse(href)
    if parsed.scheme in {"http", "https", "mailto", "tel"}:
        return None
    if href.startswith("//"):
        return None
    target = href.split("#", 1)[0].split("?", 1)[0]
    if not target:
        return None
    if target.startswith("/"):
        return (DIST / target.lstrip("/")).resolve()
    return (page.parent / target).resolve()


def parse_hrefs(text: str) -> list[str]:
    return re.findall(r'href=["\']([^"\']+)["\']', text, flags=re.I)


def main() -> None:
    for path in REQUIRED_FILES:
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    root_text = read_text(DIST / "index.html")
    demo_text = read_text(DIST / "demo" / "index.html")
    simulator_text = read_text(DIST / "demo" / "simulator.html")
    system_scale_text = read_text(DIST / "demo" / "system-scale.html")
    agent_hierarchy_text = read_text(DIST / "demo" / "agent-hierarchy.html")
    agent_registry_text = read_text(DIST / "demo" / "agent-registry.html")
    operating_model_text = read_text(DIST / "demo" / "operating-model.html")
    validator_map_text = read_text(DIST / "demo" / "validator-safety-map.html")
    review_text = read_text(DIST / "demo" / "review.html")
    review_qa_text = read_text(DIST / "demo" / "review-qa.html")
    technical_appendix_text = read_text(DIST / "demo" / "technical-appendix.html")
    safety_boundaries_text = read_text(DIST / "demo" / "safety-boundaries.html")

    for needle in ROOT_REQUIRED_STRINGS:
        assert_contains(root_text, needle, "root index")
    for needle in DEMO_REQUIRED_STRINGS:
        assert_contains(demo_text, needle, "demo hub")
    for needle in SIM_REQUIRED_STRINGS:
        assert_contains(simulator_text, needle, "simulator")
    for needle in REGISTRY_STRINGS:
        assert_contains(system_scale_text, needle, "system scale")
        assert_contains(agent_hierarchy_text, needle, "agent hierarchy")
        assert_contains(agent_registry_text, needle, "agent registry")
    for needle in NAV_STRINGS:
        assert_contains(demo_text, needle, "demo hub navigation")
        assert_contains(system_scale_text, needle, "system scale navigation")
        assert_contains(agent_hierarchy_text, needle, "agent hierarchy navigation")
        assert_contains(agent_registry_text, needle, "agent registry navigation")
        assert_contains(operating_model_text, needle, "operating model navigation")
        assert_contains(validator_map_text, needle, "validator map navigation")
        assert_contains(review_text, needle, "review navigation")
        assert_contains(review_qa_text, needle, "review qa navigation")
        assert_contains(technical_appendix_text, needle, "technical appendix navigation")
        assert_contains(safety_boundaries_text, needle, "safety boundaries navigation")
    for needle in GLOSSARY_STRINGS:
        assert_contains(root_text, needle, "root glossary")
        assert_contains(demo_text, needle, "demo glossary")
        assert_contains(technical_appendix_text, needle, "technical appendix glossary")
    for needle in FORBIDDEN_PUBLIC_STRINGS:
        for label, text in [
            ("root index", root_text),
            ("demo hub", demo_text),
            ("simulator", simulator_text),
            ("system scale", system_scale_text),
            ("agent hierarchy", agent_hierarchy_text),
            ("agent registry", agent_registry_text),
            ("operating model", operating_model_text),
            ("validator map", validator_map_text),
            ("review", review_text),
            ("review qa", review_qa_text),
            ("technical appendix", technical_appendix_text),
            ("safety boundaries", safety_boundaries_text),
        ]:
            assert_not_contains(text, needle, label)

    for needle in FORBIDDEN_SIMULATOR_PATTERNS:
        assert_not_contains(simulator_text, needle, "simulator")

    redirects = read_text(DIST / "_redirects")
    for line in REDIRECT_LINES:
        assert_contains(redirects, line, "_redirects")

    # Internal link validation for root + demo pages.
    for page in HTML_FILES:
        html = read_text(page)
        for href in parse_hrefs(html):
            target = normalize_target(page, href)
            if target is None:
                continue
            try:
                target.relative_to(DIST)
            except ValueError:
                fail(f"internal link escapes dist: {page.relative_to(ROOT)} -> {href}")
            if not target.exists():
                fail(f"broken internal link: {page.relative_to(ROOT)} -> {href}")

    raw = read_text(ROOT / "09_exports" / "system_registry" / "agent_department_registry_summary.json")
    data = json.loads(raw)
    expected = {
        "exact_agent_count": 47979,
        "exact_department_count": 1777,
        "exact_unit_count": 5331,
        "exact_family_count": 175,
        "hierarchy_level_count": 7,
        "operational_domain_count": 11,
        "live_runtime_agents_enabled": 0,
        "runtime_activation_started": False,
    }
    for key, value in expected.items():
        if data.get(key) != value:
            fail(f"registry mismatch: {key} expected={value!r} got={data.get(key)!r}")

    print("SEVEN_PERSONA_REVIEW_POLISH_AFTER_MVP50_VALIDATION_PASS")


if __name__ == "__main__":
    main()
