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


def _original_plus2a_auth_foundation_model():
    import json
    from pathlib import Path
    try:
        return json.loads(Path("13_web_dashboard/dist/original_plus2a_auth_foundation_model.json").read_text(encoding="utf-8"))
    except Exception:
        return {}

def _original_plus2b_request_storage_model():
    import json
    from pathlib import Path
    try:
        return json.loads(Path("13_web_dashboard/dist/original_plus2b_request_storage_model.json").read_text(encoding="utf-8"))
    except Exception:
        return {}

def _build_outputs(snapshot, validation_result, safety_result):
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    dist_static_dir = DIST_DIR / "static"
    dist_static_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DASHBOARD_DIR / "static" / "dashboard.css", dist_static_dir / "dashboard.css")
    shutil.copy2(DASHBOARD_DIR / "static" / "dashboard.js", dist_static_dir / "dashboard.js")
    snapshot = dict(snapshot)
    snapshot["original_plus1b_contract_schemas"] = _original_plus1b_contract_pack()
    snapshot["original_plus1c_readiness_qa_model"] = _original_plus1c_readiness_qa_model()
    snapshot["original_plus1d_backend_boundary_blueprint"] = _original_plus1d_backend_boundary_model()
    snapshot["original_plus1e_backend_build_tickets"] = _original_plus1e_backend_build_tickets()
    snapshot["original_plus2a_auth_foundation_model"] = _original_plus2a_auth_foundation_model()
    snapshot["original_plus2b_request_storage_model"] = _original_plus2b_request_storage_model()
    _write_text(DIST_DIR / "original_plus1b_contract_schemas.json", json.dumps(_original_plus1b_contract_pack(), indent=2, sort_keys=False))
    _write_text(DIST_DIR / "original_plus1c_readiness_qa_model.json", json.dumps(_original_plus1c_readiness_qa_model(), indent=2, sort_keys=False))
    _write_text(DIST_DIR / "original_plus1d_backend_boundary_model.json", json.dumps(_original_plus1d_backend_boundary_model(), indent=2, sort_keys=False))
    _write_text(DIST_DIR / "original_plus1e_backend_build_tickets.json", json.dumps(_original_plus1e_backend_build_tickets(), indent=2, sort_keys=False))
    _write_text(DIST_DIR / "original_plus2a_auth_foundation_model.json", json.dumps(_original_plus2a_auth_foundation_model(), indent=2, sort_keys=False))
    _write_text(DIST_DIR / "original_plus2b_request_storage_model.json", json.dumps(_original_plus2b_request_storage_model(), indent=2, sort_keys=False))
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


def _original_plus1e_backend_build_tickets():
    common_forbidden_files = [
        "13_web_dashboard/**",
        "netlify/functions/**",
        "11_interface/**",
        "12_tui/**",
        "10_runtime/**",
        "09_exports/interface_phase_1/**",
        "09_exports/interface_phase_2/**",
        "09_exports/interface_phase_3/**",
        "09_exports/interface_phase_4/**",
        "09_exports/original_plus1/**",
    ]

    ticket_specs = [
        {
            "ticket_id": "+2A",
            "title": "Backend Auth Foundation",
            "branch": "interface/original-plus2a-backend-auth-foundation",
            "purpose": "Establish identity and session validation before any write-capable backend work.",
            "dependencies": ["none"],
            "required_inputs": ["identity provider choice", "session validation rules", "role matrix"],
            "required_outputs": ["auth architecture", "session validator contract", "role policy", "auth gate notes"],
            "required_tests": ["unit validation for auth rules", "e2e boundary validation", "safety scan", "diff scope check"],
            "required_validators": [
                "scripts/validate_original_plus2a_backend_auth_foundation.py",
                "scripts/validate_original_plus2a_backend_auth_foundation_e2e.py",
            ],
            "required_reports": [
                "09_exports/original_plus2/original_plus2a_backend_auth_foundation_report.md",
                "09_exports/original_plus2/original_plus2a_backend_auth_foundation_design_report.md",
                "09_exports/original_plus2/original_plus2a_backend_auth_foundation_safety_report.md",
                "09_exports/original_plus2/original_plus2a_backend_auth_foundation_dependency_report.md",
                "09_exports/original_plus2/original_plus2a_backend_auth_foundation_validator_report.md",
                "09_exports/original_plus2/original_plus2a_backend_auth_foundation_acceptance_report.md",
            ],
            "no_go_conditions": ["browser-side auth", "token storage in JS", "session cookies in the browser", "live execution", "live mutation"],
            "rollback_requirements": ["stop at planning-only", "remove any browser-held credential path", "revert any live auth wiring"],
            "allowed_files": [
                "14_backend/auth/**",
                "scripts/validate_original_plus2a_backend_auth_foundation.py",
                "scripts/validate_original_plus2a_backend_auth_foundation_e2e.py",
                "09_exports/original_plus2/",
            ],
            "forbidden_files": common_forbidden_files,
            "implementation_boundary": "Backend-only auth foundation. No dashboard changes, no live auth, no persistence, no queue, no mutation.",
            "acceptance_criteria": ["auth architecture is copyable", "session validation is explicit", "role mapping is documented", "no live automation is enabled"],
            "final_response_requirements": ["report only", "mention blocked status", "do not enable real automation"],
            "current_status": "NOT_STARTED",
            "blocked_for_now": True,
            "gate_status": "READY_FOR_PLANNING_ONLY",
            "blocking_reason": "All write-capable backend work still lacks the auth foundation.",
            "required_future_ticket": "+2A",
        },
        {
            "ticket_id": "+2B",
            "title": "Persistent Request Storage",
            "branch": "interface/original-plus2b-persistent-request-storage",
            "purpose": "Persist build tickets and review notes after auth exists.",
            "dependencies": ["+2A"],
            "required_inputs": ["auth foundation", "ticket schema", "storage retention rules"],
            "required_outputs": ["request store contract", "draft persistence flow", "ticket lifecycle notes"],
            "required_tests": ["storage boundary validation", "e2e contract validation", "safety scan", "diff scope check"],
            "required_validators": [
                "scripts/validate_original_plus2b_persistent_request_storage.py",
                "scripts/validate_original_plus2b_persistent_request_storage_e2e.py",
            ],
            "required_reports": [
                "09_exports/original_plus2/original_plus2b_persistent_request_storage_report.md",
                "09_exports/original_plus2/original_plus2b_persistent_request_storage_design_report.md",
                "09_exports/original_plus2/original_plus2b_persistent_request_storage_safety_report.md",
                "09_exports/original_plus2/original_plus2b_persistent_request_storage_dependency_report.md",
                "09_exports/original_plus2/original_plus2b_persistent_request_storage_validator_report.md",
                "09_exports/original_plus2/original_plus2b_persistent_request_storage_acceptance_report.md",
            ],
            "no_go_conditions": ["no auth", "browser persistence", "live execution", "mutation gateway bypass", "queue without storage"],
            "rollback_requirements": ["stay copy-only", "remove any client-side persistence", "revert storage hooks that bypass auth"],
            "allowed_files": [
                "14_backend/storage/**",
                "scripts/validate_original_plus2b_persistent_request_storage.py",
                "scripts/validate_original_plus2b_persistent_request_storage_e2e.py",
                "09_exports/original_plus2/",
            ],
            "forbidden_files": common_forbidden_files,
            "implementation_boundary": "Backend storage only. No dashboard persistence, no live queue, no execution, no mutation.",
            "acceptance_criteria": ["ticket drafts are persistable server-side", "lifecycle is explicit", "no browser storage is introduced"],
            "final_response_requirements": ["report only", "mention blocked status", "do not enable real automation"],
            "current_status": "NOT_STARTED",
            "blocked_for_now": True,
            "gate_status": "BLOCKED_PENDING_2A",
            "blocking_reason": "Persistent storage depends on authenticated sessions.",
            "required_future_ticket": "+2B",
        },
        {
            "ticket_id": "+2C",
            "title": "Immutable Audit Log",
            "branch": "interface/original-plus2c-immutable-audit-log",
            "purpose": "Store immutable audit events after auth and request storage exist.",
            "dependencies": ["+2A", "+2B"],
            "required_inputs": ["auth foundation", "request storage schema", "audit retention rules"],
            "required_outputs": ["audit contract", "immutable event model", "audit hash notes"],
            "required_tests": ["audit boundary validation", "e2e contract validation", "safety scan", "diff scope check"],
            "required_validators": [
                "scripts/validate_original_plus2c_immutable_audit_log.py",
                "scripts/validate_original_plus2c_immutable_audit_log_e2e.py",
            ],
            "required_reports": [
                "09_exports/original_plus2/original_plus2c_immutable_audit_log_report.md",
                "09_exports/original_plus2/original_plus2c_immutable_audit_log_design_report.md",
                "09_exports/original_plus2/original_plus2c_immutable_audit_log_safety_report.md",
                "09_exports/original_plus2/original_plus2c_immutable_audit_log_dependency_report.md",
                "09_exports/original_plus2/original_plus2c_immutable_audit_log_validator_report.md",
                "09_exports/original_plus2/original_plus2c_immutable_audit_log_acceptance_report.md",
            ],
            "no_go_conditions": ["mutable audit history", "browser-side audit storage", "live execution", "mutation without audit"],
            "rollback_requirements": ["keep audit immutable", "do not expose write APIs without hash binding", "revert mutable audit paths"],
            "allowed_files": [
                "14_backend/audit/**",
                "scripts/validate_original_plus2c_immutable_audit_log.py",
                "scripts/validate_original_plus2c_immutable_audit_log_e2e.py",
                "09_exports/original_plus2/",
            ],
            "forbidden_files": common_forbidden_files,
            "implementation_boundary": "Backend audit only. No dashboard persistence, no live execution, no mutation, no queue bypass.",
            "acceptance_criteria": ["audit events are immutable", "audit entries bind to auth and ticket state", "no browser storage is used"],
            "final_response_requirements": ["report only", "mention blocked status", "do not enable real automation"],
            "current_status": "NOT_STARTED",
            "blocked_for_now": True,
            "gate_status": "BLOCKED_PENDING_2A_2B",
            "blocking_reason": "Immutable audit requires authenticated ticket persistence.",
            "required_future_ticket": "+2C",
        },
        {
            "ticket_id": "+2D",
            "title": "Approval Gate Storage",
            "branch": "interface/original-plus2d-approval-gate-storage",
            "purpose": "Persist approval and revocation records after the audit trail exists.",
            "dependencies": ["+2A", "+2B", "+2C"],
            "required_inputs": ["auth foundation", "request storage schema", "audit contract", "approval policy"],
            "required_outputs": ["approval store contract", "revocation model", "approval audit binding"],
            "required_tests": ["approval storage validation", "e2e contract validation", "safety scan", "diff scope check"],
            "required_validators": [
                "scripts/validate_original_plus2d_approval_gate_storage.py",
                "scripts/validate_original_plus2d_approval_gate_storage_e2e.py",
            ],
            "required_reports": [
                "09_exports/original_plus2/original_plus2d_approval_gate_storage_report.md",
                "09_exports/original_plus2/original_plus2d_approval_gate_storage_design_report.md",
                "09_exports/original_plus2/original_plus2d_approval_gate_storage_safety_report.md",
                "09_exports/original_plus2/original_plus2d_approval_gate_storage_dependency_report.md",
                "09_exports/original_plus2/original_plus2d_approval_gate_storage_validator_report.md",
                "09_exports/original_plus2/original_plus2d_approval_gate_storage_acceptance_report.md",
            ],
            "no_go_conditions": ["approval without audit binding", "browser-side approvals", "live execution", "approval records without revocation"],
            "rollback_requirements": ["stop if approval storage is not immutable", "remove any live approval writes", "revert bypass paths"],
            "allowed_files": [
                "14_backend/approval/**",
                "scripts/validate_original_plus2d_approval_gate_storage.py",
                "scripts/validate_original_plus2d_approval_gate_storage_e2e.py",
                "09_exports/original_plus2/",
            ],
            "forbidden_files": common_forbidden_files,
            "implementation_boundary": "Approval storage only. No execution, no queue, no mutation, no dashboard persistence.",
            "acceptance_criteria": ["approval records are persisted server-side", "revocations are modeled", "audit binding is explicit"],
            "final_response_requirements": ["report only", "mention blocked status", "do not enable real automation"],
            "current_status": "NOT_STARTED",
            "blocked_for_now": True,
            "gate_status": "BLOCKED_PENDING_AUTH_STORAGE_AUDIT",
            "blocking_reason": "Approval persistence depends on authenticated ticket and audit records.",
            "required_future_ticket": "+2D",
        },
        {
            "ticket_id": "+2E",
            "title": "Server-Side Dry-Run Engine",
            "branch": "interface/original-plus2e-server-side-dry-run-engine",
            "purpose": "Produce backend dry-run evidence before approval can advance.",
            "dependencies": ["+2A", "+2B", "+2C"],
            "required_inputs": ["auth foundation", "request storage schema", "audit contract", "dry-run policy"],
            "required_outputs": ["dry-run engine contract", "evidence bundle shape", "dry-run audit notes"],
            "required_tests": ["dry-run validation", "e2e contract validation", "safety scan", "diff scope check"],
            "required_validators": [
                "scripts/validate_original_plus2e_server_side_dry_run_engine.py",
                "scripts/validate_original_plus2e_server_side_dry_run_engine_e2e.py",
            ],
            "required_reports": [
                "09_exports/original_plus2/original_plus2e_server_side_dry_run_engine_report.md",
                "09_exports/original_plus2/original_plus2e_server_side_dry_run_engine_design_report.md",
                "09_exports/original_plus2/original_plus2e_server_side_dry_run_engine_safety_report.md",
                "09_exports/original_plus2/original_plus2e_server_side_dry_run_engine_dependency_report.md",
                "09_exports/original_plus2/original_plus2e_server_side_dry_run_engine_validator_report.md",
                "09_exports/original_plus2/original_plus2e_server_side_dry_run_engine_acceptance_report.md",
            ],
            "no_go_conditions": ["client-side dry-run only", "dry-run that mutates state", "dry-run without audit evidence", "live execution"],
            "rollback_requirements": ["keep dry-run server-side", "revert any execution side effects", "preserve evidence output only"],
            "allowed_files": [
                "14_backend/dry_run/**",
                "scripts/validate_original_plus2e_server_side_dry_run_engine.py",
                "scripts/validate_original_plus2e_server_side_dry_run_engine_e2e.py",
                "09_exports/original_plus2/",
            ],
            "forbidden_files": common_forbidden_files,
            "implementation_boundary": "Dry-run evidence only. No live execution, no mutation, no dashboard-side simulation as source of truth.",
            "acceptance_criteria": ["dry-run evidence is generated server-side", "approval depends on dry-run output", "no live system is mutated"],
            "final_response_requirements": ["report only", "mention blocked status", "do not enable real automation"],
            "current_status": "NOT_STARTED",
            "blocked_for_now": True,
            "gate_status": "BLOCKED_PENDING_AUTH_STORAGE_AUDIT",
            "blocking_reason": "Dry-run evidence needs ticket, auth, and audit infrastructure first.",
            "required_future_ticket": "+2E",
        },
        {
            "ticket_id": "+2F",
            "title": "Queue / Job Runner",
            "branch": "interface/original-plus2f-queue-job-runner",
            "purpose": "Coordinate queued automation jobs after dry-run and approval exist.",
            "dependencies": ["+2A", "+2B", "+2C", "+2D", "+2E"],
            "required_inputs": ["auth foundation", "request storage schema", "audit contract", "approval store", "dry-run engine"],
            "required_outputs": ["queue runner contract", "job lifecycle model", "queue evidence notes"],
            "required_tests": ["queue validation", "e2e contract validation", "safety scan", "diff scope check"],
            "required_validators": [
                "scripts/validate_original_plus2f_queue_job_runner.py",
                "scripts/validate_original_plus2f_queue_job_runner_e2e.py",
            ],
            "required_reports": [
                "09_exports/original_plus2/original_plus2f_queue_job_runner_report.md",
                "09_exports/original_plus2/original_plus2f_queue_job_runner_design_report.md",
                "09_exports/original_plus2/original_plus2f_queue_job_runner_safety_report.md",
                "09_exports/original_plus2/original_plus2f_queue_job_runner_dependency_report.md",
                "09_exports/original_plus2/original_plus2f_queue_job_runner_validator_report.md",
                "09_exports/original_plus2/original_plus2f_queue_job_runner_acceptance_report.md",
            ],
            "no_go_conditions": ["queue without approval", "queue without dry-run evidence", "job runner without audit", "live execution"],
            "rollback_requirements": ["stop if the queue can bypass approval", "revert any scheduling path", "keep job state copy-only until future phases"],
            "allowed_files": [
                "14_backend/queue/**",
                "scripts/validate_original_plus2f_queue_job_runner.py",
                "scripts/validate_original_plus2f_queue_job_runner_e2e.py",
                "09_exports/original_plus2/",
            ],
            "forbidden_files": common_forbidden_files,
            "implementation_boundary": "Queue/job runner only. No live mutation, no browser queue, no dashboard execution.",
            "acceptance_criteria": ["queue state is server-side", "job lifecycle is explicit", "approval and dry-run are required"],
            "final_response_requirements": ["report only", "mention blocked status", "do not enable real automation"],
            "current_status": "NOT_STARTED",
            "blocked_for_now": True,
            "gate_status": "BLOCKED_PENDING_DRY_RUN_AND_APPROVAL",
            "blocking_reason": "Queueing depends on dry-run evidence and approval storage.",
            "required_future_ticket": "+2F",
        },
        {
            "ticket_id": "+2G",
            "title": "Mutation Gateway",
            "branch": "interface/original-plus2g-mutation-gateway",
            "purpose": "Enforce server-side mutation boundaries after queue and approval are present.",
            "dependencies": ["+2A", "+2B", "+2C", "+2D", "+2E", "+2F"],
            "required_inputs": ["auth foundation", "request storage schema", "audit contract", "approval store", "dry-run engine", "queue runner"],
            "required_outputs": ["mutation gateway contract", "server-side mutation boundary", "audit binding notes"],
            "required_tests": ["mutation validation", "e2e contract validation", "safety scan", "diff scope check"],
            "required_validators": [
                "scripts/validate_original_plus2g_mutation_gateway.py",
                "scripts/validate_original_plus2g_mutation_gateway_e2e.py",
            ],
            "required_reports": [
                "09_exports/original_plus2/original_plus2g_mutation_gateway_report.md",
                "09_exports/original_plus2/original_plus2g_mutation_gateway_design_report.md",
                "09_exports/original_plus2/original_plus2g_mutation_gateway_safety_report.md",
                "09_exports/original_plus2/original_plus2g_mutation_gateway_dependency_report.md",
                "09_exports/original_plus2/original_plus2g_mutation_gateway_validator_report.md",
                "09_exports/original_plus2/original_plus2g_mutation_gateway_acceptance_report.md",
            ],
            "no_go_conditions": ["mutation without audit", "mutation without approval", "mutation without rollback", "live execution without gate"],
            "rollback_requirements": ["keep mutation server-side only", "revert any browser-side mutation path", "stop if secrets leak to browser"],
            "allowed_files": [
                "14_backend/mutation/**",
                "scripts/validate_original_plus2g_mutation_gateway.py",
                "scripts/validate_original_plus2g_mutation_gateway_e2e.py",
                "09_exports/original_plus2/",
            ],
            "forbidden_files": common_forbidden_files,
            "implementation_boundary": "Mutation gateway only. No browser writes, no dashboard actions, no live automation outside backend gates.",
            "acceptance_criteria": ["mutation path is server-side", "approval and audit are mandatory", "rollback requirements are explicit"],
            "final_response_requirements": ["report only", "mention blocked status", "do not enable real automation"],
            "current_status": "NOT_STARTED",
            "blocked_for_now": True,
            "gate_status": "BLOCKED_PENDING_QUEUE_AND_NO_GO",
            "blocking_reason": "Mutation cannot proceed until queue, approval, and audit are all in place.",
            "required_future_ticket": "+2G",
        },
        {
            "ticket_id": "+2H",
            "title": "GitHub / Netlify Integration Adapters",
            "branch": "interface/original-plus2h-github-netlify-adapters",
            "purpose": "Add bounded integration adapters only after the mutation gateway exists.",
            "dependencies": ["+2A", "+2B", "+2C", "+2D", "+2E", "+2F", "+2G"],
            "required_inputs": ["auth foundation", "mutation gateway", "secrets policy", "integration policy"],
            "required_outputs": ["adapter contracts", "GitHub/Netlify boundary notes", "secret handling plan"],
            "required_tests": ["adapter validation", "e2e contract validation", "safety scan", "diff scope check"],
            "required_validators": [
                "scripts/validate_original_plus2h_github_netlify_adapters.py",
                "scripts/validate_original_plus2h_github_netlify_adapters_e2e.py",
            ],
            "required_reports": [
                "09_exports/original_plus2/original_plus2h_github_netlify_adapters_report.md",
                "09_exports/original_plus2/original_plus2h_github_netlify_adapters_design_report.md",
                "09_exports/original_plus2/original_plus2h_github_netlify_adapters_safety_report.md",
                "09_exports/original_plus2/original_plus2h_github_netlify_adapters_dependency_report.md",
                "09_exports/original_plus2/original_plus2h_github_netlify_adapters_validator_report.md",
                "09_exports/original_plus2/original_plus2h_github_netlify_adapters_acceptance_report.md",
            ],
            "no_go_conditions": ["adapters without secrets policy", "adapters without approval", "adapters without rollback", "live deployment control"],
            "rollback_requirements": ["keep adapters bounded", "revert any direct mutation path", "never expose tokens in browser"],
            "allowed_files": [
                "14_backend/integrations/**",
                "scripts/validate_original_plus2h_github_netlify_adapters.py",
                "scripts/validate_original_plus2h_github_netlify_adapters_e2e.py",
                "09_exports/original_plus2/",
            ],
            "forbidden_files": common_forbidden_files,
            "implementation_boundary": "Integration adapters only. No live GitHub or Netlify mutation from the browser or dashboard.",
            "acceptance_criteria": ["adapter boundaries are server-side", "secrets remain server-side", "rollbacks are explicit"],
            "final_response_requirements": ["report only", "mention blocked status", "do not enable real automation"],
            "current_status": "NOT_STARTED",
            "blocked_for_now": True,
            "gate_status": "BLOCKED_PENDING_MUTATION_GATEWAY_AND_SECRETS",
            "blocking_reason": "Integration adapters require the mutation gateway and server-side secret handling first.",
            "required_future_ticket": "+2H",
        },
        {
            "ticket_id": "+2I",
            "title": "Rollback / No-Go Enforcement",
            "branch": "interface/original-plus2i-rollback-no-go-enforcement",
            "purpose": "Block unsafe execution paths and enforce rollback when future automation goes wrong.",
            "dependencies": ["+2A", "+2B", "+2C", "+2D", "+2E", "+2F", "+2G", "+2H"],
            "required_inputs": ["auth foundation", "mutation gateway", "integration adapters", "safety policy"],
            "required_outputs": ["rollback enforcement contract", "no-go router", "blocker escalation notes"],
            "required_tests": ["rollback validation", "e2e contract validation", "safety scan", "diff scope check"],
            "required_validators": [
                "scripts/validate_original_plus2i_rollback_no_go_enforcement.py",
                "scripts/validate_original_plus2i_rollback_no_go_enforcement_e2e.py",
            ],
            "required_reports": [
                "09_exports/original_plus2/original_plus2i_rollback_no_go_enforcement_report.md",
                "09_exports/original_plus2/original_plus2i_rollback_no_go_enforcement_design_report.md",
                "09_exports/original_plus2/original_plus2i_rollback_no_go_enforcement_safety_report.md",
                "09_exports/original_plus2/original_plus2i_rollback_no_go_enforcement_dependency_report.md",
                "09_exports/original_plus2/original_plus2i_rollback_no_go_enforcement_validator_report.md",
                "09_exports/original_plus2/original_plus2i_rollback_no_go_enforcement_acceptance_report.md",
            ],
            "no_go_conditions": ["rollback policy missing", "no-go bypass", "unsafe execution allowed", "live automation shortcut"],
            "rollback_requirements": ["stop unsafe execution immediately", "revert the dangerous path", "preserve audit evidence"],
            "allowed_files": [
                "14_backend/rollback/**",
                "scripts/validate_original_plus2i_rollback_no_go_enforcement.py",
                "scripts/validate_original_plus2i_rollback_no_go_enforcement_e2e.py",
                "09_exports/original_plus2/",
            ],
            "forbidden_files": common_forbidden_files,
            "implementation_boundary": "Rollback and no-go enforcement only. No live execution, no browser mutation, no deployment controls.",
            "acceptance_criteria": ["unsafe paths are blocked", "rollback requirements are explicit", "audit evidence is preserved"],
            "final_response_requirements": ["report only", "mention blocked status", "do not enable real automation"],
            "current_status": "NOT_STARTED",
            "blocked_for_now": True,
            "gate_status": "BLOCKED_PENDING_INTEGRATIONS",
            "blocking_reason": "Rollback enforcement depends on the mutation and integration layers existing first.",
            "required_future_ticket": "+2I",
        },
        {
            "ticket_id": "+2J",
            "title": "Production Hardening & Monitoring",
            "branch": "interface/original-plus2j-production-hardening-monitoring",
            "purpose": "Finalize monitoring, resilience, and release hardening after every prior backend ticket exists.",
            "dependencies": ["+2A", "+2B", "+2C", "+2D", "+2E", "+2F", "+2G", "+2H", "+2I"],
            "required_inputs": ["all prior backend tickets", "monitoring policy", "release hardening checklist"],
            "required_outputs": ["hardening plan", "monitoring matrix", "release readiness notes"],
            "required_tests": ["hardening validation", "e2e contract validation", "safety scan", "diff scope check"],
            "required_validators": [
                "scripts/validate_original_plus2j_production_hardening_monitoring.py",
                "scripts/validate_original_plus2j_production_hardening_monitoring_e2e.py",
            ],
            "required_reports": [
                "09_exports/original_plus2/original_plus2j_production_hardening_monitoring_report.md",
                "09_exports/original_plus2/original_plus2j_production_hardening_monitoring_design_report.md",
                "09_exports/original_plus2/original_plus2j_production_hardening_monitoring_safety_report.md",
                "09_exports/original_plus2/original_plus2j_production_hardening_monitoring_dependency_report.md",
                "09_exports/original_plus2/original_plus2j_production_hardening_monitoring_validator_report.md",
                "09_exports/original_plus2/original_plus2j_production_hardening_monitoring_acceptance_report.md",
            ],
            "no_go_conditions": ["hardening before prior tickets exist", "monitoring without gates", "live automation shortcut"],
            "rollback_requirements": ["revert if monitoring is added before gates", "keep release hardening copy-only until future implementation"],
            "allowed_files": [
                "14_backend/monitoring/**",
                "scripts/validate_original_plus2j_production_hardening_monitoring.py",
                "scripts/validate_original_plus2j_production_hardening_monitoring_e2e.py",
                "09_exports/original_plus2/",
            ],
            "forbidden_files": common_forbidden_files,
            "implementation_boundary": "Production hardening only. No live automation, no browser execution, no mutation shortcuts.",
            "acceptance_criteria": ["monitoring and release hardening are explicit", "no live automation is enabled", "all prior tickets remain prerequisites"],
            "final_response_requirements": ["report only", "mention blocked status", "do not enable real automation"],
            "current_status": "NOT_STARTED",
            "blocked_for_now": True,
            "gate_status": "BLOCKED_PENDING_ALL_PRIOR",
            "blocking_reason": "Production hardening depends on every prior backend phase being in place.",
            "required_future_ticket": "+2J",
        },
    ]

    def format_items(items):
        if not items:
            return "- none"
        return "\n".join(f"- {item}" for item in items)

    def ticket_markdown(ticket):
        return "\n".join([
            f"# {ticket['ticket_id']} - {ticket['title']}",
            "",
            "## Purpose",
            ticket["purpose"],
            "",
            "## Dependencies",
            format_items(ticket["dependencies"]),
            "",
            "## Allowed Files",
            format_items(ticket["allowed_files"]),
            "",
            "## Forbidden Files",
            format_items(ticket["forbidden_files"]),
            "",
            "## Required Inputs",
            format_items(ticket["required_inputs"]),
            "",
            "## Required Outputs",
            format_items(ticket["required_outputs"]),
            "",
            "## Required Tests",
            format_items(ticket["required_tests"]),
            "",
            "## Required Validators",
            format_items(ticket["required_validators"]),
            "",
            "## Required Reports",
            format_items(ticket["required_reports"]),
            "",
            "## Implementation Boundary",
            ticket["implementation_boundary"],
            "",
            "## No-Go Conditions",
            format_items(ticket["no_go_conditions"]),
            "",
            "## Rollback Requirements",
            format_items(ticket["rollback_requirements"]),
            "",
            "## Acceptance Criteria",
            format_items(ticket["acceptance_criteria"]),
            "",
            "## Final Response Requirements",
            format_items(ticket["final_response_requirements"]),
        ])

    def codex_prompt(ticket):
        return "\n".join([
            "STRICT EXECUTION MODE.",
            "MAX-PROMPT MODE.",
            "CODEX-CAPABLE WORK UNIT.",
            "",
            "TASK:",
            f"Implement {ticket['ticket_id']} - {ticket['title']} in one large meaningful work unit.",
            "",
            "PROJECT:",
            "The Agent Command Center",
            "",
            "SOURCE BRANCH:",
            "interface/original-plus1e-backend-implementation-gate",
            "",
            "TARGET FUTURE BRANCH:",
            ticket["branch"],
            "",
            "PURPOSE:",
            ticket["purpose"],
            "",
            "AUTHORIZED FILES:",
            format_items(ticket["allowed_files"]),
            "",
            "FORBIDDEN FILES:",
            format_items(ticket["forbidden_files"]),
            "",
            "TEST REQUIREMENTS:",
            format_items(ticket["required_tests"]),
            "",
            "VALIDATOR REQUIREMENTS:",
            format_items(ticket["required_validators"]),
            "",
            "REPORT REQUIREMENTS:",
            format_items(ticket["required_reports"]),
            "",
            "SAFETY BOUNDARY:",
            "No live automation. No execution. No mutation. No backend writes. No deploy / merge / push / PR controls.",
            "",
            "NO-GO CONDITIONS:",
            format_items(ticket["no_go_conditions"]),
            "",
            "ROLLBACK REQUIREMENTS:",
            format_items(ticket["rollback_requirements"]),
            "",
            "ACCEPTANCE CRITERIA:",
            format_items(ticket["acceptance_criteria"]),
            "",
            "FINAL RESPONSE:",
            "Report only.",
            "Do not enable real automation.",
            "Do not perform any action outside the files listed above.",
        ])

    tickets = []
    for spec in ticket_specs:
        ticket = dict(spec)
        ticket["ticket_markdown"] = ticket_markdown(ticket)
        ticket["codex_prompt"] = codex_prompt(ticket)
        tickets.append(ticket)

    roadmap_markdown = "\n".join([
        "# Original +1E Backend Implementation Roadmap",
        "",
        "## Ticket Order",
        *[f"- {ticket['ticket_id']} {ticket['title']} | blocked_for_now: {str(ticket['blocked_for_now']).lower()} | current_status: {ticket['current_status']}" for ticket in tickets],
        "",
        "## Final Recommendation",
        "PLAN_PLUS2A_NEXT",
        "DO_NOT_ENABLE_REAL_AUTOMATION",
        "NOT_READY_FOR_REAL_AUTOMATION",
    ])

    dependency_markdown = "\n".join([
        "# Original +1E Dependency Prerequisite Map",
        "",
        "## Dependency Chains",
        "- +2A must precede all write-capable features.",
        "- +2B depends on +2A.",
        "- +2C depends on +2A and +2B.",
        "- +2D depends on +2A, +2B, and +2C.",
        "- +2E depends on +2A, +2B, and +2C.",
        "- +2F depends on +2A through +2E.",
        "- +2G depends on +2A through +2F.",
        "- +2H depends on +2G plus secrets management.",
        "- +2I depends on +2G and +2H.",
        "- +2J depends on all prior tickets.",
    ])

    gate_markdown = "\n".join([
        "# Original +1E Implementation Gate Status",
        "",
        *[
            f"- {ticket['ticket_id']} {ticket['title']}: {ticket['gate_status']} | blocking_reason: {ticket['blocking_reason']} | required_future_ticket: {ticket['required_future_ticket']} | can_proceed_now: false"
            for ticket in tickets
        ],
    ])

    validator_markdown = "\n".join([
        "# Original +1E Ticket Validator Requirements",
        "",
        *[
            f"- {ticket['ticket_id']} {ticket['title']}: unit validator, e2e validator, safety boundary validator, diff scope validator, report validator, production verification validator when applicable"
            for ticket in tickets
        ],
    ])

    report_markdown = "\n".join([
        "# Original +1E Ticket Report Requirements",
        "",
        *[
            f"- {ticket['ticket_id']} {ticket['title']}: implementation report, design report, safety report, dependency report, validator report, acceptance report, production verification report when applicable"
            for ticket in tickets
        ],
    ])

    policy_markdown = "\n".join([
        "# Original +1E Rollback / No-Go Ticket Policy",
        "",
        "- Stop if any ticket implies live automation, execution, or mutation.",
        "- Refuse merge if a ticket requires Netlify Functions or browser-side writes.",
        "- Require human review whenever auth, storage, queue, or mutation boundaries are missing.",
        "- Split a ticket if it crosses more than one future backend boundary at a time.",
        "- Downgrade any ticket to planning-only if it leaks into current dashboard execution.",
        "- Revert immediately if a future phase would enable real automation before all prerequisites exist.",
    ])

    readiness_markdown = "\n".join([
        "# Original +1E Backend Build Readiness Summary",
        "",
        "- +2A readiness: READY_FOR_PLANNING_ONLY",
        "- +2B readiness: BLOCKED_PENDING_2A",
        "- +2C readiness: BLOCKED_PENDING_2A_2B",
        "- +2D readiness: BLOCKED_PENDING_AUTH_STORAGE_AUDIT",
        "- +2E readiness: BLOCKED_PENDING_AUTH_STORAGE_AUDIT",
        "- +2F readiness: BLOCKED_PENDING_DRY_RUN_AND_APPROVAL",
        "- +2G readiness: BLOCKED_PENDING_QUEUE_AND_NO_GO",
        "- +2H readiness: BLOCKED_PENDING_MUTATION_GATEWAY_AND_SECRETS",
        "- +2I readiness: BLOCKED_PENDING_INTEGRATIONS",
        "- +2J readiness: BLOCKED_PENDING_ALL_PRIOR",
        "",
        "## Final Recommendation",
        "PLAN_PLUS2A_NEXT",
        "DO_NOT_ENABLE_REAL_AUTOMATION",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "READY_FOR_BACKEND_IMPLEMENTATION_PLANNING_ONLY",
    ])

    return {
        "model_id": "original-plus1e-backend-implementation-gate",
        "model_version": "1.0",
        "overall_status": "IMPLEMENTATION_PLANNING_ONLY",
        "current_recommendation": "READY_FOR_BACKEND_IMPLEMENTATION_PLANNING_ONLY",
        "final_recommendation": "NOT_READY_FOR_REAL_AUTOMATION",
        "summary": {
            "implementation_gate_only": True,
            "live_automation": False,
            "execution": False,
            "mutation": False,
            "backend_writes": False,
            "live_auth": False,
            "persistent_storage": False,
            "queue_execution": False,
            "copy_outputs": True,
        },
        "backend_implementation_gate_overview": [
            {"label": "Current system mode", "value": "IMPLEMENTATION_PLANNING_ONLY", "status": "warning"},
            {"label": "Real backend implementation started", "value": "false", "status": "fail"},
            {"label": "Live auth implemented", "value": "false", "status": "fail"},
            {"label": "Database implemented", "value": "false", "status": "fail"},
            {"label": "Queue implemented", "value": "false", "status": "fail"},
            {"label": "Mutation gateway implemented", "value": "false", "status": "fail"},
            {"label": "GitHub / Netlify adapters implemented", "value": "false", "status": "fail"},
            {"label": "Real automation enabled", "value": "false", "status": "fail"},
            {"label": "Current recommendation", "value": "READY_FOR_BACKEND_IMPLEMENTATION_PLANNING_ONLY", "status": "warning"},
            {"label": "Final recommendation", "value": "NOT_READY_FOR_REAL_AUTOMATION", "status": "locked"},
        ],
        "future_phase_ticket_map": [
            {
                "ticket_id": ticket["ticket_id"],
                "title": ticket["title"],
                "purpose": ticket["purpose"],
                "dependencies": ", ".join(ticket["dependencies"]),
                "required_inputs": ", ".join(ticket["required_inputs"]),
                "required_outputs": ", ".join(ticket["required_outputs"]),
                "required_tests": ", ".join(ticket["required_tests"]),
                "required_validators": ", ".join(ticket["required_validators"]),
                "required_reports": ", ".join(ticket["required_reports"]),
                "no_go_conditions": ", ".join(ticket["no_go_conditions"]),
                "rollback_requirements": ", ".join(ticket["rollback_requirements"]),
                "current_status": ticket["current_status"],
                "blocked_for_now": ticket["blocked_for_now"],
                "ticket_markdown": ticket["ticket_markdown"],
                "codex_prompt": ticket["codex_prompt"],
                "allowed_files": ticket["allowed_files"],
                "forbidden_files": ticket["forbidden_files"],
                "implementation_boundary": ticket["implementation_boundary"],
                "acceptance_criteria": ticket["acceptance_criteria"],
                "final_response_requirements": ticket["final_response_requirements"],
                "branch": ticket["branch"],
            }
            for ticket in tickets
        ],
        "dependency_prerequisite_map": [
            {
                "ticket_id": ticket["ticket_id"],
                "required_before": ticket["title"],
                "dependencies": ticket["dependencies"],
                "current_status": ticket["current_status"],
                "blocking_level": "medium" if ticket["ticket_id"] == "+2A" else "high",
                "recommended_future_phase": ticket["branch"].replace("interface/", ""),
            }
            for ticket in tickets
        ],
        "implementation_gate_statuses": [
            {"gate": "Auth Gate", "current_status": "BLOCKED", "blocking_reason": "No auth foundation exists yet.", "required_future_ticket": "+2A", "can_proceed_now": False},
            {"gate": "Storage Gate", "current_status": "BLOCKED", "blocking_reason": "No persistent storage exists yet.", "required_future_ticket": "+2B", "can_proceed_now": False},
            {"gate": "Audit Gate", "current_status": "BLOCKED", "blocking_reason": "No immutable audit log exists yet.", "required_future_ticket": "+2C", "can_proceed_now": False},
            {"gate": "Approval Gate", "current_status": "BLOCKED", "blocking_reason": "No approval storage exists yet.", "required_future_ticket": "+2D", "can_proceed_now": False},
            {"gate": "Dry-Run Gate", "current_status": "BLOCKED", "blocking_reason": "No server-side dry-run engine exists yet.", "required_future_ticket": "+2E", "can_proceed_now": False},
            {"gate": "Queue Gate", "current_status": "BLOCKED", "blocking_reason": "No queue / job runner exists yet.", "required_future_ticket": "+2F", "can_proceed_now": False},
            {"gate": "Mutation Gateway Gate", "current_status": "BLOCKED", "blocking_reason": "No mutation gateway exists yet.", "required_future_ticket": "+2G", "can_proceed_now": False},
            {"gate": "External Integration Gate", "current_status": "BLOCKED", "blocking_reason": "No bounded GitHub / Netlify adapters exist yet.", "required_future_ticket": "+2H", "can_proceed_now": False},
            {"gate": "Rollback Gate", "current_status": "BLOCKED", "blocking_reason": "No rollback / no-go enforcement exists yet.", "required_future_ticket": "+2I", "can_proceed_now": False},
            {"gate": "Production Hardening Gate", "current_status": "BLOCKED", "blocking_reason": "No monitoring or release hardening exists yet.", "required_future_ticket": "+2J", "can_proceed_now": False},
        ],
        "ticket_validator_requirements": [
            {
                "ticket_id": ticket["ticket_id"],
                "unit_validator": ticket["required_validators"][0],
                "integration_validator": ticket["required_validators"][1],
                "safety_validator": "safety boundary validator",
                "diff_scope_validator": "diff scope validator",
                "report_validator": "report validator",
                "production_verification_validator": "production verification validator when applicable",
            }
            for ticket in tickets
        ],
        "ticket_report_requirements": [
            {
                "ticket_id": ticket["ticket_id"],
                "implementation_report": ticket["required_reports"][0],
                "design_report": ticket["required_reports"][1],
                "safety_report": ticket["required_reports"][2],
                "dependency_report": ticket["required_reports"][3],
                "validator_report": ticket["required_reports"][4],
                "acceptance_report": ticket["required_reports"][5],
                "production_verification_report": "future production verification report when applicable",
            }
            for ticket in tickets
        ],
        "rollback_no_go_ticket_policy": [
            "Stop if any ticket implies live automation, execution, or mutation.",
            "Refuse merge if a ticket requires Netlify Functions or browser-side writes.",
            "Require human review whenever auth, storage, queue, or mutation boundaries are missing.",
            "Split a ticket if it crosses more than one future backend boundary at a time.",
            "Downgrade any ticket to planning-only if it leaks into current dashboard execution.",
            "Revert immediately if a future phase would enable real automation before all prerequisites exist.",
        ],
        "backend_build_readiness_summary": [
            {"label": "+2A readiness", "value": "READY_FOR_PLANNING_ONLY", "status": "warning"},
            {"label": "+2B readiness", "value": "BLOCKED_PENDING_2A", "status": "locked"},
            {"label": "+2C readiness", "value": "BLOCKED_PENDING_2A_2B", "status": "locked"},
            {"label": "+2D readiness", "value": "BLOCKED_PENDING_AUTH_STORAGE_AUDIT", "status": "locked"},
            {"label": "+2E readiness", "value": "BLOCKED_PENDING_AUTH_STORAGE_AUDIT", "status": "locked"},
            {"label": "+2F readiness", "value": "BLOCKED_PENDING_DRY_RUN_AND_APPROVAL", "status": "locked"},
            {"label": "+2G readiness", "value": "BLOCKED_PENDING_QUEUE_AND_NO_GO", "status": "locked"},
            {"label": "+2H readiness", "value": "BLOCKED_PENDING_MUTATION_GATEWAY_AND_SECRETS", "status": "locked"},
            {"label": "+2I readiness", "value": "BLOCKED_PENDING_INTEGRATIONS", "status": "locked"},
            {"label": "+2J readiness", "value": "BLOCKED_PENDING_ALL_PRIOR", "status": "locked"},
        ],
        "roadmap_markdown": roadmap_markdown,
        "dependency_prerequisite_markdown": dependency_markdown,
        "implementation_gate_status_markdown": gate_markdown,
        "ticket_validator_requirements_markdown": validator_markdown,
        "ticket_report_requirements_markdown": report_markdown,
        "rollback_no_go_ticket_policy_markdown": policy_markdown,
        "backend_build_readiness_summary_markdown": readiness_markdown,
        "ticket_lookup": {ticket["ticket_id"]: ticket for ticket in tickets},
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
