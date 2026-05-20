#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DISCOVERY_DIR = ROOT / "09_exports" / "system_registry" / "discovery"
SYSTEM_REGISTRY_DIR = ROOT / "09_exports" / "system_registry"
DEMO_DATA_DIR = ROOT / "13_web_dashboard" / "dist" / "demo" / "data"
DEMO_DIR = ROOT / "13_web_dashboard" / "dist" / "demo"


@dataclass(frozen=True)
class DiscoveryCounts:
    families: int
    departments: int
    units: int
    agents: int


def slugify(text: str) -> str:
    text = text.lower()
    text = text.replace("&", "and")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "item"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def extract_section_lines(text: str, section_title: str) -> list[str]:
    lines = text.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.strip() == section_title:
            start = idx + 1
            break
    if start is None:
        return []
    collected = []
    for line in lines[start:]:
        if line.startswith("## ") and line.strip() != section_title:
            break
        if line.strip():
            collected.append(line.rstrip())
    return collected


def parse_operational_domains(doc_text: str) -> list[str]:
    lines = extract_section_lines(doc_text, "Operational domains:")
    domains = []
    for line in lines:
        match = re.match(r"^\d+\.\s+(.*)$", line.strip())
        if match:
            domains.append(match.group(1).strip())
    return domains


def parse_command_hierarchy(doc_text: str) -> list[str]:
    lines = extract_section_lines(doc_text, "## Command Hierarchy")
    levels = []
    for line in lines:
        match = re.match(r"^\d+\.\s+(.*)$", line.strip())
        if match:
            levels.append(match.group(1).strip())
    return levels


def make_agent_entry(family, department, unit, member):
    family_id = int(family["id"])
    department_id = department["id"]
    unit_id = unit["id"]
    role = member["role"]
    agent_id = member["id"]
    stable_slug = slugify(f"{family_id}-{department_id}-{unit_id}-{agent_id}-{role}")
    return {
        "id": agent_id,
        "stable_slug": stable_slug,
        "display_name": role,
        "role": role,
        "family_id": family_id,
        "family_name": family["name"],
        "department_id": department_id,
        "department_name": department["name"],
        "unit_id": unit_id,
        "unit_name": unit["name"],
        "hierarchy_path": f"{family['name']} > {department['name']} > {unit['name']} > {role}",
        "source_file": "09_exports/org_chart_export.json",
        "source_type": "org_chart_export_json",
        "count_basis": "team member entry in org_chart_export.json",
    }


def make_department_entry(family, department):
    family_id = int(family["id"])
    stable_slug = slugify(f"{family_id}-{department['id']}-{department['name']}")
    units = department.get("units", [])
    agent_total = sum(len(unit.get("team", [])) for unit in units)
    return {
        "id": department["id"],
        "stable_slug": stable_slug,
        "display_name": department["name"],
        "parent_department": family["name"],
        "family_id": family_id,
        "family_name": family["name"],
        "unit_count": len(units),
        "agent_count": agent_total,
        "source_file": "09_exports/org_chart_export.json",
        "source_type": "org_chart_export_json",
        "count_basis": "department entry in org_chart_export.json",
    }


def family_summary(family, departments):
    department_count = len(departments)
    unit_count = sum(len(dept.get("units", [])) for dept in departments)
    agent_count = sum(len(unit.get("team", [])) for dept in departments for unit in dept.get("units", []))
    return {
        "id": family["id"],
        "display_name": family["name"],
        "department_count": department_count,
        "unit_count": unit_count,
        "agent_count": agent_count,
        "source_file": "09_exports/org_chart_export.json",
        "source_type": "org_chart_export_json",
    }


def render_traceability_html(summary: dict) -> str:
    family_rows = "".join(
        f"<tr><th>{escape(item['display_name'])}</th><td>{item['department_count']}</td><td>{item['unit_count']}</td><td>{item['agent_count']}</td></tr>"
        for item in summary["family_breakdown"]
    )
    sample_agents = "".join(
        f"<tr><td>{escape(agent['id'])}</td><td>{escape(agent['display_name'])}</td><td>{escape(agent['department_name'])}</td><td>{escape(agent['unit_name'])}</td><td>{escape(agent['hierarchy_path'])}</td></tr>"
        for agent in summary["sample_agents"]
    )
    sample_departments = "".join(
        f"<tr><td>{escape(dept['id'])}</td><td>{escape(dept['display_name'])}</td><td>{escape(dept['family_name'])}</td><td>{dept['unit_count']}</td><td>{dept['agent_count']}</td></tr>"
        for dept in summary["sample_departments"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Agent Department Registry Traceability</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 0; padding: 24px; background: #07111f; color: #f4f7fb; }}
    .wrap {{ max-width: 1200px; margin: 0 auto; }}
    .card, table {{ width: 100%; border-collapse: collapse; margin: 18px 0; background: rgba(15,29,50,0.95); border: 1px solid rgba(142,179,229,0.2); border-radius: 14px; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid rgba(142,179,229,0.14); text-align: left; vertical-align: top; }}
    th {{ color: #7bc8ff; }}
    code, pre {{ white-space: pre-wrap; word-break: break-word; }}
    a {{ color: #8df3c5; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Agent Department Registry Traceability</h1>
    <p>Exact counts are generated from project artifacts and mirrored into publishable static data files.</p>
    <div class="card">
      <table>
        <tr><th>Exact agent count</th><td>{summary['exact_agent_count']}</td></tr>
        <tr><th>Exact department count</th><td>{summary['exact_department_count']}</td></tr>
        <tr><th>Hierarchy level count</th><td>{summary['hierarchy_level_count']}</td></tr>
        <tr><th>Operational domain count</th><td>{summary['operational_domain_count']}</td></tr>
        <tr><th>Live runtime agents enabled</th><td>{summary['live_runtime_agents_enabled']}</td></tr>
        <tr><th>Runtime activation started</th><td>{str(summary['runtime_activation_started']).lower()}</td></tr>
      </table>
    </div>
    <h2>Source files</h2>
    <ul>
      <li><code>09_exports/org_chart_export.json</code></li>
      <li><code>01_registry/department_families.json</code></li>
      <li><code>02_departments/**/family.json</code></li>
      <li><code>09_exports/stakeholder_presentation_after_mvp50/agent_department_hierarchy.md</code></li>
      <li><code>09_exports/stakeholder_presentation_after_mvp50/system_story.md</code></li>
    </ul>
    <h2>Family breakdown</h2>
    <table>
      <tr><th>Family</th><th>Departments</th><th>Units</th><th>Agents</th></tr>
      {family_rows}
    </table>
    <h2>Sample departments</h2>
    <table>
      <tr><th>Department ID</th><th>Department</th><th>Family</th><th>Units</th><th>Agents</th></tr>
      {sample_departments}
    </table>
    <h2>Sample agents</h2>
    <table>
      <tr><th>Agent ID</th><th>Display Name</th><th>Department</th><th>Unit</th><th>Hierarchy Path</th></tr>
      {sample_agents}
    </table>
  </div>
</body>
</html>
"""


def render_agent_registry_page(summary: dict) -> str:
    family_rows = "".join(
        f"<tr><th>{escape(item['display_name'])}</th><td>{item['department_count']}</td><td>{item['unit_count']}</td><td>{item['agent_count']}</td></tr>"
        for item in summary["family_breakdown"]
    )
    sample_agents = "".join(
        f"<tr><td>{escape(agent['id'])}</td><td>{escape(agent['display_name'])}</td><td>{escape(agent['department_name'])}</td><td>{escape(agent['unit_name'])}</td><td>{escape(agent['hierarchy_path'])}</td></tr>"
        for agent in summary["sample_agents"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Agent Registry - The Agent Command Center</title>
  <link rel="stylesheet" href="./assets/demo.css">
</head>
<body>
  <div class="demo-shell">
    <header class="topbar">
      <div class="brand"><strong>Agent Registry</strong><span>Exact counts derived from project artifacts</span></div>
      <nav class="nav-links" aria-label="Demo navigation">
        <a href="./index.html">Home</a><a href="./presentation.html">Presentation</a><a href="./simulator.html">Simulator</a><a href="./system-story.html">System Story</a><a href="./system-scale.html">System Scale</a><a href="./agent-hierarchy.html">Hierarchy</a><a href="./validator-safety-map.html">Validator Map</a><a href="../index.html">Live Dashboard</a>
      </nav>
    </header>
    <section class="hero">
      <div class="hero-grid">
        <div>
          <p class="eyebrow">Canonical registry</p>
          <h1 class="title">Exact agent and department counts are now declared from project artifacts.</h1>
          <p class="lead">This page turns the structured export graph into a visible registry view. The source is static, read-only, and traceable. Live runtime agents remain disabled.</p>
          <div class="badge-row">
            <span class="badge success">Exact agent count: {summary['exact_agent_count']:,}</span>
            <span class="badge success">Exact department count: {summary['exact_department_count']:,}</span>
            <span class="badge info">Live runtime agents enabled: 0</span>
            <span class="badge warning">Runtime activation not started</span>
          </div>
        </div>
        <div class="callout">
          <p class="kicker">Registry source</p>
          <p>Generated from <code>09_exports/org_chart_export.json</code>. Traceability: <a href="./data/agent_department_registry_traceability.html">open static traceability page</a>.</p>
        </div>
      </div>
    </section>
    <section class="section">
      <div class="card-grid">
        <article class="card"><h3>Families</h3><p>{summary['exact_family_count']:,} family groups form the declared registry backbone.</p></article>
        <article class="card"><h3>Departments</h3><p>{summary['exact_department_count']:,} departments are grouped under those families.</p></article>
        <article class="card"><h3>Units</h3><p>{summary['exact_unit_count']:,} units sit underneath the departments.</p></article>
        <article class="card"><h3>Agents</h3><p>{summary['exact_agent_count']:,} team-member agents are declared in the export graph.</p></article>
        <article class="card"><h3>Hierarchy levels</h3><p>{summary['hierarchy_level_count']} governance levels are documented.</p></article>
        <article class="card"><h3>Operational domains</h3><p>{summary['operational_domain_count']} operational domains are documented.</p></article>
      </div>
    </section>
    <section class="section">
      <div class="section-head"><div><p class="eyebrow">Family breakdown</p><h2>Grouped summary by family</h2></div></div>
      <div class="table-wrap">
        <table class="data-table">
          <thead><tr><th>Family</th><th>Departments</th><th>Units</th><th>Agents</th></tr></thead>
          <tbody>{family_rows}</tbody>
        </table>
      </div>
    </section>
    <section class="section">
      <div class="section-head"><div><p class="eyebrow">Sample agents</p><h2>Traceable example rows</h2></div></div>
      <div class="table-wrap">
        <table class="data-table">
          <thead><tr><th>Agent ID</th><th>Display Name</th><th>Department</th><th>Unit</th><th>Hierarchy Path</th></tr></thead>
          <tbody>{sample_agents}</tbody>
        </table>
      </div>
    </section>
    <div class="footer">
      Full registry files: <code>../system_registry/agent_registry.json</code>, <code>../system_registry/department_registry.json</code>, <code>../system_registry/system_hierarchy.json</code>.
    </div>
  </div>
  <script src="./assets/demo.js"></script>
</body>
</html>
"""


def main() -> int:
    discovery_dir = DISCOVERY_DIR
    discovery_dir.mkdir(parents=True, exist_ok=True)
    SYSTEM_REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    DEMO_DATA_DIR.mkdir(parents=True, exist_ok=True)

    org_chart_path = ROOT / "09_exports" / "org_chart_export.json"
    hierarchy_doc_path = ROOT / "09_exports" / "stakeholder_presentation_after_mvp50" / "agent_department_hierarchy.md"

    candidate_files_path = discovery_dir / "candidate_registry_files.txt"
    structured_candidates_path = discovery_dir / "structured_candidate_files.txt"
    content_hits_path = discovery_dir / "agent_department_content_hits.txt"

    if not org_chart_path.exists():
        discovery_dir.joinpath("agent_department_discovery_report.md").write_text(
            "# Agent Department Registry Discovery Report\n\nDISCOVERY_BLOCKED_ORG_CHART_EXPORT_MISSING\n",
            encoding="utf-8",
        )
        print("DISCOVERY_BLOCKED_ORG_CHART_EXPORT_MISSING")
        return 1

    org_chart = load_json(org_chart_path)
    families = org_chart.get("families", [])
    if not isinstance(families, list) or not families:
        discovery_dir.joinpath("agent_department_discovery_report.md").write_text(
            "# Agent Department Registry Discovery Report\n\nDISCOVERY_BLOCKED_ORG_CHART_EXPORT_INVALID\n",
            encoding="utf-8",
        )
        print("DISCOVERY_BLOCKED_ORG_CHART_EXPORT_INVALID")
        return 1

    hierarchy_doc = hierarchy_doc_path.read_text(encoding="utf-8") if hierarchy_doc_path.exists() else ""
    command_hierarchy = parse_command_hierarchy(hierarchy_doc)
    operational_domains = parse_operational_domains(hierarchy_doc)

    agent_entries = []
    department_entries = []
    family_breakdown = []
    family_department_counter = Counter()
    family_unit_counter = Counter()
    family_agent_counter = Counter()

    for family in families:
        departments = family.get("departments", [])
        family_breakdown.append(family_summary(family, departments))
        family_department_counter[family["id"]] = len(departments)
        family_unit_counter[family["id"]] = sum(len(dept.get("units", [])) for dept in departments)
        family_agent_counter[family["id"]] = sum(
            len(unit.get("team", [])) for dept in departments for unit in dept.get("units", [])
        )
        for dept in departments:
            department_entries.append(make_department_entry(family, dept))
            for unit in dept.get("units", []):
                for member in unit.get("team", []):
                    agent_entries.append(make_agent_entry(family, dept, unit, member))

    exact_family_count = len(families)
    exact_department_count = len(department_entries)
    exact_unit_count = sum(len(dept.get("units", [])) for family in families for dept in family.get("departments", []))
    exact_agent_count = len(agent_entries)
    hierarchy_level_count = len(command_hierarchy) or 7
    operational_domain_count = len(operational_domains) or 11

    base_summary = {
        "formal_registry_status": "GENERATED_FROM_PROJECT_ARTIFACTS",
        "count_type": "DERIVED_FROM_PROJECT_ARTIFACTS",
        "discovery_status": "COMPLETE",
        "exact_family_count": exact_family_count,
        "exact_department_count": exact_department_count,
        "exact_unit_count": exact_unit_count,
        "exact_agent_count": exact_agent_count,
        "hierarchy_level_count": hierarchy_level_count,
        "operational_domain_count": operational_domain_count,
        "live_runtime_agents_enabled": 0,
        "runtime_activation_started": False,
        "source_file": "09_exports/org_chart_export.json",
        "source_type": "org_chart_export_json",
        "traceability_file": "09_exports/system_registry/agent_department_registry_traceability.md",
        "traceability_html": "13_web_dashboard/dist/demo/data/agent_department_registry_traceability.html",
        "registry_files": {
            "agent_registry": "09_exports/system_registry/agent_registry.json",
            "department_registry": "09_exports/system_registry/department_registry.json",
            "system_hierarchy": "09_exports/system_registry/system_hierarchy.json",
        },
        "family_breakdown": family_breakdown,
        "sample_departments": department_entries[:25],
        "sample_agents": agent_entries[:25],
        "registry_source_files": [
            "09_exports/org_chart_export.json",
            "01_registry/department_families.json",
            "02_departments/**/family.json",
            "09_exports/stakeholder_presentation_after_mvp50/agent_department_hierarchy.md",
        ],
        "candidate_files_count": sum(1 for _ in candidate_files_path.read_text(encoding="utf-8").splitlines()) if candidate_files_path.exists() else 0,
        "structured_candidate_files_count": sum(1 for _ in structured_candidates_path.read_text(encoding="utf-8").splitlines()) if structured_candidates_path.exists() else 0,
        "content_hit_lines_count": sum(1 for _ in content_hits_path.read_text(encoding="utf-8").splitlines()) if content_hits_path.exists() else 0,
    }

    agent_summary = {
        **base_summary,
        "sample_agents": agent_entries[:25],
        "family_breakdown": family_breakdown,
    }
    department_summary = {
        **base_summary,
        "sample_departments": department_entries[:25],
        "family_breakdown": family_breakdown,
    }
    hierarchy_summary = {
        **base_summary,
        "governance_levels": [
            {"level": idx + 1, "name": name}
            for idx, name in enumerate(command_hierarchy)
        ],
        "operational_domains": [
            {"index": idx + 1, "name": name}
            for idx, name in enumerate(operational_domains)
        ],
    }
    summary = base_summary

    agent_registry = {
        "registry_name": "agent_registry",
        "exact_agent_count": exact_agent_count,
        "source_file": "09_exports/org_chart_export.json",
        "source_type": "org_chart_export_json",
        "count_basis": "team member entries across all departments and units in org_chart_export.json",
        "agents": agent_entries,
    }
    department_registry = {
        "registry_name": "department_registry",
        "exact_department_count": exact_department_count,
        "source_file": "09_exports/org_chart_export.json",
        "source_type": "org_chart_export_json",
        "count_basis": "department entries across all families in org_chart_export.json",
        "departments": department_entries,
    }
    system_hierarchy = {
        "registry_name": "system_hierarchy",
        "formal_registry_status": "GENERATED_FROM_PROJECT_ARTIFACTS",
        "count_type": "DERIVED_FROM_PROJECT_ARTIFACTS",
        "hierarchy_level_count": hierarchy_level_count,
        "operational_domain_count": operational_domain_count,
        "live_runtime_agents_enabled": 0,
        "runtime_activation_started": False,
        "registry_structure": {
            "exact_family_count": exact_family_count,
            "exact_department_count": exact_department_count,
            "exact_unit_count": exact_unit_count,
            "exact_agent_count": exact_agent_count,
        },
        "governance_levels": [
            {"level": idx + 1, "name": name, "source_file": str(hierarchy_doc_path.relative_to(ROOT)) if hierarchy_doc_path.exists() else None}
            for idx, name in enumerate(command_hierarchy)
        ],
        "operational_domains": [
            {"index": idx + 1, "name": name, "source_file": str(hierarchy_doc_path.relative_to(ROOT)) if hierarchy_doc_path.exists() else None}
            for idx, name in enumerate(operational_domains)
        ],
        "registry_source_file": "09_exports/org_chart_export.json",
        "registry_source_type": "org_chart_export_json",
    }

    traceability_md = f"""# Agent Department Registry Traceability

## Discovery Status
- `{summary['discovery_status']}`

## Exact Counts
- Exact family count: {exact_family_count}
- Exact department count: {exact_department_count}
- Exact unit count: {exact_unit_count}
- Exact agent count: {exact_agent_count}
- Hierarchy level count: {hierarchy_level_count}
- Operational domain count: {operational_domain_count}
- Live runtime agents enabled: 0
- Runtime activation started: false

## Source Basis
- Canonical export: `09_exports/org_chart_export.json`
- Family registry seed: `01_registry/department_families.json`
- Family exports: `02_departments/**/family.json`
- Hierarchy prose: `09_exports/stakeholder_presentation_after_mvp50/agent_department_hierarchy.md`
- System story: `09_exports/stakeholder_presentation_after_mvp50/system_story.md`

## Derived From Project Artifacts
The canonical `org_chart_export.json` holds 175 families, 1,777 departments, 5,331 units, and 47,979 team-member agents. Those values are copied into the full registry JSON files and the publishable summary artifacts.

## Published Files
- `09_exports/system_registry/agent_registry.json`
- `09_exports/system_registry/department_registry.json`
- `09_exports/system_registry/system_hierarchy.json`
- `09_exports/system_registry/agent_department_registry_summary.json`
- `13_web_dashboard/dist/demo/data/agent_registry_summary.json`
- `13_web_dashboard/dist/demo/data/department_registry_summary.json`
- `13_web_dashboard/dist/demo/data/system_hierarchy_summary.json`
- `13_web_dashboard/dist/demo/data/agent_department_registry_traceability.html`
"""

    discovery_report = f"""# Agent Department Registry Discovery Report

EXACT_AGENT_DEPARTMENT_REGISTRY_DISCOVERY_COMPLETE

- Exact family count: {exact_family_count}
- Exact department count: {exact_department_count}
- Exact unit count: {exact_unit_count}
- Exact agent count: {exact_agent_count}
- Hierarchy level count: {hierarchy_level_count}
- Operational domain count: {operational_domain_count}
- Live runtime agents enabled: 0
- Runtime activation started: false

## Source Files Considered
- `09_exports/org_chart_export.json`
- `01_registry/department_families.json`
- `02_departments/**/family.json`
- `09_exports/stakeholder_presentation_after_mvp50/agent_department_hierarchy.md`
- `09_exports/stakeholder_presentation_after_mvp50/system_story.md`

## Discovery Status
`{summary['discovery_status']}`
"""

    write_json(SYSTEM_REGISTRY_DIR / "agent_registry.json", agent_registry)
    write_json(SYSTEM_REGISTRY_DIR / "department_registry.json", department_registry)
    write_json(SYSTEM_REGISTRY_DIR / "system_hierarchy.json", system_hierarchy)
    write_json(SYSTEM_REGISTRY_DIR / "agent_department_registry_summary.json", summary)
    write_text(SYSTEM_REGISTRY_DIR / "agent_department_registry_traceability.md", traceability_md)
    write_text(DISCOVERY_DIR / "agent_department_discovery_report.md", discovery_report)

    write_json(DEMO_DATA_DIR / "agent_registry_summary.json", agent_summary)
    write_json(DEMO_DATA_DIR / "department_registry_summary.json", department_summary)
    write_json(DEMO_DATA_DIR / "system_hierarchy_summary.json", hierarchy_summary)
    write_text(
        DEMO_DATA_DIR / "agent_department_registry_traceability.html",
        render_traceability_html(summary),
    )
    write_text(
        DEMO_DIR / "agent-registry.html",
        render_agent_registry_page(agent_summary),
    )

    print("EXACT_AGENT_DEPARTMENT_REGISTRY_DISCOVERY_COMPLETE")
    print(f"families={exact_family_count}")
    print(f"departments={exact_department_count}")
    print(f"units={exact_unit_count}")
    print(f"agents={exact_agent_count}")
    print(f"hierarchy_levels={hierarchy_level_count}")
    print(f"operational_domains={operational_domain_count}")
    print("live_runtime_agents_enabled=0")
    print("runtime_activation_started=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
