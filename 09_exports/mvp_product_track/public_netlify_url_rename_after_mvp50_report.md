# Public Netlify URL Rename After MVP50 Report

PUBLIC_NETLIFY_URL_RENAME_AFTER_MVP50_COMPLETE
OLD_PUBLIC_URL_REPLACED
NEW_PUBLIC_URL_APPLIED
STATIC_SITE_URL_REFERENCES_UPDATED
DEMO_URL_REFERENCES_UPDATED
VALIDATOR_URL_REFERENCES_UPDATED
REPORT_URL_REFERENCES_UPDATED
LEGAL_URL_REFERENCES_UPDATED
NETLIFY_RENAME_ATTEMPTED_OR_MANUAL_REQUIRED
NO_ENDPOINTS_ADDED
NO_NETLIFY_FUNCTIONS_ADDED
NO_DATABASE_WRITES_ADDED
NO_SUPABASE_WRITES_ADDED
NO_COMMAND_EXECUTION_ADDED
NO_ACTION_EXECUTION_ADDED
NO_AUTOMATION_ADDED
NO_MVP51_STARTED

## URLs
- Old URL: `https://the-agent-command-center-dashboard.netlify.app`
- New URL: `https://the-agent-command-center.netlify.app`

## Netlify CLI
- CLI installed: yes
- CLI authenticated: not confirmed
- Site rename performed: no
- Manual Netlify rename required: yes

## Validation
- `PUBLIC_NETLIFY_URL_RENAME_AFTER_MVP50_VALIDATION_PASS`
- `LIVE_DASHBOARD_DYNAMIC_LATEST_STATUS_VALIDATION_PASS`
- `MVP50_MONITORING_ROLLBACK_INCIDENT_CONSOLE_VALIDATION_PASS`
- `PHASE5_PLUS1_MASTER_VALIDATOR_WALL_PASS`
- `SITEWIDE_COPYRIGHT_LEGAL_LAYER_AFTER_MVP50_VALIDATION_PASS`
- `GLOBAL_DEMO_OVERFLOW_CONTAINMENT_AFTER_MVP50_VALIDATION_PASS`
- `GLOBAL_DEMO_COLLAPSIBLE_MENU_BREADCRUMBS_AFTER_MVP50_VALIDATION_PASS`

## Changed Files
- `13_web_dashboard/build_phase4c_status_snapshot.py`
- `13_web_dashboard/dist/demo/demo-package.json`
- `13_web_dashboard/dist/status_snapshot.json`
- `scripts/validate_original_phase_4_hosted_dashboard_e2e.py`
- `scripts/validate_public_netlify_url_rename_after_mvp50.py`
- Public-facing docs and reports under `09_exports/backend_phase_4/`, `09_exports/external_demo_package/`, `09_exports/external_demo_package_after_mvp50/`, `09_exports/interface_phase_4/`, `09_exports/interface_phase_5/`, `09_exports/mvp_product_track/`, `09_exports/original_plus1/`, `09_exports/original_plus2/`, and `09_exports/stakeholder_presentation_after_mvp50/`

## Notes
- The backend/runtime and Netlify function surfaces were intentionally left out of scope.
- The old host remains only in excluded backend/runtime files that were not part of the public rename surface.
