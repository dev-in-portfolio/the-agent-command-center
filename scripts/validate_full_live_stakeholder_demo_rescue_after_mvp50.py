#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "13_web_dashboard" / "dist"


class HrefCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        for key, value in attrs:
            if key.lower() == "href" and value is not None:
                self.hrefs.append(value)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fail(messages: list[str]) -> None:
    for message in messages:
        print(f"FAIL: {message}")
    sys.exit(1)


def require_file(relpath: str, errors: list[str]) -> None:
    path = ROOT / relpath
    if not path.exists():
        errors.append(f"missing required file: {relpath}")


def require_strings(relpath: str, strings: list[str], errors: list[str]) -> None:
    path = ROOT / relpath
    contents = read_text(path)
    for needle in strings:
        if needle not in contents:
            errors.append(f"{relpath} missing string: {needle}")


def scan_for_forbidden(relpath: str, forbidden: list[str], errors: list[str]) -> None:
    contents = read_text(ROOT / relpath)
    for needle in forbidden:
        if needle in contents:
            errors.append(f"{relpath} contains forbidden string: {needle}")


def resolve_href(base: Path, href: str) -> Path | None:
    href = href.strip()
    if not href:
        return None
    parsed = urlparse(href)
    if parsed.scheme in {"http", "https", "mailto", "tel", "javascript"}:
        return None
    if href.startswith("#"):
        return None
    resolved = (base.parent / parsed.path).resolve()
    if not str(resolved).startswith(str(DIST.resolve())):
        return None
    return resolved


def check_links(html_relpaths: list[str], errors: list[str]) -> None:
    for relpath in html_relpaths:
        path = ROOT / relpath
        collector = HrefCollector()
        collector.feed(read_text(path))
        for href in collector.hrefs:
            resolved = resolve_href(path, href)
            if resolved is None:
                continue
            if href.endswith("/") or resolved.is_dir():
                if not resolved.exists():
                    errors.append(f"{relpath} links to missing directory: {href}")
                    continue
                index_file = resolved / "index.html"
                if not index_file.exists():
                    errors.append(f"{relpath} links to directory without index.html: {href}")
                continue
            if not resolved.exists():
                errors.append(f"{relpath} links to missing file: {href}")


def check_redirects(errors: list[str]) -> None:
    redirects = read_text(DIST / "_redirects")
    expected = [
        "/presentation.html /demo/presentation.html 200",
        "/simulator.html /demo/simulator.html 200",
        "/system-story.html /demo/system-story.html 200",
        "/system-scale.html /demo/system-scale.html 200",
        "/agent-hierarchy.html /demo/agent-hierarchy.html 200",
        "/agent-registry.html /demo/agent-registry.html 200",
        "/operating-model.html /demo/operating-model.html 200",
        "/validator-safety-map.html /demo/validator-safety-map.html 200",
        "/safety-boundaries.html /demo/safety-boundaries.html 200",
        "/technical-appendix.html /demo/technical-appendix.html 200",
        "/objections.html /demo/objections.html 200",
        "/review.html /demo/review.html 200",
        "/demo /demo/index.html 200",
        "/dashboard /dashboard.html 200",
        "/full-dashboard /full-audit-dashboard.html 200",
        "/audit /full-audit-dashboard.html 200",
    ]
    for line in expected:
        if line not in redirects:
            errors.append(f"_redirects missing line: {line}")


def check_headers(errors: list[str]) -> None:
    headers = read_text(DIST / "_headers")
    for block in ["/", "/demo/*", "/*.html", "/index.html", "*.json"]:
        if block not in headers:
            errors.append(f"_headers missing block: {block}")


def check_netlify(errors: list[str]) -> None:
    contents = read_text(ROOT / "netlify.toml")
    if 'publish = "13_web_dashboard/dist"' not in contents:
        errors.append('netlify.toml missing publish = "13_web_dashboard/dist"')


def check_registry_summary(errors: list[str]) -> None:
    path = ROOT / "09_exports/system_registry/agent_department_registry_summary.json"
    data = json.loads(read_text(path))
    expected = {
        "exact_family_count": 175,
        "exact_department_count": 1777,
        "exact_unit_count": 5331,
        "exact_agent_count": 47979,
        "hierarchy_level_count": 7,
        "operational_domain_count": 11,
        "live_runtime_agents_enabled": 0,
        "runtime_activation_started": False,
        "source_file": "09_exports/org_chart_export.json",
        "source_type": "org_chart_export_json",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            errors.append(f"registry summary mismatch for {key}: expected {value!r}, got {data.get(key)!r}")


def main() -> int:
    errors: list[str] = []

    required_files = [
        "netlify.toml",
        "13_web_dashboard/dist/index.html",
        "13_web_dashboard/dist/dashboard.html",
        "13_web_dashboard/dist/full-audit-dashboard.html",
        "13_web_dashboard/dist/internal/full-audit-dashboard.html",
        "13_web_dashboard/dist/demo/index.html",
        "13_web_dashboard/dist/demo/simulator.html",
        "13_web_dashboard/dist/demo/presentation.html",
        "13_web_dashboard/dist/demo/system-story.html",
        "13_web_dashboard/dist/demo/system-scale.html",
        "13_web_dashboard/dist/demo/agent-hierarchy.html",
        "13_web_dashboard/dist/demo/agent-registry.html",
        "13_web_dashboard/dist/demo/operating-model.html",
        "13_web_dashboard/dist/demo/validator-safety-map.html",
        "13_web_dashboard/dist/demo/safety-boundaries.html",
        "13_web_dashboard/dist/demo/technical-appendix.html",
        "13_web_dashboard/dist/demo/objections.html",
        "13_web_dashboard/dist/demo/review.html",
        "13_web_dashboard/dist/demo/review-qa.html",
        "13_web_dashboard/dist/_redirects",
        "13_web_dashboard/dist/_headers",
        "09_exports/system_registry/agent_department_registry_summary.json",
    ]
    for relpath in required_files:
        require_file(relpath, errors)

    root_required_strings = [
        "Command Center Launchpad",
        "Premium Stakeholder Demo",
        "Open Premium Demo Hub",
        "Runnable Static Simulator",
        "Open Simulator",
        "Agent Registry",
        "View Exact Registry",
        "System Scale",
        "Safety Boundaries",
        "Review / Scorecard",
        "Full Internal Audit Dashboard",
        "Exact agent count: 47,979",
        "Exact department count: 1,777",
        "Exact unit count: 5,331",
        "Exact family count: 175",
        "Live runtime agents enabled: 0",
        "Runtime activation has not started",
        "Backend/Supabase readiness exists",
        "Live backend runtime disabled",
        "MVP-50 Production Verified",
        "MVP-51 not started",
        "./demo/",
        "./demo/simulator.html",
        "./demo/agent-registry.html",
        "./demo/system-scale.html",
        "./demo/safety-boundaries.html",
        "./demo/review.html",
        "./full-audit-dashboard.html",
        "./dashboard.html",
    ]
    require_strings("13_web_dashboard/dist/index.html", root_required_strings, errors)

    demo_required_strings = [
        "Stakeholder Demo Hub",
        "Production verified through MVP-50",
        "Command Center Launchpad",
        "Command Center Sandbox Simulator",
        "Simulator",
        "System Story",
        "System Scale",
        "Agent / Department Hierarchy",
        "Agent Registry",
        "Operating Model",
        "Validator and Safety Gate Map",
        "Safety Boundaries",
        "Technical Appendix",
        "Objections",
        "Review / Scorecard",
        "Launch Live Dashboard",
        "NOT_READY_FOR_REAL_AUTOMATION",
    ]
    require_strings("13_web_dashboard/dist/demo/index.html", demo_required_strings, errors)

    simulator_required_strings = [
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
        "No backend calls",
        "No writes",
        "No execution",
        "No automation",
    ]
    require_strings("13_web_dashboard/dist/demo/simulator.html", simulator_required_strings, errors)

    registry_scale_required_strings = [
        "Exact agent count: 47,979",
        "Exact department count: 1,777",
        "Exact unit count: 5,331",
        "Exact family count: 175",
        "Hierarchy levels: 7",
        "Operational domains: 11",
        "Live runtime agents enabled: 0",
        "Runtime activation: not started",
        "org_chart_export.json",
    ]
    for relpath in [
        "13_web_dashboard/dist/demo/system-scale.html",
        "13_web_dashboard/dist/demo/agent-hierarchy.html",
        "13_web_dashboard/dist/demo/agent-registry.html",
    ]:
        require_strings(relpath, registry_scale_required_strings, errors)

    forbidden_public = [
        "Current build: static preview",
        "Backend integration: planned",
        "backend integration is planned",
        "Future backend integration remains a later phase",
        "agent count unknown",
        "UNKNOWN_NOT_CURRENTLY_DECLARED as a headline",
        "approx agent",
        "approximate agent",
        "about 47,000",
        "roughly",
        "MVP-51 in progress",
        "Next milestone: 51 (In Progress)",
        "{_list(",
        "{_stat(",
        "{_badge(",
        "visible {_",
        "literal \\n",
    ]
    for relpath in [
        "13_web_dashboard/dist/index.html",
        "13_web_dashboard/dist/demo/index.html",
        "13_web_dashboard/dist/demo/simulator.html",
        "13_web_dashboard/dist/demo/presentation.html",
        "13_web_dashboard/dist/demo/system-story.html",
        "13_web_dashboard/dist/demo/system-scale.html",
        "13_web_dashboard/dist/demo/agent-hierarchy.html",
        "13_web_dashboard/dist/demo/agent-registry.html",
        "13_web_dashboard/dist/demo/operating-model.html",
        "13_web_dashboard/dist/demo/validator-safety-map.html",
        "13_web_dashboard/dist/demo/safety-boundaries.html",
        "13_web_dashboard/dist/demo/technical-appendix.html",
        "13_web_dashboard/dist/demo/objections.html",
        "13_web_dashboard/dist/demo/review.html",
        "13_web_dashboard/dist/demo/review-qa.html",
    ]:
        scan_for_forbidden(relpath, forbidden_public, errors)

    simulator_forbidden = [
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
    scan_for_forbidden("13_web_dashboard/dist/demo/simulator.html", simulator_forbidden, errors)

    check_netlify(errors)
    check_redirects(errors)
    check_headers(errors)
    check_registry_summary(errors)

    link_checks = [
        "13_web_dashboard/dist/index.html",
        "13_web_dashboard/dist/demo/index.html",
        "13_web_dashboard/dist/demo/simulator.html",
        "13_web_dashboard/dist/demo/presentation.html",
        "13_web_dashboard/dist/demo/system-story.html",
        "13_web_dashboard/dist/demo/system-scale.html",
        "13_web_dashboard/dist/demo/agent-hierarchy.html",
        "13_web_dashboard/dist/demo/agent-registry.html",
        "13_web_dashboard/dist/demo/operating-model.html",
        "13_web_dashboard/dist/demo/validator-safety-map.html",
        "13_web_dashboard/dist/demo/safety-boundaries.html",
        "13_web_dashboard/dist/demo/technical-appendix.html",
        "13_web_dashboard/dist/demo/objections.html",
        "13_web_dashboard/dist/demo/review.html",
        "13_web_dashboard/dist/demo/review-qa.html",
    ]
    check_links(link_checks, errors)

    if errors:
        fail(errors)

    print("FULL_LIVE_STAKEHOLDER_DEMO_RESCUE_AFTER_MVP50_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
