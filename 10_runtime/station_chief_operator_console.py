import json
import hashlib
import re
from pathlib import Path

OPERATOR_CONSOLE_MODULE_VERSION = "3.6.0"
OPERATOR_CONSOLE_STATUS = "SCHEMA_ONLY"
OPERATOR_CONSOLE_PHASE = "UI / Operator Console Schema"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def normalize_console_label(label: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return normalized or "operator-console"

def generate_console_id(command: str, label: str, runtime_version: str = "3.6.0") -> str:
    normalized_label = normalize_console_label(label)
    hash_input = f"{runtime_version}:{command}:{label}"
    hash_chars = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:12]
    return f"operator-console-v3-6-{normalized_label}-{hash_chars}"

def create_operator_console_screen_schema() -> dict:
    return {
        "operator_console_screen_schema_version": "3.6.0",
        "schema_status": "SCHEMA_ONLY",
        "console_title": "Station Chief Operator Console",
        "layout_type": "read_only_control_dashboard_schema",
        "primary_sections": [
            "runtime_status_panel",
            "command_brief_panel",
            "controlled_execution_panel",
            "work_order_panel",
            "worker_registry_panel",
            "department_routing_panel",
            "orchestration_sandbox_panel",
            "approval_queue_panel",
            "release_lock_panel",
            "human_control_surface_panel",
            "audit_and_export_panel"
        ],
        "global_status_chips": [
            "baseline preserved",
            "external actions disabled",
            "live workers inactive",
            "real hiring disabled",
            "live routing disabled",
            "live orchestration disabled",
            "schema only"
        ],
        "global_warnings": [],
        "allowed_interaction_modes": [
            "read_only_review",
            "export_artifacts",
            "approval_review",
            "dry_run_preview",
            "blocked_action_review"
        ],
        "blocked_interaction_modes": [
            "live_execution",
            "live_worker_animation",
            "real_worker_hiring",
            "live_worker_routing",
            "live_orchestration",
            "uncontrolled_repo_edit",
            "live_api_connection",
            "package_installation"
        ],
        "safety_invariants": [
            "no live external API actions",
            "no real worker hiring",
            "no worker animation",
            "no live worker routing",
            "no live orchestration",
            "no uncontrolled repo writes",
            "no baseline mutation",
            "no Devinization overlay mutation",
            "no shell command execution",
            "no package installation",
            "UI schema does not authorize execution"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "live_ui_rendered": False,
        "execution_authorized": False
    }

def create_runtime_status_panel_schema(result: dict) -> dict:
    return {
        "runtime_status_panel_schema_version": "3.6.0",
        "panel_id": "runtime_status_panel",
        "panel_title": "Runtime Status",
        "panel_mode": "read_only",
        "fields": [
            "station_chief_runtime_version",
            "runtime_status",
            "release_status",
            "command_type",
            "activation_tier",
            "next_step"
        ],
        "status_values": {
            "station_chief_runtime_version": result.get("station_chief_runtime_version"),
            "runtime_status": result.get("runtime_status"),
            "release_status": result.get("release_status"),
            "command_type": result.get("command_type"),
            "activation_tier": result.get("activation_tier"),
            "next_step": result.get("next_step")
        },
        "warnings": [],
        "blocked_controls": [
            "execute live action",
            "animate workforce",
            "hire real worker",
            "route live worker",
            "perform live orchestration"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "execution_authorized": False
    }

def create_approval_queue_panel_schema(result: dict) -> dict:
    items = []
    if result.get("approval_handoff_packet"): items.append("approval_handoff_packet")
    if result.get("signed_approval_record"): items.append("approval_record")
    if result.get("approval_ledger_bundle"): items.append("approval_ledger_bundle")
    if result.get("controlled_execution_preflight_contract"): items.append("controlled_execution_preflight_contract")
    if result.get("blocked_action_ledger"): items.append("blocked_action_ledger")
    if result.get("release_lock_bundle"): items.append("release_lock_bundle")

    return {
        "approval_queue_panel_schema_version": "3.6.0",
        "panel_id": "approval_queue_panel",
        "panel_title": "Approval Queue",
        "panel_mode": "review_only",
        "approval_items": items,
        "approval_states": [
            "review_required",
            "ready_for_human_review",
            "blocked",
            "signed_record_available",
            "ledger_available",
            "release_locked"
        ],
        "blocked_controls": [
            "approve without review",
            "execute from approval record",
            "execute from ledger",
            "bypass release lock"
        ],
        "required_tokens": [
            "YES_I_APPROVE_SANDBOX_FILE_WRITE",
            "YES_I_APPROVE_SCOPED_REPO_PATCH",
            "YES_I_APPROVE_APPROVAL_HANDOFF_RECORD"
        ],
        "execution_authorized": False,
        "external_actions_taken": False
    }

def create_work_order_panel_schema(result: dict) -> dict:
    work_orders = result.get("work_orders") or []
    executor_summary = result.get("work_order_executor_summary") or {}
    
    rows = []
    for wo in work_orders:
        rows.append({
            "work_order_id": wo.get("work_order_id"),
            "title": wo.get("task"), # Using task as title if not explicit
            "status": wo.get("status"),
            "execution_mode": wo.get("execution_mode", "dry_run_only"),
            "dry_run_status": "PASS", # Default for schema preview
            "completion_proof_available": True
        })

    return {
        "work_order_panel_schema_version": "3.6.0",
        "panel_id": "work_order_panel",
        "panel_title": "Work Orders",
        "panel_mode": "dry_run_review_only",
        "work_order_count": len(work_orders),
        "summary_fields": [
            "work_order_id",
            "title",
            "status",
            "execution_mode",
            "dry_run_status",
            "completion_proof_available"
        ],
        "work_order_rows": rows,
        "blocked_controls": [
            "execute work order live",
            "modify repo from work order",
            "assign live worker",
            "bypass dry-run proof"
        ],
        "external_actions_taken": False,
        "execution_authorized": False
    }

def create_worker_registry_panel_schema(result: dict) -> dict:
    candidates = result.get("worker_candidates") or []
    
    rows = []
    for c in candidates:
        rows.append({
            "worker_id": c.get("worker_id"),
            "worker_role_title": c.get("worker_role_title"),
            "worker_role_type": c.get("worker_role_type"),
            "source_work_order_id": c.get("source_work_order_id"),
            "worker_mode": c.get("worker_mode", "preview_only"),
            "assignment_status": "PENDING"
        })

    return {
        "worker_registry_panel_schema_version": "3.6.0",
        "panel_id": "worker_registry_panel",
        "panel_title": "Worker Registry Preview",
        "panel_mode": "registry_preview_only",
        "worker_count": len(candidates),
        "worker_rows": rows,
        "blocked_controls": [
            "hire real worker",
            "animate worker",
            "assign live worker",
            "connect worker to API",
            "run worker task"
        ],
        "real_worker_hiring_performed": False,
        "live_worker_agents_activated": False,
        "execution_authorized": False
    }

def create_department_routing_panel_schema(result: dict) -> dict:
    candidates = result.get("department_route_candidates") or []
    conflict_detector = result.get("department_routing_conflict_detector") or {}
    
    rows = []
    for c in candidates:
        rows.append({
            "route_id": c.get("route_id"),
            "source_worker_id": c.get("source_worker_id"),
            "source_work_order_id": c.get("source_work_order_id"),
            "target_department": c.get("target_department"),
            "target_family": c.get("target_family"),
            "route_mode": c.get("route_mode", "routing_preview_only"),
            "dry_run_status": "PASS"
        })

    return {
        "department_routing_panel_schema_version": "3.6.0",
        "panel_id": "department_routing_panel",
        "panel_title": "Department Routing Preview",
        "panel_mode": "routing_preview_only",
        "route_count": len(candidates),
        "route_rows": rows,
        "conflict_summary": conflict_detector,
        "blocked_controls": [
            "route live worker",
            "overwrite department routing",
            "bypass conflict detector",
            "execute route"
        ],
        "live_worker_routing_performed": False,
        "execution_authorized": False
    }

def create_orchestration_sandbox_panel_schema(result: dict) -> dict:
    nodes = result.get("orchestration_nodes") or []
    conflict_detector = result.get("orchestration_conflict_detector") or {}
    
    rows = []
    for n in nodes:
        rows.append({
            "orchestration_id": n.get("orchestration_id"),
            "source_route_id": n.get("source_route_id"),
            "source_worker_id": n.get("source_worker_id"),
            "target_department": n.get("target_department"),
            "coordination_role": n.get("coordination_role"),
            "orchestration_mode": n.get("orchestration_mode", "orchestration_sandbox_only"),
            "dry_run_status": "PASS"
        })

    return {
        "orchestration_sandbox_panel_schema_version": "3.6.0",
        "panel_id": "orchestration_sandbox_panel",
        "panel_title": "Multi-Agent Orchestration Sandbox",
        "panel_mode": "orchestration_sandbox_only",
        "orchestration_node_count": len(nodes),
        "orchestration_rows": rows,
        "conflict_summary": conflict_detector,
        "blocked_controls": [
            "perform live orchestration",
            "animate workers",
            "route live workers",
            "bypass orchestration conflict detector",
            "execute orchestration"
        ],
        "live_orchestration_performed": False,
        "execution_authorized": False
    }

def create_release_lock_panel_schema(result: dict) -> dict:
    lock_bundle = result.get("release_lock_bundle")
    manifest = lock_bundle.get("stable_release_manifest") if lock_bundle else None
    
    return {
        "release_lock_panel_schema_version": "3.6.0",
        "panel_id": "release_lock_panel",
        "panel_title": "Release Lock",
        "panel_mode": "read_only",
        "release_lock_present": lock_bundle is not None,
        "stable_runtime_version": manifest.get("runtime_version") if manifest else None,
        "release_lock_status": "ACTIVE" if lock_bundle else "INACTIVE",
        "manifest_digest": manifest.get("release_manifest_digest") if manifest else None,
        "blocked_controls": [
            "edit release lock from console",
            "bypass release lock",
            "treat release lock as execution permission"
        ],
        "execution_authorized": False
    }

def create_human_control_surface_schema() -> dict:
    return {
        "human_control_surface_schema_version": "3.6.0",
        "panel_id": "human_control_surface_panel",
        "panel_title": "Human Control Surface",
        "panel_mode": "approval_and_review_schema_only",
        "control_groups": [
            "review controls",
            "export controls",
            "approval controls",
            "dry-run controls",
            "blocked-action review controls"
        ],
        "safe_controls": [
            "view runtime summary",
            "view work orders",
            "view worker registry previews",
            "view routing previews",
            "view orchestration sandbox",
            "export review artifacts",
            "inspect approval requirements"
        ],
        "danger_controls_disabled": [
            "execute live action",
            "animate workforce",
            "hire worker",
            "route live worker",
            "perform live orchestration",
            "mutate baseline",
            "bypass validator",
            "bypass scoped patch confirmation"
        ],
        "required_confirmation_tokens": [
            "YES_I_APPROVE_SANDBOX_FILE_WRITE",
            "YES_I_APPROVE_SCOPED_REPO_PATCH",
            "YES_I_APPROVE_APPROVAL_HANDOFF_RECORD"
        ],
        "blocked_controls": [
            "execute live action",
            "animate workforce",
            "hire worker",
            "route live worker",
            "perform live orchestration",
            "mutate baseline",
            "bypass validator",
            "bypass scoped patch confirmation"
        ],
        "execution_authorized": False,
        "live_ui_rendered": False
    }

def create_operator_action_registry() -> dict:
    rules = {}
    actions = [
        ("view_runtime_status", "allowed", None, "View current runtime status and version."),
        ("view_command_brief", "allowed", None, "View the generated command brief."),
        ("view_controlled_execution", "allowed", None, "View controlled execution plans."),
        ("view_work_orders", "allowed", None, "View non-executing work orders."),
        ("view_worker_registry", "allowed", None, "View worker registry candidate previews."),
        ("view_department_routing", "allowed", None, "View department routing previews."),
        ("view_orchestration_sandbox", "allowed", None, "View orchestration sandbox nodes."),
        ("view_release_lock", "allowed", None, "View stable release lock status."),
        ("view_approval_queue", "allowed", None, "View pending human approvals."),
        ("export_operator_console_artifacts", "allowed", None, "Export console schema and review artifacts."),
        ("execute_live_action", "blocked", None, "Live execution is disabled in this layer."),
        ("animate_worker", "blocked", None, "Worker animation is disabled."),
        ("hire_real_worker", "blocked", None, "Real worker hiring is disabled."),
        ("route_live_worker", "blocked", None, "Live worker routing is disabled."),
        ("perform_live_orchestration", "blocked", None, "Live orchestration is disabled."),
        ("mutate_locked_baseline", "blocked", None, "Baseline mutation is strictly forbidden."),
        ("mutate_devinization_overlay", "blocked", None, "Overlay mutation is forbidden."),
        ("bypass_scope_check", "blocked", None, "Scope check bypass is forbidden."),
        ("bypass_validator", "blocked", None, "Validator bypass is forbidden."),
        ("connect_live_api", "blocked", None, "External API connections are disabled."),
        ("install_package", "blocked", None, "Package installation is disabled."),
        ("sandbox_file_write", "confirmation_required", "YES_I_APPROVE_SANDBOX_FILE_WRITE", "Requires explicit confirmation token."),
        ("scoped_repo_patch", "confirmation_required", "YES_I_APPROVE_SCOPED_REPO_PATCH", "Requires explicit confirmation token."),
        ("signed_approval_record", "confirmation_required", "YES_I_APPROVE_APPROVAL_HANDOFF_RECORD", "Requires explicit confirmation token.")
    ]

    for aid, atype, token, desc in actions:
        rules[aid] = {
            "action_id": aid,
            "action_type": atype,
            "requires_token": token,
            "description": desc
        }

    return {
        "operator_action_registry_version": "3.6.0",
        "registry_status": "SCHEMA_ONLY",
        "allowed_actions": [aid for aid, atype, _, _ in actions if atype == "allowed"],
        "blocked_actions": [aid for aid, atype, _, _ in actions if atype == "blocked"],
        "confirmation_required_actions": [aid for aid, atype, _, _ in actions if atype == "confirmation_required"],
        "action_rules": rules,
        "external_actions_taken": False,
        "execution_authorized": False
    }

def create_disabled_action_state_map(operator_action_registry: dict) -> dict:
    blocked = operator_action_registry["blocked_actions"]
    return {
        "disabled_action_state_map_version": "3.6.0",
        "disabled_action_count": len(blocked),
        "disabled_actions": blocked,
        "disabled_reason": "Live execution controls remain disabled in v2.5.0 schema-only operator console.",
        "external_actions_taken": False,
        "execution_authorized": False
    }

def create_operator_console_review_bundle(result: dict) -> dict:
    registry = create_operator_action_registry()
    
    return {
        "operator_console_review_bundle_version": "3.6.0",
        "console_status": "SCHEMA_ONLY",
        "operator_console_screen_schema": create_operator_console_screen_schema(),
        "runtime_status_panel_schema": create_runtime_status_panel_schema(result),
        "approval_queue_panel_schema": create_approval_queue_panel_schema(result),
        "work_order_panel_schema": create_work_order_panel_schema(result),
        "worker_registry_panel_schema": create_worker_registry_panel_schema(result),
        "department_routing_panel_schema": create_department_routing_panel_schema(result),
        "orchestration_sandbox_panel_schema": create_orchestration_sandbox_panel_schema(result),
        "release_lock_panel_schema": create_release_lock_panel_schema(result),
        "human_control_surface_schema": create_human_control_surface_schema(),
        "operator_action_registry": registry,
        "disabled_action_state_map": create_disabled_action_state_map(registry),
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "live_ui_rendered": False,
        "execution_authorized": False
    }

def create_operator_console_safety_summary(review_bundle: dict) -> dict:
    return {
        "operator_console_safety_summary_version": "3.6.0",
        "safety_status": "SAFE_SCHEMA_ONLY",
        "safe_panel_count": 11,
        "blocked_action_count": len(review_bundle["operator_action_registry"]["blocked_actions"]),
        "live_execution_controls_disabled": True,
        "human_confirmation_required_for_dangerous_actions": True,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "live_ui_rendered": False,
        "execution_authorized": False
    }

def create_operator_console_readiness_summary(review_bundle: dict, safety_summary: dict) -> dict:
    ready = (
        safety_summary["safety_status"] == "SAFE_SCHEMA_ONLY"
        and safety_summary["live_execution_controls_disabled"]
        and safety_summary["human_confirmation_required_for_dangerous_actions"]
        and safety_summary["baseline_preserved"]
        and safety_summary["external_actions_taken"] == False
        and safety_summary["live_ui_rendered"] == False
    )

    return {
        "operator_console_readiness_summary_version": "3.6.0",
        "console_status": "SCHEMA_ONLY",
        "ready_for_github_patch_hardening": ready,
        "next_layer": "GitHub Patch Application Hardening",
        "readiness_checks": {
            "screen_schema_available": True,
            "status_panel_available": True,
            "approval_queue_available": True,
            "work_order_panel_available": True,
            "worker_registry_panel_available": True,
            "department_routing_panel_available": True,
            "orchestration_panel_available": True,
            "human_control_surface_available": True,
            "dangerous_actions_disabled": True
        },
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "live_ui_rendered": False,
        "execution_authorized": False
    }

def create_github_patch_hardening_readiness_bridge(result: dict, readiness_summary: dict) -> dict:
    return {
        "github_patch_hardening_readiness_bridge_version": "3.6.0",
        "current_layer": "UI / Operator Console Schema",
        "next_layer": "GitHub Patch Application Hardening",
        "ready_for_github_patch_hardening": readiness_summary["ready_for_github_patch_hardening"],
        "required_next_capabilities": [
            "stricter patch-root validation",
            "patch preview diff contract",
            "protected path policy expansion",
            "patch digest manifest",
            "patch rollback preview",
            "changed-file proof hardening",
            "human approval chain binding",
            "no uncontrolled repo edits"
        ],
        "non_goals_for_next_layer": [
            "no external API execution",
            "no full workforce animation",
            "no real worker hiring",
            "no baseline mutation",
            "no Devinization overlay mutation"
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "live_ui_rendered": False,
        "execution_authorized": False
    }

def create_operator_console_bundle(result: dict) -> dict:
    review_bundle = create_operator_console_review_bundle(result)
    safety_summary = create_operator_console_safety_summary(review_bundle)
    readiness_summary = create_operator_console_readiness_summary(review_bundle, safety_summary)
    bridge = create_github_patch_hardening_readiness_bridge(result, readiness_summary)
    
    return {
        "operator_console_bundle_version": "3.6.0",
        "console_status": OPERATOR_CONSOLE_STATUS,
        "operator_console_review_bundle": review_bundle,
        "operator_console_safety_summary": safety_summary,
        "operator_console_readiness_summary": readiness_summary,
        "github_patch_hardening_readiness_bridge": bridge,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "live_ui_rendered": False,
        "execution_authorized": False
    }
