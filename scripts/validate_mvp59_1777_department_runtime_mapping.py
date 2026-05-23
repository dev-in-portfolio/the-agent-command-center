#!/usr/bin/env python3
"""Validate the MVP-59 1,777-department runtime mapping pass."""

from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent

required_files = [
    ROOT / "09_exports" / "org_chart_export.json",
    ROOT / "09_exports" / "runtime_department_mapping_mvp59" / "runtime_department_map.json",
    ROOT / "09_exports" / "runtime_department_mapping_mvp59" / "runtime_department_mapping_summary.json",
    ROOT / "supabase" / "migrations" / "20260522_mvp59_department_runtime_mapping.sql",
    ROOT / "netlify" / "functions" / "_shared" / "runtime_department_helpers.js",
    ROOT / "netlify" / "functions" / "list-runtime-departments.js",
    ROOT / "netlify" / "functions" / "get-runtime-department.js",
    ROOT / "netlify" / "functions" / "assign-department-runtime-lane.js",
    ROOT / "netlify" / "functions" / "update-department-readiness.js",
    ROOT / "netlify" / "functions" / "create-department-readiness-note.js",
    ROOT / "netlify" / "functions" / "department-runtime-rollup.js",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "runtime-department-map.html",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "assets" / "runtime-department-map.js",
    ROOT / "13_web_dashboard" / "dist" / "demo" / "index.html",
    ROOT / "13_web_dashboard" / "dist" / "index.html",
    ROOT / "09_exports" / "mvp_product_track" / "mvp59_1777_department_runtime_mapping_report.md",
]

migration_required = [
    "runtime_departments",
    "runtime_department_lane_assignments",
    "runtime_department_readiness_notes",
    "runtime_department_events",
    "runtime_department_rollups",
    "command_execution_enabled boolean not null default false",
    "deploy_execution_enabled boolean not null default false",
    "rollback_execution_enabled boolean not null default false",
    "alert_sending_enabled boolean not null default false",
    "full_47979_activation_blocked boolean not null default true",
    "total_departments integer not null default 1777",
    "total_units integer not null default 5331",
    "total_families integer not null default 175",
    "full 47,979 activation is blocked",
    "activate_all is blocked",
    "Mapping is not activation.",
]

function_required = [
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "runtime_departments",
    "runtime_department_lane_assignments",
    "runtime_department_readiness_notes",
    "runtime_department_events",
    "runtime_department_rollups",
    "backendUnavailable",
    "isApprovedLane",
    "buildRollupSnapshot",
]

ui_required = [
    "1,777-Department Runtime Map",
    "Map all command-center departments to supervised runtime readiness without activating the full agent registry.",
    "Total registered agents: 47,979",
    "Total departments: 1,777",
    "Total units: 5,331",
    "Total families: 175",
    "Live runtime agents enabled: 0–1,000 from MVP-58",
    "Department runtime mapping: 1,777 departments",
    "Full 47,979 activation: blocked",
    "Command execution: disabled",
    "Deploy execution: disabled",
    "Rollback execution: disabled",
    "Alert sending: disabled",
    "Mapping is not activation.",
    "Eligible does not mean executing.",
    "No department can run commands from this page.",
    "Full 47,979-agent activation remains blocked.",
    "Open 1,777-Department Runtime Map",
    "Refresh rollup",
    "Search departments",
    "Filter by status",
    "Assign runtime lane",
    "Update readiness status",
    "Create readiness note",
    "Export current mapping view as JSON",
]

report_required = [
    "MVP59_1777_DEPARTMENT_RUNTIME_MAPPING_COMPLETE",
    "MVP58_PREREQUISITE_PASSED",
    "CANONICAL_REGISTRY_SOURCE_FOUND",
    "EXACT_1777_DEPARTMENTS_MAPPED",
    "EXACT_47979_REGISTERED_AGENTS_PRESERVED",
    "EXACT_5331_UNITS_PRESERVED",
    "EXACT_175_FAMILIES_PRESERVED",
    "RUNTIME_DEPARTMENTS_TABLE_ADDED",
    "DEPARTMENT_LANE_ASSIGNMENTS_ADDED",
    "DEPARTMENT_READINESS_NOTES_ADDED",
    "DEPARTMENT_EVENTS_ADDED",
    "DEPARTMENT_ROLLUPS_ADDED",
    "DEPARTMENT_MAPPING_FUNCTIONS_ADDED",
    "DEPARTMENT_RUNTIME_MAP_UI_ADDED",
    "DEMO_HUB_LINK_ADDED",
    "MAPPING_IS_NOT_ACTIVATION_COPY_ADDED",
    "FULL_47979_ACTIVATION_BLOCKED",
    "COMMAND_EXECUTION_DISABLED",
    "DEPLOY_EXECUTION_DISABLED",
    "ROLLBACK_EXECUTION_DISABLED",
    "ALERT_SENDING_DISABLED",
    "SERVICE_ROLE_SERVER_SIDE_ONLY",
    "NO_SERVICE_ROLE_IN_BROWSER",
    "NO_ARBITRARY_SQL_ENDPOINT_ADDED",
    "NO_ARBITRARY_COMMAND_ENDPOINT_ADDED",
]

browser_js_required = [
    "/.netlify/functions/list-runtime-departments",
    "/.netlify/functions/get-runtime-department",
    "/.netlify/functions/assign-department-runtime-lane",
    "/.netlify/functions/update-department-readiness",
    "/.netlify/functions/create-department-readiness-note",
    "/.netlify/functions/department-runtime-rollup",
]

browser_js_forbidden = [
    "SUPABASE_SERVICE_ROLE_KEY",
    "localStorage",
    "sessionStorage",
    "document.cookie",
    "indexedDB",
    "child_process",
    "exec(",
    "spawn(",
    "eval(",
    "new Function",
]


def fail(message: str) -> None:
    print("MVP59_1777_DEPARTMENT_RUNTIME_MAPPING_VALIDATION_FAIL")
    print(f"  - {message}")
    sys.exit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def load_json(path: Path):
    return json.loads(read(path))


def count_registry(source: dict[str, object]) -> dict[str, int]:
    families = source.get("families")
    require(isinstance(families, list), "Canonical registry source missing families array.")

    family_count = len(families)
    department_count = 0
    unit_count = 0
    agent_count = 0

    for family in families:
        require(isinstance(family, dict), "Canonical registry family entry is not an object.")
        departments = family.get("departments")
        require(isinstance(departments, list), "Canonical registry family missing departments array.")
        department_count += len(departments)
        for department in departments:
            require(isinstance(department, dict), "Canonical registry department entry is not an object.")
            units = department.get("units")
            require(isinstance(units, list), "Canonical registry department missing units array.")
            unit_count += len(units)
            for unit in units:
                require(isinstance(unit, dict), "Canonical registry unit entry is not an object.")
                team = unit.get("team")
                require(isinstance(team, list), "Canonical registry unit missing team array.")
                agent_count += len(team)

    return {
        "families": family_count,
        "departments": department_count,
        "units": unit_count,
        "agents": agent_count,
    }


prereq = subprocess.run(
    ["python3", str(ROOT / "scripts" / "validate_mvp58_1000_agent_runtime_division.py")],
    capture_output=True,
    text=True,
)
require(
    prereq.returncode == 0 and "MVP58_1000_AGENT_RUNTIME_DIVISION_VALIDATION_PASS" in prereq.stdout,
    "MVP-58 prerequisite validator did not pass.",
)

for path in required_files:
    require(path.exists(), f"Missing required file: {path.relative_to(ROOT)}")

registry_source = load_json(required_files[0])
registry_counts = count_registry(registry_source)
require(registry_counts["families"] == 175, f"Canonical registry family count mismatch: {registry_counts['families']}")
require(registry_counts["departments"] == 1777, f"Canonical registry department count mismatch: {registry_counts['departments']}")
require(registry_counts["units"] == 5331, f"Canonical registry unit count mismatch: {registry_counts['units']}")
require(registry_counts["agents"] == 47979, f"Canonical registry agent count mismatch: {registry_counts['agents']}")

map_payload = load_json(required_files[1])
require(isinstance(map_payload, dict), "Derived runtime department map must be a JSON object.")
departments = map_payload.get("departments")
require(isinstance(departments, list), "Derived runtime department map missing departments array.")
require(len(departments) == 1777, f"Derived runtime department map must contain exactly 1777 departments, found {len(departments)}.")
require(len({department.get("department_id") for department in departments}) == 1777, "Derived runtime department map contains duplicate department ids.")

expected_department_keys = {
    "department_id",
    "department_name",
    "family_id",
    "family_name",
    "family_folder",
    "family_file",
    "family_readme",
    "department_manager",
    "department_scribe",
    "department_auditor",
    "unit_count",
    "unit_ids",
    "unit_names",
    "primary_unit_id",
    "primary_unit_name",
    "registered_agent_count",
    "department_index",
    "family_index",
    "mapped_runtime_lane_id",
    "mapped_runtime_lane_name",
    "mapped_runtime_lane_order",
    "mapped_runtime_subdivision_id",
    "mapped_runtime_subdivision_name",
    "mapped_runtime_subdivision_order",
    "mapped_agent_capacity",
    "runtime_status",
    "activation_eligible",
    "audit_status",
    "notes_count",
    "last_readiness_update",
    "source_file",
    "source",
}
for department in departments[:5] + departments[-5:]:
    require(expected_department_keys.issubset(department.keys()), "Derived runtime department map entry is missing required fields.")

summary = load_json(required_files[2])
summary_required_values = {
    "total_registered_agents": 47979,
    "total_departments": 1777,
    "total_units": 5331,
    "total_families": 175,
    "mapped_departments": 1777,
    "full_47979_activation_blocked": True,
    "command_execution_enabled": False,
    "deploy_execution_enabled": False,
    "rollback_execution_enabled": False,
    "alert_sending_enabled": False,
}
for key, value in summary_required_values.items():
    require(summary.get(key) == value, f"Summary field {key} mismatch: {summary.get(key)!r} != {value!r}")
require(summary.get("source_file") == "09_exports/org_chart_export.json", "Summary source_file mismatch.")

migration_text = read(required_files[3])
for needle in migration_required:
    require(needle in migration_text, f"Migration missing required string: {needle}")

function_text = "\n".join(read(path) for path in required_files[4:11])
for needle in function_required:
    require(needle in function_text, f"Function layer missing required string: {needle}")

ui_text = "\n".join(read(path) for path in required_files[11:15])
for needle in ui_required:
    require(needle in ui_text, f"Runtime department mapping UI missing required string: {needle}")

page_text = read(required_files[11])
require('<header class="demo-topbar collapsible-topbar" data-collapsible-menu>' in page_text, "Runtime department page missing collapsible menu header.")
require('data-action="toggle-menu"' in page_text, "Runtime department page missing toggle menu button.")
require('aria-expanded="false"' in page_text, "Runtime department page missing collapsed aria state.")
require('data-menu-panel' in page_text, "Runtime department page missing menu panel.")
require('hidden' in page_text, "Runtime department page missing hidden menu panel marker.")
require('<nav class="nav-links"' not in page_text, "Runtime department page still contains an always-visible nav row.")
require("Demo Hub" in page_text, "Runtime department breadcrumb missing Demo Hub.")
require("Home" in page_text, "Runtime department breadcrumb missing Home.")
require("1,777-Department Runtime Map" in page_text, "Runtime department page title missing.")

report_text = read(required_files[15])
for needle in report_required:
    require(needle in report_text, f"Report missing required marker: {needle}")

js_text = read(required_files[12])
for needle in browser_js_required:
    require(needle in js_text, f"Browser JS missing required endpoint: {needle}")
for needle in browser_js_forbidden:
    require(needle not in js_text, f"Forbidden browser JS string present: {needle}")

browser_surface = page_text + "\n" + js_text
for needle in [
    "activate-all",
    "activate-all-departments",
    "activate-47979",
]:
    require(needle not in browser_surface, f"Forbidden activation route text present in browser surface: {needle}")

print("MVP59_1777_DEPARTMENT_RUNTIME_MAPPING_VALIDATION_PASS")
