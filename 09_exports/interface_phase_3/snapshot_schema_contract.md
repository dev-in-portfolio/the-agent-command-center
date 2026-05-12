# Read-Only Operations Dashboard Snapshot Schema Contract

Required JSON schema fields:

```json
{
  "dashboard_id": "...",
  "created_at_utc": "...",
  "phase": "Read-Only Operations Dashboard",
  "repo": "dev-in-portfolio/the-agent-command-center",
  "source_lineage": "dev-in-portfolio/agent-command-center-3",
  "mode": "static_local_dashboard",
  "phase_1_status": {},
  "phase_2_status": {},
  "phase_3_status": {},
  "safety_status": {},
  "boundary_status": {},
  "action_registry_summary": {},
  "artifact_summary": {},
  "approval_ledger_summary": {},
  "branch_review_summary": {},
  "session_summary": {},
  "validator_status": {},
  "document_index": {},
  "data_freshness": {},
  "source_transparency": {},
  "recommended_next_action": "..."
}
```

Required exact values:

- `phase == Read-Only Operations Dashboard`
- `repo == dev-in-portfolio/the-agent-command-center`
- `source_lineage == dev-in-portfolio/agent-command-center-3`
- `mode == static_local_dashboard`

Required boundary booleans:

- `official_repo_touched: false`
- `repo_2_touched: false`
- `repo_3_touched: false`
- `deployment_performed: false`
- `secrets_credentials_used: false`
- `command_packets_executed: false`
- `merge_performed: false`
- `push_performed: false`
- `pr_created: false`
- `network_used: false`

Required section metadata fields:

- `source_file_path`
- `source_exists`
- `source_type`
- `source_confidence`

Required source confidence labels:

- `direct_module_read`
- `report_derived`
- `file_existence_check`
- `generated_static_snapshot`
- `unknown`

Validator expectations:

- JSON snapshot parses
- Required root fields exist
- Boundary booleans are false
- `document_index.documents` exists
- `data_freshness` exists
- `source_transparency.sections` exists
- Snapshot is static hosting ready and read-only
