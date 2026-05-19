# Agent Department Registry Traceability

## Discovery Status
- `COMPLETE`

## Exact Counts
- Exact family count: 175
- Exact department count: 1777
- Exact unit count: 5331
- Exact agent count: 47979
- Hierarchy level count: 7
- Operational domain count: 11
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
