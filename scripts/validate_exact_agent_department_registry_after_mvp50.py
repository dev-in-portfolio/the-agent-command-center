#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "13_web_dashboard" / "dist"
DEMO = DIST / "demo"
REGISTRY = ROOT / "09_exports" / "system_registry"
REPORTS = ROOT / "09_exports" / "mvp_product_track"
PRESENTATION = ROOT / "09_exports" / "stakeholder_presentation_after_mvp50"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def visible_text(html: str) -> str:
    html = re.sub(r"<script\b[^>]*>.*?</script>", "", html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r"<style\b[^>]*>.*?</style>", "", html, flags=re.IGNORECASE | re.DOTALL)
    return html


def fail(failures: list[str], message: str) -> None:
    failures.append(message)


def require_path(failures: list[str], path: Path, label: str) -> None:
    if not path.exists():
        fail(failures, f"missing {label}: {path}")


def contains_any(text: str, needles: list[str]) -> list[str]:
    return [needle for needle in needles if needle in text]


def main() -> int:
    failures: list[str] = []

    required_files = [
        ROOT / "scripts" / "discover_agent_department_registry_after_mvp50.py",
        REGISTRY / "agent_registry.json",
        REGISTRY / "department_registry.json",
        REGISTRY / "system_hierarchy.json",
        REGISTRY / "agent_department_registry_summary.json",
        REGISTRY / "agent_department_registry_traceability.md",
        REGISTRY / "discovery" / "agent_department_discovery_report.md",
        DIST / "index.html",
        DIST / "_redirects",
        DEMO / "index.html",
        DEMO / "presentation.html",
        DEMO / "simulator.html",
        DEMO / "system-story.html",
        DEMO / "system-scale.html",
        DEMO / "agent-hierarchy.html",
        DEMO / "agent-registry.html",
        DEMO / "demo-package.json",
        DEMO / "data" / "agent_registry_summary.json",
        DEMO / "data" / "department_registry_summary.json",
        DEMO / "data" / "system_hierarchy_summary.json",
        DEMO / "data" / "agent_department_registry_traceability.html",
        REPORTS / "exact_agent_department_registry_after_mvp50_report.md",
    ]
    for path in required_files:
        require_path(failures, path, path.name)

    summary_path = REGISTRY / "agent_department_registry_summary.json"
    if summary_path.exists():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(failures, f"unable to parse summary json: {exc}")
            summary = {}
        else:
            checks = {
                "exact_agent_count": 47979,
                "exact_department_count": 1777,
                "hierarchy_level_count": 7,
                "operational_domain_count": 11,
                "live_runtime_agents_enabled": 0,
                "runtime_activation_started": False,
                "formal_registry_status": "GENERATED_FROM_PROJECT_ARTIFACTS",
                "count_type": "DERIVED_FROM_PROJECT_ARTIFACTS",
                "discovery_status": "COMPLETE",
            }
            for key, expected in checks.items():
                if summary.get(key) != expected:
                    fail(failures, f"summary field {key} expected {expected!r} got {summary.get(key)!r}")
            if not isinstance(summary.get("exact_agent_count"), int) or summary["exact_agent_count"] <= 0:
                fail(failures, "exact_agent_count is not a positive integer")
            if not isinstance(summary.get("exact_department_count"), int) or summary["exact_department_count"] <= 0:
                fail(failures, "exact_department_count is not a positive integer")

    for file_name, expected_len in [
        ("agent_registry.json", 47979),
        ("department_registry.json", 1777),
    ]:
        path = REGISTRY / file_name
        if path.exists():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                fail(failures, f"unable to parse {file_name}: {exc}")
                continue
            key = "agents" if file_name == "agent_registry.json" else "departments"
            items = payload.get(key) if isinstance(payload, dict) else None
            if not isinstance(items, list):
                fail(failures, f"{file_name} missing {key} array")
            elif len(items) != expected_len:
                fail(failures, f"{file_name} expected length {expected_len} got {len(items)}")

    hierarchy_path = REGISTRY / "system_hierarchy.json"
    if hierarchy_path.exists():
        try:
            hierarchy = json.loads(hierarchy_path.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(failures, f"unable to parse system_hierarchy.json: {exc}")
        else:
            if not isinstance(hierarchy, dict):
                fail(failures, "system_hierarchy.json is not a JSON object")
            else:
                if hierarchy.get("hierarchy_level_count") != 7:
                    fail(failures, f"system_hierarchy.json hierarchy_level_count expected 7 got {hierarchy.get('hierarchy_level_count')!r}")
                if hierarchy.get("operational_domain_count") != 11:
                    fail(failures, f"system_hierarchy.json operational_domain_count expected 11 got {hierarchy.get('operational_domain_count')!r}")
                registry_structure = hierarchy.get("registry_structure", {})
                expected_registry_structure = {
                    "exact_family_count": 175,
                    "exact_department_count": 1777,
                    "exact_unit_count": 5331,
                    "exact_agent_count": 47979,
                }
                for key, expected in expected_registry_structure.items():
                    if registry_structure.get(key) != expected:
                        fail(failures, f"system_hierarchy.json {key} expected {expected} got {registry_structure.get(key)!r}")

    root_html = read_text(DIST / "index.html") if (DIST / "index.html").exists() else ""
    demo_index = read_text(DEMO / "index.html") if (DEMO / "index.html").exists() else ""
    demo_pages = {
        name: read_text(DEMO / name)
        for name in [
            "presentation.html",
            "simulator.html",
            "system-story.html",
            "system-scale.html",
            "agent-hierarchy.html",
            "agent-registry.html",
        ]
        if (DEMO / name).exists()
    }
    visible_root = visible_text(root_html)
    visible_demo_index = visible_text(demo_index)
    visible_demo_pages = {name: visible_text(text) for name, text in demo_pages.items()}
    page_blobs = [visible_root, visible_demo_index, *visible_demo_pages.values(), read_text(DEMO / "demo-package.json") if (DEMO / "demo-package.json").exists() else ""]

    current_root_strings = [
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
    for needle in current_root_strings:
        if needle not in visible_root:
            fail(failures, f"root dashboard missing {needle!r}")

    archive_text = visible_text(read_text(DIST / "full-audit-dashboard.html")) if (DIST / "full-audit-dashboard.html").exists() else ""
    archive_required_strings = [
        "Open Static Simulator",
        "Current Status / Readiness Overview",
        "Original Full Audit Dashboard",
        "Latest Verified MVP",
        "Backend/Supabase readiness architecture exists",
        "Live backend runtime is disabled",
        "MVP-50",
    ]
    for needle in archive_required_strings:
        if needle not in archive_text:
            fail(failures, f"archive dashboard missing {needle!r}")

    required_demo_index_strings = [
        "Stakeholder Demo Hub",
        "Production verified through MVP-50",
        "Command Center Sandbox Simulator",
        "./simulator.html",
        "Launch Live Dashboard",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "Agent Registry",
    ]
    for needle in required_demo_index_strings:
        if needle not in visible_demo_index:
            fail(failures, f"demo index missing {needle!r}")

    required_simulator_strings = [
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
    ]
    simulator_text = visible_demo_pages.get("simulator.html", "")
    for needle in required_simulator_strings:
        if needle not in simulator_text:
            fail(failures, f"simulator page missing {needle!r}")

    required_registry_strings = [
        "Exact agent count: 47,979",
        "Exact department count: 1,777",
        "Registry source",
        "09_exports/org_chart_export.json",
        "Traceability",
    ]
    registry_text = visible_demo_pages.get("agent-registry.html", "")
    for needle in required_registry_strings:
        if needle not in registry_text:
            fail(failures, f"agent registry page missing {needle!r}")

    for page_name, text in visible_demo_pages.items():
        forbidden = contains_any(
            text,
            [
                "UNKNOWN_NOT_CURRENTLY_DECLARED",
                "{_list(",
                "{_stat(",
                "{_badge(",
                "backend integration is planned",
                "Backend integration: planned",
                "no backend integration",
                "backend missing",
                "backend does not exist",
                "MVP-51 in progress",
                "approx",
                "about",
                "roughly",
                "\\n",
            ],
        )
        if forbidden:
            fail(failures, f"{page_name} contains forbidden text: {forbidden}")

    if "{_list(" in visible_root or "{_stat(" in visible_root or "{_badge(" in visible_root or "{_" in visible_root:
        fail(failures, "root dashboard contains raw template fragments")
    if "\\n" in visible_root:
        fail(failures, "root dashboard contains literal \\n")

    redirects = read_text(DIST / "_redirects") if (DIST / "_redirects").exists() else ""
    for needle in [
        "/demo /demo/index.html 200",
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
    ]:
        if needle not in redirects:
            fail(failures, f"_redirects missing {needle!r}")

    if "UNKNOWN_NOT_CURRENTLY_DECLARED" in visible_root:
        fail(failures, "root dashboard still uses UNKNOWN_NOT_CURRENTLY_DECLARED")
    if "MVP-51 in progress" in visible_root:
        fail(failures, "root dashboard still says MVP-51 in progress")
    if "backend integration is planned" in visible_root:
        fail(failures, "root dashboard still says backend integration is planned")

    demo_package_path = DEMO / "demo-package.json"
    if demo_package_path.exists():
        try:
            demo_package = json.loads(demo_package_path.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(failures, f"unable to parse demo-package.json: {exc}")
        else:
            expected_demo_fields = {
                "registry_source": "09_exports/org_chart_export.json",
                "exact_family_count": 175,
                "exact_department_count": 1777,
                "exact_unit_count": 5331,
                "exact_agent_count": 47979,
                "hierarchy_level_count": 7,
                "operational_domain_count": 11,
                "live_runtime_agents_enabled": 0,
                "runtime_activation_started": False,
                "backend_runtime_enabled": False,
                "supabase_writes_enabled": False,
                "public_writes_enabled": False,
                "command_execution_enabled": False,
                "action_execution_enabled": False,
                "automation_enabled": False,
                "simulator_page": "simulator.html",
                "simulator_type": "static_in_memory_sandbox",
            }
            for key, expected in expected_demo_fields.items():
                if demo_package.get(key) != expected:
                    fail(failures, f"demo-package field {key} expected {expected!r} got {demo_package.get(key)!r}")

    if any("UNKNOWN_NOT_CURRENTLY_DECLARED" in blob for blob in page_blobs):
        fail(failures, "one or more published pages still contain UNKNOWN_NOT_CURRENTLY_DECLARED")

    if any(re.search(r"\b(approx|about|roughly)\b", blob, re.IGNORECASE) for blob in [demo_index, simulator_text, registry_text]):
        fail(failures, "approximate agent count wording remains in demo pages")

    if failures:
        print("EXACT_AGENT_DEPARTMENT_REGISTRY_AFTER_MVP50_VALIDATION_FAIL")
        for failure in failures:
            print(" -", failure)
        return 1

    print("EXACT_AGENT_DEPARTMENT_REGISTRY_AFTER_MVP50_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
