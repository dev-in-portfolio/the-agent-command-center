# Read-Only Operations Dashboard Map

| Dashboard section | Backend source | Safety category | Writes files? | Executes commands? | Uses network? | Notes |
|---|---|---|---|---|---|---|
| Header | `dashboard_data.py` | Info | No | No | No | Repo, lineage, timestamp, mode |
| Sticky safety banner | `dashboard_renderer.py` / `dashboard_schema.py` | Locked | No | No | No | Large visible boundary banner |
| Visual status summary | `dashboard_data.py` | Info | No | No | No | Top summary strip |
| Overview cards | `dashboard_data.py` | Info | No | No | No | Phase 1, Phase 2, Phase 3, safety, next action |
| Safety boundary panel | `dashboard_schema.py` | Locked/disabled | No | No | No | All required locked values |
| Action registry panel | `11_interface/interface_action_registry.py` + `11_interface/interface_policy_enforcer.py` | Controlled/locked | No | No | No | Read-only action summary |
| Artifact deep-dive panel | `11_interface/interface_artifact_inspector.py` | Safe/read-only | No | No | No | Package counts, warnings, missing files |
| Reports Library panel | Phase 1, Phase 2, Phase 3 reports | Read-only | No | No | No | Relative links and previews |
| Validator Command Center | `scripts/validate_interface_phase_*.py` references | Read-only | No | No | No | Command references only |
| Data Freshness / Source Transparency | `dashboard_data.py` | Read-only | No | No | No | Source paths and confidence labels |
| Compare Phases panel | `dashboard_data.py` | Read-only | No | No | No | Phase 1/2/3 capability comparison |
| Branch Review panel | `11_interface/interface_branch_review.py` | Controlled/read-only | No | No | No | Review packet summary only |
| Approval Ledger panel | `11_interface/interface_approval_ledger.py` | Controlled/read-only | No | No | No | Ledger inspection only |
| Session / Audit panel | `11_interface/interface_session_log.py` + export files | Read-only | No | No | No | Session path summary and build report reference |
| Footer | `dashboard_renderer.py` | Info | No | No | No | Local static file notice |
