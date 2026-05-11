# Station Chief v25 General Operator Runtime Command Menu

Welcome to the Station Chief v25 Open-Gate Command Layer. The core command center is complete and ready to accept job tickets.

## Supported Task Types
- `repo_integrity_inspection`: Perform a read-only integrity check of the repository.
- `operational_workpack`: Execute standard agent operational workpacks.
- `local_artifact_factory`: Generate local documents, CSVs, and manifests.
- `business_workflow_packet`: Execute business-logic-aligned workpacks.
- `external_tool_gateway_probe`: Perform approved metadata-only HTTPS probes.
- `external_evidence_snapshot`: Perform approved external content fetches and digests.
- `capability_status_report`: Generate a report of all installed and executable capabilities.

## Job Ticket Examples
- "Perform a repo integrity check"
- "Generate a project brief in the local artifact factory"
- "Snapshot example.com content for external evidence"
- "What can the system do now?"

## Approval Requirement
All executable tasks require the exact approval phrase:
`I_APPROVE_V25_OPEN_GATE_GENERAL_OPERATOR_RUNTIME`

## Safety Boundaries
- **Repo Mutation:** DISABLED.
- **Credential Access:** DISABLED.
- **Production Mutation:** DISABLED.
- **Uncontrolled Autonomy:** DISABLED.

## Lab Repositories and Self-Improvement Modes
The Station Chief ecosystem includes specialized labs for autonomous evolution within protected boundaries.

- **Official repo:** `dev-in-portfolio/agent-command-center`
  - **Purpose:** Operator-approved lineage only.
- **Lab repo 1:** `dev-in-portfolio/agent-command-center-2`
  - **Identity:** `auto-self-improve-1`
  - **Mode:** Propose/evaluate/rank/archive/recommend only.
  - **Constraints:** Cannot self-authorize, self-mutate, or self-promote.
- **Lab repo 2:** `dev-in-portfolio/agent-command-center-3`
  - **Identity:** `auto-self-improve-2`
  - **Mode:** Contained sandbox self-improvement.
  - **Constraints:** Can self-authorize sandbox metadata/mutations only. Cannot touch official repo, repo 2, deploy, use secrets, or self-promote.

## Safe Lab Run Examples
To trigger a sandbox improvement hunt in the active lab:
```bash
cd agent-command-center-3
python3 scripts/validate_station_chief_runtime_v25_0.py
python3 scripts/validate_auto_self_improve_2.py
```
- Sandbox artifacts live under `/tmp/auto_self_improve_2_sandbox/`.
- Official promotion requires explicit future operator approval.
- Sandbox success is NOT official promotion.

## Core Status
**DONE-DONE RELEASE**
Core command center is operationally complete. Future work is adapter/plugin expansion.
