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
| Exact agent count | UNKNOWN_NOT_CURRENTLY_DECLARED | UNKNOWN_NOT_CURRENTLY_DECLARED | No canonical agent registry exists in the repo |
| Exact department count | UNKNOWN_NOT_CURRENTLY_DECLARED | UNKNOWN_NOT_CURRENTLY_DECLARED | No canonical department registry exists in the repo |
| Hierarchy levels | 7 | DERIVED_FROM_DOC | documented hierarchy levels in `agent_department_hierarchy.md` |
| Action registry items | 12 | DERIVED_FROM_DASHBOARD_DATA | `13_web_dashboard/dist/dashboard_data.json` |

## Recommended Next Documentation Improvement
Create a canonical `agent_registry.json` and `department_registry.json` so future demos can state exact operating-unit counts.

Create a canonical `system_hierarchy.json` so future demos can distinguish levels, domains, and verification gates without relying on prose alone.
