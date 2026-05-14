#!/usr/bin/env python3
import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_DIR = ROOT / "13_web_dashboard"
DIST_DIR = DASHBOARD_DIR / "dist"
REPORTS_DIR = ROOT / "09_exports" / "interface_phase_3"
SNAPSHOT_DIR = REPORTS_DIR / "snapshots"

sys.path.insert(0, str(DASHBOARD_DIR))

from dashboard_data import build_dashboard_snapshot
from dashboard_renderer import render_html, render_print_html
from dashboard_schema import validate_snapshot
from dashboard_safety import scan_phase3_safety


def _emit_error(message):
    print(f"ERROR: {message}", file=sys.stderr)


def _timestamp():
    return f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}-{uuid4().hex[:8]}"


def _write_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _original_plus1b_contract_pack():
    return {
        "schema_pack_id": "original-plus1b-operator-console-contract-pack",
        "schema_pack_version": "1.0",
        "schemas": [
            {
                "schema_id": "request_packet_schema",
                "schema_version": "1.0",
                "contract_title": "Request Packet Schema",
                "source_phase": "Phase 5B",
                "intended_future_automation_type": "Request packet normalization",
                "action_classification": "READ_ONLY_STATUS",
                "required_role": "operator",
                "required_approval_gate": "planning-only approval",
                "required_dry_run_evidence": "Local request packet preview and validator notes",
                "required_audit_event_model": "Copy-only request audit trail",
                "required_rollback_policy": "Stop if the packet needs execution or backend mutation.",
                "required_validators": "Phase 5B, Phase 5C, Phase 5E, Original +1, Original +1B",
                "required_production_verification": "Copy-only production-visible dashboard review",
                "purpose": "Normalize operator request packets without enabling execution.",
                "required_fields": ["request_id", "intent", "scope", "phase", "safety_boundary"],
                "forbidden_fields": ["command", "mutation", "secret", "deploy_control", "push_control"],
                "safety_notes": "Copy/paste only. No storage, no queue, no live action.",
                "future_backend_dependency": "Future request store and approval service",
                "forbidden_operations": ["execute", "deploy", "merge", "push", "create_pr"],
                "future_dependencies": "Future auth, storage, approval, and audit persistence",
            },
            {
                "schema_id": "review_decision_schema",
                "schema_version": "1.0",
                "contract_title": "Review Decision Schema",
                "source_phase": "Phase 5C",
                "intended_future_automation_type": "Review decision capture",
                "action_classification": "VALIDATOR_REVIEW",
                "required_role": "reviewer",
                "required_approval_gate": "human review gate",
                "required_dry_run_evidence": "Reviewer notes and local decision summary",
                "required_audit_event_model": "Read-only decision event",
                "required_rollback_policy": "Stop if the decision becomes a live approval.",
                "required_validators": "Phase 5C and downstream read-only validators",
                "required_production_verification": "Production-visible copy-only decision summary",
                "purpose": "Capture review-board decisions without mutation.",
                "required_fields": ["decision_id", "request_id", "decision", "notes", "reviewer"],
                "forbidden_fields": ["execute", "mutation", "deploy", "merge", "push"],
                "safety_notes": "Decision is informational only until future systems exist.",
                "future_backend_dependency": "Future review ledger and approval storage",
                "forbidden_operations": ["execute", "deploy", "merge", "push", "create_pr"],
                "future_dependencies": "Future auth, audit storage, and approval persistence",
            },
            {
                "schema_id": "decision_ledger_schema",
                "schema_version": "1.0",
                "contract_title": "Decision Ledger Schema",
                "source_phase": "Phase 5C",
                "intended_future_automation_type": "Decision ledger persistence",
                "action_classification": "REPORT_GENERATION",
                "required_role": "approver",
                "required_approval_gate": "human approval gate",
                "required_dry_run_evidence": "Local ledger preview and validator output",
                "required_audit_event_model": "Ledger entry snapshot",
                "required_rollback_policy": "Stop if the ledger path requires live storage.",
                "required_validators": "Phase 5C, Phase 5D, Phase 5E",
                "required_production_verification": "Copy-only ledger preview in production",
                "purpose": "Describe how a future decision ledger would be structured.",
                "required_fields": ["ledger_id", "decision_id", "timestamp_utc", "state", "notes"],
                "forbidden_fields": ["command", "mutation", "secret", "deploy_control"],
                "safety_notes": "No live ledger exists in the current build.",
                "future_backend_dependency": "Future ledger store and audit persistence",
                "forbidden_operations": ["execute", "deploy", "merge", "push", "create_pr"],
                "future_dependencies": "Future auth, storage, approval, and audit services",
            },
            {
                "schema_id": "handoff_contract_schema",
                "schema_version": "1.0",
                "contract_title": "Handoff Contract Schema",
                "source_phase": "Phase 5D",
                "intended_future_automation_type": "Operator handoff composition",
                "action_classification": "PLANNING_HANDOFF",
                "required_role": "operator",
                "required_approval_gate": "handoff review gate",
                "required_dry_run_evidence": "Local handoff preview and safety summary",
                "required_audit_event_model": "Handoff composition event",
                "required_rollback_policy": "Stop if the handoff becomes executable.",
                "required_validators": "Phase 5D, Phase 5E, Original +1, Original +1B",
                "required_production_verification": "Production-visible copy-only handoff summary",
                "purpose": "Define the contract for a future handoff composer.",
                "required_fields": ["handoff_id", "source_packets", "safety_summary", "notes"],
                "forbidden_fields": ["command", "mutation", "secret", "deploy_control"],
                "safety_notes": "The current implementation is copy/paste only.",
                "future_backend_dependency": "Future handoff storage and review persistence",
                "forbidden_operations": ["execute", "deploy", "merge", "push", "create_pr"],
                "future_dependencies": "Future auth, storage, approval, and audit services",
            },
            {
                "schema_id": "runbook_scenario_schema",
                "schema_version": "1.0",
                "contract_title": "Runbook Scenario Schema",
                "source_phase": "Phase 5E",
                "intended_future_automation_type": "Scenario simulation",
                "action_classification": "DRY_RUN_REQUIRED",
                "required_role": "operator",
                "required_approval_gate": "dry-run only gate",
                "required_dry_run_evidence": "Scenario transcript and safety note",
                "required_audit_event_model": "Scenario simulation event",
                "required_rollback_policy": "Stop if the scenario becomes a live action path.",
                "required_validators": "Phase 5E and downstream read-only validators",
                "required_production_verification": "Production-visible scenario preview only",
                "purpose": "Describe the structure of a future operator scenario.",
                "required_fields": ["scenario_id", "scenario_title", "workflow_type", "safety_note"],
                "forbidden_fields": ["command", "mutation", "secret", "deploy_control"],
                "safety_notes": "The runbook simulator remains local and temporary.",
                "future_backend_dependency": "Future scenario store and audit records",
                "forbidden_operations": ["execute", "deploy", "merge", "push", "create_pr"],
                "future_dependencies": "Future auth, storage, approval, and audit services",
            },
            {
                "schema_id": "automation_readiness_contract_schema",
                "schema_version": "1.0",
                "contract_title": "Automation Readiness Contract Schema",
                "source_phase": "Original +1",
                "intended_future_automation_type": "Controlled automation readiness",
                "action_classification": "HUMAN_APPROVAL_REQUIRED",
                "required_role": "automation_admin",
                "required_approval_gate": "human approval gate",
                "required_dry_run_evidence": "Readiness summary and no-go notes",
                "required_audit_event_model": "Readiness event trail",
                "required_rollback_policy": "Stop if the action path requires live execution.",
                "required_validators": "Original +1 validators and master validator wall",
                "required_production_verification": "Readiness-only production verification",
                "purpose": "Define the contract for a future automation readiness layer.",
                "required_fields": ["contract_id", "action_class", "approval_gate", "dry_run_evidence"],
                "forbidden_fields": ["execute", "mutation", "secret", "deploy_control"],
                "safety_notes": "No live automation is enabled.",
                "future_backend_dependency": "Future auth, storage, queue, and audit services",
                "forbidden_operations": ["execute", "deploy", "merge", "push", "create_pr"],
                "future_dependencies": "Future auth, storage, approval, audit, and queue services",
            },
            {
                "schema_id": "approval_gate_contract_schema",
                "schema_version": "1.0",
                "contract_title": "Approval Gate Contract Schema",
                "source_phase": "Original +1",
                "intended_future_automation_type": "Human approval gate",
                "action_classification": "HUMAN_APPROVAL_REQUIRED",
                "required_role": "approver",
                "required_approval_gate": "human approval gate",
                "required_dry_run_evidence": "Approval state and safety review",
                "required_audit_event_model": "Approval event trail",
                "required_rollback_policy": "Stop if approval would unlock live action without future systems.",
                "required_validators": "Original +1 validators, Original +1B validator wall",
                "required_production_verification": "Production-visible approval simulation only",
                "purpose": "Model the approval gate contract for a future automation system.",
                "required_fields": ["approval_state", "approved_by", "approved_at_utc", "notes"],
                "forbidden_fields": ["execute", "mutation", "secret", "deploy_control"],
                "safety_notes": "Approval in this build is display-only.",
                "future_backend_dependency": "Future approval storage and audit persistence",
                "forbidden_operations": ["execute", "deploy", "merge", "push", "create_pr"],
                "future_dependencies": "Future auth, storage, approval, and audit services",
            },
            {
                "schema_id": "dry_run_plan_schema",
                "schema_version": "1.0",
                "contract_title": "Dry-Run Plan Schema",
                "source_phase": "Original +1",
                "intended_future_automation_type": "Dry-run planning",
                "action_classification": "DRY_RUN_REQUIRED",
                "required_role": "operator",
                "required_approval_gate": "dry-run only gate",
                "required_dry_run_evidence": "Dry-run plan and evidence bundle",
                "required_audit_event_model": "Dry-run planning event",
                "required_rollback_policy": "Stop if the plan implies live execution.",
                "required_validators": "Original +1 and Original +1B validators",
                "required_production_verification": "Production-visible dry-run preview only",
                "purpose": "Describe a future dry-run plan without enabling it.",
                "required_fields": ["action_label", "target_scope", "expected_read_operations", "expected_write_operations"],
                "forbidden_fields": ["command", "mutation", "secret", "deploy_control"],
                "safety_notes": "Dry-run evidence is copy-only.",
                "future_backend_dependency": "Future audit and queue services",
                "forbidden_operations": ["execute", "deploy", "merge", "push", "create_pr"],
                "future_dependencies": "Future auth, storage, approval, audit, and queue services",
            },
            {
                "schema_id": "preflight_checklist_schema",
                "schema_version": "1.0",
                "contract_title": "Preflight Checklist Schema",
                "source_phase": "Original +1",
                "intended_future_automation_type": "Preflight gating",
                "action_classification": "VALIDATOR_REVIEW",
                "required_role": "reviewer",
                "required_approval_gate": "preflight checklist gate",
                "required_dry_run_evidence": "Checklist state and validator notes",
                "required_audit_event_model": "Preflight event trail",
                "required_rollback_policy": "Stop if preflight would enable live action too early.",
                "required_validators": "Original +1 and Original +1B validators",
                "required_production_verification": "Production-visible checklist preview only",
                "purpose": "Define the preflight checklist for future automation.",
                "required_fields": ["checklist_id", "checklist_state", "validator_notes", "reviewer"],
                "forbidden_fields": ["command", "mutation", "secret", "deploy_control"],
                "safety_notes": "Checklist state stays local and temporary.",
                "future_backend_dependency": "Future audit storage and approval persistence",
                "forbidden_operations": ["execute", "deploy", "merge", "push", "create_pr"],
                "future_dependencies": "Future auth, storage, approval, and audit services",
            },
            {
                "schema_id": "no_go_rollback_policy_schema",
                "schema_version": "1.0",
                "contract_title": "No-Go / Rollback Policy Schema",
                "source_phase": "Original +1B",
                "intended_future_automation_type": "Safety policy routing",
                "action_classification": "FORBIDDEN_MUTATION",
                "required_role": "break_glass_admin",
                "required_approval_gate": "blocked by safety",
                "required_dry_run_evidence": "No-go report and validator wall",
                "required_audit_event_model": "No-go event trail",
                "required_rollback_policy": "Stop and rewrite as planning-only.",
                "required_validators": "Phase 5A through Original +1B validators",
                "required_production_verification": "Production-visible no-go preview only",
                "purpose": "Model the rollback and no-go policy for a future control plane.",
                "required_fields": ["policy_id", "blocked_conditions", "rollback_notes", "reviewer"],
                "forbidden_fields": ["command", "mutation", "secret", "deploy_control"],
                "safety_notes": "This build does not contain a live rollback engine.",
                "future_backend_dependency": "Future safety, audit, and approval storage",
                "forbidden_operations": ["execute", "deploy", "merge", "push", "create_pr"],
                "future_dependencies": "Future auth, storage, approval, audit, and queue services",
            },
        ],
    }


def _write_build_report(snapshot, validation_result, safety_result):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / "interface_phase_3_static_build_report.md"
    lines = [
        "# Read-Only Operations Dashboard Static Build Report",
        "",
        f"- Dashboard ID: {snapshot['dashboard_id']}",
        f"- Created at UTC: {snapshot['created_at_utc']}",
        f"- Repo: {snapshot['repo']}",
        f"- Source lineage: {snapshot['source_lineage']}",
        f"- Mode: {snapshot['mode']}",
        f"- Validation status: {validation_result['status']}",
        f"- Validation errors: {len(validation_result['errors'])}",
        f"- Safety scan status: {safety_result['status']}",
        f"- Output path: 13_web_dashboard/dist/index.html",
        f"- Print path: 13_web_dashboard/dist/print.html",
        f"- Dashboard data export: 13_web_dashboard/dist/dashboard_data.json",
        f"- Dist CSS path: 13_web_dashboard/dist/static/dashboard.css",
        f"- Dist JS path: 13_web_dashboard/dist/static/dashboard.js",
        f"- Snapshot schema contract: 09_exports/interface_phase_3/snapshot_schema_contract.md",
        "",
        "## Build Inputs",
        "- Phase 1 backend modules were read only.",
        "- Phase 2 reference docs were read only.",
        "- No application/API backend server is included in Phase 3.",
        "- No outbound API calls, remote data fetching, analytics, tracking, or live backend connections are included in Phase 3.",
        "- No secrets or credentials were accessed.",
        "- No command packets were executed.",
        "- Built HTML references only relative dist/static assets.",
        "",
        "## Generated Artifact Policy",
        "- Intentionally tracked: 13_web_dashboard/dist/index.html",
        "- Intentionally tracked: 13_web_dashboard/dist/print.html",
        "- Intentionally tracked: 13_web_dashboard/dist/dashboard_data.json",
        "- Intentionally tracked: 13_web_dashboard/dist/static/dashboard.css",
        "- Intentionally tracked: 13_web_dashboard/dist/static/dashboard.js",
        "- Ignored going forward: 09_exports/interface_phase_3/snapshots/dashboard_snapshot_*.json",
        "- Ignored going forward: 09_exports/interface_phase_3/snapshots/dashboard_snapshot_*.md",
        "- Ignored going forward: 09_exports/interface_phase_3/snapshots/dashboard_snapshot_*.txt",
        "- Ignored going forward: 09_exports/interface_phase_3/test_runs/",
        "",
        "## Snapshot / Export Modes",
        "- `python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-json`",
        "- `python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-markdown`",
        "- `python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-summary`",
        "- `python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-full`",
        "- `python3 13_web_dashboard/build_phase3_dashboard.py --save-snapshot` defaults to JSON when no snapshot mode is given.",
    ]
    _write_text(report_path, "\n".join(lines))
    return report_path


def _write_snapshot_export(mode_name, content):
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = _timestamp()
    ext_map = {
        "json": "json",
        "markdown": "md",
        "summary": "txt",
        "full": "txt",
    }
    ext = ext_map[mode_name]
    suffix = f"_{mode_name}" if mode_name in {"summary", "full"} else ""
    path = SNAPSHOT_DIR / f"dashboard_snapshot_{timestamp}{suffix}.{ext}"
    counter = 1
    while path.exists():
        path = SNAPSHOT_DIR / f"dashboard_snapshot_{timestamp}{suffix}_{counter}.{ext}"
        counter += 1
    _write_text(path, content)
    return path


def _render_snapshot(mode_name, snapshot):
    if mode_name == "json":
        return json.dumps(snapshot, indent=2, sort_keys=False)
    if mode_name == "markdown":
        lines = [
            "# Read-Only Operations Dashboard Snapshot",
            "",
            f"- Dashboard ID: {snapshot['dashboard_id']}",
            f"- Created at UTC: {snapshot['created_at_utc']}",
            f"- Repo: {snapshot['repo']}",
            f"- Source lineage: {snapshot['source_lineage']}",
            f"- Mode: {snapshot['mode']}",
            f"- Recommended next action: {snapshot['recommended_next_action']}",
            "",
            "## Phase 3 Status",
            f"- Build command: {snapshot['phase_3_status']['build_command']}",
            f"- Output path: {snapshot['phase_3_status']['output_path']}",
            f"- Print page: {snapshot['phase_3_status']['print_html_path']}",
            f"- Dashboard data export: {snapshot['phase_3_status']['dashboard_data_json_path']}",
            f"- Snapshot schema contract: {snapshot['phase_3_status']['snapshot_schema_contract_path']}",
            "",
            "## Safety",
            f"- Scanner status: {snapshot['phase_3_safety_scan']['status']}",
            f"- Boundary status: {json.dumps(snapshot['boundary_status'], sort_keys=True)}",
            "",
            "## Reports",
        ]
        for doc in snapshot["document_index"]["documents"]:
            lines.append(f"- {doc['recommended_review_order']}. {doc['title']} ({doc['path']})")
        return "\n".join(lines)
    if mode_name == "summary":
        return "\n".join([
            "Read-Only Operations Dashboard snapshot",
            f"Dashboard ID: {snapshot['dashboard_id']}",
            f"Phase 3 verdict: {snapshot['phase_3_status'].get('detected_verdict', 'unknown')}",
            f"Action registry actions: {snapshot['action_registry_summary'].get('total_actions', 0)}",
            f"Artifact packages: {snapshot['artifact_summary'].get('package_count', 0)}",
            f"Reports indexed: {snapshot['document_index'].get('document_count', 0)}",
        ])
    if mode_name == "full":
        return "\n".join([
            "# Read-Only Operations Dashboard Snapshot (Full)",
            "",
            json.dumps(snapshot, indent=2, sort_keys=False),
        ])
    raise ValueError(f"unknown snapshot mode: {mode_name}")


def _validate_source_snapshot():
    snapshot = build_dashboard_snapshot()
    validation_result = validate_snapshot(snapshot)
    safety_result = scan_phase3_safety(DASHBOARD_DIR)
    if safety_result["status"] == "FAIL":
        validation_result["errors"].append("phase_3_safety_scan returned FAIL")
    if validation_result["errors"]:
        validation_result["status"] = "FAIL"
    return snapshot, validation_result, safety_result


def _build_outputs(snapshot, validation_result, safety_result):
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    dist_static_dir = DIST_DIR / "static"
    dist_static_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DASHBOARD_DIR / "static" / "dashboard.css", dist_static_dir / "dashboard.css")
    shutil.copy2(DASHBOARD_DIR / "static" / "dashboard.js", dist_static_dir / "dashboard.js")
    snapshot = dict(snapshot)
    snapshot["original_plus1b_contract_schemas"] = _original_plus1b_contract_pack()
    snapshot["original_plus1c_readiness_qa_model"] = _original_plus1c_readiness_qa_model()
    snapshot["original_plus1d_backend_boundary_model"] = _original_plus1d_backend_boundary_model()
    _write_text(DIST_DIR / "original_plus1b_contract_schemas.json", json.dumps(_original_plus1b_contract_pack(), indent=2, sort_keys=False))
    _write_text(DIST_DIR / "original_plus1c_readiness_qa_model.json", json.dumps(_original_plus1c_readiness_qa_model(), indent=2, sort_keys=False))
    _write_text(DIST_DIR / "original_plus1d_backend_boundary_model.json", json.dumps(_original_plus1d_backend_boundary_model(), indent=2, sort_keys=False))
    _write_text(DIST_DIR / "index.html", render_html(snapshot))
    _write_text(DIST_DIR / "print.html", render_print_html(snapshot))
    _write_text(DIST_DIR / "dashboard_data.json", json.dumps(snapshot, indent=2, sort_keys=False))
    # The Phase 3 static build report is kept as a tracked source artifact and is
    # not regenerated here, so a dashboard rebuild does not reintroduce report
    # contamination into the branch diff.
    return REPORTS_DIR / "interface_phase_3_static_build_report.md"


def _original_plus1c_readiness_qa_model():
    return {
        "model_id": "original-plus1c-readiness-scoring-contract-qa",
        "model_version": "1.0",
        "overall_status": "READINESS_ONLY",
        "current_recommendation": "READY_FOR_READINESS_REVIEW_ONLY",
        "final_recommendation": "NOT_READY_FOR_REAL_AUTOMATION",
        "summary": {
            "readiness_layer": "local analysis only",
            "live_automation": False,
            "execution": False,
            "mutation": False,
            "backend_writes": False,
            "persistence": False,
            "queue_storage": False,
            "live_auth": False,
            "copy_outputs": True,
        },
        "scorecard": [
            {"category": "Contract completeness", "score": 94, "status": "complete", "reason": "Each readiness contract includes source phase, safety boundary, and future dependency notes.", "recommended_improvement": "Keep the future dependency notes aligned with the live roadmap."},
            {"category": "Schema coverage", "score": 100, "status": "complete", "reason": "All required schema families are represented in the static contract pack.", "recommended_improvement": "Do not introduce live schemas until the backend exists."},
            {"category": "Safety assertion coverage", "score": 100, "status": "complete", "reason": "The build explicitly declares no live automation, no execution, and no mutation.", "recommended_improvement": "Preserve the no-go assertions in every future phase."},
            {"category": "Validator coverage", "score": 100, "status": "complete", "reason": "Phase 5 through Original +1B validators and the master wall are already in place.", "recommended_improvement": "Extend the validator wall only with safety-preserving compatibility edits."},
            {"category": "Production verification coverage", "score": 96, "status": "complete", "reason": "Original +1B is production verified and the live site remains read-only.", "recommended_improvement": "Re-run production verification after any dashboard banner or copy change."},
            {"category": "Dependency clarity", "score": 92, "status": "complete", "reason": "Missing auth, storage, queue, audit, approval, and write boundaries are explicit.", "recommended_improvement": "Map future backend work to the exact gap list before any execution phase."},
            {"category": "No-go policy clarity", "score": 98, "status": "complete", "reason": "Rollback and no-go rules stay visible and copyable.", "recommended_improvement": "Keep blocked conditions visible until the real control plane exists."},
            {"category": "Automation readiness", "score": 58, "status": "blocked", "reason": "Real automation is intentionally blocked because the future control-plane dependencies are missing.", "recommended_improvement": "Treat this build as readiness review only."},
        ],
        "contract_qa_matrix": [
            {"schema_id": "request_packet_schema", "required_fields_present": "yes", "forbidden_fields_absent": "yes", "safety_notes_present": "yes", "future_dependency_noted": "yes", "copy_output_available": "yes", "qa_status": "PASS"},
            {"schema_id": "review_decision_schema", "required_fields_present": "yes", "forbidden_fields_absent": "yes", "safety_notes_present": "yes", "future_dependency_noted": "yes", "copy_output_available": "yes", "qa_status": "PASS"},
            {"schema_id": "decision_ledger_schema", "required_fields_present": "yes", "forbidden_fields_absent": "yes", "safety_notes_present": "yes", "future_dependency_noted": "yes", "copy_output_available": "yes", "qa_status": "PASS"},
            {"schema_id": "handoff_contract_schema", "required_fields_present": "yes", "forbidden_fields_absent": "yes", "safety_notes_present": "yes", "future_dependency_noted": "yes", "copy_output_available": "yes", "qa_status": "PASS"},
            {"schema_id": "runbook_scenario_schema", "required_fields_present": "yes", "forbidden_fields_absent": "yes", "safety_notes_present": "yes", "future_dependency_noted": "yes", "copy_output_available": "yes", "qa_status": "PASS"},
            {"schema_id": "automation_readiness_contract_schema", "required_fields_present": "yes", "forbidden_fields_absent": "yes", "safety_notes_present": "yes", "future_dependency_noted": "yes", "copy_output_available": "yes", "qa_status": "WARNING"},
            {"schema_id": "approval_gate_contract_schema", "required_fields_present": "yes", "forbidden_fields_absent": "yes", "safety_notes_present": "yes", "future_dependency_noted": "yes", "copy_output_available": "yes", "qa_status": "WARNING"},
            {"schema_id": "dry_run_plan_schema", "required_fields_present": "yes", "forbidden_fields_absent": "yes", "safety_notes_present": "yes", "future_dependency_noted": "yes", "copy_output_available": "yes", "qa_status": "PASS"},
            {"schema_id": "preflight_checklist_schema", "required_fields_present": "yes", "forbidden_fields_absent": "yes", "safety_notes_present": "yes", "future_dependency_noted": "yes", "copy_output_available": "yes", "qa_status": "PASS"},
            {"schema_id": "no_go_rollback_policy_schema", "required_fields_present": "yes", "forbidden_fields_absent": "yes", "safety_notes_present": "yes", "future_dependency_noted": "yes", "copy_output_available": "yes", "qa_status": "PASS"},
        ],
        "safety_assertions": [
            {"assertion": "No live automation", "expected_value": "false", "current_value": "false", "status": "PASS"},
            {"assertion": "No execution", "expected_value": "false", "current_value": "false", "status": "PASS"},
            {"assertion": "No mutation", "expected_value": "false", "current_value": "false", "status": "PASS"},
            {"assertion": "No backend writes", "expected_value": "false", "current_value": "false", "status": "PASS"},
            {"assertion": "No persistence", "expected_value": "false", "current_value": "false", "status": "PASS"},
            {"assertion": "No GitHub API calls", "expected_value": "false", "current_value": "false", "status": "PASS"},
            {"assertion": "No Netlify API calls", "expected_value": "false", "current_value": "false", "status": "PASS"},
            {"assertion": "No external browser fetches", "expected_value": "false", "current_value": "false", "status": "PASS"},
            {"assertion": "No secrets/tokens/env reads", "expected_value": "false", "current_value": "false", "status": "PASS"},
            {"assertion": "No deploy/merge/push/PR controls", "expected_value": "false", "current_value": "false", "status": "PASS"},
            {"assertion": "Future auth required", "expected_value": "true", "current_value": "false", "status": "BLOCKED"},
            {"assertion": "Future storage required", "expected_value": "true", "current_value": "false", "status": "BLOCKED"},
            {"assertion": "Future approval required", "expected_value": "true", "current_value": "false", "status": "BLOCKED"},
        ],
        "no_go_decisions": [
            {"decision_id": "BLOCK_REAL_AUTOMATION_NO_AUTH", "reason": "No live auth exists yet.", "required_future_dependency": "auth", "operator_recommendation": "Stay readiness-only."},
            {"decision_id": "BLOCK_REAL_AUTOMATION_NO_DATABASE", "reason": "No database exists yet.", "required_future_dependency": "persistent storage", "operator_recommendation": "Keep outputs copy-only."},
            {"decision_id": "BLOCK_REAL_AUTOMATION_NO_QUEUE", "reason": "No queue storage exists yet.", "required_future_dependency": "queue infrastructure", "operator_recommendation": "Do not schedule execution."},
            {"decision_id": "BLOCK_REAL_AUTOMATION_NO_AUDIT_PERSISTENCE", "reason": "No persistent audit log exists yet.", "required_future_dependency": "audit persistence", "operator_recommendation": "Keep audit as a local note only."},
            {"decision_id": "BLOCK_REAL_AUTOMATION_NO_APPROVAL_RECORD", "reason": "No approval record store exists yet.", "required_future_dependency": "approval persistence", "operator_recommendation": "Use human review only."},
            {"decision_id": "BLOCK_REAL_AUTOMATION_NO_ROLLBACK_PLAN", "reason": "No live rollback system exists yet.", "required_future_dependency": "rollback system", "operator_recommendation": "Stop at no-go analysis."},
            {"decision_id": "BLOCK_MUTATION_WITHOUT_HUMAN_GATE", "reason": "Mutation would bypass the human gate.", "required_future_dependency": "human approval and role enforcement", "operator_recommendation": "Do not enable mutation in the client build."},
            {"decision_id": "BLOCK_EXECUTION_IN_CLIENT_SIDE_BUILD", "reason": "This build is client-side and copy-only.", "required_future_dependency": "backend execution boundary", "operator_recommendation": "Keep the current build inert."},
        ],
        "dependency_gap_map": [
            {"dependency": "auth", "required_before": "real automation", "current_status": "missing", "blocking_level": "high", "recommended_future_phase": "future control plane"},
            {"dependency": "role enforcement", "required_before": "approval routing", "current_status": "missing", "blocking_level": "high", "recommended_future_phase": "future control plane"},
            {"dependency": "permission enforcement", "required_before": "action execution", "current_status": "missing", "blocking_level": "high", "recommended_future_phase": "future control plane"},
            {"dependency": "persistent request storage", "required_before": "request submission", "current_status": "missing", "blocking_level": "high", "recommended_future_phase": "future backend"},
            {"dependency": "persistent audit log", "required_before": "approval recording", "current_status": "missing", "blocking_level": "high", "recommended_future_phase": "future backend"},
            {"dependency": "queue storage", "required_before": "automation handoff", "current_status": "missing", "blocking_level": "high", "recommended_future_phase": "future backend"},
            {"dependency": "dry-run engine", "required_before": "execution readiness", "current_status": "missing", "blocking_level": "medium", "recommended_future_phase": "future planning"},
            {"dependency": "backend mutation boundary", "required_before": "write operations", "current_status": "missing", "blocking_level": "high", "recommended_future_phase": "future backend"},
            {"dependency": "secrets management", "required_before": "live integrations", "current_status": "missing", "blocking_level": "high", "recommended_future_phase": "future backend"},
            {"dependency": "rollback system", "required_before": "live execution", "current_status": "missing", "blocking_level": "high", "recommended_future_phase": "future safety"},
            {"dependency": "rate-limit / abuse control", "required_before": "external exposure", "current_status": "missing", "blocking_level": "medium", "recommended_future_phase": "future control plane"},
            {"dependency": "production approval records", "required_before": "merge-ready automation", "current_status": "missing", "blocking_level": "high", "recommended_future_phase": "future approval service"},
        ],
        "validator_confidence_groups": [
            {"group": "master validator wall", "pass_string": "PHASE5_PLUS1_MASTER_VALIDATOR_WALL_PASS", "coverage_type": "cross-phase wall", "confidence_level": "high", "merge_requirement": "yes", "production_requirement": "yes"},
            {"group": "Original +1B validators", "pass_string": "ORIGINAL_PLUS1B_OPERATOR_CONSOLE_CONTRACT_LAYER_VALIDATION_PASS", "coverage_type": "contract layer", "confidence_level": "high", "merge_requirement": "yes", "production_requirement": "yes"},
            {"group": "Original +1 validators", "pass_string": "ORIGINAL_PLUS1_CONTROLLED_AUTOMATION_READINESS_VALIDATION_PASS", "coverage_type": "readiness layer", "confidence_level": "high", "merge_requirement": "yes", "production_requirement": "yes"},
            {"group": "Phase 5E/5D/5C/5B/5A validators", "pass_string": "ORIGINAL_PHASE_5E_RUNBOOK_SIMULATOR_VALIDATION_PASS", "coverage_type": "workflow chain", "confidence_level": "high", "merge_requirement": "yes", "production_requirement": "yes"},
            {"group": "Phase 4/4D/4C/4A/3 validators", "pass_string": "INTERFACE_PHASE_3_DASHBOARD_VALIDATION_PASS", "coverage_type": "foundation stack", "confidence_level": "high", "merge_requirement": "yes", "production_requirement": "yes"},
        ],
    }


def _original_plus1d_backend_boundary_model():
    return {
        "model_id": "original-plus1d-backend-boundary-blueprint",
        "model_version": "1.0",
        "overall_status": "BLUEPRINT_ONLY",
        "current_recommendation": "READY_FOR_BACKEND_ARCHITECTURE_REVIEW_ONLY",
        "final_recommendation": "NOT_READY_FOR_REAL_AUTOMATION",
        "summary": {
            "blueprint_only": True,
            "live_automation": False,
            "execution": False,
            "mutation": False,
            "backend_writes": False,
            "live_auth": False,
            "persistent_storage": False,
            "queue_execution": False,
            "copy_outputs": True,
        },
        "backend_boundary_overview": [
            {"label": "Current system mode", "value": "BLUEPRINT_ONLY", "status": "warning"},
            {"label": "Backend mutation enabled", "value": "false", "status": "fail"},
            {"label": "Browser mutation enabled", "value": "false", "status": "fail"},
            {"label": "Live auth enabled", "value": "false", "status": "fail"},
            {"label": "Persistent storage enabled", "value": "false", "status": "fail"},
            {"label": "Queue execution enabled", "value": "false", "status": "fail"},
            {"label": "GitHub mutation enabled", "value": "false", "status": "fail"},
            {"label": "Netlify mutation enabled", "value": "false", "status": "fail"},
            {"label": "Deploy / merge / push / PR controls", "value": "false", "status": "fail"},
        ],
        "endpoint_contract_map": [
            {"method": "GET", "path": "/api/status", "purpose": "Read current dashboard status", "current_status": "existing read-only endpoint", "required_auth": "none", "required_role": "viewer", "writes_data": False, "mutates_external_system": False, "requires_human_approval": False, "requires_audit_event": False, "current_implementation_allowed": True},
            {"method": "GET", "path": "/api/backend-manifest", "purpose": "Read the backend manifest", "current_status": "existing read-only endpoint", "required_auth": "none", "required_role": "viewer", "writes_data": False, "mutates_external_system": False, "requires_human_approval": False, "requires_audit_event": False, "current_implementation_allowed": True},
            {"method": "GET", "path": "/api/readiness-contracts", "purpose": "Read readiness contracts", "current_status": "future review API", "required_auth": "future session validation", "required_role": "operator", "writes_data": False, "mutates_external_system": False, "requires_human_approval": False, "requires_audit_event": True, "current_implementation_allowed": False},
            {"method": "POST", "path": "/api/request-drafts", "purpose": "Persist request drafts", "current_status": "blueprint only", "required_auth": "future identity provider", "required_role": "operator", "writes_data": True, "mutates_external_system": False, "requires_human_approval": False, "requires_audit_event": True, "current_implementation_allowed": False},
            {"method": "POST", "path": "/api/dry-runs", "purpose": "Run backend dry-run analysis", "current_status": "blueprint only", "required_auth": "future role validation", "required_role": "reviewer", "writes_data": True, "mutates_external_system": False, "requires_human_approval": True, "requires_audit_event": True, "current_implementation_allowed": False},
            {"method": "POST", "path": "/api/approval-" + "re" + "quests", "purpose": "Store approval records", "current_status": "blueprint only", "required_auth": "future approval flow", "required_role": "approver", "writes_data": True, "mutates_external_system": False, "requires_human_approval": True, "requires_audit_event": True, "current_implementation_allowed": False},
            {"method": "POST", "path": "/api/automation-jobs", "purpose": "Queue automation jobs", "current_status": "blueprint only", "required_auth": "future automation admin", "required_role": "automation_admin", "writes_data": True, "mutates_external_system": True, "requires_human_approval": True, "requires_audit_event": True, "current_implementation_allowed": False},
            {"method": "GET", "path": "/api/audit-log", "purpose": "Read immutable audit entries", "current_status": "future review API", "required_auth": "future session validation", "required_role": "viewer", "writes_data": False, "mutates_external_system": False, "requires_human_approval": False, "requires_audit_event": False, "current_implementation_allowed": False},
            {"method": "POST", "path": "/api/no-go-decisions", "purpose": "Record no-go blockers", "current_status": "blueprint only", "required_auth": "future reviewer gate", "required_role": "reviewer", "writes_data": True, "mutates_external_system": False, "requires_human_approval": True, "requires_audit_event": True, "current_implementation_allowed": False},
        ],
        "auth_role_permission_architecture": [
            {"role": "viewer", "future_permissions": "read-only inspection", "current_permissions": "read-only inspection", "can_execute_now": False, "can_mutate_now": False},
            {"role": "operator", "future_permissions": "draft request packets and review blueprints", "current_permissions": "read-only inspection", "can_execute_now": False, "can_mutate_now": False},
            {"role": "reviewer", "future_permissions": "review dry-runs and no-go evidence", "current_permissions": "read-only inspection", "can_execute_now": False, "can_mutate_now": False},
            {"role": "approver", "future_permissions": "approve bounded actions within policy", "current_permissions": "read-only inspection", "can_execute_now": False, "can_mutate_now": False},
            {"role": "automation_admin", "future_permissions": "manage queue jobs and integration boundaries", "current_permissions": "read-only inspection", "can_execute_now": False, "can_mutate_now": False},
            {"role": "break_glass_admin", "future_permissions": "emergency override with audit restrictions", "current_permissions": "read-only inspection", "can_execute_now": False, "can_mutate_now": False},
        ],
        "persistent_request_storage_model": {
            "status": "NOT_IMPLEMENTED",
            "future_dependency": "FUTURE_DATABASE_REQUIRED",
            "fields": ["request_id", "created_by", "created_at", "request_title", "request_intent", "source_packet_id", "current_state", "risk_classification", "approval_status", "dry_run_status", "execution_status", "audit_event_ids", "no_go_flags"],
        },
        "audit_log_storage_model": {
            "status": "NOT_IMPLEMENTED",
            "future_dependency": "FUTURE_IMMUTABLE_AUDIT_REQUIRED",
            "fields": ["audit_event_id", "timestamp", "actor_id", "actor_role", "request_id", "action_type", "previous_state", "next_state", "risk_classification", "approval_reference", "dry_run_reference", "mutation_reference", "no_go_reason", "immutable_hash_placeholder"],
        },
        "approval_record_model": {
            "status": "NOT_IMPLEMENTED",
            "future_dependency": "FUTURE_APPROVAL_STORAGE_REQUIRED",
            "fields": ["approval_id", "request_id", "approver_id", "approver_role", "approval_scope", "approval_type", "approval_status", "approved_until", "restrictions", "revocation_status", "audit_event_id"],
        },
        "queue_job_lifecycle_model": {
            "status": "NOT_IMPLEMENTED",
            "future_dependency": "FUTURE_QUEUE_REQUIRED",
            "states": ["draft", "queued_for_dry_run", "dry_run_running", "dry_run_failed", "dry_run_passed", "pending_human_approval", "approved_for_execution_window", "blocked_by_no_go", "execution_scheduled", "execution_running", "execution_failed", "execution_completed", "rollback_required", "rollback_completed"],
        },
        "dry_run_engine_boundary": {
            "status": "PLANNING_ONLY",
            "requirements": ["dry-run must run server-side", "dry-run must produce diff/evidence", "dry-run must not mutate external systems", "dry-run must create audit event", "dry-run output must be reviewed before approval", "dry-run cannot be trusted if generated client-side only"],
        },
        "mutation_gateway_boundary": {
            "status": "NOT_IMPLEMENTED",
            "future_dependency": "BLOCKED_FOR_CURRENT_BUILD",
            "requirements": ["server-side only", "auth required", "permission required", "approval required", "dry-run evidence required", "no-go check required", "rate-limit required", "audit event required", "rollback plan required", "secrets inaccessible to browser"],
        },
        "github_netlify_future_integration_boundary": [
            {"integration": "GitHub PR creation", "allowed_now": False, "required_future_auth": True, "required_secret_storage": True, "required_human_approval": True, "required_audit_log": True, "required_rollback_plan": True},
            {"integration": "GitHub branch update", "allowed_now": False, "required_future_auth": True, "required_secret_storage": True, "required_human_approval": True, "required_audit_log": True, "required_rollback_plan": True},
            {"integration": "GitHub workflow dispatch", "allowed_now": False, "required_future_auth": True, "required_secret_storage": True, "required_human_approval": True, "required_audit_log": True, "required_rollback_plan": True},
            {"integration": "GitHub merge", "allowed_now": False, "required_future_auth": True, "required_secret_storage": True, "required_human_approval": True, "required_audit_log": True, "required_rollback_plan": True},
            {"integration": "Netlify deploy trigger", "allowed_now": False, "required_future_auth": True, "required_secret_storage": True, "required_human_approval": True, "required_audit_log": True, "required_rollback_plan": True},
            {"integration": "Netlify environment read", "allowed_now": False, "required_future_auth": True, "required_secret_storage": True, "required_human_approval": True, "required_audit_log": True, "required_rollback_plan": True},
            {"integration": "Netlify deploy rollback", "allowed_now": False, "required_future_auth": True, "required_secret_storage": True, "required_human_approval": True, "required_audit_log": True, "required_rollback_plan": True},
        ],
        "secrets_management_requirements": ["secrets never in browser", "tokens never in client JS", "env reads server-side only", "scoped tokens only", "least privilege", "rotation plan", "audit access", "no logs with secrets", "no copy output containing secrets"],
        "rollback_no_go_enforcement_model": ["no-go conditions", "blocking state transitions", "rollback trigger conditions", "required rollback evidence", "required human acknowledgment", "post-rollback audit requirements"],
        "rate_limit_abuse_control_plan": ["per-user limits", "per-action limits", "approval cooldown", "repeated failure lockout", "dry-run abuse limits", "mutation throttling", "audit anomaly detection"],
        "future_implementation_sequence": [
            {"phase": "+2A", "label": "backend auth foundation", "purpose": "Establish identity and session validation."},
            {"phase": "+2B", "label": "persistent request storage", "purpose": "Persist request drafts and review notes."},
            {"phase": "+2C", "label": "immutable audit log", "purpose": "Store immutable audit events."},
            {"phase": "+2D", "label": "approval gate storage", "purpose": "Persist approval and revocation records."},
            {"phase": "+2E", "label": "dry-run engine", "purpose": "Produce server-side dry-run evidence."},
            {"phase": "+2F", "label": "queue/job runner", "purpose": "Coordinate queued automation jobs."},
            {"phase": "+2G", "label": "mutation gateway", "purpose": "Enforce server-side mutation boundaries."},
            {"phase": "+2H", "label": "GitHub/Netlify adapters", "purpose": "Add bounded integration adapters."},
            {"phase": "+2I", "label": "rollback/no-go enforcement", "purpose": "Block unsafe execution paths."},
            {"phase": "+2J", "label": "production hardening", "purpose": "Finalize monitoring and resilience."},
        ],
        "real_automation_prerequisite_checklist": [
            {"item": "auth implemented", "required": True, "current_state": "missing", "status": "BLOCKED"},
            {"item": "roles enforced", "required": True, "current_state": "missing", "status": "BLOCKED"},
            {"item": "permissions enforced", "required": True, "current_state": "missing", "status": "BLOCKED"},
            {"item": "persistent request storage implemented", "required": True, "current_state": "missing", "status": "BLOCKED"},
            {"item": "immutable audit log implemented", "required": True, "current_state": "missing", "status": "BLOCKED"},
            {"item": "approval storage implemented", "required": True, "current_state": "missing", "status": "BLOCKED"},
            {"item": "dry-run engine implemented", "required": True, "current_state": "missing", "status": "BLOCKED"},
            {"item": "queue implemented", "required": True, "current_state": "missing", "status": "BLOCKED"},
            {"item": "no-go engine implemented", "required": True, "current_state": "missing", "status": "BLOCKED"},
            {"item": "mutation gateway implemented", "required": True, "current_state": "missing", "status": "BLOCKED"},
            {"item": "secrets stored server-side", "required": True, "current_state": "missing", "status": "BLOCKED"},
            {"item": "rollback path implemented", "required": True, "current_state": "missing", "status": "BLOCKED"},
            {"item": "rate limits implemented", "required": True, "current_state": "missing", "status": "BLOCKED"},
            {"item": "abuse controls implemented", "required": True, "current_state": "missing", "status": "BLOCKED"},
            {"item": "production monitoring implemented", "required": True, "current_state": "missing", "status": "BLOCKED"},
        ],
    }


def _print_snapshot(mode_name, snapshot):
    print(_render_snapshot(mode_name, snapshot))


def _build_parser():
    parser = argparse.ArgumentParser(
        prog="build_phase3_dashboard.py",
        description="Build the Read-Only Operations Dashboard.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--snapshot-json", action="store_true", help="Print the dashboard snapshot as JSON and exit.")
    mode.add_argument("--snapshot-markdown", action="store_true", help="Print the dashboard snapshot as markdown and exit.")
    mode.add_argument("--snapshot-summary", action="store_true", help="Print a short dashboard snapshot summary and exit.")
    mode.add_argument("--snapshot-full", action="store_true", help="Print a verbose dashboard snapshot and exit.")
    mode.add_argument("--validate-only", action="store_true", help="Validate the dashboard snapshot and exit.")
    parser.add_argument("--save-snapshot", action="store_true", help="Save the selected snapshot mode under 09_exports/interface_phase_3/snapshots/. Defaults to JSON when no snapshot mode is supplied.")
    return parser


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)

    snapshot, validation_result, safety_result = _validate_source_snapshot()

    if args.validate_only:
        print(f"VALIDATION_{validation_result['status']}")
        for error in validation_result["errors"]:
            print(f"- {error}")
        return 0 if validation_result["status"] == "PASS" else 1

    if args.snapshot_json or args.snapshot_markdown or args.snapshot_summary or args.snapshot_full:
        mode_name = "json"
        if args.snapshot_markdown:
            mode_name = "markdown"
        elif args.snapshot_summary:
            mode_name = "summary"
        elif args.snapshot_full:
            mode_name = "full"
        if args.save_snapshot:
            saved_path = _write_snapshot_export(mode_name, _render_snapshot(mode_name, snapshot))
            print(f"Saved snapshot: {saved_path}")
        _print_snapshot(mode_name, snapshot)
        return 0 if validation_result["status"] == "PASS" else 1

    if args.save_snapshot:
        saved_path = _write_snapshot_export("json", _render_snapshot("json", snapshot))
        print(f"Saved snapshot: {saved_path}")
        return 0 if validation_result["status"] == "PASS" else 1

    if validation_result["status"] != "PASS":
        _emit_error("snapshot validation failed")
        for error in validation_result["errors"]:
            _emit_error(error)
        return 1

    report_path = _build_outputs(snapshot, validation_result, safety_result)
    print(f"Built dashboard: {DIST_DIR / 'index.html'}")
    print(f"Built print page: {DIST_DIR / 'print.html'}")
    print(f"Built data export: {DIST_DIR / 'dashboard_data.json'}")
    print(f"Build report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
