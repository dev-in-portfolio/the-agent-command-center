# System Scale Inventory

| Category | Count | Count Type | Source / Method |
|---|---:|---|---|
| MVP readiness layers completed | 8 | DERIVED_FROM_MANIFEST | `presentation_manifest.json` readiness layers |
| Production verification reports | 67 | DERIVED_FROM_FILE_COUNT | `find 09_exports -type f -name '*production_verification_report.md'` |
| MVP product-track files | 582 | DERIVED_FROM_FILE_COUNT | `find 09_exports/mvp_product_track -type f` |
| Release package artifacts | 177 | DERIVED_FROM_FILE_COUNT | `find 09_exports/release_package -type f` |
| UI model JSON files | 226 | DERIVED_FROM_FILE_COUNT | `find 14_backend/product_runtime/ui_models -type f` |
| Validator scripts | 280 | DERIVED_FROM_FILE_COUNT | `find scripts -maxdepth 1 -type f -name 'validate_*.py'` |
| Dashboard static artifacts | 70 | DERIVED_FROM_FILE_COUNT | `find 13_web_dashboard/dist -type f` |
| Demo package files | 16 | DERIVED_FROM_MANIFEST | `demo_package_manifest.json` |
| Stakeholder presentation files | 19 | DERIVED_FROM_MANIFEST | `presentation_manifest.json` |
| Viewable demo hub pages | 11 | DERIVED_FROM_FILE_COUNT | planned HTML pages under `13_web_dashboard/dist/demo/` |
| Safety boundary markers | 13 | DERIVED_FROM_MANIFEST | `demo_package_manifest.json` safety boundaries |
| Disabled capability categories | 13 | DERIVED_FROM_MANIFEST | `presentation_manifest.json` disabled capabilities |
| Operational domains | 11 | DERIVED_FROM_DOC | documented hierarchy domains in `agent_department_hierarchy.md` |
| Exact family count | 175 | DERIVED_FROM_PROJECT_ARTIFACTS | `09_exports/org_chart_export.json` |
| Exact department count | 1,777 | DERIVED_FROM_PROJECT_ARTIFACTS | `09_exports/org_chart_export.json` |
| Exact unit count | 5,331 | DERIVED_FROM_PROJECT_ARTIFACTS | `09_exports/org_chart_export.json` |
| Exact agent count | 47,979 | DERIVED_FROM_PROJECT_ARTIFACTS | `09_exports/org_chart_export.json` |
| Hierarchy levels | 7 | DERIVED_FROM_DOC | documented hierarchy levels in `agent_department_hierarchy.md` |
| Action registry items | 12 | DERIVED_FROM_DASHBOARD_DATA | `13_web_dashboard/dist/dashboard_data.json` |

## Recommended Next Documentation Improvement
The canonical registry has now been generated into `09_exports/system_registry/agent_registry.json`, `09_exports/system_registry/department_registry.json`, and `09_exports/system_registry/system_hierarchy.json`.

The publishable traceability view lives at `13_web_dashboard/dist/demo/agent-registry.html` and `13_web_dashboard/dist/demo/data/agent_department_registry_traceability.html`.
