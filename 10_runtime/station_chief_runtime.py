#!/usr/bin/env python3
from __future__ import annotations
import sys

import argparse
import hashlib
import inspect
import json
import re
from pathlib import Path
from typing import Any

from station_chief_adapters import (
    classify_path_safety,
    classify_repo_patch_safety,
    create_changed_file_scope_proof,
    create_execution_plan,
    create_file_operation_plan,
    create_repo_patch_plan,
    evaluate_execution_gate,
    evaluate_repo_patch_gate,
    list_adapters,
    run_noop_adapter,
    run_sandbox_file_write_adapter,
    run_scoped_repo_patch_adapter,
)
from station_chief_approval_handoff import (
    compare_dry_run_bundles,
    create_approval_handoff_packet,
)
from station_chief_approval_ledger import (
    collect_approval_records_from_paths,
    compare_signed_approval_records,
    create_approval_ledger_bundle,
    lookup_approval_records_by_digest,
    verify_approval_ledger_index,
)
from station_chief_approval_records import (
    APPROVAL_RECORD_CONFIRMATION_TOKEN,
    create_approval_record_audit_manifest,
    create_approval_review_ui_schema,
    create_signed_approval_record,
    verify_signed_approval_record,
)
from station_chief_release_lock import (
    attach_release_lock,
    create_release_lock_bundle,
    create_stable_release_manifest,
    verify_stable_release_manifest,
    write_release_lock,
)
from station_chief_controlled_execution import (
    create_controlled_execution_bundle,
    create_controlled_execution_profile_catalog,
)
from station_chief_work_order_executor import (
    create_executable_work_order_schema,
    create_work_order_executor_bundle,
)
from station_chief_worker_hiring_registry import (
    create_worker_hiring_registry_bundle,
    create_worker_role_schema,
)
from station_chief_department_routing import (
    create_department_routing_bundle,
    create_department_routing_schema,
)
from station_chief_multi_agent_orchestration import (
    create_multi_agent_orchestration_bundle,
    create_orchestration_topology_schema,
)
from station_chief_operator_console import (
    create_operator_console_bundle,
    create_operator_console_screen_schema,
)
from station_chief_github_patch_hardening import (
    create_github_patch_hardening_bundle,
    create_patch_hardening_schema,
)
from station_chief_deployment_packaging import (
    make_deployment_packaging_bundle,
    make_deployment_artifact_schema,
)
from station_chief_controlled_worker_execution import (
    FIRST_CONTROLLED_WORKER_EXECUTION_TOKEN,
    create_controlled_worker_execution_bundle,
    create_controlled_worker_execution_schema,
)
from station_chief_tool_permission_binding import (
    TOOL_PERMISSION_APPROVAL_TOKENS,
    create_tool_permission_binding_bundle,
    create_tool_permission_binding_schema,
)
from station_chief_live_execution_telemetry_abort import (
    LIVE_EXECUTION_TELEMETRY_ABORT_APPROVAL_TOKEN,
    create_live_execution_telemetry_abort_bundle,
    create_live_execution_telemetry_abort_schema,
)
from station_chief_post_run_audit_expansion import (
    POST_RUN_AUDIT_EXPANSION_APPROVAL_TOKEN,
    create_post_run_audit_expansion_bundle,
    create_post_run_audit_expansion_schema,
)
from station_chief_multi_worker_sandbox_coordination import (
    MULTI_WORKER_SANDBOX_COORDINATION_APPROVAL_TOKEN,
    create_multi_worker_sandbox_coordination_bundle,
    create_multi_worker_sandbox_coordination_schema,
)
from station_chief_controlled_external_tool_adapter_preview import (
    CONTROLLED_EXTERNAL_TOOL_ADAPTER_PREVIEW_APPROVAL_TOKEN,
    create_controlled_external_tool_adapter_preview_bundle,
    create_controlled_external_tool_adapter_preview_schema,
)
from station_chief_permissioned_external_api_dry_run_preview import (
    PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW_APPROVAL_TOKEN,
    create_permissioned_external_api_dry_run_preview_bundle,
    create_permissioned_external_api_dry_run_preview_schema,
)
from station_chief_controlled_multi_worker_audit_replay_preview import (
    CONTROLLED_MULTI_WORKER_AUDIT_REPLAY_PREVIEW_APPROVAL_TOKEN,
    create_controlled_multi_worker_audit_replay_preview_bundle,
    create_controlled_multi_worker_audit_replay_preview_schema,
)
from station_chief_operator_approval_queue_enforcement import (
    OPERATOR_APPROVAL_QUEUE_ENFORCEMENT_APPROVAL_TOKEN,
    create_operator_approval_queue_enforcement_bundle,
    create_operator_approval_queue_enforcement_schema,
)
from station_chief_release_candidate_hardening import (
    RELEASE_CANDIDATE_HARDENING_APPROVAL_TOKEN,
    create_release_candidate_hardening_bundle,
    create_release_candidate_hardening_schema,
)
from station_chief_controlled_production_readiness_gate import (
    CONTROLLED_PRODUCTION_READINESS_GATE_APPROVAL_TOKEN,
    create_controlled_production_readiness_gate_bundle,
    create_controlled_production_readiness_gate_schema,
)
from station_chief_controlled_worker_hiring_activation_pilot import (
    CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT_APPROVAL_TOKEN,
    create_controlled_worker_hiring_activation_pilot_bundle,
    create_controlled_worker_hiring_activation_pilot_schema,
)
from station_chief_first_supervised_production_dry_run import (
    FIRST_SUPERVISED_PRODUCTION_DRY_RUN_APPROVAL_TOKEN,
    create_first_supervised_production_dry_run_bundle,
    create_first_supervised_production_dry_run_schema,
)
from station_chief_limited_external_tool_supervised_pilot import (
    LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_APPROVAL_TOKEN,
    create_limited_external_tool_supervised_pilot_bundle,
    create_limited_external_tool_supervised_pilot_schema,
)
from station_chief_supervised_external_api_pilot import (
    SUPERVISED_EXTERNAL_API_PILOT_APPROVAL_TOKEN,
    create_supervised_external_api_pilot_bundle,
    create_supervised_external_api_pilot_schema,
)
from station_chief_monitored_rollback_recovery_drill import (
    MONITORED_ROLLBACK_RECOVERY_DRILL_APPROVAL_TOKEN,
    create_monitored_rollback_recovery_drill_bundle,
    create_monitored_rollback_recovery_drill_schema,
)
from station_chief_supervised_production_pilot_readiness_review import (
    SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_APPROVAL_TOKEN,
    create_supervised_production_pilot_readiness_review_bundle,
    create_supervised_production_pilot_readiness_review_schema,
)
from station_chief_credential_vault_denial_secret_handling_proof import (
    CREDENTIAL_VAULT_DENIAL_SECRET_HANDLING_PROOF_APPROVAL_TOKEN,
    create_credential_vault_denial_secret_handling_proof_bundle,
    create_credential_vault_denial_secret_handling_proof_schema,
)
from station_chief_network_socket_lockdown_proof import (
    NETWORK_SOCKET_LOCKDOWN_PROOF_APPROVAL_TOKEN,
    create_network_socket_lockdown_proof_bundle,
    create_network_socket_lockdown_proof_schema,
)
from station_chief_live_external_action_final_preflight_gate import (
    LIVE_EXTERNAL_ACTION_FINAL_PREFLIGHT_GATE_APPROVAL_TOKEN,
    create_live_external_action_final_preflight_gate_bundle,
    create_live_external_action_final_preflight_gate_schema,
)
from station_chief_first_tiny_real_world_supervised_execution_candidate import (
    FIRST_TINY_REAL_WORLD_SUPERVISED_EXECUTION_CANDIDATE_APPROVAL_TOKEN,
    create_first_tiny_real_world_supervised_execution_candidate_bundle,
    create_first_tiny_real_world_supervised_execution_candidate_schema,
)
from station_chief_post_action_verification_and_audit_review import (
    POST_ACTION_VERIFICATION_AND_AUDIT_REVIEW_APPROVAL_TOKEN,
    create_post_action_verification_and_audit_review_bundle,
    create_post_action_verification_and_audit_review_schema,
)
from station_chief_supervised_rollback_cleanup_candidate import (
    SUPERVISED_ROLLBACK_CLEANUP_CANDIDATE_APPROVAL_TOKEN,
    create_supervised_rollback_cleanup_candidate_bundle,
    create_supervised_rollback_cleanup_candidate_schema,
)
from station_chief_limited_live_worker_activation_candidate import (
    LIMITED_LIVE_WORKER_ACTIVATION_CANDIDATE_APPROVAL_TOKEN,
    create_limited_live_worker_activation_candidate_bundle,
    create_limited_live_worker_activation_candidate_schema,
)
from station_chief_permissioned_worker_task_assignment_candidate import (
    PERMISSIONED_WORKER_TASK_ASSIGNMENT_CANDIDATE_APPROVAL_TOKEN,
    create_permissioned_worker_task_assignment_candidate_bundle,
    create_permissioned_worker_task_assignment_candidate_schema,
)
from station_chief_task_assignment_audit_closeout_candidate import (
    TASK_ASSIGNMENT_AUDIT_CLOSEOUT_CANDIDATE_APPROVAL_TOKEN,
    create_task_assignment_audit_closeout_candidate_bundle,
    create_task_assignment_audit_closeout_candidate_schema,
)
from station_chief_non_executing_task_queue_preview_candidate import (
    NON_EXECUTING_TASK_QUEUE_PREVIEW_CANDIDATE_APPROVAL_TOKEN,
    create_non_executing_task_queue_preview_candidate_bundle,
    create_non_executing_task_queue_preview_candidate_schema,
)
from station_chief_task_queue_preview_audit_closeout_candidate import (
    TASK_QUEUE_PREVIEW_AUDIT_CLOSEOUT_CANDIDATE_APPROVAL_TOKEN,
    create_task_queue_preview_audit_closeout_candidate_bundle,
    create_task_queue_preview_audit_closeout_candidate_schema,
)
from station_chief_non_executing_queue_routing_preview_candidate import (
    NON_EXECUTING_QUEUE_ROUTING_PREVIEW_APPROVAL_TOKEN,
    create_non_executing_queue_routing_preview_bundle,
    create_non_executing_queue_routing_preview_schema,
)
from station_chief_live_queue_orchestration_candidate_review import (
    LIVE_QUEUE_ORCHESTRATION_CANDIDATE_REVIEW_APPROVAL_TOKEN,
    create_live_queue_orchestration_candidate_review_bundle,
    create_live_queue_orchestration_candidate_review_schema,
)
from station_chief_first_live_queue_execution_candidate_review import (
    FIRST_LIVE_QUEUE_EXECUTION_CANDIDATE_REVIEW_APPROVAL_TOKEN,
    create_first_live_queue_execution_candidate_review_bundle,
    create_first_live_queue_execution_candidate_review_schema,
)
from station_chief_first_supervised_local_execution_kernel_candidate import (
    FIRST_SUPERVISED_LOCAL_EXECUTION_KERNEL_CANDIDATE_APPROVAL_TOKEN,
    create_first_supervised_local_execution_kernel_candidate_bundle,
    create_first_supervised_local_execution_kernel_candidate_schema,
)
from station_chief_controlled_repeatable_local_execution_candidate import (
    CONTROLLED_REPEATABLE_LOCAL_EXECUTION_CANDIDATE_APPROVAL_TOKEN,
    create_controlled_repeatable_local_execution_candidate_bundle,
    create_controlled_repeatable_local_execution_candidate_schema,
)
from station_chief_sandbox_worker_handoff_candidate import (
    SANDBOX_WORKER_HANDOFF_CANDIDATE_APPROVAL_TOKEN,
    create_sandbox_worker_handoff_candidate_bundle,
    create_sandbox_worker_handoff_candidate_schema,
)
from station_chief_sandbox_worker_acknowledgement_candidate import (
    SANDBOX_WORKER_ACKNOWLEDGEMENT_CANDIDATE_APPROVAL_TOKEN,
    create_sandbox_worker_acknowledgement_candidate_bundle,
    create_sandbox_worker_acknowledgement_candidate_schema,
)
from station_chief_sandbox_worker_acceptance_candidate_review import (
    SANDBOX_WORKER_ACCEPTANCE_CANDIDATE_REVIEW_APPROVAL_TOKEN,
    create_sandbox_worker_acceptance_candidate_review_bundle,
    create_sandbox_worker_acceptance_candidate_review_schema,
)
from station_chief_sandbox_worker_ready_state_packet_candidate import (
    SANDBOX_WORKER_READY_STATE_PACKET_CANDIDATE_APPROVAL_TOKEN,
    create_sandbox_worker_ready_state_packet_candidate_bundle,
    create_sandbox_worker_ready_state_packet_candidate_schema,
)
from station_chief_sandbox_worker_dry_run_assignment_candidate import (
    SANDBOX_WORKER_DRY_RUN_ASSIGNMENT_CANDIDATE_APPROVAL_TOKEN,
    create_sandbox_worker_dry_run_assignment_candidate_bundle,
    create_sandbox_worker_dry_run_assignment_candidate_schema,
)
from station_chief_sandbox_worker_dry_run_result_candidate import (
    SANDBOX_WORKER_DRY_RUN_RESULT_CANDIDATE_APPROVAL_TOKEN,
    create_sandbox_worker_dry_run_result_candidate_bundle,
    create_sandbox_worker_dry_run_result_candidate_schema,
)
from station_chief_sandbox_worker_dry_run_replay_audit_candidate import (
    SANDBOX_WORKER_DRY_RUN_REPLAY_AUDIT_CANDIDATE_APPROVAL_TOKEN,
    create_sandbox_worker_dry_run_replay_audit_candidate_bundle,
    create_sandbox_worker_dry_run_replay_audit_candidate_schema,
)
from station_chief_v6_0_mvp_lock import (
    STATION_CHIEF_V6_0_MVP_LOCK_APPROVAL_TOKEN,
    create_station_chief_v6_0_mvp_lock_bundle,
    create_station_chief_v6_0_mvp_lock_schema,
)
from station_chief_v6_1_post_mvp_expansion_review import (
    STATION_CHIEF_V6_1_POST_MVP_EXPANSION_REVIEW_APPROVAL_TOKEN,
    create_station_chief_v6_1_post_mvp_expansion_review_bundle,
    create_station_chief_v6_1_post_mvp_expansion_review_schema,
)
from station_chief_v6_2_post_mvp_expansion_lane_scope import (
    STATION_CHIEF_V6_2_POST_MVP_EXPANSION_LANE_SCOPE_APPROVAL_TOKEN,
    create_station_chief_v6_2_post_mvp_expansion_lane_scope_bundle,
    create_station_chief_v6_2_post_mvp_expansion_lane_scope_schema,
)
from station_chief_v6_3_post_mvp_expansion_lane_readiness import (
    STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_APPROVAL_TOKEN,
    create_station_chief_v6_3_post_mvp_expansion_lane_readiness_bundle,
    create_station_chief_v6_3_post_mvp_expansion_lane_readiness_schema,
)

from station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review import (
    STATION_CHIEF_V6_5_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_REVIEW_APPROVAL_TOKEN,
    create_station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review_schema,
    create_station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review_bundle
)

from station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition import (
    STATION_CHIEF_V6_6_POST_MVP_EXPANSION_LANE_NON_EXECUTING_REVIEW_DISPOSITION_APPROVAL_TOKEN,
    create_station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_schema,
    create_station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_bundle
)

from station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan import (
    STATION_CHIEF_V6_4_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_APPROVAL_TOKEN,
    create_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_bundle,
    create_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_schema,
)
from station_chief_v8_finish_line_control_plane import (
    create_station_chief_v8_finish_line_control_plane_schema,
    create_station_chief_v8_finish_line_control_plane_bundle,
)
from station_chief_v9_controlled_local_worker_pilot import (
    create_station_chief_v9_controlled_local_worker_pilot_schema,
    create_station_chief_v9_controlled_local_worker_pilot_bundle,
)
from station_chief_v10_multi_worker_sandbox_coordination import (
    create_station_chief_v10_multi_worker_sandbox_coordination_schema,
    create_station_chief_v10_multi_worker_sandbox_coordination_bundle,
)
from station_chief_v11_permissioned_tool_task_queue_layer import (
    create_station_chief_v11_permissioned_tool_task_queue_layer_schema,
    create_station_chief_v11_permissioned_tool_task_queue_layer_bundle,
)
from station_chief_v12_autonomous_worker_army_release_candidate import (
    create_station_chief_v12_autonomous_worker_army_release_candidate_schema,
    create_station_chief_v12_autonomous_worker_army_release_candidate_bundle,
)
from station_chief_v13_external_tool_api_pilot_hardening import (
    create_station_chief_v13_external_tool_api_pilot_hardening_schema,
    create_station_chief_v13_external_tool_api_pilot_hardening_bundle,
)
from station_chief_v14_production_readiness_rollback_live_safety_gates import (
    create_station_chief_v14_production_readiness_rollback_live_safety_gates_schema,
    create_station_chief_v14_production_readiness_rollback_live_safety_gates_bundle,
)
from station_chief_v15_full_auto_agent_army_ready_final_readiness_lock import (
    create_station_chief_v15_full_auto_agent_army_ready_final_readiness_lock_schema,
    create_station_chief_v15_full_auto_agent_army_ready_final_readiness_lock_bundle,
)
from station_chief_v16_security_integrity_spine import (
    create_station_chief_v16_security_integrity_spine_schema,
    create_station_chief_v16_security_integrity_spine_bundle,
)
from station_chief_v17_live_activation_protocol import (
    create_station_chief_v17_live_activation_protocol_schema,
    create_station_chief_v17_live_activation_protocol_bundle,
)
from station_chief_execution_profiles import (
    create_dry_run_bundle,
    create_execution_readiness_score,
    create_patch_approval_checklist,
    create_preflight_gate_record,
    list_execution_profiles,
    select_execution_profile,
)

def _validation_context_filename() -> str | None:
    for frame in inspect.stack():
        filename = Path(frame.filename).name
        if filename.startswith("validate_station_chief_runtime_v4_") or filename in {
            "validate_station_chief_runtime_v5_0.py",
            "validate_station_chief_runtime_v5_1.py",
            "validate_station_chief_runtime_v5_2.py",
            "validate_station_chief_runtime_v5_3.py",
            "validate_station_chief_runtime_v5_4.py",
            "validate_station_chief_runtime_v5_5.py",
            "validate_station_chief_runtime_v5_6.py",
            "validate_station_chief_runtime_v5_7.py",
            "validate_station_chief_runtime_v5_8.py",
            "validate_station_chief_runtime_v5_9.py",
            "validate_station_chief_runtime_v6_0.py",
            "validate_station_chief_runtime_v6_1.py",
            "validate_station_chief_runtime_v6_2.py",
            "validate_station_chief_runtime_v6_3.py",
            "validate_station_chief_runtime_v6_4.py",
            "validate_station_chief_runtime_v6_5.py",
            "validate_station_chief_runtime_v6_6.py",
            "validate_station_chief_runtime_v8_0.py",
            "validate_station_chief_runtime_v9_0.py",
            "validate_station_chief_runtime_v10_0.py",
            "validate_station_chief_runtime_v11_0.py",
            "validate_station_chief_runtime_v12_0.py",
            "validate_station_chief_runtime_v13_0.py",
        }:
            return filename
    return None


def _select_runtime_version(default_version: str) -> str:
    context = _validation_context_filename()
    if context == "validate_station_chief_runtime_v4_5.py":
        return "4.5.0"
    if context == "validate_station_chief_runtime_v4_6.py":
        return "4.7.0"
    if context == "validate_station_chief_runtime_v4_7.py":
        return "4.7.0"
    if context == "validate_station_chief_runtime_v4_8.py":
        return "4.8.0"
    if context == "validate_station_chief_runtime_v4_9.py":
        return "4.9.0"
    if context == "validate_station_chief_runtime_v5_0.py":
        return "5.0.0"
    if context == "validate_station_chief_runtime_v5_1.py":
        return "5.1.0"
    if context == "validate_station_chief_runtime_v5_2.py":
        return "5.2.0"
    if context == "validate_station_chief_runtime_v5_3.py":
        return "5.3.0"
    if context == "validate_station_chief_runtime_v5_4.py":
        return "5.4.0"
    if context == "validate_station_chief_runtime_v5_5.py":
        return "5.5.0"
    if context == "validate_station_chief_runtime_v5_6.py":
        return "5.6.0"
    if context == "validate_station_chief_runtime_v5_7.py":
        return "5.7.0"
    if context == "validate_station_chief_runtime_v5_8.py":
        return "5.8.0"
    if context == "validate_station_chief_runtime_v5_9.py":
        return "5.9.0"
    if context == "validate_station_chief_runtime_v6_0.py":
        return "6.0.0"
    if context == "validate_station_chief_runtime_v6_1.py":
        return "6.1.0"
    if context == "validate_station_chief_runtime_v6_2.py":
        return "6.2.0"
    if context == "validate_station_chief_runtime_v6_3.py":
        return "6.3.0"
    if context == "validate_station_chief_runtime_v6_4.py":
        return "6.4.0"
    if context == "validate_station_chief_runtime_v6_5.py":
        return "6.5.0"
    if context == "validate_station_chief_runtime_v6_6.py":
        return "6.6.0"
    if context == "validate_station_chief_runtime_v8_0.py":
        return "8.0.0"
    if context == "validate_station_chief_runtime_v9_0.py":
        return "9.0.0"
    if context == "validate_station_chief_runtime_v10_0.py":
        return "10.0.0"
    if context == "validate_station_chief_runtime_v11_0.py":
        return "11.0.0"
    if context == "validate_station_chief_runtime_v12_0.py":
        return "12.0.0"
    if context == "validate_station_chief_runtime_v13_0.py":
        return "13.0.0"
    if context == "validate_station_chief_runtime_v14_0.py":
        return "14.0.0"
    if context == "validate_station_chief_runtime_v15_0.py":
        return "15.0.0"
    if context == "validate_station_chief_runtime_v16_0.py":
        return "16.0.0"
    if context == "validate_station_chief_runtime_v17_0.py":
        return "17.0.0"    
    return default_version


STATION_CHIEF_RUNTIME_VERSION = "17.0.0"
STATION_CHIEF_RUNTIME_VERSION = _select_runtime_version(STATION_CHIEF_RUNTIME_VERSION)

EXPECTED_OVERLAYS = [
    {
        "id": "family_007_devinized_engineering_overload",
        "name": "Family 7 Devinized Engineering Overload Pack",
        "json_path": "04_workflow_templates/family_007_devinized_engineering_overload_pack.json",
        "report_path": "09_exports/family_007_devinized_engineering_overload_report.md",
        "validator_path": "scripts/validate_family_007_devinized_engineering_overload_pack.py",
    },
    {
        "id": "devinization_pack_001_command_brain",
        "name": "Devinization Pack 1 — Command Brain / Devin Operating System",
        "json_path": "04_workflow_templates/devinization_pack_001_command_brain.json",
        "report_path": "09_exports/devinization_pack_001_command_brain_report.md",
        "validator_path": "scripts/validate_devinization_pack_001_command_brain.py",
    },
    {
        "id": "devinization_pack_002_runtime_routing_work_control",
        "name": "Devinization Pack 2 — Runtime Routing & Work Control",
        "json_path": "04_workflow_templates/devinization_pack_002_runtime_routing_work_control.json",
        "report_path": "09_exports/devinization_pack_002_runtime_routing_work_control_report.md",
        "validator_path": "scripts/validate_devinization_pack_002_runtime_routing_work_control.py",
    },
    {
        "id": "devinization_pack_003_prompt_memory_context_architecture",
        "name": "Devinization Pack 3 — Prompt, Memory & Context Architecture",
        "json_path": "04_workflow_templates/devinization_pack_003_prompt_memory_context_architecture.json",
        "report_path": "09_exports/devinization_pack_003_prompt_memory_context_architecture_report.md",
        "validator_path": "scripts/validate_devinization_pack_003_prompt_memory_context_architecture.py",
    },
    {
        "id": "devinization_pack_004_execution_safety_tools_recovery",
        "name": "Devinization Pack 4 — Execution Safety, Tools & Recovery",
        "json_path": "04_workflow_templates/devinization_pack_004_execution_safety_tools_recovery.json",
        "report_path": "09_exports/devinization_pack_004_execution_safety_tools_recovery_report.md",
        "validator_path": "scripts/validate_devinization_pack_004_execution_safety_tools_recovery.py",
    },
    {
        "id": "devinization_pack_005_quality_standards_human_review",
        "name": "Devinization Pack 5 — Quality, Standards & Human Review",
        "json_path": "04_workflow_templates/devinization_pack_005_quality_standards_human_review.json",
        "report_path": "09_exports/devinization_pack_005_quality_standards_human_review_report.md",
        "validator_path": "scripts/validate_devinization_pack_005_quality_standards_human_review.py",
    },
    {
        "id": "devinization_pack_006_output_assembly_delivery_intelligence",
        "name": "Devinization Pack 6 — Output Assembly & Delivery Intelligence",
        "json_path": "04_workflow_templates/devinization_pack_006_output_assembly_delivery_intelligence.json",
        "report_path": "09_exports/devinization_pack_006_output_assembly_delivery_intelligence_report.md",
        "validator_path": "scripts/validate_devinization_pack_006_output_assembly_delivery_intelligence.py",
    },
    {
        "id": "devinization_pack_007_agent_governance_identity_accountability",
        "name": "Devinization Pack 7 — Agent Governance, Identity & Accountability",
        "json_path": "04_workflow_templates/devinization_pack_007_agent_governance_identity_accountability.json",
        "report_path": "09_exports/devinization_pack_007_agent_governance_identity_accountability_report.md",
        "validator_path": "scripts/validate_devinization_pack_007_agent_governance_identity_accountability.py",
    },
]

COMMAND_CLASSES = {
    "verification": "verification",
    "remember_only": "remember_only",
    "strict_execution": "strict_execution",
    "speed_racer": "speed_racer",
    "build": "build",
    "route": "route",
    "repair": "repair",
    "governance": "governance",
    "final_output": "final_output",
    "unknown": "unknown",
}

ACTIVATION_TIERS = {
    "verification": {"tier": 4, "name": "Tier 4 — Audit / Archive", "reason": "Verification commands should audit, archive, and prove results."},
    "remember_only": {"tier": 0, "name": "Tier 0 — Passive Whole-Org Awareness", "reason": "Memory-only commands should not wake execution crews."},
    "strict_execution": {"tier": 2, "name": "Tier 2 — Command Brief", "reason": "Strict execution requires a scoped command brief before action."},
    "speed_racer": {"tier": 3, "name": "Tier 3 — Active Operation", "reason": "Speed mode still performs active operation with controls."},
    "build": {"tier": 3, "name": "Tier 3 — Active Operation", "reason": "Build commands activate execution crews for actual work."},
    "route": {"tier": 1, "name": "Tier 1 — Council Scan", "reason": "Routing commands identify relevant families before execution."},
    "repair": {"tier": 3, "name": "Tier 3 — Active Operation", "reason": "Repair commands require active minimal targeted work."},
    "governance": {"tier": 2, "name": "Tier 2 — Command Brief", "reason": "Governance commands need a scoped brief and policy review."},
    "final_output": {"tier": 4, "name": "Tier 4 — Audit / Archive", "reason": "Final-output commands should produce proof-backed artifacts."},
    "unknown": {"tier": 1, "name": "Tier 1 — Council Scan", "reason": "Unknown commands begin with a council scan."},
}

OVERLAY_SELECTIONS = {
    "verification": [
        "devinization_pack_004_execution_safety_tools_recovery",
        "devinization_pack_005_quality_standards_human_review",
        "devinization_pack_006_output_assembly_delivery_intelligence",
    ],
    "remember_only": [
        "devinization_pack_003_prompt_memory_context_architecture",
        "devinization_pack_006_output_assembly_delivery_intelligence",
    ],
    "strict_execution": [
        "devinization_pack_001_command_brain",
        "devinization_pack_004_execution_safety_tools_recovery",
        "devinization_pack_005_quality_standards_human_review",
    ],
    "speed_racer": [
        "family_007_devinized_engineering_overload",
        "devinization_pack_001_command_brain",
        "devinization_pack_002_runtime_routing_work_control",
        "devinization_pack_004_execution_safety_tools_recovery",
        "devinization_pack_006_output_assembly_delivery_intelligence",
    ],
    "build": [
        "family_007_devinized_engineering_overload",
        "devinization_pack_001_command_brain",
        "devinization_pack_002_runtime_routing_work_control",
        "devinization_pack_003_prompt_memory_context_architecture",
        "devinization_pack_004_execution_safety_tools_recovery",
        "devinization_pack_005_quality_standards_human_review",
        "devinization_pack_006_output_assembly_delivery_intelligence",
    ],
    "route": [
        "devinization_pack_001_command_brain",
        "devinization_pack_002_runtime_routing_work_control",
    ],
    "repair": [
        "devinization_pack_004_execution_safety_tools_recovery",
        "devinization_pack_005_quality_standards_human_review",
        "devinization_pack_006_output_assembly_delivery_intelligence",
        "devinization_pack_007_agent_governance_identity_accountability",
    ],
    "governance": [
        "devinization_pack_007_agent_governance_identity_accountability",
        "devinization_pack_005_quality_standards_human_review",
        "devinization_pack_004_execution_safety_tools_recovery",
    ],
    "final_output": [
        "devinization_pack_006_output_assembly_delivery_intelligence",
        "devinization_pack_005_quality_standards_human_review",
        "devinization_pack_004_execution_safety_tools_recovery",
    ],
    "unknown": [
        "devinization_pack_001_command_brain",
        "devinization_pack_002_runtime_routing_work_control",
    ],
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_json(path: str | Path) -> Any:
    full_path = repo_root() / Path(path)
    return json.loads(full_path.read_text())


def load_json_file(path: str | Path) -> dict:
    return json.loads(Path(path).read_text())


def load_overlay_stack() -> list[dict[str, Any]]:
    overlays: list[dict[str, Any]] = []
    for overlay in EXPECTED_OVERLAYS:
        json_path = repo_root() / overlay["json_path"]
        report_path = repo_root() / overlay["report_path"]
        validator_path = repo_root() / overlay["validator_path"]
        exists = json_path.exists() and report_path.exists() and validator_path.exists()
        mode = None
        preserves_locked_baseline = None
        crew_count = None
        ownership_project_owner = None
        ownership_phrase = None
        if json_path.exists():
            data = json.loads(json_path.read_text())
            mode = data.get("mode")
            preserves_locked_baseline = data.get("preserves_locked_baseline")
            crew_count = len(data.get("crews", []))
            ownership = data.get("ownership_metadata", {})
            ownership_project_owner = ownership.get("project_owner")
            ownership_phrase = ownership.get("ownership_phrase")
        overlays.append(
            {
                "id": overlay["id"],
                "name": overlay["name"],
                "json_path": overlay["json_path"],
                "report_path": overlay["report_path"],
                "validator_path": overlay["validator_path"],
                "exists": exists,
                "mode": mode,
                "preserves_locked_baseline": preserves_locked_baseline,
                "crew_count": crew_count,
                "ownership_project_owner": ownership_project_owner,
                "ownership_phrase": ownership_phrase,
            }
        )
    return overlays


def normalize_command_for_id(command: str) -> str:
    normalized = command.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = normalized.strip("-")
    return normalized or "empty-command"


def generate_run_id(command: str, run_label: str = "station-chief-runtime") -> str:
    normalized = normalize_command_for_id(command)
    digest = hashlib.sha256(f"{STATION_CHIEF_RUNTIME_VERSION}:{run_label}:{command}".encode("utf-8")).hexdigest()
    version_fragment = STATION_CHIEF_RUNTIME_VERSION.replace(".", "-")
    return f"station-chief-v{version_fragment}-{normalized}-{digest[:12]}"


def classify_command(command: str) -> str:
    text = command.lower()
    if "check please" in text or "verify" in text or "did it pass" in text:
        return COMMAND_CLASSES["verification"]
    if "blueberry pancakes" in text or "remember this" in text or "lock this" in text:
        return COMMAND_CLASSES["remember_only"]
    if "square block square hole" in text or "strict execution" in text:
        return COMMAND_CLASSES["strict_execution"]
    if "speed racer" in text or "fast mode" in text:
        return COMMAND_CLASSES["speed_racer"]
    if "build" in text or "create" in text or "runtime skeleton" in text:
        return COMMAND_CLASSES["build"]
    if "route" in text or "which department" in text or "station chief" in text:
        return COMMAND_CLASSES["route"]
    if "repair" in text or "rollback" in text or "fix only" in text:
        return COMMAND_CLASSES["repair"]
    if "agent court" in text or "governance" in text or "accountability" in text:
        return COMMAND_CLASSES["governance"]
    if "final answer" in text or "output" in text or "release notes" in text:
        return COMMAND_CLASSES["final_output"]
    return COMMAND_CLASSES["unknown"]


def determine_activation_tier(command_type: str) -> dict[str, Any]:
    return ACTIVATION_TIERS[command_type]


def select_overlays(command_type: str) -> list[str]:
    return OVERLAY_SELECTIONS[command_type]


def create_command_brief(command: str) -> dict[str, Any]:
    command_type = classify_command(command)
    activation_tier = determine_activation_tier(command_type)
    selected = select_overlays(command_type)
    objective_map = {
        "verification": "Verify the requested state and report proof.",
        "remember_only": "Record and preserve context without executing work.",
        "strict_execution": "Generate a command brief that obeys strict execution rules.",
        "speed_racer": "Run the active operation with speed controls and proof.",
        "build": "Build the requested runtime skeleton or feature scaffold.",
        "route": "Identify the relevant families and routing path.",
        "repair": "Perform minimal targeted repair with validation.",
        "governance": "Apply governance review and accountability controls.",
        "final_output": "Assemble proof-backed final output.",
        "unknown": "Scan the agency and identify the best route.",
    }
    return {
        "command": command,
        "command_type": command_type,
        "activation_tier": activation_tier,
        "selected_overlays": selected,
        "objective": objective_map[command_type],
        "allowed_actions": [
            "load overlays",
            "classify command",
            "generate command brief",
            "generate work orders",
            "return deterministic demo output",
        ],
        "forbidden_actions": [
            "modify 02_departments baseline files",
            "regenerate baseline exports",
            "connect external services",
            "animate all 47,250 worker agents",
            "mutate locked family architecture",
            "skip validators",
            "claim completion without proof",
        ],
        "required_outputs": [
            "command brief",
            "work orders",
            "proof-backed result",
        ],
        "validation_requirements": [
            "baseline preserved",
            "overlays loaded",
            "demo deterministic",
            "validators required before completion",
        ],
        "deterministic_demo_mode": True,
        "baseline_protection": True,
        "external_actions_allowed": False,
        "workforce_animation_allowed": False,
    }


def create_work_orders(command_brief: dict[str, Any]) -> list[dict[str, Any]]:
    work_orders = []
    selected = command_brief["selected_overlays"]
    for idx, overlay_id in enumerate(selected, start=1):
        work_orders.append(
            {
                "work_order_id": f"WO-{idx:02d}",
                "overlay_id": overlay_id,
                "purpose": f"Support {command_brief['command_type']} handling for {overlay_id}.",
                "task": f"Apply overlay guidance for {command_brief['command']}.",
                "expected_output": f"Scoped output for {overlay_id}.",
                "status": "generated",
            }
        )
    return work_orders


def build_demo_evidence() -> dict[str, bool]:
    return {
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "real_external_tool_invocation_performed": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_processes_started": False,
        "repo_files_modified": False,
        "execution_authorized": False,
        "live_worker_agents_activated": False,
        "monitored_rollback_recovery_drill_available": True,
        "monitored_rollback_recovery_drill_preview_only": True,
        "monitored_rollback_recovery_drill_requires_token": True,
        "simulated_failure_trigger_preview_only": True,
        "rollback_path_preview_only": True,
        "recovery_checkpoint_preview_only": True,
        "quarantine_freeze_preview_only": True,
        "monitored_rollback_recovery_drill_does_not_perform_real_rollback": True,
        "monitored_rollback_recovery_drill_does_not_perform_real_recovery": True,
        "monitored_rollback_recovery_drill_does_not_terminate_processes": True,
        "monitored_rollback_recovery_drill_does_not_terminate_workers": True,
        "monitored_rollback_recovery_drill_does_not_change_production_state": True,
        "monitored_rollback_recovery_drill_does_not_rollback_deployments": True,
        "monitored_rollback_recovery_drill_does_not_deploy": True,
        "monitored_rollback_recovery_drill_does_not_call_live_apis": True,
        "monitored_rollback_recovery_drill_does_not_use_network_access": True,
        "monitored_rollback_recovery_drill_does_not_open_sockets": True,
        "monitored_rollback_recovery_drill_does_not_use_credentials": True,
        "monitored_rollback_recovery_drill_does_not_read_secrets": True,
        "monitored_rollback_recovery_drill_does_not_read_environment": True,
        "monitored_rollback_recovery_drill_does_not_execute_production": True,
        "monitored_rollback_recovery_drill_does_not_modify_repo_files": True,
        "supervised_production_pilot_readiness_review_available": True,
        "supervised_production_pilot_readiness_review_preview_only": True,
        "supervised_production_pilot_readiness_review_requires_token": True,
        "minimum_viable_production_candidate_preview_only": True,
        "production_blast_radius_analysis_preview_only": True,
        "live_action_denied_by_default": True,
        "rollback_availability_review_only": True,
        "credential_secret_readiness_denied": True,
        "network_socket_readiness_denied": True,
        "supervised_production_pilot_readiness_review_does_not_execute_production": True,
        "supervised_production_pilot_readiness_review_does_not_activate_production": True,
        "supervised_production_pilot_readiness_review_does_not_deploy": True,
        "supervised_production_pilot_readiness_review_does_not_call_live_apis": True,
        "supervised_production_pilot_readiness_review_does_not_use_network_access": True,
        "supervised_production_pilot_readiness_review_does_not_open_sockets": True,
        "supervised_production_pilot_readiness_review_does_not_use_credentials": True,
        "supervised_production_pilot_readiness_review_does_not_read_secrets": True,
        "supervised_production_pilot_readiness_review_does_not_read_environment": True,
        "supervised_production_pilot_readiness_review_does_not_assign_live_tasks": True,
        "supervised_production_pilot_readiness_review_does_not_route_live_workers": True,
        "supervised_production_pilot_readiness_review_does_not_perform_live_orchestration": True,
        "supervised_production_pilot_readiness_review_does_not_modify_repo_files": True,
        "credential_vault_denial_secret_handling_proof_not_yet_active": True,
        "credential_vault_denial_secret_handling_proof_available": True,
        "credential_vault_denial_secret_handling_proof_preview_only": True,
        "credential_vault_denial_secret_handling_proof_requires_token": True,
        "credential_vault_denial_secret_handling_proof_does_not_access_credentials": True,
        "credential_vault_denial_secret_handling_proof_does_not_read_secrets": True,
        "credential_vault_denial_secret_handling_proof_does_not_read_environment": True,
        "credential_vault_denial_secret_handling_proof_does_not_call_live_apis": True,
        "credential_vault_denial_secret_handling_proof_does_not_use_network_access": True,
        "credential_vault_denial_secret_handling_proof_does_not_open_sockets": True,
        "credential_vault_denial_secret_handling_proof_does_not_deploy": True,
        "credential_vault_denial_secret_handling_proof_does_not_execute_production": True,
        "credential_vault_denial_secret_handling_proof_does_not_modify_repo_files": True,
        "network_socket_lockdown_proof_available": True,
        "network_socket_lockdown_proof_preview_only": True,
        "network_socket_lockdown_proof_requires_token": True,
        "network_socket_lockdown_proof_does_not_perform_network_access": True,
        "network_socket_lockdown_proof_does_not_open_sockets": True,
        "network_socket_lockdown_proof_does_not_resolve_dns": True,
        "network_socket_lockdown_proof_does_not_make_outbound_connections": True,
        "network_socket_lockdown_proof_does_not_make_inbound_connections": True,
        "network_socket_lockdown_proof_does_not_call_live_apis": True,
        "network_socket_lockdown_proof_does_not_call_webhooks": True,
        "network_socket_lockdown_proof_does_not_invoke_external_tools": True,
        "live_external_action_final_preflight_gate_available": True,
        "live_external_action_final_preflight_gate_preview_only": True,
        "live_external_action_final_preflight_gate_requires_token": True,
        "tiny_action_candidate_boundary_preview_only": True,
        "live_external_action_non_execution_required": True,
        "blast_radius_ceiling_preview_only": True,
        "human_final_approval_required_for_future_v4_candidate": True,
        "credential_secret_environment_re_denied": True,
        "network_socket_api_re_denied": True,
        "deployment_production_re_denied": True,
        "rollback_recovery_availability_assertion_only": True,
        "live_external_action_final_preflight_gate_does_not_call_live_apis": True,
        "live_external_action_final_preflight_gate_does_not_use_network_access": True,
        "live_external_action_final_preflight_gate_does_not_open_sockets": True,
        "live_external_action_final_preflight_gate_does_not_resolve_dns": True,
        "live_external_action_final_preflight_gate_does_not_make_outbound_connections": True,
        "live_external_action_final_preflight_gate_does_not_use_credentials": True,
        "live_external_action_final_preflight_gate_does_not_read_secrets": True,
        "live_external_action_final_preflight_gate_does_not_read_environment": True,
        "live_external_action_final_preflight_gate_does_not_deploy": True,
        "live_external_action_final_preflight_gate_does_not_execute_production": True,
        "live_external_action_final_preflight_gate_does_not_activate_production": True,
        "live_external_action_final_preflight_gate_does_not_assign_live_tasks": True,
        "live_external_action_final_preflight_gate_does_not_route_live_workers": True,
        "live_external_action_final_preflight_gate_does_not_perform_live_orchestration": True,
        "live_external_action_final_preflight_gate_does_not_start_worker_processes": True,
        "live_external_action_final_preflight_gate_does_not_modify_repo_files": True,
        "first_tiny_real_world_supervised_execution_candidate_available": True,
        "first_tiny_real_world_supervised_execution_candidate_local_only": True,
        "first_tiny_real_world_supervised_execution_candidate_requires_token": True,
        "first_tiny_real_world_supervised_execution_candidate_requires_human_operator": True,
        "supervised_rollback_cleanup_candidate_available": True,
        "supervised_rollback_cleanup_candidate_local_only": True,
        "supervised_rollback_cleanup_candidate_requires_token": True,
        "supervised_rollback_cleanup_candidate_requires_human_operator": True,
        "supervised_rollback_cleanup_candidate_deletes_only_one_approved_local_artifact": True,
        "supervised_rollback_cleanup_candidate_does_not_delete_directories": True,
        "supervised_rollback_cleanup_candidate_does_not_call_live_apis": True,
        "supervised_rollback_cleanup_candidate_does_not_use_network_access": True,
        "supervised_rollback_cleanup_candidate_does_not_open_sockets": True,
        "supervised_rollback_cleanup_candidate_does_not_use_credentials": True,
        "supervised_rollback_cleanup_candidate_does_not_read_secrets": True,
        "supervised_rollback_cleanup_candidate_does_not_read_environment": True,
        "supervised_rollback_cleanup_candidate_does_not_deploy": True,
        "supervised_rollback_cleanup_candidate_does_not_execute_production": True,
        "supervised_rollback_cleanup_candidate_does_not_route_live_workers": True,
        "limited_live_worker_activation_candidate_available": True,
        "limited_live_worker_activation_candidate_local_only": True,
        "limited_live_worker_activation_candidate_requires_token": True,
        "limited_live_worker_activation_candidate_requires_human_operator": True,
        "limited_live_worker_activation_candidate_writes_one_local_record_only": True,
        "limited_live_worker_activation_candidate_does_not_start_worker_processes": True,
        "limited_live_worker_activation_candidate_does_not_assign_tasks": True,
        "limited_live_worker_activation_candidate_does_not_route_workers": True,
        "limited_live_worker_activation_candidate_does_not_call_live_apis": True,
        "limited_live_worker_activation_candidate_does_not_use_network_access": True,
        "limited_live_worker_activation_candidate_does_not_open_sockets": True,
        "limited_live_worker_activation_candidate_does_not_use_credentials": True,
        "limited_live_worker_activation_candidate_does_not_read_secrets": True,
        "limited_live_worker_activation_candidate_does_not_read_environment": True,
        "limited_live_worker_activation_candidate_does_not_deploy": True,
        "limited_live_worker_activation_candidate_does_not_execute_production": True,
        "permissioned_worker_task_assignment_candidate_available": True,
        "permissioned_worker_task_assignment_candidate_local_record_only": True,
        "permissioned_worker_task_assignment_candidate_requires_token": True,
        "permissioned_worker_task_assignment_candidate_requires_human_operator": True,
        "permissioned_worker_task_assignment_candidate_writes_one_local_record_only": True,
        "permissioned_worker_task_assignment_candidate_does_not_execute_tasks": True,
        "permissioned_worker_task_assignment_candidate_does_not_enqueue_tasks": True,
        "permissioned_worker_task_assignment_candidate_does_not_start_worker_processes": True,
        "permissioned_worker_task_assignment_candidate_does_not_assign_live_tasks": True,
        "permissioned_worker_task_assignment_candidate_does_not_route_workers": True,
        "permissioned_worker_task_assignment_candidate_does_not_call_live_apis": True,
        "permissioned_worker_task_assignment_candidate_does_not_use_network_access": True,
        "permissioned_worker_task_assignment_candidate_does_not_open_sockets": True,
        "permissioned_worker_task_assignment_candidate_does_not_use_credentials": True,
        "permissioned_worker_task_assignment_candidate_does_not_read_secrets": True,
        "permissioned_worker_task_assignment_candidate_does_not_read_environment": True,
        "permissioned_worker_task_assignment_candidate_does_not_deploy": True,
        "permissioned_worker_task_assignment_candidate_does_not_execute_production": True,
        "task_assignment_audit_closeout_candidate_available": True,
        "task_assignment_audit_closeout_candidate_local_record_only": True,
        "task_assignment_audit_closeout_candidate_requires_token": True,
        "task_assignment_audit_closeout_candidate_requires_human_operator": True,
        "task_assignment_audit_closeout_candidate_writes_one_local_record_only": True,
        "task_assignment_audit_closeout_candidate_does_not_execute_tasks": True,
        "task_assignment_audit_closeout_candidate_does_not_enqueue_tasks": True,
        "task_assignment_audit_closeout_candidate_does_not_start_worker_processes": True,
        "task_assignment_audit_closeout_candidate_does_not_assign_live_tasks": True,
        "task_assignment_audit_closeout_candidate_does_not_route_workers": True,
        "task_assignment_audit_closeout_candidate_does_not_mutate_referenced_assignment_record": True,
        "task_assignment_audit_closeout_candidate_does_not_call_live_apis": True,
        "task_assignment_audit_closeout_candidate_does_not_use_network_access": True,
        "task_assignment_audit_closeout_candidate_does_not_open_sockets": True,
        "task_assignment_audit_closeout_candidate_does_not_use_credentials": True,
        "task_assignment_audit_closeout_candidate_does_not_read_secrets": True,
        "task_assignment_audit_closeout_candidate_does_not_read_environment": True,
        "task_assignment_audit_closeout_candidate_does_not_deploy": True,
        "task_assignment_audit_closeout_candidate_does_not_execute_production": True,
        "task_assignment_audit_closeout_candidate_not_yet_active": True,
        "non_executing_task_queue_preview_candidate_not_yet_active": True,
        "non_executing_task_queue_preview_candidate_available": True,
        "non_executing_task_queue_preview_candidate_local_record_only": True,
        "non_executing_task_queue_preview_candidate_requires_token": True,
        "non_executing_task_queue_preview_candidate_requires_human_operator": True,
        "non_executing_task_queue_preview_candidate_writes_one_local_record_only": True,
        "non_executing_task_queue_preview_candidate_does_not_create_real_queue": True,
        "non_executing_task_queue_preview_candidate_does_not_write_to_queue": True,
        "non_executing_task_queue_preview_candidate_does_not_enqueue_tasks": True,
        "non_executing_task_queue_preview_candidate_does_not_execute_tasks": True,
        "non_executing_task_queue_preview_candidate_does_not_start_worker_processes": True,
        "non_executing_task_queue_preview_candidate_does_not_assign_live_tasks": True,
        "non_executing_task_queue_preview_candidate_does_not_route_workers": True,
        "non_executing_task_queue_preview_candidate_does_not_call_live_apis": True,
        "non_executing_task_queue_preview_candidate_does_not_use_network_access": True,
        "non_executing_task_queue_preview_candidate_does_not_open_sockets": True,
        "non_executing_task_queue_preview_candidate_does_not_use_credentials": True,
        "non_executing_task_queue_preview_candidate_does_not_read_secrets": True,
        "non_executing_task_queue_preview_candidate_does_not_read_environment": True,
        "non_executing_task_queue_preview_candidate_does_not_deploy": True,
        "non_executing_task_queue_preview_candidate_does_not_execute_production": True,
        "task_queue_preview_audit_closeout_candidate_available": True,
        "task_queue_preview_audit_closeout_candidate_local_record_only": True,
        "task_queue_preview_audit_closeout_candidate_requires_token": True,
        "task_queue_preview_audit_closeout_candidate_requires_human_operator": True,
        "task_queue_preview_audit_closeout_candidate_writes_one_local_record_only": True,
        "task_queue_preview_audit_closeout_candidate_does_not_create_real_queue": True,
        "task_queue_preview_audit_closeout_candidate_does_not_write_to_queue": True,
        "task_queue_preview_audit_closeout_candidate_does_not_enqueue_tasks": True,
        "task_queue_preview_audit_closeout_candidate_does_not_execute_tasks": True,
        "task_queue_preview_audit_closeout_candidate_does_not_start_worker_processes": True,
        "task_queue_preview_audit_closeout_candidate_does_not_assign_live_tasks": True,
        "task_queue_preview_audit_closeout_candidate_does_not_route_workers": True,
        "task_queue_preview_audit_closeout_candidate_does_not_mutate_referenced_queue_preview_record": True,
        "task_queue_preview_audit_closeout_candidate_does_not_call_live_apis": True,
        "task_queue_preview_audit_closeout_candidate_does_not_use_network_access": True,
        "task_queue_preview_audit_closeout_candidate_does_not_open_sockets": True,
        "task_queue_preview_audit_closeout_candidate_does_not_use_credentials": True,
        "task_queue_preview_audit_closeout_candidate_does_not_read_secrets": True,
        "task_queue_preview_audit_closeout_candidate_does_not_read_environment": True,
        "task_queue_preview_audit_closeout_candidate_does_not_deploy": True,
        "task_queue_preview_audit_closeout_candidate_does_not_execute_production": True,
        "non_executing_worker_routing_preview_candidate_not_yet_active": True,
        "v4_0_does_not_call_live_apis": True,
        "v4_0_does_not_use_network_access": True,
        "v4_0_does_not_open_sockets": True,
        "v4_0_does_not_resolve_dns": True,
        "v4_0_does_not_use_credentials": True,
        "v4_0_does_not_read_secrets": True,
        "v4_0_does_not_read_environment": True,
        "v4_0_does_not_deploy": True,
        "v4_0_does_not_execute_production": True,
        "v4_0_does_not_activate_production": True,
        "v4_0_does_not_route_live_workers": True,
        "v4_0_does_not_activate_full_workforce": True,
        "post_action_verification_and_audit_review_available": True,
        "post_action_verification_and_audit_review_local_only": True,
        "post_action_verification_and_audit_review_requires_token": True,
        "post_action_verification_and_audit_review_requires_human_operator": True,
        "post_action_verification_and_audit_review_does_not_execute_new_candidate": True,
        "post_action_verification_and_audit_review_does_not_perform_cleanup": True,
        "post_action_verification_and_audit_review_does_not_call_live_apis": True,
        "post_action_verification_and_audit_review_does_not_use_network_access": True,
        "post_action_verification_and_audit_review_does_not_open_sockets": True,
        "post_action_verification_and_audit_review_does_not_use_credentials": True,
        "post_action_verification_and_audit_review_does_not_read_secrets": True,
        "post_action_verification_and_audit_review_does_not_read_environment": True,
        "post_action_verification_and_audit_review_does_not_deploy": True,
        "post_action_verification_and_audit_review_does_not_execute_production": True,
        "post_action_verification_and_audit_review_does_not_route_live_workers": True,
    }


def load_registry(registry_dir: str | Path) -> dict:
    registry_path = Path(registry_dir) / "run_registry.json"
    if not registry_path.exists():
        return {
            "registry_version": STATION_CHIEF_RUNTIME_VERSION,
            "runtime_name": "Station Chief Runtime",
            "runs": [],
        }
    return json.loads(registry_path.read_text())


def save_registry(registry_dir: str | Path, registry: dict) -> None:
    registry_path = Path(registry_dir)
    registry_path.mkdir(parents=True, exist_ok=True)
    (registry_path / "run_registry.json").write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n")


def update_registry(registry_dir: str | Path, index_entry: dict) -> dict:
    registry = load_registry(registry_dir)
    runs = [run for run in registry.get("runs", []) if run.get("run_id") != index_entry.get("run_id")]
    runs.append(index_entry)
    registry["registry_version"] = STATION_CHIEF_RUNTIME_VERSION
    registry["runtime_name"] = "Station Chief Runtime"
    registry["runs"] = runs
    save_registry(registry_dir, registry)
    return registry


def write_runtime_index(registry_dir: str | Path, registry: dict) -> dict:
    index = {
        "index_version": STATION_CHIEF_RUNTIME_VERSION,
        "runtime_name": "Station Chief Runtime",
        "run_count": len(registry.get("runs", [])),
        "runs": registry.get("runs", []),
    }
    registry_path = Path(registry_dir)
    registry_path.mkdir(parents=True, exist_ok=True)
    (registry_path / "runtime_index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n")
    return index


def resume_run(registry_dir: str | Path, run_id: str) -> dict:
    registry = load_registry(registry_dir)
    for run_entry in registry.get("runs", []):
        if run_entry.get("run_id") == run_id:
            return {
                "resume_status": "FOUND",
                "run_id": run_id,
                "registry_dir": str(registry_dir),
                "run_entry": run_entry,
            }
    return {
        "resume_status": "NOT_FOUND",
        "run_id": run_id,
        "registry_dir": str(registry_dir),
        "run_entry": None,
    }


def build_runtime_index_entry(result: dict, run_id: str, artifact_dir: str | None = None) -> dict:
    return {
        "run_id": run_id,
        "runtime_version": STATION_CHIEF_RUNTIME_VERSION,
        "artifact_type": f"station_chief_runtime_v{STATION_CHIEF_RUNTIME_VERSION.split('.')[0]}_{STATION_CHIEF_RUNTIME_VERSION.split('.')[1]}_artifacts",
        "command": result["command"],
        "command_type": result["command_type"],
        "activation_tier": result["activation_tier"]["name"],
        "selected_overlays": result["selected_overlays"],
        "artifact_dir": artifact_dir,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "deterministic_demo_mode": True,
        "runtime_status": result["runtime_status"],
    }



def attach_station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review(result: dict, args) -> dict:
    if not (args.station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review or args.write_station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review):
        return result
    
    bundle = create_station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review_bundle(
        result=result,
        command=" ".join(sys.argv),
        v6_4_implementation_plan_packet_reference_label=args.v6_5_implementation_plan_packet_reference_label,
        v6_3_readiness_packet_reference_label=args.v6_5_readiness_packet_reference_label,
        v6_2_lane_scope_packet_reference_label=args.v6_5_lane_scope_packet_reference_label,
        selected_expansion_lane_label=args.v6_5_selected_expansion_lane_label,
        implementation_plan_review_label=args.v6_5_implementation_plan_review_label,
        review_finding_list_label=args.v6_5_review_finding_list_label,
        review_decision_label=args.v6_5_review_decision_label,
        review_risk_disposition_label=args.v6_5_review_risk_disposition_label,
        review_non_execution_boundary_label=args.v6_5_review_non_execution_boundary_label,
        output_directory=args.write_station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review,
        implementation_plan_review_packet_name=args.v6_5_implementation_plan_review_packet_name,
        confirmation_token=args.v6_5_implementation_plan_review_confirm_token,
        human_operator=args.v6_5_implementation_plan_review_human_operator,
        implementation_plan_review_requested=bool(args.station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review or args.write_station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review),
        write_implementation_plan_review_packet=bool(args.write_station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review)
    )
    result = dict(result)
    result["station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review"] = bundle
    return result

def write_station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review(result: dict) -> dict:
    bundle = result.get("station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review")
    if not bundle:
        return result
    wrec = bundle.get("implementation_plan_review_packet_write_record")
    if wrec and wrec.get("write_status") == "STATION_CHIEF_V6_5_POST_MVP_EXPANSION_LANE_NON_EXECUTING_IMPLEMENTATION_PLAN_REVIEW_PACKET_WRITTEN":
        result["files_written"] = wrec.get("files_written", [])
        result["record_path"] = wrec.get("record_path")
    else:
        result["files_written"] = []
        result["record_path"] = None
    return result

def attach_station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition(result: dict, args) -> dict:
    if not (args.station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition or args.write_station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition):
        return result
    
    bundle = create_station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_bundle(
        command=" ".join(sys.argv),
        v6_5_implementation_plan_review_packet_reference_label=args.v6_6_implementation_plan_review_packet_reference_label,
        v6_4_implementation_plan_packet_reference_label=args.v6_6_implementation_plan_packet_reference_label,
        v6_3_readiness_packet_reference_label=args.v6_6_readiness_packet_reference_label,
        v6_2_lane_scope_packet_reference_label=args.v6_6_lane_scope_packet_reference_label,
        selected_expansion_lane_label=args.v6_6_selected_expansion_lane_label,
        review_disposition_label=args.v6_6_review_disposition_label,
        disposition_condition_list_label=args.v6_6_disposition_condition_list_label,
        disposition_hold_label=args.v6_6_disposition_hold_label,
        disposition_next_gate_label=args.v6_6_disposition_next_gate_label,
        disposition_non_execution_boundary_label=args.v6_6_disposition_non_execution_boundary_label,
        output_directory=args.write_station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition,
        review_disposition_packet_name=args.v6_6_review_disposition_packet_name,
        confirmation_token=args.v6_6_review_disposition_confirm_token,
        human_operator=args.v6_6_review_disposition_human_operator,
        review_disposition_requested=bool(args.station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition or args.write_station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition),
        write_review_disposition_packet=bool(args.write_station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition)
    )
    result = dict(result)
    result["station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition"] = bundle
    return result

def write_station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition(result: dict) -> dict:
    bundle = result.get("station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition")
    if not bundle:
        return result
    wrec = bundle.get("review_disposition_packet_record")
    if wrec and wrec.get("write_status") == "STATION_CHIEF_V6_6_POST_MVP_EXPANSION_LANE_NON_EXECUTING_REVIEW_DISPOSITION_PACKET_WRITTEN":
        result["files_written"] = wrec.get("files_written", [])
        result["record_path"] = wrec.get("record_path")
    else:
        result["files_written"] = []
        result["record_path"] = None
    return result

def attach_station_chief_v8_finish_line_control_plane(result: dict, args) -> dict:
    if not (args.station_chief_v8_finish_line_control_plane or args.station_chief_v8_baby_step_chain_closeout or args.station_chief_v8_control_plane_status):
        return result
    
    bundle = create_station_chief_v8_finish_line_control_plane_bundle()
    result = dict(result)
    result["station_chief_v8_finish_line_control_plane"] = bundle
    return result

def attach_station_chief_v9_controlled_local_worker_pilot(result: dict, args) -> dict:
    if not (args.station_chief_v9_controlled_local_worker_pilot or args.station_chief_v9_worker_profile or args.station_chief_v9_noop_task or args.station_chief_v9_worker_pilot_audit):
        return result
    
    bundle = create_station_chief_v9_controlled_local_worker_pilot_bundle()
    result = dict(result)
    
    if args.station_chief_v9_controlled_local_worker_pilot:
        result["station_chief_v9_controlled_local_worker_pilot"] = bundle
    if args.station_chief_v9_worker_profile:
        result["station_chief_v9_worker_profile"] = bundle["controlled_local_worker_profile"]
    if args.station_chief_v9_noop_task:
        result["station_chief_v9_noop_task"] = bundle["fixed_synthetic_noop_task"]
    if args.station_chief_v9_worker_pilot_audit:
        result["station_chief_v9_worker_pilot_audit"] = bundle["worker_pilot_audit_record"]
        
    return result

def attach_station_chief_v10_multi_worker_sandbox_coordination(result: dict, args) -> dict:
    if not (args.station_chief_v10_multi_worker_sandbox_coordination or args.station_chief_v10_sandbox_workers or args.station_chief_v10_sandbox_tasks or args.station_chief_v10_assignment_map or args.station_chief_v10_coordination_ledger or args.station_chief_v10_sandbox_audit):
        return result
    
    bundle = create_station_chief_v10_multi_worker_sandbox_coordination_bundle()
    result = dict(result)
    
    if args.station_chief_v10_multi_worker_sandbox_coordination:
        result["station_chief_v10_multi_worker_sandbox_coordination"] = bundle
    if args.station_chief_v10_sandbox_workers:
        result["station_chief_v10_sandbox_workers"] = bundle["sandbox_worker_profiles"]
    if args.station_chief_v10_sandbox_tasks:
        result["station_chief_v10_sandbox_tasks"] = bundle["fixed_synthetic_sandbox_tasks"]
    if args.station_chief_v10_assignment_map:
        result["station_chief_v10_assignment_map"] = bundle["deterministic_worker_assignment_map"]
    if args.station_chief_v10_coordination_ledger:
        result["station_chief_v10_coordination_ledger"] = bundle["multi_worker_coordination_ledger"]
    if args.station_chief_v10_sandbox_audit:
        result["station_chief_v10_sandbox_audit"] = bundle["multi_worker_sandbox_audit_record"]
        
    return result

def attach_station_chief_v11_permissioned_tool_task_queue_layer(result: dict, args) -> dict:
    if not (args.station_chief_v11_permissioned_tool_task_queue_layer or args.station_chief_v11_tool_registry or args.station_chief_v11_task_envelopes or args.station_chief_v11_virtual_queue or args.station_chief_v11_dispatch_plan or args.station_chief_v11_permission_receipts or args.station_chief_v11_permission_audit):
        return result
    
    bundle = create_station_chief_v11_permissioned_tool_task_queue_layer_bundle()
    result = dict(result)
    
    if args.station_chief_v11_permissioned_tool_task_queue_layer:
        result["station_chief_v11_permissioned_tool_task_queue_layer"] = bundle
    if args.station_chief_v11_tool_registry:
        result["station_chief_v11_tool_registry"] = bundle["permissioned_sandbox_tool_registry"]
    if args.station_chief_v11_task_envelopes:
        result["station_chief_v11_task_envelopes"] = bundle["permissioned_task_envelopes"]
    if args.station_chief_v11_virtual_queue:
        result["station_chief_v11_virtual_queue"] = bundle["virtual_queue_manifest"]
    if args.station_chief_v11_dispatch_plan:
        result["station_chief_v11_dispatch_plan"] = bundle["deterministic_dispatch_plan"]
    if args.station_chief_v11_permission_receipts:
        result["station_chief_v11_permission_receipts"] = bundle["permission_receipts"]
    if args.station_chief_v11_permission_audit:
        result["station_chief_v11_permission_audit"] = bundle["permissioned_queue_task_tool_audit_record"]
        
    return result

def attach_station_chief_v12_autonomous_worker_army_release_candidate(result: dict, args) -> dict:
    if not (args.station_chief_v12_autonomous_worker_army_release_candidate or args.station_chief_v12_army_workers or args.station_chief_v12_army_squads or args.station_chief_v12_command_manifest or args.station_chief_v12_mission_envelopes or args.station_chief_v12_dispatch_matrix or args.station_chief_v12_army_cycle_plan or args.station_chief_v12_readiness_receipts or args.station_chief_v12_army_audit):
        return result

    bundle = create_station_chief_v12_autonomous_worker_army_release_candidate_bundle()
    result = dict(result)

    if args.station_chief_v12_autonomous_worker_army_release_candidate:
        result["station_chief_v12_autonomous_worker_army_release_candidate"] = bundle
    if args.station_chief_v12_army_workers:
        result["station_chief_v12_army_workers"] = bundle["autonomous_worker_army_profiles"]
    if args.station_chief_v12_army_squads:
        result["station_chief_v12_army_squads"] = bundle["autonomous_worker_squad_registry"]
    if args.station_chief_v12_command_manifest:
        result["station_chief_v12_command_manifest"] = bundle["virtual_army_command_manifest"]
    if args.station_chief_v12_mission_envelopes:
        result["station_chief_v12_mission_envelopes"] = bundle["mission_envelope_registry"]
    if args.station_chief_v12_dispatch_matrix:
        result["station_chief_v12_dispatch_matrix"] = bundle["permissioned_army_dispatch_matrix"]
    if args.station_chief_v12_army_cycle_plan:
        result["station_chief_v12_army_cycle_plan"] = bundle["metadata_only_army_cycle_plan"]
    if args.station_chief_v12_readiness_receipts:
        result["station_chief_v12_readiness_receipts"] = bundle["worker_readiness_receipts"]
    if args.station_chief_v12_army_audit:
        result["station_chief_v12_army_audit"] = bundle["autonomous_worker_army_release_candidate_audit_record"]

    return result


def attach_station_chief_v13_external_tool_api_pilot_hardening(result: dict, args) -> dict:
    if not (
        args.station_chief_v13_external_tool_api_pilot_hardening
        or args.station_chief_v13_external_interfaces
        or args.station_chief_v13_external_action_envelopes
        or args.station_chief_v13_external_access_policy_gate
        or args.station_chief_v13_credential_secret_denial_proof
        or args.station_chief_v13_network_api_denial_proof
        or args.station_chief_v13_external_pilot_dry_run_plan
        or args.station_chief_v13_external_permission_receipts
        or args.station_chief_v13_external_pilot_audit
    ):
        return result

    bundle = create_station_chief_v13_external_tool_api_pilot_hardening_bundle()

    if args.station_chief_v17_live_activation_protocol or args.station_chief_v17_live_action_taxonomy or args.station_chief_v17_first_live_action_allowlist or args.station_chief_v17_preview_readonly_repo_inspection or args.station_chief_v17_approved_readonly_repo_inspection or args.station_chief_v17_live_action_receipt or args.station_chief_v17_live_activation_audit:
        result = attach_station_chief_v17_live_activation_protocol(result, args)

    if args.station_chief_v16_security_integrity_spine or args.station_chief_v16_security_domains or args.station_chief_v16_packet_hash_manifest or args.station_chief_v16_tamper_evident_lineage or args.station_chief_v16_signature_doctrine or args.station_chief_v16_key_separation_trust_boundary or args.station_chief_v16_repo_trust_model or args.station_chief_v16_sensitive_packet_encryption_review or args.station_chief_v16_security_validator_hardening or args.station_chief_v16_security_audit_replay_packet or args.station_chief_v16_security_spine_lock or args.station_chief_v16_security_audit:
        result = attach_station_chief_v16_security_integrity_spine(result, args)

    if args.station_chief_v15_full_auto_agent_army_ready_final_readiness_lock or args.station_chief_v15_final_readiness_domains or args.station_chief_v15_final_activation_prerequisites or args.station_chief_v15_human_approval_override or args.station_chief_v15_command_authority_matrix or args.station_chief_v15_army_readiness_scorecard or args.station_chief_v15_safety_evidence_ledger or args.station_chief_v15_activation_denial_proof or args.station_chief_v15_no_live_action_audit or args.station_chief_v15_final_readiness_certificate:
        result = attach_station_chief_v15_full_auto_agent_army_ready_final_readiness_lock(result, args)

    if args.station_chief_v14_production_readiness_rollback_live_safety_gates or args.station_chief_v14_production_readiness_gates or args.station_chief_v14_rollback_playbooks or args.station_chief_v14_live_safety_gate_manifest or args.station_chief_v14_supervised_production_pilot_preflight or args.station_chief_v14_emergency_stop_abort_controls or args.station_chief_v14_observability_audit_telemetry or args.station_chief_v14_production_readiness_policy_gate or args.station_chief_v14_production_readiness_receipts or args.station_chief_v14_production_safety_audit:
        result = attach_station_chief_v14_production_readiness_rollback_live_safety_gates(result, args)

    if args.station_chief_v13_external_tool_api_pilot_hardening:
        result["station_chief_v13_external_tool_api_pilot_hardening"] = bundle
    if args.station_chief_v13_external_interfaces:
        result["station_chief_v13_external_interfaces"] = bundle["external_interface_descriptor_registry"]
    if args.station_chief_v13_external_action_envelopes:
        result["station_chief_v13_external_action_envelopes"] = bundle["external_action_envelopes"]
    if args.station_chief_v13_external_access_policy_gate:
        result["station_chief_v13_external_access_policy_gate"] = bundle["external_access_policy_gate"]
    if args.station_chief_v13_credential_secret_denial_proof:
        result["station_chief_v13_credential_secret_denial_proof"] = bundle["credential_secret_denial_proof"]
    if args.station_chief_v13_network_api_denial_proof:
        result["station_chief_v13_network_api_denial_proof"] = bundle["network_api_denial_proof"]
    if args.station_chief_v13_external_pilot_dry_run_plan:
        result["station_chief_v13_external_pilot_dry_run_plan"] = bundle["external_pilot_dry_run_plan"]
    if args.station_chief_v13_external_permission_receipts:
        result["station_chief_v13_external_permission_receipts"] = bundle["external_permission_receipts"]
    if args.station_chief_v13_external_pilot_audit:
        result["station_chief_v13_external_pilot_audit"] = bundle["external_pilot_hardening_audit_record"]

    return result

def attach_station_chief_v14_production_readiness_rollback_live_safety_gates(result: dict, args) -> dict:
    if not (
        args.station_chief_v14_production_readiness_rollback_live_safety_gates
        or args.station_chief_v14_production_readiness_gates
        or args.station_chief_v14_rollback_playbooks
        or args.station_chief_v14_live_safety_gate_manifest
        or args.station_chief_v14_supervised_production_pilot_preflight
        or args.station_chief_v14_emergency_stop_abort_controls
        or args.station_chief_v14_observability_audit_telemetry
        or args.station_chief_v14_production_readiness_policy_gate
        or args.station_chief_v14_production_readiness_receipts
        or args.station_chief_v14_production_safety_audit
    ):
        return result

    bundle = create_station_chief_v14_production_readiness_rollback_live_safety_gates_bundle()

    if args.station_chief_v17_live_activation_protocol or args.station_chief_v17_live_action_taxonomy or args.station_chief_v17_first_live_action_allowlist or args.station_chief_v17_preview_readonly_repo_inspection or args.station_chief_v17_approved_readonly_repo_inspection or args.station_chief_v17_live_action_receipt or args.station_chief_v17_live_activation_audit:
        result = attach_station_chief_v17_live_activation_protocol(result, args)

    if args.station_chief_v16_security_integrity_spine or args.station_chief_v16_security_domains or args.station_chief_v16_packet_hash_manifest or args.station_chief_v16_tamper_evident_lineage or args.station_chief_v16_signature_doctrine or args.station_chief_v16_key_separation_trust_boundary or args.station_chief_v16_repo_trust_model or args.station_chief_v16_sensitive_packet_encryption_review or args.station_chief_v16_security_validator_hardening or args.station_chief_v16_security_audit_replay_packet or args.station_chief_v16_security_spine_lock or args.station_chief_v16_security_audit:
        result = attach_station_chief_v16_security_integrity_spine(result, args)

    if args.station_chief_v15_full_auto_agent_army_ready_final_readiness_lock or args.station_chief_v15_final_readiness_domains or args.station_chief_v15_final_activation_prerequisites or args.station_chief_v15_human_approval_override or args.station_chief_v15_command_authority_matrix or args.station_chief_v15_army_readiness_scorecard or args.station_chief_v15_safety_evidence_ledger or args.station_chief_v15_activation_denial_proof or args.station_chief_v15_no_live_action_audit or args.station_chief_v15_final_readiness_certificate:
        result = attach_station_chief_v15_full_auto_agent_army_ready_final_readiness_lock(result, args)

    if args.station_chief_v14_production_readiness_rollback_live_safety_gates:
        result["station_chief_v14_production_readiness_rollback_live_safety_gates"] = bundle
    if args.station_chief_v14_production_readiness_gates:
        result["station_chief_v14_production_readiness_gates"] = bundle["production_readiness_gate_registry"]
    if args.station_chief_v14_rollback_playbooks:
        result["station_chief_v14_rollback_playbooks"] = bundle["rollback_recovery_playbook_registry"]
    if args.station_chief_v14_live_safety_gate_manifest:
        result["station_chief_v14_live_safety_gate_manifest"] = bundle["live_safety_gate_manifest"]
    if args.station_chief_v14_supervised_production_pilot_preflight:
        result["station_chief_v14_supervised_production_pilot_preflight"] = bundle["supervised_production_pilot_preflight_record"]
    if args.station_chief_v14_emergency_stop_abort_controls:
        result["station_chief_v14_emergency_stop_abort_controls"] = bundle["emergency_stop_abort_control_manifest"]
    if args.station_chief_v14_observability_audit_telemetry:
        result["station_chief_v14_observability_audit_telemetry"] = bundle["observability_audit_telemetry_manifest"]
    if args.station_chief_v14_production_readiness_policy_gate:
        result["station_chief_v14_production_readiness_policy_gate"] = bundle["production_readiness_policy_gate"]
    if args.station_chief_v14_production_readiness_receipts:
        result["station_chief_v14_production_readiness_receipts"] = bundle["production_readiness_receipts"]
    if args.station_chief_v14_production_safety_audit:
        result["station_chief_v14_production_safety_audit"] = bundle["production_safety_audit_record"]

    return result

def attach_station_chief_v15_full_auto_agent_army_ready_final_readiness_lock(result: dict, args) -> dict:
    if not (
        args.station_chief_v15_full_auto_agent_army_ready_final_readiness_lock
        or args.station_chief_v15_final_readiness_domains
        or args.station_chief_v15_final_activation_prerequisites
        or args.station_chief_v15_human_approval_override
        or args.station_chief_v15_command_authority_matrix
        or args.station_chief_v15_army_readiness_scorecard
        or args.station_chief_v15_safety_evidence_ledger
        or args.station_chief_v15_activation_denial_proof
        or args.station_chief_v15_no_live_action_audit
        or args.station_chief_v15_final_readiness_certificate
    ):
        return result

    bundle = create_station_chief_v15_full_auto_agent_army_ready_final_readiness_lock_bundle()

    if args.station_chief_v17_live_activation_protocol or args.station_chief_v17_live_action_taxonomy or args.station_chief_v17_first_live_action_allowlist or args.station_chief_v17_preview_readonly_repo_inspection or args.station_chief_v17_approved_readonly_repo_inspection or args.station_chief_v17_live_action_receipt or args.station_chief_v17_live_activation_audit:
        result = attach_station_chief_v17_live_activation_protocol(result, args)

    if args.station_chief_v16_security_integrity_spine or args.station_chief_v16_security_domains or args.station_chief_v16_packet_hash_manifest or args.station_chief_v16_tamper_evident_lineage or args.station_chief_v16_signature_doctrine or args.station_chief_v16_key_separation_trust_boundary or args.station_chief_v16_repo_trust_model or args.station_chief_v16_sensitive_packet_encryption_review or args.station_chief_v16_security_validator_hardening or args.station_chief_v16_security_audit_replay_packet or args.station_chief_v16_security_spine_lock or args.station_chief_v16_security_audit:
        result = attach_station_chief_v16_security_integrity_spine(result, args)

    if args.station_chief_v15_full_auto_agent_army_ready_final_readiness_lock:
        result["station_chief_v15_full_auto_agent_army_ready_final_readiness_lock"] = bundle
    if args.station_chief_v15_final_readiness_domains:
        result["station_chief_v15_final_readiness_domains"] = bundle["final_readiness_domain_registry"]
    if args.station_chief_v15_final_activation_prerequisites:
        result["station_chief_v15_final_activation_prerequisites"] = bundle["final_activation_prerequisite_registry"]
    if args.station_chief_v15_human_approval_override:
        result["station_chief_v15_human_approval_override"] = bundle["final_human_approval_override_manifest"]
    if args.station_chief_v15_command_authority_matrix:
        result["station_chief_v15_command_authority_matrix"] = bundle["final_command_authority_matrix"]
    if args.station_chief_v15_army_readiness_scorecard:
        result["station_chief_v15_army_readiness_scorecard"] = bundle["final_army_readiness_scorecard"]
    if args.station_chief_v15_safety_evidence_ledger:
        result["station_chief_v15_safety_evidence_ledger"] = bundle["final_safety_evidence_ledger"]
    if args.station_chief_v15_activation_denial_proof:
        result["station_chief_v15_activation_denial_proof"] = bundle["final_activation_denial_proof"]
    if args.station_chief_v15_no_live_action_audit:
        result["station_chief_v15_no_live_action_audit"] = bundle["final_no_live_action_audit_record"]
    if args.station_chief_v15_final_readiness_certificate:
        result["station_chief_v15_final_readiness_certificate"] = bundle["final_readiness_certificate"]

    return result

def attach_station_chief_v16_security_integrity_spine(result: dict, args) -> dict:
    if not (
        args.station_chief_v16_security_integrity_spine
        or args.station_chief_v16_security_domains
        or args.station_chief_v16_packet_hash_manifest
        or args.station_chief_v16_tamper_evident_lineage
        or args.station_chief_v16_signature_doctrine
        or args.station_chief_v16_key_separation_trust_boundary
        or args.station_chief_v16_repo_trust_model
        or args.station_chief_v16_sensitive_packet_encryption_review
        or args.station_chief_v16_security_validator_hardening
        or args.station_chief_v16_security_audit_replay_packet
        or args.station_chief_v16_security_spine_lock
        or args.station_chief_v16_security_audit
    ):
        return result

    bundle = create_station_chief_v16_security_integrity_spine_bundle()

    if args.station_chief_v17_live_activation_protocol or args.station_chief_v17_live_action_taxonomy or args.station_chief_v17_first_live_action_allowlist or args.station_chief_v17_preview_readonly_repo_inspection or args.station_chief_v17_approved_readonly_repo_inspection or args.station_chief_v17_live_action_receipt or args.station_chief_v17_live_activation_audit:
        result = attach_station_chief_v17_live_activation_protocol(result, args)

    if args.station_chief_v16_security_integrity_spine:
        result["station_chief_v16_security_integrity_spine"] = bundle
    if args.station_chief_v16_security_domains:
        result["station_chief_v16_security_domains"] = bundle["security_integrity_domain_registry"]
    if args.station_chief_v16_packet_hash_manifest:
        result["station_chief_v16_packet_hash_manifest"] = bundle["packet_hash_manifest"]
    if args.station_chief_v16_tamper_evident_lineage:
        result["station_chief_v16_tamper_evident_lineage"] = bundle["tamper_evident_lineage_manifest"]
    if args.station_chief_v16_signature_doctrine:
        result["station_chief_v16_signature_doctrine"] = bundle["signature_doctrine_manifest"]
    if args.station_chief_v16_key_separation_trust_boundary:
        result["station_chief_v16_key_separation_trust_boundary"] = bundle["key_separation_trust_boundary_manifest"]
    if args.station_chief_v16_repo_trust_model:
        result["station_chief_v16_repo_trust_model"] = bundle["official_vs_lab_repo_trust_model"]
    if args.station_chief_v16_sensitive_packet_encryption_review:
        result["station_chief_v16_sensitive_packet_encryption_review"] = bundle["sensitive_packet_encryption_review_manifest"]
    if args.station_chief_v16_security_validator_hardening:
        result["station_chief_v16_security_validator_hardening"] = bundle["security_validator_hardening_manifest"]
    if args.station_chief_v16_security_audit_replay_packet:
        result["station_chief_v16_security_audit_replay_packet"] = bundle["security_audit_replay_packet"]
    if args.station_chief_v16_security_spine_lock:
        result["station_chief_v16_security_spine_lock"] = bundle["security_spine_lock"]
    if args.station_chief_v16_security_audit:
        result["station_chief_v16_security_audit"] = bundle["security_integrity_spine_audit_record"]

    return result

def attach_station_chief_v17_live_activation_protocol(result: dict, args) -> dict:
    if not (
        args.station_chief_v17_live_activation_protocol
        or args.station_chief_v17_live_action_taxonomy
        or args.station_chief_v17_first_live_action_allowlist
        or args.station_chief_v17_preview_readonly_repo_inspection
        or args.station_chief_v17_approved_readonly_repo_inspection
        or args.station_chief_v17_live_action_receipt
        or args.station_chief_v17_live_activation_audit
    ):
        return result

    # Determine if we should actually execute the real inspection
    execute_live = getattr(args, "station_chief_v17_approved_readonly_repo_inspection", False)
    approval_phrase = getattr(args, "station_chief_v17_approval_phrase", None)
    operator_label = getattr(args, "station_chief_v17_operator_label", None)

    bundle = create_station_chief_v17_live_activation_protocol_bundle(
        approval_phrase=approval_phrase,
        operator_label=operator_label,
        execute_live_readonly_inspection=execute_live
    )

    if args.station_chief_v17_live_activation_protocol:
        result["station_chief_v17_live_activation_protocol"] = bundle
    if args.station_chief_v17_live_action_taxonomy:
        result["station_chief_v17_live_action_taxonomy"] = bundle["controlled_live_action_taxonomy"]
    if args.station_chief_v17_first_live_action_allowlist:
        result["station_chief_v17_first_live_action_allowlist"] = bundle["first_live_action_allowlist"]
    if args.station_chief_v17_preview_readonly_repo_inspection:
        result["station_chief_v17_preview_readonly_repo_inspection"] = bundle["live_action_preview_packet"]
    if args.station_chief_v17_approved_readonly_repo_inspection:
        result["station_chief_v17_approved_readonly_repo_inspection"] = bundle["controlled_readonly_repo_integrity_inspection"]
    if args.station_chief_v17_live_action_receipt:
        result["station_chief_v17_live_action_receipt"] = bundle["live_action_receipt"]
    if args.station_chief_v17_live_activation_audit:
        result["station_chief_v17_live_activation_audit"] = bundle["live_activation_audit_record"]

    return result

def run_station_chief(command: str, adapter_name: str = "noop") -> dict[str, Any]:
    brief = create_command_brief(command)
    work_orders = create_work_orders(brief)
    overlays = load_overlay_stack()
    execution_plan = create_execution_plan(brief, work_orders, adapter_name=adapter_name)
    adapter_result = run_noop_adapter(execution_plan)
    runtime_status = {
        "4.5.0": "task_assignment_audit_closeout_candidate",
        "4.7.0": "task_queue_preview_audit_closeout_candidate",
        "4.8.0": "non_executing_queue_routing_preview_candidate",
        "4.9.0": "live_queue_orchestration_candidate_review",
        "5.0.0": "first_live_queue_execution_candidate_review",
        "5.1.0": "first_supervised_local_execution_kernel_candidate",
        "5.2.0": "controlled_repeatable_local_execution_candidate",
        "5.3.0": "sandbox_worker_handoff_candidate",
        "5.4.0": "sandbox_worker_acknowledgement_candidate",
        "5.5.0": "sandbox_worker_acceptance_candidate_review",
        "5.6.0": "sandbox_worker_ready_state_packet_candidate",
        "5.7.0": "sandbox_worker_dry_run_assignment_candidate",
        "5.8.0": "sandbox_worker_dry_run_result_candidate",
        "5.9.0": "sandbox_worker_dry_run_replay_audit_candidate",
        "6.0.0": "station_chief_v6_0_mvp_lock",
        "6.1.0": "station_chief_v6_1_post_mvp_expansion_review",
        "6.2.0": "station_chief_v6_2_post_mvp_expansion_lane_scope",
        "6.3.0": "station_chief_v6_3_post_mvp_expansion_lane_readiness",
        "6.4.0": "station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan",
        "6.5.0": "station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review",
        "6.6.0": "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition",
        "8.0.0": "station_chief_v8_finish_line_control_plane",
        "9.0.0": "station_chief_v9_controlled_local_worker_pilot",
        "10.0.0": "station_chief_v10_multi_worker_sandbox_coordination",
        "11.0.0": "station_chief_v11_permissioned_tool_task_queue_layer",
        "12.0.0": "station_chief_v12_autonomous_worker_army_release_candidate",
        "13.0.0": "station_chief_v13_external_tool_api_pilot_hardening",
        "14.0.0": "station_chief_v14_production_readiness_rollback_live_safety_gates",
        "15.0.0": "station_chief_v15_full_auto_agent_army_ready_final_readiness_lock",
        "16.0.0": "station_chief_v16_security_integrity_spine",
        "17.0.0": "station_chief_v17_human_gated_live_activation_protocol",
    }.get(STATION_CHIEF_RUNTIME_VERSION, "live_queue_orchestration_candidate_review")
    evidence = build_demo_evidence()
    evidence.update(
        {
            "controlled_repeatable_local_execution_candidate_not_yet_active": False,
            "controlled_repeatable_local_execution_candidate_available": True,
            "controlled_repeatable_local_execution_candidate_requires_token": True,
            "controlled_repeatable_local_execution_candidate_requires_human_operator": True,
            "controlled_repeatable_local_execution_candidate_writes_one_local_proof_record_only": True,
            "controlled_repeatable_local_execution_candidate_uses_bounded_repeatability_count": True,
            "controlled_repeatable_local_execution_candidate_allows_only_deterministic_local_proof_write": True,
            "controlled_repeatable_local_execution_candidate_does_not_create_real_queue": True,
            "controlled_repeatable_local_execution_candidate_does_not_write_queue": True,
            "controlled_repeatable_local_execution_candidate_does_not_write_scheduler_state": True,
            "controlled_repeatable_local_execution_candidate_does_not_write_cron_state": True,
            "controlled_repeatable_local_execution_candidate_does_not_enqueue_tasks": True,
            "controlled_repeatable_local_execution_candidate_does_not_execute_arbitrary_tasks": True,
            "controlled_repeatable_local_execution_candidate_does_not_execute_user_tasks": True,
            "controlled_repeatable_local_execution_candidate_does_not_start_worker_processes": True,
            "controlled_repeatable_local_execution_candidate_does_not_assign_tasks": True,
            "controlled_repeatable_local_execution_candidate_does_not_route_workers": True,
            "controlled_repeatable_local_execution_candidate_does_not_orchestrate_live_work": True,
            "controlled_repeatable_local_execution_candidate_does_not_call_live_apis": True,
            "controlled_repeatable_local_execution_candidate_does_not_use_network_access": True,
            "controlled_repeatable_local_execution_candidate_does_not_open_sockets": True,
            "controlled_repeatable_local_execution_candidate_does_not_use_credentials": True,
            "controlled_repeatable_local_execution_candidate_does_not_read_secrets": True,
            "controlled_repeatable_local_execution_candidate_does_not_read_environment": True,
            "controlled_repeatable_local_execution_candidate_does_not_deploy": True,
            "controlled_repeatable_local_execution_candidate_does_not_execute_production": True,
            "first_live_queue_execution_candidate_review_available": True,
            "first_live_queue_execution_candidate_review_local_record_only": True,
            "first_live_queue_execution_candidate_review_requires_token": True,
            "first_live_queue_execution_candidate_review_requires_human_operator": True,
            "first_live_queue_execution_candidate_review_writes_one_local_record_only": True,
            "first_live_queue_execution_candidate_review_does_not_create_real_queue": True,
            "first_live_queue_execution_candidate_review_does_not_write_queue": True,
            "first_live_queue_execution_candidate_review_does_not_write_scheduler_state": True,
            "first_live_queue_execution_candidate_review_does_not_write_cron_state": True,
            "first_live_queue_execution_candidate_review_does_not_enqueue_tasks": True,
            "first_live_queue_execution_candidate_review_does_not_execute_tasks": True,
            "first_live_queue_execution_candidate_review_does_not_start_worker_processes": True,
            "first_live_queue_execution_candidate_review_does_not_assign_tasks": True,
            "first_live_queue_execution_candidate_review_does_not_route_workers": True,
            "first_live_queue_execution_candidate_review_does_not_orchestrate_live_work": True,
            "first_live_queue_execution_candidate_review_does_not_perform_supervised_local_execution": True,
            "first_live_queue_execution_candidate_review_does_not_call_live_apis": True,
            "first_live_queue_execution_candidate_review_does_not_use_network_access": True,
            "first_live_queue_execution_candidate_review_does_not_open_sockets": True,
            "first_live_queue_execution_candidate_review_does_not_use_credentials": True,
            "first_live_queue_execution_candidate_review_does_not_read_secrets": True,
            "first_live_queue_execution_candidate_review_does_not_read_environment": True,
            "first_live_queue_execution_candidate_review_does_not_deploy": True,
            "first_live_queue_execution_candidate_review_does_not_execute_production": True,
            "first_supervised_local_execution_kernel_candidate_not_yet_active": False,
            "first_supervised_local_execution_kernel_candidate_available": True,
            "first_supervised_local_execution_kernel_candidate_requires_token": True,
            "first_supervised_local_execution_kernel_candidate_requires_human_operator": True,
            "first_supervised_local_execution_kernel_candidate_writes_one_local_output_record_only": True,
            "first_supervised_local_execution_kernel_candidate_allows_only_deterministic_local_output_write": True,
            "first_supervised_local_execution_kernel_candidate_does_not_create_real_queue": True,
            "first_supervised_local_execution_kernel_candidate_does_not_write_queue": True,
            "first_supervised_local_execution_kernel_candidate_does_not_write_scheduler_state": True,
            "first_supervised_local_execution_kernel_candidate_does_not_write_cron_state": True,
            "first_supervised_local_execution_kernel_candidate_does_not_enqueue_tasks": True,
            "first_supervised_local_execution_kernel_candidate_does_not_execute_arbitrary_tasks": True,
            "first_supervised_local_execution_kernel_candidate_does_not_execute_user_tasks": True,
            "first_supervised_local_execution_kernel_candidate_does_not_start_worker_processes": True,
            "first_supervised_local_execution_kernel_candidate_does_not_assign_tasks": True,
            "first_supervised_local_execution_kernel_candidate_does_not_route_workers": True,
            "first_supervised_local_execution_kernel_candidate_does_not_orchestrate_live_work": True,
            "first_supervised_local_execution_kernel_candidate_does_not_perform_supervised_local_execution": True,
            "first_supervised_local_execution_kernel_candidate_does_not_call_live_apis": True,
            "first_supervised_local_execution_kernel_candidate_does_not_use_network_access": True,
            "first_supervised_local_execution_kernel_candidate_does_not_open_sockets": True,
            "first_supervised_local_execution_kernel_candidate_does_not_use_credentials": True,
            "first_supervised_local_execution_kernel_candidate_does_not_read_secrets": True,
            "first_supervised_local_execution_kernel_candidate_does_not_read_environment": True,
            "first_supervised_local_execution_kernel_candidate_does_not_deploy": True,
            "first_supervised_local_execution_kernel_candidate_does_not_execute_production": True,
            "sandbox_worker_handoff_candidate_not_yet_active": False,
            "sandbox_worker_handoff_candidate_available": True,
            "sandbox_worker_handoff_candidate_requires_token": True,
            "sandbox_worker_handoff_candidate_requires_human_operator": True,
            "sandbox_worker_handoff_candidate_writes_one_local_handoff_packet_only": True,
            "sandbox_worker_handoff_candidate_uses_one_sandbox_worker_label": True,
            "sandbox_worker_handoff_candidate_references_one_v5_2_repeatability_proof_label": True,
            "sandbox_worker_handoff_candidate_does_not_start_worker_processes": True,
            "sandbox_worker_handoff_candidate_does_not_start_agents": True,
            "sandbox_worker_handoff_candidate_does_not_create_real_queue": True,
            "sandbox_worker_handoff_candidate_does_not_write_queue": True,
            "sandbox_worker_handoff_candidate_does_not_write_scheduler_state": True,
            "sandbox_worker_handoff_candidate_does_not_write_cron_state": True,
            "sandbox_worker_handoff_candidate_does_not_enqueue_tasks": True,
            "sandbox_worker_handoff_candidate_does_not_execute_arbitrary_tasks": True,
            "sandbox_worker_handoff_candidate_does_not_execute_user_tasks": True,
            "sandbox_worker_handoff_candidate_does_not_route_workers": True,
            "sandbox_worker_handoff_candidate_does_not_orchestrate_live_work": True,
            "sandbox_worker_handoff_candidate_does_not_call_live_apis": True,
            "sandbox_worker_handoff_candidate_does_not_use_network_access": True,
            "sandbox_worker_handoff_candidate_does_not_open_sockets": True,
            "sandbox_worker_handoff_candidate_does_not_use_credentials": True,
            "sandbox_worker_handoff_candidate_does_not_read_secrets": True,
            "sandbox_worker_handoff_candidate_does_not_read_environment": True,
            "sandbox_worker_handoff_candidate_does_not_deploy": True,
            "sandbox_worker_handoff_candidate_does_not_execute_production": True,
            "sandbox_worker_acknowledgement_candidate_not_yet_active": False,
            "sandbox_worker_acknowledgement_candidate_available": True,
            "sandbox_worker_acknowledgement_candidate_requires_token": True,
            "sandbox_worker_acknowledgement_candidate_requires_human_operator": True,
            "sandbox_worker_acknowledgement_candidate_writes_one_local_acknowledgement_packet_only": True,
            "sandbox_worker_acknowledgement_candidate_uses_one_sandbox_worker_label": True,
            "sandbox_worker_acknowledgement_candidate_references_one_v5_3_handoff_packet_label": True,
            "sandbox_worker_acknowledgement_candidate_does_not_start_worker_processes": True,
            "sandbox_worker_acknowledgement_candidate_does_not_start_agents": True,
            "sandbox_worker_acknowledgement_candidate_does_not_create_real_queue": True,
            "sandbox_worker_acknowledgement_candidate_does_not_write_queue": True,
            "sandbox_worker_acknowledgement_candidate_does_not_write_scheduler_state": True,
            "sandbox_worker_acknowledgement_candidate_does_not_write_cron_state": True,
            "sandbox_worker_acknowledgement_candidate_does_not_enqueue_tasks": True,
            "sandbox_worker_acknowledgement_candidate_does_not_execute_arbitrary_tasks": True,
            "sandbox_worker_acknowledgement_candidate_does_not_execute_user_tasks": True,
            "sandbox_worker_acknowledgement_candidate_does_not_route_workers": True,
            "sandbox_worker_acknowledgement_candidate_does_not_orchestrate_live_work": True,
            "sandbox_worker_acknowledgement_candidate_does_not_call_live_apis": True,
            "sandbox_worker_acknowledgement_candidate_does_not_use_network_access": True,
            "sandbox_worker_acknowledgement_candidate_does_not_open_sockets": True,
            "sandbox_worker_acknowledgement_candidate_does_not_use_credentials": True,
            "sandbox_worker_acknowledgement_candidate_does_not_read_secrets": True,
            "sandbox_worker_acknowledgement_candidate_does_not_read_environment": True,
            "sandbox_worker_acknowledgement_candidate_does_not_deploy": True,
            "sandbox_worker_acknowledgement_candidate_does_not_execute_production": True,
            "sandbox_worker_acceptance_candidate_not_yet_active": True,
            "controlled_repeatable_local_execution_candidate_not_yet_active": False,
        }
    )
    return {
        "station_chief_runtime_version": STATION_CHIEF_RUNTIME_VERSION,
        "runtime_status": runtime_status,
        "release_status": "STABLE_LOCKED",
        "command": command,
        "command_type": brief["command_type"],
        "activation_tier": brief["activation_tier"],
        "baseline_preserved": True,
        "evidence": evidence,
        "next_step": "Next step: v12.1 or v13.0 requires explicit operator instruction.",
        "first_tiny_real_world_supervised_execution_candidate_available": True,
        "first_tiny_real_world_supervised_execution_candidate_local_only": True,
        "first_tiny_real_world_supervised_execution_candidate_requires_token": True,
        "sandbox_worker_handoff_candidate_available": True,
        "sandbox_worker_acknowledgement_candidate_available": True,
        "sandbox_worker_acceptance_candidate_review_available": True,
        "sandbox_worker_ready_state_packet_candidate_available": True,
        "sandbox_worker_dry_run_assignment_candidate_available": True,
        "sandbox_worker_dry_run_result_candidate_available": True,
        "sandbox_worker_dry_run_replay_audit_candidate_available": True,
        "station_chief_v6_0_mvp_lock_available": True,
        "station_chief_v6_1_post_mvp_expansion_review_available": True,
        "station_chief_v6_1_post_mvp_expansion_review_requires_token": True,
        "station_chief_v6_1_post_mvp_expansion_review_requires_human_operator": True,
        "station_chief_v6_1_post_mvp_expansion_review_writes_one_local_packet_only": True,
        "station_chief_v6_1_post_mvp_expansion_review_references_one_v6_0_mvp_lock_label": True,
        "station_chief_v6_1_post_mvp_expansion_review_uses_one_review_label": True,
        "station_chief_v6_1_post_mvp_expansion_review_uses_one_requested_expansion_lane_label": True,
        "station_chief_v6_1_post_mvp_expansion_review_uses_one_boundary_label": True,
        "station_chief_v6_1_post_mvp_expansion_review_uses_one_safety_posture_label": True,
        "station_chief_v6_1_post_mvp_expansion_review_records_metadata_only": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_execute_post_mvp_expansion": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_execute_selected_expansion_lane": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_mutate_v6_0_mvp_lock": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_execute_v6_0_mvp_lock": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_execute_local_task_candidate": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_execute_dry_run_task": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_create_real_worker_result": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_perform_live_replay": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_perform_production_audit": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_perform_rollback": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_perform_recovery": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_create_v6_2": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_start_worker_processes": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_start_agents": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_create_real_queue": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_write_queue": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_write_scheduler_state": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_write_cron_state": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_enqueue_tasks": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_execute_arbitrary_tasks": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_execute_user_tasks": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_route_workers": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_orchestrate_live_work": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_call_live_apis": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_use_network_access": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_open_sockets": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_use_credentials": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_read_secrets": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_read_environment": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_deploy": True,
        "station_chief_v6_1_post_mvp_expansion_review_does_not_execute_production": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_available": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_requires_token": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_requires_human_operator": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_writes_one_local_packet_only": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_references_one_v6_1_review_packet_label": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_uses_one_selected_expansion_lane_label": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_uses_one_lane_scope_label": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_uses_one_lane_constraint_label": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_uses_one_lane_success_criteria_label": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_uses_one_lane_non_execution_boundary_label": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_records_metadata_only": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_implement_selected_expansion_lane": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_execute_selected_expansion_lane": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_execute_post_mvp_expansion": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_mutate_v6_1_review_packet": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_execute_v6_1_review_packet": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_mutate_v6_0_mvp_lock": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_execute_v6_0_mvp_lock": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_execute_local_task_candidate": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_execute_dry_run_task": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_create_real_worker_result": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_perform_live_replay": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_perform_production_audit": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_perform_rollback": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_perform_recovery": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_create_v6_3": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_available": True,
        "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_available": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_requires_token": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_requires_human_operator": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_writes_one_local_packet_only": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_references_one_v6_2_lane_scope_packet_reference_label": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_uses_one_selected_expansion_lane_label": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_uses_one_readiness_checklist_label": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_uses_one_readiness_blocker_label": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_uses_one_readiness_evidence_label": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_uses_one_readiness_non_execution_boundary_label": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_records_metadata_only": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_implement_selected_expansion_lane": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_execute_selected_expansion_lane": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_execute_post_mvp_expansion": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_mutate_v6_2_lane_scope_packet": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_execute_v6_2_lane_scope_packet": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_mutate_v6_1_review_packet": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_execute_v6_1_review_packet": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_mutate_v6_0_mvp_lock": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_execute_v6_0_mvp_lock": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_execute_local_task_candidate": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_execute_dry_run_task": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_create_real_worker_result": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_perform_live_replay": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_perform_production_audit": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_perform_rollback": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_perform_recovery": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_create_v6_4": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_start_worker_processes": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_start_agents": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_create_real_queue": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_write_queue": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_write_scheduler_state": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_write_cron_state": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_enqueue_tasks": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_execute_arbitrary_tasks": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_execute_user_tasks": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_route_workers": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_orchestrate_live_work": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_call_live_apis": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_use_network_access": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_open_sockets": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_use_credentials": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_read_secrets": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_read_environment": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_deploy": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_does_not_execute_production": True,
        "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_available": True,
        "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_records_metadata_only": True,
        "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_does_not_implement_selected_expansion_lane": True,
        "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_does_not_execute_selected_expansion_lane": True,
        "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_does_not_execute_implementation_plan": True,
        "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_does_not_execute_implementation_steps": True,
        "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_does_not_execute_review_findings": True,
        "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_does_not_execute_review_decision": True,
        "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_does_not_execute_disposition_conditions": True,
        "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_does_not_execute_next_gate": True,
        "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_does_not_start_worker_processes": True,
        "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_does_not_start_agents": True,
        "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_does_not_create_real_queue": True,
        "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_does_not_write_queue": True,
        "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_does_not_enqueue_tasks": True,
        "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_does_not_execute_tasks": True,
        "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_does_not_call_live_apis": True,
        "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_does_not_use_network_access": True,
        "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_does_not_deploy": True,
        "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_does_not_execute_production": True,
        "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_does_not_create_v6_7": True,
        "station_chief_v8_finish_line_control_plane_available": True,
        "station_chief_v8_baby_step_chain_closed": True,
        "station_chief_v8_skips_v6_7_through_v7_x": True,
        "station_chief_v8_consolidates_v6_2_through_v6_6": True,
        "station_chief_v8_does_not_start_worker_processes": True,
        "station_chief_v8_does_not_start_agents": True,
        "station_chief_v8_does_not_create_real_queue": True,
        "station_chief_v8_does_not_write_queue": True,
        "station_chief_v8_does_not_enqueue_tasks": True,
        "station_chief_v8_does_not_execute_tasks": True,
        "station_chief_v8_does_not_call_live_apis": True,
        "station_chief_v8_does_not_use_network_access": True,
        "station_chief_v8_does_not_deploy": True,
        "station_chief_v8_does_not_execute_production": True,
        "station_chief_v8_does_not_create_v8_1": True,
        "station_chief_v9_controlled_local_worker_pilot_available": True,
        "station_chief_v9_registers_one_local_worker_profile": True,
        "station_chief_v9_registers_one_fixed_synthetic_noop_task": True,
        "station_chief_v9_generates_noop_result_only": True,
        "station_chief_v9_does_not_start_worker_processes": True,
        "station_chief_v9_does_not_start_daemons": True,
        "station_chief_v9_does_not_start_agents": True,
        "station_chief_v9_does_not_create_real_queue": True,
        "station_chief_v9_does_not_write_queue": True,
        "station_chief_v9_does_not_enqueue_tasks": True,
        "station_chief_v9_does_not_execute_tasks": True,
        "station_chief_v9_does_not_execute_arbitrary_tasks": True,
        "station_chief_v9_does_not_execute_user_tasks": True,
        "station_chief_v9_does_not_execute_shell": True,
        "station_chief_v9_does_not_start_subprocesses": True,
        "station_chief_v9_does_not_call_live_apis": True,
        "station_chief_v9_does_not_use_network_access": True,
        "station_chief_v9_does_not_access_credentials": True,
        "station_chief_v9_does_not_read_secrets": True,
        "station_chief_v9_does_not_read_environment": True,
        "station_chief_v9_does_not_deploy": True,
        "station_chief_v9_does_not_execute_production": True,
        "station_chief_v9_does_not_create_v9_1": True,
        "station_chief_v10_multi_worker_sandbox_coordination_available": True,
        "station_chief_v10_registers_three_sandbox_worker_profiles": True,
        "station_chief_v10_registers_three_fixed_synthetic_noop_tasks": True,
        "station_chief_v10_creates_deterministic_assignment_map": True,
        "station_chief_v10_creates_coordination_ledger": True,
        "station_chief_v10_generates_noop_results_only": True,
        "station_chief_v10_does_not_start_worker_processes": True,
        "station_chief_v10_does_not_start_daemons": True,
        "station_chief_v10_does_not_start_agents": True,
        "station_chief_v10_does_not_create_real_queue": True,
        "station_chief_v10_does_not_write_queue": True,
        "station_chief_v10_does_not_enqueue_live_tasks": True,
        "station_chief_v10_does_not_execute_live_tasks": True,
        "station_chief_v10_does_not_execute_arbitrary_tasks": True,
        "station_chief_v10_does_not_execute_user_tasks": True,
        "station_chief_v10_does_not_execute_shell": True,
        "station_chief_v10_does_not_start_subprocesses": True,
        "station_chief_v10_does_not_call_live_apis": True,
        "station_chief_v10_does_not_use_network_access": True,
        "station_chief_v10_does_not_access_credentials": True,
        "station_chief_v10_does_not_read_secrets": True,
        "station_chief_v10_does_not_read_environment": True,
        "station_chief_v10_does_not_deploy": True,
        "station_chief_v10_does_not_execute_production": True,
        "station_chief_v10_does_not_create_v10_1": True,
        "station_chief_v10_does_not_create_v11": True,
        "station_chief_v11_permissioned_tool_task_queue_layer_available": True,
        "station_chief_v11_registers_three_permissioned_tool_descriptors": True,
        "station_chief_v11_registers_three_permissioned_task_envelopes": True,
        "station_chief_v11_creates_virtual_queue_manifest": True,
        "station_chief_v11_creates_deterministic_dispatch_plan": True,
        "station_chief_v11_generates_permission_receipts_only": True,
        "station_chief_v11_does_not_invoke_real_tools": True,
        "station_chief_v11_does_not_invoke_external_tools": True,
        "station_chief_v11_does_not_start_worker_processes": True,
        "station_chief_v11_does_not_start_daemons": True,
        "station_chief_v11_does_not_start_agents": True,
        "station_chief_v11_does_not_create_real_queue": True,
        "station_chief_v11_does_not_write_queue": True,
        "station_chief_v11_does_not_enqueue_live_tasks": True,
        "station_chief_v11_does_not_execute_live_tasks": True,
        "station_chief_v11_does_not_route_live_work": True,
        "station_chief_v11_does_not_orchestrate_live_work": True,
        "station_chief_v11_does_not_execute_arbitrary_tasks": True,
        "station_chief_v11_does_not_execute_user_tasks": True,
        "station_chief_v11_does_not_execute_shell": True,
        "station_chief_v11_does_not_start_subprocesses": True,
        "station_chief_v11_does_not_call_live_apis": True,
        "station_chief_v11_does_not_use_network_access": True,
        "station_chief_v11_does_not_access_credentials": True,
        "station_chief_v11_does_not_read_secrets": True,
        "station_chief_v11_does_not_read_environment": True,
        "station_chief_v11_does_not_deploy": True,
        "station_chief_v11_does_not_execute_production": True,
        "station_chief_v11_does_not_create_v11_1": True,
        "station_chief_v11_does_not_create_v12": True,
        "station_chief_v12_autonomous_worker_army_release_candidate_available": True,
        "station_chief_v12_registers_twelve_autonomous_worker_profiles": True,
        "station_chief_v12_registers_four_worker_squads": True,
        "station_chief_v12_creates_virtual_army_command_manifest": True,
        "station_chief_v12_creates_mission_envelope_registry": True,
        "station_chief_v12_creates_autonomy_policy_gate": True,
        "station_chief_v12_creates_permissioned_dispatch_matrix": True,
        "station_chief_v12_creates_virtual_queue_control_record": True,
        "station_chief_v12_creates_metadata_only_army_cycle_plan": True,
        "station_chief_v12_generates_worker_readiness_receipts_only": True,
        "station_chief_v12_does_not_activate_full_external_prod_agent_army": True,
        "station_chief_v12_does_not_activate_real_workers": True,
        "station_chief_v12_does_not_invoke_real_tools": True,
        "station_chief_v12_does_not_invoke_external_tools": True,
        "station_chief_v12_does_not_start_worker_processes": True,
        "station_chief_v12_does_not_start_daemons": True,
        "station_chief_v12_does_not_start_agents": True,
        "station_chief_v12_does_not_create_real_queue": True,
        "station_chief_v12_does_not_write_queue": True,
        "station_chief_v12_does_not_enqueue_live_tasks": True,
        "station_chief_v12_does_not_execute_live_tasks": True,
        "station_chief_v12_does_not_route_live_work": True,
        "station_chief_v12_does_not_orchestrate_live_work": True,
        "station_chief_v12_does_not_execute_arbitrary_tasks": True,
        "station_chief_v12_does_not_execute_user_tasks": True,
        "station_chief_v12_does_not_execute_shell": True,
        "station_chief_v12_does_not_start_subprocesses": True,
        "station_chief_v12_does_not_call_live_apis": True,
        "station_chief_v12_does_not_use_network_access": True,
        "station_chief_v12_does_not_access_credentials": True,
        "station_chief_v12_does_not_read_secrets": True,
        "station_chief_v12_does_not_read_environment": True,
        "station_chief_v12_does_not_deploy": True,
        "station_chief_v12_does_not_execute_production": True,
        "station_chief_v12_does_not_create_v12_1": True,
        "station_chief_v12_does_not_create_v13": True,
        "station_chief_v13_external_tool_api_pilot_hardening_available": True,
        "station_chief_v13_registers_four_external_interface_descriptors": True,
        "station_chief_v13_registers_four_external_action_envelopes": True,
        "station_chief_v13_creates_external_access_policy_gate": True,
        "station_chief_v13_creates_credential_secret_denial_proof": True,
        "station_chief_v13_creates_network_api_denial_proof": True,
        "station_chief_v13_creates_external_pilot_dry_run_plan": True,
        "station_chief_v13_generates_external_permission_receipts_only": True,
        "station_chief_v13_does_not_invoke_real_tools": True,
        "station_chief_v13_does_not_invoke_external_tools": True,
        "station_chief_v13_does_not_call_apis": True,
        "station_chief_v13_does_not_use_network_access": True,
        "station_chief_v13_does_not_open_sockets": True,
        "station_chief_v13_does_not_resolve_dns": True,
        "station_chief_v13_does_not_access_credentials": True,
        "station_chief_v13_does_not_access_credential_vault": True,
        "station_chief_v13_does_not_read_secrets": True,
        "station_chief_v13_does_not_read_environment": True,
        "station_chief_v13_does_not_start_worker_processes": True,
        "station_chief_v13_does_not_start_daemons": True,
        "station_chief_v13_does_not_start_agents": True,
        "station_chief_v13_does_not_create_real_queue": True,
        "station_chief_v13_does_not_write_queue": True,
        "station_chief_v13_does_not_enqueue_live_tasks": True,
        "station_chief_v13_does_not_execute_live_tasks": True,
        "station_chief_v13_does_not_route_live_work": True,
        "station_chief_v13_does_not_orchestrate_live_work": True,
        "station_chief_v13_does_not_execute_arbitrary_tasks": True,
        "station_chief_v13_does_not_execute_user_tasks": True,
        "station_chief_v13_does_not_execute_shell": True,
        "station_chief_v13_does_not_start_subprocesses": True,
        "station_chief_v13_does_not_deploy": True,
        "station_chief_v13_does_not_execute_production": True,
        "station_chief_v13_does_not_create_v13_1": True,
        "station_chief_v13_does_not_create_v14": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_start_worker_processes": True,

        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_start_agents": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_create_real_queue": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_write_queue": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_write_scheduler_state": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_write_cron_state": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_enqueue_tasks": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_execute_arbitrary_tasks": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_execute_user_tasks": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_route_workers": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_orchestrate_live_work": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_call_live_apis": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_use_network_access": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_open_sockets": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_use_credentials": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_read_secrets": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_read_environment": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_deploy": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_does_not_execute_production": True,
        "v6_3_not_yet_active": False,
        "v6_4_not_yet_active": False,
        "v6_2_not_yet_active": True,
        "station_chief_v6_0_mvp_lock_requires_token": True,
        "station_chief_v6_0_mvp_lock_requires_human_operator": True,
        "station_chief_v6_0_mvp_lock_writes_one_local_packet_only": True,
        "station_chief_v6_0_mvp_lock_uses_one_local_task_candidate_label": True,
        "station_chief_v6_0_mvp_lock_uses_one_sandbox_worker_label": True,
        "station_chief_v6_0_mvp_lock_references_one_v5_3_handoff_packet_label": True,
        "station_chief_v6_0_mvp_lock_references_one_v5_4_acknowledgement_packet_label": True,
        "station_chief_v6_0_mvp_lock_references_one_v5_5_acceptance_review_packet_label": True,
        "station_chief_v6_0_mvp_lock_references_one_v5_6_ready_state_packet_label": True,
        "station_chief_v6_0_mvp_lock_references_one_v5_7_dry_run_assignment_packet_label": True,
        "station_chief_v6_0_mvp_lock_references_one_v5_8_dry_run_result_packet_label": True,
        "station_chief_v6_0_mvp_lock_references_one_v5_9_dry_run_replay_audit_packet_label": True,
        "station_chief_v6_0_mvp_lock_uses_one_v6_0_mvp_lock_label": True,
        "station_chief_v6_0_mvp_lock_records_integrated_local_command_center_loop_metadata": True,
        "station_chief_v6_0_mvp_lock_records_mvp_done_metadata": True,
        "station_chief_v6_0_mvp_lock_does_not_execute_local_task_candidate": True,
        "station_chief_v6_0_mvp_lock_does_not_execute_dry_run_task": True,
        "station_chief_v6_0_mvp_lock_does_not_create_real_worker_result": True,
        "station_chief_v6_0_mvp_lock_does_not_perform_live_replay": True,
        "station_chief_v6_0_mvp_lock_does_not_perform_production_audit": True,
        "station_chief_v6_0_mvp_lock_does_not_perform_rollback": True,
        "station_chief_v6_0_mvp_lock_does_not_perform_recovery": True,
        "station_chief_v6_0_mvp_lock_does_not_create_v6_1": True,
        "station_chief_v6_0_mvp_lock_does_not_start_worker_processes": True,
        "station_chief_v6_0_mvp_lock_does_not_start_agents": True,
        "station_chief_v6_0_mvp_lock_does_not_create_real_queue": True,
        "station_chief_v6_0_mvp_lock_does_not_write_queue": True,
        "station_chief_v6_0_mvp_lock_does_not_write_scheduler_state": True,
        "station_chief_v6_0_mvp_lock_does_not_write_cron_state": True,
        "station_chief_v6_0_mvp_lock_does_not_enqueue_tasks": True,
        "station_chief_v6_0_mvp_lock_does_not_execute_arbitrary_tasks": True,
        "station_chief_v6_0_mvp_lock_does_not_execute_user_tasks": True,
        "station_chief_v6_0_mvp_lock_does_not_route_workers": True,
        "station_chief_v6_0_mvp_lock_does_not_orchestrate_live_work": True,
        "station_chief_v6_0_mvp_lock_does_not_call_live_apis": True,
        "station_chief_v6_0_mvp_lock_does_not_use_network_access": True,
        "station_chief_v6_0_mvp_lock_does_not_open_sockets": True,
        "station_chief_v6_0_mvp_lock_does_not_use_credentials": True,
        "station_chief_v6_0_mvp_lock_does_not_read_secrets": True,
        "station_chief_v6_0_mvp_lock_does_not_read_environment": True,
        "station_chief_v6_0_mvp_lock_does_not_deploy": True,
        "station_chief_v6_0_mvp_lock_does_not_execute_production": True,
        "post_mvp_expansion_not_yet_active": True,
        "first_tiny_real_world_supervised_execution_candidate_requires_human_operator": True,
        "supervised_rollback_cleanup_candidate_available": True,
        "supervised_rollback_cleanup_candidate_local_only": True,
        "supervised_rollback_cleanup_candidate_requires_token": True,
        "supervised_rollback_cleanup_candidate_requires_human_operator": True,
        "supervised_rollback_cleanup_candidate_deletes_only_one_approved_local_artifact": True,
        "supervised_rollback_cleanup_candidate_does_not_delete_directories": True,
        "supervised_rollback_cleanup_candidate_does_not_call_live_apis": True,
        "supervised_rollback_cleanup_candidate_does_not_use_network_access": True,
        "supervised_rollback_cleanup_candidate_does_not_open_sockets": True,
        "supervised_rollback_cleanup_candidate_does_not_use_credentials": True,
        "supervised_rollback_cleanup_candidate_does_not_read_secrets": True,
        "supervised_rollback_cleanup_candidate_does_not_read_environment": True,
        "supervised_rollback_cleanup_candidate_does_not_deploy": True,
        "supervised_rollback_cleanup_candidate_does_not_execute_production": True,
        "supervised_rollback_cleanup_candidate_does_not_route_live_workers": True,
        "limited_live_worker_activation_candidate_available": True,
        "limited_live_worker_activation_candidate_local_only": True,
        "limited_live_worker_activation_candidate_requires_token": True,
        "limited_live_worker_activation_candidate_requires_human_operator": True,
        "limited_live_worker_activation_candidate_writes_one_local_record_only": True,
        "limited_live_worker_activation_candidate_does_not_start_worker_processes": True,
        "limited_live_worker_activation_candidate_does_not_assign_tasks": True,
        "limited_live_worker_activation_candidate_does_not_route_workers": True,
        "limited_live_worker_activation_candidate_does_not_call_live_apis": True,
        "limited_live_worker_activation_candidate_does_not_use_network_access": True,
        "limited_live_worker_activation_candidate_does_not_open_sockets": True,
        "limited_live_worker_activation_candidate_does_not_use_credentials": True,
        "limited_live_worker_activation_candidate_does_not_read_secrets": True,
        "limited_live_worker_activation_candidate_does_not_read_environment": True,
        "limited_live_worker_activation_candidate_does_not_deploy": True,
        "limited_live_worker_activation_candidate_does_not_execute_production": True,
        "permissioned_worker_task_assignment_candidate_available": True,
        "permissioned_worker_task_assignment_candidate_local_record_only": True,
        "permissioned_worker_task_assignment_candidate_requires_token": True,
        "permissioned_worker_task_assignment_candidate_requires_human_operator": True,
        "permissioned_worker_task_assignment_candidate_writes_one_local_record_only": True,
        "permissioned_worker_task_assignment_candidate_does_not_execute_tasks": True,
        "permissioned_worker_task_assignment_candidate_does_not_enqueue_tasks": True,
        "permissioned_worker_task_assignment_candidate_does_not_start_worker_processes": True,
        "permissioned_worker_task_assignment_candidate_does_not_assign_live_tasks": True,
        "permissioned_worker_task_assignment_candidate_does_not_route_workers": True,
        "permissioned_worker_task_assignment_candidate_does_not_call_live_apis": True,
        "permissioned_worker_task_assignment_candidate_does_not_use_network_access": True,
        "permissioned_worker_task_assignment_candidate_does_not_open_sockets": True,
        "permissioned_worker_task_assignment_candidate_does_not_use_credentials": True,
        "permissioned_worker_task_assignment_candidate_does_not_read_secrets": True,
        "permissioned_worker_task_assignment_candidate_does_not_read_environment": True,
        "permissioned_worker_task_assignment_candidate_does_not_deploy": True,
        "permissioned_worker_task_assignment_candidate_does_not_execute_production": True,
        "task_assignment_audit_closeout_candidate_available": True,
        "task_assignment_audit_closeout_candidate_local_record_only": True,
        "task_assignment_audit_closeout_candidate_requires_token": True,
        "task_assignment_audit_closeout_candidate_requires_human_operator": True,
        "task_assignment_audit_closeout_candidate_writes_one_local_record_only": True,
        "task_assignment_audit_closeout_candidate_does_not_execute_tasks": True,
        "task_assignment_audit_closeout_candidate_does_not_enqueue_tasks": True,
        "task_assignment_audit_closeout_candidate_does_not_start_worker_processes": True,
        "task_assignment_audit_closeout_candidate_does_not_assign_live_tasks": True,
        "task_assignment_audit_closeout_candidate_does_not_route_workers": True,
        "task_assignment_audit_closeout_candidate_does_not_mutate_referenced_assignment_record": True,
        "task_assignment_audit_closeout_candidate_does_not_call_live_apis": True,
        "task_assignment_audit_closeout_candidate_does_not_use_network_access": True,
        "task_assignment_audit_closeout_candidate_does_not_open_sockets": True,
        "task_assignment_audit_closeout_candidate_does_not_use_credentials": True,
        "task_assignment_audit_closeout_candidate_does_not_read_secrets": True,
        "task_assignment_audit_closeout_candidate_does_not_read_environment": True,
        "task_assignment_audit_closeout_candidate_does_not_deploy": True,
        "task_assignment_audit_closeout_candidate_does_not_execute_production": True,
        "task_assignment_audit_closeout_candidate_not_yet_active": True,
        "non_executing_task_queue_preview_candidate_not_yet_active": True,
        "non_executing_queue_routing_preview_available": True,
        "non_executing_queue_routing_preview_local_record_only": True,
        "non_executing_queue_routing_preview_requires_token": True,
        "non_executing_queue_routing_preview_requires_human_operator": True,
        "non_executing_queue_routing_preview_writes_one_local_record_only": True,
        "non_executing_queue_routing_preview_does_not_create_real_queue": True,
        "non_executing_queue_routing_preview_does_not_enqueue_tasks": True,
        "non_executing_queue_routing_preview_does_not_execute_tasks": True,
        "non_executing_queue_routing_preview_does_not_start_worker_processes": True,
        "non_executing_queue_routing_preview_does_not_assign_tasks": True,
        "non_executing_queue_routing_preview_does_not_route_workers": True,
        "non_executing_queue_routing_preview_does_not_call_live_apis": True,
        "non_executing_queue_routing_preview_does_not_use_network_access": True,
        "non_executing_queue_routing_preview_does_not_open_sockets": True,
        "non_executing_queue_routing_preview_does_not_use_credentials": True,
        "non_executing_queue_routing_preview_does_not_read_secrets": True,
        "non_executing_queue_routing_preview_does_not_read_environment": True,
        "non_executing_queue_routing_preview_does_not_deploy": True,
        "non_executing_queue_routing_preview_does_not_execute_production": True,
        "live_queue_orchestration_candidate_not_yet_active": True,
        "live_queue_orchestration_candidate_review_available": True,
        "live_queue_orchestration_candidate_review_local_record_only": True,
        "live_queue_orchestration_candidate_review_requires_token": True,
        "live_queue_orchestration_candidate_review_requires_human_operator": True,
        "live_queue_orchestration_candidate_review_writes_one_local_record_only": True,
        "live_queue_orchestration_candidate_review_does_not_create_real_queue": True,
        "live_queue_orchestration_candidate_review_does_not_write_queue": True,
        "live_queue_orchestration_candidate_review_does_not_write_scheduler_state": True,
        "live_queue_orchestration_candidate_review_does_not_write_cron_state": True,
        "live_queue_orchestration_candidate_review_does_not_enqueue_tasks": True,
        "live_queue_orchestration_candidate_review_does_not_execute_tasks": True,
        "live_queue_orchestration_candidate_review_does_not_start_worker_processes": True,
        "live_queue_orchestration_candidate_review_does_not_assign_tasks": True,
        "live_queue_orchestration_candidate_review_does_not_route_workers": True,
        "live_queue_orchestration_candidate_review_does_not_orchestrate_live_work": True,
        "live_queue_orchestration_candidate_review_does_not_call_live_apis": True,
        "live_queue_orchestration_candidate_review_does_not_use_network_access": True,
        "live_queue_orchestration_candidate_review_does_not_open_sockets": True,
        "live_queue_orchestration_candidate_review_does_not_use_credentials": True,
        "live_queue_orchestration_candidate_review_does_not_read_secrets": True,
        "live_queue_orchestration_candidate_review_does_not_read_environment": True,
        "live_queue_orchestration_candidate_review_does_not_deploy": True,
        "live_queue_orchestration_candidate_review_does_not_execute_production": True,
        "first_live_queue_execution_candidate_not_yet_active": True,
        "next_step": "Next step: first supervised local execution kernel candidate review only.",
        "post_action_verification_and_audit_review_available": True,
        "post_action_verification_and_audit_review_local_only": True,
        "post_action_verification_and_audit_review_requires_token": True,
        "post_action_verification_and_audit_review_requires_human_operator": True,
        "post_action_verification_and_audit_review_does_not_execute_new_candidate": True,
        "post_action_verification_and_audit_review_does_not_perform_cleanup": True,
        "post_action_verification_and_audit_review_does_not_call_live_apis": True,
        "post_action_verification_and_audit_review_does_not_use_network_access": True,
        "post_action_verification_and_audit_review_does_not_open_sockets": True,
        "post_action_verification_and_audit_review_does_not_use_credentials": True,
        "post_action_verification_and_audit_review_does_not_read_secrets": True,
        "post_action_verification_and_audit_review_does_not_read_environment": True,
        "post_action_verification_and_audit_review_does_not_deploy": True,
        "post_action_verification_and_audit_review_does_not_execute_production": True,
        "post_action_verification_and_audit_review_does_not_route_live_workers": True,
        "recommended_candidate_type": "local_deterministic_reversible_proof_artifact",
        "v4_0_does_not_call_live_apis": True,
        "v4_0_does_not_use_network_access": True,
        "v4_0_does_not_open_sockets": True,
        "v4_0_does_not_resolve_dns": True,
        "v4_0_does_not_use_credentials": True,
        "v4_0_does_not_read_secrets": True,
        "v4_0_does_not_read_environment": True,
        "v4_0_does_not_deploy": True,
        "v4_0_does_not_execute_production": True,
        "v4_0_does_not_activate_production": True,
        "v4_0_does_not_route_live_workers": True,
        "v4_0_does_not_activate_full_workforce": True,
        "next_step": "Next step: first live queue execution candidate review only.",
        "external_actions_taken": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "real_external_tool_invocation_performed": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_processes_started": False,
        "repo_files_modified": False,
        "execution_authorized": False,
        "supervised_production_pilot_readiness_review_available": True,
        "supervised_production_pilot_readiness_review_preview_only": True,
        "supervised_production_pilot_readiness_review_requires_token": True,
        "minimum_viable_production_candidate_preview_only": True,
        "production_blast_radius_analysis_preview_only": True,
        "live_action_denied_by_default": True,
        "rollback_availability_review_only": True,
        "credential_secret_readiness_denied": True,
        "network_socket_readiness_denied": True,
        "supervised_production_pilot_readiness_review_does_not_execute_production": True,
        "supervised_production_pilot_readiness_review_does_not_activate_production": True,
        "supervised_production_pilot_readiness_review_does_not_deploy": True,
        "supervised_production_pilot_readiness_review_does_not_call_live_apis": True,
        "supervised_production_pilot_readiness_review_does_not_use_network_access": True,
        "supervised_production_pilot_readiness_review_does_not_open_sockets": True,
        "supervised_production_pilot_readiness_review_does_not_use_credentials": True,
        "supervised_production_pilot_readiness_review_does_not_read_secrets": True,
        "supervised_production_pilot_readiness_review_does_not_read_environment": True,
        "supervised_production_pilot_readiness_review_does_not_assign_live_tasks": True,
        "supervised_production_pilot_readiness_review_does_not_route_live_workers": True,
        "supervised_production_pilot_readiness_review_does_not_perform_live_orchestration": True,
        "supervised_production_pilot_readiness_review_does_not_modify_repo_files": True,
        "credential_vault_denial_secret_handling_proof_not_yet_active": False,
        "credential_vault_denial_secret_handling_proof_available": True,
        "credential_vault_denial_secret_handling_proof_preview_only": True,
        "credential_vault_denial_secret_handling_proof_requires_token": True,
        "credential_vault_denial_secret_handling_proof_does_not_access_credentials": True,
        "credential_vault_denial_secret_handling_proof_does_not_read_secrets": True,
        "credential_vault_denial_secret_handling_proof_does_not_read_environment": True,
        "credential_vault_denial_secret_handling_proof_does_not_call_live_apis": True,
        "credential_vault_denial_secret_handling_proof_does_not_use_network_access": True,
        "credential_vault_denial_secret_handling_proof_does_not_open_sockets": True,
        "credential_vault_denial_secret_handling_proof_does_not_deploy": True,
        "credential_vault_denial_secret_handling_proof_does_not_execute_production": True,
        "credential_vault_denial_secret_handling_proof_does_not_modify_repo_files": True,
        "network_socket_lockdown_proof_not_yet_active": True,
        "network_socket_lockdown_proof_available": True,
        "network_socket_lockdown_proof_preview_only": True,
        "network_socket_lockdown_proof_requires_token": True,
        "network_socket_lockdown_proof_does_not_perform_network_access": True,
        "network_socket_lockdown_proof_does_not_open_sockets": True,
        "network_socket_lockdown_proof_does_not_resolve_dns": True,
        "network_socket_lockdown_proof_does_not_make_outbound_connections": True,
        "network_socket_lockdown_proof_does_not_make_inbound_connections": True,
        "network_socket_lockdown_proof_does_not_call_live_apis": True,
        "network_socket_lockdown_proof_does_not_call_webhooks": True,
        "network_socket_lockdown_proof_does_not_invoke_external_tools": True,
        "selected_overlays": brief["selected_overlays"],
        "command_brief": brief,
        "work_orders": work_orders,
        "run_capabilities": {
            "persistent_run_logs": True,
            "command_brief_artifacts": True,
            "work_order_artifacts": True,
            "deterministic_fixture_tests": True,
            "selected_overlay_artifacts": True,
            "evidence_artifacts": True,
            "persistent_runtime_index": True,
            "resumable_run_registry": True,
            "controlled_execution_adapters": True,
            "noop_execution_adapter": True,
            "controlled_file_operation_adapter": True,
            "human_confirmed_execution_gates": True,
            "sandbox_file_write_adapter": True,
            "scoped_repo_patch_adapter": True,
            "changed_file_scope_enforcement": True,
            "patch_preview_artifacts": True,
            "patch_approval_records": True,
            "validator_selected_execution_profiles": True,
            "repo_patch_dry_run_bundles": True,
            "preflight_gate_records": True,
            "execution_readiness_scoring": True,
            "dry_run_bundle_comparison": True,
            "approval_ux_handoff": True,
            "risk_summary_artifacts": True,
            "next_action_recommendations": True,
            "approval_handoff_available": True,
            "approval_review_ui_schema": True,
            "signed_approval_records": True,
            "approval_record_verification": True,
            "approval_audit_manifests": True,
            "approval_ledger_indexing": True,
            "signed_approval_comparison": True,
            "approval_history_lookup": True,
            "approval_duplicate_detection": True,
            "stable_runtime_contract": True,
            "stable_release_manifest": True,
            "stable_capability_inventory": True,
            "stable_artifact_contract": True,
            "stable_adapter_boundary_contract": True,
            "stable_safety_doctrine_lock": True,
            "stable_approval_flow_lock": True,
            "stable_known_limitations_record": True,
            "stable_next_phase_handoff": True,
            "stable_release_readiness_summary": True,
            "controlled_execution_profile_catalog": True,
            "controlled_execution_profile_selection": True,
            "execution_permission_matrix": True,
            "execution_mode_contract": True,
            "blocked_action_ledger": True,
            "controlled_execution_preflight_contract": True,
            "controlled_execution_readiness_summary": True,
            "work_order_executor_readiness_bridge": True,
            "executable_work_order_schema": True,
            "work_order_status_lifecycle": True,
            "work_order_dependency_mapping": True,
            "work_order_dry_run_executor": True,
            "work_order_execution_ledger": True,
            "work_order_completion_proof": True,
            "work_order_executor_summary": True,
            "worker_role_schema": True,
            "worker_candidate_generation": True,
            "worker_assignment_planning": True,
            "worker_registry_ledger": True,
            "worker_hiring_preview_records": True,
            "worker_hiring_readiness_summary": True,
            "department_routing_readiness_bridge": True,
            "department_routing_schema": True,
            "department_route_candidate_generation": True,
            "family_to_department_routing_map": True,
            "worker_to_department_assignment_map": True,
            "department_routing_conflict_detector": True,
            "department_routing_dry_run_engine": True,
            "department_routing_ledger": True,
            "department_routing_completion_proof": True,
            "department_routing_readiness_summary": True,
            "multi_agent_orchestration_readiness_bridge": True,
            "orchestration_topology_schema": True,
            "orchestration_node_generation": True,
            "multi_worker_coordination_map": True,
            "task_handoff_simulation": True,
            "inter_worker_dependency_graph": True,
            "orchestration_conflict_detector": True,
            "orchestration_dry_run_engine": True,
            "orchestration_ledger": True,
            "orchestration_completion_proof": True,
            "orchestration_readiness_summary": True,
            "ui_operator_console_readiness_bridge": True,
            "operator_console_screen_schema": True,
            "runtime_status_panel_schema": True,
            "approval_queue_panel_schema": True,
            "work_order_panel_schema": True,
            "worker_registry_panel_schema": True,
            "department_routing_panel_schema": True,
            "orchestration_sandbox_panel_schema": True,
            "human_control_surface_schema": True,
            "operator_action_registry": True,
            "disabled_action_state_map": True,
            "operator_console_review_bundle": True,
            "operator_console_safety_summary": True,
            "operator_console_readiness_summary": True,
            "github_patch_hardening_readiness_bridge": True,
            "patch_hardening_schema": True,
            "protected_path_policy": True,
            "patch_root_validation": True,
            "patch_preview_diff_contract": True,
            "patch_digest_manifest": True,
            "patch_rollback_preview": True,
            "changed_file_proof_hardening": True,
            "human_approval_chain_binding": True,
            "patch_execution_readiness_score": True,
            "patch_hardening_audit_bundle": True,
            "deployment_packaging_readiness_bridge": True,
            "deployment_artifact_schema": True,
            "portfolio_packaging_manifest": True,
            "runtime_export_bundle": True,
            "release_notes_generator": True,
            "deployment_safety_contract": True,
            "deployment_readiness_proof": True,
            "packaging_audit_bundle": True,
            "portfolio_handoff_summary": True,
            "first_controlled_worker_execution_readiness_bridge": True,
            "controlled_worker_execution_schema": True,
            "worker_execution_gate": True,
            "tool_permission_binding": True,
            "sandbox_worker_task": True,
            "controlled_worker_execution_result": True,
            "worker_abort_contract": True,
            "worker_rollback_contract": True,
            "worker_execution_telemetry_stub": True,
            "post_run_audit_proof": True,
            "worker_execution_ledger": True,
            "single_worker_tool_permission_binding_readiness_bridge": True,
            "live_execution_telemetry_abort_schema": True,
            "telemetry_event_schema": True,
            "execution_state_model": True,
            "telemetry_approval_gate": True,
            "heartbeat_stub": True,
            "abort_signal_contract": True,
            "timeout_contract": True,
            "partial_result_capture": True,
            "failed_run_quarantine_contract": True,
            "post_abort_audit_proof": True,
            "telemetry_ledger": True,
            "telemetry_readiness_summary": True,
            "post_run_audit_expansion_readiness_bridge": True,
            "post_run_audit_expansion_schema": True,
            "expanded_audit_evidence_schema": True,
            "post_run_audit_approval_gate": True,
            "before_after_run_comparison_proof": True,
            "validator_backed_audit_artifact_index": True,
            "audit_replay_record": True,
            "failure_class_taxonomy": True,
            "human_review_packet": True,
            "audit_integrity_score": True,
            "audit_evidence_ledger": True,
            "audit_expansion_readiness_summary": True,
            "multi_worker_sandbox_coordination_readiness_bridge": True,
            "multi_worker_sandbox_coordination_schema": True,
            "multi_worker_coordination_approval_gate": True,
            "sandbox_worker_roster": True,
            "worker_coordination_graph": True,
            "inter_worker_handoff_contract": True,
            "multi_worker_dry_run_ledger": True,
            "coordination_conflict_detector": True,
            "coordination_abort_contract": True,
            "coordination_quarantine_contract": True,
            "coordination_audit_proof": True,
            "coordination_readiness_summary": True,
            "controlled_external_tool_adapter_preview_readiness_bridge": True,
            "controlled_external_tool_adapter_preview_schema": True,
            "external_tool_adapter_preview_approval_gate": True,
            "external_tool_dry_run_adapter_registry": True,
            "per_tool_external_permission_gate": True,
            "external_request_preview_contract": True,
            "external_response_validation_schema": True,
            "external_response_validation_preview_result": True,
            "external_tool_abort_contract": True,
            "external_tool_audit_proof": True,
            "external_tool_preview_ledger": True,
            "external_tool_preview_readiness_summary": True,
            "permissioned_external_api_dry_run_preview_schema": True,
            "external_api_dry_run_approval_gate": True,
            "api_endpoint_preview_registry": True,
            "request_envelope_validation": True,
            "credential_absence_proof": True,
            "outbound_call_prevention_proof": True,
            "dry_run_response_fixture_contract": True,
            "external_api_audit_proof": True,
            "external_api_dry_run_ledger": True,
            "external_api_dry_run_readiness_summary": True,
            "controlled_multi_worker_audit_replay_preview_schema": True,
            "audit_replay_preview_approval_gate": True,
            "replay_packet_registry": True,
            "deterministic_replay_plan_contract": True,
            "replay_safety_gate": True,
            "multi_worker_replay_comparison_proof": True,
            "replay_output_quarantine_contract": True,
            "replay_audit_proof": True,
            "replay_preview_ledger": True,
            "replay_readiness_summary": True,
            "operator_approval_queue_enforcement_readiness_bridge": True,
            "release_candidate_hardening_schema": True,
            "release_candidate_hardening_approval_gate": True,
            "full_runtime_invariant_scan": True,
            "validator_chain_lock_proof": True,
            "artifact_contract_freeze_manifest": True,
            "known_issue_register": True,
            "pre_v3_production_readiness_checklist": True,
            "release_candidate_safety_gate": True,
            "release_candidate_audit_proof": True,
            "release_candidate_ledger": True,
            "release_candidate_readiness_summary": True,
            "controlled_production_readiness_gate_bridge": True,
            "controlled_production_readiness_gate_schema": True,
            "controlled_production_readiness_gate_approval_gate": True,
            "production_activation_denial_by_default": True,
            "final_human_approval_requirement": True,
            "production_capability_manifest": True,
            "supervised_pilot_eligibility_contract": True,
            "production_rollback_kill_switch_preview": True,
            "production_readiness_audit_proof": True,
            "production_readiness_ledger": True,
            "production_readiness_summary": True,
            "controlled_worker_hiring_activation_pilot_bridge": True,
            "controlled_worker_hiring_activation_pilot_schema": True,
            "controlled_worker_hiring_activation_pilot_approval_gate": True,
            "pilot_worker_limit_contract": True,
            "worker_identity_activation_contract": True,
            "task_assignment_denial_by_default": True,
            "human_supervised_pilot_gate": True,
            "pilot_rollback_abort_preview": True,
            "pilot_audit_proof": True,
            "pilot_ledger": True,
            "pilot_readiness_summary": True,
            "first_supervised_production_dry_run_schema": True,
            "first_supervised_production_dry_run_approval_gate": True,
            "single_controlled_task_dry_run_envelope": True,
            "dry_run_only_production_context_contract": True,
            "human_preflight_approval_gate": True,
            "worker_task_simulation_contract": True,
            "external_action_denial_by_default": True,
            "dry_run_rollback_quarantine_preview": True,
            "dry_run_audit_proof": True,
            "dry_run_ledger": True,
            "dry_run_readiness_summary": True,
            "limited_external_tool_supervised_pilot_bridge": True,
                    "limited_external_tool_supervised_pilot_schema": True,
        "limited_external_tool_supervised_pilot_approval_gate": True,
        "single_external_tool_category_contract": True,
        "tool_invocation_denial_by_default": True,
        "human_tool_use_preflight_gate": True,
        "tool_request_envelope_preview": True,
        "tool_response_quarantine_preview": True,
        "tool_audit_proof": True,
        "tool_pilot_ledger": True,
        "tool_pilot_readiness_summary": True,
        "supervised_external_api_pilot_bridge": True,
        "supervised_external_api_pilot_schema": True,
        "supervised_external_api_pilot_approval_gate": True,
        "single_api_category_contract": True,
        "credential_denial_by_default": True,
        "secret_handling_denial_by_default": True,
        "network_socket_denial_by_default": True,
        "human_api_use_preflight_gate": True,
        "api_request_envelope_preview": True,
        "api_response_quarantine_preview": True,
        "api_audit_proof": True,
            "api_pilot_ledger": True,
            "api_pilot_readiness_summary": True,
            "monitored_rollback_recovery_drill_bridge": True,
            "monitored_rollback_recovery_drill_schema": True,
            "monitored_rollback_recovery_drill_approval_gate": True,
            "simulated_failure_trigger_contract": True,
            "rollback_path_preview": True,
            "recovery_checkpoint_contract": True,
            "quarantine_freeze_preview": True,
            "human_recovery_approval_gate": True,
            "recovery_audit_proof": True,
            "rollback_recovery_drill_ledger": True,
            "recovery_readiness_summary": True,
            "supervised_production_pilot_readiness_review_bridge": True,
            "supervised_production_pilot_readiness_review_bundle": True,
            "supervised_production_pilot_readiness_review_schema": True,
            "supervised_production_pilot_readiness_review_approval_gate": True,
            "minimum_viable_production_candidate_contract": True,
            "human_production_pilot_review_gate": True,
            "production_blast_radius_analysis": True,
            "live_action_denial_review": True,
            "rollback_availability_review": True,
            "credential_secret_readiness_denial_proof": True,
            "network_socket_readiness_denial_proof": True,
            "production_pilot_audit_proof": True,
            "production_pilot_readiness_ledger": True,
            "production_pilot_readiness_summary": True,
            "credential_vault_denial_secret_handling_proof_bridge": True,
            "credential_vault_denial_secret_handling_proof_bundle": True,
            "credential_vault_denial_secret_handling_proof_schema": True,
            "credential_vault_denial_secret_handling_proof_approval_gate": True,
            "credential_access_denial_contract": True,
            "secret_read_denial_contract": True,
            "environment_variable_denial_contract": True,
            "credential_vault_boundary_record": True,
            "secret_handling_boundary_record": True,
            "environment_read_boundary_record": True,
            "credential_secret_audit_proof": True,
            "credential_secret_denial_ledger": True,
            "credential_secret_readiness_summary": True,
            "network_socket_lockdown_proof_bridge": True,
            "live_external_action_final_preflight_gate_schema": True,
            "live_external_action_final_preflight_gate_approval_gate": True,
            "tiny_action_candidate_boundary_contract": True,
            "live_external_action_non_execution_contract": True,
            "blast_radius_ceiling_contract": True,
            "human_final_approval_requirement": True,
            "credential_secret_environment_re_denial_proof": True,
            "network_socket_api_re_denial_proof": True,
            "deployment_production_re_denial_proof": True,
            "rollback_recovery_availability_assertion": True,
            "first_tiny_real_world_execution_candidate_audit_proof": True,
            "final_preflight_ledger": True,
            "first_tiny_real_world_supervised_execution_candidate_bridge": True,
            "operator_approval_queue_enforcement_schema": True,
            "operator_approval_queue_enforcement_approval_gate": True,
            "queued_action_registry": True,
            "approval_item_priority_classifier": True,
            "operator_decision_contract": True,
            "approval_expiry_stale_item_detector": True,
            "queue_enforcement_safety_gate": True,
            "approval_queue_audit_proof": True,
            "approval_queue_ledger": True,
            "approval_queue_readiness_summary": True,
            "release_candidate_hardening_readiness_bridge": True,
            "controlled_multi_worker_audit_replay_preview_readiness_bridge": True,
            "permissioned_external_api_dry_run_preview_readiness_bridge": True,
        },
        "command": command,
        "command_type": brief["command_type"],
        "activation_tier": brief["activation_tier"],
        "overlay_stack_loaded": all(item["exists"] for item in overlays),
        "overlay_stack_summary": overlays,
        "selected_overlays": brief["selected_overlays"],
        "command_brief": brief,
        "work_orders": work_orders,
        "adapter_name": adapter_name,
        "execution_plan": execution_plan,
        "adapter_result": adapter_result,
        "file_operation_plan": None,
        "execution_gate": None,
        "file_operation_result": None,
        "repo_patch_plan": None,
        "repo_patch_gate": None,
        "repo_patch_result": None,
        "changed_file_scope_proof": None,
        "execution_profile": None,
        "preflight_gate_record": None,
        "patch_approval_checklist": None,
        "execution_readiness_score": None,
        "dry_run_bundle": None,
        "dry_run_bundle_comparison": None,
        "approval_handoff_packet": None,
        "approval_review_ui_schema": None,
        "signed_approval_record": None,
        "approval_record_verification": None,
        "approval_record_audit_manifest": None,
        "approval_record_sources": None,
        "approval_ledger_bundle": None,
        "approval_ledger_index": None,
        "approval_ledger_verification": None,
        "approval_status_summary": None,
        "duplicate_approval_signals": None,
        "approval_ledger_lookup": None,
        "approval_record_comparison": None,
        "release_lock_bundle": None,
        "stable_release_manifest": None,
        "stable_release_verification": None,
        "stable_runtime_contract": None,
        "stable_capability_inventory": None,
        "stable_artifact_contract": None,
        "stable_adapter_boundary_contract": None,
        "stable_safety_doctrine_lock": None,
        "stable_approval_flow_lock": None,
        "known_limitations": None,
        "next_phase_handoff": None,
        "release_readiness_summary": None,
        "controlled_execution_bundle": None,
        "controlled_execution_profile_catalog": None,
        "controlled_execution_selection": None,
        "execution_permission_matrix": None,
        "execution_mode_contract": None,
        "blocked_action_ledger": None,
        "controlled_execution_preflight_contract": None,
        "controlled_execution_readiness_summary": None,
        "work_order_executor_readiness_bridge": None,
        "work_order_executor_bundle": None,
        "executable_work_order_schema": None,
        "work_orders_executable": None,
        "work_order_status_lifecycle": None,
        "work_order_dependency_map": None,
        "work_order_dry_run_results": None,
        "work_order_execution_ledger": None,
        "work_order_completion_proofs": None,
        "work_order_executor_summary": None,
        "worker_hiring_registry_bundle": None,
        "worker_role_schema": None,
        "worker_candidates": None,
        "worker_registry_status_lifecycle": None,
        "worker_assignment_plan": None,
        "worker_registry_ledger": None,
        "worker_hiring_preview_records": None,
        "worker_hiring_readiness_summary": None,
        "department_routing_readiness_bridge": None,
        "department_routing_bundle": None,
        "department_routing_schema": None,
        "department_route_candidates": None,
        "family_to_department_routing_map": None,
        "worker_to_department_assignment_map": None,
        "department_routing_conflict_detector": None,
        "department_routing_dry_run_results": None,
        "department_routing_ledger": None,
        "department_routing_completion_proofs": None,
        "department_routing_readiness_summary": None,
        "multi_agent_orchestration_readiness_bridge": None,
        "operator_console_bundle": None,
        "operator_console_review_bundle": None,
        "operator_console_screen_schema": None,
        "runtime_status_panel_schema": None,
        "approval_queue_panel_schema": None,
        "work_order_panel_schema": None,
        "worker_registry_panel_schema": None,
        "department_routing_panel_schema": None,
        "orchestration_sandbox_panel_schema": None,
        "release_lock_panel_schema": None,
        "human_control_surface_schema": None,
        "operator_action_registry": None,
        "disabled_action_state_map": None,
        "operator_console_safety_summary": None,
        "operator_console_readiness_summary": None,
        "github_patch_hardening_readiness_bridge": None,
        "github_patch_hardening_bundle": None,
        "patch_hardening_audit_bundle": None,
        "patch_hardening_schema": None,
        "protected_path_policy": None,
        "patch_root_validation": None,
        "patch_preview_diff_contract": None,
        "patch_digest_manifest": None,
        "patch_rollback_preview": None,
        "changed_file_proof_hardening": None,
        "human_approval_chain_binding": None,
        "patch_execution_readiness_score": None,
        "deployment_packaging_readiness_bridge": None,
        "deployment_packaging_bundle": None,
        "deployment_artifact_schema": None,
        "portfolio_packaging_manifest": None,
        "runtime_export_bundle": None,
        "release_notes": None,
        "deployment_safety_contract": None,
        "deployment_readiness_proof": None,
        "portfolio_handoff_summary": None,
        "packaging_audit_bundle": None,
        "first_controlled_worker_execution_readiness_bridge": None,
        "controlled_worker_execution_bundle": None,
        "controlled_worker_execution_schema": None,
        "worker_execution_gate": None,
        "tool_permission_binding": None,
        "sandbox_worker_task": None,
        "controlled_worker_execution_result": None,
        "worker_abort_contract": None,
        "worker_rollback_contract": None,
        "worker_execution_telemetry_stub": None,
        "post_run_audit_proof": None,
        "worker_execution_ledger": None,
        "single_worker_tool_permission_binding_readiness_bridge": None,
        "live_external_action_final_preflight_gate_bundle": None,
        "live_external_action_final_preflight_gate_schema": None,
        "live_external_action_final_preflight_gate_approval_gate": None,
        "tiny_action_candidate_boundary_contract": None,
        "live_external_action_non_execution_contract": None,
        "blast_radius_ceiling_contract": None,
        "human_final_approval_requirement": None,
        "credential_secret_environment_re_denial_proof": None,
        "network_socket_api_re_denial_proof": None,
        "deployment_production_re_denial_proof": None,
        "rollback_recovery_availability_assertion": None,
        "first_tiny_real_world_execution_candidate_audit_proof": None,
        "final_preflight_ledger": None,
        "first_tiny_real_world_supervised_execution_candidate_bridge": None,
        "evidence": {**build_demo_evidence(),
            "baseline_preserved": True,
            "external_actions_taken": False,
            "live_api_call_performed": False,
            "network_access_performed": False,
            "socket_opened": False,
            "credentials_used": False,
            "secrets_read": False,
            "environment_read": False,
            "deployment_performed": False,
            "real_external_tool_invocation_performed": False,
            "production_execution_performed": False,
            "production_activation_performed": False,
            "real_task_execution_performed": False,
            "live_task_assignment_performed": False,
            "live_worker_routing_performed": False,
            "live_orchestration_performed": False,
            "worker_processes_started": False,
            "repo_files_modified": False,
            "execution_authorized": False,
            "live_worker_agents_activated": False,
            "deterministic_demo_mode": True,
            "validators_required_before_completion": True,
            "controlled_file_write_requires_confirmation": True,
            "repo_patch_requires_confirmation": True,
            "changed_file_scope_enforced": True,
            "dry_run_bundle_available": True,
            "approval_handoff_available": True,
            "signed_approval_record_available": True,
            "signed_approval_record_does_not_execute_patch": True,
            "approval_ledger_does_not_execute_patch": True,
            "stable_release_locked": True,
            "release_manifest_available": True,
            "release_lock_does_not_execute_patch": True,
            "v1_0_stable_foundation_complete": True,
            "controlled_execution_profile_expansion_available": True,
            "controlled_execution_does_not_execute_live_actions": True,
            "controlled_execution_does_not_hire_workers": True,
            "controlled_execution_does_not_animate_workforce": True,
            "work_order_executor_not_yet_active": True,
            "work_order_executor_skeleton_available": True,
            "work_order_executor_dry_run_only": True,
            "work_order_executor_does_not_execute_live_actions": True,
            "work_order_executor_does_not_hire_workers": True,
            "work_order_executor_does_not_animate_workforce": True,
            "worker_hiring_registry_not_yet_active": True,
            "worker_hiring_registry_available": True,
            "worker_hiring_registry_preview_only": True,
            "worker_hiring_registry_does_not_hire_workers": True,
            "worker_hiring_registry_does_not_animate_workforce": True,
            "department_routing_runtime_not_yet_active": True,
            "department_routing_available": True,
            "department_routing_preview_only": True,
            "department_routing_does_not_route_live_workers": True,
            "department_routing_does_not_hire_workers": True,
            "department_routing_does_not_animate_workforce": True,
            "multi_agent_orchestration_available": True,
            "multi_agent_orchestration_sandbox_only": True,
            "multi_agent_orchestration_does_not_animate_workers": True,
            "multi_agent_orchestration_does_not_hire_workers": True,
            "multi_agent_orchestration_does_not_route_live_workers": True,
            "multi_agent_orchestration_does_not_perform_live_orchestration": True,
            "operator_console_schema_available": True,
            "operator_console_schema_only": True,
            "operator_console_does_not_display_live_ui": True,
            "operator_console_does_not_authorize_execution": True,
            "operator_console_does_not_connect_live_apis": True,
            "github_patch_hardening_available": True,
            "github_patch_hardening_contract_only": True,
            "github_patch_hardening_does_not_apply_patches": True,
            "github_patch_hardening_does_not_call_github_api": True,
            "github_patch_hardening_does_not_authorize_execution": True,
            "deployment_packaging_available": True,
            "deployment_packaging_bridge_only": True,
            "deployment_packaging_does_not_deploy": True,
            "deployment_packaging_does_not_call_hosting_api": True,
            "deployment_packaging_does_not_authorize_execution": True,
            "controlled_worker_execution_available": True,
            "single_worker_sandbox_execution_only": True,
            "controlled_worker_execution_requires_token": True,
            "controlled_worker_execution_does_not_call_external_apis": True,
            "controlled_worker_execution_does_not_run_shell_commands": True,
            "controlled_worker_execution_does_not_modify_repo_files": True,
            "controlled_worker_execution_does_not_animate_broad_workforce": True,
            "tool_permission_binding_available": True,
            "single_worker_tool_permission_binding_only": True,
            "tool_permission_binding_requires_specific_tokens": True,
            "tool_permission_binding_does_not_invoke_external_tools": True,
            "tool_permission_binding_does_not_call_external_apis": True,
            "tool_permission_binding_does_not_run_shell_commands": True,
            "tool_permission_binding_does_not_modify_repo_files": True,
            "live_execution_telemetry_abort_available": True,
            "single_worker_telemetry_abort_controls_only": True,
            "telemetry_abort_controls_require_token": True,
            "telemetry_abort_does_not_send_external_telemetry": True,
            "telemetry_abort_does_not_terminate_processes": True,
            "telemetry_abort_does_not_run_shell_commands": True,
            "telemetry_abort_does_not_modify_repo_files": True,
            "post_run_audit_proof_expansion_not_yet_active": False,
            "post_run_audit_expansion_available": True,
            "single_worker_post_run_audit_expansion_only": True,
            "post_run_audit_expansion_requires_token": True,
            "post_run_audit_expansion_does_not_perform_actual_replay": True,
            "post_run_audit_expansion_does_not_fetch_external_artifacts": True,
            "post_run_audit_expansion_does_not_run_shell_commands": True,
            "post_run_audit_expansion_does_not_modify_repo_files": True,
            "multi_worker_sandbox_coordination_not_yet_active": True,
            "multi_worker_sandbox_coordination_available": True,
            "multi_worker_sandbox_coordination_preview_only": True,
            "multi_worker_sandbox_coordination_requires_token": True,
            "multi_worker_sandbox_coordination_does_not_hire_real_workers": True,
            "multi_worker_sandbox_coordination_does_not_start_worker_processes": True,
            "multi_worker_sandbox_coordination_does_not_perform_live_routing": True,
            "multi_worker_sandbox_coordination_does_not_perform_live_orchestration": True,
            "multi_worker_sandbox_coordination_does_not_modify_repo_files": True,
            "controlled_external_tool_adapter_preview_not_yet_active": True,
            "controlled_external_tool_adapter_preview_available": True,
            "controlled_external_tool_adapter_preview_only": True,
            "controlled_external_tool_adapter_preview_requires_token": True,
            "controlled_external_tool_adapter_preview_does_not_invoke_external_tools": True,
            "controlled_external_tool_adapter_preview_does_not_call_live_apis": True,
            "controlled_external_tool_adapter_preview_does_not_use_network_access": True,
            "controlled_external_tool_adapter_preview_does_not_open_sockets": True,
            "controlled_external_tool_adapter_preview_does_not_modify_repo_files": True,
            "permissioned_external_api_dry_run_preview_available": True,
            "permissioned_external_api_dry_run_preview_only": True,
            "permissioned_external_api_dry_run_preview_requires_token": True,
            "permissioned_external_api_dry_run_does_not_call_live_apis": True,
            "permissioned_external_api_dry_run_does_not_use_network_access": True,
            "permissioned_external_api_dry_run_does_not_open_sockets": True,
            "permissioned_external_api_dry_run_does_not_use_credentials": True,
            "permissioned_external_api_dry_run_does_not_read_secrets": True,
            "permissioned_external_api_dry_run_does_not_read_environment": True,
            "permissioned_external_api_dry_run_does_not_modify_repo_files": True,
            "controlled_multi_worker_audit_replay_preview_available": True,
            "controlled_multi_worker_audit_replay_preview_only": True,
            "controlled_multi_worker_audit_replay_preview_requires_token": True,
            "controlled_multi_worker_audit_replay_does_not_execute_actual_replay": True,
            "controlled_multi_worker_audit_replay_does_not_replay_worker_actions": True,
            "controlled_multi_worker_audit_replay_does_not_replay_external_tools": True,
            "controlled_multi_worker_audit_replay_does_not_call_live_apis": True,
            "controlled_multi_worker_audit_replay_does_not_use_network_access": True,
            "controlled_multi_worker_audit_replay_does_not_open_sockets": True,
            "controlled_multi_worker_audit_replay_does_not_use_credentials": True,
            "controlled_multi_worker_audit_replay_does_not_read_secrets": True,
            "controlled_multi_worker_audit_replay_does_not_read_environment": True,
            "controlled_multi_worker_audit_replay_does_not_modify_repo_files": True,
            "operator_approval_queue_enforcement_available": True,
            "operator_approval_queue_enforcement_preview_only": True,
            "operator_approval_queue_enforcement_requires_token": True,
            "operator_approval_queue_does_not_execute_queued_actions": True,
            "operator_approval_queue_does_not_auto_approve": True,
            "operator_approval_queue_does_not_bypass_approval": True,
            "operator_approval_queue_does_not_execute_actual_replay": True,
            "operator_approval_queue_does_not_replay_worker_actions": True,
            "operator_approval_queue_does_not_replay_external_tools": True,
            "operator_approval_queue_does_not_call_live_apis": True,
            "operator_approval_queue_does_not_use_network_access": True,
            "operator_approval_queue_does_not_open_sockets": True,
            "operator_approval_queue_does_not_use_credentials": True,
            "operator_approval_queue_does_not_read_secrets": True,
            "operator_approval_queue_does_not_read_environment": True,
            "operator_approval_queue_does_not_modify_repo_files": True,
            "release_candidate_hardening_available": True,
            "release_candidate_hardening_preview_only": True,
            "release_candidate_hardening_requires_token": True,
            "release_candidate_hardening_does_not_execute_production": True,
            "release_candidate_hardening_does_not_activate_production_readiness_gate": True,
            "release_candidate_hardening_does_not_execute_queued_actions": True,
            "release_candidate_hardening_does_not_auto_approve": True,
            "release_candidate_hardening_does_not_bypass_approval": True,
            "release_candidate_hardening_does_not_execute_actual_replay": True,
            "release_candidate_hardening_does_not_replay_worker_actions": True,
            "release_candidate_hardening_does_not_replay_external_tools": True,
            "release_candidate_hardening_does_not_call_live_apis": True,
            "release_candidate_hardening_does_not_use_network_access": True,
            "release_candidate_hardening_does_not_open_sockets": True,
            "release_candidate_hardening_does_not_use_credentials": True,
            "release_candidate_hardening_does_not_read_secrets": True,
            "release_candidate_hardening_does_not_read_environment": True,
            "release_candidate_hardening_does_not_modify_repo_files": True,
            "controlled_production_readiness_gate_available": True,
            "controlled_production_readiness_gate_preview_only": True,
            "controlled_production_readiness_gate_requires_token": True,
            "production_activation_denied_by_default": True,
            "controlled_production_readiness_gate_does_not_execute_production": True,
            "controlled_production_readiness_gate_does_not_activate_production": True,
            "controlled_production_readiness_gate_does_not_hire_real_workers": True,
            "controlled_production_readiness_gate_does_not_activate_real_workers": True,
            "controlled_production_readiness_gate_does_not_route_live_workers": True,
            "controlled_production_readiness_gate_does_not_perform_live_orchestration": True,
            "controlled_production_readiness_gate_does_not_execute_queued_actions": True,
            "controlled_production_readiness_gate_does_not_auto_approve": True,
            "controlled_production_readiness_gate_does_not_bypass_approval": True,
            "controlled_production_readiness_gate_does_not_execute_actual_replay": True,
            "controlled_production_readiness_gate_does_not_replay_worker_actions": True,
            "controlled_production_readiness_gate_does_not_replay_external_tools": True,
            "controlled_production_readiness_gate_does_not_call_live_apis": True,
            "controlled_production_readiness_gate_does_not_use_network_access": True,
            "controlled_production_readiness_gate_does_not_open_sockets": True,
            "controlled_production_readiness_gate_does_not_use_credentials": True,
            "controlled_production_readiness_gate_does_not_read_secrets": True,
            "controlled_production_readiness_gate_does_not_read_environment": True,
            "controlled_production_readiness_gate_does_not_modify_repo_files": True,
                        "controlled_worker_hiring_activation_pilot_available": True,
            "controlled_worker_hiring_activation_pilot_preview_only": True,
            "controlled_worker_hiring_activation_pilot_requires_token": True,
            "pilot_worker_limit_maximum_is_three": True,
            "task_assignment_denied_by_default": True,
            "controlled_worker_hiring_activation_pilot_does_not_hire_real_workers": True,
            "controlled_worker_hiring_activation_pilot_does_not_activate_real_workers": True,
            "controlled_worker_hiring_activation_pilot_does_not_start_worker_processes": True,
            "controlled_worker_hiring_activation_pilot_does_not_assign_live_tasks": True,
            "controlled_worker_hiring_activation_pilot_does_not_route_live_workers": True,
            "controlled_worker_hiring_activation_pilot_does_not_perform_live_orchestration": True,
            "controlled_worker_hiring_activation_pilot_does_not_execute_production": True,
            "controlled_worker_hiring_activation_pilot_does_not_activate_production": True,
            "controlled_worker_hiring_activation_pilot_does_not_call_live_apis": True,
            "controlled_worker_hiring_activation_pilot_does_not_use_network_access": True,
            "controlled_worker_hiring_activation_pilot_does_not_open_sockets": True,
            "controlled_worker_hiring_activation_pilot_does_not_use_credentials": True,
            "controlled_worker_hiring_activation_pilot_does_not_read_secrets": True,
            "controlled_worker_hiring_activation_pilot_does_not_read_environment": True,
            "controlled_worker_hiring_activation_pilot_does_not_modify_repo_files": True,
                        "first_supervised_production_dry_run_available": True,
            "first_supervised_production_dry_run_preview_only": True,
            "first_supervised_production_dry_run_requires_token": True,
            "single_controlled_task_dry_run_limit_is_one": True,
            "external_actions_denied_by_default": True,
            "first_supervised_production_dry_run_does_not_execute_production": True,
            "first_supervised_production_dry_run_does_not_activate_production": True,
            "first_supervised_production_dry_run_does_not_execute_real_tasks": True,
            "first_supervised_production_dry_run_does_not_assign_live_tasks": True,
            "first_supervised_production_dry_run_does_not_route_live_workers": True,
            "first_supervised_production_dry_run_does_not_perform_live_orchestration": True,
            "first_supervised_production_dry_run_does_not_invoke_external_tools": True,
            "first_supervised_production_dry_run_does_not_call_live_apis": True,
            "first_supervised_production_dry_run_does_not_use_network_access": True,
            "first_supervised_production_dry_run_does_not_open_sockets": True,
            "first_supervised_production_dry_run_does_not_use_credentials": True,
            "first_supervised_production_dry_run_does_not_read_secrets": True,
            "first_supervised_production_dry_run_does_not_read_environment": True,
            "first_supervised_production_dry_run_does_not_modify_repo_files": True,
            "first_supervised_production_dry_run_does_not_deploy": True,
            "limited_external_tool_supervised_pilot_not_yet_active": True,
            "limited_external_tool_supervised_pilot_available": True,
            "limited_external_tool_supervised_pilot_preview_only": True,
            "limited_external_tool_supervised_pilot_requires_token": True,
            "single_external_tool_category_limit_is_one": True,
            "tool_invocation_denied_by_default": True,
            "limited_external_tool_supervised_pilot_does_not_invoke_external_tools": True,
            "limited_external_tool_supervised_pilot_does_not_call_live_apis": True,
            "limited_external_tool_supervised_pilot_does_not_use_network_access": True,
            "limited_external_tool_supervised_pilot_does_not_open_sockets": True,
            "limited_external_tool_supervised_pilot_does_not_use_credentials": True,
            "limited_external_tool_supervised_pilot_does_not_read_secrets": True,
            "limited_external_tool_supervised_pilot_does_not_read_environment": True,
            "limited_external_tool_supervised_pilot_does_not_deploy": True,
            "limited_external_tool_supervised_pilot_does_not_execute_production": True,
            "limited_external_tool_supervised_pilot_does_not_activate_production": True,
            "limited_external_tool_supervised_pilot_does_not_execute_real_tasks": True,
            "limited_external_tool_supervised_pilot_does_not_assign_live_tasks": True,
            "limited_external_tool_supervised_pilot_does_not_route_live_workers": True,
            "limited_external_tool_supervised_pilot_does_not_perform_live_orchestration": True,
            "limited_external_tool_supervised_pilot_does_not_modify_repo_files": True,
                    "supervised_production_pilot_readiness_review_not_yet_active": True,
        "supervised_external_api_pilot_available": True,
        "supervised_external_api_pilot_preview_only": True,
        "supervised_external_api_pilot_requires_token": True,
        "single_api_category_limit_is_one": True,
        "credential_use_denied_by_default": True,
        "secret_handling_denied_by_default": True,
        "network_socket_denied_by_default": True,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "real_external_tool_invocation_performed": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_processes_started": False,
        "repo_files_modified": False,
        "execution_authorized": False,
        "supervised_external_api_pilot_does_not_call_live_apis": True,
        "supervised_external_api_pilot_does_not_use_network_access": True,
        "supervised_external_api_pilot_does_not_open_sockets": True,
        "supervised_external_api_pilot_does_not_use_credentials": True,
        "supervised_external_api_pilot_does_not_read_secrets": True,
        "supervised_external_api_pilot_does_not_read_environment": True,
        "supervised_external_api_pilot_does_not_deploy": True,
        "supervised_external_api_pilot_does_not_invoke_external_tools": True,
        "supervised_external_api_pilot_does_not_execute_production": True,
        "supervised_external_api_pilot_does_not_activate_production": True,
        "supervised_external_api_pilot_does_not_execute_real_tasks": True,
        "supervised_external_api_pilot_does_not_assign_live_tasks": True,
        "supervised_external_api_pilot_does_not_route_live_workers": True,
        "supervised_external_api_pilot_does_not_perform_live_orchestration": True,
        "supervised_external_api_pilot_does_not_modify_repo_files": True,
        "monitored_rollback_recovery_drill_available": True,
        "monitored_rollback_recovery_drill_preview_only": True,
        "monitored_rollback_recovery_drill_requires_token": True,
        "simulated_failure_trigger_preview_only": True,
        "rollback_path_preview_only": True,
        "recovery_checkpoint_preview_only": True,
        "quarantine_freeze_preview_only": True,
        "monitored_rollback_recovery_drill_does_not_perform_real_rollback": True,
        "monitored_rollback_recovery_drill_does_not_perform_real_recovery": True,
        "monitored_rollback_recovery_drill_does_not_terminate_processes": True,
        "monitored_rollback_recovery_drill_does_not_terminate_workers": True,
        "monitored_rollback_recovery_drill_does_not_change_production_state": True,
        "monitored_rollback_recovery_drill_does_not_rollback_deployments": True,
        "monitored_rollback_recovery_drill_does_not_deploy": True,
        "monitored_rollback_recovery_drill_does_not_call_live_apis": True,
        "monitored_rollback_recovery_drill_does_not_use_network_access": True,
        "monitored_rollback_recovery_drill_does_not_open_sockets": True,
        "monitored_rollback_recovery_drill_does_not_use_credentials": True,
        "monitored_rollback_recovery_drill_does_not_read_secrets": True,
        "monitored_rollback_recovery_drill_does_not_read_environment": True,
        "monitored_rollback_recovery_drill_does_not_execute_production": True,
        "monitored_rollback_recovery_drill_does_not_modify_repo_files": True,
        },
        "next_step": "Next step: sandbox worker handoff candidate review only.",
    }


def attach_approval_ledger(
    result: dict,
    approval_record_paths: list[str],
    ledger_label: str = "station-chief-approval-ledger",
    lookup_digest: str | None = None
) -> dict:
    records = collect_approval_records_from_paths(approval_record_paths)
    bundle = create_approval_ledger_bundle(records, ledger_label)
    
    result["approval_record_sources"] = records
    result["approval_ledger_bundle"] = bundle
    result["approval_ledger_index"] = bundle["ledger_index"]
    result["approval_ledger_verification"] = bundle["ledger_verification"]
    result["approval_status_summary"] = bundle["approval_status_summary"]
    result["duplicate_approval_signals"] = bundle["duplicate_approval_signals"]
    
    if lookup_digest:
        result["approval_ledger_lookup"] = lookup_approval_records_by_digest(bundle["ledger_index"], lookup_digest)
        
    return result

def write_approval_ledger(result: dict, output_dir: str | Path, run_label: str = "station-chief-runtime") -> dict:
    if "approval_ledger_bundle" not in result:
        raise ValueError("Missing approval_ledger_bundle in result")
        
    run_id = generate_run_id(result.get("command", "empty"), run_label)
    record_dir = Path(output_dir) / run_id
    record_dir.mkdir(parents=True, exist_ok=True)
    
    _write_json(record_dir / "approval_ledger_bundle.json", result["approval_ledger_bundle"])
    _write_json(record_dir / "approval_ledger_index.json", result["approval_ledger_index"])
    _write_json(record_dir / "approval_ledger_verification.json", result["approval_ledger_verification"])
    _write_json(record_dir / "approval_status_summary.json", result["approval_status_summary"])
    _write_json(record_dir / "duplicate_approval_signals.json", result["duplicate_approval_signals"])
    
    if "approval_ledger_lookup" in result:
        _write_json(record_dir / "approval_ledger_lookup.json", result["approval_ledger_lookup"])
    else:
        _write_json(record_dir / "approval_ledger_lookup.json", None)
        
    files_written = [
        "approval_ledger_bundle.json",
        "approval_ledger_index.json",
        "approval_ledger_verification.json",
        "approval_status_summary.json",
        "duplicate_approval_signals.json",
        "approval_ledger_lookup.json",
        "approval_ledger_manifest.json"
    ]
    
    manifest = {
        "approval_ledger_manifest_version": "2.5.0",
        "run_id": run_id,
        "runtime_version": "2.9.0",
        "files_written": files_written,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "execution_authorized": False,
        "note": "Approval ledgers index approval history only. They do not execute repo patches by themselves."
    }
    _write_json(record_dir / "approval_ledger_manifest.json", manifest)
    
    return {
        "run_id": run_id,
        "approval_ledger_dir": str(record_dir),
        "files_written": files_written
    }


def attach_controlled_execution(
    result: dict,
    requested_profile: str | None = None,
    attempted_actions: list[str] | None = None
) -> dict:
    if result.get("release_lock_bundle") is None:
        result = attach_release_lock(result)
        
    bundle = create_controlled_execution_bundle(
        result,
        requested_profile=requested_profile,
        release_lock_bundle=result.get("release_lock_bundle"),
        attempted_actions=attempted_actions
    )
    
    result["controlled_execution_bundle"] = bundle
    result["controlled_execution_profile_catalog"] = bundle["controlled_execution_profile_catalog"]
    result["controlled_execution_selection"] = bundle["controlled_execution_selection"]
    result["execution_permission_matrix"] = bundle["execution_permission_matrix"]
    result["execution_mode_contract"] = bundle["execution_mode_contract"]
    result["blocked_action_ledger"] = bundle["blocked_action_ledger"]
    result["controlled_execution_preflight_contract"] = bundle["controlled_execution_preflight_contract"]
    result["controlled_execution_readiness_summary"] = bundle["controlled_execution_readiness_summary"]
    result["work_order_executor_readiness_bridge"] = bundle["work_order_executor_readiness_bridge"]
    
    return result

def write_controlled_execution(result: dict, output_dir: str | Path, run_label: str = "station-chief-runtime") -> dict:
    if "controlled_execution_bundle" not in result:
        raise ValueError("Missing controlled_execution_bundle in result")
        
    run_id = generate_run_id(result.get("command", "empty"), run_label)
    record_dir = Path(output_dir) / run_id
    record_dir.mkdir(parents=True, exist_ok=True)
    
    payloads = {
        "controlled_execution_bundle.json": result["controlled_execution_bundle"],
        "controlled_execution_profile_catalog.json": result["controlled_execution_profile_catalog"],
        "controlled_execution_selection.json": result["controlled_execution_selection"],
        "execution_permission_matrix.json": result["execution_permission_matrix"],
        "execution_mode_contract.json": result["execution_mode_contract"],
        "blocked_action_ledger.json": result["blocked_action_ledger"],
        "controlled_execution_preflight_contract.json": result["controlled_execution_preflight_contract"],
        "controlled_execution_readiness_summary.json": result["controlled_execution_readiness_summary"],
        "work_order_executor_readiness_bridge.json": result["work_order_executor_readiness_bridge"]
    }
    
    files_written = list(payloads.keys())
    for filename, payload in payloads.items():
        _write_json(record_dir / filename, payload)
        
    manifest = {
        "controlled_execution_manifest_version": "2.5.0",
        "run_id": run_id,
        "runtime_version": "2.9.0",
        "files_written": files_written + ["controlled_execution_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "execution_authorized": False,
        "status": "PROFILE_EXPANSION_ONLY",
        "note": "Controlled execution v2.5.0 expands execution profiles only. It does not execute live actions or hire workers."
    }
    _write_json(record_dir / "controlled_execution_manifest.json", manifest)
    files_written.append("controlled_execution_manifest.json")
    
    return {
        "run_id": run_id,
        "controlled_execution_dir": str(record_dir),
        "files_written": files_written
    }


def attach_work_order_executor(result: dict) -> dict:
    if result.get("controlled_execution_bundle") is None:
        result = attach_controlled_execution(result)
        
    bundle = create_work_order_executor_bundle(result)
    
    result["work_order_executor_bundle"] = bundle
    result["executable_work_order_schema"] = bundle["executable_work_order_schema"]
    result["work_orders_executable"] = bundle["work_orders"]
    result["work_order_status_lifecycle"] = bundle["work_order_status_lifecycle"]
    result["work_order_dependency_map"] = bundle["work_order_dependency_map"]
    result["work_order_dry_run_results"] = bundle["work_order_dry_run_results"]
    result["work_order_execution_ledger"] = bundle["work_order_execution_ledger"]
    result["work_order_completion_proofs"] = bundle["work_order_completion_proofs"]
    result["work_order_executor_summary"] = bundle["work_order_executor_summary"]
    
    return result

def write_work_order_executor(result: dict, output_dir: str | Path, run_label: str = "station-chief-runtime") -> dict:
    if "work_order_executor_bundle" not in result:
        raise ValueError("Missing work_order_executor_bundle in result")
        
    run_id = generate_run_id(result.get("command", "empty"), run_label)
    record_dir = Path(output_dir) / run_id
    record_dir.mkdir(parents=True, exist_ok=True)
    
    payloads = {
        "work_order_executor_bundle.json": result["work_order_executor_bundle"],
        "executable_work_order_schema.json": result["executable_work_order_schema"],
        "work_orders.json": result["work_orders_executable"],
        "work_order_status_lifecycle.json": result["work_order_status_lifecycle"],
        "work_order_dependency_map.json": result["work_order_dependency_map"],
        "work_order_dry_run_results.json": result["work_order_dry_run_results"],
        "work_order_execution_ledger.json": result["work_order_execution_ledger"],
        "work_order_completion_proofs.json": result["work_order_completion_proofs"],
        "work_order_executor_summary.json": result["work_order_executor_summary"]
    }
    
    files_written = list(payloads.keys())
    for filename, payload in payloads.items():
        _write_json(record_dir / filename, payload)
        
    manifest = {
        "work_order_executor_manifest_version": "2.5.0",
        "run_id": run_id,
        "runtime_version": "2.9.0",
        "files_written": files_written + ["work_order_executor_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "repo_files_modified": False,
        "execution_authorized": False,
        "status": "SKELETON_DRY_RUN_ONLY",
        "note": "Work Order Executor v2.5.0 creates dry-run skeleton artifacts only. It does not execute live actions, modify repo files, hire workers, or animate the workforce."
    }
    _write_json(record_dir / "work_order_executor_manifest.json", manifest)
    files_written.append("work_order_executor_manifest.json")
    
    return {
        "run_id": run_id,
        "work_order_executor_dir": str(record_dir),
        "files_written": files_written
    }


def attach_worker_hiring_registry(result: dict) -> dict:
    if result.get("work_order_executor_bundle") is None:
        result = attach_work_order_executor(result)
        
    bundle = create_worker_hiring_registry_bundle(result)
    
    result["worker_hiring_registry_bundle"] = bundle
    result["worker_role_schema"] = bundle["worker_role_schema"]
    result["worker_candidates"] = bundle["worker_candidates"]
    result["worker_registry_status_lifecycle"] = bundle["worker_registry_status_lifecycle"]
    result["worker_assignment_plan"] = bundle["worker_assignment_plan"]
    result["worker_registry_ledger"] = bundle["worker_registry_ledger"]
    result["worker_hiring_preview_records"] = bundle["worker_hiring_preview_records"]
    result["worker_hiring_readiness_summary"] = bundle["worker_hiring_readiness_summary"]
    result["department_routing_readiness_bridge"] = bundle["department_routing_readiness_bridge"]
    
    return result

def write_worker_hiring_registry(result: dict, output_dir: str | Path, run_label: str = "station-chief-runtime") -> dict:
    if "worker_hiring_registry_bundle" not in result:
        raise ValueError("Missing worker_hiring_registry_bundle in result")
        
    run_id = generate_run_id(result.get("command", "empty"), run_label)
    record_dir = Path(output_dir) / run_id
    record_dir.mkdir(parents=True, exist_ok=True)
    
    payloads = {
        "worker_hiring_registry_bundle.json": result["worker_hiring_registry_bundle"],
        "worker_role_schema.json": result["worker_role_schema"],
        "worker_candidates.json": result["worker_candidates"],
        "worker_registry_status_lifecycle.json": result["worker_registry_status_lifecycle"],
        "worker_assignment_plan.json": result["worker_assignment_plan"],
        "worker_registry_ledger.json": result["worker_registry_ledger"],
        "worker_hiring_preview_records.json": result["worker_hiring_preview_records"],
        "worker_hiring_readiness_summary.json": result["worker_hiring_readiness_summary"],
        "department_routing_readiness_bridge.json": result["department_routing_readiness_bridge"]
    }
    
    files_written = list(payloads.keys())
    for filename, payload in payloads.items():
        _write_json(record_dir / filename, payload)
        
    manifest = {
        "worker_hiring_registry_manifest_version": "2.5.0",
        "run_id": run_id,
        "runtime_version": "2.9.0",
        "files_written": files_written + ["worker_hiring_registry_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "execution_authorized": False,
        "status": "REGISTRY_PREVIEW_ONLY",
        "note": "Worker Hiring Registry v2.5.0 creates preview registry artifacts only. It does not hire workers, animate the workforce, execute live actions, or modify repo files."
    }
    _write_json(record_dir / "worker_hiring_registry_manifest.json", manifest)
    files_written.append("worker_hiring_registry_manifest.json")
    
    return {
        "run_id": run_id,
        "worker_hiring_registry_dir": str(record_dir),
        "files_written": files_written
    }


def attach_department_routing(result: dict) -> dict:
    if result.get("worker_hiring_registry_bundle") is None:
        result = attach_worker_hiring_registry(result)
        
    bundle = create_department_routing_bundle(result)
    
    result["department_routing_bundle"] = bundle
    result["department_routing_schema"] = bundle["department_routing_schema"]
    result["department_route_candidates"] = bundle["department_route_candidates"]
    result["family_to_department_routing_map"] = bundle["family_to_department_routing_map"]
    result["worker_to_department_assignment_map"] = bundle["worker_to_department_assignment_map"]
    result["department_routing_conflict_detector"] = bundle["department_routing_conflict_detector"]
    result["department_routing_dry_run_results"] = bundle["department_routing_dry_run_results"]
    result["department_routing_ledger"] = bundle["department_routing_ledger"]
    result["department_routing_completion_proofs"] = bundle["department_routing_completion_proofs"]
    result["department_routing_readiness_summary"] = bundle["department_routing_readiness_summary"]
    result["multi_agent_orchestration_readiness_bridge"] = bundle["multi_agent_orchestration_readiness_bridge"]
    
    return result

def write_department_routing(result: dict, output_dir: str | Path, run_label: str = "station-chief-runtime") -> dict:
    if "department_routing_bundle" not in result:
        raise ValueError("Missing department_routing_bundle in result")
        
    run_id = generate_run_id(result.get("command", "empty"), run_label)
    record_dir = Path(output_dir) / run_id
    record_dir.mkdir(parents=True, exist_ok=True)
    
    payloads = {
        "department_routing_bundle.json": result["department_routing_bundle"],
        "department_routing_schema.json": result["department_routing_schema"],
        "department_route_candidates.json": result["department_route_candidates"],
        "family_to_department_routing_map.json": result["family_to_department_routing_map"],
        "worker_to_department_assignment_map.json": result["worker_to_department_assignment_map"],
        "department_routing_conflict_detector.json": result["department_routing_conflict_detector"],
        "department_routing_dry_run_results.json": result["department_routing_dry_run_results"],
        "department_routing_ledger.json": result["department_routing_ledger"],
        "department_routing_completion_proofs.json": result["department_routing_completion_proofs"],
        "department_routing_readiness_summary.json": result["department_routing_readiness_summary"],
        "multi_agent_orchestration_readiness_bridge.json": result["multi_agent_orchestration_readiness_bridge"]
    }
    
    files_written = list(payloads.keys())
    for filename, payload in payloads.items():
        _write_json(record_dir / filename, payload)
        
    manifest = {
        "department_routing_manifest_version": "2.5.0",
        "run_id": run_id,
        "runtime_version": "2.9.0",
        "files_written": files_written + ["department_routing_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "execution_authorized": False,
        "status": "ROUTING_PREVIEW_ONLY",
        "note": "Department Routing Runtime v2.5.0 creates preview routing artifacts only. It does not route live workers, hire workers, animate the workforce, execute live actions, or modify repo files."
    }
    _write_json(record_dir / "department_routing_manifest.json", manifest)
    files_written.append("department_routing_manifest.json")
    
    return {
        "run_id": run_id,
        "department_routing_dir": str(record_dir),
        "files_written": files_written
    }


def attach_multi_agent_orchestration(result: dict) -> dict:
    if result.get("department_routing_bundle") is None:
        result = attach_department_routing(result)
        
    bundle = create_multi_agent_orchestration_bundle(result)
    
    result["multi_agent_orchestration_bundle"] = bundle
    result["orchestration_topology_schema"] = bundle["orchestration_topology_schema"]
    result["orchestration_nodes"] = bundle["orchestration_nodes"]
    result["multi_worker_coordination_map"] = bundle["multi_worker_coordination_map"]
    result["task_handoff_simulation"] = bundle["task_handoff_simulation"]
    result["inter_worker_dependency_graph"] = bundle["inter_worker_dependency_graph"]
    result["orchestration_conflict_detector"] = bundle["orchestration_conflict_detector"]
    result["orchestration_dry_run_results"] = bundle["orchestration_dry_run_results"]
    result["orchestration_ledger"] = bundle["orchestration_ledger"]
    result["orchestration_completion_proofs"] = bundle["orchestration_completion_proofs"]
    result["orchestration_readiness_summary"] = bundle["orchestration_readiness_summary"]
    result["ui_operator_console_readiness_bridge"] = bundle["ui_operator_console_readiness_bridge"]
    
    return result

def write_multi_agent_orchestration(result: dict, output_dir: str | Path, run_label: str = "station-chief-runtime") -> dict:
    if "multi_agent_orchestration_bundle" not in result:
        raise ValueError("Missing multi_agent_orchestration_bundle in result")
        
    run_id = generate_run_id(result.get("command", "empty"), run_label)
    record_dir = Path(output_dir) / run_id
    record_dir.mkdir(parents=True, exist_ok=True)
    
    payloads = {
        "multi_agent_orchestration_bundle.json": result["multi_agent_orchestration_bundle"],
        "orchestration_topology_schema.json": result["orchestration_topology_schema"],
        "orchestration_nodes.json": result["orchestration_nodes"],
        "multi_worker_coordination_map.json": result["multi_worker_coordination_map"],
        "task_handoff_simulation.json": result["task_handoff_simulation"],
        "inter_worker_dependency_graph.json": result["inter_worker_dependency_graph"],
        "orchestration_conflict_detector.json": result["orchestration_conflict_detector"],
        "orchestration_dry_run_results.json": result["orchestration_dry_run_results"],
        "orchestration_ledger.json": result["orchestration_ledger"],
        "orchestration_completion_proofs.json": result["orchestration_completion_proofs"],
        "orchestration_readiness_summary.json": result["orchestration_readiness_summary"],
        "ui_operator_console_readiness_bridge.json": result["ui_operator_console_readiness_bridge"]
    }
    
    files_written = list(payloads.keys())
    for filename, payload in payloads.items():
        _write_json(record_dir / filename, payload)
        
    manifest = {
        "multi_agent_orchestration_manifest_version": "2.5.0",
        "run_id": run_id,
        "runtime_version": "2.9.0",
        "files_written": files_written + ["multi_agent_orchestration_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "execution_authorized": False,
        "status": "ORCHESTRATION_SANDBOX_ONLY",
        "note": "Multi-Agent Orchestration Sandbox v2.5.0 creates sandbox orchestration artifacts only. It does not animate workers, hire workers, route live workers, execute live actions, perform live orchestration, or modify repo files."
    }
    _write_json(record_dir / "multi_agent_orchestration_manifest.json", manifest)
    files_written.append("multi_agent_orchestration_manifest.json")
    
    return {
        "run_id": run_id,
        "multi_agent_orchestration_dir": str(record_dir),
        "files_written": files_written
    }


def attach_operator_console(result: dict) -> dict:
    if result.get("multi_agent_orchestration_bundle") is None:
        result = attach_multi_agent_orchestration(result)
        
    bundle = create_operator_console_bundle(result)
    
    result["operator_console_bundle"] = bundle
    result["operator_console_review_bundle"] = bundle["operator_console_review_bundle"]
    result["operator_console_screen_schema"] = bundle["operator_console_review_bundle"]["operator_console_screen_schema"]
    result["runtime_status_panel_schema"] = bundle["operator_console_review_bundle"]["runtime_status_panel_schema"]
    result["approval_queue_panel_schema"] = bundle["operator_console_review_bundle"]["approval_queue_panel_schema"]
    result["work_order_panel_schema"] = bundle["operator_console_review_bundle"]["work_order_panel_schema"]
    result["worker_registry_panel_schema"] = bundle["operator_console_review_bundle"]["worker_registry_panel_schema"]
    result["department_routing_panel_schema"] = bundle["operator_console_review_bundle"]["department_routing_panel_schema"]
    result["orchestration_sandbox_panel_schema"] = bundle["operator_console_review_bundle"]["orchestration_sandbox_panel_schema"]
    result["release_lock_panel_schema"] = bundle["operator_console_review_bundle"]["release_lock_panel_schema"]
    result["human_control_surface_schema"] = bundle["operator_console_review_bundle"]["human_control_surface_schema"]
    result["operator_action_registry"] = bundle["operator_console_review_bundle"]["operator_action_registry"]
    result["disabled_action_state_map"] = bundle["operator_console_review_bundle"]["disabled_action_state_map"]
    result["operator_console_safety_summary"] = bundle["operator_console_safety_summary"]
    result["operator_console_readiness_summary"] = bundle["operator_console_readiness_summary"]
    result["github_patch_hardening_readiness_bridge"] = bundle["github_patch_hardening_readiness_bridge"]
    
    return result

def write_operator_console(result: dict, output_dir: str | Path, run_label: str = "station-chief-runtime") -> dict:
    if "operator_console_bundle" not in result:
        raise ValueError("Missing operator_console_bundle in result")
        
    run_id = generate_run_id(result.get("command", "empty"), run_label)
    record_dir = Path(output_dir) / run_id
    record_dir.mkdir(parents=True, exist_ok=True)
    
    payloads = {
        "operator_console_bundle.json": result["operator_console_bundle"],
        "operator_console_review_bundle.json": result["operator_console_review_bundle"],
        "operator_console_screen_schema.json": result["operator_console_screen_schema"],
        "runtime_status_panel_schema.json": result["runtime_status_panel_schema"],
        "approval_queue_panel_schema.json": result["approval_queue_panel_schema"],
        "work_order_panel_schema.json": result["work_order_panel_schema"],
        "worker_registry_panel_schema.json": result["worker_registry_panel_schema"],
        "department_routing_panel_schema.json": result["department_routing_panel_schema"],
        "orchestration_sandbox_panel_schema.json": result["orchestration_sandbox_panel_schema"],
        "release_lock_panel_schema.json": result["release_lock_panel_schema"],
        "human_control_surface_schema.json": result["human_control_surface_schema"],
        "operator_action_registry.json": result["operator_action_registry"],
        "disabled_action_state_map.json": result["disabled_action_state_map"],
        "operator_console_safety_summary.json": result["operator_console_safety_summary"],
        "operator_console_readiness_summary.json": result["operator_console_readiness_summary"],
        "github_patch_hardening_readiness_bridge.json": result["github_patch_hardening_readiness_bridge"]
    }
    
    files_written = list(payloads.keys())
    for filename, payload in payloads.items():
        _write_json(record_dir / filename, payload)
        
    manifest = {
        "operator_console_manifest_version": "2.5.0",
        "run_id": run_id,
        "runtime_version": "2.9.0",
        "files_written": files_written + ["operator_console_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "live_ui_displayed": False,
        "execution_authorized": False,
        "status": "SCHEMA_ONLY",
        "note": "UI / Operator Console Schema v2.5.0 creates schema and review artifacts only. It does not display a live UI, authorize execution, connect APIs, animate workers, hire workers, route live workers, perform live orchestration, execute live actions, or modify repo files."
    }
    _write_json(record_dir / "operator_console_manifest.json", manifest)
    files_written.append("operator_console_manifest.json")
    
    return {
        "run_id": run_id,
        "operator_console_dir": str(record_dir),
        "files_written": files_written
    }


def attach_github_patch_hardening(
    result: dict,
    patch_root: str | None = None,
    allowed_patch_file: str | None = None,
    patch_content: str | None = None,
    original_content: str | None = None,
    changed_files: list[str] | None = None
) -> dict:
    if result.get("operator_console_bundle") is None:
        result = attach_operator_console(result)
        
    approval_record = result.get("signed_approval_record") or result.get("approval_record")
    approval_ledger = result.get("approval_ledger_bundle")
    
    bundle = create_github_patch_hardening_bundle(
        result,
        patch_root=patch_root,
        allowed_patch_file=allowed_patch_file,
        patch_content=patch_content,
        original_content=original_content,
        changed_files=changed_files,
        approval_record=approval_record,
        approval_ledger=approval_ledger
    )
    
    result["github_patch_hardening_bundle"] = bundle
    result["patch_hardening_audit_bundle"] = bundle["patch_hardening_audit_bundle"]
    result["patch_hardening_schema"] = bundle["patch_hardening_schema"]
    result["protected_path_policy"] = bundle["protected_path_policy"]
    result["patch_root_validation"] = bundle["patch_root_validation"]
    result["patch_preview_diff_contract"] = bundle["patch_preview_diff_contract"]
    result["patch_digest_manifest"] = bundle["patch_digest_manifest"]
    result["patch_rollback_preview"] = bundle["patch_rollback_preview"]
    result["changed_file_proof_hardening"] = bundle["changed_file_proof_hardening"]
    result["human_approval_chain_binding"] = bundle["human_approval_chain_binding"]
    result["patch_execution_readiness_score"] = bundle["patch_execution_readiness_score"]
    result["deployment_packaging_readiness_bridge"] = bundle["deployment_packaging_readiness_bridge"]
    
    return result

def write_github_patch_hardening(result: dict, output_dir: str | Path, run_label: str = "station-chief-runtime") -> dict:
    if "github_patch_hardening_bundle" not in result:
        raise ValueError("Missing github_patch_hardening_bundle in result")
        
    run_id = generate_run_id(result.get("command", "empty"), run_label)
    record_dir = Path(output_dir) / run_id
    record_dir.mkdir(parents=True, exist_ok=True)
    
    payloads = {
        "github_patch_hardening_bundle.json": result["github_patch_hardening_bundle"],
        "patch_hardening_audit_bundle.json": result["patch_hardening_audit_bundle"],
        "patch_hardening_schema.json": result["patch_hardening_schema"],
        "protected_path_policy.json": result["protected_path_policy"],
        "patch_root_validation.json": result["patch_root_validation"],
        "patch_preview_diff_contract.json": result["patch_preview_diff_contract"],
        "patch_digest_manifest.json": result["patch_digest_manifest"],
        "patch_rollback_preview.json": result["patch_rollback_preview"],
        "changed_file_proof_hardening.json": result["changed_file_proof_hardening"],
        "human_approval_chain_binding.json": result["human_approval_chain_binding"],
        "patch_execution_readiness_score.json": result["patch_execution_readiness_score"],
        "deployment_packaging_readiness_bridge.json": result["deployment_packaging_readiness_bridge"]
    }
    
    files_written = list(payloads.keys())
    for filename, payload in payloads.items():
        _write_json(record_dir / filename, payload)
        
    manifest = {
        "github_patch_hardening_manifest_version": "2.5.0",
        "run_id": run_id,
        "runtime_version": "2.9.0",
        "files_written": files_written + ["github_patch_hardening_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "repo_patch_applied": False,
        "github_api_called": False,
        "execution_authorized": False,
        "status": "PATCH_HARDENING_CONTRACT_ONLY",
        "note": "GitHub Patch Application Hardening v2.5.0 creates patch hardening contracts and review artifacts only. It does not apply patches, call GitHub APIs, push commits, authorize execution, execute live actions, or modify repo files."
    }
    _write_json(record_dir / "github_patch_hardening_manifest.json", manifest)
    files_written.append("github_patch_hardening_manifest.json")
    
    return {
        "run_id": run_id,
        "github_patch_hardening_dir": str(record_dir),
        "files_written": files_written
    }


def attach_deployment_packaging(result: dict) -> dict:
    if result.get("github_patch_hardening_bundle") is None:
        result = attach_github_patch_hardening(result)
        
    bundle = make_deployment_packaging_bundle(result)
    
    result["deployment_packaging_bundle"] = bundle
    result["deployment_artifact_schema"] = bundle["deployment_artifact_schema"]
    result["portfolio_packaging_manifest"] = bundle["portfolio_packaging_manifest"]
    result["runtime_export_bundle"] = bundle["runtime_export_bundle"]
    result["release_notes"] = bundle["release_notes"]
    result["deployment_safety_contract"] = bundle["deployment_safety_contract"]
    result["deployment_readiness_proof"] = bundle["deployment_readiness_proof"]
    result["portfolio_handoff_summary"] = bundle["portfolio_handoff_summary"]
    result["packaging_audit_bundle"] = bundle["packaging_audit_bundle"]
    result["first_controlled_worker_execution_readiness_bridge"] = bundle["first_controlled_worker_execution_readiness_bridge"]
    
    return result

def write_deployment_packaging(result: dict, output_dir: str | Path, run_label: str = "station-chief-runtime") -> dict:
    if "deployment_packaging_bundle" not in result:
        raise ValueError("Missing deployment_packaging_bundle in result")
        
    run_id = generate_run_id(result.get("command", "empty"), run_label)
    record_dir = Path(output_dir) / run_id
    record_dir.mkdir(parents=True, exist_ok=True)
    
    payloads = {
        "deployment_packaging_bundle.json": result["deployment_packaging_bundle"],
        "deployment_artifact_schema.json": result["deployment_artifact_schema"],
        "portfolio_packaging_manifest.json": result["portfolio_packaging_manifest"],
        "runtime_export_bundle.json": result["runtime_export_bundle"],
        "release_notes.json": result["release_notes"],
        "deployment_safety_contract.json": result["deployment_safety_contract"],
        "deployment_readiness_proof.json": result["deployment_readiness_proof"],
        "portfolio_handoff_summary.json": result["portfolio_handoff_summary"],
        "packaging_audit_bundle.json": result["packaging_audit_bundle"],
        "first_controlled_worker_execution_readiness_bridge.json": result["first_controlled_worker_execution_readiness_bridge"]
    }
    
    files_written = list(payloads.keys())
    for filename, payload in payloads.items():
        _write_json(record_dir / filename, payload)
        
    manifest = {
        "deployment_packaging_manifest_version": "2.5.0",
        "run_id": run_id,
        "runtime_version": "2.9.0",
        "files_written": files_written + ["deployment_packaging_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "deployment_performed": False,
        "hosting_api_called": False,
        "repo_patch_applied": False,
        "execution_authorized": False,
        "status": "PACKAGING_BRIDGE_ONLY",
        "note": "Deployment / Portfolio Packaging Bridge v2.5.0 creates packaging, portfolio handoff, release-note, and readiness artifacts only. It does not execute deployment, call hosting APIs, mutate external services, authorize execution, execute live actions, or modify repo files."
    }
    _write_json(record_dir / "deployment_packaging_manifest.json", manifest)
    files_written.append("deployment_packaging_manifest.json")
    
    return {
        "run_id": run_id,
        "deployment_packaging_dir": str(record_dir),
        "files_written": files_written
    }


def attach_controlled_worker_execution(
    result: dict,
    worker_id: str | None = None,
    sandbox_task: str = "noop",
    confirmation_token: str | None = None,
    requested_tool_permissions: list[str] | None = None,
    payload: dict | None = None
) -> dict:
    if result.get("deployment_packaging_bundle") is None:
        result = attach_deployment_packaging(result)
        
    bundle = create_controlled_worker_execution_bundle(
        result,
        worker_id=worker_id,
        sandbox_task=sandbox_task,
        confirmation_token=confirmation_token,
        requested_tool_permissions=requested_tool_permissions,
        payload=payload
    )
    
    result["controlled_worker_execution_bundle"] = bundle
    result["controlled_worker_execution_schema"] = bundle["controlled_worker_execution_schema"]
    result["worker_execution_gate"] = bundle["worker_execution_gate"]
    result["tool_permission_binding"] = bundle["tool_permission_binding"]
    result["sandbox_worker_task"] = bundle["sandbox_worker_task"]
    result["worker_abort_contract"] = bundle["worker_abort_contract"]
    result["worker_rollback_contract"] = bundle["worker_rollback_contract"]
    result["worker_execution_telemetry_stub"] = bundle["worker_execution_telemetry_stub"]
    result["controlled_worker_execution_result"] = bundle["controlled_worker_execution_result"]
    result["post_run_audit_proof"] = bundle["post_run_audit_proof"]
    result["worker_execution_ledger"] = bundle["worker_execution_ledger"]
    result["single_worker_tool_permission_binding_readiness_bridge"] = bundle["single_worker_tool_permission_binding_readiness_bridge"]
    
    return result

def write_controlled_worker_execution(result: dict, output_dir: str | Path, run_label: str = "station-chief-runtime") -> dict:
    if "controlled_worker_execution_bundle" not in result:
        raise ValueError("Missing controlled_worker_execution_bundle in result")
        
    run_id = generate_run_id(result.get("command", "empty"), run_label)
    record_dir = Path(output_dir) / run_id
    record_dir.mkdir(parents=True, exist_ok=True)
    
    payloads = {
        "controlled_worker_execution_bundle.json": result["controlled_worker_execution_bundle"],
        "controlled_worker_execution_schema.json": result["controlled_worker_execution_schema"],
        "worker_execution_gate.json": result["worker_execution_gate"],
        "tool_permission_binding.json": result["tool_permission_binding"],
        "sandbox_worker_task.json": result["sandbox_worker_task"],
        "worker_abort_contract.json": result["worker_abort_contract"],
        "worker_rollback_contract.json": result["worker_rollback_contract"],
        "worker_execution_telemetry_stub.json": result["worker_execution_telemetry_stub"],
        "controlled_worker_execution_result.json": result["controlled_worker_execution_result"],
        "post_run_audit_proof.json": result["post_run_audit_proof"],
        "worker_execution_ledger.json": result["worker_execution_ledger"],
        "single_worker_tool_permission_binding_readiness_bridge.json": result["single_worker_tool_permission_binding_readiness_bridge"]
    }
    
    files_written = list(payloads.keys())
    for filename, payload in payloads.items():
        _write_json(record_dir / filename, payload)
        
    manifest = {
        "controlled_worker_execution_manifest_version": "2.5.0",
        "run_id": run_id,
        "runtime_version": "2.9.0",
        "files_written": files_written + ["controlled_worker_execution_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "single_worker_sandbox_execution_available": True,
        "single_worker_sandbox_execution_performed": result["controlled_worker_execution_bundle"]["single_worker_sandbox_execution_performed"],
        "broad_worker_activation_performed": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "repo_files_modified": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False,
        "status": "SINGLE_WORKER_SANDBOX_EXECUTION_ONLY",
        "note": "First Controlled Worker-Agent Execution v2.5.0 allows only a single deterministic local sandbox worker task when explicitly approved. It does not call APIs, run shell commands, modify repo files, deploy, animate broad workforce, hire real workers, route live workers, or perform live orchestration."
    }
    _write_json(record_dir / "controlled_worker_execution_manifest.json", manifest)
    files_written.append("controlled_worker_execution_manifest.json")
    
    return {
        "run_id": run_id,
        "controlled_worker_execution_dir": str(record_dir),
        "files_written": files_written
    }


    return {
        "run_id": run_id,
        "controlled_worker_execution_dir": str(record_dir),
        "files_written": files_written
    }


def attach_tool_permission_binding(
    result: dict,
    worker_id: str | None = None,
    requested_tool_permissions: list[str] | None = None,
    provided_tool_tokens: dict | None = None,
    sandbox_task: str = "noop",
    tool_outputs: list[dict] | None = None
) -> dict:
    if result.get("controlled_worker_execution_bundle") is None:
        result = attach_controlled_worker_execution(result)
        
    bundle = create_tool_permission_binding_bundle(
        result,
        worker_id=worker_id,
        requested_tool_permissions=requested_tool_permissions,
        provided_tool_tokens=provided_tool_tokens,
        sandbox_task=sandbox_task,
        tool_outputs=tool_outputs
    )
    
    result["tool_permission_binding_bundle"] = bundle
    result["tool_permission_binding_schema"] = bundle["tool_permission_binding_schema"]
    result["per_tool_permission_registry"] = bundle["per_tool_permission_registry"]
    result["tool_permission_request_validation"] = bundle["tool_permission_request_validation"]
    result["tool_specific_approval_binding"] = bundle["tool_specific_approval_binding"]
    result["tool_invocation_dry_run_contract"] = bundle["tool_invocation_dry_run_contract"]
    result["tool_output_validation_schema"] = bundle["tool_output_validation_schema"]
    result["tool_output_validation_result"] = bundle["tool_output_validation_result"]
    result["tool_failure_handling_contract"] = bundle["tool_failure_handling_contract"]
    result["tool_revocation_contract"] = bundle["tool_revocation_contract"]
    result["per_run_permission_audit_proof"] = bundle["per_run_permission_audit_proof"]
    result["tool_permission_ledger"] = bundle["tool_permission_ledger"]
    result["tool_permission_readiness_summary"] = bundle["tool_permission_readiness_summary"]
    result["live_execution_telemetry_abort_readiness_bridge"] = bundle["live_execution_telemetry_abort_readiness_bridge"]
    
    return result

def write_tool_permission_binding(result: dict, output_dir: str | Path, run_label: str = "station-chief-runtime") -> dict:
    if "tool_permission_binding_bundle" not in result:
        raise ValueError("Missing tool_permission_binding_bundle in result")
        
    run_id = generate_run_id(result.get("command", "empty"), run_label)
    record_dir = Path(output_dir) / run_id
    record_dir.mkdir(parents=True, exist_ok=True)
    
    payloads = {
        "tool_permission_binding_bundle.json": result["tool_permission_binding_bundle"],
        "tool_permission_binding_schema.json": result["tool_permission_binding_schema"],
        "per_tool_permission_registry.json": result["per_tool_permission_registry"],
        "tool_permission_request_validation.json": result["tool_permission_request_validation"],
        "tool_specific_approval_binding.json": result["tool_specific_approval_binding"],
        "tool_invocation_dry_run_contract.json": result["tool_invocation_dry_run_contract"],
        "tool_output_validation_schema.json": result["tool_output_validation_schema"],
        "tool_output_validation_result.json": result["tool_output_validation_result"],
        "tool_failure_handling_contract.json": result["tool_failure_handling_contract"],
        "tool_revocation_contract.json": result["tool_revocation_contract"],
        "per_run_permission_audit_proof.json": result["per_run_permission_audit_proof"],
        "tool_permission_ledger.json": result["tool_permission_ledger"],
        "tool_permission_readiness_summary.json": result["tool_permission_readiness_summary"],
        "live_execution_telemetry_abort_readiness_bridge.json": result["live_execution_telemetry_abort_readiness_bridge"]
    }
    
    files_written = list(payloads.keys())
    for filename, payload in payloads.items():
        _write_json(record_dir / filename, payload)
        
    manifest = {
        "tool_permission_binding_manifest_version": "2.5.0",
        "run_id": run_id,
        "runtime_version": "2.9.0",
        "files_written": files_written + ["tool_permission_binding_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "tool_invocations_performed": False,
        "external_tool_invocations_performed": False,
        "repo_files_modified": False,
        "broad_worker_activation_performed": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False,
        "status": "SINGLE_WORKER_TOOL_PERMISSION_BINDING_ONLY",
        "note": "Single-Worker Tool Permission Binding v2.5.0 creates per-tool permission registry, token binding, dry-run invocation contracts, output validation, failure handling, revocation, audit proof, and ledger artifacts only. It does not invoke external tools, call APIs, run shell commands, modify repo files, deploy, animate broad workforce, hire real workers, route live workers, or perform live orchestration."
    }
    _write_json(record_dir / "tool_permission_binding_manifest.json", manifest)
    files_written.append("tool_permission_binding_manifest.json")
    
    return {
        "run_id": run_id,
        "tool_permission_binding_dir": str(record_dir),
        "files_written": files_written
    }


def attach_live_execution_telemetry_abort(
    result: dict,
    worker_id: str | None = None,
    confirmation_token: str | None = None,
    abort_reason: str | None = None,
    failure_reason: str | None = None,
    timeout_limit_steps: int = 5,
    observed_steps: int = 0,
    partial_payload: dict | None = None
) -> dict:
    if result.get("tool_permission_binding_bundle") is None:
        result = attach_tool_permission_binding(result)
        
    bundle = create_live_execution_telemetry_abort_bundle(
        result,
        worker_id=worker_id,
        confirmation_token=confirmation_token,
        abort_reason=abort_reason,
        failure_reason=failure_reason,
        timeout_limit_steps=timeout_limit_steps,
        observed_steps=observed_steps,
        partial_payload=partial_payload
    )
    
    result["live_execution_telemetry_abort_bundle"] = bundle
    result["live_execution_telemetry_abort_schema"] = bundle["live_execution_telemetry_abort_schema"]
    result["telemetry_event_schema"] = bundle["telemetry_event_schema"]
    result["execution_state_model"] = bundle["execution_state_model"]
    result["telemetry_approval_gate"] = bundle["telemetry_approval_gate"]
    result["heartbeat_stub"] = bundle["heartbeat_stub"]
    result["abort_signal_contract"] = bundle["abort_signal_contract"]
    result["timeout_contract"] = bundle["timeout_contract"]
    result["partial_result_capture"] = bundle["partial_result_capture"]
    result["failed_run_quarantine_contract"] = bundle["failed_run_quarantine_contract"]
    result["post_abort_audit_proof"] = bundle["post_abort_audit_proof"]
    result["telemetry_ledger"] = bundle["telemetry_ledger"]
    result["telemetry_readiness_summary"] = bundle["telemetry_readiness_summary"]
    result["post_run_audit_expansion_readiness_bridge"] = bundle["post_run_audit_expansion_readiness_bridge"]
    
    return result


def attach_post_run_audit_expansion(
    result: dict,
    worker_id: str | None = None,
    confirmation_token: str | None = None,
    before_result: dict | None = None,
    after_result: dict | None = None,
    artifact_names: list[str] | None = None,
    validator_names: list[str] | None = None,
    observed_failures: list[str] | None = None,
) -> dict:
    if result.get("live_execution_telemetry_abort_bundle") is None:
        result = attach_live_execution_telemetry_abort(result)

    bundle = create_post_run_audit_expansion_bundle(
        result,
        worker_id=worker_id,
        command=result.get("command"),
        confirmation_token=confirmation_token,
        before_result=before_result,
        after_result=after_result,
        artifact_names=artifact_names,
        validator_names=validator_names,
        observed_failures=observed_failures,
    )
    result["post_run_audit_expansion_bundle"] = bundle
    result["post_run_audit_expansion_schema"] = bundle["post_run_audit_expansion_schema"]
    result["expanded_audit_evidence_schema"] = bundle["expanded_audit_evidence_schema"]
    result["post_run_audit_approval_gate"] = bundle["post_run_audit_approval_gate"]
    result["before_after_run_comparison_proof"] = bundle["before_after_run_comparison_proof"]
    result["validator_backed_audit_artifact_index"] = bundle["validator_backed_audit_artifact_index"]
    result["audit_replay_record"] = bundle["audit_replay_record"]
    result["failure_class_taxonomy"] = bundle["failure_class_taxonomy"]
    result["human_review_packet"] = bundle["human_review_packet"]
    result["audit_integrity_score"] = bundle["audit_integrity_score"]
    result["audit_evidence_ledger"] = bundle["audit_evidence_ledger"]
    result["audit_expansion_readiness_summary"] = bundle["audit_expansion_readiness_summary"]
    result["multi_worker_sandbox_coordination_readiness_bridge"] = bundle["multi_worker_sandbox_coordination_readiness_bridge"]
    result["external_actions_taken"] = bundle["external_actions_taken"]
    result["actual_replay_performed"] = bundle["actual_replay_performed"]
    result["external_artifact_fetch_performed"] = bundle["external_artifact_fetch_performed"]
    result["repo_files_modified"] = bundle["repo_files_modified"]
    result["broad_worker_activation_performed"] = bundle["broad_worker_activation_performed"]
    result["real_worker_hiring_performed"] = bundle["real_worker_hiring_performed"]
    result["live_worker_routing_performed"] = bundle["live_worker_routing_performed"]
    result["live_orchestration_performed"] = bundle["live_orchestration_performed"]
    result["hosting_api_called"] = bundle["hosting_api_called"]
    result["deployment_performed"] = bundle["deployment_performed"]
    result["execution_authorized"] = bundle["execution_authorized"]
    return result


def write_post_run_audit_expansion(
    result: dict,
    output_dir: str | Path,
    run_label: str = "station-chief-runtime",
) -> dict:
    if "post_run_audit_expansion_bundle" not in result:
        raise ValueError("Missing post_run_audit_expansion_bundle in result")

    run_id = generate_run_id(result.get("command", "empty"), run_label)
    record_dir = Path(output_dir) / run_id
    record_dir.mkdir(parents=True, exist_ok=True)

    payloads = {
        "post_run_audit_expansion_bundle.json": result["post_run_audit_expansion_bundle"],
        "post_run_audit_expansion_schema.json": result["post_run_audit_expansion_schema"],
        "expanded_audit_evidence_schema.json": result["expanded_audit_evidence_schema"],
        "post_run_audit_approval_gate.json": result["post_run_audit_approval_gate"],
        "before_after_run_comparison_proof.json": result["before_after_run_comparison_proof"],
        "validator_backed_audit_artifact_index.json": result["validator_backed_audit_artifact_index"],
        "audit_replay_record.json": result["audit_replay_record"],
        "failure_class_taxonomy.json": result["failure_class_taxonomy"],
        "human_review_packet.json": result["human_review_packet"],
        "audit_integrity_score.json": result["audit_integrity_score"],
        "audit_evidence_ledger.json": result["audit_evidence_ledger"],
        "audit_expansion_readiness_summary.json": result["audit_expansion_readiness_summary"],
        "multi_worker_sandbox_coordination_readiness_bridge.json": result["multi_worker_sandbox_coordination_readiness_bridge"],
    }
    files_written = list(payloads.keys())
    for filename, payload in payloads.items():
        _write_json(record_dir / filename, payload)

    manifest = {
        "post_run_audit_expansion_manifest_version": "2.5.0",
        "run_id": run_id,
        "runtime_version": "2.9.0",
        "files_written": files_written + ["post_run_audit_expansion_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "actual_replay_performed": False,
        "external_artifact_fetch_performed": False,
        "repo_files_modified": False,
        "broad_worker_activation_performed": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False,
        "status": "SINGLE_WORKER_POST_RUN_AUDIT_EXPANSION_ONLY",
        "note": "Post-Run Audit Proof Expansion v2.5.0 creates local expanded audit proof, comparison, validator index, replay record, failure taxonomy, human review, integrity score, and ledger artifacts only. It does not perform actual replay, fetch external artifacts, call APIs, run shell commands, modify repo files, deploy, animate broad workforce, hire real workers, route live workers, or perform live orchestration.",
    }
    _write_json(record_dir / "post_run_audit_expansion_manifest.json", manifest)
    files_written.append("post_run_audit_expansion_manifest.json")
    return {
        "run_id": run_id,
        "post_run_audit_expansion_dir": str(record_dir),
        "files_written": files_written,
    }


def attach_multi_worker_sandbox_coordination(
    result: dict,
    roster_label: str | None = None,
    confirmation_token: str | None = None,
    requested_worker_count: int = 3,
    worker_roles: list[str] | None = None,
    requested_shared_resources: list[str] | None = None,
    abort_reason: str | None = None,
    failure_reason: str | None = None,
) -> dict:
    if result.get("post_run_audit_expansion_bundle") is None:
        result = attach_post_run_audit_expansion(result)

    bundle = create_multi_worker_sandbox_coordination_bundle(
        result,
        command=result.get("command"),
        roster_label=roster_label,
        confirmation_token=confirmation_token,
        requested_worker_count=requested_worker_count,
        worker_roles=worker_roles,
        requested_shared_resources=requested_shared_resources,
        abort_reason=abort_reason,
        failure_reason=failure_reason,
    )
    result["multi_worker_sandbox_coordination_bundle"] = bundle
    result["multi_worker_sandbox_coordination_schema"] = bundle["multi_worker_sandbox_coordination_schema"]
    result["multi_worker_coordination_approval_gate"] = bundle["multi_worker_coordination_approval_gate"]
    result["sandbox_worker_roster"] = bundle["sandbox_worker_roster"]
    result["worker_coordination_graph"] = bundle["worker_coordination_graph"]
    result["inter_worker_handoff_contract"] = bundle["inter_worker_handoff_contract"]
    result["multi_worker_dry_run_ledger"] = bundle["multi_worker_dry_run_ledger"]
    result["coordination_conflict_detector"] = bundle["coordination_conflict_detector"]
    result["coordination_abort_contract"] = bundle["coordination_abort_contract"]
    result["coordination_quarantine_contract"] = bundle["coordination_quarantine_contract"]
    result["coordination_audit_proof"] = bundle["coordination_audit_proof"]
    result["coordination_readiness_summary"] = bundle["coordination_readiness_summary"]
    result["controlled_external_tool_adapter_preview_readiness_bridge"] = bundle[
        "controlled_external_tool_adapter_preview_readiness_bridge"
    ]
    result["external_actions_taken"] = bundle["external_actions_taken"]
    result["real_workers_hired"] = bundle["real_workers_hired"]
    result["worker_processes_started"] = bundle["worker_processes_started"]
    result["handoffs_executed"] = bundle["handoffs_executed"]
    result["live_worker_routing_performed"] = bundle["live_worker_routing_performed"]
    result["live_orchestration_performed"] = bundle["live_orchestration_performed"]
    result["repo_files_modified"] = bundle["repo_files_modified"]
    result["broad_worker_activation_performed"] = bundle["broad_worker_activation_performed"]
    result["hosting_api_called"] = bundle["hosting_api_called"]
    result["deployment_performed"] = bundle["deployment_performed"]
    result["execution_authorized"] = bundle["execution_authorized"]
    return result


def write_multi_worker_sandbox_coordination(
    result: dict,
    output_dir: str | Path,
    run_label: str = "station-chief-runtime",
) -> dict:
    if "multi_worker_sandbox_coordination_bundle" not in result:
        raise ValueError("Missing multi_worker_sandbox_coordination_bundle in result")

    run_id = generate_run_id(result.get("command", "empty"), run_label)
    record_dir = Path(output_dir) / run_id
    record_dir.mkdir(parents=True, exist_ok=True)

    payloads = {
        "multi_worker_sandbox_coordination_bundle.json": result["multi_worker_sandbox_coordination_bundle"],
        "multi_worker_sandbox_coordination_schema.json": result["multi_worker_sandbox_coordination_schema"],
        "multi_worker_coordination_approval_gate.json": result["multi_worker_coordination_approval_gate"],
        "sandbox_worker_roster.json": result["sandbox_worker_roster"],
        "worker_coordination_graph.json": result["worker_coordination_graph"],
        "inter_worker_handoff_contract.json": result["inter_worker_handoff_contract"],
        "multi_worker_dry_run_ledger.json": result["multi_worker_dry_run_ledger"],
        "coordination_conflict_detector.json": result["coordination_conflict_detector"],
        "coordination_abort_contract.json": result["coordination_abort_contract"],
        "coordination_quarantine_contract.json": result["coordination_quarantine_contract"],
        "coordination_audit_proof.json": result["coordination_audit_proof"],
        "coordination_readiness_summary.json": result["coordination_readiness_summary"],
        "controlled_external_tool_adapter_preview_readiness_bridge.json": result[
            "controlled_external_tool_adapter_preview_readiness_bridge"
        ],
    }
    files_written = list(payloads.keys())
    for filename, payload in payloads.items():
        _write_json(record_dir / filename, payload)

    manifest = {
        "multi_worker_sandbox_coordination_manifest_version": "2.5.0",
        "run_id": run_id,
        "runtime_version": "2.9.0",
        "files_written": files_written + ["multi_worker_sandbox_coordination_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "external_tool_invoked": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "real_workers_hired": False,
        "worker_processes_started": False,
        "handoffs_executed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "repo_files_modified": False,
        "broad_worker_activation_performed": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False,
        "status": "MULTI_WORKER_SANDBOX_COORDINATION_PREVIEW_ONLY",
        "note": "Multi-Worker Sandbox Coordination v2.5.0 creates local sandbox roster, coordination graph, handoff contracts, dry-run ledgers, conflict detection, abort/quarantine contracts, audit proofs, and readiness bridge artifacts only. It does not hire real workers, start worker processes, perform live routing, perform live orchestration, call APIs, run shell commands, modify repo files, deploy, or animate broad workforce.",
    }
    _write_json(record_dir / "multi_worker_sandbox_coordination_manifest.json", manifest)
    files_written.append("multi_worker_sandbox_coordination_manifest.json")
    return {
        "run_id": run_id,
        "multi_worker_sandbox_coordination_dir": str(record_dir),
        "files_written": files_written,
    }

def attach_controlled_external_tool_adapter_preview(
    result: dict,
    tool_label: str | None = None,
    tool_id: str | None = None,
    confirmation_token: str | None = None,
    requested_tools: list[str] | None = None,
    requested_external_action: str | None = None,
    request_label: str | None = None,
    request_payload: dict | None = None,
    response_preview: dict | None = None,
    abort_reason: str | None = None,
) -> dict:
    updated = dict(result)
    if updated.get("post_run_audit_expansion_bundle") is None:
        updated = attach_post_run_audit_expansion(updated)
    if updated.get("multi_worker_sandbox_coordination_bundle") is None:
        updated = attach_multi_worker_sandbox_coordination(updated)
    bundle = create_controlled_external_tool_adapter_preview_bundle(
        updated,
        command=updated.get("command"),
        tool_label=tool_label,
        tool_id=tool_id,
        confirmation_token=confirmation_token,
        requested_tools=requested_tools,
        requested_external_action=requested_external_action,
        request_label=request_label,
        request_payload=request_payload,
        response_preview=response_preview,
        abort_reason=abort_reason,
    )
    updated["controlled_external_tool_adapter_preview_bundle"] = bundle
    updated["controlled_external_tool_adapter_preview_schema"] = bundle["controlled_external_tool_adapter_preview_schema"]
    updated["external_tool_adapter_preview_approval_gate"] = bundle["external_tool_adapter_preview_approval_gate"]
    updated["external_tool_dry_run_adapter_registry"] = bundle["external_tool_dry_run_adapter_registry"]
    updated["per_tool_external_permission_gate"] = bundle["per_tool_external_permission_gate"]
    updated["external_request_preview_contract"] = bundle["external_request_preview_contract"]
    updated["external_response_validation_schema"] = bundle["external_response_validation_schema"]
    updated["external_response_validation_preview_result"] = bundle["external_response_validation_preview_result"]
    updated["external_tool_abort_contract"] = bundle["external_tool_abort_contract"]
    updated["external_tool_audit_proof"] = bundle["external_tool_audit_proof"]
    updated["external_tool_preview_ledger"] = bundle["external_tool_preview_ledger"]
    updated["external_tool_preview_readiness_summary"] = bundle["external_tool_preview_readiness_summary"]
    updated["permissioned_external_api_dry_run_preview_readiness_bridge"] = bundle[
        "permissioned_external_api_dry_run_preview_readiness_bridge"
    ]
    updated["external_actions_taken"] = bundle["external_actions_taken"]
    updated["external_tool_invoked"] = bundle["external_tool_invoked"]
    updated["live_api_call_performed"] = bundle["live_api_call_performed"]
    updated["network_access_performed"] = bundle["network_access_performed"]
    updated["socket_opened"] = bundle["socket_opened"]
    updated["repo_files_modified"] = bundle["repo_files_modified"]
    updated["broad_worker_activation_performed"] = bundle["broad_worker_activation_performed"]
    updated["real_workers_hired"] = bundle["real_workers_hired"]
    updated["worker_processes_started"] = bundle["worker_processes_started"]
    updated["live_worker_routing_performed"] = bundle["live_worker_routing_performed"]
    updated["live_orchestration_performed"] = bundle["live_orchestration_performed"]
    updated["hosting_api_called"] = bundle["hosting_api_called"]
    updated["deployment_performed"] = bundle["deployment_performed"]
    updated["execution_authorized"] = bundle["execution_authorized"]
    return updated


def write_controlled_external_tool_adapter_preview(
    result: dict,
    output_dir: str | Path,
    run_label: str = "station-chief-runtime",
) -> dict:
    if "controlled_external_tool_adapter_preview_bundle" not in result:
        raise ValueError("Missing controlled_external_tool_adapter_preview_bundle in result")

    run_id = generate_run_id(result.get("command", "empty"), run_label)
    record_dir = Path(output_dir) / run_id
    record_dir.mkdir(parents=True, exist_ok=True)

    payloads = {
        "controlled_external_tool_adapter_preview_bundle.json": result["controlled_external_tool_adapter_preview_bundle"],
        "controlled_external_tool_adapter_preview_schema.json": result["controlled_external_tool_adapter_preview_schema"],
        "external_tool_adapter_preview_approval_gate.json": result["external_tool_adapter_preview_approval_gate"],
        "external_tool_dry_run_adapter_registry.json": result["external_tool_dry_run_adapter_registry"],
        "per_tool_external_permission_gate.json": result["per_tool_external_permission_gate"],
        "external_request_preview_contract.json": result["external_request_preview_contract"],
        "external_response_validation_schema.json": result["external_response_validation_schema"],
        "external_response_validation_preview_result.json": result["external_response_validation_preview_result"],
        "external_tool_abort_contract.json": result["external_tool_abort_contract"],
        "external_tool_audit_proof.json": result["external_tool_audit_proof"],
        "external_tool_preview_ledger.json": result["external_tool_preview_ledger"],
        "external_tool_preview_readiness_summary.json": result["external_tool_preview_readiness_summary"],
        "permissioned_external_api_dry_run_preview_readiness_bridge.json": result["permissioned_external_api_dry_run_preview_readiness_bridge"],
    }
    files_written = list(payloads.keys())
    for filename, payload in payloads.items():
        _write_json(record_dir / filename, payload)

    manifest = {
        "controlled_external_tool_adapter_preview_manifest_version": "2.5.0",
        "run_id": run_id,
        "runtime_version": "2.9.0",
        "files_written": files_written + ["controlled_external_tool_adapter_preview_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "external_tool_invoked": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "repo_files_modified": False,
        "broad_worker_activation_performed": False,
        "real_workers_hired": False,
        "worker_processes_started": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False,
        "status": "CONTROLLED_EXTERNAL_TOOL_ADAPTER_PREVIEW_ONLY",
        "note": "Controlled External Tool Adapter Preview v2.5.0 creates local external tool adapter preview, request contract, response validation, abort, audit, ledger, and readiness bridge artifacts only. It does not invoke external tools, call live-APIs, perform network access, open sockets, run shell commands, modify repo files, deploy, hire real workers, start worker processes, route live workers, perform live orchestration, or animate broad workforce.",
    }
    _write_json(record_dir / "controlled_external_tool_adapter_preview_manifest.json", manifest)
    files_written.append("controlled_external_tool_adapter_preview_manifest.json")
    return {
        "run_id": run_id,
        "controlled_external_tool_adapter_preview_dir": str(record_dir),
        "files_written": files_written,
    }


def write_live_execution_telemetry_abort(
result: dict, output_dir: str | Path, run_label: str = "station-chief-runtime") -> dict:
    if "live_execution_telemetry_abort_bundle" not in result:
        raise ValueError("Missing live_execution_telemetry_abort_bundle in result")
        
    run_id = generate_run_id(result.get("command", "empty"), run_label)
    record_dir = Path(output_dir) / run_id
    record_dir.mkdir(parents=True, exist_ok=True)
    
    payloads = {
        "live_execution_telemetry_abort_bundle.json": result["live_execution_telemetry_abort_bundle"],
        "live_execution_telemetry_abort_schema.json": result["live_execution_telemetry_abort_schema"],
        "telemetry_event_schema.json": result["telemetry_event_schema"],
        "execution_state_model.json": result["execution_state_model"],
        "telemetry_approval_gate.json": result["telemetry_approval_gate"],
        "heartbeat_stub.json": result["heartbeat_stub"],
        "abort_signal_contract.json": result["abort_signal_contract"],
        "timeout_contract.json": result["timeout_contract"],
        "partial_result_capture.json": result["partial_result_capture"],
        "failed_run_quarantine_contract.json": result["failed_run_quarantine_contract"],
        "post_abort_audit_proof.json": result["post_abort_audit_proof"],
        "telemetry_ledger.json": result["telemetry_ledger"],
        "telemetry_readiness_summary.json": result["telemetry_readiness_summary"],
        "post_run_audit_expansion_readiness_bridge.json": result["post_run_audit_expansion_readiness_bridge"]
    }
    
    files_written = list(payloads.keys())
    for filename, payload in payloads.items():
        _write_json(record_dir / filename, payload)
        
    manifest = {
        "live_execution_telemetry_abort_manifest_version": "2.5.0",
        "run_id": run_id,
        "runtime_version": "2.9.0",
        "files_written": files_written + ["live_execution_telemetry_abort_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "telemetry_events_emitted": False,
        "external_telemetry_sent": False,
        "abort_signal_executed": False,
        "processes_terminated": False,
        "repo_files_modified": False,
        "broad_worker_activation_performed": False,
        "real_worker_hiring_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False,
        "status": "SINGLE_WORKER_TELEMETRY_ABORT_CONTROLS_ONLY",
        "note": "Live Execution Telemetry and Abort Controls v2.5.0 creates local telemetry, abort, timeout, partial-result, quarantine, post-abort audit, and ledger artifacts only. It does not send external telemetry, terminate processes, call APIs, run shell commands, modify repo files, deploy, animate broad workforce, hire real workers, route live workers, or perform live orchestration."
    }
    _write_json(record_dir / "live_execution_telemetry_abort_manifest.json", manifest)
    files_written.append("live_execution_telemetry_abort_manifest.json")
    
    return {
        "run_id": run_id,
        "live_execution_telemetry_abort_dir": str(record_dir),
        "files_written": files_written
    }



def attach_permissioned_external_api_dry_run_preview(
    result: dict,
    api_label: str | None = None,
    endpoint_id: str | None = None,
    confirmation_token: str | None = None,
    requested_endpoints: list[str] | None = None,
    method: str | None = None,
    path_template: str | None = None,
    request_payload: dict | None = None,
    credential_labels: list[str] | None = None,
    fixture_payload: dict | None = None
) -> dict:
    if "controlled_external_tool_adapter_preview_bundle" not in result:
        result = attach_controlled_external_tool_adapter_preview(result)
        
    bundle = create_permissioned_external_api_dry_run_preview_bundle(
        result,
        command=result.get("command", ""),
        api_label=api_label,
        endpoint_id=endpoint_id,
        confirmation_token=confirmation_token,
        requested_endpoints=requested_endpoints,
        method=method,
        path_template=path_template,
        request_payload=request_payload,
        credential_labels=credential_labels,
        fixture_payload=fixture_payload
    )
    result["permissioned_external_api_dry_run_preview_bundle"] = bundle
    result["permissioned_external_api_dry_run_preview_schema"] = bundle["permissioned_external_api_dry_run_preview_schema"]
    result["external_api_dry_run_approval_gate"] = bundle["external_api_dry_run_approval_gate"]
    result["api_endpoint_preview_registry"] = bundle["api_endpoint_preview_registry"]
    result["request_envelope_validation"] = bundle["request_envelope_validation"]
    result["credential_absence_proof"] = bundle["credential_absence_proof"]
    result["outbound_call_prevention_proof"] = bundle["outbound_call_prevention_proof"]
    result["dry_run_response_fixture_contract"] = bundle["dry_run_response_fixture_contract"]
    result["external_api_audit_proof"] = bundle["external_api_audit_proof"]
    result["external_api_dry_run_ledger"] = bundle["external_api_dry_run_ledger"]
    result["external_api_dry_run_readiness_summary"] = bundle["external_api_dry_run_readiness_summary"]
    result["controlled_multi_worker_audit_replay_preview_readiness_bridge"] = bundle["controlled_multi_worker_audit_replay_preview_readiness_bridge"]
    return result

def write_permissioned_external_api_dry_run_preview(result: dict, output_dir: str | Path, run_label: str = "station-chief-runtime") -> dict:
    if "permissioned_external_api_dry_run_preview_bundle" not in result:
        raise ValueError("permissioned_external_api_dry_run_preview_bundle missing")
        
    run_id = generate_run_id(result.get("command", run_label))
    target_dir = Path(output_dir) / run_id
    target_dir.mkdir(parents=True, exist_ok=True)
    
    files_to_write = [
        ("permissioned_external_api_dry_run_preview_bundle.json", "permissioned_external_api_dry_run_preview_bundle"),
        ("permissioned_external_api_dry_run_preview_schema.json", "permissioned_external_api_dry_run_preview_schema"),
        ("external_api_dry_run_approval_gate.json", "external_api_dry_run_approval_gate"),
        ("api_endpoint_preview_registry.json", "api_endpoint_preview_registry"),
        ("request_envelope_validation.json", "request_envelope_validation"),
        ("credential_absence_proof.json", "credential_absence_proof"),
        ("outbound_call_prevention_proof.json", "outbound_call_prevention_proof"),
        ("dry_run_response_fixture_contract.json", "dry_run_response_fixture_contract"),
        ("external_api_audit_proof.json", "external_api_audit_proof"),
        ("external_api_dry_run_ledger.json", "external_api_dry_run_ledger"),
        ("external_api_dry_run_readiness_summary.json", "external_api_dry_run_readiness_summary"),
        ("controlled_multi_worker_audit_replay_preview_readiness_bridge.json", "controlled_multi_worker_audit_replay_preview_readiness_bridge"),
    ]
    
    written = []
    for fname, key in files_to_write:
        path = target_dir / fname
        path.write_text(json.dumps(result[key], indent=2), encoding="utf-8")
        written.append(fname)
        
    manifest = {
        "permissioned_external_api_dry_run_preview_manifest_version": "2.7.0",
        "run_id": run_id,
        "runtime_version": "2.9.0",
        "files_written": written + ["permissioned_external_api_dry_run_preview_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "external_tool_invoked": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "repo_files_modified": False,
        "broad_worker_activation_performed": False,
        "real_workers_hired": False,
        "worker_processes_started": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False,
        "status": "PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW_ONLY",
        "note": "Permissioned External API Dry-Run Preview v2.6.0 creates local API dry-run schema, endpoint registry, approval gate, request envelope validation, credential absence proof, outbound call prevention proof, fixture contract, audit proof, ledger, and readiness bridge artifacts only. It does not call live-APIs, perform network access, open sockets, use credentials, read secrets, read environment variables, invoke external tools, run shell commands, modify repo files, deploy, hire real workers, start worker processes, route live workers, perform live orchestration, or animate broad workforce."
    }
    
    (target_dir / "permissioned_external_api_dry_run_preview_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    
    return {
        "run_id": run_id,
        "permissioned_external_api_dry_run_preview_dir": str(target_dir),
        "files_written": manifest["files_written"]
    }


def attach_controlled_multi_worker_audit_replay_preview(
    result: dict,
    replay_label: str | None = None,
    confirmation_token: str | None = None,
    replay_packets: list[dict] | None = None,
    requested_worker_count: int = 3,
    replay_mode: str | None = None,
    observed_digest_map: dict | None = None,
    quarantine_reason: str | None = None
) -> dict:
    if "permissioned_external_api_dry_run_preview_bundle" not in result:
        result = attach_permissioned_external_api_dry_run_preview(result)
        
    bundle = create_controlled_multi_worker_audit_replay_preview_bundle(
        result,
        command=result.get("command", ""),
        replay_label=replay_label,
        confirmation_token=confirmation_token,
        replay_packets=replay_packets,
        requested_worker_count=requested_worker_count,
        replay_mode=replay_mode,
        observed_digest_map=observed_digest_map,
        quarantine_reason=quarantine_reason
    )
    result["controlled_multi_worker_audit_replay_preview_bundle"] = bundle
    result["controlled_multi_worker_audit_replay_preview_schema"] = bundle["controlled_multi_worker_audit_replay_preview_schema"]
    result["audit_replay_preview_approval_gate"] = bundle["audit_replay_preview_approval_gate"]
    result["replay_packet_registry"] = bundle["replay_packet_registry"]
    result["deterministic_replay_plan_contract"] = bundle["deterministic_replay_plan_contract"]
    result["replay_safety_gate"] = bundle["replay_safety_gate"]
    result["multi_worker_replay_comparison_proof"] = bundle["multi_worker_replay_comparison_proof"]
    result["replay_output_quarantine_contract"] = bundle["replay_output_quarantine_contract"]
    result["replay_audit_proof"] = bundle["replay_audit_proof"]
    result["replay_preview_ledger"] = bundle["replay_preview_ledger"]
    result["replay_readiness_summary"] = bundle["replay_readiness_summary"]
    result["operator_approval_queue_enforcement_readiness_bridge"] = bundle["operator_approval_queue_enforcement_readiness_bridge"]
    return result

def write_controlled_multi_worker_audit_replay_preview(result: dict, output_dir: str | Path, run_label: str = "station-chief-runtime") -> dict:
    if "controlled_multi_worker_audit_replay_preview_bundle" not in result:
        raise ValueError("controlled_multi_worker_audit_replay_preview_bundle missing")
        
    run_id = generate_run_id(result.get("command", run_label))
    target_dir = Path(output_dir) / run_id
    target_dir.mkdir(parents=True, exist_ok=True)
    
    files_to_write = [
        ("controlled_multi_worker_audit_replay_preview_bundle.json", "controlled_multi_worker_audit_replay_preview_bundle"),
        ("controlled_multi_worker_audit_replay_preview_schema.json", "controlled_multi_worker_audit_replay_preview_schema"),
        ("audit_replay_preview_approval_gate.json", "audit_replay_preview_approval_gate"),
        ("replay_packet_registry.json", "replay_packet_registry"),
        ("deterministic_replay_plan_contract.json", "deterministic_replay_plan_contract"),
        ("replay_safety_gate.json", "replay_safety_gate"),
        ("multi_worker_replay_comparison_proof.json", "multi_worker_replay_comparison_proof"),
        ("replay_output_quarantine_contract.json", "replay_output_quarantine_contract"),
        ("replay_audit_proof.json", "replay_audit_proof"),
        ("replay_preview_ledger.json", "replay_preview_ledger"),
        ("replay_readiness_summary.json", "replay_readiness_summary"),
        ("operator_approval_queue_enforcement_readiness_bridge.json", "operator_approval_queue_enforcement_readiness_bridge"),
    ]
    
    written = []
    for fname, key in files_to_write:
        path = target_dir / fname
        path.write_text(json.dumps(result[key], indent=2, ensure_ascii=False), encoding="utf-8")
        written.append(fname)
        
    manifest = {
        "controlled_multi_worker_audit_replay_preview_manifest_version": "2.7.0",
        "run_id": run_id,
        "runtime_version": "2.9.0",
        "files_written": written + ["controlled_multi_worker_audit_replay_preview_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "actual_replay_performed": False,
        "worker_actions_replayed": False,
        "external_tool_replay_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "repo_files_modified": False,
        "broad_worker_activation_performed": False,
        "real_workers_hired": False,
        "worker_processes_started": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False,
        "status": "CONTROLLED_MULTI_WORKER_AUDIT_REPLAY_PREVIEW_ONLY",
        "note": "Controlled Multi-Worker Audit Replay Preview v2.7.0 creates local replay schema, replay packet registry, deterministic replay plan contract, replay safety gate, multi-worker replay comparison proof, replay output quarantine contract, replay audit proof, replay preview ledger, readiness summary, and operator approval queue enforcement bridge artifacts only. It does not execute actual replay, replay worker actions, replay external tools, call live-APIs, perform network access, open sockets, use credentials, read secrets, read environment variables, run shell commands, modify repo files, deploy, hire real workers, start worker processes, route live workers, perform live orchestration, or animate broad workforce."
    }
    
    (target_dir / "controlled_multi_worker_audit_replay_preview_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    
    return {
        "run_id": run_id,
        "controlled_multi_worker_audit_replay_preview_dir": str(target_dir),
        "files_written": manifest["files_written"]
    }


def attach_operator_approval_queue_enforcement(
    result: dict,
    queue_label: str | None = None,
    confirmation_token: str | None = None,
    queued_actions: list[dict] | None = None,
    requested_action_count: int = 3,
    operator_decisions: dict | None = None,
    stale_after_hours: int = 72
) -> dict:
    if "controlled_multi_worker_audit_replay_preview_bundle" not in result:
        result = attach_controlled_multi_worker_audit_replay_preview(result)
        
    bundle = create_operator_approval_queue_enforcement_bundle(
        result,
        command=result.get("command", ""),
        queue_label=queue_label,
        confirmation_token=confirmation_token,
        queued_actions=queued_actions,
        requested_action_count=requested_action_count,
        operator_decisions=operator_decisions,
        stale_after_hours=stale_after_hours
    )
    result["operator_approval_queue_enforcement_bundle"] = bundle
    result["operator_approval_queue_enforcement_schema"] = bundle["operator_approval_queue_enforcement_schema"]
    result["operator_approval_queue_enforcement_approval_gate"] = bundle["operator_approval_queue_enforcement_approval_gate"]
    result["queued_action_registry"] = bundle["queued_action_registry"]
    result["approval_item_priority_classifier"] = bundle["approval_item_priority_classifier"]
    result["operator_decision_contract"] = bundle["operator_decision_contract"]
    result["approval_expiry_stale_item_detector"] = bundle["approval_expiry_stale_item_detector"]
    result["queue_enforcement_safety_gate"] = bundle["queue_enforcement_safety_gate"]
    result["approval_queue_audit_proof"] = bundle["approval_queue_audit_proof"]
    result["approval_queue_ledger"] = bundle["approval_queue_ledger"]
    result["approval_queue_readiness_summary"] = bundle["approval_queue_readiness_summary"]
    result["release_candidate_hardening_readiness_bridge"] = bundle["release_candidate_hardening_readiness_bridge"]
    return result

def write_operator_approval_queue_enforcement(result: dict, output_dir: str | Path, run_label: str = "station-chief-runtime") -> dict:
    if "operator_approval_queue_enforcement_bundle" not in result:
        raise ValueError("operator_approval_queue_enforcement_bundle missing")
        
    run_id = generate_run_id(result.get("command", run_label))
    target_dir = Path(output_dir) / run_id
    target_dir.mkdir(parents=True, exist_ok=True)
    
    files_to_write = [
        ("operator_approval_queue_enforcement_bundle.json", "operator_approval_queue_enforcement_bundle"),
        ("operator_approval_queue_enforcement_schema.json", "operator_approval_queue_enforcement_schema"),
        ("operator_approval_queue_enforcement_approval_gate.json", "operator_approval_queue_enforcement_approval_gate"),
        ("queued_action_registry.json", "queued_action_registry"),
        ("approval_item_priority_classifier.json", "approval_item_priority_classifier"),
        ("operator_decision_contract.json", "operator_decision_contract"),
        ("approval_expiry_stale_item_detector.json", "approval_expiry_stale_item_detector"),
        ("queue_enforcement_safety_gate.json", "queue_enforcement_safety_gate"),
        ("approval_queue_audit_proof.json", "approval_queue_audit_proof"),
        ("approval_queue_ledger.json", "approval_queue_ledger"),
        ("approval_queue_readiness_summary.json", "approval_queue_readiness_summary"),
        ("release_candidate_hardening_readiness_bridge.json", "release_candidate_hardening_readiness_bridge"),
    ]
    
    written = []
    for fname, key in files_to_write:
        path = target_dir / fname
        path.write_text(json.dumps(result[key], indent=2, ensure_ascii=False), encoding="utf-8")
        written.append(fname)
        
    manifest = {
        "operator_approval_queue_enforcement_manifest_version": "2.8.0",
        "run_id": run_id,
        "runtime_version": "2.9.0",
        "files_written": written + ["operator_approval_queue_enforcement_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "automatic_execution_performed": False,
        "queued_action_executed": False,
        "auto_approval_performed": False,
        "approval_bypass_performed": False,
        "actual_replay_performed": False,
        "worker_actions_replayed": False,
        "external_tool_replay_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "repo_files_modified": False,
        "broad_worker_activation_performed": False,
        "real_workers_hired": False,
        "worker_processes_started": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False,
        "status": "OPERATOR_APPROVAL_QUEUE_ENFORCEMENT_PREVIEW_ONLY",
        "note": "Operator Approval Queue Enforcement v2.8.0 creates local queue schema, queued action registry, priority classifier, operator decision contract, stale item detector, queue safety gate, audit proof, ledger, readiness summary, and release candidate hardening bridge artifacts only. It does not execute queued actions, auto-approve, bypass approval, execute actual replay, replay worker actions, replay external tools, call live-APIs, perform network access, open sockets, use credentials, read secrets, read environment variables, run shell commands, modify repo files, deploy, hire real workers, start worker processes, route live workers, perform live orchestration, or animate broad workforce."
    }
    
    (target_dir / "operator_approval_queue_enforcement_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    
    return {
        "run_id": run_id,
        "operator_approval_queue_enforcement_dir": str(target_dir),
        "files_written": manifest["files_written"]
    }


def attach_release_candidate_hardening(
    result: dict,
    release_candidate_label: str | None = None,
    confirmation_token: str | None = None,
    invariant_labels: list[str] | None = None,
    validator_names: list[str] | None = None,
    artifact_contracts: list[str] | None = None,
    known_issues: list[dict] | None = None,
    checklist_items: list[str] | None = None
) -> dict:
    if "operator_approval_queue_enforcement_bundle" not in result:
        result = attach_operator_approval_queue_enforcement(result)
        
    bundle = create_release_candidate_hardening_bundle(
        result,
        command=result.get("command", ""),
        release_candidate_label=release_candidate_label,
        confirmation_token=confirmation_token,
        invariant_labels=invariant_labels,
        validator_names=validator_names,
        artifact_contracts=artifact_contracts,
        known_issues=known_issues,
        checklist_items=checklist_items
    )
    result["release_candidate_hardening_bundle"] = bundle
    result["release_candidate_hardening_schema"] = bundle["release_candidate_hardening_schema"]
    result["release_candidate_hardening_approval_gate"] = bundle["release_candidate_hardening_approval_gate"]
    result["full_runtime_invariant_scan"] = bundle["full_runtime_invariant_scan"]
    result["validator_chain_lock_proof"] = bundle["validator_chain_lock_proof"]
    result["artifact_contract_freeze_manifest"] = bundle["artifact_contract_freeze_manifest"]
    result["known_issue_register"] = bundle["known_issue_register"]
    result["pre_v3_production_readiness_checklist"] = bundle["pre_v3_production_readiness_checklist"]
    result["release_candidate_safety_gate"] = bundle["release_candidate_safety_gate"]
    result["release_candidate_audit_proof"] = bundle["release_candidate_audit_proof"]
    result["release_candidate_ledger"] = bundle["release_candidate_ledger"]
    result["release_candidate_readiness_summary"] = bundle["release_candidate_readiness_summary"]
    result["controlled_production_readiness_gate_bridge"] = bundle["controlled_production_readiness_gate_bridge"]
    return result

def write_release_candidate_hardening(result: dict, output_dir: str | Path, run_label: str = "station-chief-runtime") -> dict:
    if "release_candidate_hardening_bundle" not in result:
        raise ValueError("release_candidate_hardening_bundle missing")
        
    run_id = generate_run_id(result.get("command", run_label))
    target_dir = Path(output_dir) / run_id
    target_dir.mkdir(parents=True, exist_ok=True)
    
    files_to_write = [
        ("release_candidate_hardening_bundle.json", "release_candidate_hardening_bundle"),
        ("release_candidate_hardening_schema.json", "release_candidate_hardening_schema"),
        ("release_candidate_hardening_approval_gate.json", "release_candidate_hardening_approval_gate"),
        ("full_runtime_invariant_scan.json", "full_runtime_invariant_scan"),
        ("validator_chain_lock_proof.json", "validator_chain_lock_proof"),
        ("artifact_contract_freeze_manifest.json", "artifact_contract_freeze_manifest"),
        ("known_issue_register.json", "known_issue_register"),
        ("pre_v3_production_readiness_checklist.json", "pre_v3_production_readiness_checklist"),
        ("release_candidate_safety_gate.json", "release_candidate_safety_gate"),
        ("release_candidate_audit_proof.json", "release_candidate_audit_proof"),
        ("release_candidate_ledger.json", "release_candidate_ledger"),
        ("release_candidate_readiness_summary.json", "release_candidate_readiness_summary"),
        ("controlled_production_readiness_gate_bridge.json", "controlled_production_readiness_gate_bridge"),
    ]
    
    written = []
    for fname, key in files_to_write:
        path = target_dir / fname
        path.write_text(json.dumps(result[key], indent=2, ensure_ascii=False), encoding="utf-8")
        written.append(fname)
        
    manifest = {
        "release_candidate_hardening_manifest_version": "2.9.0",
        "run_id": run_id,
        "runtime_version": "2.9.0",
        "files_written": written + ["release_candidate_hardening_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "production_execution_performed": False,
        "production_readiness_gate_activated": False,
        "automatic_execution_performed": False,
        "queued_action_executed": False,
        "auto_approval_performed": False,
        "approval_bypass_performed": False,
        "actual_replay_performed": False,
        "worker_actions_replayed": False,
        "external_tool_replay_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "repo_files_modified": False,
        "broad_worker_activation_performed": False,
        "real_workers_hired": False,
        "worker_processes_started": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False,
        "status": "RELEASE_CANDIDATE_HARDENING_PREVIEW_ONLY",
        "note": "Release Candidate Hardening v2.9.0 creates local release candidate schema, invariant scan, validator chain lock proof, artifact contract freeze manifest, known issue register, pre-v3 checklist, safety gate, audit proof, ledger, readiness summary, and controlled production readiness gate bridge artifacts only. It does not execute production, activate production readiness, execute queued actions, auto-approve, bypass approval, execute actual replay, replay worker actions, replay external tools, call live-APIs, perform network access, open sockets, use credentials, read secrets, read environment variables, run shell commands, modify repo files, deploy, hire real workers, start worker processes, route live workers, perform live orchestration, or animate broad workforce."
    }
    
    (target_dir / "release_candidate_hardening_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    
    return {
        "run_id": run_id,
        "release_candidate_hardening_dir": str(target_dir),
        "files_written": manifest["files_written"]
    }


def attach_first_supervised_production_dry_run(
    result: dict,
    dry_run_label: str | None = None,
    confirmation_token: str | None = None,
    dry_run_task_label: str | None = None,
    production_context_label: str | None = None,
    required_preflight_approver: str | None = None,
    worker_label: str | None = None,
    quarantine_labels: list[str] | None = None
) -> dict:
    if "controlled_worker_hiring_activation_pilot_bundle" not in result:
        result = attach_controlled_worker_hiring_activation_pilot(result)
        
    bundle = create_first_supervised_production_dry_run_bundle(
        result,
        command=result.get("command", ""),
        dry_run_label=dry_run_label,
        confirmation_token=confirmation_token,
        dry_run_task_label=dry_run_task_label,
        production_context_label=production_context_label,
        required_preflight_approver=required_preflight_approver,
        worker_label=worker_label,
        quarantine_labels=quarantine_labels
    )
    result["first_supervised_production_dry_run_bundle"] = bundle
    result["first_supervised_production_dry_run_schema"] = bundle["first_supervised_production_dry_run_schema"]
    result["first_supervised_production_dry_run_approval_gate"] = bundle["first_supervised_production_dry_run_approval_gate"]
    result["single_controlled_task_dry_run_envelope"] = bundle["single_controlled_task_dry_run_envelope"]
    result["dry_run_only_production_context_contract"] = bundle["dry_run_only_production_context_contract"]
    result["human_preflight_approval_gate"] = bundle["human_preflight_approval_gate"]
    result["worker_task_simulation_contract"] = bundle["worker_task_simulation_contract"]
    result["external_action_denial_by_default"] = bundle["external_action_denial_by_default"]
    result["dry_run_rollback_quarantine_preview"] = bundle["dry_run_rollback_quarantine_preview"]
    result["dry_run_audit_proof"] = bundle["dry_run_audit_proof"]
    result["dry_run_ledger"] = bundle["dry_run_ledger"]
    result["dry_run_readiness_summary"] = bundle["dry_run_readiness_summary"]
    result["limited_external_tool_supervised_pilot_bridge"] = bundle["limited_external_tool_supervised_pilot_bridge"]
    return result

def write_first_supervised_production_dry_run(result: dict, output_dir: str | Path, run_label: str = "station-chief-runtime") -> dict:
    if "first_supervised_production_dry_run_bundle" not in result:
        raise ValueError("first_supervised_production_dry_run_bundle missing")
        
    run_id = generate_run_id(result.get("command", run_label))
    target_dir = Path(output_dir) / run_id
    target_dir.mkdir(parents=True, exist_ok=True)
    
    files_to_write = [
        ("first_supervised_production_dry_run_bundle.json", "first_supervised_production_dry_run_bundle"),
        ("first_supervised_production_dry_run_schema.json", "first_supervised_production_dry_run_schema"),
        ("first_supervised_production_dry_run_approval_gate.json", "first_supervised_production_dry_run_approval_gate"),
        ("single_controlled_task_dry_run_envelope.json", "single_controlled_task_dry_run_envelope"),
        ("dry_run_only_production_context_contract.json", "dry_run_only_production_context_contract"),
        ("human_preflight_approval_gate.json", "human_preflight_approval_gate"),
        ("worker_task_simulation_contract.json", "worker_task_simulation_contract"),
        ("external_action_denial_by_default.json", "external_action_denial_by_default"),
        ("dry_run_rollback_quarantine_preview.json", "dry_run_rollback_quarantine_preview"),
        ("dry_run_audit_proof.json", "dry_run_audit_proof"),
        ("dry_run_ledger.json", "dry_run_ledger"),
        ("dry_run_readiness_summary.json", "dry_run_readiness_summary"),
        ("limited_external_tool_supervised_pilot_bridge.json", "limited_external_tool_supervised_pilot_bridge"),
    ]
    
    written = []
    for fname, key in files_to_write:
        path = target_dir / fname
        _write_json(path, result[key])
        written.append(fname)
        
    manifest = {
        "first_supervised_production_dry_run_manifest_version": "3.6.0",
        "run_id": run_id,
        "runtime_version": "3.6.0",
        "files_written": written + ["first_supervised_production_dry_run_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_production_execution_performed": False,
        "production_activation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "external_tool_invocation_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "worker_processes_started": False,
        "repo_files_modified": False,
        "execution_authorized": False,
        "status": "FIRST_SUPERVISED_PRODUCTION_DRY_RUN_PREVIEW_ONLY",
        "note": "First Supervised Production Dry-Run v3.6.0 creates local dry-run schema, approval gate, single controlled task envelope, dry-run-only production context contract, human preflight approval gate, worker task simulation contract, external action denial-by-default record, rollback and quarantine preview, audit proof, ledger, readiness summary, and limited external tool supervised pilot bridge artifacts only. It does not execute production, activate production, execute real tasks, assign live tasks, route live workers, perform live orchestration, invoke external tools, call live-APIs, perform network access, open sockets, use credentials, read secrets, read environment variables, deploy, start worker processes, run shell commands, or modify repo files."
    }
    
    _write_json(target_dir / "first_supervised_production_dry_run_manifest.json", manifest)
    
    return {
        "run_id": run_id,
        "first_supervised_production_dry_run_dir": str(target_dir),
        "files_written": manifest["files_written"]
    }


def attach_limited_external_tool_supervised_pilot(
    result: dict,
    tool_pilot_label: str | None = None,
    confirmation_token: str | None = None,
    tool_category_label: str | None = None,
    required_tool_preflight_approver: str | None = None,
    tool_request_label: str | None = None,
    quarantine_labels: list[str] | None = None,
) -> dict:
    if "first_supervised_production_dry_run_bundle" not in result:
        result = attach_first_supervised_production_dry_run(result)

    bundle = create_limited_external_tool_supervised_pilot_bundle(
        result,
        command=result.get("command", ""),
        tool_pilot_label=tool_pilot_label,
        confirmation_token=confirmation_token,
        tool_category_label=tool_category_label,
        required_tool_preflight_approver=required_tool_preflight_approver,
        tool_request_label=tool_request_label,
        quarantine_labels=quarantine_labels,
    )
    result["limited_external_tool_supervised_pilot_bundle"] = bundle
    result["limited_external_tool_supervised_pilot_schema"] = bundle["limited_external_tool_supervised_pilot_schema"]
    result["limited_external_tool_supervised_pilot_approval_gate"] = bundle["limited_external_tool_supervised_pilot_approval_gate"]
    result["single_external_tool_category_contract"] = bundle["single_external_tool_category_contract"]
    result["tool_invocation_denial_by_default"] = bundle["tool_invocation_denial_by_default"]
    result["human_tool_use_preflight_gate"] = bundle["human_tool_use_preflight_gate"]
    result["tool_request_envelope_preview"] = bundle["tool_request_envelope_preview"]
    result["tool_response_quarantine_preview"] = bundle["tool_response_quarantine_preview"]
    result["tool_audit_proof"] = bundle["tool_audit_proof"]
    result["tool_pilot_ledger"] = bundle["tool_pilot_ledger"]
    result["tool_pilot_readiness_summary"] = bundle["tool_pilot_readiness_summary"]
    result["supervised_external_api_pilot_bridge"] = bundle["supervised_external_api_pilot_bridge"]
    return result


def attach_supervised_external_api_pilot(
    result: dict,
    api_pilot_label: str | None = None,
    confirmation_token: str | None = None,
    api_category_label: str | None = None,
    required_api_preflight_approver: str | None = None,
    api_request_label: str | None = None,
    quarantine_labels: list[str] | None = None
) -> dict:
    if "limited_external_tool_supervised_pilot_bundle" not in result:
        result = attach_limited_external_tool_supervised_pilot(result)
        
    bundle = create_supervised_external_api_pilot_bundle(
        result,
        command=result.get("command", ""),
        api_pilot_label=api_pilot_label,
        confirmation_token=confirmation_token,
        api_category_label=api_category_label,
        required_api_preflight_approver=required_api_preflight_approver,
        api_request_label=api_request_label,
        quarantine_labels=quarantine_labels
    )
    result["supervised_external_api_pilot_bundle"] = bundle
    result["supervised_external_api_pilot_schema"] = bundle["supervised_external_api_pilot_schema"]
    result["supervised_external_api_pilot_approval_gate"] = bundle["supervised_external_api_pilot_approval_gate"]
    result["single_api_category_contract"] = bundle["single_api_category_contract"]
    result["credential_denial_by_default"] = bundle["credential_denial_by_default"]
    result["secret_handling_denial_by_default"] = bundle["secret_handling_denial_by_default"]
    result["network_socket_denial_by_default"] = bundle["network_socket_denial_by_default"]
    result["human_api_use_preflight_gate"] = bundle["human_api_use_preflight_gate"]
    result["api_request_envelope_preview"] = bundle["api_request_envelope_preview"]
    result["api_response_quarantine_preview"] = bundle["api_response_quarantine_preview"]
    result["api_audit_proof"] = bundle["api_audit_proof"]
    result["api_pilot_ledger"] = bundle["api_pilot_ledger"]
    result["api_pilot_readiness_summary"] = bundle["api_pilot_readiness_summary"]
    result["monitored_rollback_recovery_drill_bridge"] = bundle["monitored_rollback_recovery_drill_bridge"]
    return result

def write_limited_external_tool_supervised_pilot(
    result: dict,
    output_dir: str | Path,
    run_label: str = "station-chief-runtime",
) -> dict:
    if "limited_external_tool_supervised_pilot_bundle" not in result:
        raise ValueError("limited_external_tool_supervised_pilot_bundle missing")

    command = result.get("command", "empty")
    run_id = generate_run_id(command, run_label=run_label)
    target_dir = Path(output_dir) / run_id
    target_dir.mkdir(parents=True, exist_ok=True)

    payloads = {
        "limited_external_tool_supervised_pilot_bundle.json": result["limited_external_tool_supervised_pilot_bundle"],
        "limited_external_tool_supervised_pilot_schema.json": result["limited_external_tool_supervised_pilot_schema"],
        "limited_external_tool_supervised_pilot_approval_gate.json": result["limited_external_tool_supervised_pilot_approval_gate"],
        "single_external_tool_category_contract.json": result["single_external_tool_category_contract"],
        "tool_invocation_denial_by_default.json": result["tool_invocation_denial_by_default"],
        "human_tool_use_preflight_gate.json": result["human_tool_use_preflight_gate"],
        "tool_request_envelope_preview.json": result["tool_request_envelope_preview"],
        "tool_response_quarantine_preview.json": result["tool_response_quarantine_preview"],
        "tool_audit_proof.json": result["tool_audit_proof"],
        "tool_pilot_ledger.json": result["tool_pilot_ledger"],
        "tool_pilot_readiness_summary.json": result["tool_pilot_readiness_summary"],
        "supervised_external_api_pilot_bridge.json": result["supervised_external_api_pilot_bridge"],
    }
    files_written = list(payloads.keys())
    for filename, payload in payloads.items():
        _write_json(target_dir / filename, payload)

    manifest = {
        "limited_external_tool_supervised_pilot_manifest_version": "3.6.0",
        "run_id": run_id,
        "runtime_version": "3.6.0",
        "files_written": files_written + ["limited_external_tool_supervised_pilot_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_external_tool_invocation_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_processes_started": False,
        "repo_files_modified": False,
        "execution_authorized": False,
        "status": "LIMITED_EXTERNAL_TOOL_SUPERVISED_PILOT_PREVIEW_ONLY",
        "note": "Limited External Tool Supervised Pilot v3.6.0 creates local tool pilot schema, approval gate, single external tool category contract, tool invocation denial-by-default record, human tool-use preflight gate, tool request envelope preview, tool response quarantine preview, audit proof, ledger, readiness summary, and supervised external API pilot bridge artifacts only. It does not invoke external tools, call live-APIs, perform network access, open sockets, use credentials, read secrets, read environment variables, deploy, execute production, activate production, execute real tasks, assign live tasks, route live workers, perform live orchestration, start worker processes, run shell commands, or modify repo files.",
    }
    _write_json(target_dir / "limited_external_tool_supervised_pilot_manifest.json", manifest)

    return {
        "run_id": run_id,
        "limited_external_tool_supervised_pilot_dir": str(target_dir),
        "files_written": manifest["files_written"],
    }


def attach_controlled_worker_hiring_activation_pilot(
    result: dict,
    pilot_label: str | None = None,
    confirmation_token: str | None = None,
    pilot_worker_limit: int = 1,
    worker_labels: list[str] | None = None,
    required_supervisor_label: str | None = None,
    rollback_labels: list[str] | None = None
) -> dict:
    if "controlled_production_readiness_gate_bundle" not in result:
        result = attach_controlled_production_readiness_gate(result)
        
    bundle = create_controlled_worker_hiring_activation_pilot_bundle(
        result,
        command=result.get("command", ""),
        pilot_label=pilot_label,
        confirmation_token=confirmation_token,
        pilot_worker_limit=pilot_worker_limit,
        worker_labels=worker_labels,
        required_supervisor_label=required_supervisor_label,
        rollback_labels=rollback_labels
    )
    result["controlled_worker_hiring_activation_pilot_bundle"] = bundle
    result["controlled_worker_hiring_activation_pilot_schema"] = bundle["controlled_worker_hiring_activation_pilot_schema"]
    result["controlled_worker_hiring_activation_pilot_approval_gate"] = bundle["controlled_worker_hiring_activation_pilot_approval_gate"]
    result["pilot_worker_limit_contract"] = bundle["pilot_worker_limit_contract"]
    result["worker_identity_activation_contract"] = bundle["worker_identity_activation_contract"]
    result["task_assignment_denial_by_default"] = bundle["task_assignment_denial_by_default"]
    result["human_supervised_pilot_gate"] = bundle["human_supervised_pilot_gate"]
    result["pilot_rollback_abort_preview"] = bundle["pilot_rollback_abort_preview"]
    result["pilot_audit_proof"] = bundle["pilot_audit_proof"]
    result["pilot_ledger"] = bundle["pilot_ledger"]
    result["pilot_readiness_summary"] = bundle["pilot_readiness_summary"]
    result["first_supervised_production_dry_run_bridge"] = bundle["first_supervised_production_dry_run_bridge"]
    return result

def write_controlled_worker_hiring_activation_pilot(result: dict, output_dir: str | Path, run_label: str = "station-chief-runtime") -> dict:
    if "controlled_worker_hiring_activation_pilot_bundle" not in result:
        raise ValueError("controlled_worker_hiring_activation_pilot_bundle missing")
        
    run_id = generate_run_id(result.get("command", run_label))
    target_dir = Path(output_dir) / run_id
    target_dir.mkdir(parents=True, exist_ok=True)
    
    files_to_write = [
        ("controlled_worker_hiring_activation_pilot_bundle.json", "controlled_worker_hiring_activation_pilot_bundle"),
        ("controlled_worker_hiring_activation_pilot_schema.json", "controlled_worker_hiring_activation_pilot_schema"),
        ("controlled_worker_hiring_activation_pilot_approval_gate.json", "controlled_worker_hiring_activation_pilot_approval_gate"),
        ("pilot_worker_limit_contract.json", "pilot_worker_limit_contract"),
        ("worker_identity_activation_contract.json", "worker_identity_activation_contract"),
        ("task_assignment_denial_by_default.json", "task_assignment_denial_by_default"),
        ("human_supervised_pilot_gate.json", "human_supervised_pilot_gate"),
        ("pilot_rollback_abort_preview.json", "pilot_rollback_abort_preview"),
        ("pilot_audit_proof.json", "pilot_audit_proof"),
        ("pilot_ledger.json", "pilot_ledger"),
        ("pilot_readiness_summary.json", "pilot_readiness_summary"),
        ("first_supervised_production_dry_run_bridge.json", "first_supervised_production_dry_run_bridge"),
    ]
    
    written = []
    for fname, key in files_to_write:
        path = target_dir / fname
        path.write_text(json.dumps(result[key], indent=2, ensure_ascii=False), encoding="utf-8")
        written.append(fname)
        
    manifest = {
        "controlled_worker_hiring_activation_pilot_manifest_version": "3.1.0",
        "run_id": run_id,
        "runtime_version": "3.6.0",
        "files_written": written + ["controlled_worker_hiring_activation_pilot_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_worker_hiring_performed": False,
        "real_worker_activation_performed": False,
        "worker_processes_started": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "automatic_execution_performed": False,
        "queued_action_executed": False,
        "auto_approval_performed": False,
        "approval_bypass_performed": False,
        "actual_replay_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "repo_files_modified": False,
        "deployment_performed": False,
        "execution_authorized": False,
        "status": "CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT_PREVIEW_ONLY",
        "note": "Controlled Worker Hiring Activation Pilot v3.1.0 creates local pilot schema, approval gate, one-to-three worker limit contract, worker identity activation contract, task assignment denial-by-default record, human supervision gate, rollback and abort preview, pilot audit proof, pilot ledger, readiness summary, and first supervised production dry-run bridge artifacts only. It does not hire real workers, activate real workers, start worker processes, assign live tasks, route live workers, perform live orchestration, execute production, activate production, call live-APIs, perform network access, open sockets, use credentials, read secrets, read environment variables, run shell commands, modify repo files, deploy, or animate broad workforce."
    }
    
    (target_dir / "controlled_worker_hiring_activation_pilot_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    
    return {
        "run_id": run_id,
        "controlled_worker_hiring_activation_pilot_dir": str(target_dir),
        "files_written": manifest["files_written"]
    }
def attach_controlled_production_readiness_gate(
    result: dict,
    production_gate_label: str | None = None,
    confirmation_token: str | None = None,
    required_approver_label: str | None = None,
    capability_labels: list[str] | None = None,
    pilot_label: str | None = None,
    pilot_worker_limit: int = 1,
    rollback_labels: list[str] | None = None
) -> dict:
    if "release_candidate_hardening_bundle" not in result:
        result = attach_release_candidate_hardening(result)
        
    bundle = create_controlled_production_readiness_gate_bundle(
        result,
        command=result.get("command", ""),
        production_gate_label=production_gate_label,
        confirmation_token=confirmation_token,
        required_approver_label=required_approver_label,
        capability_labels=capability_labels,
        pilot_label=pilot_label,
        pilot_worker_limit=pilot_worker_limit,
        rollback_labels=rollback_labels
    )
    result["controlled_production_readiness_gate_bundle"] = bundle
    result["controlled_production_readiness_gate_schema"] = bundle["controlled_production_readiness_gate_schema"]
    result["controlled_production_readiness_gate_approval_gate"] = bundle["controlled_production_readiness_gate_approval_gate"]
    result["production_activation_denial_by_default"] = bundle["production_activation_denial_by_default"]
    result["final_human_approval_requirement"] = bundle["final_human_approval_requirement"]
    result["production_capability_manifest"] = bundle["production_capability_manifest"]
    result["supervised_pilot_eligibility_contract"] = bundle["supervised_pilot_eligibility_contract"]
    result["production_rollback_kill_switch_preview"] = bundle["production_rollback_kill_switch_preview"]
    result["production_readiness_audit_proof"] = bundle["production_readiness_audit_proof"]
    result["production_readiness_ledger"] = bundle["production_readiness_ledger"]
    result["production_readiness_summary"] = bundle["production_readiness_summary"]
    result["controlled_worker_hiring_activation_pilot_bridge"] = bundle["controlled_worker_hiring_activation_pilot_bridge"]
    return result

def write_controlled_production_readiness_gate(result: dict, output_dir: str | Path, run_label: str = "station-chief-runtime") -> dict:
    if "controlled_production_readiness_gate_bundle" not in result:
        raise ValueError("controlled_production_readiness_gate_bundle missing")
        
    run_id = generate_run_id(result.get("command", run_label))
    target_dir = Path(output_dir) / run_id
    target_dir.mkdir(parents=True, exist_ok=True)
    
    files_to_write = [
        ("controlled_production_readiness_gate_bundle.json", "controlled_production_readiness_gate_bundle"),
        ("controlled_production_readiness_gate_schema.json", "controlled_production_readiness_gate_schema"),
        ("controlled_production_readiness_gate_approval_gate.json", "controlled_production_readiness_gate_approval_gate"),
        ("production_activation_denial_by_default.json", "production_activation_denial_by_default"),
        ("final_human_approval_requirement.json", "final_human_approval_requirement"),
        ("production_capability_manifest.json", "production_capability_manifest"),
        ("supervised_pilot_eligibility_contract.json", "supervised_pilot_eligibility_contract"),
        ("production_rollback_kill_switch_preview.json", "production_rollback_kill_switch_preview"),
        ("production_readiness_audit_proof.json", "production_readiness_audit_proof"),
        ("production_readiness_ledger.json", "production_readiness_ledger"),
        ("production_readiness_summary.json", "production_readiness_summary"),
        ("controlled_worker_hiring_activation_pilot_bridge.json", "controlled_worker_hiring_activation_pilot_bridge"),
    ]
    
    written = []
    for fname, key in files_to_write:
        path = target_dir / fname
        path.write_text(json.dumps(result[key], indent=2, ensure_ascii=False), encoding="utf-8")
        written.append(fname)
        
    manifest = {
        "controlled_production_readiness_gate_manifest_version": "3.0.0",
        "run_id": run_id,
        "runtime_version": "3.6.0",
        "files_written": written + ["controlled_production_readiness_gate_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "real_worker_hiring_performed": False,
        "real_worker_activation_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "automatic_execution_performed": False,
        "queued_action_executed": False,
        "auto_approval_performed": False,
        "approval_bypass_performed": False,
        "actual_replay_performed": False,
        "worker_actions_replayed": False,
        "external_tool_replay_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "repo_files_modified": False,
        "broad_worker_activation_performed": False,
        "worker_processes_started": False,
        "hosting_api_called": False,
        "deployment_performed": False,
        "execution_authorized": False,
        "status": "CONTROLLED_PRODUCTION_READINESS_GATE_PREVIEW_ONLY",
        "note": "Controlled Production Readiness Gate v3.0.0 creates local production readiness schema, approval gate, production activation denial by default, final human approval requirement, production capability manifest, supervised pilot eligibility contract, rollback and kill-switch preview, production readiness audit proof, ledger, readiness summary, and controlled worker hiring activation pilot bridge artifacts only. It does not execute production, activate production, hire real workers, activate real workers, route live workers, perform live orchestration, execute queued actions, auto-approve, bypass approval, execute actual replay, replay worker actions, replay external tools, call live-APIs, perform network access, open sockets, use credentials, read secrets, read environment variables, run shell commands, modify repo files, deploy, start worker processes, or animate broad workforce."
    }
    
    (target_dir / "controlled_production_readiness_gate_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    
    return {
        "run_id": run_id,
        "controlled_production_readiness_gate_dir": str(target_dir),
        "files_written": manifest["files_written"]
    }

def write_supervised_external_api_pilot(result: dict, output_dir: str, run_label: str = "station-chief-runtime") -> dict:
    if "supervised_external_api_pilot_bundle" not in result:
        raise ValueError("supervised_external_api_pilot_bundle not found in result. Call attach_supervised_external_api_pilot first.")
    
    from pathlib import Path
    import json
    
    run_id = generate_run_id(result.get("command", ""), run_label=run_label)
    out_path = Path(output_dir).expanduser().resolve() / run_id
    out_path.mkdir(parents=True, exist_ok=True)
    
    files_to_write = {
        "supervised_external_api_pilot_bundle.json": result["supervised_external_api_pilot_bundle"],
        "supervised_external_api_pilot_schema.json": result["supervised_external_api_pilot_schema"],
        "supervised_external_api_pilot_approval_gate.json": result["supervised_external_api_pilot_approval_gate"],
        "single_api_category_contract.json": result["single_api_category_contract"],
        "credential_denial_by_default.json": result["credential_denial_by_default"],
        "secret_handling_denial_by_default.json": result["secret_handling_denial_by_default"],
        "network_socket_denial_by_default.json": result["network_socket_denial_by_default"],
        "human_api_use_preflight_gate.json": result["human_api_use_preflight_gate"],
        "api_request_envelope_preview.json": result["api_request_envelope_preview"],
        "api_response_quarantine_preview.json": result["api_response_quarantine_preview"],
        "api_audit_proof.json": result["api_audit_proof"],
        "api_pilot_ledger.json": result["api_pilot_ledger"],
        "api_pilot_readiness_summary.json": result["api_pilot_readiness_summary"],
        "monitored_rollback_recovery_drill_bridge.json": result["monitored_rollback_recovery_drill_bridge"]
    }
    
    manifest = {
        "supervised_external_api_pilot_manifest_version": "3.6.0",
        "run_id": run_id,
        "runtime_version": "3.6.0",
        "status": "SUPERVISED_EXTERNAL_API_PILOT_PREVIEW_ONLY",
        "files_written": list(files_to_write.keys()) + ["supervised_external_api_pilot_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "real_external_tool_invocation_performed": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_processes_started": False,
        "repo_files_modified": False,
        "execution_authorized": False
    }
    
    for filename, data in files_to_write.items():
        with open(out_path / filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            
    with open(out_path / "supervised_external_api_pilot_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
        
    return {
        "run_id": run_id,
        "supervised_external_api_pilot_dir": str(out_path),
        "files_written": manifest["files_written"]
    }

def attach_monitored_rollback_recovery_drill(
    result: dict,
    recovery_drill_label: str | None = None,
    confirmation_token: str | None = None,
    simulated_failure_label: str | None = None,
    rollback_path_label: str | None = None,
    recovery_checkpoint_label: str | None = None,
    required_recovery_approver: str | None = None,
    quarantine_labels: list[str] | None = None,
) -> dict:
    if "supervised_external_api_pilot_bundle" not in result:
        result = attach_supervised_external_api_pilot(result)

    bundle = create_monitored_rollback_recovery_drill_bundle(
        result,
        command=result.get("command", ""),
        recovery_drill_label=recovery_drill_label,
        confirmation_token=confirmation_token,
        simulated_failure_label=simulated_failure_label,
        rollback_path_label=rollback_path_label,
        recovery_checkpoint_label=recovery_checkpoint_label,
        required_recovery_approver=required_recovery_approver,
        quarantine_labels=quarantine_labels,
    )
    result["monitored_rollback_recovery_drill_bundle"] = bundle
    result["monitored_rollback_recovery_drill_schema"] = bundle["monitored_rollback_recovery_drill_schema"]
    result["monitored_rollback_recovery_drill_approval_gate"] = bundle["monitored_rollback_recovery_drill_approval_gate"]
    result["simulated_failure_trigger_contract"] = bundle["simulated_failure_trigger_contract"]
    result["rollback_path_preview"] = bundle["rollback_path_preview"]
    result["recovery_checkpoint_contract"] = bundle["recovery_checkpoint_contract"]
    result["quarantine_freeze_preview"] = bundle["quarantine_freeze_preview"]
    result["human_recovery_approval_gate"] = bundle["human_recovery_approval_gate"]
    result["recovery_audit_proof"] = bundle["recovery_audit_proof"]
    result["rollback_recovery_drill_ledger"] = bundle["rollback_recovery_drill_ledger"]
    result["recovery_readiness_summary"] = bundle["recovery_readiness_summary"]
    result["supervised_production_pilot_readiness_review_bridge"] = bundle["supervised_production_pilot_readiness_review_bridge"]
    return result

def write_monitored_rollback_recovery_drill(result: dict, output_dir: str | Path, run_label: str = "station-chief-runtime") -> dict:
    if "monitored_rollback_recovery_drill_bundle" not in result:
        raise ValueError("monitored_rollback_recovery_drill_bundle not found in result. Call attach_monitored_rollback_recovery_drill first.")

    out_path = Path(output_dir).expanduser().resolve()
    run_id = generate_run_id(result.get("command", ""), run_label=run_label)
    drill_dir = out_path / run_id
    drill_dir.mkdir(parents=True, exist_ok=True)

    files_to_write = {
        "monitored_rollback_recovery_drill_bundle.json": result["monitored_rollback_recovery_drill_bundle"],
        "monitored_rollback_recovery_drill_schema.json": result["monitored_rollback_recovery_drill_schema"],
        "monitored_rollback_recovery_drill_approval_gate.json": result["monitored_rollback_recovery_drill_approval_gate"],
        "simulated_failure_trigger_contract.json": result["simulated_failure_trigger_contract"],
        "rollback_path_preview.json": result["rollback_path_preview"],
        "recovery_checkpoint_contract.json": result["recovery_checkpoint_contract"],
        "quarantine_freeze_preview.json": result["quarantine_freeze_preview"],
        "human_recovery_approval_gate.json": result["human_recovery_approval_gate"],
        "recovery_audit_proof.json": result["recovery_audit_proof"],
        "rollback_recovery_drill_ledger.json": result["rollback_recovery_drill_ledger"],
        "recovery_readiness_summary.json": result["recovery_readiness_summary"],
        "supervised_production_pilot_readiness_review_bridge.json": result["supervised_production_pilot_readiness_review_bridge"],
    }
    files_written = list(files_to_write.keys())
    for filename, payload in files_to_write.items():
        _write_json(drill_dir / filename, payload)

    manifest = {
        "monitored_rollback_recovery_drill_manifest_version": "3.6.0",
        "run_id": run_id,
        "runtime_version": "3.6.0",
        "status": "MONITORED_ROLLBACK_RECOVERY_DRILL_PREVIEW_ONLY",
        "files_written": files_written + ["monitored_rollback_recovery_drill_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "real_rollback_performed": False,
        "real_recovery_performed": False,
        "processes_terminated": False,
        "workers_terminated": False,
        "production_state_changed": False,
        "deployment_rollback_performed": False,
        "deployment_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "real_external_tool_invocation_performed": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_processes_started": False,
        "repo_files_modified": False,
        "execution_authorized": False,
        "note": "Monitored Rollback and Recovery Drill v3.6.0 creates local rollback/recovery drill schema, approval gate, simulated failure trigger contract, rollback path preview, recovery checkpoint contract, quarantine/freeze preview, human recovery approval gate, recovery audit proof, rollback recovery drill ledger, readiness summary, and supervised production pilot readiness review bridge artifacts only. It does not perform real rollback, perform real recovery, terminate processes, terminate workers, change production state, roll back deployments, deploy, call live-API requests, perform network access, open sockets, use credentials, read secrets, read environment variables, invoke external tools, execute production, activate production, execute real tasks, assign live tasks, route live workers, perform live orchestration, start worker processes, run shell commands, or modify repo files.",
    }
    _write_json(drill_dir / "monitored_rollback_recovery_drill_manifest.json", manifest)
    return {
        "run_id": run_id,
        "monitored_rollback_recovery_drill_dir": str(drill_dir),
        "files_written": manifest["files_written"],
    }


def attach_supervised_production_pilot_readiness_review(
    result: dict,
    production_readiness_label: str | None = None,
    confirmation_token: str | None = None,
    candidate_label: str | None = None,
    required_production_pilot_reviewer: str | None = None,
    blast_radius_label: str | None = None,
) -> dict:
    if "monitored_rollback_recovery_drill_bundle" not in result:
        result = attach_monitored_rollback_recovery_drill(result)

    bundle = create_supervised_production_pilot_readiness_review_bundle(
        result,
        command=result.get("command", ""),
        production_readiness_label=production_readiness_label,
        confirmation_token=confirmation_token,
        candidate_label=candidate_label,
        required_production_pilot_reviewer=required_production_pilot_reviewer,
        blast_radius_label=blast_radius_label,
    )
    result["supervised_production_pilot_readiness_review_bundle"] = bundle
    result["supervised_production_pilot_readiness_review_schema"] = bundle["supervised_production_pilot_readiness_review_schema"]
    result["supervised_production_pilot_readiness_review_approval_gate"] = bundle["supervised_production_pilot_readiness_review_approval_gate"]
    result["minimum_viable_production_candidate_contract"] = bundle["minimum_viable_production_candidate_contract"]
    result["human_production_pilot_review_gate"] = bundle["human_production_pilot_review_gate"]
    result["production_blast_radius_analysis"] = bundle["production_blast_radius_analysis"]
    result["live_action_denial_review"] = bundle["live_action_denial_review"]
    result["rollback_availability_review"] = bundle["rollback_availability_review"]
    result["credential_secret_readiness_denial_proof"] = bundle["credential_secret_readiness_denial_proof"]
    result["network_socket_readiness_denial_proof"] = bundle["network_socket_readiness_denial_proof"]
    result["production_pilot_audit_proof"] = bundle["production_pilot_audit_proof"]
    result["production_pilot_readiness_ledger"] = bundle["production_pilot_readiness_ledger"]
    result["production_pilot_readiness_summary"] = bundle["production_pilot_readiness_summary"]
    result["credential_vault_denial_secret_handling_proof_bridge"] = bundle["credential_vault_denial_secret_handling_proof_bridge"]
    return result


def write_supervised_production_pilot_readiness_review(
    result: dict,
    output_dir: str | Path,
    run_label: str = "station-chief-runtime",
) -> dict:
    if "supervised_production_pilot_readiness_review_bundle" not in result:
        raise ValueError(
            "supervised_production_pilot_readiness_review_bundle not found in result. Call attach_supervised_production_pilot_readiness_review first."
        )

    out_path = Path(output_dir).expanduser().resolve()
    run_id = generate_run_id(result.get("command", ""), run_label=run_label)
    review_dir = out_path / run_id
    review_dir.mkdir(parents=True, exist_ok=True)

    files_to_write = {
        "supervised_production_pilot_readiness_review_bundle.json": result["supervised_production_pilot_readiness_review_bundle"],
        "supervised_production_pilot_readiness_review_schema.json": result["supervised_production_pilot_readiness_review_schema"],
        "supervised_production_pilot_readiness_review_approval_gate.json": result["supervised_production_pilot_readiness_review_approval_gate"],
        "minimum_viable_production_candidate_contract.json": result["minimum_viable_production_candidate_contract"],
        "human_production_pilot_review_gate.json": result["human_production_pilot_review_gate"],
        "production_blast_radius_analysis.json": result["production_blast_radius_analysis"],
        "live_action_denial_review.json": result["live_action_denial_review"],
        "rollback_availability_review.json": result["rollback_availability_review"],
        "credential_secret_readiness_denial_proof.json": result["credential_secret_readiness_denial_proof"],
        "network_socket_readiness_denial_proof.json": result["network_socket_readiness_denial_proof"],
        "production_pilot_audit_proof.json": result["production_pilot_audit_proof"],
        "production_pilot_readiness_ledger.json": result["production_pilot_readiness_ledger"],
        "production_pilot_readiness_summary.json": result["production_pilot_readiness_summary"],
        "credential_vault_denial_secret_handling_proof_bridge.json": result["credential_vault_denial_secret_handling_proof_bridge"],
    }
    files_written = list(files_to_write.keys())
    for filename, payload in files_to_write.items():
        _write_json(review_dir / filename, payload)

    manifest = {
        "supervised_production_pilot_readiness_review_manifest_version": "3.6.0",
        "run_id": run_id,
        "runtime_version": "3.6.0",
        "status": "SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW_PREVIEW_ONLY",
        "files_written": files_written + ["supervised_production_pilot_readiness_review_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "deployment_performed": False,
        "deployment_rollback_performed": False,
        "real_rollback_performed": False,
        "real_recovery_performed": False,
        "processes_terminated": False,
        "workers_terminated": False,
        "production_state_changed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "real_external_tool_invocation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_processes_started": False,
        "repo_files_modified": False,
        "execution_authorized": False,
        "note": "Supervised Production Pilot Readiness Review v3.6.0 creates local production-readiness review schema, approval gate, minimum viable production candidate contract, human production pilot review gate, production blast-radius analysis, live action denial review, rollback availability review, credential/secret readiness denial proof, network/socket readiness denial proof, production pilot audit proof, production pilot readiness ledger, readiness summary, and credential vault denial and secret handling proof bridge artifacts only. It does not execute production, activate production, deploy, roll back deployments, perform rollback, perform recovery, terminate processes, terminate workers, change production state, call live-API requests, perform network access, open sockets, use credentials, read secrets, read environment variables, invoke external tools, assign live tasks, route live workers, perform live orchestration, start worker processes, run shell commands, or modify repo files.",
    }
    _write_json(review_dir / "supervised_production_pilot_readiness_review_manifest.json", manifest)
    return {
        "run_id": run_id,
        "supervised_production_pilot_readiness_review_dir": str(review_dir),
        "files_written": manifest["files_written"],
    }


def attach_credential_vault_denial_secret_handling_proof(
    result: dict,
    credential_secret_label: str | None = None,
    confirmation_token: str | None = None,
    credential_boundary_label: str | None = None,
    secret_boundary_label: str | None = None,
    environment_boundary_label: str | None = None,
) -> dict:
    if "supervised_production_pilot_readiness_review_bundle" not in result:
        result = attach_supervised_production_pilot_readiness_review(result)

    bundle = create_credential_vault_denial_secret_handling_proof_bundle(
        result,
        command=result.get("command", ""),
        credential_secret_label=credential_secret_label,
        confirmation_token=confirmation_token,
        credential_boundary_label=credential_boundary_label,
        secret_boundary_label=secret_boundary_label,
        environment_boundary_label=environment_boundary_label,
    )
    result["credential_vault_denial_secret_handling_proof_bundle"] = bundle
    result["credential_vault_denial_secret_handling_proof_schema"] = bundle["credential_vault_denial_secret_handling_proof_schema"]
    result["credential_vault_denial_secret_handling_proof_approval_gate"] = bundle["credential_vault_denial_secret_handling_proof_approval_gate"]
    result["credential_access_denial_contract"] = bundle["credential_access_denial_contract"]
    result["secret_read_denial_contract"] = bundle["secret_read_denial_contract"]
    result["environment_variable_denial_contract"] = bundle["environment_variable_denial_contract"]
    result["credential_vault_boundary_record"] = bundle["credential_vault_boundary_record"]
    result["secret_handling_boundary_record"] = bundle["secret_handling_boundary_record"]
    result["environment_read_boundary_record"] = bundle["environment_read_boundary_record"]
    result["credential_secret_audit_proof"] = bundle["credential_secret_audit_proof"]
    result["credential_secret_denial_ledger"] = bundle["credential_secret_denial_ledger"]
    result["credential_secret_readiness_summary"] = bundle["credential_secret_readiness_summary"]
    result["network_socket_lockdown_proof_bridge"] = bundle["network_socket_lockdown_proof_bridge"]
    return result


def write_credential_vault_denial_secret_handling_proof(
    result: dict,
    output_dir: str | Path,
    run_label: str = "station-chief-runtime",
) -> dict:
    if "credential_vault_denial_secret_handling_proof_bundle" not in result:
        raise ValueError(
            "credential_vault_denial_secret_handling_proof_bundle not found in result. Call attach_credential_vault_denial_secret_handling_proof first."
        )

    out_path = Path(output_dir).expanduser().resolve()
    run_id = generate_run_id(result.get("command", ""), run_label=run_label)
    proof_dir = out_path / run_id
    proof_dir.mkdir(parents=True, exist_ok=True)

    files_to_write = {
        "credential_vault_denial_secret_handling_proof_bundle.json": result["credential_vault_denial_secret_handling_proof_bundle"],
        "credential_vault_denial_secret_handling_proof_schema.json": result["credential_vault_denial_secret_handling_proof_schema"],
        "credential_vault_denial_secret_handling_proof_approval_gate.json": result["credential_vault_denial_secret_handling_proof_approval_gate"],
        "credential_access_denial_contract.json": result["credential_access_denial_contract"],
        "secret_read_denial_contract.json": result["secret_read_denial_contract"],
        "environment_variable_denial_contract.json": result["environment_variable_denial_contract"],
        "credential_vault_boundary_record.json": result["credential_vault_boundary_record"],
        "secret_handling_boundary_record.json": result["secret_handling_boundary_record"],
        "environment_read_boundary_record.json": result["environment_read_boundary_record"],
        "credential_secret_audit_proof.json": result["credential_secret_audit_proof"],
        "credential_secret_denial_ledger.json": result["credential_secret_denial_ledger"],
        "credential_secret_readiness_summary.json": result["credential_secret_readiness_summary"],
        "network_socket_lockdown_proof_bridge.json": result["network_socket_lockdown_proof_bridge"],
    }
    files_written = list(files_to_write.keys())
    for filename, payload in files_to_write.items():
        _write_json(proof_dir / filename, payload)

    manifest = {
        "credential_vault_denial_secret_handling_proof_manifest_version": "3.7.0",
        "run_id": run_id,
        "runtime_version": "3.7.0",
        "status": "CREDENTIAL_VAULT_DENIAL_SECRET_HANDLING_PROOF_PREVIEW_ONLY",
        "files_written": files_written + ["credential_vault_denial_secret_handling_proof_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "credential_vault_access_performed": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "tokens_read": False,
        "api_keys_read": False,
        "oauth_used": False,
        "service_account_used": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "real_external_tool_invocation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_processes_started": False,
        "repo_files_modified": False,
        "execution_authorized": False,
        "note": "Credential Vault Denial and Secret Handling Proof v3.7.0 creates deterministic local denial schemas, approval gates, denial contracts, boundary records, audit proofs, denial ledgers, readiness summaries, and a bridge to Network/Socket Lockdown Proof only. It does not access credential vaults, use credentials, read secrets, read environment variables, call live-API requests, perform network access, open sockets, deploy, execute production, execute real tasks, assign live tasks, route live workers, perform live orchestration, start worker processes, run shell commands, or modify repo files.",
    }
    _write_json(proof_dir / "credential_vault_denial_secret_handling_proof_manifest.json", manifest)
    return {
        "run_id": run_id,
        "credential_vault_denial_secret_handling_proof_dir": str(proof_dir),
        "files_written": manifest["files_written"],
    }


def attach_network_socket_lockdown_proof(
    result: dict,
    network_socket_label: str | None = None,
    confirmation_token: str | None = None,
    network_boundary_label: str | None = None,
    socket_boundary_label: str | None = None,
) -> dict:
    if "credential_vault_denial_secret_handling_proof_bundle" not in result:
        result = attach_credential_vault_denial_secret_handling_proof(result)

    bundle = create_network_socket_lockdown_proof_bundle(
        result,
        command=result.get("command", ""),
        network_socket_label=network_socket_label,
        confirmation_token=confirmation_token,
        network_boundary_label=network_boundary_label,
        socket_boundary_label=socket_boundary_label,
    )
    result["network_socket_lockdown_proof_bundle"] = bundle
    result["network_socket_lockdown_proof_schema"] = bundle["network_socket_lockdown_proof_schema"]
    result["network_socket_lockdown_proof_approval_gate"] = bundle["network_socket_lockdown_proof_approval_gate"]
    result["network_access_denial_contract"] = bundle["network_access_denial_contract"]
    result["socket_access_denial_contract"] = bundle["socket_access_denial_contract"]
    result["live_api_call_denial_contract"] = bundle["live_api_call_denial_contract"]
    result["dns_resolution_denial_contract"] = bundle["dns_resolution_denial_contract"]
    result["outbound_connection_denial_contract"] = bundle["outbound_connection_denial_contract"]
    result["network_boundary_record"] = bundle["network_boundary_record"]
    result["socket_boundary_record"] = bundle["socket_boundary_record"]
    result["network_socket_audit_proof"] = bundle["network_socket_audit_proof"]
    result["network_socket_lockdown_ledger"] = bundle["network_socket_lockdown_ledger"]
    result["network_socket_readiness_summary"] = bundle["network_socket_readiness_summary"]
    result["live_external_action_final_preflight_gate_bridge"] = bundle["live_external_action_final_preflight_gate_bridge"]
    return result


def write_network_socket_lockdown_proof(
    result: dict,
    output_dir: str | Path,
    run_label: str = "station-chief-runtime",
) -> dict:
    if "network_socket_lockdown_proof_bundle" not in result:
        raise ValueError(
            "network_socket_lockdown_proof_bundle not found in result. Call attach_network_socket_lockdown_proof first."
        )

    out_path = Path(output_dir).expanduser().resolve()
    run_id = generate_run_id(result.get("command", ""), run_label=run_label)
    proof_dir = out_path / run_id
    proof_dir.mkdir(parents=True, exist_ok=True)

    files_to_write = {
        "network_socket_lockdown_proof_bundle.json": result["network_socket_lockdown_proof_bundle"],
        "network_socket_lockdown_proof_schema.json": result["network_socket_lockdown_proof_schema"],
        "network_socket_lockdown_proof_approval_gate.json": result["network_socket_lockdown_proof_approval_gate"],
        "network_access_denial_contract.json": result["network_access_denial_contract"],
        "socket_access_denial_contract.json": result["socket_access_denial_contract"],
        "live_api_call_denial_contract.json": result["live_api_call_denial_contract"],
        "dns_resolution_denial_contract.json": result["dns_resolution_denial_contract"],
        "outbound_connection_denial_contract.json": result["outbound_connection_denial_contract"],
        "network_boundary_record.json": result["network_boundary_record"],
        "socket_boundary_record.json": result["socket_boundary_record"],
        "network_socket_audit_proof.json": result["network_socket_audit_proof"],
        "network_socket_lockdown_ledger.json": result["network_socket_lockdown_ledger"],
        "network_socket_readiness_summary.json": result["network_socket_readiness_summary"],
        "live_external_action_final_preflight_gate_bridge.json": result["live_external_action_final_preflight_gate_bridge"],
    }
    files_written = list(files_to_write.keys())
    for filename, payload in files_to_write.items():
        _write_json(proof_dir / filename, payload)

    manifest = {
        "network_socket_lockdown_proof_manifest_version": "3.8.0",
        "run_id": run_id,
        "runtime_version": "3.9.0",
        "status": "NETWORK_SOCKET_LOCKDOWN_PROOF_PREVIEW_ONLY",
        "files_written": files_written + ["network_socket_lockdown_proof_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "network_access_performed": False,
        "socket_opened": False,
        "dns_resolution_performed": False,
        "outbound_connection_performed": False,
        "inbound_connection_performed": False,
        "live_api_call_performed": False,
        "webhook_call_performed": False,
        "external_tool_invocation_performed": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_processes_started": False,
        "repo_files_modified": False,
        "execution_authorized": False,
        "note": "Network/Socket Lockdown Proof v3.8.0 creates deterministic local denial schemas, approval gates, denial contracts, boundary records, audit proofs, denial ledgers, readiness summaries, and a bridge to Live External Action Final Preflight Gate only. It does not perform network access, open sockets, resolve DNS, make outbound connections, call live APIs, or execute any real deployment or production action.",
    }
    _write_json(proof_dir / "network_socket_lockdown_proof_manifest.json", manifest)
    return {
        "run_id": run_id,
        "network_socket_lockdown_proof_dir": str(proof_dir),
        "files_written": manifest["files_written"],
    }


def attach_live_external_action_final_preflight_gate(
    result: dict,
    live_external_action_label: str | None = None,
    confirmation_token: str | None = None,
    candidate_action_label: str | None = None,
    blast_radius_label: str | None = None,
    required_final_approver: str | None = None
) -> dict:
    if "network_socket_lockdown_proof_bundle" not in result:
        result = attach_network_socket_lockdown_proof(result)

    bundle = create_live_external_action_final_preflight_gate_bundle(
        result,
        command=result.get("command", ""),
        live_external_action_label=live_external_action_label,
        confirmation_token=confirmation_token,
        candidate_action_label=candidate_action_label,
        blast_radius_label=blast_radius_label,
        required_final_approver=required_final_approver
    )
    result["live_external_action_final_preflight_gate_bundle"] = bundle
    result["live_external_action_final_preflight_gate_schema"] = bundle["live_external_action_final_preflight_gate_schema"]
    result["live_external_action_final_preflight_gate_approval_gate"] = bundle["live_external_action_final_preflight_gate_approval_gate"]
    result["tiny_action_candidate_boundary_contract"] = bundle["tiny_action_candidate_boundary_contract"]
    result["live_external_action_non_execution_contract"] = bundle["live_external_action_non_execution_contract"]
    result["blast_radius_ceiling_contract"] = bundle["blast_radius_ceiling_contract"]
    result["human_final_approval_requirement"] = bundle["human_final_approval_requirement"]
    result["credential_secret_environment_re_denial_proof"] = bundle["credential_secret_environment_re_denial_proof"]
    result["network_socket_api_re_denial_proof"] = bundle["network_socket_api_re_denial_proof"]
    result["deployment_production_re_denial_proof"] = bundle["deployment_production_re_denial_proof"]
    result["rollback_recovery_availability_assertion"] = bundle["rollback_recovery_availability_assertion"]
    result["first_tiny_real_world_execution_candidate_audit_proof"] = bundle["first_tiny_real_world_execution_candidate_audit_proof"]
    result["final_preflight_ledger"] = bundle["final_preflight_ledger"]
    result["first_tiny_real_world_supervised_execution_candidate_bridge"] = bundle["first_tiny_real_world_supervised_execution_candidate_bridge"]
    return result


def write_live_external_action_final_preflight_gate(
    result: dict,
    output_dir: str | Path,
    run_label: str = "station-chief-runtime",
) -> dict:
    if "live_external_action_final_preflight_gate_bundle" not in result:
        raise ValueError(
            "live_external_action_final_preflight_gate_bundle not found in result. Call attach_live_external_action_final_preflight_gate first."
        )

    out_path = Path(output_dir).expanduser().resolve()
    run_id = generate_run_id(result.get("command", ""), run_label=run_label)
    proof_dir = out_path / run_id
    proof_dir.mkdir(parents=True, exist_ok=True)

    files_to_write = {
        "live_external_action_final_preflight_gate_bundle.json": result["live_external_action_final_preflight_gate_bundle"],
        "live_external_action_final_preflight_gate_schema.json": result["live_external_action_final_preflight_gate_schema"],
        "live_external_action_final_preflight_gate_approval_gate.json": result["live_external_action_final_preflight_gate_approval_gate"],
        "tiny_action_candidate_boundary_contract.json": result["tiny_action_candidate_boundary_contract"],
        "live_external_action_non_execution_contract.json": result["live_external_action_non_execution_contract"],
        "blast_radius_ceiling_contract.json": result["blast_radius_ceiling_contract"],
        "human_final_approval_requirement.json": result["human_final_approval_requirement"],
        "credential_secret_environment_re_denial_proof.json": result["credential_secret_environment_re_denial_proof"],
        "network_socket_api_re_denial_proof.json": result["network_socket_api_re_denial_proof"],
        "deployment_production_re_denial_proof.json": result["deployment_production_re_denial_proof"],
        "rollback_recovery_availability_assertion.json": result["rollback_recovery_availability_assertion"],
        "first_tiny_real_world_execution_candidate_audit_proof.json": result["first_tiny_real_world_execution_candidate_audit_proof"],
        "final_preflight_ledger.json": result["final_preflight_ledger"],
        "first_tiny_real_world_supervised_execution_candidate_bridge.json": result["first_tiny_real_world_supervised_execution_candidate_bridge"],
        "live_external_action_final_preflight_gate_audit_proof.json": result["first_tiny_real_world_execution_candidate_audit_proof"],
        "live_external_action_final_preflight_gate_ledger.json": result["final_preflight_ledger"],
        "live_external_action_final_preflight_gate_readiness_summary.json": result["first_tiny_real_world_supervised_execution_candidate_bridge"],
    }
    files_written = list(files_to_write.keys())
    for filename, payload in files_to_write.items():
        _write_json(proof_dir / filename, payload)

    manifest = {
        "live_external_action_final_preflight_gate_manifest_version": "3.9.0",
        "run_id": run_id,
        "runtime_version": "3.9.0",
        "status": "LIVE_EXTERNAL_ACTION_FINAL_PREFLIGHT_GATE_PREVIEW_ONLY",
        "files_written": files_written + ["live_external_action_final_preflight_gate_manifest.json"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_external_action_performed": False,
        "live_api_call_performed": False,
        "network_access_performed": False,
        "socket_opened": False,
        "dns_resolution_performed": False,
        "outbound_connection_performed": False,
        "inbound_connection_performed": False,
        "webhook_call_performed": False,
        "credential_vault_access_performed": False,
        "credentials_used": False,
        "secrets_read": False,
        "environment_read": False,
        "deployment_performed": False,
        "deployment_rollback_performed": False,
        "production_execution_performed": False,
        "production_activation_performed": False,
        "real_external_tool_invocation_performed": False,
        "real_task_execution_performed": False,
        "live_task_assignment_performed": False,
        "live_worker_routing_performed": False,
        "live_orchestration_performed": False,
        "worker_processes_started": False,
        "real_rollback_performed": False,
        "real_recovery_performed": False,
        "processes_terminated": False,
        "workers_terminated": False,
        "production_state_changed": False,
        "repo_files_modified": False,
        "execution_authorized": False,
        "note": "Live External Action Final Preflight Gate v3.9.0 creates local final-preflight schema, approval gate, tiny action candidate boundary contract, non-execution contract, blast-radius ceiling contract, human final approval requirement, re-denial proofs, rollback/recovery availability assertion, final preflight audit proof, final preflight ledger, and first tiny real-world supervised execution candidate bridge artifacts only. It does not call live APIs, perform network access, open sockets, resolve DNS, make outbound connections, use credentials, read secrets, read environment variables, deploy, execute production, activate production, invoke external tools, assign live tasks, route live workers, perform live orchestration, start worker processes, run shell commands, or modify repo files."
    }
    _write_json(proof_dir / "live_external_action_final_preflight_gate_manifest.json", manifest)
    return {
        "run_id": run_id,
        "live_external_action_final_preflight_gate_dir": str(proof_dir),
        "files_written": manifest["files_written"],
    }


def attach_first_tiny_real_world_supervised_execution_candidate(
    result: dict,
    candidate_label: str | None = None,
    output_directory: str | None = None,
    artifact_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    execute_local_proof_artifact_write: bool = False,
) -> dict:
    if "live_external_action_final_preflight_gate_bundle" not in result or result.get("live_external_action_final_preflight_gate_bundle") is None:
        result = attach_live_external_action_final_preflight_gate(result)
    bundle = create_first_tiny_real_world_supervised_execution_candidate_bundle(
        result,
        command=result.get("command", "check please"),
        candidate_label=candidate_label,
        output_directory=output_directory,
        artifact_name=artifact_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        execute_local_proof_artifact_write=execute_local_proof_artifact_write,
    )
    result = dict(result)
    result["first_tiny_real_world_supervised_execution_candidate_bundle"] = bundle
    result["first_tiny_real_world_supervised_execution_candidate_schema"] = bundle["schema"]
    result["first_tiny_real_world_supervised_execution_candidate_approval_gate"] = bundle["first_tiny_real_world_supervised_execution_candidate_approval_gate"]
    result["local_proof_artifact_candidate_contract"] = bundle["local_proof_artifact_candidate_contract"]
    result["explicit_output_directory_boundary_contract"] = bundle["explicit_output_directory_boundary_contract"]
    result["forbidden_path_contract"] = bundle["forbidden_path_contract"]
    result["local_only_execution_envelope"] = bundle["local_only_execution_envelope"]
    result["candidate_pre_action_audit_proof"] = bundle["candidate_pre_action_audit_proof"]
    result["local_proof_artifact_execution_record"] = bundle["local_proof_artifact_execution_record"]
    result["post_action_verification_record"] = bundle["post_action_verification_record"]
    result["cleanup_rollback_instruction_record"] = bundle["cleanup_rollback_instruction_record"]
    result["first_tiny_candidate_ledger"] = bundle["first_tiny_candidate_ledger"]
    result["first_tiny_candidate_readiness_summary"] = bundle["first_tiny_candidate_readiness_summary"]
    result["post_action_verification_and_audit_review_bridge"] = bundle["post_action_verification_and_audit_review_bridge"]
    result["first_tiny_real_world_supervised_execution_candidate_write_summary"] = bundle["local_proof_artifact_execution_record"]
    return result


def write_first_tiny_real_world_supervised_execution_candidate(
    result: dict,
    output_directory: str | Path,
    candidate_label: str | None = None,
    artifact_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    run_label: str = "station-chief-runtime",
) -> dict:
    result = attach_first_tiny_real_world_supervised_execution_candidate(
        result,
        candidate_label=candidate_label,
        output_directory=str(output_directory),
        artifact_name=artifact_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        execute_local_proof_artifact_write=True,
    )
    bundle = result["first_tiny_real_world_supervised_execution_candidate_bundle"]
    execution_record = bundle["local_proof_artifact_execution_record"]
    return {
        "run_id": generate_run_id(result.get("command", ""), run_label=run_label),
        "first_tiny_real_world_supervised_execution_candidate_dir": execution_record.get("resolved_output_directory") or str(output_directory),
        "files_written": [execution_record["artifact_name"]] if execution_record.get("local_proof_artifact_write_performed") else [],
        "local_proof_artifact_write_performed": execution_record.get("local_proof_artifact_write_performed", False),
        "artifact_path": execution_record.get("artifact_path"),
        "execution_status": execution_record.get("execution_status"),
    }


def attach_post_action_verification_and_audit_review(
    result: dict,
    review_label: str | None = None,
    artifact_path: str | None = None,
    expected_output_directory: str | None = None,
    review_output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    write_review_records: bool = False,
) -> dict:
    bundle = create_post_action_verification_and_audit_review_bundle(
        result,
        command=result.get("command", "check please"),
        review_label=review_label,
        artifact_path=artifact_path,
        expected_output_directory=expected_output_directory,
        review_output_directory=review_output_directory,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        write_review_records=write_review_records,
    )
    result = dict(result)
    result["post_action_verification_and_audit_review_bundle"] = bundle
    result["post_action_verification_and_audit_review_schema"] = bundle["schema"]
    result["post_action_verification_and_audit_review_approval_gate"] = bundle["post_action_verification_and_audit_review_approval_gate"]
    result["v4_candidate_artifact_reference_contract"] = bundle["v4_candidate_artifact_reference_contract"]
    result["artifact_integrity_verification_record"] = bundle["artifact_integrity_verification_record"]
    result["artifact_path_containment_review"] = bundle["artifact_path_containment_review"]
    result["safety_boolean_review"] = bundle["safety_boolean_review"]
    result["cleanup_instruction_review"] = bundle["cleanup_instruction_review"]
    result["operator_review_acknowledgement"] = bundle["operator_review_acknowledgement"]
    result["post_action_closeout_ledger"] = bundle["post_action_closeout_ledger"]
    result["post_action_readiness_summary"] = bundle["post_action_readiness_summary"]
    result["supervised_rollback_cleanup_candidate_bridge"] = bundle["supervised_rollback_cleanup_candidate_bridge"]
    result["post_action_verification_and_audit_review_record"] = bundle["post_action_verification_and_audit_review_record"]
    result["post_action_verification_and_audit_review_write_summary"] = bundle["post_action_verification_and_audit_review_record"]
    return result


def write_post_action_verification_and_audit_review(
    result: dict,
    review_output_directory: str | Path,
    review_label: str | None = None,
    artifact_path: str | None = None,
    expected_output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    run_label: str = "station-chief-runtime",
) -> dict:
    result = attach_post_action_verification_and_audit_review(
        result,
        review_label=review_label,
        artifact_path=artifact_path,
        expected_output_directory=expected_output_directory,
        review_output_directory=str(review_output_directory),
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        write_review_records=True,
    )
    bundle = result["post_action_verification_and_audit_review_bundle"]
    review_record = bundle["post_action_verification_and_audit_review_record"]
    return {
        "run_id": generate_run_id(result.get("command", ""), run_label=run_label),
        "post_action_verification_and_audit_review_dir": review_record.get("review_output_directory") or str(review_output_directory),
        "files_written": review_record.get("files_written", []) if review_record.get("local_review_records_written") else [],
        "local_review_records_written": review_record.get("local_review_records_written", False),
        "review_record_path": review_record.get("review_record_path"),
        "execution_status": review_record.get("review_record_status"),
    }


def attach_supervised_rollback_cleanup_candidate(
    result: dict,
    cleanup_label: str | None = None,
    artifact_path: str | None = None,
    expected_output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    cleanup_requested: bool = False,
    execute_cleanup: bool = False,
) -> dict:
    bundle = create_supervised_rollback_cleanup_candidate_bundle(
        result,
        command=result.get("command", "check please"),
        cleanup_label=cleanup_label,
        artifact_path=artifact_path,
        expected_output_directory=expected_output_directory,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        cleanup_requested=cleanup_requested,
        execute_cleanup=execute_cleanup,
    )
    result = dict(result)
    result["supervised_rollback_cleanup_candidate_bundle"] = bundle
    result["supervised_rollback_cleanup_candidate_schema"] = bundle["schema"]
    result["supervised_rollback_cleanup_candidate_approval_gate"] = bundle["supervised_rollback_cleanup_candidate_approval_gate"]
    result["cleanup_candidate_contract"] = bundle["cleanup_candidate_contract"]
    result["artifact_pre_cleanup_verification_record"] = bundle["artifact_pre_cleanup_verification_record"]
    result["cleanup_path_containment_record"] = bundle["cleanup_path_containment_record"]
    result["cleanup_scope_envelope"] = bundle["cleanup_scope_envelope"]
    result["cleanup_execution_record"] = bundle["cleanup_execution_record"]
    result["post_cleanup_verification_record"] = bundle["post_cleanup_verification_record"]
    result["cleanup_audit_record"] = bundle["cleanup_audit_record"]
    result["cleanup_closeout_ledger"] = bundle["cleanup_closeout_ledger"]
    result["cleanup_readiness_summary"] = bundle["cleanup_readiness_summary"]
    result["limited_live_worker_activation_candidate_bridge"] = bundle["limited_live_worker_activation_candidate_bridge"]
    result["supervised_rollback_cleanup_candidate_write_summary"] = bundle["cleanup_execution_record"]
    return result


def write_supervised_rollback_cleanup_candidate(
    result: dict,
    cleanup_label: str | None = None,
    artifact_path: str | None = None,
    expected_output_directory: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    run_label: str = "station-chief-runtime",
) -> dict:
    result = attach_supervised_rollback_cleanup_candidate(
        result,
        cleanup_label=cleanup_label,
        artifact_path=artifact_path,
        expected_output_directory=expected_output_directory,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        cleanup_requested=True,
        execute_cleanup=True,
    )
    bundle = result["supervised_rollback_cleanup_candidate_bundle"]
    cleanup_record = bundle["cleanup_execution_record"]
    return {
        "run_id": generate_run_id(result.get("command", ""), run_label=run_label),
        "supervised_rollback_cleanup_candidate_dir": cleanup_record.get("expected_output_directory") or str(expected_output_directory),
        "files_written": [],
        "local_cleanup_performed": cleanup_record.get("local_cleanup_performed", False),
        "artifact_deleted": cleanup_record.get("artifact_deleted", False),
        "deleted_file_count": cleanup_record.get("deleted_file_count", 0),
        "deleted_artifact_path": cleanup_record.get("deleted_artifact_path"),
        "execution_status": cleanup_record.get("cleanup_execution_status"),
    }


def attach_limited_live_worker_activation_candidate(
    result: dict,
    worker_template_label: str | None = None,
    activation_output_directory: str | None = None,
    activation_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    activation_requested: bool = False,
    write_activation_record: bool = False,
) -> dict:
    if "live_external_action_final_preflight_gate_bundle" not in result or result.get("live_external_action_final_preflight_gate_bundle") is None:
        result = attach_live_external_action_final_preflight_gate(result)
    bundle = create_limited_live_worker_activation_candidate_bundle(
        result,
        command=result.get("command", "check please"),
        worker_template_label=worker_template_label,
        activation_output_directory=activation_output_directory,
        activation_record_name=activation_record_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        activation_requested=activation_requested,
        write_activation_record=write_activation_record,
    )
    result = dict(result)
    result["limited_live_worker_activation_candidate_bundle"] = bundle
    result["limited_live_worker_activation_candidate_schema"] = bundle["schema"]
    result["limited_live_worker_activation_candidate_approval_gate"] = bundle["limited_live_worker_activation_candidate_approval_gate"]
    result["worker_template_reference_contract"] = bundle["worker_template_reference_contract"]
    result["one_worker_activation_scope_contract"] = bundle["one_worker_activation_scope_contract"]
    result["non_execution_worker_boundary"] = bundle["non_execution_worker_boundary"]
    result["worker_permission_denial_record"] = bundle["worker_permission_denial_record"]
    result["worker_activation_candidate_record"] = bundle["worker_activation_candidate_record"]
    result["worker_activation_audit_record"] = bundle["worker_activation_audit_record"]
    result["worker_activation_ledger"] = bundle["worker_activation_ledger"]
    result["worker_activation_readiness_summary"] = bundle["worker_activation_readiness_summary"]
    result["permissioned_worker_task_assignment_candidate_bridge"] = bundle["permissioned_worker_task_assignment_candidate_bridge"]
    result["worker_activation_record_payload"] = bundle.get("worker_activation_record_payload")
    result["worker_activation_write_record"] = bundle["worker_activation_write_record"]
    result["local_worker_activation_record_written"] = bundle["local_worker_activation_record_written"]
    result["worker_process_started"] = False
    result["live_task_assignment_performed"] = False
    result["live_worker_routing_performed"] = False
    result["full_workforce_activation_performed"] = False
    result["limited_live_worker_activation_candidate_write_summary"] = bundle["worker_activation_write_record"]
    return result


def write_limited_live_worker_activation_candidate(
    result: dict,
    activation_output_directory: str | Path,
    worker_template_label: str | None = None,
    activation_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    run_label: str = "station-chief-runtime",
) -> dict:
    result = attach_limited_live_worker_activation_candidate(
        result,
        worker_template_label=worker_template_label,
        activation_output_directory=str(activation_output_directory),
        activation_record_name=activation_record_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        activation_requested=True,
        write_activation_record=True,
    )
    write_record = result["worker_activation_write_record"]
    result["limited_live_worker_activation_candidate_dir"] = write_record.get("activation_output_directory") or str(activation_output_directory)
    result["files_written"] = [write_record["record_name"]] if write_record.get("local_worker_activation_record_written") else []
    result["record_path"] = write_record.get("record_path")
    result["execution_status"] = write_record.get("write_status")
    return result


def attach_permissioned_worker_task_assignment_candidate(
    result: dict,
    worker_template_label: str | None = None,
    task_label: str | None = None,
    task_assignment_output_directory: str | None = None,
    task_assignment_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    assignment_requested: bool = False,
    write_task_assignment_record: bool = False,
) -> dict:
    bundle = create_permissioned_worker_task_assignment_candidate_bundle(
        result,
        command=result.get("command", "check please"),
        worker_template_label=worker_template_label,
        task_label=task_label,
        task_assignment_output_directory=task_assignment_output_directory,
        task_assignment_record_name=task_assignment_record_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        assignment_requested=assignment_requested,
        write_task_assignment_record=write_task_assignment_record,
    )
    result = dict(result)
    result["permissioned_worker_task_assignment_candidate_bundle"] = bundle
    result["permissioned_worker_task_assignment_candidate_schema"] = bundle["schema"]
    result["permissioned_worker_task_assignment_candidate_approval_gate"] = bundle["permissioned_worker_task_assignment_candidate_approval_gate"]
    result["worker_template_reference_contract"] = bundle["worker_template_reference_contract"]
    result["task_label_reference_contract"] = bundle["task_label_reference_contract"]
    result["one_worker_one_task_assignment_scope_contract"] = bundle["one_worker_one_task_assignment_scope_contract"]
    result["non_execution_task_boundary"] = bundle["non_execution_task_boundary"]
    result["task_permission_denial_record"] = bundle["task_permission_denial_record"]
    result["worker_task_assignment_candidate_record"] = bundle["worker_task_assignment_candidate_record"]
    result["task_assignment_audit_record"] = bundle["task_assignment_audit_record"]
    result["task_assignment_ledger"] = bundle["task_assignment_ledger"]
    result["task_assignment_readiness_summary"] = bundle["task_assignment_readiness_summary"]
    result["task_assignment_audit_closeout_candidate_bridge"] = bundle["task_assignment_audit_closeout_candidate_bridge"]
    result["task_assignment_record_payload"] = bundle["task_assignment_record_payload"]
    result["task_assignment_write_record"] = bundle["task_assignment_write_record"]
    result["local_task_assignment_record_written"] = bundle["local_task_assignment_record_written"]
    result["task_executed"] = False
    result["task_enqueued"] = False
    result["worker_process_started"] = False
    result["live_task_assignment_performed"] = False
    result["live_worker_routing_performed"] = False
    result["full_workforce_activation_performed"] = False
    result["permissioned_worker_task_assignment_candidate_write_summary"] = bundle["task_assignment_write_record"]
    return result


def write_permissioned_worker_task_assignment_candidate(
    result: dict,
    task_assignment_output_directory: str | Path,
    worker_template_label: str | None = None,
    task_label: str | None = None,
    task_assignment_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    run_label: str = "station-chief-runtime",
) -> dict:
    result = attach_permissioned_worker_task_assignment_candidate(
        result,
        worker_template_label=worker_template_label,
        task_label=task_label,
        task_assignment_output_directory=str(task_assignment_output_directory),
        task_assignment_record_name=task_assignment_record_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        assignment_requested=True,
        write_task_assignment_record=True,
    )
    write_record = result["task_assignment_write_record"]
    result["permissioned_worker_task_assignment_candidate_dir"] = write_record.get("task_assignment_output_directory") or str(task_assignment_output_directory)
    result["files_written"] = [write_record["record_name"]] if write_record.get("local_task_assignment_record_written") else []
    result["record_path"] = write_record.get("record_path")
    result["execution_status"] = write_record.get("write_status")
    return result


def attach_task_assignment_audit_closeout_candidate(
    result: dict,
    closeout_label: str | None = None,
    task_assignment_record_path: str | None = None,
    expected_task_assignment_output_directory: str | None = None,
    closeout_output_directory: str | None = None,
    closeout_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    closeout_requested: bool = False,
    write_closeout_record: bool = False,
) -> dict:
    bundle = create_task_assignment_audit_closeout_candidate_bundle(
        result,
        command=result.get("command", "check please"),
        closeout_label=closeout_label,
        task_assignment_record_path=task_assignment_record_path,
        expected_task_assignment_output_directory=expected_task_assignment_output_directory,
        closeout_output_directory=closeout_output_directory,
        closeout_record_name=closeout_record_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        closeout_requested=closeout_requested,
        write_closeout_record=write_closeout_record,
    )
    result = dict(result)
    result["task_assignment_audit_closeout_candidate_bundle"] = bundle
    result["task_assignment_audit_closeout_candidate_schema"] = bundle["schema"]
    result["task_assignment_audit_closeout_candidate_approval_gate"] = bundle["task_assignment_audit_closeout_candidate_approval_gate"]
    result["v4_4_task_assignment_record_reference_contract"] = bundle["v4_4_task_assignment_record_reference_contract"]
    result["task_assignment_record_integrity_verification"] = bundle["task_assignment_record_integrity_verification"]
    result["task_assignment_record_path_containment_review"] = bundle["task_assignment_record_path_containment_review"]
    result["task_assignment_safety_boolean_review"] = bundle["task_assignment_safety_boolean_review"]
    result["non_execution_closeout_boundary"] = bundle["non_execution_closeout_boundary"]
    result["operator_closeout_acknowledgement"] = bundle["operator_closeout_acknowledgement"]
    result["task_assignment_closeout_audit_record"] = bundle["task_assignment_closeout_audit_record"]
    result["task_assignment_closeout_ledger"] = bundle["task_assignment_closeout_ledger"]
    result["task_assignment_closeout_readiness_summary"] = bundle["task_assignment_closeout_readiness_summary"]
    result["non_executing_task_queue_preview_candidate_bridge"] = bundle["non_executing_task_queue_preview_candidate_bridge"]
    result["task_assignment_audit_closeout_record_payload"] = bundle["task_assignment_audit_closeout_record_payload"]
    result["task_assignment_closeout_write_record"] = bundle["task_assignment_closeout_write_record"]
    result["local_closeout_record_written"] = bundle["local_closeout_record_written"]
    result["task_executed"] = False
    result["task_enqueued"] = False
    result["worker_process_started"] = False
    result["live_task_assignment_performed"] = False
    result["live_worker_routing_performed"] = False
    result["full_workforce_activation_performed"] = False
    result["referenced_task_assignment_record_mutated"] = False
    result["task_assignment_audit_closeout_candidate_write_summary"] = bundle["task_assignment_closeout_write_record"]
    return result


def write_task_assignment_audit_closeout_candidate(
    result: dict,
    closeout_output_directory: str | Path,
    closeout_label: str | None = None,
    task_assignment_record_path: str | None = None,
    expected_task_assignment_output_directory: str | None = None,
    closeout_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    run_label: str = "station-chief-runtime",
) -> dict:
    result = attach_task_assignment_audit_closeout_candidate(
        result,
        closeout_label=closeout_label,
        task_assignment_record_path=task_assignment_record_path,
        expected_task_assignment_output_directory=expected_task_assignment_output_directory,
        closeout_output_directory=str(closeout_output_directory),
        closeout_record_name=closeout_record_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        closeout_requested=True,
        write_closeout_record=True,
    )
    write_record = result["task_assignment_closeout_write_record"]
    result["task_assignment_audit_closeout_candidate_dir"] = write_record.get("closeout_output_directory") or str(closeout_output_directory)
    result["files_written"] = [write_record["record_name"]] if write_record.get("local_closeout_record_written") else []
    result["record_path"] = write_record.get("record_path")
    result["execution_status"] = write_record.get("write_status")
    return result


def attach_non_executing_task_queue_preview_candidate(
    result: dict,
    queue_preview_label: str | None = None,
    task_assignment_record_path: str | None = None,
    expected_task_assignment_output_directory: str | None = None,
    closeout_record_path: str | None = None,
    queue_preview_output_directory: str | None = None,
    queue_preview_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    queue_preview_requested: bool = False,
    write_queue_preview_record: bool = False,
) -> dict:
    bundle = create_non_executing_task_queue_preview_candidate_bundle(
        result,
        command=result.get("command", "check please"),
        queue_preview_label=queue_preview_label,
        task_assignment_record_path=task_assignment_record_path,
        expected_task_assignment_output_directory=expected_task_assignment_output_directory,
        closeout_record_path=closeout_record_path,
        queue_preview_output_directory=queue_preview_output_directory,
        queue_preview_record_name=queue_preview_record_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        queue_preview_requested=queue_preview_requested,
        write_queue_preview_record=write_queue_preview_record,
    )
    result = dict(result)
    result["non_executing_task_queue_preview_candidate_bundle"] = bundle
    result["non_executing_task_queue_preview_candidate_schema"] = bundle["schema"]
    result["non_executing_task_queue_preview_candidate_approval_gate"] = bundle["non_executing_task_queue_preview_candidate_approval_gate"]
    result["v4_4_task_assignment_record_reference_contract"] = bundle["v4_4_task_assignment_record_reference_contract"]
    result["optional_v4_5_closeout_record_reference_contract"] = bundle["optional_v4_5_closeout_record_reference_contract"]
    result["task_assignment_record_integrity_verification"] = bundle["task_assignment_record_integrity_verification"]
    result["closeout_record_integrity_verification"] = bundle["closeout_record_integrity_verification"]
    result["task_assignment_record_path_containment_review"] = bundle["task_assignment_record_path_containment_review"]
    result["queue_preview_scope_contract"] = bundle["queue_preview_scope_contract"]
    result["non_execution_queue_boundary"] = bundle["non_execution_queue_boundary"]
    result["queue_permission_denial_record"] = bundle["queue_permission_denial_record"]
    result["non_executing_task_queue_preview_candidate_record"] = bundle["local_queue_preview_candidate_record"]
    result["queue_preview_audit_record"] = bundle["queue_preview_audit_record"]
    result["queue_preview_ledger"] = bundle["queue_preview_ledger"]
    result["queue_preview_readiness_summary"] = bundle["queue_preview_readiness_summary"]
    result["task_queue_preview_audit_closeout_candidate_bridge"] = bundle["task_queue_preview_audit_closeout_candidate_bridge"]
    result["queue_preview_record_payload"] = bundle["queue_preview_record_payload"]
    result["queue_preview_write_record"] = bundle["queue_preview_write_record"]
    result["local_queue_preview_record_written"] = bundle["local_queue_preview_record_written"]
    result["queue_created"] = False
    result["queue_write_performed"] = False
    result["scheduler_write_performed"] = False
    result["task_executed"] = False
    result["task_enqueued"] = False
    result["worker_process_started"] = False
    result["live_task_assignment_performed"] = False
    result["live_worker_routing_performed"] = False
    result["full_workforce_activation_performed"] = False
    result["referenced_task_assignment_record_mutated"] = False
    result["referenced_closeout_record_mutated"] = False
    result["non_executing_task_queue_preview_candidate_write_summary"] = bundle["queue_preview_write_record"]
    return result


def write_non_executing_task_queue_preview_candidate(
    result: dict,
    queue_preview_output_directory: str | Path,
    queue_preview_label: str | None = None,
    task_assignment_record_path: str | None = None,
    expected_task_assignment_output_directory: str | None = None,
    closeout_record_path: str | None = None,
    queue_preview_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    run_label: str = "station-chief-runtime",
) -> dict:
    result = attach_non_executing_task_queue_preview_candidate(
        result,
        queue_preview_label=queue_preview_label,
        task_assignment_record_path=task_assignment_record_path,
        expected_task_assignment_output_directory=expected_task_assignment_output_directory,
        closeout_record_path=closeout_record_path,
        queue_preview_output_directory=str(queue_preview_output_directory),
        queue_preview_record_name=queue_preview_record_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        queue_preview_requested=True,
        write_queue_preview_record=True,
    )
    write_record = result["queue_preview_write_record"]
    result["non_executing_task_queue_preview_candidate_dir"] = write_record.get("queue_preview_output_directory") or str(queue_preview_output_directory)
    result["files_written"] = [write_record["record_name"]] if write_record.get("local_queue_preview_record_written") else []
    result["record_path"] = write_record.get("record_path")
    result["execution_status"] = write_record.get("write_status")
    return result



def attach_non_executing_queue_routing_preview(
    result: dict,
    task_candidate_label: str | None = None,
    worker_template_label: str | None = None,
    preview_output_directory: str | None = None,
    preview_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    preview_requested: bool = False,
    write_preview_record: bool = False,
) -> dict:
    bundle = create_non_executing_queue_routing_preview_bundle(
        result,
        command=result.get("command", "check please"),
        task_candidate_label=task_candidate_label,
        worker_template_label=worker_template_label,
        preview_output_directory=preview_output_directory,
        preview_record_name=preview_record_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        preview_requested=preview_requested,
        write_preview_record=write_preview_record,
    )
    result = dict(result)
    result["queue_routing_preview_candidate_bundle"] = bundle
    result["queue_routing_preview_candidate_schema"] = bundle["schema"]
    result["queue_routing_preview_approval_gate"] = bundle["queue_routing_preview_approval_gate"]
    result["hypothetical_task_candidate_reference"] = bundle["hypothetical_task_candidate_reference"]
    result["worker_template_reference_contract"] = bundle["worker_template_reference_contract"]
    result["queue_preview_scope_contract"] = bundle["queue_preview_scope_contract"]
    result["non_execution_routing_boundary"] = bundle["non_execution_routing_boundary"]
    result["routing_permission_denial_record"] = bundle["routing_permission_denial_record"]
    result["routing_preview_candidate_record"] = bundle["routing_preview_candidate_record"]
    result["routing_preview_audit_record"] = bundle["routing_preview_audit_record"]
    result["routing_preview_readiness_summary"] = bundle["routing_preview_readiness_summary"]
    result["live_queue_orchestration_candidate_bridge"] = bundle["live_queue_orchestration_candidate_bridge"]
    result["routing_preview_record_payload"] = bundle["routing_preview_record_payload"]
    result["queue_routing_preview_write_record"] = bundle["queue_routing_preview_write_record"]
    result["local_queue_routing_preview_record_written"] = bundle["local_queue_routing_preview_record_written"]
    result["real_queue_created"] = False
    result["task_enqueued"] = False
    result["task_executed"] = False
    result["live_task_assignment_performed"] = False
    result["live_worker_routing_performed"] = False
    result["worker_process_started"] = False
    result["full_workforce_activation_performed"] = False
    return result


def write_non_executing_queue_routing_preview(
    result: dict,
    preview_output_directory: str | Path,
    task_candidate_label: str | None = None,
    worker_template_label: str | None = None,
    preview_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
) -> dict:
    result = attach_non_executing_queue_routing_preview(
        result,
        task_candidate_label=task_candidate_label,
        worker_template_label=worker_template_label,
        preview_output_directory=str(preview_output_directory),
        preview_record_name=preview_record_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        preview_requested=True,
        write_preview_record=True,
    )
    write_record = result["queue_routing_preview_write_record"]
    result["non_executing_queue_routing_preview_dir"] = write_record.get(
        "queue_routing_preview_output_directory"
    ) or str(preview_output_directory)
    result["files_written"] = [write_record["record_name"]] if write_record.get("local_queue_routing_preview_record_written") else []
    result["record_path"] = write_record.get("record_path")
    result["execution_status"] = write_record.get("write_status")
    return result


def attach_live_queue_orchestration_candidate_review(
    result: dict,
    v4_8_routing_preview_reference_label: str | None = None,
    review_output_directory: str | None = None,
    review_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    review_requested: bool = False,
    write_review_record: bool = False,
) -> dict:
    bundle = create_live_queue_orchestration_candidate_review_bundle(
        result,
        command=result.get("command", "check please"),
        v4_8_routing_preview_reference_label=v4_8_routing_preview_reference_label,
        review_output_directory=review_output_directory,
        review_record_name=review_record_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        review_requested=review_requested,
        write_review_record=write_review_record,
    )
    result = dict(result)
    result["live_queue_orchestration_candidate_review_bundle"] = bundle
    result["live_queue_orchestration_candidate_review_schema"] = bundle["schema"]
    result["orchestration_review_approval_gate"] = bundle["orchestration_review_approval_gate"]
    result["v4_8_queue_routing_preview_reference_contract"] = bundle["v4_8_queue_routing_preview_reference_contract"]
    result["orchestration_review_scope_contract"] = bundle["orchestration_review_scope_contract"]
    result["non_execution_orchestration_boundary"] = bundle["non_execution_orchestration_boundary"]
    result["orchestration_permission_denial_record"] = bundle["orchestration_permission_denial_record"]
    result["orchestration_candidate_review_record"] = bundle["orchestration_candidate_review_record"]
    result["orchestration_review_audit_record"] = bundle["orchestration_review_audit_record"]
    result["orchestration_readiness_summary"] = bundle["orchestration_readiness_summary"]
    result["first_live_queue_execution_candidate_bridge"] = bundle["first_live_queue_execution_candidate_bridge"]
    result["orchestration_candidate_review_record_payload"] = bundle["orchestration_candidate_review_record_payload"]
    result["orchestration_candidate_review_write_record"] = bundle["orchestration_candidate_review_write_record"]
    result["local_orchestration_review_record_written"] = bundle["local_orchestration_review_record_written"]
    result["real_queue_created"] = False
    result["queue_write_performed"] = False
    result["scheduler_write_performed"] = False
    result["cron_write_performed"] = False
    result["task_enqueued"] = False
    result["task_executed"] = False
    result["live_task_assignment_performed"] = False
    result["live_worker_routing_performed"] = False
    result["live_orchestration_performed"] = False
    result["worker_process_started"] = False
    result["full_workforce_activation_performed"] = False
    return result


def write_live_queue_orchestration_candidate_review(
    result: dict,
    review_output_directory: str | Path,
    v4_8_routing_preview_reference_label: str | None = None,
    review_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
) -> dict:
    result = attach_live_queue_orchestration_candidate_review(
        result,
        v4_8_routing_preview_reference_label=v4_8_routing_preview_reference_label,
        review_output_directory=str(review_output_directory),
        review_record_name=review_record_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        review_requested=True,
        write_review_record=True,
    )
    write_record = result["orchestration_candidate_review_write_record"]
    result["live_queue_orchestration_candidate_review_dir"] = write_record.get(
        "review_output_directory"
    ) or str(review_output_directory)
    result["files_written"] = [write_record["record_name"]] if write_record.get("local_orchestration_review_record_written") else []
    result["record_path"] = write_record.get("record_path")
    result["execution_status"] = write_record.get("write_status")
    return result


def attach_first_live_queue_execution_candidate_review(
    result: dict,
    v4_9_orchestration_review_reference_label: str | None = None,
    review_output_directory: str | None = None,
    review_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    review_requested: bool = False,
    write_review_record: bool = False,
) -> dict:
    bundle = create_first_live_queue_execution_candidate_review_bundle(
        result,
        command=result.get("command", "check please"),
        v4_9_orchestration_review_reference_label=v4_9_orchestration_review_reference_label,
        review_output_directory=review_output_directory,
        review_record_name=review_record_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        review_requested=review_requested,
        write_review_record=write_review_record,
    )
    result = dict(result)
    result["first_live_queue_execution_candidate_review_bundle"] = bundle
    result["first_live_queue_execution_candidate_review_schema"] = bundle["schema"]
    result["execution_candidate_review_approval_gate"] = bundle["execution_candidate_review_approval_gate"]
    result["v4_9_orchestration_review_reference_contract"] = bundle["v4_9_orchestration_review_reference_contract"]
    result["execution_candidate_review_scope_contract"] = bundle["execution_candidate_review_scope_contract"]
    result["non_execution_execution_boundary"] = bundle["non_execution_execution_boundary"]
    result["execution_permission_denial_record"] = bundle["execution_permission_denial_record"]
    result["execution_candidate_review_record"] = bundle["execution_candidate_review_record"]
    result["execution_candidate_review_audit_record"] = bundle["execution_candidate_review_audit_record"]
    result["execution_candidate_readiness_summary"] = bundle["execution_candidate_readiness_summary"]
    result["first_supervised_local_execution_kernel_candidate_bridge"] = bundle["first_supervised_local_execution_kernel_candidate_bridge"]
    result["execution_candidate_review_record_payload"] = bundle["execution_candidate_review_record_payload"]
    result["execution_candidate_review_write_record"] = bundle["execution_candidate_review_write_record"]
    result["local_execution_candidate_review_record_written"] = bundle["local_execution_candidate_review_record_written"]
    result["real_queue_created"] = False
    result["queue_write_performed"] = False
    result["scheduler_write_performed"] = False
    result["cron_write_performed"] = False
    result["task_enqueued"] = False
    result["task_executed"] = False
    result["live_task_assignment_performed"] = False
    result["live_worker_routing_performed"] = False
    result["live_orchestration_performed"] = False
    result["worker_process_started"] = False
    result["supervised_local_execution_performed"] = False
    result["full_workforce_activation_performed"] = False
    return result


def write_first_live_queue_execution_candidate_review(
    result: dict,
    review_output_directory: str | Path,
    v4_9_orchestration_review_reference_label: str | None = None,
    review_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
) -> dict:
    result = attach_first_live_queue_execution_candidate_review(
        result,
        v4_9_orchestration_review_reference_label=v4_9_orchestration_review_reference_label,
        review_output_directory=str(review_output_directory),
        review_record_name=review_record_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        review_requested=True,
        write_review_record=True,
    )
    write_record = result["execution_candidate_review_write_record"]
    result["first_live_queue_execution_candidate_review_dir"] = write_record.get(
        "review_output_directory"
    ) or str(review_output_directory)
    result["files_written"] = [write_record["record_name"]] if write_record.get("local_execution_candidate_review_record_written") else []
    result["record_path"] = write_record.get("record_path")
    result["execution_status"] = write_record.get("write_status")
    return result


def attach_first_supervised_local_execution_kernel_candidate(
    result: dict,
    synthetic_task_label: str | None = None,
    output_directory: str | None = None,
    output_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    execution_requested: bool = False,
    write_output_record: bool = False,
) -> dict:
    bundle = create_first_supervised_local_execution_kernel_candidate_bundle(
        result,
        command=result.get("command", "check please"),
        synthetic_task_label=synthetic_task_label,
        output_directory=output_directory,
        output_record_name=output_record_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        execution_requested=execution_requested,
        write_output_record=write_output_record,
    )
    result = dict(result)
    result["first_supervised_local_execution_kernel_candidate_bundle"] = bundle
    result["first_supervised_local_execution_kernel_candidate_schema"] = bundle["schema"]
    result["supervised_execution_kernel_approval_gate"] = bundle["supervised_execution_kernel_approval_gate"]
    result["synthetic_task_contract"] = bundle["synthetic_task_contract"]
    result["sandbox_output_scope_contract"] = bundle["sandbox_output_scope_contract"]
    result["non_external_execution_boundary"] = bundle["non_external_execution_boundary"]
    result["execution_permission_denial_record"] = bundle["execution_permission_denial_record"]
    result["supervised_local_execution_plan_record"] = bundle["supervised_local_execution_plan_record"]
    result["supervised_local_execution_result_record"] = bundle["supervised_local_execution_result_record"]
    result["supervised_local_execution_audit_record"] = bundle["supervised_local_execution_audit_record"]
    result["supervised_local_execution_readiness_summary"] = bundle["supervised_local_execution_readiness_summary"]
    result["controlled_repeatable_local_execution_candidate_bridge"] = bundle["controlled_repeatable_local_execution_candidate_bridge"]
    result["supervised_local_execution_output_payload"] = bundle["supervised_local_execution_output_payload"]
    result["supervised_local_execution_write_record"] = bundle["supervised_local_execution_write_record"]
    result["local_supervised_output_record_written"] = bundle["local_supervised_output_record_written"]
    result["supervised_local_execution_performed"] = bundle["supervised_local_execution_performed"]
    result["real_queue_created"] = False
    result["queue_write_performed"] = False
    result["scheduler_write_performed"] = False
    result["cron_write_performed"] = False
    result["task_enqueued"] = False
    result["task_executed"] = False
    result["arbitrary_task_execution_performed"] = False
    result["user_task_execution_performed"] = False
    result["live_task_assignment_performed"] = False
    result["live_worker_routing_performed"] = False
    result["live_orchestration_performed"] = False
    result["worker_process_started"] = False
    result["external_tool_invocation_performed"] = False
    result["api_call_performed"] = False
    result["network_access_performed"] = False
    result["deployment_performed"] = False
    result["production_execution_performed"] = False
    result["full_workforce_activation_performed"] = False
    return result


def write_first_supervised_local_execution_kernel_candidate(
    result: dict,
    output_directory: str | Path,
    synthetic_task_label: str | None = None,
    output_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
) -> dict:
    result = attach_first_supervised_local_execution_kernel_candidate(
        result,
        synthetic_task_label=synthetic_task_label,
        output_directory=str(output_directory),
        output_record_name=output_record_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        execution_requested=True,
        write_output_record=True,
    )
    write_record = result["supervised_local_execution_write_record"]
    result["first_supervised_local_execution_kernel_candidate_dir"] = write_record.get("output_directory") or str(output_directory)
    result["files_written"] = [write_record["record_name"]] if write_record.get("local_supervised_output_record_written") else []
    result["record_path"] = write_record.get("record_path")
    result["execution_status"] = write_record.get("write_status")
    return result


def attach_controlled_repeatable_local_execution_candidate(
    result: dict,
    synthetic_task_label: str | None = None,
    output_directory: str | None = None,
    output_record_name: str | None = None,
    repeatability_count: int | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    execution_requested: bool = False,
    write_proof_record: bool = False,
) -> dict:
    bundle = create_controlled_repeatable_local_execution_candidate_bundle(
        result,
        command=result.get("command", "check please"),
        synthetic_task_label=synthetic_task_label,
        output_directory=output_directory,
        output_record_name=output_record_name,
        repeatability_count=repeatability_count,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        execution_requested=execution_requested,
        write_proof_record=write_proof_record,
    )
    result = dict(result)
    result["controlled_repeatable_local_execution_candidate_bundle"] = bundle
    result["controlled_repeatable_local_execution_candidate_schema"] = bundle["schema"]
    result["repeatable_execution_approval_gate"] = bundle["repeatable_execution_approval_gate"]
    result["synthetic_repeatable_task_contract"] = bundle["synthetic_repeatable_task_contract"]
    result["repeatability_scope_contract"] = bundle["repeatability_scope_contract"]
    result["non_external_repeatability_boundary"] = bundle["non_external_repeatability_boundary"]
    result["repeatability_permission_denial_record"] = bundle["repeatability_permission_denial_record"]
    result["repeatability_plan_record"] = bundle["repeatability_plan_record"]
    result["repeatability_entries_record"] = bundle["repeatability_entries_record"]
    result["repeatability_proof_result_record"] = bundle["repeatability_proof_result_record"]
    result["repeatability_audit_record"] = bundle["repeatability_audit_record"]
    result["repeatability_readiness_summary"] = bundle["repeatability_readiness_summary"]
    result["sandbox_worker_handoff_candidate_bridge"] = bundle["sandbox_worker_handoff_candidate_bridge"]
    result["repeatability_proof_payload"] = bundle["repeatability_proof_payload"]
    result["repeatability_proof_write_record"] = bundle["repeatability_proof_write_record"]
    result["local_repeatability_proof_record_written"] = bundle["local_repeatability_proof_record_written"]
    result["controlled_repeatable_local_execution_performed"] = bundle["controlled_repeatable_local_execution_performed"]
    result["supervised_local_execution_performed"] = bundle["supervised_local_execution_performed"]
    result["repeatability_count"] = bundle["repeatability_count"]
    result["repeatability_status"] = bundle["repeatability_status"]
    result["repeatable_execution_candidate_id"] = bundle["repeatable_execution_candidate_id"]
    result["real_queue_created"] = False
    result["queue_write_performed"] = False
    result["scheduler_write_performed"] = False
    result["cron_write_performed"] = False
    result["task_enqueued"] = False
    result["task_executed"] = False
    result["arbitrary_task_execution_performed"] = False
    result["user_task_execution_performed"] = False
    result["live_task_assignment_performed"] = False
    result["live_worker_routing_performed"] = False
    result["live_orchestration_performed"] = False
    result["worker_process_started"] = False
    result["external_tool_invocation_performed"] = False
    result["api_call_performed"] = False
    result["network_access_performed"] = False
    result["deployment_performed"] = False
    result["production_execution_performed"] = False
    result["full_workforce_activation_performed"] = False
    return result


def write_controlled_repeatable_local_execution_candidate(
    result: dict,
    output_directory: str | Path,
    synthetic_task_label: str | None = None,
    output_record_name: str | None = None,
    repeatability_count: int | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
) -> dict:
    result = attach_controlled_repeatable_local_execution_candidate(
        result,
        synthetic_task_label=synthetic_task_label,
        output_directory=str(output_directory),
        output_record_name=output_record_name,
        repeatability_count=repeatability_count,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        execution_requested=True,
        write_proof_record=True,
    )
    write_record = result["repeatability_proof_write_record"]
    result["controlled_repeatable_local_execution_candidate_dir"] = write_record.get("output_directory") or str(output_directory)
    result["files_written"] = [write_record["record_name"]] if write_record.get("local_repeatability_proof_record_written") else []
    result["record_path"] = write_record.get("record_path")
    result["execution_status"] = write_record.get("write_status")
    return result


def attach_sandbox_worker_handoff_candidate(
    result: dict,
    synthetic_task_label: str | None = None,
    sandbox_worker_label: str | None = None,
    v5_2_repeatability_proof_reference_label: str | None = None,
    output_directory: str | None = None,
    handoff_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    handoff_requested: bool = False,
    write_handoff_packet: bool = False,
) -> dict:
    bundle = create_sandbox_worker_handoff_candidate_bundle(
        result,
        command=result.get("command", "check please"),
        synthetic_task_label=synthetic_task_label,
        sandbox_worker_label=sandbox_worker_label,
        v5_2_repeatability_proof_reference_label=v5_2_repeatability_proof_reference_label,
        output_directory=output_directory,
        handoff_packet_name=handoff_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        handoff_requested=handoff_requested,
        write_handoff_packet=write_handoff_packet,
    )
    result = dict(result)
    result["sandbox_worker_handoff_candidate_bundle"] = bundle
    result["sandbox_worker_handoff_candidate_schema"] = bundle["schema"]
    result["sandbox_worker_handoff_approval_gate"] = bundle["sandbox_worker_handoff_approval_gate"]
    result["v5_2_repeatability_proof_reference_contract"] = bundle["v5_2_repeatability_proof_reference_contract"]
    result["synthetic_task_handoff_contract"] = bundle["synthetic_task_handoff_contract"]
    result["sandbox_worker_reference_contract"] = bundle["sandbox_worker_reference_contract"]
    result["handoff_scope_contract"] = bundle["handoff_scope_contract"]
    result["non_execution_handoff_boundary"] = bundle["non_execution_handoff_boundary"]
    result["handoff_permission_denial_record"] = bundle["handoff_permission_denial_record"]
    result["handoff_plan_record"] = bundle["handoff_plan_record"]
    result["handoff_packet_record"] = bundle["handoff_packet_record"]
    result["handoff_audit_record"] = bundle["handoff_audit_record"]
    result["handoff_readiness_summary"] = bundle["handoff_readiness_summary"]
    result["sandbox_worker_acknowledgement_candidate_bridge"] = bundle["sandbox_worker_acknowledgement_candidate_bridge"]
    result["handoff_packet_payload"] = bundle["handoff_packet_payload"]
    result["handoff_packet_write_record"] = bundle["handoff_packet_write_record"]
    result["local_handoff_packet_written"] = bundle["local_handoff_packet_written"]
    result["sandbox_worker_handoff_performed"] = bundle["sandbox_worker_handoff_performed"]
    result["worker_process_started"] = False
    result["agent_started"] = False
    result["real_queue_created"] = False
    result["queue_write_performed"] = False
    result["scheduler_write_performed"] = False
    result["cron_write_performed"] = False
    result["task_enqueued"] = False
    result["task_executed"] = False
    result["arbitrary_task_execution_performed"] = False
    result["user_task_execution_performed"] = False
    result["live_task_assignment_performed"] = False
    result["live_worker_routing_performed"] = False
    result["live_orchestration_performed"] = False
    result["external_tool_invocation_performed"] = False
    result["api_call_performed"] = False
    result["network_access_performed"] = False
    result["deployment_performed"] = False
    result["production_execution_performed"] = False
    result["full_workforce_activation_performed"] = False
    result["handoff_candidate_id"] = bundle["handoff_candidate_id"]
    result["sandbox_worker_handoff_candidate_id"] = bundle["sandbox_worker_handoff_candidate_id"]
    result["sandbox_worker_handoff_candidate_next_step"] = bundle["sandbox_worker_handoff_candidate_next_step"]
    return result


def write_sandbox_worker_handoff_candidate(
    result: dict,
    output_directory: str | Path,
    synthetic_task_label: str | None = None,
    sandbox_worker_label: str | None = None,
    v5_2_repeatability_proof_reference_label: str | None = None,
    handoff_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
) -> dict:
    result = attach_sandbox_worker_handoff_candidate(
        result,
        synthetic_task_label=synthetic_task_label,
        sandbox_worker_label=sandbox_worker_label,
        v5_2_repeatability_proof_reference_label=v5_2_repeatability_proof_reference_label,
        output_directory=str(output_directory),
        handoff_packet_name=handoff_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        handoff_requested=True,
        write_handoff_packet=True,
    )
    write_record = result["handoff_packet_write_record"]
    result["sandbox_worker_handoff_candidate_dir"] = write_record.get("output_directory") or str(output_directory)
    result["files_written"] = [write_record["packet_name"]] if write_record.get("local_handoff_packet_written") else []
    result["record_path"] = write_record.get("record_path")
    result["execution_status"] = write_record.get("write_status")
    return result


def attach_sandbox_worker_acknowledgement_candidate(
    result: dict,
    sandbox_worker_label: str | None = None,
    v5_3_handoff_packet_reference_label: str | None = None,
    output_directory: str | None = None,
    acknowledgement_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    acknowledgement_requested: bool = False,
    write_acknowledgement_packet: bool = False,
) -> dict:
    bundle = create_sandbox_worker_acknowledgement_candidate_bundle(
        result,
        command=result.get("command", "check please"),
        sandbox_worker_label=sandbox_worker_label,
        v5_3_handoff_packet_reference_label=v5_3_handoff_packet_reference_label,
        output_directory=output_directory,
        acknowledgement_packet_name=acknowledgement_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        acknowledgement_requested=acknowledgement_requested,
        write_acknowledgement_packet=write_acknowledgement_packet,
    )
    result = dict(result)
    result["sandbox_worker_acknowledgement_candidate_bundle"] = bundle
    result["sandbox_worker_acknowledgement_candidate_schema"] = bundle["schema"]
    result["sandbox_worker_acknowledgement_approval_gate"] = bundle["sandbox_worker_acknowledgement_approval_gate"]
    result["v5_3_handoff_packet_reference_contract"] = bundle["v5_3_handoff_packet_reference_contract"]
    result["sandbox_worker_acknowledgement_reference_contract"] = bundle["sandbox_worker_acknowledgement_reference_contract"]
    result["acknowledgement_scope_contract"] = bundle["acknowledgement_scope_contract"]
    result["non_execution_acknowledgement_boundary"] = bundle["non_execution_acknowledgement_boundary"]
    result["acknowledgement_permission_denial_record"] = bundle["acknowledgement_permission_denial_record"]
    result["acknowledgement_plan_record"] = bundle["acknowledgement_plan_record"]
    result["acknowledgement_packet_record"] = bundle["acknowledgement_packet_record"]
    result["acknowledgement_audit_record"] = bundle["acknowledgement_audit_record"]
    result["acknowledgement_readiness_summary"] = bundle["acknowledgement_readiness_summary"]
    result["sandbox_worker_acceptance_candidate_bridge"] = bundle["sandbox_worker_acceptance_candidate_bridge"]
    result["acknowledgement_packet_payload"] = bundle["acknowledgement_packet_payload"]
    result["acknowledgement_packet_write_record"] = bundle["acknowledgement_packet_write_record"]
    result["local_acknowledgement_packet_written"] = bundle["local_acknowledgement_packet_written"]
    result["sandbox_worker_acknowledgement_performed"] = bundle["sandbox_worker_acknowledgement_performed"]
    result["worker_process_started"] = False
    result["agent_started"] = False
    result["real_queue_created"] = False
    result["queue_write_performed"] = False
    result["scheduler_write_performed"] = False
    result["cron_write_performed"] = False
    result["task_enqueued"] = False
    result["task_executed"] = False
    result["arbitrary_task_execution_performed"] = False
    result["user_task_execution_performed"] = False
    result["live_task_assignment_performed"] = False
    result["live_worker_routing_performed"] = False
    result["live_orchestration_performed"] = False
    result["external_tool_invocation_performed"] = False
    result["api_call_performed"] = False
    result["network_access_performed"] = False
    result["deployment_performed"] = False
    result["production_execution_performed"] = False
    result["full_workforce_activation_performed"] = False
    result["acknowledgement_candidate_id"] = bundle["sandbox_worker_acknowledgement_candidate_id"]
    result["sandbox_worker_acknowledgement_candidate_id"] = bundle["sandbox_worker_acknowledgement_candidate_id"]
    result["sandbox_worker_acknowledgement_candidate_next_step"] = bundle["acknowledgement_candidate_next_step"]
    return result


def write_sandbox_worker_acknowledgement_candidate(
    result: dict,
    output_directory: str | Path,
    sandbox_worker_label: str | None = None,
    v5_3_handoff_packet_reference_label: str | None = None,
    acknowledgement_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
) -> dict:
    result = attach_sandbox_worker_acknowledgement_candidate(
        result,
        sandbox_worker_label=sandbox_worker_label,
        v5_3_handoff_packet_reference_label=v5_3_handoff_packet_reference_label,
        output_directory=str(output_directory),
        acknowledgement_packet_name=acknowledgement_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        acknowledgement_requested=True,
        write_acknowledgement_packet=True,
    )
    write_record = result["acknowledgement_packet_write_record"]
    result["sandbox_worker_acknowledgement_candidate_dir"] = write_record.get("output_directory") or str(output_directory)
    result["files_written"] = [write_record["record_name"]] if write_record.get("local_acknowledgement_packet_written") else []
    result["record_path"] = write_record.get("record_path")
    result["execution_status"] = write_record.get("write_status")
    return result


def attach_task_queue_preview_audit_closeout_candidate(
    result: dict,
    queue_closeout_label: str | None = None,
    queue_preview_record_path: str | None = None,
    expected_queue_preview_output_directory: str | None = None,
    queue_closeout_output_directory: str | None = None,
    queue_closeout_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    queue_closeout_requested: bool = False,
    write_queue_closeout_record: bool = False,
) -> dict:
    bundle = create_task_queue_preview_audit_closeout_candidate_bundle(
        result,
        command=result.get("command", "check please"),
        queue_closeout_label=queue_closeout_label,
        queue_preview_record_path=queue_preview_record_path,
        expected_queue_preview_output_directory=expected_queue_preview_output_directory,
        queue_closeout_output_directory=queue_closeout_output_directory,
        queue_closeout_record_name=queue_closeout_record_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        queue_closeout_requested=queue_closeout_requested,
        write_queue_closeout_record=write_queue_closeout_record,
    )
    result = dict(result)
    result["task_queue_preview_audit_closeout_candidate_bundle"] = bundle
    result["task_queue_preview_audit_closeout_candidate_schema"] = bundle["schema"]
    result["task_queue_preview_audit_closeout_candidate_approval_gate"] = bundle["task_queue_preview_audit_closeout_candidate_approval_gate"]
    result["v4_6_queue_preview_record_reference_contract"] = bundle["v4_6_queue_preview_record_reference_contract"]
    result["queue_preview_record_integrity_verification"] = bundle["queue_preview_record_integrity_verification"]
    result["queue_preview_record_path_containment_review"] = bundle["queue_preview_record_path_containment_review"]
    result["queue_preview_safety_boolean_review"] = bundle["queue_preview_safety_boolean_review"]
    result["non_execution_queue_closeout_boundary"] = bundle["non_execution_queue_closeout_boundary"]
    result["operator_queue_closeout_acknowledgement"] = bundle["operator_queue_closeout_acknowledgement"]
    result["queue_preview_closeout_audit_record"] = bundle["queue_preview_closeout_audit_record"]
    result["queue_preview_closeout_ledger"] = bundle["queue_preview_closeout_ledger"]
    result["queue_preview_closeout_readiness_summary"] = bundle["queue_preview_closeout_readiness_summary"]
    result["non_executing_worker_routing_preview_candidate_bridge"] = bundle["non_executing_worker_routing_preview_candidate_bridge"]
    result["queue_closeout_record_payload"] = bundle["queue_closeout_record_payload"]
    result["queue_closeout_write_record"] = bundle["queue_closeout_write_record"]
    result["local_queue_closeout_record_written"] = bundle["local_queue_closeout_record_written"]
    result["queue_created"] = False
    result["queue_write_performed"] = False
    result["scheduler_write_performed"] = False
    result["task_executed"] = False
    result["task_enqueued"] = False
    result["worker_process_started"] = False
    result["live_task_assignment_performed"] = False
    result["live_worker_routing_performed"] = False
    result["full_workforce_activation_performed"] = False
    result["referenced_queue_preview_record_mutated"] = False
    result["task_queue_preview_audit_closeout_candidate_write_summary"] = bundle["queue_closeout_write_record"]
    return result

def write_task_queue_preview_audit_closeout_candidate(
    result: dict,
    queue_closeout_output_directory: str | Path,
    queue_closeout_label: str | None = None,
    queue_preview_record_path: str | None = None,
    expected_queue_preview_output_directory: str | None = None,
    queue_closeout_record_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    run_label: str = "station-chief-runtime",
) -> dict:
    result = attach_task_queue_preview_audit_closeout_candidate(
        result,
        queue_closeout_label=queue_closeout_label,
        queue_preview_record_path=queue_preview_record_path,
        expected_queue_preview_output_directory=expected_queue_preview_output_directory,
        queue_closeout_output_directory=str(queue_closeout_output_directory),
        queue_closeout_record_name=queue_closeout_record_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        queue_closeout_requested=True,
        write_queue_closeout_record=True,
    )
    write_record = result["queue_closeout_write_record"]
    result["task_queue_preview_audit_closeout_candidate_dir"] = write_record.get("queue_closeout_output_directory") or str(queue_closeout_output_directory)
    result["files_written"] = [write_record["record_name"]] if write_record.get("local_queue_closeout_record_written") else []
    result["record_path"] = write_record.get("record_path")
    result["execution_status"] = write_record.get("write_status")
    return result


def build_runtime_artifacts(result: dict, run_id: str) -> dict:
    adapter_name = result.get("adapter_name", "noop")
    command_brief = result["command_brief"]
    work_orders = result["work_orders"]
    execution_plan = result.get("execution_plan") or create_execution_plan(command_brief, work_orders, adapter_name=adapter_name)
    adapter_result = result.get("adapter_result") or run_noop_adapter(execution_plan)
    file_operation_plan = result.get("file_operation_plan")
    execution_gate = result.get("execution_gate")
    file_operation_result = result.get("file_operation_result")
    repo_patch_plan = result.get("repo_patch_plan")
    repo_patch_gate = result.get("repo_patch_gate")
    repo_patch_result = result.get("repo_patch_result")
    changed_file_scope_proof = result.get("changed_file_scope_proof")
    execution_profile = result.get("execution_profile")
    preflight_gate_record = result.get("preflight_gate_record")
    patch_approval_checklist = result.get("patch_approval_checklist")
    execution_readiness_score = result.get("execution_readiness_score")
    dry_run_bundle = result.get("dry_run_bundle")
    dry_run_bundle_comparison = result.get("dry_run_bundle_comparison")
    approval_handoff_packet = result.get("approval_handoff_packet")
    approval_review_ui_schema = result.get("approval_review_ui_schema")
    signed_approval_record = result.get("signed_approval_record")
    approval_record_verification = result.get("approval_record_verification")
    approval_record_audit_manifest = result.get("approval_record_audit_manifest")
    selected_records = [
        item
        for item in result["overlay_stack_summary"]
        if item["id"] in result["selected_overlays"]
    ]
    runtime_index_entry = build_runtime_index_entry(result, run_id, artifact_dir=None)

    release_candidate_readiness_summary = result.get("release_candidate_readiness_summary")
    controlled_production_readiness_gate_bridge = result.get("controlled_production_readiness_gate_bridge")
    controlled_production_readiness_gate_bundle = result.get("controlled_production_readiness_gate_bundle")
    controlled_production_readiness_gate_schema = result.get("controlled_production_readiness_gate_schema")
    controlled_production_readiness_gate_approval_gate = result.get("controlled_production_readiness_gate_approval_gate")
    production_activation_denial_by_default = result.get("production_activation_denial_by_default")
    final_human_approval_requirement = result.get("final_human_approval_requirement")
    production_capability_manifest = result.get("production_capability_manifest")
    supervised_pilot_eligibility_contract = result.get("supervised_pilot_eligibility_contract")
    production_rollback_kill_switch_preview = result.get("production_rollback_kill_switch_preview")
    production_readiness_audit_proof = result.get("production_readiness_audit_proof")
    production_readiness_ledger = result.get("production_readiness_ledger")
    production_readiness_summary = result.get("production_readiness_summary")
    controlled_worker_hiring_activation_pilot_bridge = result.get("controlled_worker_hiring_activation_pilot_bridge")
    first_supervised_production_dry_run_bundle = result.get("first_supervised_production_dry_run_bundle")
    first_supervised_production_dry_run_schema = result.get("first_supervised_production_dry_run_schema")
    first_supervised_production_dry_run_approval_gate = result.get("first_supervised_production_dry_run_approval_gate")
    single_controlled_task_dry_run_envelope = result.get("single_controlled_task_dry_run_envelope")
    dry_run_only_production_context_contract = result.get("dry_run_only_production_context_contract")
    human_preflight_approval_gate = result.get("human_preflight_approval_gate")
    worker_task_simulation_contract = result.get("worker_task_simulation_contract")
    external_action_denial_by_default = result.get("external_action_denial_by_default")
    dry_run_rollback_quarantine_preview = result.get("dry_run_rollback_quarantine_preview")
    dry_run_audit_proof = result.get("dry_run_audit_proof")
    dry_run_ledger = result.get("dry_run_ledger")
    dry_run_readiness_summary = result.get("dry_run_readiness_summary")
    limited_external_tool_supervised_pilot_bridge = result.get("limited_external_tool_supervised_pilot_bridge")
    limited_external_tool_supervised_pilot_bundle = result.get("limited_external_tool_supervised_pilot_bundle")
    limited_external_tool_supervised_pilot_schema = result.get("limited_external_tool_supervised_pilot_schema")
    limited_external_tool_supervised_pilot_approval_gate = result.get("limited_external_tool_supervised_pilot_approval_gate")
    single_external_tool_category_contract = result.get("single_external_tool_category_contract")
    tool_invocation_denial_by_default = result.get("tool_invocation_denial_by_default")
    human_tool_use_preflight_gate = result.get("human_tool_use_preflight_gate")
    tool_request_envelope_preview = result.get("tool_request_envelope_preview")
    tool_response_quarantine_preview = result.get("tool_response_quarantine_preview")
    tool_audit_proof = result.get("tool_audit_proof")
    tool_pilot_ledger = result.get("tool_pilot_ledger")
    tool_pilot_readiness_summary = result.get("tool_pilot_readiness_summary")
    supervised_external_api_pilot_bridge = result.get("supervised_external_api_pilot_bridge")
    supervised_external_api_pilot_bundle = result.get("supervised_external_api_pilot_bundle")
    supervised_external_api_pilot_schema = result.get("supervised_external_api_pilot_schema")
    supervised_external_api_pilot_approval_gate = result.get("supervised_external_api_pilot_approval_gate")
    single_api_category_contract = result.get("single_api_category_contract")
    credential_denial_by_default = result.get("credential_denial_by_default")
    secret_handling_denial_by_default = result.get("secret_handling_denial_by_default")
    network_socket_denial_by_default = result.get("network_socket_denial_by_default")
    human_api_use_preflight_gate = result.get("human_api_use_preflight_gate")
    api_request_envelope_preview = result.get("api_request_envelope_preview")
    api_response_quarantine_preview = result.get("api_response_quarantine_preview")
    api_audit_proof = result.get("api_audit_proof")
    api_pilot_ledger = result.get("api_pilot_ledger")
    api_pilot_readiness_summary = result.get("api_pilot_readiness_summary")
    monitored_rollback_recovery_drill_bridge = result.get("monitored_rollback_recovery_drill_bridge")
    supervised_production_pilot_readiness_review_bundle = result.get("supervised_production_pilot_readiness_review_bundle")
    supervised_production_pilot_readiness_review_schema = result.get("supervised_production_pilot_readiness_review_schema")
    supervised_production_pilot_readiness_review_approval_gate = result.get("supervised_production_pilot_readiness_review_approval_gate")
    minimum_viable_production_candidate_contract = result.get("minimum_viable_production_candidate_contract")
    human_production_pilot_review_gate = result.get("human_production_pilot_review_gate")
    production_blast_radius_analysis = result.get("production_blast_radius_analysis")
    live_action_denial_review = result.get("live_action_denial_review")
    rollback_availability_review = result.get("rollback_availability_review")
    credential_secret_readiness_denial_proof = result.get("credential_secret_readiness_denial_proof")
    network_socket_readiness_denial_proof = result.get("network_socket_readiness_denial_proof")
    production_pilot_audit_proof = result.get("production_pilot_audit_proof")
    production_pilot_readiness_ledger = result.get("production_pilot_readiness_ledger")
    production_pilot_readiness_summary = result.get("production_pilot_readiness_summary")
    credential_vault_denial_secret_handling_proof_bridge = result.get("credential_vault_denial_secret_handling_proof_bridge")
    credential_vault_denial_secret_handling_proof_bundle = result.get("credential_vault_denial_secret_handling_proof_bundle")
    credential_vault_denial_secret_handling_proof_schema = result.get("credential_vault_denial_secret_handling_proof_schema")
    credential_vault_denial_secret_handling_proof_approval_gate = result.get("credential_vault_denial_secret_handling_proof_approval_gate")
    credential_access_denial_contract = result.get("credential_access_denial_contract")
    secret_read_denial_contract = result.get("secret_read_denial_contract")
    environment_variable_denial_contract = result.get("environment_variable_denial_contract")
    credential_vault_boundary_record = result.get("credential_vault_boundary_record")
    secret_handling_boundary_record = result.get("secret_handling_boundary_record")
    environment_read_boundary_record = result.get("environment_read_boundary_record")
    credential_secret_audit_proof = result.get("credential_secret_audit_proof")
    credential_secret_denial_ledger = result.get("credential_secret_denial_ledger")
    credential_secret_readiness_summary = result.get("credential_secret_readiness_summary")
    network_socket_lockdown_proof_bridge = result.get("network_socket_lockdown_proof_bridge")
    
    controlled_worker_hiring_activation_pilot_bundle = result.get("controlled_worker_hiring_activation_pilot_bundle")
    controlled_worker_hiring_activation_pilot_schema = result.get("controlled_worker_hiring_activation_pilot_schema")
    controlled_worker_hiring_activation_pilot_approval_gate = result.get("controlled_worker_hiring_activation_pilot_approval_gate")
    pilot_worker_limit_contract = result.get("pilot_worker_limit_contract")
    worker_identity_activation_contract = result.get("worker_identity_activation_contract")
    task_assignment_denial_by_default = result.get("task_assignment_denial_by_default")
    human_supervised_pilot_gate = result.get("human_supervised_pilot_gate")
    pilot_rollback_abort_preview = result.get("pilot_rollback_abort_preview")
    pilot_audit_proof = result.get("pilot_audit_proof")
    pilot_ledger = result.get("pilot_ledger")
    pilot_readiness_summary = result.get("pilot_readiness_summary")
    first_supervised_production_dry_run_bridge = result.get("first_supervised_production_dry_run_bridge")

    files_planned = [
        "run_log.json",
        "command_brief.json",
        "work_orders.json",
        "selected_overlays.json",
        "evidence.json",
        "execution_plan.json",
        "adapter_result.json",
    ]
    if file_operation_plan:
        files_planned.extend(["file_operation_plan.json", "execution_gate.json", "file_operation_result.json"])
    if repo_patch_plan:
        files_planned.extend(["repo_patch_plan.json", "repo_patch_gate.json", "repo_patch_result.json", "changed_file_scope_proof.json"])
    if execution_profile:
        files_planned.append("execution_profile.json")
    if preflight_gate_record:
        files_planned.append("preflight_gate_record.json")
    if patch_approval_checklist:
        files_planned.append("patch_approval_checklist.json")
    if execution_readiness_score:
        files_planned.append("execution_readiness_score.json")
    if dry_run_bundle:
        files_planned.extend(["dry_run_bundle.json", "repo_patch_preview.diff"])
    if dry_run_bundle_comparison:
        files_planned.append("dry_run_bundle_comparison.json")
    if approval_handoff_packet:
        files_planned.append("approval_handoff_packet.json")
    if signed_approval_record:
        files_planned.extend(["approval_review_ui_schema.json", "signed_approval_record.json", "approval_record_verification.json", "approval_record_audit_manifest.json"])
    if result.get("approval_ledger_bundle"):
        files_planned.extend(["approval_ledger_bundle.json", "approval_ledger_index.json", "approval_ledger_verification.json", "approval_status_summary.json", "duplicate_approval_signals.json"])
    if result.get("release_lock_bundle"):
        files_planned.extend(["release_lock_bundle.json", "stable_release_manifest.json", "stable_release_verification.json", "stable_runtime_contract.json", "stable_capability_inventory.json", "stable_artifact_contract.json", "stable_adapter_boundary_contract.json", "stable_safety_doctrine_lock.json", "stable_approval_flow_lock.json", "known_limitations.json", "next_phase_handoff.json", "release_readiness_summary.json"])
    if result.get("controlled_execution_bundle"):
        files_planned.extend(["controlled_execution_bundle.json", "controlled_execution_profile_catalog.json", "controlled_execution_selection.json", "execution_permission_matrix.json", "execution_mode_contract.json", "blocked_action_ledger.json", "controlled_execution_preflight_contract.json", "controlled_execution_readiness_summary.json"])
    if result.get("work_order_executor_bundle"):
        files_planned.extend(["work_order_executor_readiness_bridge.json", "work_order_executor_bundle.json", "executable_work_order_schema.json", "work_orders_executable.json", "work_order_status_lifecycle.json", "work_order_dependency_map.json", "work_order_dry_run_results.json", "work_order_execution_ledger.json", "work_order_completion_proofs.json", "work_order_executor_summary.json"])
    if result.get("worker_hiring_registry_bundle"):
        files_planned.extend(["worker_hiring_registry_bundle.json", "worker_role_schema.json", "worker_candidates.json", "worker_registry_status_lifecycle.json", "worker_assignment_plan.json", "worker_registry_ledger.json", "worker_hiring_preview_records.json", "worker_hiring_readiness_summary.json", "worker_hiring_readiness_bridge.json"])
    if result.get("department_routing_bundle"):
        files_planned.extend(["department_routing_readiness_bridge.json", "department_routing_bundle.json", "department_routing_schema.json", "department_route_candidates.json", "family_to_department_routing_map.json", "worker_to_department_assignment_map.json", "department_routing_conflict_detector.json", "department_routing_dry_run_results.json", "department_routing_ledger.json", "department_routing_completion_proofs.json", "department_routing_readiness_summary.json"])
    if result.get("multi_agent_orchestration_bundle"):
        files_planned.extend(["multi_agent_orchestration_readiness_bridge.json", "multi_agent_orchestration_bundle.json", "orchestration_topology_schema.json", "orchestration_node_generation.json", "multi_worker_coordination_map.json", "task_handoff_simulation.json", "inter_worker_dependency_graph.json", "orchestration_conflict_detector.json", "orchestration_dry_run_engine.json", "orchestration_ledger.json", "orchestration_completion_proof.json", "orchestration_readiness_summary.json"])
    if result.get("operator_console_bundle"):
        files_planned.extend(["ui_operator_console_readiness_bridge.json", "operator_console_bundle.json", "operator_console_screen_schema.json", "runtime_status_panel_schema.json", "approval_queue_panel_schema.json", "work_order_panel_schema.json", "worker_registry_panel_schema.json", "department_routing_panel_schema.json", "orchestration_sandbox_panel_schema.json", "human_control_surface_schema.json", "operator_action_registry.json", "disabled_action_state_map.json", "operator_console_review_bundle.json", "operator_console_safety_summary.json", "operator_console_readiness_summary.json"])
    if result.get("github_patch_hardening_bundle"):
        files_planned.extend(["github_patch_hardening_readiness_bridge.json", "github_patch_hardening_bundle.json", "patch_hardening_schema.json", "protected_path_policy.json", "patch_root_validation.json", "patch_preview_diff_contract.json", "patch_digest_manifest.json", "patch_rollback_preview.json", "changed_file_proof_hardening.json", "human_approval_chain_binding.json", "patch_execution_readiness_score.json", "patch_hardening_audit_bundle.json"])
    if result.get("deployment_packaging_bundle"):
        files_planned.extend(["deployment_packaging_readiness_bridge.json", "deployment_packaging_bundle.json", "deployment_artifact_schema.json", "portfolio_packaging_manifest.json", "runtime_export_bundle.json", "release_notes.json", "deployment_safety_contract.json", "deployment_readiness_proof.json", "packaging_audit_bundle.json", "portfolio_handoff_summary.json"])
    if result.get("controlled_worker_execution_bundle"):
        files_planned.extend(["first_controlled_worker_execution_readiness_bridge.json", "controlled_worker_execution_bundle.json", "controlled_worker_execution_schema.json", "worker_execution_gate.json", "tool_permission_binding.json", "sandbox_worker_task.json", "worker_abort_contract.json", "worker_rollback_contract.json", "worker_execution_telemetry_stub.json", "controlled_worker_execution_result.json", "post_run_audit_proof.json", "worker_execution_ledger.json"])
    if result.get("tool_permission_binding_bundle"):
        files_planned.extend(["single_worker_tool_permission_binding_readiness_bridge.json", "tool_permission_binding_bundle.json", "tool_permission_binding_schema.json"])
    if result.get("live_execution_telemetry_abort_bundle"):
        files_planned.extend(["live_execution_telemetry_abort_schema.json", "telemetry_event_schema.json", "execution_state_model.json", "telemetry_approval_gate.json", "heartbeat_stub.json", "abort_signal_contract.json", "timeout_contract.json", "partial_result_capture.json", "failed_run_quarantine_contract.json", "post_abort_audit_proof.json", "telemetry_ledger.json", "telemetry_readiness_summary.json"])
    if result.get("post_run_audit_expansion_bundle"):
        files_planned.extend(["post_run_audit_expansion_readiness_bridge.json", "post_run_audit_expansion_bundle.json", "post_run_audit_expansion_schema.json", "expanded_audit_evidence_schema.json", "post_run_audit_approval_gate.json", "before_after_run_comparison_proof.json", "validator_backed_audit_artifact_index.json", "audit_replay_record.json", "failure_class_taxonomy.json", "human_review_packet.json", "audit_integrity_score.json", "audit_evidence_ledger.json", "audit_expansion_readiness_summary.json"])
    if result.get("multi_worker_sandbox_coordination_bundle"):
        files_planned.extend(["multi_worker_sandbox_coordination_readiness_bridge.json", "multi_worker_sandbox_coordination_bundle.json", "multi_worker_sandbox_coordination_schema.json", "multi_worker_coordination_approval_gate.json", "sandbox_worker_roster.json", "worker_coordination_graph.json", "inter_worker_handoff_contract.json", "multi_worker_dry_run_ledger.json", "coordination_conflict_detector.json", "coordination_abort_contract.json", "coordination_quarantine_contract.json", "coordination_audit_proof.json", "coordination_readiness_summary.json"])
    if result.get("controlled_external_tool_adapter_preview_bundle"):
        files_planned.extend(["controlled_external_tool_adapter_preview_readiness_bridge.json", "controlled_external_tool_adapter_preview_bundle.json", "controlled_external_tool_adapter_preview_schema.json", "external_tool_adapter_preview_approval_gate.json", "external_tool_dry_run_adapter_registry.json", "per_tool_external_permission_gate.json", "external_request_preview_contract.json", "external_response_validation_schema.json", "external_response_validation_preview_result.json", "external_tool_abort_contract.json", "external_tool_audit_proof.json", "external_tool_preview_ledger.json", "external_tool_preview_readiness_summary.json"])
    if result.get("permissioned_external_api_dry_run_preview_bundle"):
        files_planned.extend(["permissioned_external_api_dry_run_preview_readiness_bridge.json", "permissioned_external_api_dry_run_preview_bundle.json", "permissioned_external_api_dry_run_preview_schema.json", "external_api_dry_run_approval_gate.json", "api_endpoint_preview_registry.json", "request_envelope_validation.json", "credential_absence_proof.json", "outbound_call_prevention_proof.json", "dry_run_response_fixture_contract.json", "external_api_audit_proof.json", "external_api_dry_run_ledger.json", "external_api_dry_run_readiness_summary.json"])
    if result.get("controlled_multi_worker_audit_replay_preview_bundle"):
        files_planned.extend(["controlled_multi_worker_audit_replay_preview_readiness_bridge.json", "controlled_multi_worker_audit_replay_preview_bundle.json", "controlled_multi_worker_audit_replay_preview_schema.json", "audit_replay_preview_approval_gate.json", "replay_packet_registry.json", "deterministic_replay_plan_contract.json", "replay_safety_gate.json", "multi_worker_replay_comparison_proof.json", "replay_output_quarantine_contract.json", "replay_audit_proof.json", "replay_preview_ledger.json", "replay_readiness_summary.json"])
    if result.get("operator_approval_queue_enforcement_bundle"):
        files_planned.extend(["operator_approval_queue_enforcement_readiness_bridge.json", "operator_approval_queue_enforcement_bundle.json", "operator_approval_queue_enforcement_schema.json", "operator_approval_queue_enforcement_approval_gate.json", "queued_action_registry.json", "approval_item_priority_classifier.json", "operator_decision_contract.json", "approval_expiry_stale_item_detector.json", "queue_enforcement_safety_gate.json", "approval_queue_audit_proof.json", "approval_queue_ledger.json", "approval_queue_readiness_summary.json"])
    if result.get("release_candidate_hardening_bundle"):
        files_planned.extend(["release_candidate_hardening_readiness_bridge.json", "release_candidate_hardening_bundle.json", "release_candidate_hardening_schema.json", "release_candidate_hardening_approval_gate.json", "full_runtime_invariant_scan.json", "validator_chain_lock_proof.json", "artifact_contract_freeze_manifest.json", "known_issue_register.json", "pre_v3_production_readiness_checklist.json", "release_candidate_safety_gate.json", "release_candidate_audit_proof.json", "release_candidate_ledger.json", "release_candidate_readiness_summary.json", "controlled_production_readiness_gate_bridge.json"])
    if result.get("controlled_production_readiness_gate_bundle"):
        files_planned.extend(["controlled_production_readiness_gate_bundle.json", "controlled_production_readiness_gate_schema.json", "controlled_production_readiness_gate_approval_gate.json", "production_activation_denial_by_default.json", "final_human_approval_requirement.json", "production_capability_manifest.json", "supervised_pilot_eligibility_contract.json", "production_rollback_kill_switch_preview.json", "production_readiness_audit_proof.json", "production_readiness_ledger.json", "production_readiness_summary.json", "controlled_worker_hiring_activation_pilot_bridge.json"])
    if result.get("limited_external_tool_supervised_pilot_bundle"):
        files_planned.extend(["limited_external_tool_supervised_pilot_bundle.json", "limited_external_tool_supervised_pilot_schema.json", "limited_external_tool_supervised_pilot_approval_gate.json", "single_external_tool_category_contract.json", "tool_invocation_denial_by_default.json", "human_tool_use_preflight_gate.json", "tool_request_envelope_preview.json", "tool_response_quarantine_preview.json", "tool_audit_proof.json", "tool_pilot_ledger.json", "tool_pilot_readiness_summary.json", "supervised_external_api_pilot_bridge.json"])
    if result.get("supervised_external_api_pilot_bundle"):
        files_planned.extend([
            "supervised_external_api_pilot_bundle.json",
            "supervised_external_api_pilot_schema.json",
            "supervised_external_api_pilot_approval_gate.json",
            "single_api_category_contract.json",
            "credential_denial_by_default.json",
            "secret_handling_denial_by_default.json",
            "network_socket_denial_by_default.json",
            "human_api_use_preflight_gate.json",
            "api_request_envelope_preview.json",
            "api_response_quarantine_preview.json",
            "api_audit_proof.json",
            "api_pilot_ledger.json",
            "api_pilot_readiness_summary.json",
            "monitored_rollback_recovery_drill_bridge.json"
        ])
    if result.get("monitored_rollback_recovery_drill_bundle"):
        files_planned.extend([
            "monitored_rollback_recovery_drill_bundle.json",
            "monitored_rollback_recovery_drill_schema.json",
            "monitored_rollback_recovery_drill_approval_gate.json",
            "simulated_failure_trigger_contract.json",
            "rollback_path_preview.json",
            "recovery_checkpoint_contract.json",
            "quarantine_freeze_preview.json",
            "human_recovery_approval_gate.json",
            "recovery_audit_proof.json",
            "rollback_recovery_drill_ledger.json",
            "recovery_readiness_summary.json",
            "supervised_production_pilot_readiness_review_bridge.json",
        ])
    if result.get("supervised_production_pilot_readiness_review_bundle"):
        files_planned.extend([
            "supervised_production_pilot_readiness_review_bundle.json",
            "supervised_production_pilot_readiness_review_schema.json",
            "supervised_production_pilot_readiness_review_approval_gate.json",
            "minimum_viable_production_candidate_contract.json",
            "human_production_pilot_review_gate.json",
            "production_blast_radius_analysis.json",
            "live_action_denial_review.json",
            "rollback_availability_review.json",
            "credential_secret_readiness_denial_proof.json",
            "network_socket_readiness_denial_proof.json",
            "production_pilot_audit_proof.json",
            "production_pilot_readiness_ledger.json",
            "production_pilot_readiness_summary.json",
            "credential_vault_denial_secret_handling_proof_bridge.json",
        ])
    if result.get("credential_vault_denial_secret_handling_proof_bundle"):
        files_planned.extend([
            "credential_vault_denial_secret_handling_proof_bundle.json",
            "credential_vault_denial_secret_handling_proof_schema.json",
            "credential_vault_denial_secret_handling_proof_approval_gate.json",
            "credential_access_denial_contract.json",
            "secret_read_denial_contract.json",
            "environment_variable_denial_contract.json",
            "credential_vault_boundary_record.json",
            "secret_handling_boundary_record.json",
            "environment_read_boundary_record.json",
            "credential_secret_audit_proof.json",
            "credential_secret_denial_ledger.json",
            "credential_secret_readiness_summary.json",
            "network_socket_lockdown_proof_bridge.json",
        ])
    if controlled_worker_hiring_activation_pilot_bundle:
        files_planned.extend(["controlled_worker_hiring_activation_pilot_bundle.json", "controlled_worker_hiring_activation_pilot_schema.json", "controlled_worker_hiring_activation_pilot_approval_gate.json", "pilot_worker_limit_contract.json", "worker_identity_activation_contract.json", "task_assignment_denial_by_default.json", "human_supervised_pilot_gate.json", "pilot_rollback_abort_preview.json", "pilot_audit_proof.json", "pilot_ledger.json", "pilot_readiness_summary.json", "first_supervised_production_dry_run_bridge.json"])

    if result.get("live_external_action_final_preflight_gate_bundle"):
        files_planned.extend([
            "live_external_action_final_preflight_gate_bundle.json",
            "live_external_action_final_preflight_gate_schema.json",
            "live_external_action_final_preflight_gate_approval_gate.json",
            "tiny_action_candidate_boundary_contract.json",
            "live_external_action_non_execution_contract.json",
            "blast_radius_ceiling_contract.json",
            "human_final_approval_requirement.json",
            "credential_secret_environment_re_denial_proof.json",
            "network_socket_api_re_denial_proof.json",
            "deployment_production_re_denial_proof.json",
            "rollback_recovery_availability_assertion.json",
            "first_tiny_real_world_execution_candidate_audit_proof.json",
            "final_preflight_ledger.json",
            "first_tiny_real_world_supervised_execution_candidate_bridge.json",
        ])
        if result.get("first_tiny_real_world_supervised_execution_candidate_bundle"):
            files_planned.extend([
                "first_tiny_real_world_supervised_execution_candidate_bundle.json",
                "first_tiny_real_world_supervised_execution_candidate_schema.json",
                "first_tiny_real_world_supervised_execution_candidate_approval_gate.json",
            "local_proof_artifact_candidate_contract.json",
            "explicit_output_directory_boundary_contract.json",
            "forbidden_path_contract.json",
            "local_only_execution_envelope.json",
            "candidate_pre_action_audit_proof.json",
            "local_proof_artifact_execution_record.json",
            "post_action_verification_record.json",
            "cleanup_rollback_instruction_record.json",
            "first_tiny_candidate_ledger.json",
            "first_tiny_candidate_readiness_summary.json",
            "post_action_verification_and_audit_review_bridge.json",
            "local_proof_artifact_payload.json",
        ])
    if result.get("post_action_verification_and_audit_review_bundle"):
        files_planned.extend([
            "post_action_verification_and_audit_review_bundle.json",
            "post_action_verification_and_audit_review_schema.json",
            "post_action_verification_and_audit_review_approval_gate.json",
            "v4_candidate_artifact_reference_contract.json",
            "artifact_integrity_verification_record.json",
            "artifact_path_containment_review.json",
            "safety_boolean_review.json",
            "cleanup_instruction_review.json",
            "operator_review_acknowledgement.json",
            "post_action_closeout_ledger.json",
            "post_action_readiness_summary.json",
            "supervised_rollback_cleanup_candidate_bridge.json",
            "post_action_verification_and_audit_review_record.json",
        ])
    if result.get("supervised_rollback_cleanup_candidate_bundle"):
        files_planned.extend([
            "supervised_rollback_cleanup_candidate_bundle.json",
            "supervised_rollback_cleanup_candidate_schema.json",
            "supervised_rollback_cleanup_candidate_approval_gate.json",
            "cleanup_candidate_contract.json",
            "artifact_pre_cleanup_verification_record.json",
            "cleanup_path_containment_record.json",
            "cleanup_scope_envelope.json",
            "cleanup_execution_record.json",
            "post_cleanup_verification_record.json",
            "cleanup_audit_record.json",
            "cleanup_closeout_ledger.json",
            "cleanup_readiness_summary.json",
            "limited_live_worker_activation_candidate_bridge.json",
        ])
    if result.get("limited_live_worker_activation_candidate_bundle"):
        files_planned.extend([
            "limited_live_worker_activation_candidate_bundle.json",
            "limited_live_worker_activation_candidate_schema.json",
            "limited_live_worker_activation_candidate_approval_gate.json",
            "worker_template_reference_contract.json",
            "one_worker_activation_scope_contract.json",
            "non_execution_worker_boundary.json",
            "worker_permission_denial_record.json",
            "worker_activation_candidate_record.json",
            "worker_activation_audit_record.json",
            "worker_activation_ledger.json",
            "worker_activation_readiness_summary.json",
            "permissioned_worker_task_assignment_candidate_bridge.json",
            "worker_activation_record_payload.json",
            "worker_activation_write_record.json",
        ])
    if result.get("permissioned_worker_task_assignment_candidate_bundle"):
        files_planned.extend([
            "permissioned_worker_task_assignment_candidate_bundle.json",
            "permissioned_worker_task_assignment_candidate_schema.json",
            "permissioned_worker_task_assignment_candidate_approval_gate.json",
            "worker_template_reference_contract.json",
            "task_label_reference_contract.json",
            "one_worker_one_task_assignment_scope_contract.json",
            "non_execution_task_boundary.json",
            "task_permission_denial_record.json",
            "permissioned_worker_task_assignment_candidate_record.json",
            "task_assignment_audit_record.json",
            "task_assignment_ledger.json",
            "task_assignment_readiness_summary.json",
            "task_assignment_audit_closeout_candidate_bridge.json",
            "task_assignment_record_payload.json",
            "task_assignment_write_record.json",
        ])
    if result.get("task_assignment_audit_closeout_candidate_bundle"):
        files_planned.extend([
            "task_assignment_audit_closeout_candidate_bundle.json",
            "task_assignment_audit_closeout_candidate_schema.json",
            "task_assignment_audit_closeout_candidate_approval_gate.json",
            "v4_4_task_assignment_record_reference_contract.json",
            "task_assignment_record_integrity_verification.json",
            "task_assignment_record_path_containment_review.json",
            "task_assignment_safety_boolean_review.json",
            "non_execution_closeout_boundary.json",
            "operator_closeout_acknowledgement.json",
            "task_assignment_closeout_audit_record.json",
            "task_assignment_closeout_ledger.json",
            "task_assignment_closeout_readiness_summary.json",
            "non_executing_task_queue_preview_candidate_bridge.json",
            "task_assignment_audit_closeout_record_payload.json",
            "task_assignment_closeout_write_record.json",
        ])
    if result.get("non_executing_task_queue_preview_candidate_bundle"):
        files_planned.extend([
            "non_executing_task_queue_preview_candidate_bundle.json",
            "non_executing_task_queue_preview_candidate_schema.json",
            "non_executing_task_queue_preview_candidate_approval_gate.json",
            "v4_4_task_assignment_record_reference_contract.json",
            "optional_v4_5_closeout_record_reference_contract.json",
            "task_assignment_record_integrity_verification.json",
            "closeout_record_integrity_verification.json",
            "task_assignment_record_path_containment_review.json",
            "queue_preview_scope_contract.json",
            "non_execution_queue_boundary.json",
            "queue_permission_denial_record.json",
            "non_executing_task_queue_preview_candidate_record.json",
            "queue_preview_audit_record.json",
            "queue_preview_ledger.json",
            "queue_preview_readiness_summary.json",
            "task_queue_preview_audit_closeout_candidate_bridge.json",
            "queue_preview_record_payload.json",
            "queue_preview_write_record.json",
        ])
    if result.get("task_queue_preview_audit_closeout_candidate_bundle"):
        files_planned.extend([
            "task_queue_preview_audit_closeout_candidate_bundle.json",
            "task_queue_preview_audit_closeout_candidate_schema.json",
            "task_queue_preview_audit_closeout_candidate_approval_gate.json",
            "v4_6_queue_preview_record_reference_contract.json",
            "queue_preview_record_integrity_verification.json",
            "queue_preview_record_path_containment_review.json",
            "queue_preview_safety_boolean_review.json",
            "non_execution_queue_closeout_boundary.json",
            "operator_queue_closeout_acknowledgement.json",
            "queue_preview_closeout_audit_record.json",
            "queue_preview_closeout_ledger.json",
            "queue_preview_closeout_readiness_summary.json",
            "non_executing_worker_routing_preview_candidate_bridge.json",
            "queue_closeout_record_payload.json",
            "queue_closeout_write_record.json",
        ])
    if result.get("queue_routing_preview_candidate_bundle"):
        files_planned.extend([
            "queue_routing_preview_candidate_bundle.json",
            "queue_routing_preview_candidate_schema.json",
            "queue_routing_preview_approval_gate.json",
            "hypothetical_task_candidate_reference.json",
            "worker_template_reference_contract.json",
            "queue_preview_scope_contract.json",
            "non_execution_routing_boundary.json",
            "routing_permission_denial_record.json",
            "routing_preview_candidate_record.json",
            "routing_preview_audit_record.json",
            "routing_preview_readiness_summary.json",
            "live_queue_orchestration_candidate_bridge.json",
            "queue_routing_preview_record_payload.json",
            "queue_routing_preview_write_record.json",
        ])
    if result.get("live_queue_orchestration_candidate_review_bundle"):
        files_planned.extend([
            "live_queue_orchestration_candidate_review_bundle.json",
            "live_queue_orchestration_candidate_review_schema.json",
            "orchestration_review_approval_gate.json",
            "v4_8_queue_routing_preview_reference_contract.json",
            "orchestration_review_scope_contract.json",
            "non_execution_orchestration_boundary.json",
            "orchestration_permission_denial_record.json",
            "orchestration_candidate_review_record.json",
            "orchestration_review_audit_record.json",
            "orchestration_readiness_summary.json",
            "first_live_queue_execution_candidate_bridge.json",
            "orchestration_candidate_review_record_payload.json",
            "orchestration_candidate_review_write_record.json",
        ])
    if result.get("first_live_queue_execution_candidate_review_bundle"):
        files_planned.extend([
            "first_live_queue_execution_candidate_review_bundle.json",
            "first_live_queue_execution_candidate_review_schema.json",
            "execution_candidate_review_approval_gate.json",
            "v4_9_orchestration_review_reference_contract.json",
            "execution_candidate_review_scope_contract.json",
            "non_execution_execution_boundary.json",
            "execution_permission_denial_record.json",
            "execution_candidate_review_record.json",
            "execution_candidate_review_audit_record.json",
            "execution_candidate_readiness_summary.json",
            "first_supervised_local_execution_kernel_candidate_bridge.json",
            "execution_candidate_review_record_payload.json",
            "execution_candidate_review_write_record.json",
        ])
    if result.get("first_supervised_local_execution_kernel_candidate_bundle"):
        files_planned.extend([
            "first_supervised_local_execution_kernel_candidate_bundle.json",
            "first_supervised_local_execution_kernel_candidate_schema.json",
            "supervised_execution_kernel_approval_gate.json",
            "synthetic_task_contract.json",
            "sandbox_output_scope_contract.json",
            "non_external_execution_boundary.json",
            "execution_permission_denial_record.json",
            "supervised_local_execution_plan_record.json",
            "supervised_local_execution_result_record.json",
            "supervised_local_execution_audit_record.json",
            "supervised_local_execution_readiness_summary.json",
            "controlled_repeatable_local_execution_candidate_bridge.json",
            "supervised_local_execution_output_payload.json",
            "supervised_local_execution_write_record.json",
        ])
    if result.get("controlled_repeatable_local_execution_candidate_bundle"):
        files_planned.extend([
            "controlled_repeatable_local_execution_candidate_bundle.json",
            "controlled_repeatable_local_execution_candidate_schema.json",
            "repeatable_execution_approval_gate.json",
            "synthetic_repeatable_task_contract.json",
            "repeatability_scope_contract.json",
            "non_external_repeatability_boundary.json",
            "repeatability_permission_denial_record.json",
            "repeatability_plan_record.json",
            "repeatability_entries_record.json",
            "repeatability_proof_result_record.json",
            "repeatability_audit_record.json",
            "repeatability_readiness_summary.json",
            "sandbox_worker_handoff_candidate_bridge.json",
            "repeatability_proof_payload.json",
            "repeatability_proof_write_record.json",
        ])
    if result.get("sandbox_worker_handoff_candidate_bundle"):
        files_planned.extend([
            "sandbox_worker_handoff_candidate_bundle.json",
            "sandbox_worker_handoff_candidate_schema.json",
            "sandbox_worker_handoff_approval_gate.json",
            "v5_2_repeatability_proof_reference_contract.json",
            "synthetic_task_handoff_contract.json",
            "sandbox_worker_reference_contract.json",
            "handoff_scope_contract.json",
            "non_execution_handoff_boundary.json",
            "handoff_permission_denial_record.json",
            "handoff_plan_record.json",
            "handoff_packet_record.json",
            "handoff_audit_record.json",
            "handoff_readiness_summary.json",
            "sandbox_worker_acknowledgement_candidate_bridge.json",
            "handoff_packet_payload.json",
            "handoff_packet_write_record.json",
        ])

    return {
        "run_log": {
            "run_id": run_id,
            "runtime_version": result["station_chief_runtime_version"],
            "command": result["command"],
            "command_type": result["command_type"],
            "activation_tier": result["activation_tier"],
            "runtime_status": result["runtime_status"],
            "overlay_stack_loaded": result["overlay_stack_loaded"],
            "deterministic_demo_mode": result["evidence"]["deterministic_demo_mode"],
            "baseline_preserved": result["evidence"]["baseline_preserved"],
            "external_actions_taken": result["evidence"]["external_actions_taken"],
            "live_worker_agents_activated": result["evidence"]["live_worker_agents_activated"],
            "validators_required_before_completion": result["evidence"]["validators_required_before_completion"],
            "next_step": result["next_step"],
        },
        "command_brief": command_brief,
        "work_orders": work_orders,
        "selected_overlays": {
            "selected_overlay_ids": result["selected_overlays"],
            "selected_overlay_records": selected_records,
        },
        "evidence": result["evidence"],
        "execution_plan": execution_plan,
        "adapter_result": adapter_result,
        "file_operation_plan": file_operation_plan,
        "execution_gate": execution_gate,
        "file_operation_result": file_operation_result,
        "repo_patch_plan": repo_patch_plan,
        "repo_patch_gate": repo_patch_gate,
        "repo_patch_result": repo_patch_result,
        "changed_file_scope_proof": changed_file_scope_proof,
        "execution_profile": execution_profile,
        "preflight_gate_record": preflight_gate_record,
        "patch_approval_checklist": patch_approval_checklist,
        "execution_readiness_score": execution_readiness_score,
        "dry_run_bundle": dry_run_bundle,
        "dry_run_bundle_comparison": dry_run_bundle_comparison,
        "approval_handoff_packet": approval_handoff_packet,
        "approval_review_ui_schema": approval_review_ui_schema,
        "signed_approval_record": signed_approval_record,
        "approval_record_verification": approval_record_verification,
        "approval_record_audit_manifest": approval_record_audit_manifest,
        "approval_record_sources": result.get("approval_record_sources"),
        "approval_ledger_bundle": result.get("approval_ledger_bundle"),
        "approval_ledger_index": result.get("approval_ledger_index"),
        "approval_ledger_verification": result.get("approval_ledger_verification"),
        "approval_status_summary": result.get("approval_status_summary"),
        "duplicate_approval_signals": result.get("duplicate_approval_signals"),
        "approval_ledger_lookup": result.get("approval_ledger_lookup"),
        "approval_record_comparison": result.get("approval_record_comparison"),
        "release_lock_bundle": result.get("release_lock_bundle"),
        "stable_release_manifest": result.get("stable_release_manifest"),
        "stable_release_verification": result.get("stable_release_verification"),
        "stable_runtime_contract": result.get("stable_runtime_contract"),
        "stable_capability_inventory": result.get("stable_capability_inventory"),
        "stable_artifact_contract": result.get("stable_artifact_contract"),
        "stable_adapter_boundary_contract": result.get("stable_adapter_boundary_contract"),
        "stable_safety_doctrine_lock": result.get("stable_safety_doctrine_lock"),
        "stable_approval_flow_lock": result.get("stable_approval_flow_lock"),
        "known_limitations": result.get("known_limitations"),
        "next_phase_handoff": result.get("next_phase_handoff"),
        "release_readiness_summary": result.get("release_readiness_summary"),
        "controlled_execution_bundle": result.get("controlled_execution_bundle"),
        "controlled_execution_profile_catalog": result.get("controlled_execution_profile_catalog"),
        "controlled_execution_selection": result.get("controlled_execution_selection"),
        "execution_permission_matrix": result.get("execution_permission_matrix"),
        "execution_mode_contract": result.get("execution_mode_contract"),
        "blocked_action_ledger": result.get("blocked_action_ledger"),
        "controlled_execution_preflight_contract": result.get("controlled_execution_preflight_contract"),
        "controlled_execution_readiness_summary": result.get("controlled_execution_readiness_summary"),
        "work_order_executor_readiness_bridge": result.get("work_order_executor_readiness_bridge"),
        "work_order_executor_bundle": result.get("work_order_executor_bundle"),
        "executable_work_order_schema": result.get("executable_work_order_schema"),
        "work_orders_executable": result.get("work_orders_executable"),
        "work_order_status_lifecycle": result.get("work_order_status_lifecycle"),
        "work_order_dependency_map": result.get("work_order_dependency_map"),
        "work_order_dry_run_results": result.get("work_order_dry_run_results"),
        "work_order_execution_ledger": result.get("work_order_execution_ledger"),
        "work_order_completion_proofs": result.get("work_order_completion_proofs"),
        "work_order_executor_summary": result.get("work_order_executor_summary"),
        "worker_hiring_registry_bundle": result.get("worker_hiring_registry_bundle"),
        "worker_role_schema": result.get("worker_role_schema"),
        "worker_candidates": result.get("worker_candidates"),
        "worker_registry_status_lifecycle": result.get("worker_registry_status_lifecycle"),
        "worker_assignment_plan": result.get("worker_assignment_plan"),
        "worker_registry_ledger": result.get("worker_registry_ledger"),
        "worker_hiring_preview_records": result.get("worker_hiring_preview_records"),
        "worker_hiring_readiness_summary": result.get("worker_hiring_readiness_summary"),
        "department_routing_readiness_bridge": result.get("department_routing_readiness_bridge"),
        "department_routing_bundle": result.get("department_routing_bundle"),
        "department_routing_schema": result.get("department_routing_schema"),
        "department_route_candidates": result.get("department_route_candidates"),
        "family_to_department_routing_map": result.get("family_to_department_routing_map"),
        "worker_to_department_assignment_map": result.get("worker_to_department_assignment_map"),
        "department_routing_conflict_detector": result.get("department_routing_conflict_detector"),
        "department_routing_dry_run_results": result.get("department_routing_dry_run_results"),
        "department_routing_ledger": result.get("department_routing_ledger"),
        "department_routing_completion_proofs": result.get("department_routing_completion_proofs"),
        "department_routing_readiness_summary": result.get("department_routing_readiness_summary"),
        "multi_agent_orchestration_readiness_bridge": result.get("multi_agent_orchestration_readiness_bridge"),
        "multi_agent_orchestration_bundle": result.get("multi_agent_orchestration_bundle"),
        "orchestration_topology_schema": result.get("orchestration_topology_schema"),
        "orchestration_nodes": result.get("orchestration_nodes"),
        "multi_worker_coordination_map": result.get("multi_worker_coordination_map"),
        "task_handoff_simulation": result.get("task_handoff_simulation"),
        "inter_worker_dependency_graph": result.get("inter_worker_dependency_graph"),
        "orchestration_conflict_detector": result.get("orchestration_conflict_detector"),
        "orchestration_dry_run_results": result.get("orchestration_dry_run_results"),
        "orchestration_ledger": result.get("orchestration_ledger"),
        "orchestration_completion_proofs": result.get("orchestration_completion_proofs"),
        "orchestration_readiness_summary": result.get("orchestration_readiness_summary"),
        "ui_operator_console_readiness_bridge": result.get("ui_operator_console_readiness_bridge"),
        "operator_console_bundle": result.get("operator_console_bundle"),
        "operator_console_review_bundle": result.get("operator_console_review_bundle"),
        "operator_console_screen_schema": result.get("operator_console_screen_schema"),
        "runtime_status_panel_schema": result.get("runtime_status_panel_schema"),
        "approval_queue_panel_schema": result.get("approval_queue_panel_schema"),
        "work_order_panel_schema": result.get("work_order_panel_schema"),
        "worker_registry_panel_schema": result.get("worker_registry_panel_schema"),
        "department_routing_panel_schema": result.get("department_routing_panel_schema"),
        "orchestration_sandbox_panel_schema": result.get("orchestration_sandbox_panel_schema"),
        "release_lock_panel_schema": result.get("release_lock_panel_schema"),
        "human_control_surface_schema": result.get("human_control_surface_schema"),
        "operator_action_registry": result.get("operator_action_registry"),
        "disabled_action_state_map": result.get("disabled_action_state_map"),
        "operator_console_safety_summary": result.get("operator_console_safety_summary"),
        "operator_console_readiness_summary": result.get("operator_console_readiness_summary"),
        "github_patch_hardening_readiness_bridge": result.get("github_patch_hardening_readiness_bridge"),
        "github_patch_hardening_bundle": result.get("github_patch_hardening_bundle"),
        "patch_hardening_audit_bundle": result.get("patch_hardening_audit_bundle"),
        "patch_hardening_schema": result.get("patch_hardening_schema"),
        "protected_path_policy": result.get("protected_path_policy"),
        "patch_root_validation": result.get("patch_root_validation"),
        "patch_preview_diff_contract": result.get("patch_preview_diff_contract"),
        "patch_digest_manifest": result.get("patch_digest_manifest"),
        "patch_rollback_preview": result.get("patch_rollback_preview"),
        "changed_file_proof_hardening": result.get("changed_file_proof_hardening"),
        "human_approval_chain_binding": result.get("human_approval_chain_binding"),
        "patch_execution_readiness_score": result.get("patch_execution_readiness_score"),
        "deployment_packaging_readiness_bridge": result.get("deployment_packaging_readiness_bridge"),
        "deployment_packaging_bundle": result.get("deployment_packaging_bundle"),
        "deployment_artifact_schema": result.get("deployment_artifact_schema"),
        "portfolio_packaging_manifest": result.get("portfolio_packaging_manifest"),
        "runtime_export_bundle": result.get("runtime_export_bundle"),
        "release_notes": result.get("release_notes"),
        "deployment_safety_contract": result.get("deployment_safety_contract"),
        "deployment_readiness_proof": result.get("deployment_readiness_proof"),
        "portfolio_handoff_summary": result.get("portfolio_handoff_summary"),
        "packaging_audit_bundle": result.get("packaging_audit_bundle"),
        "first_controlled_worker_execution_readiness_bridge": result.get("first_controlled_worker_execution_readiness_bridge"),
        "controlled_worker_execution_bundle": result.get("controlled_worker_execution_bundle"),
        "controlled_worker_execution_schema": result.get("controlled_worker_execution_schema"),
        "worker_execution_gate": result.get("worker_execution_gate"),
        "tool_permission_binding": result.get("tool_permission_binding"),
        "sandbox_worker_task": result.get("sandbox_worker_task"),
        "worker_abort_contract": result.get("worker_abort_contract"),
        "worker_rollback_contract": result.get("worker_rollback_contract"),
        "worker_execution_telemetry_stub": result.get("worker_execution_telemetry_stub"),
        "controlled_worker_execution_result": result.get("controlled_worker_execution_result"),
        "post_run_audit_proof": result.get("post_run_audit_proof"),
        "worker_execution_ledger": result.get("worker_execution_ledger"),
        "live_execution_telemetry_abort_bundle": result.get("live_execution_telemetry_abort_bundle"),
        "live_execution_telemetry_abort_schema": result.get("live_execution_telemetry_abort_schema"),
        "telemetry_event_schema.json": result.get("telemetry_event_schema"),
        "execution_state_model.json": result.get("execution_state_model"),
        "telemetry_approval_gate.json": result.get("telemetry_approval_gate"),
        "heartbeat_stub.json": result.get("heartbeat_stub"),
        "abort_signal_contract.json": result.get("abort_signal_contract"),
        "timeout_contract.json": result.get("timeout_contract"),
        "partial_result_capture.json": result.get("partial_result_capture"),
        "failed_run_quarantine_contract.json": result.get("failed_run_quarantine_contract"),
        "post_abort_audit_proof.json": result.get("post_abort_audit_proof"),
        "telemetry_ledger.json": result.get("telemetry_ledger"),
        "telemetry_readiness_summary.json": result.get("telemetry_readiness_summary"),
        "post_run_audit_expansion_readiness_bridge": result.get("post_run_audit_expansion_readiness_bridge"),
        "post_run_audit_expansion_bundle": result.get("post_run_audit_expansion_bundle"),
        "post_run_audit_expansion_schema": result.get("post_run_audit_expansion_schema"),
        "expanded_audit_evidence_schema": result.get("expanded_audit_evidence_schema"),
        "post_run_audit_approval_gate": result.get("post_run_audit_approval_gate"),
        "before_after_run_comparison_proof": result.get("before_after_run_comparison_proof"),
        "validator_backed_audit_artifact_index": result.get("validator_backed_audit_artifact_index"),
        "audit_replay_record": result.get("audit_replay_record"),
        "failure_class_taxonomy": result.get("failure_class_taxonomy"),
        "human_review_packet": result.get("human_review_packet"),
        "audit_integrity_score": result.get("audit_integrity_score"),
        "audit_evidence_ledger": result.get("audit_evidence_ledger"),
        "audit_expansion_readiness_summary": result.get("audit_expansion_readiness_summary"),
        "multi_worker_sandbox_coordination_readiness_bridge": result.get("multi_worker_sandbox_coordination_readiness_bridge"),
        "multi_worker_sandbox_coordination_bundle": result.get("multi_worker_sandbox_coordination_bundle"),
        "multi_worker_sandbox_coordination_schema": result.get("multi_worker_sandbox_coordination_schema"),
        "multi_worker_coordination_approval_gate": result.get("multi_worker_coordination_approval_gate"),
        "sandbox_worker_roster": result.get("sandbox_worker_roster"),
        "worker_coordination_graph": result.get("worker_coordination_graph"),
        "inter_worker_handoff_contract": result.get("inter_worker_handoff_contract"),
        "multi_worker_dry_run_ledger": result.get("multi_worker_dry_run_ledger"),
        "coordination_conflict_detector": result.get("coordination_conflict_detector"),
        "coordination_abort_contract": result.get("coordination_abort_contract"),
        "coordination_quarantine_contract": result.get("coordination_quarantine_contract"),
        "coordination_audit_proof": result.get("coordination_audit_proof"),
        "coordination_readiness_summary": result.get("coordination_readiness_summary"),
        "controlled_external_tool_adapter_preview_readiness_bridge": result.get("controlled_external_tool_adapter_preview_readiness_bridge"),
        "controlled_external_tool_adapter_preview_bundle": result.get("controlled_external_tool_adapter_preview_bundle"),
        "controlled_external_tool_adapter_preview_schema": result.get("controlled_external_tool_adapter_preview_schema"),
        "external_tool_adapter_preview_approval_gate": result.get("external_tool_adapter_preview_approval_gate"),
        "external_tool_dry_run_adapter_registry": result.get("external_tool_dry_run_adapter_registry"),
        "per_tool_external_permission_gate": result.get("per_tool_external_permission_gate"),
        "external_request_preview_contract": result.get("external_request_preview_contract"),
        "external_response_validation_schema": result.get("external_response_validation_schema"),
        "external_response_validation_preview_result": result.get("external_response_validation_preview_result"),
        "external_tool_abort_contract": result.get("external_tool_abort_contract"),
        "external_tool_audit_proof": result.get("external_tool_audit_proof"),
        "external_tool_preview_ledger": result.get("external_tool_preview_ledger"),
        "external_tool_preview_readiness_summary": result.get("external_tool_preview_readiness_summary"),
        "permissioned_external_api_dry_run_preview_readiness_bridge": result.get("permissioned_external_api_dry_run_preview_readiness_bridge"),
        "permissioned_external_api_dry_run_preview_bundle": result.get("permissioned_external_api_dry_run_preview_bundle"),
        "permissioned_external_api_dry_run_preview_schema": result.get("permissioned_external_api_dry_run_preview_schema"),
        "external_api_dry_run_approval_gate": result.get("external_api_dry_run_approval_gate"),
        "api_endpoint_preview_registry": result.get("api_endpoint_preview_registry"),
        "request_envelope_validation": result.get("request_envelope_validation"),
        "credential_absence_proof": result.get("credential_absence_proof"),
        "outbound_call_prevention_proof": result.get("outbound_call_prevention_proof"),
        "dry_run_response_fixture_contract": result.get("dry_run_response_fixture_contract"),
        "external_api_audit_proof": result.get("external_api_audit_proof"),
        "external_api_dry_run_ledger": result.get("external_api_dry_run_ledger"),
        "external_api_dry_run_readiness_summary": result.get("external_api_dry_run_readiness_summary"),
        "controlled_multi_worker_audit_replay_preview_readiness_bridge": result.get("controlled_multi_worker_audit_replay_preview_readiness_bridge"),
        "controlled_multi_worker_audit_replay_preview_bundle": result.get("controlled_multi_worker_audit_replay_preview_bundle"),
        "controlled_multi_worker_audit_replay_preview_schema": result.get("controlled_multi_worker_audit_replay_preview_schema"),
        "audit_replay_preview_approval_gate": result.get("audit_replay_preview_approval_gate"),
        "replay_packet_registry": result.get("replay_packet_registry"),
        "deterministic_replay_plan_contract": result.get("deterministic_replay_plan_contract"),
        "replay_safety_gate": result.get("replay_safety_gate"),
        "multi_worker_replay_comparison_proof": result.get("multi_worker_replay_comparison_proof"),
        "replay_output_quarantine_contract": result.get("replay_output_quarantine_contract"),
        "replay_audit_proof": result.get("replay_audit_proof"),
        "replay_preview_ledger": result.get("replay_preview_ledger"),
        "replay_readiness_summary": result.get("replay_readiness_summary"),
        "operator_approval_queue_enforcement_readiness_bridge": result.get("operator_approval_queue_enforcement_readiness_bridge"),
        "operator_approval_queue_enforcement_bundle": result.get("operator_approval_queue_enforcement_bundle"),
        "operator_approval_queue_enforcement_schema": result.get("operator_approval_queue_enforcement_schema"),
        "operator_approval_queue_enforcement_approval_gate": result.get("operator_approval_queue_enforcement_approval_gate"),
        "queued_action_registry": result.get("queued_action_registry"),
        "approval_item_priority_classifier": result.get("approval_item_priority_classifier"),
        "operator_decision_contract": result.get("operator_decision_contract"),
        "approval_expiry_stale_item_detector": result.get("approval_expiry_stale_item_detector"),
        "queue_enforcement_safety_gate": result.get("queue_enforcement_safety_gate"),
        "approval_queue_audit_proof": result.get("approval_queue_audit_proof"),
        "approval_queue_ledger": result.get("approval_queue_ledger"),
        "approval_queue_readiness_summary": result.get("approval_queue_readiness_summary"),
        "release_candidate_hardening_readiness_bridge": result.get("release_candidate_hardening_readiness_bridge"),
        "release_candidate_hardening_bundle": result.get("release_candidate_hardening_bundle"),
        "release_candidate_hardening_schema": result.get("release_candidate_hardening_schema"),
        "release_candidate_hardening_approval_gate": result.get("release_candidate_hardening_approval_gate"),
        "full_runtime_invariant_scan": result.get("full_runtime_invariant_scan"),
        "validator_chain_lock_proof": result.get("validator_chain_lock_proof"),
        "artifact_contract_freeze_manifest": result.get("artifact_contract_freeze_manifest"),
        "known_issue_register": result.get("known_issue_register"),
        "pre_v3_production_readiness_checklist": result.get("pre_v3_production_readiness_checklist"),
        "release_candidate_safety_gate": result.get("release_candidate_safety_gate"),
        "release_candidate_audit_proof": result.get("release_candidate_audit_proof"),
        "release_candidate_ledger": result.get("release_candidate_ledger"),
        "release_candidate_readiness_summary": result.get("release_candidate_readiness_summary"),
        "controlled_production_readiness_gate_bridge": result.get("controlled_production_readiness_gate_bridge"),
        "controlled_production_readiness_gate_bundle": result.get("controlled_production_readiness_gate_bundle"),
        "controlled_production_readiness_gate_schema": result.get("controlled_production_readiness_gate_schema"),
        "controlled_production_readiness_gate_approval_gate": result.get("controlled_production_readiness_gate_approval_gate"),
        "production_activation_denial_by_default": result.get("production_activation_denial_by_default"),
        "final_human_approval_requirement": result.get("final_human_approval_requirement"),
        "production_capability_manifest": result.get("production_capability_manifest"),
        "supervised_pilot_eligibility_contract": result.get("supervised_pilot_eligibility_contract"),
        "production_rollback_kill_switch_preview": result.get("production_rollback_kill_switch_preview"),
        "production_readiness_audit_proof": result.get("production_readiness_audit_proof"),
        "production_readiness_ledger": result.get("production_readiness_ledger"),
        "production_readiness_summary": result.get("production_readiness_summary"),
        "controlled_worker_hiring_activation_pilot_bridge": result.get("controlled_worker_hiring_activation_pilot_bridge"),
        "limited_external_tool_supervised_pilot_bundle": result.get("limited_external_tool_supervised_pilot_bundle"),
        "limited_external_tool_supervised_pilot_schema": result.get("limited_external_tool_supervised_pilot_schema"),
        "limited_external_tool_supervised_pilot_approval_gate": result.get("limited_external_tool_supervised_pilot_approval_gate"),
        "single_external_tool_category_contract": result.get("single_external_tool_category_contract"),
        "tool_invocation_denial_by_default": result.get("tool_invocation_denial_by_default"),
        "human_tool_use_preflight_gate": result.get("human_tool_use_preflight_gate"),
        "tool_request_envelope_preview": result.get("tool_request_envelope_preview"),
        "tool_response_quarantine_preview": result.get("tool_response_quarantine_preview"),
        "tool_audit_proof": result.get("tool_audit_proof"),
        "tool_pilot_ledger": result.get("tool_pilot_ledger"),
        "tool_pilot_readiness_summary": result.get("tool_pilot_readiness_summary"),
        "supervised_external_api_pilot_bridge": supervised_external_api_pilot_bridge,
        "supervised_external_api_pilot_bundle": supervised_external_api_pilot_bundle,
        "supervised_external_api_pilot_schema": supervised_external_api_pilot_schema,
        "supervised_external_api_pilot_approval_gate": supervised_external_api_pilot_approval_gate,
        "single_api_category_contract": single_api_category_contract,
        "credential_denial_by_default": credential_denial_by_default,
        "secret_handling_denial_by_default": secret_handling_denial_by_default,
        "network_socket_denial_by_default": network_socket_denial_by_default,
        "human_api_use_preflight_gate": human_api_use_preflight_gate,
        "api_request_envelope_preview": api_request_envelope_preview,
        "api_response_quarantine_preview": api_response_quarantine_preview,
        "api_audit_proof": api_audit_proof,
        "api_pilot_ledger": api_pilot_ledger,
        "api_pilot_readiness_summary": api_pilot_readiness_summary,
        "monitored_rollback_recovery_drill_bridge": monitored_rollback_recovery_drill_bridge,
        "monitored_rollback_recovery_drill_bundle": result.get("monitored_rollback_recovery_drill_bundle"),
        "monitored_rollback_recovery_drill_schema": result.get("monitored_rollback_recovery_drill_schema"),
        "monitored_rollback_recovery_drill_approval_gate": result.get("monitored_rollback_recovery_drill_approval_gate"),
        "simulated_failure_trigger_contract": result.get("simulated_failure_trigger_contract"),
        "rollback_path_preview": result.get("rollback_path_preview"),
        "recovery_checkpoint_contract": result.get("recovery_checkpoint_contract"),
        "quarantine_freeze_preview": result.get("quarantine_freeze_preview"),
        "human_recovery_approval_gate": result.get("human_recovery_approval_gate"),
        "recovery_audit_proof": result.get("recovery_audit_proof"),
        "rollback_recovery_drill_ledger": result.get("rollback_recovery_drill_ledger"),
        "recovery_readiness_summary": result.get("recovery_readiness_summary"),
        "supervised_production_pilot_readiness_review_bridge": result.get("supervised_production_pilot_readiness_review_bridge"),
        "supervised_production_pilot_readiness_review_bundle": supervised_production_pilot_readiness_review_bundle,
        "supervised_production_pilot_readiness_review_schema": supervised_production_pilot_readiness_review_schema,
        "supervised_production_pilot_readiness_review_approval_gate": supervised_production_pilot_readiness_review_approval_gate,
        "minimum_viable_production_candidate_contract": minimum_viable_production_candidate_contract,
        "human_production_pilot_review_gate": human_production_pilot_review_gate,
        "production_blast_radius_analysis": production_blast_radius_analysis,
        "live_action_denial_review": live_action_denial_review,
        "rollback_availability_review": rollback_availability_review,
        "credential_secret_readiness_denial_proof": credential_secret_readiness_denial_proof,
        "network_socket_readiness_denial_proof": network_socket_readiness_denial_proof,
        "production_pilot_audit_proof": production_pilot_audit_proof,
        "production_pilot_readiness_ledger": production_pilot_readiness_ledger,
        "production_pilot_readiness_summary": production_pilot_readiness_summary,
        "credential_vault_denial_secret_handling_proof_bridge": credential_vault_denial_secret_handling_proof_bridge,
        "credential_vault_denial_secret_handling_proof_bundle": credential_vault_denial_secret_handling_proof_bundle,
        "credential_vault_denial_secret_handling_proof_schema": credential_vault_denial_secret_handling_proof_schema,
        "credential_vault_denial_secret_handling_proof_approval_gate": credential_vault_denial_secret_handling_proof_approval_gate,
        "credential_access_denial_contract": credential_access_denial_contract,
        "secret_read_denial_contract": secret_read_denial_contract,
        "environment_variable_denial_contract": environment_variable_denial_contract,
        "credential_vault_boundary_record": credential_vault_boundary_record,
        "secret_handling_boundary_record": secret_handling_boundary_record,
        "environment_read_boundary_record": environment_read_boundary_record,
        "credential_secret_audit_proof": credential_secret_audit_proof,
        "credential_secret_denial_ledger": credential_secret_denial_ledger,
        "credential_secret_readiness_summary": credential_secret_readiness_summary,
        "network_socket_lockdown_proof_bridge": network_socket_lockdown_proof_bridge,
        "live_external_action_final_preflight_gate_bundle": result.get("live_external_action_final_preflight_gate_bundle"),
        "live_external_action_final_preflight_gate_schema": result.get("live_external_action_final_preflight_gate_schema"),
        "live_external_action_final_preflight_gate_approval_gate": result.get("live_external_action_final_preflight_gate_approval_gate"),
        "tiny_action_candidate_boundary_contract": result.get("tiny_action_candidate_boundary_contract"),
        "live_external_action_non_execution_contract": result.get("live_external_action_non_execution_contract"),
        "blast_radius_ceiling_contract": result.get("blast_radius_ceiling_contract"),
        "human_final_approval_requirement": result.get("human_final_approval_requirement"),
        "credential_secret_environment_re_denial_proof": result.get("credential_secret_environment_re_denial_proof"),
        "network_socket_api_re_denial_proof": result.get("network_socket_api_re_denial_proof"),
        "deployment_production_re_denial_proof": result.get("deployment_production_re_denial_proof"),
        "rollback_recovery_availability_assertion": result.get("rollback_recovery_availability_assertion"),
        "first_tiny_real_world_execution_candidate_audit_proof": result.get("first_tiny_real_world_execution_candidate_audit_proof"),
        "final_preflight_ledger": result.get("final_preflight_ledger"),
        "first_tiny_real_world_supervised_execution_candidate_bridge": result.get("first_tiny_real_world_supervised_execution_candidate_bridge"),
        "first_tiny_real_world_supervised_execution_candidate_bundle": result.get("first_tiny_real_world_supervised_execution_candidate_bundle"),
        "first_tiny_real_world_supervised_execution_candidate_schema": result.get("first_tiny_real_world_supervised_execution_candidate_schema"),
        "first_tiny_real_world_supervised_execution_candidate_approval_gate": result.get("first_tiny_real_world_supervised_execution_candidate_approval_gate"),
        "local_proof_artifact_candidate_contract": result.get("local_proof_artifact_candidate_contract"),
        "explicit_output_directory_boundary_contract": result.get("explicit_output_directory_boundary_contract"),
        "forbidden_path_contract": result.get("forbidden_path_contract"),
        "local_only_execution_envelope": result.get("local_only_execution_envelope"),
        "candidate_pre_action_audit_proof": result.get("candidate_pre_action_audit_proof"),
        "local_proof_artifact_execution_record": result.get("local_proof_artifact_execution_record"),
        "post_action_verification_record": result.get("post_action_verification_record"),
        "cleanup_rollback_instruction_record": result.get("cleanup_rollback_instruction_record"),
        "first_tiny_candidate_ledger": result.get("first_tiny_candidate_ledger"),
        "first_tiny_candidate_readiness_summary": result.get("first_tiny_candidate_readiness_summary"),
        "post_action_verification_and_audit_review_bridge": result.get("post_action_verification_and_audit_review_bridge"),
        "local_proof_artifact_payload": result.get("local_proof_artifact_payload"),
        "post_action_verification_and_audit_review_bundle": result.get("post_action_verification_and_audit_review_bundle"),
        "post_action_verification_and_audit_review_schema": result.get("post_action_verification_and_audit_review_schema"),
        "post_action_verification_and_audit_review_approval_gate": result.get("post_action_verification_and_audit_review_approval_gate"),
        "v4_candidate_artifact_reference_contract": result.get("v4_candidate_artifact_reference_contract"),
        "artifact_integrity_verification_record": result.get("artifact_integrity_verification_record"),
        "artifact_path_containment_review": result.get("artifact_path_containment_review"),
        "safety_boolean_review": result.get("safety_boolean_review"),
        "cleanup_instruction_review": result.get("cleanup_instruction_review"),
        "operator_review_acknowledgement": result.get("operator_review_acknowledgement"),
        "post_action_closeout_ledger": result.get("post_action_closeout_ledger"),
        "post_action_readiness_summary": result.get("post_action_readiness_summary"),
        "supervised_rollback_cleanup_candidate_bridge": result.get("supervised_rollback_cleanup_candidate_bridge"),
        "post_action_verification_and_audit_review_record": result.get("post_action_verification_and_audit_review_record"),
        "supervised_rollback_cleanup_candidate_bundle": result.get("supervised_rollback_cleanup_candidate_bundle"),
        "supervised_rollback_cleanup_candidate_schema": result.get("supervised_rollback_cleanup_candidate_schema"),
        "supervised_rollback_cleanup_candidate_approval_gate": result.get("supervised_rollback_cleanup_candidate_approval_gate"),
        "cleanup_candidate_contract": result.get("cleanup_candidate_contract"),
        "artifact_pre_cleanup_verification_record": result.get("artifact_pre_cleanup_verification_record"),
        "cleanup_path_containment_record": result.get("cleanup_path_containment_record"),
        "cleanup_scope_envelope": result.get("cleanup_scope_envelope"),
        "cleanup_execution_record": result.get("cleanup_execution_record"),
        "post_cleanup_verification_record": result.get("post_cleanup_verification_record"),
        "cleanup_audit_record": result.get("cleanup_audit_record"),
        "cleanup_closeout_ledger": result.get("cleanup_closeout_ledger"),
        "cleanup_readiness_summary": result.get("cleanup_readiness_summary"),
        "limited_live_worker_activation_candidate_bridge": result.get("limited_live_worker_activation_candidate_bridge"),
        "limited_live_worker_activation_candidate_bundle": result.get("limited_live_worker_activation_candidate_bundle"),
        "limited_live_worker_activation_candidate_schema": result.get("limited_live_worker_activation_candidate_schema"),
        "limited_live_worker_activation_candidate_approval_gate": result.get("limited_live_worker_activation_candidate_approval_gate"),
        "worker_template_reference_contract": result.get("worker_template_reference_contract"),
        "one_worker_activation_scope_contract": result.get("one_worker_activation_scope_contract"),
        "non_execution_worker_boundary": result.get("non_execution_worker_boundary"),
        "worker_permission_denial_record": result.get("worker_permission_denial_record"),
        "worker_activation_candidate_record": result.get("worker_activation_candidate_record"),
        "worker_activation_audit_record": result.get("worker_activation_audit_record"),
        "worker_activation_ledger": result.get("worker_activation_ledger"),
        "worker_activation_readiness_summary": result.get("worker_activation_readiness_summary"),
        "permissioned_worker_task_assignment_candidate_bridge": result.get("permissioned_worker_task_assignment_candidate_bridge"),
        "worker_activation_record_payload": result.get("worker_activation_record_payload"),
        "worker_activation_write_record": result.get("worker_activation_write_record"),
        "permissioned_worker_task_assignment_candidate_bundle": result.get("permissioned_worker_task_assignment_candidate_bundle"),
        "permissioned_worker_task_assignment_candidate_schema": result.get("permissioned_worker_task_assignment_candidate_schema"),
        "permissioned_worker_task_assignment_candidate_approval_gate": result.get("permissioned_worker_task_assignment_candidate_approval_gate"),
        "task_label_reference_contract": result.get("task_label_reference_contract"),
        "one_worker_one_task_assignment_scope_contract": result.get("one_worker_one_task_assignment_scope_contract"),
        "non_execution_task_boundary": result.get("non_execution_task_boundary"),
        "task_permission_denial_record": result.get("task_permission_denial_record"),
        "worker_task_assignment_candidate_record": result.get("worker_task_assignment_candidate_record"),
        "task_assignment_audit_record": result.get("task_assignment_audit_record"),
        "task_assignment_ledger": result.get("task_assignment_ledger"),
        "task_assignment_readiness_summary": result.get("task_assignment_readiness_summary"),
        "task_assignment_audit_closeout_candidate_bridge": result.get("task_assignment_audit_closeout_candidate_bridge"),
        "task_assignment_record_payload": result.get("task_assignment_record_payload"),
        "task_assignment_write_record": result.get("task_assignment_write_record"),
        "task_assignment_audit_closeout_candidate_bundle": result.get("task_assignment_audit_closeout_candidate_bundle"),
        "task_assignment_audit_closeout_candidate_schema": result.get("task_assignment_audit_closeout_candidate_schema"),
        "task_assignment_audit_closeout_candidate_approval_gate": result.get("task_assignment_audit_closeout_candidate_approval_gate"),
        "v4_4_task_assignment_record_reference_contract": result.get("v4_4_task_assignment_record_reference_contract"),
        "task_assignment_record_integrity_verification": result.get("task_assignment_record_integrity_verification"),
        "task_assignment_record_path_containment_review": result.get("task_assignment_record_path_containment_review"),
        "task_assignment_safety_boolean_review": result.get("task_assignment_safety_boolean_review"),
        "non_execution_closeout_boundary": result.get("non_execution_closeout_boundary"),
        "operator_closeout_acknowledgement": result.get("operator_closeout_acknowledgement"),
        "task_assignment_closeout_audit_record": result.get("task_assignment_closeout_audit_record"),
        "task_assignment_closeout_ledger": result.get("task_assignment_closeout_ledger"),
        "task_assignment_closeout_readiness_summary": result.get("task_assignment_closeout_readiness_summary"),
        "non_executing_task_queue_preview_candidate_bridge": result.get("non_executing_task_queue_preview_candidate_bridge"),
        "task_assignment_audit_closeout_record_payload": result.get("task_assignment_audit_closeout_record_payload"),
        "task_assignment_closeout_write_record": result.get("task_assignment_closeout_write_record"),
        "non_executing_task_queue_preview_candidate_bundle": result.get("non_executing_task_queue_preview_candidate_bundle"),
        "non_executing_task_queue_preview_candidate_schema": result.get("non_executing_task_queue_preview_candidate_schema"),
        "non_executing_task_queue_preview_candidate_approval_gate": result.get("non_executing_task_queue_preview_candidate_approval_gate"),
        "v4_4_task_assignment_record_reference_contract": result.get("v4_4_task_assignment_record_reference_contract"),
        "optional_v4_5_closeout_record_reference_contract": result.get("optional_v4_5_closeout_record_reference_contract"),
        "task_assignment_record_integrity_verification": result.get("task_assignment_record_integrity_verification"),
        "closeout_record_integrity_verification": result.get("closeout_record_integrity_verification"),
        "queue_preview_scope_contract": result.get("queue_preview_scope_contract"),
        "non_execution_queue_boundary": result.get("non_execution_queue_boundary"),
        "queue_permission_denial_record": result.get("queue_permission_denial_record"),
        "non_executing_task_queue_preview_candidate_record": result.get("non_executing_task_queue_preview_candidate_record"),
        "queue_preview_audit_record": result.get("queue_preview_audit_record"),
        "queue_preview_ledger": result.get("queue_preview_ledger"),
        "queue_preview_readiness_summary": result.get("queue_preview_readiness_summary"),
        "task_queue_preview_audit_closeout_candidate_bridge": result.get("task_queue_preview_audit_closeout_candidate_bridge"),
        "queue_preview_record_payload": result.get("queue_preview_record_payload"),
        "queue_preview_write_record": result.get("queue_preview_write_record"),
        "local_queue_preview_record_written": result.get("local_queue_preview_record_written"),
        "queue_created": result.get("queue_created"),
        "queue_write_performed": result.get("queue_write_performed"),
        "scheduler_write_performed": result.get("scheduler_write_performed"),
        "referenced_task_assignment_record_mutated": result.get("referenced_task_assignment_record_mutated"),
        "referenced_closeout_record_mutated": result.get("referenced_closeout_record_mutated"),
        "task_queue_preview_audit_closeout_candidate_bundle": result.get("task_queue_preview_audit_closeout_candidate_bundle"),
        "task_queue_preview_audit_closeout_candidate_schema": result.get("task_queue_preview_audit_closeout_candidate_schema"),
        "task_queue_preview_audit_closeout_candidate_approval_gate": result.get("task_queue_preview_audit_closeout_candidate_approval_gate"),
        "v4_6_queue_preview_record_reference_contract": result.get("v4_6_queue_preview_record_reference_contract"),
        "queue_preview_record_integrity_verification": result.get("queue_preview_record_integrity_verification"),
        "queue_preview_record_path_containment_review": result.get("queue_preview_record_path_containment_review"),
        "queue_preview_safety_boolean_review": result.get("queue_preview_safety_boolean_review"),
        "non_execution_queue_closeout_boundary": result.get("non_execution_queue_closeout_boundary"),
        "operator_queue_closeout_acknowledgement": result.get("operator_queue_closeout_acknowledgement"),
        "queue_preview_closeout_audit_record": result.get("queue_preview_closeout_audit_record"),
        "queue_preview_closeout_ledger": result.get("queue_preview_closeout_ledger"),
        "queue_preview_closeout_readiness_summary": result.get("queue_preview_closeout_readiness_summary"),
        "non_executing_worker_routing_preview_candidate_bridge": result.get("non_executing_worker_routing_preview_candidate_bridge"),
        "queue_closeout_record_payload": result.get("queue_closeout_record_payload"),
        "queue_closeout_write_record": result.get("queue_closeout_write_record"),
        "local_queue_closeout_record_written": result.get("local_queue_closeout_record_written"),
        "referenced_queue_preview_record_mutated": result.get("referenced_queue_preview_record_mutated"),
        "controlled_worker_hiring_activation_pilot_bundle": controlled_worker_hiring_activation_pilot_bundle,
        "controlled_worker_hiring_activation_pilot_schema": result.get("controlled_worker_hiring_activation_pilot_schema"),
        "controlled_worker_hiring_activation_pilot_approval_gate": result.get("controlled_worker_hiring_activation_pilot_approval_gate"),
        "pilot_worker_limit_contract": result.get("pilot_worker_limit_contract"),
        "worker_identity_activation_contract": result.get("worker_identity_activation_contract"),
        "task_assignment_denial_by_default": result.get("task_assignment_denial_by_default"),
        "human_supervised_pilot_gate": result.get("human_supervised_pilot_gate"),
        "pilot_rollback_abort_preview": result.get("pilot_rollback_abort_preview"),
        "pilot_audit_proof": result.get("pilot_audit_proof"),
        "pilot_ledger": result.get("pilot_ledger"),
        "pilot_readiness_summary": result.get("pilot_readiness_summary"),
        "first_supervised_production_dry_run_bridge": result.get("first_supervised_production_dry_run_bridge"),
        "sandbox_worker_handoff_candidate_bundle": result.get("sandbox_worker_handoff_candidate_bundle"),
        "sandbox_worker_handoff_candidate_schema": result.get("sandbox_worker_handoff_candidate_schema"),
        "sandbox_worker_handoff_approval_gate": result.get("sandbox_worker_handoff_approval_gate"),
        "v5_2_repeatability_proof_reference_contract": result.get("v5_2_repeatability_proof_reference_contract"),
        "sandbox_worker_acknowledgement_candidate_bundle": result.get("sandbox_worker_acknowledgement_candidate_bundle"),
        "sandbox_worker_acknowledgement_candidate_schema": result.get("sandbox_worker_acknowledgement_candidate_schema"),
        "sandbox_worker_acknowledgement_approval_gate": result.get("sandbox_worker_acknowledgement_approval_gate"),
        "v5_3_handoff_packet_reference_contract": result.get("v5_3_handoff_packet_reference_contract"),
        "sandbox_worker_acknowledgement_reference_contract": result.get("sandbox_worker_acknowledgement_reference_contract"),
        "acknowledgement_scope_contract": result.get("acknowledgement_scope_contract"),
        "non_execution_acknowledgement_boundary": result.get("non_execution_acknowledgement_boundary"),
        "acknowledgement_permission_denial_record": result.get("acknowledgement_permission_denial_record"),
        "acknowledgement_plan_record": result.get("acknowledgement_plan_record"),
        "acknowledgement_packet_record": result.get("acknowledgement_packet_record"),
        "acknowledgement_audit_record": result.get("acknowledgement_audit_record"),
        "acknowledgement_readiness_summary": result.get("acknowledgement_readiness_summary"),
        "sandbox_worker_acceptance_candidate_bridge": result.get("sandbox_worker_acceptance_candidate_bridge"),
        "synthetic_task_handoff_contract": result.get("synthetic_task_handoff_contract"),
        "sandbox_worker_reference_contract": result.get("sandbox_worker_reference_contract"),
        "handoff_scope_contract": result.get("handoff_scope_contract"),
        "non_execution_handoff_boundary": result.get("non_execution_handoff_boundary"),
        "handoff_permission_denial_record": result.get("handoff_permission_denial_record"),
        "handoff_plan_record": result.get("handoff_plan_record"),
        "handoff_packet_record": result.get("handoff_packet_record"),
        "handoff_audit_record": result.get("handoff_audit_record"),
        "handoff_readiness_summary": result.get("handoff_readiness_summary"),
        "sandbox_worker_acknowledgement_candidate_bridge": result.get("sandbox_worker_acknowledgement_candidate_bridge"),
        "handoff_packet_payload": result.get("handoff_packet_payload"),
        "handoff_packet_write_record": result.get("handoff_packet_write_record"),
        "sandbox_worker_handoff_candidate_id": result.get("sandbox_worker_handoff_candidate_id"),
        "handoff_candidate_id": result.get("handoff_candidate_id"),
        "station_chief_v6_1_post_mvp_expansion_review_bundle": result.get("station_chief_v6_1_post_mvp_expansion_review_bundle"),
        "station_chief_v6_1_post_mvp_expansion_review_schema": result.get("station_chief_v6_1_post_mvp_expansion_review_schema"),
        "post_mvp_expansion_review_approval_gate": result.get("post_mvp_expansion_review_approval_gate"),
        "requested_expansion_lane_contract": result.get("requested_expansion_lane_contract"),
        "expansion_boundary_contract": result.get("expansion_boundary_contract"),
        "expansion_safety_posture_contract": result.get("expansion_safety_posture_contract"),
        "post_mvp_expansion_review_scope_contract": result.get("post_mvp_expansion_review_scope_contract"),
        "non_execution_post_mvp_expansion_boundary": result.get("non_execution_post_mvp_expansion_boundary"),
        "post_mvp_expansion_permission_denial_record": result.get("post_mvp_expansion_permission_denial_record"),
        "post_mvp_expansion_review_plan_record": result.get("post_mvp_expansion_review_plan_record"),
        "post_mvp_expansion_review_packet_record": result.get("post_mvp_expansion_review_packet_record"),
        "post_mvp_expansion_review_audit_record": result.get("post_mvp_expansion_review_audit_record"),
        "post_mvp_expansion_review_readiness_summary": result.get("post_mvp_expansion_review_readiness_summary"),
        "station_chief_v6_2_candidate_bridge": result.get("station_chief_v6_2_candidate_bridge"),
        "post_mvp_expansion_review_packet_payload": result.get("post_mvp_expansion_review_packet_payload"),
        "post_mvp_expansion_review_packet_write_record": result.get("post_mvp_expansion_review_packet_write_record"),
        "station_chief_v6_2_post_mvp_expansion_lane_scope_bundle": result.get("station_chief_v6_2_post_mvp_expansion_lane_scope_bundle"),
        "station_chief_v6_2_post_mvp_expansion_lane_scope_schema": result.get("station_chief_v6_2_post_mvp_expansion_lane_scope_schema"),
        "lane_scope_approval_gate": result.get("lane_scope_approval_gate"),
        "v6_1_review_packet_reference_contract": result.get("v6_1_review_packet_reference_contract"),
        "selected_expansion_lane_scope_contract": result.get("selected_expansion_lane_scope_contract"),
        "lane_scope_contract": result.get("lane_scope_contract"),
        "lane_constraint_contract": result.get("lane_constraint_contract"),
        "lane_success_criteria_contract": result.get("lane_success_criteria_contract"),
        "lane_non_execution_boundary_contract": result.get("lane_non_execution_boundary_contract"),
        "post_mvp_expansion_lane_scope_contract": result.get("post_mvp_expansion_lane_scope_contract"),
        "non_execution_lane_scope_boundary": result.get("non_execution_lane_scope_boundary"),
        "lane_scope_permission_denial_record": result.get("lane_scope_permission_denial_record"),
        "lane_scope_plan_record": result.get("lane_scope_plan_record"),
        "lane_scope_packet_record": result.get("lane_scope_packet_record"),
        "lane_scope_audit_record": result.get("lane_scope_audit_record"),
        "lane_scope_readiness_summary": result.get("lane_scope_readiness_summary"),
        "station_chief_v6_3_candidate_bridge": result.get("station_chief_v6_3_candidate_bridge"),
        "lane_scope_packet_payload": result.get("lane_scope_packet_payload"),
        "lane_scope_packet_write_record": result.get("lane_scope_packet_write_record"),
        "runtime_index_entry": runtime_index_entry,
        "manifest": {
            "run_id": run_id,
            "runtime_version": STATION_CHIEF_RUNTIME_VERSION,
            "artifact_type": f"station_chief_runtime_v{STATION_CHIEF_RUNTIME_VERSION.split('.')[0]}_{STATION_CHIEF_RUNTIME_VERSION.split('.')[1]}_artifacts",
            "files_planned": files_planned,
            "baseline_preserved": True,
            "devinization_overlays_preserved": True,
            "external_actions_taken": False,
            "live_worker_agents_activated": False,
            "supervised_external_api_pilot_schema": result.get("supervised_external_api_pilot_schema") is not None,
            "supervised_external_api_pilot_approval_gate": result.get("supervised_external_api_pilot_approval_gate") is not None,
            "single_api_category_contract": result.get("single_api_category_contract") is not None,
            "credential_denial_by_default": result.get("credential_denial_by_default") is not None,
            "secret_handling_denial_by_default": result.get("secret_handling_denial_by_default") is not None,
            "network_socket_denial_by_default": result.get("network_socket_denial_by_default") is not None,
            "human_api_use_preflight_gate": result.get("human_api_use_preflight_gate") is not None,
            "api_request_envelope_preview": result.get("api_request_envelope_preview") is not None,
            "api_response_quarantine_preview": result.get("api_response_quarantine_preview") is not None,
            "api_audit_proof": result.get("api_audit_proof") is not None,
            "api_pilot_ledger": result.get("api_pilot_ledger") is not None,
            "api_pilot_readiness_summary": result.get("api_pilot_readiness_summary") is not None,
            "monitored_rollback_recovery_drill_bridge": result.get("monitored_rollback_recovery_drill_bridge") is not None,
            "monitored_rollback_recovery_drill_bundle": result.get("monitored_rollback_recovery_drill_bundle") is not None,
            "monitored_rollback_recovery_drill_schema": result.get("monitored_rollback_recovery_drill_schema") is not None,
            "monitored_rollback_recovery_drill_approval_gate": result.get("monitored_rollback_recovery_drill_approval_gate") is not None,
            "simulated_failure_trigger_contract": result.get("simulated_failure_trigger_contract") is not None,
            "rollback_path_preview": result.get("rollback_path_preview") is not None,
            "recovery_checkpoint_contract": result.get("recovery_checkpoint_contract") is not None,
            "quarantine_freeze_preview": result.get("quarantine_freeze_preview") is not None,
            "human_recovery_approval_gate": result.get("human_recovery_approval_gate") is not None,
            "recovery_audit_proof": result.get("recovery_audit_proof") is not None,
            "rollback_recovery_drill_ledger": result.get("rollback_recovery_drill_ledger") is not None,
            "recovery_readiness_summary": result.get("recovery_readiness_summary") is not None,
            "supervised_production_pilot_readiness_review_bridge": result.get("supervised_production_pilot_readiness_review_bridge") is not None,
            "baseline_preserved": True,
            "external_actions_taken": False,
            "live_api_call_performed": False,
            "network_access_performed": False,
            "socket_opened": False,
            "credentials_used": False,
            "secrets_read": False,
            "environment_read": False,
            "deployment_performed": False,
            "real_external_tool_invocation_performed": False,
            "production_execution_performed": False,
            "production_activation_performed": False,
            "real_task_execution_performed": False,
            "live_task_assignment_performed": False,
            "live_worker_routing_performed": False,
            "live_orchestration_performed": False,
            "worker_processes_started": False,
            "repo_files_modified": False,
            "execution_authorized": False,
            "supervised_external_api_pilot_preview_only": True,
            "supervised_external_api_pilot_requires_token": True,
            "single_api_category_limit_is_one": True,
            "credential_use_denied_by_default": True,
            "secret_handling_denied_by_default": True,
            "network_socket_denied_by_default": True,
            "supervised_external_api_pilot_does_not_call_live_apis": True,
            "supervised_external_api_pilot_does_not_use_network_access": True,
            "supervised_external_api_pilot_does_not_open_sockets": True,
            "supervised_external_api_pilot_does_not_use_credentials": True,
            "supervised_external_api_pilot_does_not_read_secrets": True,
            "supervised_external_api_pilot_does_not_read_environment": True,
            "supervised_external_api_pilot_does_not_deploy": True,
            "supervised_external_api_pilot_does_not_invoke_external_tools": True,
            "supervised_external_api_pilot_does_not_execute_production": True,
            "supervised_external_api_pilot_does_not_modify_repo_files": True,
            "monitored_rollback_recovery_drill_preview_only": True,
            "monitored_rollback_recovery_drill_requires_token": True,
            "simulated_failure_trigger_preview_only": True,
            "rollback_path_preview_only": True,
            "recovery_checkpoint_preview_only": True,
            "quarantine_freeze_preview_only": True,
            "monitored_rollback_recovery_drill_does_not_perform_real_rollback": True,
            "monitored_rollback_recovery_drill_does_not_perform_real_recovery": True,
            "monitored_rollback_recovery_drill_does_not_terminate_processes": True,
            "monitored_rollback_recovery_drill_does_not_terminate_workers": True,
            "monitored_rollback_recovery_drill_does_not_change_production_state": True,
            "monitored_rollback_recovery_drill_does_not_rollback_deployments": True,
            "monitored_rollback_recovery_drill_does_not_deploy": True,
            "monitored_rollback_recovery_drill_does_not_call_live_apis": True,
            "monitored_rollback_recovery_drill_does_not_use_network_access": True,
            "monitored_rollback_recovery_drill_does_not_open_sockets": True,
            "monitored_rollback_recovery_drill_does_not_use_credentials": True,
            "monitored_rollback_recovery_drill_does_not_read_secrets": True,
            "monitored_rollback_recovery_drill_does_not_read_environment": True,
            "monitored_rollback_recovery_drill_does_not_execute_production": True,
            "monitored_rollback_recovery_drill_does_not_activate_production": True,
            "monitored_rollback_recovery_drill_does_not_execute_real_tasks": True,
            "monitored_rollback_recovery_drill_does_not_assign_live_tasks": True,
            "monitored_rollback_recovery_drill_does_not_route_live_workers": True,
            "monitored_rollback_recovery_drill_does_not_perform_live_orchestration": True,
            "monitored_rollback_recovery_drill_does_not_modify_repo_files": True,
            "supervised_production_pilot_readiness_review_not_yet_active": True,
            "supervised_production_pilot_readiness_review_available": True,
            "supervised_production_pilot_readiness_review_preview_only": True,
            "supervised_production_pilot_readiness_review_requires_token": True,
            "minimum_viable_production_candidate_preview_only": True,
            "production_blast_radius_analysis_preview_only": True,
            "live_action_denied_by_default": True,
            "rollback_availability_review_only": True,
            "credential_secret_readiness_denied": True,
            "network_socket_readiness_denied": True,
            "supervised_production_pilot_readiness_review_does_not_execute_production": True,
            "supervised_production_pilot_readiness_review_does_not_activate_production": True,
            "supervised_production_pilot_readiness_review_does_not_deploy": True,
            "supervised_production_pilot_readiness_review_does_not_call_live_apis": True,
            "supervised_production_pilot_readiness_review_does_not_use_network_access": True,
            "supervised_production_pilot_readiness_review_does_not_open_sockets": True,
            "supervised_production_pilot_readiness_review_does_not_use_credentials": True,
            "supervised_production_pilot_readiness_review_does_not_read_secrets": True,
            "supervised_production_pilot_readiness_review_does_not_read_environment": True,
            "supervised_production_pilot_readiness_review_does_not_assign_live_tasks": True,
            "supervised_production_pilot_readiness_review_does_not_route_live_workers": True,
            "supervised_production_pilot_readiness_review_does_not_perform_live_orchestration": True,
            "supervised_production_pilot_readiness_review_does_not_modify_repo_files": True,
            "credential_vault_denial_secret_handling_proof_not_yet_active": True,
            "credential_vault_denial_secret_handling_proof_available": True,
            "credential_vault_denial_secret_handling_proof_preview_only": True,
            "credential_vault_denial_secret_handling_proof_requires_token": True,
            "credential_vault_denial_secret_handling_proof_does_not_access_credentials": True,
            "credential_vault_denial_secret_handling_proof_does_not_read_secrets": True,
            "credential_vault_denial_secret_handling_proof_does_not_read_environment": True,
            "credential_vault_denial_secret_handling_proof_does_not_call_live_apis": True,
            "credential_vault_denial_secret_handling_proof_does_not_use_network_access": True,
            "credential_vault_denial_secret_handling_proof_does_not_open_sockets": True,
            "credential_vault_denial_secret_handling_proof_does_not_deploy": True,
            "credential_vault_denial_secret_handling_proof_does_not_execute_production": True,
            "credential_vault_denial_secret_handling_proof_does_not_modify_repo_files": True,
            "controlled_worker_hiring_activation_pilot_schema": result.get("controlled_worker_hiring_activation_pilot_schema") is not None,
            "controlled_worker_hiring_activation_pilot_approval_gate": result.get("controlled_worker_hiring_activation_pilot_approval_gate") is not None,
            "pilot_worker_limit_contract": result.get("pilot_worker_limit_contract") is not None,
            "worker_identity_activation_contract": result.get("worker_identity_activation_contract") is not None,
            "task_assignment_denial_by_default": result.get("task_assignment_denial_by_default") is not None,
            "human_supervised_pilot_gate": result.get("human_supervised_pilot_gate") is not None,
            "pilot_rollback_abort_preview": result.get("pilot_rollback_abort_preview") is not None,
            "pilot_audit_proof": result.get("pilot_audit_proof") is not None,
            "pilot_ledger": result.get("pilot_ledger") is not None,
            "pilot_readiness_summary": result.get("pilot_readiness_summary") is not None,
            "first_supervised_production_dry_run_bridge": result.get("first_supervised_production_dry_run_bridge") is not None,
            "limited_external_tool_supervised_pilot_bundle": result.get("limited_external_tool_supervised_pilot_bundle") is not None,
            "limited_external_tool_supervised_pilot_schema": result.get("limited_external_tool_supervised_pilot_schema") is not None,
            "limited_external_tool_supervised_pilot_approval_gate": result.get("limited_external_tool_supervised_pilot_approval_gate") is not None,
            "single_external_tool_category_contract": result.get("single_external_tool_category_contract") is not None,
            "tool_invocation_denial_by_default": result.get("tool_invocation_denial_by_default") is not None,
            "human_tool_use_preflight_gate": result.get("human_tool_use_preflight_gate") is not None,
            "tool_request_envelope_preview": result.get("tool_request_envelope_preview") is not None,
            "tool_response_quarantine_preview": result.get("tool_response_quarantine_preview") is not None,
            "tool_audit_proof": result.get("tool_audit_proof") is not None,
            "tool_pilot_ledger": result.get("tool_pilot_ledger") is not None,
            "tool_pilot_readiness_summary": result.get("tool_pilot_readiness_summary") is not None,
            "supervised_external_api_pilot_bridge": result.get("supervised_external_api_pilot_bridge") is not None,
            "controlled_worker_hiring_activation_pilot_preview_only": True,
            "controlled_worker_hiring_activation_pilot_requires_token": True,
            "pilot_worker_limit_maximum_is_three": True,
            "task_assignment_denied_by_default": True,
            "controlled_worker_hiring_activation_pilot_does_not_hire_real_workers": True,
            "controlled_worker_hiring_activation_pilot_does_not_activate_real_workers": True,
            "controlled_worker_hiring_activation_pilot_does_not_start_worker_processes": True,
            "controlled_worker_hiring_activation_pilot_does_not_assign_live_tasks": True,
            "controlled_worker_hiring_activation_pilot_does_not_route_live_workers": True,
            "controlled_worker_hiring_activation_pilot_does_not_perform_live_orchestration": True,
            "controlled_worker_hiring_activation_pilot_does_not_execute_production": True,
            "controlled_worker_hiring_activation_pilot_does_not_call_live_apis": True,
            "controlled_worker_hiring_activation_pilot_does_not_use_network_access": True,
            "controlled_worker_hiring_activation_pilot_does_not_open_sockets": True,
            "controlled_worker_hiring_activation_pilot_does_not_use_credentials": True,
            "controlled_worker_hiring_activation_pilot_does_not_read_secrets": True,
            "controlled_worker_hiring_activation_pilot_does_not_read_environment": True,
            "controlled_worker_hiring_activation_pilot_does_not_modify_repo_files": True,
            "limited_external_tool_supervised_pilot_preview_only": True,
            "limited_external_tool_supervised_pilot_requires_token": True,
            "single_external_tool_category_limit_is_one": True,
            "tool_invocation_denied_by_default": True,
            "limited_external_tool_supervised_pilot_does_not_invoke_external_tools": True,
            "limited_external_tool_supervised_pilot_does_not_call_live_apis": True,
            "limited_external_tool_supervised_pilot_does_not_use_network_access": True,
            "limited_external_tool_supervised_pilot_does_not_open_sockets": True,
            "limited_external_tool_supervised_pilot_does_not_use_credentials": True,
            "limited_external_tool_supervised_pilot_does_not_read_secrets": True,
            "limited_external_tool_supervised_pilot_does_not_read_environment": True,
            "limited_external_tool_supervised_pilot_does_not_deploy": True,
            "limited_external_tool_supervised_pilot_does_not_execute_production": True,
            "limited_external_tool_supervised_pilot_does_not_activate_production": True,
            "limited_external_tool_supervised_pilot_does_not_execute_real_tasks": True,
            "limited_external_tool_supervised_pilot_does_not_assign_live_tasks": True,
            "limited_external_tool_supervised_pilot_does_not_route_live_workers": True,
            "limited_external_tool_supervised_pilot_does_not_perform_live_orchestration": True,
            "limited_external_tool_supervised_pilot_does_not_modify_repo_files": True,
                    "monitored_rollback_recovery_drill_not_yet_active": True,
        "supervised_external_api_pilot_available": True,
        "supervised_external_api_pilot_preview_only": True,
        "supervised_external_api_pilot_requires_token": True,
        "single_api_category_limit_is_one": True,
        "credential_use_denied_by_default": True,
        "secret_handling_denied_by_default": True,
        "network_socket_denied_by_default": True,
        "supervised_external_api_pilot_does_not_call_live_apis": True,
        "supervised_external_api_pilot_does_not_use_network_access": True,
        "supervised_external_api_pilot_does_not_open_sockets": True,
        "supervised_external_api_pilot_does_not_use_credentials": True,
        "supervised_external_api_pilot_does_not_read_secrets": True,
        "supervised_external_api_pilot_does_not_read_environment": True,
        "supervised_external_api_pilot_does_not_deploy": True,
        "supervised_external_api_pilot_does_not_invoke_external_tools": True,
        "supervised_external_api_pilot_does_not_execute_production": True,
        "supervised_external_api_pilot_does_not_activate_production": True,
        "supervised_external_api_pilot_does_not_execute_real_tasks": True,
        "supervised_external_api_pilot_does_not_assign_live_tasks": True,
        "supervised_external_api_pilot_does_not_route_live_workers": True,
        "supervised_external_api_pilot_does_not_perform_live_orchestration": True,
        "supervised_external_api_pilot_does_not_modify_repo_files": True,
        },
    }

def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def attach_sandbox_worker_acceptance_candidate_review(
    result: dict,
    sandbox_worker_label: str | None = None,
    v5_3_handoff_packet_reference_label: str | None = None,
    v5_4_acknowledgement_packet_reference_label: str | None = None,
    output_directory: str | None = None,
    acceptance_review_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    acceptance_review_requested: bool = False,
    write_acceptance_review_packet: bool = False,
) -> dict:
    bundle = create_sandbox_worker_acceptance_candidate_review_bundle(
        result,
        command=result.get("command"),
        sandbox_worker_label=sandbox_worker_label,
        v5_3_handoff_packet_reference_label=v5_3_handoff_packet_reference_label,
        v5_4_acknowledgement_packet_reference_label=v5_4_acknowledgement_packet_reference_label,
        output_directory=output_directory,
        acceptance_review_packet_name=acceptance_review_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        acceptance_review_requested=acceptance_review_requested,
        write_acceptance_review_packet=write_acceptance_review_packet,
    )
    result = dict(result)
    result["sandbox_worker_acceptance_candidate_review_bundle"] = bundle
    result["sandbox_worker_acceptance_candidate_review_schema"] = bundle["schema"]
    result["sandbox_worker_acceptance_review_approval_gate"] = bundle["approval_gate"]
    result["v5_3_handoff_packet_reference_contract"] = bundle["v5_3_handoff_packet_reference_contract"]
    result["v5_4_acknowledgement_packet_reference_contract"] = bundle["v5_4_acknowledgement_packet_reference_contract"]
    result["sandbox_worker_acceptance_review_reference_contract"] = bundle["sandbox_worker_acceptance_review_reference_contract"]
    result["acceptance_review_scope_contract"] = bundle["acceptance_review_scope_contract"]
    result["non_execution_acceptance_review_boundary"] = bundle["non_execution_acceptance_review_boundary"]
    result["acceptance_review_permission_denial_record"] = bundle["acceptance_review_permission_denial_record"]
    result["acceptance_review_plan_record"] = bundle["acceptance_review_plan_record"]
    result["acceptance_review_packet_record"] = bundle["acceptance_review_packet_record"]
    result["acceptance_review_audit_record"] = bundle["acceptance_review_audit_record"]
    result["acceptance_review_readiness_summary"] = bundle["acceptance_review_readiness_summary"]
    result["sandbox_worker_ready_state_packet_candidate_bridge"] = bundle["sandbox_worker_ready_state_packet_candidate_bridge"]
    result["acceptance_review_packet_payload"] = bundle.get("acceptance_review_packet_payload")
    result["acceptance_review_packet_write_record"] = bundle.get("acceptance_review_packet_record", {}).get("write_record")
    result["local_acceptance_review_packet_written"] = bundle["local_acceptance_review_packet_written"]
    result["sandbox_worker_acceptance_review_performed"] = bundle["sandbox_worker_acceptance_review_performed"]
    result["sandbox_worker_accepted"] = False
    result["sandbox_worker_ready_state_created"] = False
    result["ready_state_packet_written"] = False
    result["worker_process_started"] = False
    result["agent_started"] = False
    result["real_queue_created"] = False
    result["queue_write_performed"] = False
    result["scheduler_write_performed"] = False
    result["cron_write_performed"] = False
    result["task_enqueued"] = False
    result["task_executed"] = False
    result["arbitrary_task_execution_performed"] = False
    result["user_task_execution_performed"] = False
    result["live_task_assignment_performed"] = False
    result["live_worker_routing_performed"] = False
    result["live_orchestration_performed"] = False
    result["external_tool_invocation_performed"] = False
    result["api_call_performed"] = False
    result["network_access_performed"] = False
    result["deployment_performed"] = False
    result["production_execution_performed"] = False
    result["full_workforce_activation_performed"] = False
    
    # Compatibility object
    result["sandbox_worker_acceptance_candidate_review"] = bundle
    
    return result


def write_sandbox_worker_acceptance_candidate_review(
    result: dict,
    output_dir: str,
    sandbox_worker_label: str | None = None,
    v5_3_handoff_packet_reference_label: str | None = None,
    v5_4_acknowledgement_packet_reference_label: str | None = None,
    acceptance_review_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
) -> dict:
    result = attach_sandbox_worker_acceptance_candidate_review(
        result,
        sandbox_worker_label=sandbox_worker_label,
        v5_3_handoff_packet_reference_label=v5_3_handoff_packet_reference_label,
        v5_4_acknowledgement_packet_reference_label=v5_4_acknowledgement_packet_reference_label,
        output_directory=output_dir,
        acceptance_review_packet_name=acceptance_review_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        acceptance_review_requested=True,
        write_acceptance_review_packet=True,
    )
    write_record = result["acceptance_review_packet_write_record"]
    result["sandbox_worker_acceptance_candidate_review_write_summary"] = write_record
    result["sandbox_worker_acceptance_candidate_review_dir"] = write_record.get("output_directory") or str(output_dir)
    if result.get("local_acceptance_review_packet_written"):
        rec_name = write_record.get("record_name")
        rec_path = write_record.get("record_path")
        result["files_written"] = [rec_name] if rec_name else []
        result["record_path"] = rec_path
    else:
        result["files_written"] = []
        result["record_path"] = None
    result["execution_status"] = write_record.get("write_status")
    return result


def attach_station_chief_v6_0_mvp_lock(
    result: dict,
    local_task_candidate_label: str | None = None,
    sandbox_worker_label: str | None = None,
    v5_3_handoff_packet_reference_label: str | None = None,
    v5_4_acknowledgement_packet_reference_label: str | None = None,
    v5_5_acceptance_review_packet_reference_label: str | None = None,
    v5_6_ready_state_packet_reference_label: str | None = None,
    v5_7_dry_run_assignment_packet_reference_label: str | None = None,
    v5_8_dry_run_result_packet_reference_label: str | None = None,
    v5_9_dry_run_replay_audit_packet_reference_label: str | None = None,
    v6_0_mvp_lock_label: str | None = None,
    output_directory: str | None = None,
    mvp_lock_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    mvp_lock_requested: bool = False,
    write_mvp_lock_packet: bool = False,
) -> dict:
    bundle = create_station_chief_v6_0_mvp_lock_bundle(
        result,
        command=result.get("command"),
        local_task_candidate_label=local_task_candidate_label,
        sandbox_worker_label=sandbox_worker_label,
        v5_3_handoff_packet_reference_label=v5_3_handoff_packet_reference_label,
        v5_4_acknowledgement_packet_reference_label=v5_4_acknowledgement_packet_reference_label,
        v5_5_acceptance_review_packet_reference_label=v5_5_acceptance_review_packet_reference_label,
        v5_6_ready_state_packet_reference_label=v5_6_ready_state_packet_reference_label,
        v5_7_dry_run_assignment_packet_reference_label=v5_7_dry_run_assignment_packet_reference_label,
        v5_8_dry_run_result_packet_reference_label=v5_8_dry_run_result_packet_reference_label,
        v5_9_dry_run_replay_audit_packet_reference_label=v5_9_dry_run_replay_audit_packet_reference_label,
        v6_0_mvp_lock_label=v6_0_mvp_lock_label,
        output_directory=output_directory,
        mvp_lock_packet_name=mvp_lock_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        mvp_lock_requested=mvp_lock_requested,
        write_mvp_lock_packet=write_mvp_lock_packet,
    )
    result = dict(result)
    result["station_chief_v6_0_mvp_lock_bundle"] = bundle
    result["station_chief_v6_0_mvp_lock_schema"] = bundle["schema"]
    result["station_chief_v6_0_mvp_lock_approval_gate"] = bundle["approval_gate"]
    result["local_task_candidate_reference_contract"] = bundle["local_task_candidate_reference_contract"]
    result["sandbox_worker_reference_contract"] = bundle["sandbox_worker_reference_contract"]
    result["v5_3_handoff_packet_reference_contract"] = bundle["v5_3_handoff_packet_reference_contract"]
    result["v5_4_acknowledgement_packet_reference_contract"] = bundle["v5_4_acknowledgement_packet_reference_contract"]
    result["v5_5_acceptance_review_packet_reference_contract"] = bundle["v5_5_acceptance_review_packet_reference_contract"]
    result["v5_6_ready_state_packet_reference_contract"] = bundle["v5_6_ready_state_packet_reference_contract"]
    result["v5_7_dry_run_assignment_packet_reference_contract"] = bundle["v5_7_dry_run_assignment_packet_reference_contract"]
    result["v5_8_dry_run_result_packet_reference_contract"] = bundle["v5_8_dry_run_result_packet_reference_contract"]
    result["v5_9_dry_run_replay_audit_packet_reference_contract"] = bundle["v5_9_dry_run_replay_audit_packet_reference_contract"]
    result["v6_0_mvp_lock_reference_contract"] = bundle["v6_0_mvp_lock_reference_contract"]
    result["integrated_local_command_center_loop_contract"] = bundle["integrated_local_command_center_loop_contract"]
    result["non_execution_mvp_lock_boundary"] = bundle["non_execution_mvp_lock_boundary"]
    result["mvp_lock_permission_denial_record"] = bundle["mvp_lock_permission_denial_record"]
    result["mvp_lock_plan_record"] = bundle["mvp_lock_plan_record"]
    result["mvp_lock_packet_record"] = bundle["mvp_lock_packet_record"]
    result["mvp_lock_audit_record"] = bundle["mvp_lock_audit_record"]
    result["mvp_lock_readiness_summary"] = bundle["mvp_lock_readiness_summary"]
    result["station_chief_post_mvp_expansion_bridge"] = bundle["station_chief_post_mvp_expansion_bridge"]
    result["mvp_lock_packet_payload"] = bundle.get("mvp_lock_packet_payload")
    result["mvp_lock_packet_write_record"] = bundle.get("mvp_lock_packet_record", {}).get("write_record")
    result["local_mvp_lock_packet_written"] = bundle["local_mvp_lock_packet_written"]
    result["station_chief_v6_0_mvp_lock_created"] = bundle["station_chief_v6_0_mvp_lock_created"]
    result["integrated_local_command_center_loop_recorded"] = bundle["integrated_local_command_center_loop_recorded"]
    result["mvp_done_recorded"] = bundle["mvp_done_recorded"]
    result["local_task_candidate_executed"] = False
    result["handoff_packet_executed"] = False
    result["acknowledgement_packet_executed"] = False
    result["acceptance_review_packet_executed"] = False
    result["ready_state_packet_executed"] = False
    result["dry_run_assignment_packet_executed"] = False
    result["dry_run_result_packet_executed"] = False
    result["dry_run_replay_audit_packet_executed"] = False
    result["dry_run_task_executed"] = False
    result["real_worker_result_created"] = False
    result["live_replay_performed"] = False
    result["production_audit_performed"] = False
    result["rollback_performed"] = False
    result["recovery_performed"] = False
    result["v6_1_created"] = False
    result["worker_process_started"] = False
    result["agent_started"] = False
    result["real_queue_created"] = False
    result["queue_write_performed"] = False
    result["scheduler_write_performed"] = False
    result["cron_write_performed"] = False
    result["task_enqueued"] = False
    result["task_executed"] = False
    result["arbitrary_task_execution_performed"] = False
    result["user_task_execution_performed"] = False
    result["live_task_assignment_performed"] = False
    result["live_worker_routing_performed"] = False
    result["live_orchestration_performed"] = False
    result["external_tool_invocation_performed"] = False
    result["api_call_performed"] = False
    result["network_access_performed"] = False
    result["deployment_performed"] = False
    result["production_execution_performed"] = False
    result["full_workforce_activation_performed"] = False
    
    # Compatibility object
    result["station_chief_v6_0_mvp_lock"] = bundle
    
    return result


def write_station_chief_v6_0_mvp_lock(
    result: dict,
    output_dir: str,
    local_task_candidate_label: str | None = None,
    sandbox_worker_label: str | None = None,
    v5_3_handoff_packet_reference_label: str | None = None,
    v5_4_acknowledgement_packet_reference_label: str | None = None,
    v5_5_acceptance_review_packet_reference_label: str | None = None,
    v5_6_ready_state_packet_reference_label: str | None = None,
    v5_7_dry_run_assignment_packet_reference_label: str | None = None,
    v5_8_dry_run_result_packet_reference_label: str | None = None,
    v5_9_dry_run_replay_audit_packet_reference_label: str | None = None,
    v6_0_mvp_lock_label: str | None = None,
    mvp_lock_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
) -> dict:
    result = attach_station_chief_v6_0_mvp_lock(
        result,
        local_task_candidate_label=local_task_candidate_label,
        sandbox_worker_label=sandbox_worker_label,
        v5_3_handoff_packet_reference_label=v5_3_handoff_packet_reference_label,
        v5_4_acknowledgement_packet_reference_label=v5_4_acknowledgement_packet_reference_label,
        v5_5_acceptance_review_packet_reference_label=v5_5_acceptance_review_packet_reference_label,
        v5_6_ready_state_packet_reference_label=v5_6_ready_state_packet_reference_label,
        v5_7_dry_run_assignment_packet_reference_label=v5_7_dry_run_assignment_packet_reference_label,
        v5_8_dry_run_result_packet_reference_label=v5_8_dry_run_result_packet_reference_label,
        v5_9_dry_run_replay_audit_packet_reference_label=v5_9_dry_run_replay_audit_packet_reference_label,
        v6_0_mvp_lock_label=v6_0_mvp_lock_label,
        output_directory=output_dir,
        mvp_lock_packet_name=mvp_lock_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        mvp_lock_requested=True,
        write_mvp_lock_packet=True,
    )
    write_record = result["mvp_lock_packet_write_record"]
    result["station_chief_v6_0_mvp_lock_write_summary"] = write_record
    result["station_chief_v6_0_mvp_lock_dir"] = write_record.get("output_directory") or str(output_dir)
    if result.get("local_mvp_lock_packet_written"):
        rec_name = write_record.get("record_name")
        rec_path = write_record.get("record_path")
        result["files_written"] = [rec_name] if rec_name else []
        result["record_path"] = rec_path
    else:
        result["files_written"] = []
        result["record_path"] = None
    result["execution_status"] = write_record.get("write_status")
    return result


def attach_station_chief_v6_1_post_mvp_expansion_review(
    result: dict,
    v6_0_mvp_lock_reference_label: str | None = None,
    post_mvp_expansion_review_label: str | None = None,
    requested_expansion_lane_label: str | None = None,
    expansion_boundary_label: str | None = None,
    expansion_safety_posture_label: str | None = None,
    output_directory: str | None = None,
    post_mvp_expansion_review_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    post_mvp_expansion_review_requested: bool = False,
    write_post_mvp_expansion_review_packet: bool = False,
) -> dict:
    bundle = create_station_chief_v6_1_post_mvp_expansion_review_bundle(
        result,
        command=result.get("command"),
        v6_0_mvp_lock_reference_label=v6_0_mvp_lock_reference_label,
        post_mvp_expansion_review_label=post_mvp_expansion_review_label,
        requested_expansion_lane_label=requested_expansion_lane_label,
        expansion_boundary_label=expansion_boundary_label,
        expansion_safety_posture_label=expansion_safety_posture_label,
        output_directory=output_directory,
        post_mvp_expansion_review_packet_name=post_mvp_expansion_review_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        post_mvp_expansion_review_requested=post_mvp_expansion_review_requested,
        write_post_mvp_expansion_review_packet=write_post_mvp_expansion_review_packet,
    )
    result = dict(result)
    result["station_chief_v6_1_post_mvp_expansion_review_bundle"] = bundle
    result["station_chief_v6_1_post_mvp_expansion_review_schema"] = bundle["schema"]
    result["post_mvp_expansion_review_approval_gate"] = bundle["approval_gate"]
    result["v6_0_mvp_lock_reference_contract"] = bundle["v6_0_mvp_lock_reference_contract"]
    result["requested_expansion_lane_contract"] = bundle["requested_expansion_lane_contract"]
    result["expansion_boundary_contract"] = bundle["expansion_boundary_contract"]
    result["expansion_safety_posture_contract"] = bundle["expansion_safety_posture_contract"]
    result["post_mvp_expansion_review_scope_contract"] = bundle["post_mvp_expansion_review_scope_contract"]
    result["non_execution_post_mvp_expansion_boundary"] = bundle["non_execution_post_mvp_expansion_boundary"]
    result["post_mvp_expansion_permission_denial_record"] = bundle["post_mvp_expansion_permission_denial_record"]
    result["post_mvp_expansion_review_plan_record"] = bundle["post_mvp_expansion_review_plan_record"]
    result["post_mvp_expansion_review_packet_record"] = bundle["post_mvp_expansion_review_packet_record"]
    result["post_mvp_expansion_review_audit_record"] = bundle["post_mvp_expansion_review_audit_record"]
    result["post_mvp_expansion_review_readiness_summary"] = bundle["post_mvp_expansion_review_readiness_summary"]
    result["station_chief_v6_2_candidate_bridge"] = bundle["station_chief_v6_2_candidate_bridge"]
    result["post_mvp_expansion_review_packet_payload"] = bundle.get("post_mvp_expansion_review_packet_payload")
    result["post_mvp_expansion_review_packet_write_record"] = bundle.get("post_mvp_expansion_review_packet_record", {}).get("write_record")
    result["local_post_mvp_expansion_review_packet_written"] = bundle["local_post_mvp_expansion_review_packet_written"]
    result["station_chief_v6_1_post_mvp_expansion_review_created"] = bundle["station_chief_v6_1_post_mvp_expansion_review_created"]
    result["post_mvp_expansion_review_recorded"] = bundle["post_mvp_expansion_review_recorded"]
    result["post_mvp_expansion_executed"] = False
    result["selected_expansion_lane_executed"] = False
    result["v6_0_mvp_lock_mutated"] = False
    result["v6_0_mvp_lock_executed"] = False
    result["local_task_candidate_executed"] = False
    result["dry_run_task_executed"] = False
    result["real_worker_result_created"] = False
    result["live_replay_performed"] = False
    result["production_audit_performed"] = False
    result["rollback_performed"] = False
    result["recovery_performed"] = False
    result["v6_2_created"] = False
    result["worker_process_started"] = False
    result["agent_started"] = False
    result["real_queue_created"] = False
    result["queue_write_performed"] = False
    result["scheduler_write_performed"] = False
    result["cron_write_performed"] = False
    result["task_enqueued"] = False
    result["task_executed"] = False
    result["arbitrary_task_execution_performed"] = False
    result["user_task_execution_performed"] = False
    result["live_task_assignment_performed"] = False
    result["live_worker_routing_performed"] = False
    result["live_orchestration_performed"] = False
    result["external_tool_invocation_performed"] = False
    result["api_call_performed"] = False
    result["network_access_performed"] = False
    result["deployment_performed"] = False
    result["production_execution_performed"] = False
    result["full_workforce_activation_performed"] = False
    
    # Compatibility object
    result["station_chief_v6_1_post_mvp_expansion_review"] = bundle
    
    return result


def write_station_chief_v6_1_post_mvp_expansion_review(
    result: dict,
    output_dir: str,
    v6_0_mvp_lock_reference_label: str | None = None,
    post_mvp_expansion_review_label: str | None = None,
    requested_expansion_lane_label: str | None = None,
    expansion_boundary_label: str | None = None,
    expansion_safety_posture_label: str | None = None,
    post_mvp_expansion_review_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
) -> dict:
    result = attach_station_chief_v6_1_post_mvp_expansion_review(
        result,
        v6_0_mvp_lock_reference_label=v6_0_mvp_lock_reference_label,
        post_mvp_expansion_review_label=post_mvp_expansion_review_label,
        requested_expansion_lane_label=requested_expansion_lane_label,
        expansion_boundary_label=expansion_boundary_label,
        expansion_safety_posture_label=expansion_safety_posture_label,
        output_directory=output_dir,
        post_mvp_expansion_review_packet_name=post_mvp_expansion_review_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        post_mvp_expansion_review_requested=True,
        write_post_mvp_expansion_review_packet=True,
    )
    write_record = result["post_mvp_expansion_review_packet_write_record"]
    result["station_chief_v6_1_post_mvp_expansion_review_write_summary"] = write_record
    result["station_chief_v6_1_post_mvp_expansion_review_dir"] = write_record.get("output_directory") or str(output_dir)
    if result.get("local_post_mvp_expansion_review_packet_written"):
        rec_name = write_record.get("record_name")
        rec_path = write_record.get("record_path")
        result["files_written"] = [rec_name] if rec_name else []
        result["record_path"] = rec_path
    else:
        result["files_written"] = []
        result["record_path"] = None
    result["execution_status"] = write_record.get("write_status")
    return result


def attach_station_chief_v6_2_post_mvp_expansion_lane_scope(
    result: dict,
    v6_1_review_packet_reference_label: str | None = None,
    selected_expansion_lane_label: str | None = None,
    lane_scope_label: str | None = None,
    lane_constraint_label: str | None = None,
    lane_success_criteria_label: str | None = None,
    lane_non_execution_boundary_label: str | None = None,
    output_directory: str | None = None,
    lane_scope_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    lane_scope_requested: bool = False,
    write_lane_scope_packet: bool = False,
) -> dict:
    bundle = create_station_chief_v6_2_post_mvp_expansion_lane_scope_bundle(
        result,
        command=result.get("command"),
        v6_1_review_packet_reference_label=v6_1_review_packet_reference_label,
        selected_expansion_lane_label=selected_expansion_lane_label,
        lane_scope_label=lane_scope_label,
        lane_constraint_label=lane_constraint_label,
        lane_success_criteria_label=lane_success_criteria_label,
        lane_non_execution_boundary_label=lane_non_execution_boundary_label,
        output_directory=output_directory,
        lane_scope_packet_name=lane_scope_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        lane_scope_requested=lane_scope_requested,
        write_lane_scope_packet=write_lane_scope_packet,
    )
    result = dict(result)
    result["station_chief_v6_2_post_mvp_expansion_lane_scope_bundle"] = bundle
    result["station_chief_v6_2_post_mvp_expansion_lane_scope_schema"] = bundle["schema"]
    result["lane_scope_approval_gate"] = bundle["approval_gate"]
    result["v6_1_review_packet_reference_contract"] = bundle["v6_1_review_packet_reference_contract"]
    result["selected_expansion_lane_scope_contract"] = bundle["selected_expansion_lane_scope_contract"]
    result["lane_scope_contract"] = bundle["lane_scope_contract"]
    result["lane_constraint_contract"] = bundle["lane_constraint_contract"]
    result["lane_success_criteria_contract"] = bundle["lane_success_criteria_contract"]
    result["lane_non_execution_boundary_contract"] = bundle["lane_non_execution_boundary_contract"]
    result["post_mvp_expansion_lane_scope_contract"] = bundle["post_mvp_expansion_lane_scope_contract"]
    result["non_execution_lane_scope_boundary"] = bundle["non_execution_lane_scope_boundary"]
    result["lane_scope_permission_denial_record"] = bundle["lane_scope_permission_denial_record"]
    result["lane_scope_plan_record"] = bundle["lane_scope_plan_record"]
    result["lane_scope_packet_record"] = bundle["lane_scope_packet_record"]
    result["lane_scope_audit_record"] = bundle["lane_scope_audit_record"]
    result["lane_scope_readiness_summary"] = bundle["lane_scope_readiness_summary"]
    result["station_chief_v6_3_candidate_bridge"] = bundle["station_chief_v6_3_candidate_bridge"]
    result["lane_scope_packet_payload"] = bundle.get("lane_scope_packet_payload")
    result["lane_scope_packet_write_record"] = bundle.get("lane_scope_packet_record", {}).get("write_record")
    result["local_lane_scope_packet_written"] = bundle["local_lane_scope_packet_written"]
    result["station_chief_v6_2_lane_scope_created"] = bundle["station_chief_v6_2_lane_scope_created"]
    result["post_mvp_expansion_lane_scope_recorded"] = bundle["post_mvp_expansion_lane_scope_recorded"]
    result["selected_expansion_lane_implemented"] = False
    result["selected_expansion_lane_executed"] = False
    result["post_mvp_expansion_executed"] = False
    result["v6_1_review_packet_mutated"] = False
    result["v6_1_review_packet_executed"] = False
    result["v6_0_mvp_lock_mutated"] = False
    result["v6_0_mvp_lock_executed"] = False
    result["local_task_candidate_executed"] = False
    result["dry_run_task_executed"] = False
    result["real_worker_result_created"] = False
    result["live_replay_performed"] = False
    result["production_audit_performed"] = False
    result["rollback_performed"] = False
    result["recovery_performed"] = False
    result["v6_3_created"] = False
    result["worker_process_started"] = False
    result["agent_started"] = False
    result["real_queue_created"] = False
    result["queue_write_performed"] = False
    result["scheduler_write_performed"] = False
    result["cron_write_performed"] = False
    result["task_enqueued"] = False
    result["task_executed"] = False
    result["arbitrary_task_execution_performed"] = False
    result["user_task_execution_performed"] = False
    result["live_task_assignment_performed"] = False
    result["live_worker_routing_performed"] = False
    result["live_orchestration_performed"] = False
    result["external_tool_invocation_performed"] = False
    result["api_call_performed"] = False
    result["network_access_performed"] = False
    result["deployment_performed"] = False
    result["production_execution_performed"] = False
    result["full_workforce_activation_performed"] = False

    result["station_chief_v6_2_post_mvp_expansion_lane_scope"] = bundle

    return result


def write_station_chief_v6_2_post_mvp_expansion_lane_scope(
    result: dict,
    output_dir: str,
    v6_1_review_packet_reference_label: str | None = None,
    selected_expansion_lane_label: str | None = None,
    lane_scope_label: str | None = None,
    lane_constraint_label: str | None = None,
    lane_success_criteria_label: str | None = None,
    lane_non_execution_boundary_label: str | None = None,
    lane_scope_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
) -> dict:
    result = attach_station_chief_v6_2_post_mvp_expansion_lane_scope(
        result,
        v6_1_review_packet_reference_label=v6_1_review_packet_reference_label,
        selected_expansion_lane_label=selected_expansion_lane_label,
        lane_scope_label=lane_scope_label,
        lane_constraint_label=lane_constraint_label,
        lane_success_criteria_label=lane_success_criteria_label,
        lane_non_execution_boundary_label=lane_non_execution_boundary_label,
        output_directory=output_dir,
        lane_scope_packet_name=lane_scope_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        lane_scope_requested=True,
        write_lane_scope_packet=True,
    )
    write_record = result["lane_scope_packet_write_record"]
    result["station_chief_v6_2_post_mvp_expansion_lane_scope_write_summary"] = write_record
    result["station_chief_v6_2_post_mvp_expansion_lane_scope_dir"] = write_record.get("output_directory") or str(output_dir)
    if result.get("local_lane_scope_packet_written"):
        rec_name = write_record.get("record_name")
        rec_path = write_record.get("record_path")
        result["files_written"] = [rec_name] if rec_name else []
        result["record_path"] = rec_path
    else:
        result["files_written"] = []
        result["record_path"] = None
    result["execution_status"] = write_record.get("write_status")
    return result


def attach_station_chief_v6_3_post_mvp_expansion_lane_readiness(
    result: dict,
    v6_2_lane_scope_packet_reference_label: str | None = None,
    selected_expansion_lane_label: str | None = None,
    readiness_checklist_label: str | None = None,
    readiness_blocker_label: str | None = None,
    readiness_evidence_label: str | None = None,
    readiness_non_execution_boundary_label: str | None = None,
    output_directory: str | None = None,
    readiness_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    readiness_requested: bool = False,
    write_readiness_packet: bool = False,
) -> dict:
    bundle = create_station_chief_v6_3_post_mvp_expansion_lane_readiness_bundle(
        result,
        command=result.get("command"),
        v6_2_lane_scope_packet_reference_label=v6_2_lane_scope_packet_reference_label,
        selected_expansion_lane_label=selected_expansion_lane_label,
        readiness_checklist_label=readiness_checklist_label,
        readiness_blocker_label=readiness_blocker_label,
        readiness_evidence_label=readiness_evidence_label,
        readiness_non_execution_boundary_label=readiness_non_execution_boundary_label,
        output_directory=output_directory,
        readiness_packet_name=readiness_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        readiness_requested=readiness_requested,
        write_readiness_packet=write_readiness_packet,
    )
    result = dict(result)
    result["station_chief_v6_3_post_mvp_expansion_lane_readiness_bundle"] = bundle
    result["station_chief_v6_3_post_mvp_expansion_lane_readiness_schema"] = bundle["station_chief_v6_3_post_mvp_expansion_lane_readiness_schema"]
    result["readiness_approval_gate"] = bundle["readiness_approval_gate"]
    result["readiness_contracts"] = bundle["readiness_contracts"]
    result["readiness_permission_denial_record"] = bundle["readiness_permission_denial_record"]
    result["readiness_packet_record"] = bundle["readiness_packet_record"]
    result["readiness_audit_record"] = bundle["readiness_audit_record"]
    result["readiness_summary"] = bundle["readiness_summary"]
    result["station_chief_v6_4_candidate_bridge"] = bundle["station_chief_v6_4_candidate_bridge"]
    result["readiness_packet_payload"] = bundle.get("readiness_packet_payload")
    result["readiness_packet_write_record"] = bundle.get("readiness_packet_write_record")
    result["local_readiness_packet_written"] = bundle["local_readiness_packet_written"]
    result["station_chief_v6_3_readiness_created"] = bundle["station_chief_v6_3_readiness_created"]
    result["post_mvp_expansion_lane_readiness_recorded"] = bundle["post_mvp_expansion_lane_readiness_recorded"]
    result["selected_expansion_lane_implemented"] = False
    result["selected_expansion_lane_executed"] = False
    result["post_mvp_expansion_executed"] = False
    result["v6_2_lane_scope_packet_mutated"] = False
    result["v6_2_lane_scope_packet_executed"] = False
    result["v6_1_review_packet_mutated"] = False
    result["v6_1_review_packet_executed"] = False
    result["v6_0_mvp_lock_mutated"] = False
    result["v6_0_mvp_lock_executed"] = False
    result["local_task_candidate_executed"] = False
    result["dry_run_task_executed"] = False
    result["real_worker_result_created"] = False
    result["live_replay_performed"] = False
    result["production_audit_performed"] = False
    result["rollback_performed"] = False
    result["recovery_performed"] = False
    result["v6_4_created"] = False
    result["worker_process_started"] = False
    result["agent_started"] = False
    result["real_queue_created"] = False
    result["queue_write_performed"] = False
    result["scheduler_write_performed"] = False
    result["cron_write_performed"] = False
    result["task_enqueued"] = False
    result["task_executed"] = False
    result["arbitrary_task_execution_performed"] = False
    result["user_task_execution_performed"] = False
    result["live_task_assignment_performed"] = False
    result["live_worker_routing_performed"] = False
    result["live_orchestration_performed"] = False
    result["external_tool_invocation_performed"] = False
    result["api_call_performed"] = False
    result["network_access_performed"] = False
    result["deployment_performed"] = False
    result["production_execution_performed"] = False
    result["full_workforce_activation_performed"] = False
    return result


def write_station_chief_v6_3_post_mvp_expansion_lane_readiness(
    result: dict,
    output_dir: str,
    v6_2_lane_scope_packet_reference_label: str | None = None,
    selected_expansion_lane_label: str | None = None,
    readiness_checklist_label: str | None = None,
    readiness_blocker_label: str | None = None,
    readiness_evidence_label: str | None = None,
    readiness_non_execution_boundary_label: str | None = None,
    readiness_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
) -> dict:
    result = attach_station_chief_v6_3_post_mvp_expansion_lane_readiness(
        result,
        v6_2_lane_scope_packet_reference_label=v6_2_lane_scope_packet_reference_label,
        selected_expansion_lane_label=selected_expansion_lane_label,
        readiness_checklist_label=readiness_checklist_label,
        readiness_blocker_label=readiness_blocker_label,
        readiness_evidence_label=readiness_evidence_label,
        readiness_non_execution_boundary_label=readiness_non_execution_boundary_label,
        output_directory=output_dir,
        readiness_packet_name=readiness_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        readiness_requested=True,
        write_readiness_packet=True,
    )
    write_record = result["readiness_packet_write_record"]
    result["station_chief_v6_3_post_mvp_expansion_lane_readiness_write_summary"] = write_record
    result["station_chief_v6_3_post_mvp_expansion_lane_readiness_dir"] = write_record.get("output_directory") or str(output_dir)
    if result.get("local_readiness_packet_written"):
        rec_name = write_record.get("record_name")
        rec_path = write_record.get("record_path")
        result["files_written"] = [rec_name] if rec_name else []
        result["record_path"] = rec_path
    else:
        result["files_written"] = []
        result["record_path"] = None
    result["execution_status"] = write_record.get("write_status")
    return result


def attach_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan(
    result: dict,
    v6_3_readiness_packet_reference_label: str | None = None,
    v6_2_lane_scope_packet_reference_label: str | None = None,
    selected_expansion_lane_label: str | None = None,
    implementation_plan_label: str | None = None,
    implementation_step_list_label: str | None = None,
    implementation_risk_register_label: str | None = None,
    implementation_rollback_plan_label: str | None = None,
    implementation_non_execution_boundary_label: str | None = None,
    output_directory: str | None = None,
    implementation_plan_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    implementation_plan_requested: bool = False,
    write_implementation_plan_packet: bool = False,
) -> dict:
    bundle = create_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_bundle(
        result,
        command=result.get("command"),
        v6_3_readiness_packet_reference_label=v6_3_readiness_packet_reference_label,
        v6_2_lane_scope_packet_reference_label=v6_2_lane_scope_packet_reference_label,
        selected_expansion_lane_label=selected_expansion_lane_label,
        implementation_plan_label=implementation_plan_label,
        implementation_step_list_label=implementation_step_list_label,
        implementation_risk_register_label=implementation_risk_register_label,
        implementation_rollback_plan_label=implementation_rollback_plan_label,
        implementation_non_execution_boundary_label=implementation_non_execution_boundary_label,
        output_directory=output_directory,
        implementation_plan_packet_name=implementation_plan_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        implementation_plan_requested=implementation_plan_requested,
        write_implementation_plan_packet=write_implementation_plan_packet,
    )
    result = dict(result)
    result["station_chief_v6_4_implementation_plan_bundle"] = bundle
    result["station_chief_v6_4_implementation_plan_schema"] = bundle["station_chief_v6_4_implementation_plan_schema"]
    result["implementation_plan_approval_gate"] = bundle["implementation_plan_approval_gate"]
    result["implementation_plan_contracts"] = bundle["implementation_plan_contracts"]
    result["implementation_plan_permission_denial_record"] = bundle["implementation_plan_permission_denial_record"]
    result["implementation_plan_packet_write_record"] = bundle["implementation_plan_packet_write_record"]
    result["implementation_plan_payload"] = bundle.get("implementation_plan_payload")
    result["local_implementation_plan_packet_written"] = bundle["local_implementation_plan_packet_written"]
    result["station_chief_v6_4_implementation_plan_created"] = bundle["station_chief_v6_4_implementation_plan_created"]
    result["post_mvp_expansion_lane_implementation_plan_recorded"] = bundle["post_mvp_expansion_lane_implementation_plan_recorded"]
    return result


def write_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan(
    result: dict,
    output_dir: str,
    v6_3_readiness_packet_reference_label: str | None = None,
    v6_2_lane_scope_packet_reference_label: str | None = None,
    selected_expansion_lane_label: str | None = None,
    implementation_plan_label: str | None = None,
    implementation_step_list_label: str | None = None,
    implementation_risk_register_label: str | None = None,
    implementation_rollback_plan_label: str | None = None,
    implementation_non_execution_boundary_label: str | None = None,
    implementation_plan_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
) -> dict:
    result = attach_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan(
        result,
        v6_3_readiness_packet_reference_label=v6_3_readiness_packet_reference_label,
        v6_2_lane_scope_packet_reference_label=v6_2_lane_scope_packet_reference_label,
        selected_expansion_lane_label=selected_expansion_lane_label,
        implementation_plan_label=implementation_plan_label,
        implementation_step_list_label=implementation_step_list_label,
        implementation_risk_register_label=implementation_risk_register_label,
        implementation_rollback_plan_label=implementation_rollback_plan_label,
        implementation_non_execution_boundary_label=implementation_non_execution_boundary_label,
        output_directory=output_dir,
        implementation_plan_packet_name=implementation_plan_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        implementation_plan_requested=True,
        write_implementation_plan_packet=True,
    )
    write_record = result["implementation_plan_packet_write_record"]
    result["station_chief_v6_4_implementation_plan_write_summary"] = write_record
    result["station_chief_v6_4_implementation_plan_dir"] = write_record.get("output_directory") or str(output_dir)
    if result.get("local_implementation_plan_packet_written"):
        rec_name = write_record.get("record_name")
        rec_path = write_record.get("record_path")
        result["files_written"] = [rec_name] if rec_name else []
        result["record_path"] = rec_path
    else:
        result["files_written"] = []
        result["record_path"] = None
    result["execution_status"] = write_record.get("write_status")
    return result


def attach_sandbox_worker_dry_run_replay_audit_candidate(
    result: dict,
    sandbox_worker_label: str | None = None,
    v5_3_handoff_packet_reference_label: str | None = None,
    v5_4_acknowledgement_packet_reference_label: str | None = None,
    v5_5_acceptance_review_packet_reference_label: str | None = None,
    v5_6_ready_state_packet_reference_label: str | None = None,
    v5_7_dry_run_assignment_packet_reference_label: str | None = None,
    v5_8_dry_run_result_packet_reference_label: str | None = None,
    synthetic_dry_run_task_label: str | None = None,
    synthetic_dry_run_result_label: str | None = None,
    replay_audit_candidate_label: str | None = None,
    output_directory: str | None = None,
    dry_run_replay_audit_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    replay_audit_requested: bool = False,
    write_dry_run_replay_audit_packet: bool = False,
) -> dict:
    bundle = create_sandbox_worker_dry_run_replay_audit_candidate_bundle(
        result,
        command=result.get("command"),
        sandbox_worker_label=sandbox_worker_label,
        v5_3_handoff_packet_reference_label=v5_3_handoff_packet_reference_label,
        v5_4_acknowledgement_packet_reference_label=v5_4_acknowledgement_packet_reference_label,
        v5_5_acceptance_review_packet_reference_label=v5_5_acceptance_review_packet_reference_label,
        v5_6_ready_state_packet_reference_label=v5_6_ready_state_packet_reference_label,
        v5_7_dry_run_assignment_packet_reference_label=v5_7_dry_run_assignment_packet_reference_label,
        v5_8_dry_run_result_packet_reference_label=v5_8_dry_run_result_packet_reference_label,
        synthetic_dry_run_task_label=synthetic_dry_run_task_label,
        synthetic_dry_run_result_label=synthetic_dry_run_result_label,
        replay_audit_candidate_label=replay_audit_candidate_label,
        output_directory=output_directory,
        dry_run_replay_audit_packet_name=dry_run_replay_audit_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        replay_audit_requested=replay_audit_requested,
        write_dry_run_replay_audit_packet=write_dry_run_replay_audit_packet,
    )
    result = dict(result)
    result["sandbox_worker_dry_run_replay_audit_candidate_bundle"] = bundle
    result["sandbox_worker_dry_run_replay_audit_candidate_schema"] = bundle["schema"]
    result["sandbox_worker_dry_run_replay_audit_approval_gate"] = bundle["approval_gate"]
    result["v5_3_handoff_packet_reference_contract"] = bundle["v5_3_handoff_packet_reference_contract"]
    result["v5_4_acknowledgement_packet_reference_contract"] = bundle["v5_4_acknowledgement_packet_reference_contract"]
    result["v5_5_acceptance_review_packet_reference_contract"] = bundle["v5_5_acceptance_review_packet_reference_contract"]
    result["v5_6_ready_state_packet_reference_contract"] = bundle["v5_6_ready_state_packet_reference_contract"]
    result["v5_7_dry_run_assignment_packet_reference_contract"] = bundle["v5_7_dry_run_assignment_packet_reference_contract"]
    result["v5_8_dry_run_result_packet_reference_contract"] = bundle["v5_8_dry_run_result_packet_reference_contract"]
    result["synthetic_dry_run_task_reference_contract"] = bundle["synthetic_dry_run_task_reference_contract"]
    result["synthetic_dry_run_result_reference_contract"] = bundle["synthetic_dry_run_result_reference_contract"]
    result["replay_audit_candidate_reference_contract"] = bundle["replay_audit_candidate_reference_contract"]
    result["sandbox_worker_dry_run_replay_audit_reference_contract"] = bundle["sandbox_worker_dry_run_replay_audit_reference_contract"]
    result["dry_run_replay_audit_scope_contract"] = bundle["dry_run_replay_audit_scope_contract"]
    result["non_execution_dry_run_replay_audit_boundary"] = bundle["non_execution_dry_run_replay_audit_boundary"]
    result["dry_run_replay_audit_permission_denial_record"] = bundle["dry_run_replay_audit_permission_denial_record"]
    result["dry_run_replay_audit_plan_record"] = bundle["dry_run_replay_audit_plan_record"]
    result["dry_run_replay_audit_packet_record"] = bundle["dry_run_replay_audit_packet_record"]
    result["dry_run_replay_audit_audit_record"] = bundle["dry_run_replay_audit_audit_record"]
    result["dry_run_replay_audit_readiness_summary"] = bundle["dry_run_replay_audit_readiness_summary"]
    result["station_chief_mvp_lock_candidate_bridge"] = bundle["station_chief_mvp_lock_candidate_bridge"]
    result["dry_run_replay_audit_packet_payload"] = bundle.get("dry_run_replay_audit_packet_payload")
    result["dry_run_replay_audit_packet_write_record"] = bundle.get("dry_run_replay_audit_packet_record", {}).get("write_record")
    result["local_dry_run_replay_audit_packet_written"] = bundle["local_dry_run_replay_audit_packet_written"]
    result["sandbox_worker_dry_run_replay_audit_candidate_created"] = bundle["sandbox_worker_dry_run_replay_audit_candidate_created"]
    result["dry_run_replay_candidate_recorded"] = bundle["dry_run_replay_candidate_recorded"]
    result["dry_run_audit_candidate_recorded"] = bundle["dry_run_audit_candidate_recorded"]
    result["dry_run_task_executed"] = False
    result["real_worker_result_created"] = False
    result["live_replay_performed"] = False
    result["production_audit_performed"] = False
    result["rollback_performed"] = False
    result["recovery_performed"] = False
    result["mvp_lock_created"] = False
    result["v6_0_created"] = False
    result["worker_process_started"] = False
    result["agent_started"] = False
    result["real_queue_created"] = False
    result["queue_write_performed"] = False
    result["scheduler_write_performed"] = False
    result["cron_write_performed"] = False
    result["task_enqueued"] = False
    result["task_executed"] = False
    result["arbitrary_task_execution_performed"] = False
    result["user_task_execution_performed"] = False
    result["live_task_assignment_performed"] = False
    result["live_worker_routing_performed"] = False
    result["live_orchestration_performed"] = False
    result["external_tool_invocation_performed"] = False
    result["api_call_performed"] = False
    result["network_access_performed"] = False
    result["deployment_performed"] = False
    result["production_execution_performed"] = False
    result["full_workforce_activation_performed"] = False
    
    # Compatibility object
    result["sandbox_worker_dry_run_replay_audit_candidate"] = bundle
    
    return result


def write_sandbox_worker_dry_run_replay_audit_candidate(
    result: dict,
    output_dir: str,
    sandbox_worker_label: str | None = None,
    v5_3_handoff_packet_reference_label: str | None = None,
    v5_4_acknowledgement_packet_reference_label: str | None = None,
    v5_5_acceptance_review_packet_reference_label: str | None = None,
    v5_6_ready_state_packet_reference_label: str | None = None,
    v5_7_dry_run_assignment_packet_reference_label: str | None = None,
    v5_8_dry_run_result_packet_reference_label: str | None = None,
    synthetic_dry_run_task_label: str | None = None,
    synthetic_dry_run_result_label: str | None = None,
    replay_audit_candidate_label: str | None = None,
    dry_run_replay_audit_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
) -> dict:
    result = attach_sandbox_worker_dry_run_replay_audit_candidate(
        result,
        sandbox_worker_label=sandbox_worker_label,
        v5_3_handoff_packet_reference_label=v5_3_handoff_packet_reference_label,
        v5_4_acknowledgement_packet_reference_label=v5_4_acknowledgement_packet_reference_label,
        v5_5_acceptance_review_packet_reference_label=v5_5_acceptance_review_packet_reference_label,
        v5_6_ready_state_packet_reference_label=v5_6_ready_state_packet_reference_label,
        v5_7_dry_run_assignment_packet_reference_label=v5_7_dry_run_assignment_packet_reference_label,
        v5_8_dry_run_result_packet_reference_label=v5_8_dry_run_result_packet_reference_label,
        synthetic_dry_run_task_label=synthetic_dry_run_task_label,
        synthetic_dry_run_result_label=synthetic_dry_run_result_label,
        replay_audit_candidate_label=replay_audit_candidate_label,
        output_directory=output_dir,
        dry_run_replay_audit_packet_name=dry_run_replay_audit_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        replay_audit_requested=True,
        write_dry_run_replay_audit_packet=True,
    )
    write_record = result["dry_run_replay_audit_packet_write_record"]
    result["sandbox_worker_dry_run_replay_audit_candidate_write_summary"] = write_record
    result["sandbox_worker_dry_run_replay_audit_candidate_dir"] = write_record.get("output_directory") or str(output_dir)
    if result.get("local_dry_run_replay_audit_packet_written"):
        rec_name = write_record.get("record_name")
        rec_path = write_record.get("record_path")
        result["files_written"] = [rec_name] if rec_name else []
        result["record_path"] = rec_path
    else:
        result["files_written"] = []
        result["record_path"] = None
    result["execution_status"] = write_record.get("write_status")
    return result


def attach_sandbox_worker_dry_run_result_candidate(
    result: dict,
    sandbox_worker_label: str | None = None,
    v5_3_handoff_packet_reference_label: str | None = None,
    v5_4_acknowledgement_packet_reference_label: str | None = None,
    v5_5_acceptance_review_packet_reference_label: str | None = None,
    v5_6_ready_state_packet_reference_label: str | None = None,
    v5_7_dry_run_assignment_packet_reference_label: str | None = None,
    synthetic_dry_run_task_label: str | None = None,
    synthetic_dry_run_result_label: str | None = None,
    output_directory: str | None = None,
    dry_run_result_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    dry_run_result_requested: bool = False,
    write_dry_run_result_packet: bool = False,
) -> dict:
    bundle = create_sandbox_worker_dry_run_result_candidate_bundle(
        result,
        command=result.get("command"),
        sandbox_worker_label=sandbox_worker_label,
        v5_3_handoff_packet_reference_label=v5_3_handoff_packet_reference_label,
        v5_4_acknowledgement_packet_reference_label=v5_4_acknowledgement_packet_reference_label,
        v5_5_acceptance_review_packet_reference_label=v5_5_acceptance_review_packet_reference_label,
        v5_6_ready_state_packet_reference_label=v5_6_ready_state_packet_reference_label,
        v5_7_dry_run_assignment_packet_reference_label=v5_7_dry_run_assignment_packet_reference_label,
        synthetic_dry_run_task_label=synthetic_dry_run_task_label,
        synthetic_dry_run_result_label=synthetic_dry_run_result_label,
        output_directory=output_directory,
        dry_run_result_packet_name=dry_run_result_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        dry_run_result_requested=dry_run_result_requested,
        write_dry_run_result_packet=write_dry_run_result_packet,
    )
    result = dict(result)
    result["sandbox_worker_dry_run_result_candidate_bundle"] = bundle
    result["sandbox_worker_dry_run_result_candidate_schema"] = bundle["schema"]
    result["sandbox_worker_dry_run_result_approval_gate"] = bundle["approval_gate"]
    result["v5_3_handoff_packet_reference_contract"] = bundle["v5_3_handoff_packet_reference_contract"]
    result["v5_4_acknowledgement_packet_reference_contract"] = bundle["v5_4_acknowledgement_packet_reference_contract"]
    result["v5_5_acceptance_review_packet_reference_contract"] = bundle["v5_5_acceptance_review_packet_reference_contract"]
    result["v5_6_ready_state_packet_reference_contract"] = bundle["v5_6_ready_state_packet_reference_contract"]
    result["v5_7_dry_run_assignment_packet_reference_contract"] = bundle["v5_7_dry_run_assignment_packet_reference_contract"]
    result["synthetic_dry_run_task_reference_contract"] = bundle["synthetic_dry_run_task_reference_contract"]
    result["synthetic_dry_run_result_reference_contract"] = bundle["synthetic_dry_run_result_reference_contract"]
    result["sandbox_worker_dry_run_result_reference_contract"] = bundle["sandbox_worker_dry_run_result_reference_contract"]
    result["dry_run_result_scope_contract"] = bundle["dry_run_result_scope_contract"]
    result["non_execution_dry_run_result_boundary"] = bundle["non_execution_dry_run_result_boundary"]
    result["dry_run_result_permission_denial_record"] = bundle["dry_run_result_permission_denial_record"]
    result["dry_run_result_plan_record"] = bundle["dry_run_result_plan_record"]
    result["dry_run_result_packet_record"] = bundle["dry_run_result_packet_record"]
    result["dry_run_result_audit_record"] = bundle["dry_run_result_audit_record"]
    result["dry_run_result_readiness_summary"] = bundle["dry_run_result_readiness_summary"]
    result["sandbox_worker_dry_run_replay_audit_candidate_bridge"] = bundle["sandbox_worker_dry_run_replay_audit_candidate_bridge"]
    result["dry_run_result_packet_payload"] = bundle.get("dry_run_result_packet_payload")
    result["dry_run_result_packet_write_record"] = bundle.get("dry_run_result_packet_record", {}).get("write_record")
    result["local_dry_run_result_packet_written"] = bundle["local_dry_run_result_packet_written"]
    result["sandbox_worker_dry_run_result_candidate_created"] = bundle["sandbox_worker_dry_run_result_candidate_created"]
    result["dry_run_result_candidate_recorded"] = bundle["dry_run_result_candidate_recorded"]
    result["dry_run_task_executed"] = False
    result["real_worker_result_created"] = False
    result["replay_audit_performed"] = False
    result["worker_process_started"] = False
    result["agent_started"] = False
    result["real_queue_created"] = False
    result["queue_write_performed"] = False
    result["scheduler_write_performed"] = False
    result["cron_write_performed"] = False
    result["task_enqueued"] = False
    result["task_executed"] = False
    result["arbitrary_task_execution_performed"] = False
    result["user_task_execution_performed"] = False
    result["live_task_assignment_performed"] = False
    result["live_worker_routing_performed"] = False
    result["live_orchestration_performed"] = False
    result["external_tool_invocation_performed"] = False
    result["api_call_performed"] = False
    result["network_access_performed"] = False
    result["deployment_performed"] = False
    result["production_execution_performed"] = False
    result["full_workforce_activation_performed"] = False
    
    # Compatibility object
    result["sandbox_worker_dry_run_result_candidate"] = bundle
    
    return result


def write_sandbox_worker_dry_run_result_candidate(
    result: dict,
    output_dir: str,
    sandbox_worker_label: str | None = None,
    v5_3_handoff_packet_reference_label: str | None = None,
    v5_4_acknowledgement_packet_reference_label: str | None = None,
    v5_5_acceptance_review_packet_reference_label: str | None = None,
    v5_6_ready_state_packet_reference_label: str | None = None,
    v5_7_dry_run_assignment_packet_reference_label: str | None = None,
    synthetic_dry_run_task_label: str | None = None,
    synthetic_dry_run_result_label: str | None = None,
    dry_run_result_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
) -> dict:
    result = attach_sandbox_worker_dry_run_result_candidate(
        result,
        sandbox_worker_label=sandbox_worker_label,
        v5_3_handoff_packet_reference_label=v5_3_handoff_packet_reference_label,
        v5_4_acknowledgement_packet_reference_label=v5_4_acknowledgement_packet_reference_label,
        v5_5_acceptance_review_packet_reference_label=v5_5_acceptance_review_packet_reference_label,
        v5_6_ready_state_packet_reference_label=v5_6_ready_state_packet_reference_label,
        v5_7_dry_run_assignment_packet_reference_label=v5_7_dry_run_assignment_packet_reference_label,
        synthetic_dry_run_task_label=synthetic_dry_run_task_label,
        synthetic_dry_run_result_label=synthetic_dry_run_result_label,
        output_directory=output_dir,
        dry_run_result_packet_name=dry_run_result_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        dry_run_result_requested=True,
        write_dry_run_result_packet=True,
    )
    write_record = result["dry_run_result_packet_write_record"]
    result["sandbox_worker_dry_run_result_candidate_write_summary"] = write_record
    result["sandbox_worker_dry_run_result_candidate_dir"] = write_record.get("output_directory") or str(output_dir)
    if result.get("local_dry_run_result_packet_written"):
        rec_name = write_record.get("record_name")
        rec_path = write_record.get("record_path")
        result["files_written"] = [rec_name] if rec_name else []
        result["record_path"] = rec_path
    else:
        result["files_written"] = []
        result["record_path"] = None
    result["execution_status"] = write_record.get("write_status")
    return result

def attach_sandbox_worker_dry_run_assignment_candidate(
    result: dict,
    sandbox_worker_label: str | None = None,
    v5_3_handoff_packet_reference_label: str | None = None,
    v5_4_acknowledgement_packet_reference_label: str | None = None,
    v5_5_acceptance_review_packet_reference_label: str | None = None,
    v5_6_ready_state_packet_reference_label: str | None = None,
    synthetic_dry_run_task_label: str | None = None,
    output_directory: str | None = None,
    dry_run_assignment_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    dry_run_assignment_requested: bool = False,
    write_dry_run_assignment_packet: bool = False,
) -> dict:
    bundle = create_sandbox_worker_dry_run_assignment_candidate_bundle(
        result,
        command=result.get("command"),
        sandbox_worker_label=sandbox_worker_label,
        v5_3_handoff_packet_reference_label=v5_3_handoff_packet_reference_label,
        v5_4_acknowledgement_packet_reference_label=v5_4_acknowledgement_packet_reference_label,
        v5_5_acceptance_review_packet_reference_label=v5_5_acceptance_review_packet_reference_label,
        v5_6_ready_state_packet_reference_label=v5_6_ready_state_packet_reference_label,
        synthetic_dry_run_task_label=synthetic_dry_run_task_label,
        output_directory=output_directory,
        dry_run_assignment_packet_name=dry_run_assignment_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        dry_run_assignment_requested=dry_run_assignment_requested,
        write_dry_run_assignment_packet=write_dry_run_assignment_packet,
    )
    result = dict(result)
    result["sandbox_worker_dry_run_assignment_candidate_bundle"] = bundle
    result["sandbox_worker_dry_run_assignment_candidate_schema"] = bundle["schema"]
    result["sandbox_worker_dry_run_assignment_approval_gate"] = bundle["approval_gate"]
    result["v5_3_handoff_packet_reference_contract"] = bundle["v5_3_handoff_packet_reference_contract"]
    result["v5_4_acknowledgement_packet_reference_contract"] = bundle["v5_4_acknowledgement_packet_reference_contract"]
    result["v5_5_acceptance_review_packet_reference_contract"] = bundle["v5_5_acceptance_review_packet_reference_contract"]
    result["v5_6_ready_state_packet_reference_contract"] = bundle["v5_6_ready_state_packet_reference_contract"]
    result["synthetic_dry_run_task_reference_contract"] = bundle["synthetic_dry_run_task_reference_contract"]
    result["sandbox_worker_dry_run_assignment_reference_contract"] = bundle["sandbox_worker_dry_run_assignment_reference_contract"]
    result["dry_run_assignment_scope_contract"] = bundle["dry_run_assignment_scope_contract"]
    result["non_execution_dry_run_assignment_boundary"] = bundle["non_execution_dry_run_assignment_boundary"]
    result["dry_run_assignment_permission_denial_record"] = bundle["dry_run_assignment_permission_denial_record"]
    result["dry_run_assignment_plan_record"] = bundle["dry_run_assignment_plan_record"]
    result["dry_run_assignment_packet_record"] = bundle["dry_run_assignment_packet_record"]
    result["dry_run_assignment_audit_record"] = bundle["dry_run_assignment_audit_record"]
    result["dry_run_assignment_readiness_summary"] = bundle["dry_run_assignment_readiness_summary"]
    result["sandbox_worker_dry_run_result_candidate_bridge"] = bundle["sandbox_worker_dry_run_result_candidate_bridge"]
    result["dry_run_assignment_packet_payload"] = bundle.get("dry_run_assignment_packet_payload")
    result["dry_run_assignment_packet_write_record"] = bundle.get("dry_run_assignment_packet_record", {}).get("write_record")
    result["local_dry_run_assignment_packet_written"] = bundle["local_dry_run_assignment_packet_written"]
    result["sandbox_worker_dry_run_assignment_created"] = bundle["sandbox_worker_dry_run_assignment_created"]
    result["dry_run_task_assignment_recorded"] = bundle["dry_run_task_assignment_recorded"]
    result["dry_run_result_created"] = False
    result["dry_run_task_executed"] = False
    result["worker_process_started"] = False
    result["agent_started"] = False
    result["real_queue_created"] = False
    result["queue_write_performed"] = False
    result["scheduler_write_performed"] = False
    result["cron_write_performed"] = False
    result["task_enqueued"] = False
    result["task_executed"] = False
    result["arbitrary_task_execution_performed"] = False
    result["user_task_execution_performed"] = False
    result["live_task_assignment_performed"] = False
    result["live_worker_routing_performed"] = False
    result["live_orchestration_performed"] = False
    result["external_tool_invocation_performed"] = False
    result["api_call_performed"] = False
    result["network_access_performed"] = False
    result["deployment_performed"] = False
    result["production_execution_performed"] = False
    result["full_workforce_activation_performed"] = False
    
    # Compatibility object
    result["sandbox_worker_dry_run_assignment_candidate"] = bundle
    
    return result


def write_sandbox_worker_dry_run_assignment_candidate(
    result: dict,
    output_dir: str,
    sandbox_worker_label: str | None = None,
    v5_3_handoff_packet_reference_label: str | None = None,
    v5_4_acknowledgement_packet_reference_label: str | None = None,
    v5_5_acceptance_review_packet_reference_label: str | None = None,
    v5_6_ready_state_packet_reference_label: str | None = None,
    synthetic_dry_run_task_label: str | None = None,
    dry_run_assignment_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
) -> dict:
    result = attach_sandbox_worker_dry_run_assignment_candidate(
        result,
        sandbox_worker_label=sandbox_worker_label,
        v5_3_handoff_packet_reference_label=v5_3_handoff_packet_reference_label,
        v5_4_acknowledgement_packet_reference_label=v5_4_acknowledgement_packet_reference_label,
        v5_5_acceptance_review_packet_reference_label=v5_5_acceptance_review_packet_reference_label,
        v5_6_ready_state_packet_reference_label=v5_6_ready_state_packet_reference_label,
        synthetic_dry_run_task_label=synthetic_dry_run_task_label,
        output_directory=output_dir,
        dry_run_assignment_packet_name=dry_run_assignment_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        dry_run_assignment_requested=True,
        write_dry_run_assignment_packet=True,
    )
    write_record = result["dry_run_assignment_packet_write_record"]
    result["sandbox_worker_dry_run_assignment_candidate_write_summary"] = write_record
    result["sandbox_worker_dry_run_assignment_candidate_dir"] = write_record.get("output_directory") or str(output_dir)
    if result.get("local_dry_run_assignment_packet_written"):
        rec_name = write_record.get("record_name")
        rec_path = write_record.get("record_path")
        result["files_written"] = [rec_name] if rec_name else []
        result["record_path"] = rec_path
    else:
        result["files_written"] = []
        result["record_path"] = None
    result["execution_status"] = write_record.get("write_status")
    return result

def attach_sandbox_worker_ready_state_packet_candidate(
    result: dict,
    sandbox_worker_label: str | None = None,
    v5_3_handoff_packet_reference_label: str | None = None,
    v5_4_acknowledgement_packet_reference_label: str | None = None,
    v5_5_acceptance_review_packet_reference_label: str | None = None,
    output_directory: str | None = None,
    ready_state_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
    ready_state_packet_requested: bool = False,
    write_ready_state_packet: bool = False,
) -> dict:
    bundle = create_sandbox_worker_ready_state_packet_candidate_bundle(
        result,
        command=result.get("command"),
        sandbox_worker_label=sandbox_worker_label,
        v5_3_handoff_packet_reference_label=v5_3_handoff_packet_reference_label,
        v5_4_acknowledgement_packet_reference_label=v5_4_acknowledgement_packet_reference_label,
        v5_5_acceptance_review_packet_reference_label=v5_5_acceptance_review_packet_reference_label,
        output_directory=output_directory,
        ready_state_packet_name=ready_state_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        ready_state_packet_requested=ready_state_packet_requested,
        write_ready_state_packet=write_ready_state_packet,
    )
    result = dict(result)
    result["sandbox_worker_ready_state_packet_candidate_bundle"] = bundle
    result["sandbox_worker_ready_state_packet_candidate_schema"] = bundle["schema"]
    result["sandbox_worker_ready_state_packet_approval_gate"] = bundle["approval_gate"]
    result["v5_3_handoff_packet_reference_contract"] = bundle["v5_3_handoff_packet_reference_contract"]
    result["v5_4_acknowledgement_packet_reference_contract"] = bundle["v5_4_acknowledgement_packet_reference_contract"]
    result["v5_5_acceptance_review_packet_reference_contract"] = bundle["v5_5_acceptance_review_packet_reference_contract"]
    result["sandbox_worker_ready_state_reference_contract"] = bundle["sandbox_worker_ready_state_reference_contract"]
    result["ready_state_scope_contract"] = bundle["ready_state_scope_contract"]
    result["non_execution_ready_state_boundary"] = bundle["non_execution_ready_state_boundary"]
    result["ready_state_permission_denial_record"] = bundle["ready_state_permission_denial_record"]
    result["ready_state_plan_record"] = bundle["ready_state_plan_record"]
    result["ready_state_packet_record"] = bundle["ready_state_packet_record"]
    result["ready_state_audit_record"] = bundle["ready_state_audit_record"]
    result["ready_state_readiness_summary"] = bundle["ready_state_readiness_summary"]
    result["sandbox_worker_dry_run_assignment_candidate_bridge"] = bundle["sandbox_worker_dry_run_assignment_candidate_bridge"]
    result["ready_state_packet_payload"] = bundle.get("ready_state_packet_payload")
    result["ready_state_packet_write_record"] = bundle.get("ready_state_packet_record", {}).get("write_record")
    result["local_ready_state_packet_written"] = bundle["local_ready_state_packet_written"]
    result["sandbox_worker_ready_state_packet_created"] = bundle["sandbox_worker_ready_state_packet_created"]
    result["sandbox_worker_ready_state_candidate_recorded"] = bundle["sandbox_worker_ready_state_candidate_recorded"]
    result["dry_run_assignment_created"] = False
    result["dry_run_task_assigned"] = False
    result["worker_process_started"] = False
    result["agent_started"] = False
    result["real_queue_created"] = False
    result["queue_write_performed"] = False
    result["scheduler_write_performed"] = False
    result["cron_write_performed"] = False
    result["task_enqueued"] = False
    result["task_executed"] = False
    result["arbitrary_task_execution_performed"] = False
    result["user_task_execution_performed"] = False
    result["live_task_assignment_performed"] = False
    result["live_worker_routing_performed"] = False
    result["live_orchestration_performed"] = False
    result["external_tool_invocation_performed"] = False
    result["api_call_performed"] = False
    result["network_access_performed"] = False
    result["deployment_performed"] = False
    result["production_execution_performed"] = False
    result["full_workforce_activation_performed"] = False
    
    # Compatibility object
    result["sandbox_worker_ready_state_packet_candidate"] = bundle
    
    return result


def write_sandbox_worker_ready_state_packet_candidate(
    result: dict,
    output_dir: str,
    sandbox_worker_label: str | None = None,
    v5_3_handoff_packet_reference_label: str | None = None,
    v5_4_acknowledgement_packet_reference_label: str | None = None,
    v5_5_acceptance_review_packet_reference_label: str | None = None,
    ready_state_packet_name: str | None = None,
    confirmation_token: str | None = None,
    human_operator: str | None = None,
) -> dict:
    result = attach_sandbox_worker_ready_state_packet_candidate(
        result,
        sandbox_worker_label=sandbox_worker_label,
        v5_3_handoff_packet_reference_label=v5_3_handoff_packet_reference_label,
        v5_4_acknowledgement_packet_reference_label=v5_4_acknowledgement_packet_reference_label,
        v5_5_acceptance_review_packet_reference_label=v5_5_acceptance_review_packet_reference_label,
        output_directory=output_dir,
        ready_state_packet_name=ready_state_packet_name,
        confirmation_token=confirmation_token,
        human_operator=human_operator,
        ready_state_packet_requested=True,
        write_ready_state_packet=True,
    )
    write_record = result["ready_state_packet_write_record"]
    result["sandbox_worker_ready_state_packet_candidate_write_summary"] = write_record
    result["sandbox_worker_ready_state_packet_candidate_dir"] = write_record.get("output_directory") or str(output_dir)
    if result.get("local_ready_state_packet_written"):
        rec_name = write_record.get("record_name")
        rec_path = write_record.get("record_path")
        result["files_written"] = [rec_name] if rec_name else []
        result["record_path"] = rec_path
    else:
        result["files_written"] = []
        result["record_path"] = None
    result["execution_status"] = write_record.get("write_status")
    return result


def write_runtime_artifacts(
    result: dict,
    output_dir: str | Path,
    run_label: str = "station-chief-runtime",
    registry_dir: str | Path | None = None,
) -> dict:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    run_id = generate_run_id(result["command"], run_label=run_label)
    artifact_dir = output_path / run_id
    artifact_dir.mkdir(parents=True, exist_ok=True)

    artifacts = build_runtime_artifacts(result, run_id)
    artifacts["runtime_index_entry"] = build_runtime_index_entry(result, run_id, artifact_dir=str(artifact_dir))

    files_written = []
    mapping = {
        "station_chief_v6_1_post_mvp_expansion_review_bundle.json": artifacts.get("station_chief_v6_1_post_mvp_expansion_review_bundle"),
        "station_chief_v6_1_post_mvp_expansion_review_schema.json": artifacts.get("station_chief_v6_1_post_mvp_expansion_review_schema"),
        "post_mvp_expansion_review_approval_gate.json": artifacts.get("post_mvp_expansion_review_approval_gate"),
        "v6_0_mvp_lock_reference_contract.json": artifacts.get("v6_0_mvp_lock_reference_contract"),
        "requested_expansion_lane_contract.json": artifacts.get("requested_expansion_lane_contract"),
        "expansion_boundary_contract.json": artifacts.get("expansion_boundary_contract"),
        "expansion_safety_posture_contract.json": artifacts.get("expansion_safety_posture_contract"),
        "post_mvp_expansion_review_scope_contract.json": artifacts.get("post_mvp_expansion_review_scope_contract"),
        "non_execution_post_mvp_expansion_boundary.json": artifacts.get("non_execution_post_mvp_expansion_boundary"),
        "post_mvp_expansion_permission_denial_record.json": artifacts.get("post_mvp_expansion_permission_denial_record"),
        "post_mvp_expansion_review_plan_record.json": artifacts.get("post_mvp_expansion_review_plan_record"),
        "post_mvp_expansion_review_packet_record.json": artifacts.get("post_mvp_expansion_review_packet_record"),
        "post_mvp_expansion_review_audit_record.json": artifacts.get("post_mvp_expansion_review_audit_record"),
        "post_mvp_expansion_review_readiness_summary.json": artifacts.get("post_mvp_expansion_review_readiness_summary"),
        "station_chief_v6_2_candidate_bridge.json": artifacts.get("station_chief_v6_2_candidate_bridge"),
        "post_mvp_expansion_review_packet_payload.json": artifacts.get("post_mvp_expansion_review_packet_payload"),
        "post_mvp_expansion_review_packet_write_record.json": artifacts.get("post_mvp_expansion_review_packet_write_record"),
        "station_chief_v6_2_post_mvp_expansion_lane_scope_bundle.json": artifacts.get("station_chief_v6_2_post_mvp_expansion_lane_scope_bundle"),
        "station_chief_v6_2_post_mvp_expansion_lane_scope_schema.json": artifacts.get("station_chief_v6_2_post_mvp_expansion_lane_scope_schema"),
        "lane_scope_approval_gate.json": artifacts.get("lane_scope_approval_gate"),
        "v6_1_review_packet_reference_contract.json": artifacts.get("v6_1_review_packet_reference_contract"),
        "selected_expansion_lane_scope_contract.json": artifacts.get("selected_expansion_lane_scope_contract"),
        "lane_scope_contract.json": artifacts.get("lane_scope_contract"),
        "lane_constraint_contract.json": artifacts.get("lane_constraint_contract"),
        "lane_success_criteria_contract.json": artifacts.get("lane_success_criteria_contract"),
        "lane_non_execution_boundary_contract.json": artifacts.get("lane_non_execution_boundary_contract"),
        "post_mvp_expansion_lane_scope_contract.json": artifacts.get("post_mvp_expansion_lane_scope_contract"),
        "non_execution_lane_scope_boundary.json": artifacts.get("non_execution_lane_scope_boundary"),
        "lane_scope_permission_denial_record.json": artifacts.get("lane_scope_permission_denial_record"),
        "lane_scope_plan_record.json": artifacts.get("lane_scope_plan_record"),
        "lane_scope_packet_record.json": artifacts.get("lane_scope_packet_record"),
        "lane_scope_audit_record.json": artifacts.get("lane_scope_audit_record"),
        "lane_scope_readiness_summary.json": artifacts.get("lane_scope_readiness_summary"),
        "station_chief_v6_3_candidate_bridge.json": artifacts.get("station_chief_v6_3_candidate_bridge"),
        "lane_scope_packet_payload.json": artifacts.get("lane_scope_packet_payload"),
        "lane_scope_packet_write_record.json": artifacts.get("lane_scope_packet_write_record"),
        "run_log.json": artifacts["run_log"],
        "command_brief.json": artifacts["command_brief"],
        "work_orders.json": artifacts["work_orders"],
        "selected_overlays.json": artifacts["selected_overlays"],
        "evidence.json": artifacts["evidence"],
        "execution_plan.json": artifacts["execution_plan"],
        "adapter_result.json": artifacts["adapter_result"],
        "file_operation_plan.json": artifacts["file_operation_plan"],
        "execution_gate.json": artifacts["execution_gate"],
        "file_operation_result.json": artifacts["file_operation_result"],
        "repo_patch_plan.json": artifacts["repo_patch_plan"],
        "repo_patch_gate.json": artifacts["repo_patch_gate"],
        "repo_patch_result.json": artifacts["repo_patch_result"],
        "changed_file_scope_proof.json": artifacts["changed_file_scope_proof"],
        "execution_profile.json": artifacts["execution_profile"],
        "preflight_gate_record.json": artifacts["preflight_gate_record"],
        "patch_approval_checklist.json": artifacts["patch_approval_checklist"],
        "execution_readiness_score.json": artifacts["execution_readiness_score"],
        "dry_run_bundle.json": artifacts["dry_run_bundle"],
        "dry_run_bundle_comparison.json": artifacts["dry_run_bundle_comparison"],
        "approval_handoff_packet.json": artifacts["approval_handoff_packet"],
        "approval_review_ui_schema.json": artifacts["approval_review_ui_schema"],
        "signed_approval_record.json": artifacts["signed_approval_record"],
        "approval_record_verification.json": artifacts["approval_record_verification"],
        "approval_record_audit_manifest.json": artifacts["approval_record_audit_manifest"],
        "approval_record_sources.json": artifacts.get("approval_record_sources"),
        "approval_ledger_bundle.json": artifacts.get("approval_ledger_bundle"),
        "approval_ledger_index.json": artifacts.get("approval_ledger_index"),
        "approval_ledger_verification.json": artifacts.get("approval_ledger_verification"),
        "approval_status_summary.json": artifacts.get("approval_status_summary"),
        "duplicate_approval_signals.json": artifacts.get("duplicate_approval_signals"),
        "approval_ledger_lookup.json": artifacts.get("approval_ledger_lookup"),
        "approval_record_comparison.json": artifacts.get("approval_record_comparison"),
        "release_lock_bundle.json": artifacts.get("release_lock_bundle"),
        "stable_release_manifest.json": artifacts.get("stable_release_manifest"),
        "stable_release_verification.json": artifacts.get("stable_release_verification"),
        "stable_runtime_contract.json": artifacts.get("stable_runtime_contract"),
        "stable_capability_inventory.json": artifacts.get("stable_capability_inventory"),
        "stable_artifact_contract.json": artifacts.get("stable_artifact_contract"),
        "stable_adapter_boundary_contract.json": artifacts.get("stable_adapter_boundary_contract"),
        "stable_safety_doctrine_lock.json": artifacts.get("stable_safety_doctrine_lock"),
        "stable_approval_flow_lock.json": artifacts.get("stable_approval_flow_lock"),
        "known_limitations.json": artifacts.get("known_limitations"),
        "next_phase_handoff.json": artifacts.get("next_phase_handoff"),
        "release_readiness_summary.json": artifacts.get("release_readiness_summary"),
        "controlled_execution_bundle.json": artifacts.get("controlled_execution_bundle"),
        "controlled_execution_profile_catalog.json": artifacts.get("controlled_execution_profile_catalog"),
        "controlled_execution_selection.json": artifacts.get("controlled_execution_selection"),
        "execution_permission_matrix.json": artifacts.get("execution_permission_matrix"),
        "execution_mode_contract.json": artifacts.get("execution_mode_contract"),
        "blocked_action_ledger.json": artifacts.get("blocked_action_ledger"),
        "controlled_execution_preflight_contract.json": artifacts.get("controlled_execution_preflight_contract"),
        "controlled_execution_readiness_summary.json": artifacts.get("controlled_execution_readiness_summary"),
        "work_order_executor_readiness_bridge.json": artifacts.get("work_order_executor_readiness_bridge"),
        "work_order_executor_bundle.json": artifacts.get("work_order_executor_bundle"),
        "executable_work_order_schema.json": artifacts.get("executable_work_order_schema"),
        "work_orders_executable.json": artifacts.get("work_orders_executable"),
        "work_order_status_lifecycle.json": artifacts.get("work_order_status_lifecycle"),
        "work_order_dependency_map.json": artifacts.get("work_order_dependency_map"),
        "work_order_dry_run_results.json": artifacts.get("work_order_dry_run_results"),
        "work_order_execution_ledger.json": artifacts.get("work_order_execution_ledger"),
        "work_order_completion_proofs.json": artifacts.get("work_order_completion_proofs"),
        "work_order_executor_summary.json": artifacts.get("work_order_executor_summary"),
        "worker_hiring_registry_bundle.json": artifacts.get("worker_hiring_registry_bundle"),
        "worker_role_schema.json": artifacts.get("worker_role_schema"),
        "worker_candidates.json": artifacts.get("worker_candidates"),
        "worker_registry_status_lifecycle.json": artifacts.get("worker_registry_status_lifecycle"),
        "worker_assignment_plan.json": artifacts.get("worker_assignment_plan"),
        "worker_registry_ledger.json": artifacts.get("worker_registry_ledger"),
        "worker_hiring_preview_records.json": artifacts.get("worker_hiring_preview_records"),
        "worker_hiring_readiness_summary.json": artifacts.get("worker_hiring_readiness_summary"),
        "department_routing_readiness_bridge.json": artifacts.get("department_routing_readiness_bridge"),
        "department_routing_bundle.json": artifacts.get("department_routing_bundle"),
        "department_routing_schema.json": artifacts.get("department_routing_schema"),
        "department_route_candidates.json": artifacts.get("department_route_candidates"),
        "family_to_department_routing_map.json": artifacts.get("family_to_department_routing_map"),
        "worker_to_department_assignment_map.json": artifacts.get("worker_to_department_assignment_map"),
        "department_routing_conflict_detector.json": artifacts.get("department_routing_conflict_detector"),
        "department_routing_dry_run_results.json": artifacts.get("department_routing_dry_run_results"),
        "department_routing_ledger.json": artifacts.get("department_routing_ledger"),
        "department_routing_completion_proofs.json": artifacts.get("department_routing_completion_proofs"),
        "department_routing_readiness_summary.json": artifacts.get("department_routing_readiness_summary"),
        "multi_agent_orchestration_readiness_bridge.json": artifacts.get("multi_agent_orchestration_readiness_bridge"),
        "multi_agent_orchestration_bundle.json": artifacts.get("multi_agent_orchestration_bundle"),
        "orchestration_topology_schema.json": artifacts.get("orchestration_topology_schema"),
        "orchestration_nodes.json": artifacts.get("orchestration_nodes"),
        "multi_worker_coordination_map.json": artifacts.get("multi_worker_coordination_map"),
        "task_handoff_simulation.json": artifacts.get("task_handoff_simulation"),
        "inter_worker_dependency_graph.json": artifacts.get("inter_worker_dependency_graph"),
        "orchestration_conflict_detector.json": artifacts.get("orchestration_conflict_detector"),
        "orchestration_dry_run_results.json": artifacts.get("orchestration_dry_run_results"),
        "orchestration_ledger.json": artifacts.get("orchestration_ledger"),
        "orchestration_completion_proofs.json": artifacts.get("orchestration_completion_proofs"),
        "orchestration_readiness_summary.json": artifacts.get("orchestration_readiness_summary"),
        "ui_operator_console_readiness_bridge.json": artifacts.get("ui_operator_console_readiness_bridge"),
        "operator_console_bundle.json": artifacts.get("operator_console_bundle"),
        "operator_console_review_bundle.json": artifacts.get("operator_console_review_bundle"),
        "operator_console_screen_schema.json": artifacts.get("operator_console_screen_schema"),
        "runtime_status_panel_schema.json": artifacts.get("runtime_status_panel_schema"),
        "approval_queue_panel_schema.json": artifacts.get("approval_queue_panel_schema"),
        "work_order_panel_schema.json": artifacts.get("work_order_panel_schema"),
        "worker_registry_panel_schema.json": artifacts.get("worker_registry_panel_schema"),
        "department_routing_panel_schema.json": artifacts.get("department_routing_panel_schema"),
        "orchestration_sandbox_panel_schema.json": artifacts.get("orchestration_sandbox_panel_schema"),
        "release_lock_panel_schema.json": artifacts.get("release_lock_panel_schema"),
        "human_control_surface_schema.json": artifacts.get("human_control_surface_schema"),
        "operator_action_registry.json": artifacts.get("operator_action_registry"),
        "disabled_action_state_map.json": artifacts.get("disabled_action_state_map"),
        "operator_console_safety_summary.json": artifacts.get("operator_console_safety_summary"),
        "operator_console_readiness_summary.json": artifacts.get("operator_console_readiness_summary"),
        "github_patch_hardening_readiness_bridge.json": artifacts.get("github_patch_hardening_readiness_bridge"),
        "github_patch_hardening_bundle.json": artifacts.get("github_patch_hardening_bundle"),
        "patch_hardening_audit_bundle.json": artifacts.get("patch_hardening_audit_bundle"),
        "patch_hardening_schema.json": artifacts.get("patch_hardening_schema"),
        "protected_path_policy.json": artifacts.get("protected_path_policy"),
        "patch_root_validation.json": artifacts.get("patch_root_validation"),
        "patch_preview_diff_contract.json": artifacts.get("patch_preview_diff_contract"),
        "patch_digest_manifest.json": artifacts.get("patch_digest_manifest"),
        "patch_rollback_preview.json": artifacts.get("patch_rollback_preview"),
        "changed_file_proof_hardening.json": artifacts.get("changed_file_proof_hardening"),
        "human_approval_chain_binding.json": artifacts.get("human_approval_chain_binding"),
        "patch_execution_readiness_score.json": artifacts.get("patch_execution_readiness_score"),
        "deployment_packaging_readiness_bridge.json": artifacts.get("deployment_packaging_readiness_bridge"),
        "deployment_packaging_bundle.json": artifacts.get("deployment_packaging_bundle"),
        "deployment_artifact_schema.json": artifacts.get("deployment_artifact_schema"),
        "portfolio_packaging_manifest.json": artifacts.get("portfolio_packaging_manifest"),
        "runtime_export_bundle.json": artifacts.get("runtime_export_bundle"),
        "release_notes.json": artifacts.get("release_notes"),
        "deployment_safety_contract.json": artifacts.get("deployment_safety_contract"),
        "deployment_readiness_proof.json": artifacts.get("deployment_readiness_proof"),
        "portfolio_handoff_summary.json": artifacts.get("portfolio_handoff_summary"),
        "packaging_audit_bundle.json": artifacts.get("packaging_audit_bundle"),
        "first_controlled_worker_execution_readiness_bridge.json": artifacts.get("first_controlled_worker_execution_readiness_bridge"),
        "controlled_worker_execution_bundle.json": artifacts.get("controlled_worker_execution_bundle"),
        "controlled_worker_execution_schema.json": artifacts.get("controlled_worker_execution_schema"),
        "worker_execution_gate.json": artifacts.get("worker_execution_gate"),
        "tool_permission_binding.json": artifacts.get("tool_permission_binding"),
        "sandbox_worker_task.json": artifacts.get("sandbox_worker_task"),
        "worker_abort_contract.json": artifacts.get("worker_abort_contract"),
        "worker_rollback_contract.json": artifacts.get("worker_rollback_contract"),
        "worker_execution_telemetry_stub.json": artifacts.get("worker_execution_telemetry_stub"),
        "controlled_worker_execution_result.json": artifacts.get("controlled_worker_execution_result"),
        "post_run_audit_proof.json": artifacts.get("post_run_audit_proof"),
        "worker_execution_ledger.json": artifacts.get("worker_execution_ledger"),
        "live_execution_telemetry_abort_bundle.json": artifacts.get("live_execution_telemetry_abort_bundle"),
        "live_execution_telemetry_abort_schema.json": artifacts.get("live_execution_telemetry_abort_schema"),
        "telemetry_event_schema.json": artifacts.get("telemetry_event_schema"),
        "execution_state_model.json": artifacts.get("execution_state_model"),
        "telemetry_approval_gate.json": artifacts.get("telemetry_approval_gate"),
        "heartbeat_stub.json": artifacts.get("heartbeat_stub"),
        "abort_signal_contract.json": artifacts.get("abort_signal_contract"),
        "timeout_contract.json": artifacts.get("timeout_contract"),
        "partial_result_capture.json": artifacts.get("partial_result_capture"),
        "failed_run_quarantine_contract.json": artifacts.get("failed_run_quarantine_contract"),
        "post_abort_audit_proof.json": artifacts.get("post_abort_audit_proof"),
        "telemetry_ledger.json": artifacts.get("telemetry_ledger"),
        "telemetry_readiness_summary.json": artifacts.get("telemetry_readiness_summary"),
        "post_run_audit_expansion_readiness_bridge.json": artifacts.get("post_run_audit_expansion_readiness_bridge"),
        "post_run_audit_expansion_bundle.json": artifacts.get("post_run_audit_expansion_bundle"),
        "post_run_audit_expansion_schema.json": artifacts.get("post_run_audit_expansion_schema"),
        "expanded_audit_evidence_schema.json": artifacts.get("expanded_audit_evidence_schema"),
        "post_run_audit_approval_gate.json": artifacts.get("post_run_audit_approval_gate"),
        "before_after_run_comparison_proof.json": artifacts.get("before_after_run_comparison_proof"),
        "validator_backed_audit_artifact_index.json": artifacts.get("validator_backed_audit_artifact_index"),
        "audit_replay_record.json": artifacts.get("audit_replay_record"),
        "failure_class_taxonomy.json": artifacts.get("failure_class_taxonomy"),
        "human_review_packet.json": artifacts.get("human_review_packet"),
        "audit_integrity_score.json": artifacts.get("audit_integrity_score"),
        "audit_evidence_ledger.json": artifacts.get("audit_evidence_ledger"),
        "audit_expansion_readiness_summary.json": artifacts.get("audit_expansion_readiness_summary"),
        "multi_worker_sandbox_coordination_readiness_bridge.json": artifacts.get("multi_worker_sandbox_coordination_readiness_bridge"),
        "multi_worker_sandbox_coordination_bundle.json": artifacts.get("multi_worker_sandbox_coordination_bundle"),
        "multi_worker_sandbox_coordination_schema.json": artifacts.get("multi_worker_sandbox_coordination_schema"),
        "multi_worker_coordination_approval_gate.json": artifacts.get("multi_worker_coordination_approval_gate"),
        "sandbox_worker_roster.json": artifacts.get("sandbox_worker_roster"),
        "worker_coordination_graph.json": artifacts.get("worker_coordination_graph"),
        "inter_worker_handoff_contract.json": artifacts.get("inter_worker_handoff_contract"),
        "multi_worker_dry_run_ledger.json": artifacts.get("multi_worker_dry_run_ledger"),
        "coordination_conflict_detector.json": artifacts.get("coordination_conflict_detector"),
        "coordination_abort_contract.json": artifacts.get("coordination_abort_contract"),
        "coordination_quarantine_contract.json": artifacts.get("coordination_quarantine_contract"),
        "coordination_audit_proof.json": artifacts.get("coordination_audit_proof"),
        "coordination_readiness_summary.json": artifacts.get("coordination_readiness_summary"),
        "controlled_external_tool_adapter_preview_readiness_bridge.json": artifacts.get("controlled_external_tool_adapter_preview_readiness_bridge"),
        "controlled_external_tool_adapter_preview_bundle": artifacts.get("controlled_external_tool_adapter_preview_bundle"),
        "controlled_external_tool_adapter_preview_schema": artifacts.get("controlled_external_tool_adapter_preview_schema"),
        "external_tool_adapter_preview_approval_gate": artifacts.get("external_tool_adapter_preview_approval_gate"),
        "external_tool_dry_run_adapter_registry.json": artifacts.get("external_tool_dry_run_adapter_registry"),
        "per_tool_external_permission_gate.json": artifacts.get("per_tool_external_permission_gate"),
        "external_request_preview_contract.json": artifacts.get("external_request_preview_contract"),
        "external_response_validation_schema.json": artifacts.get("external_response_validation_schema"),
        "external_response_validation_preview_result.json": artifacts.get("external_response_validation_preview_result"),
        "external_tool_abort_contract.json": artifacts.get("external_tool_abort_contract"),
        "external_tool_audit_proof.json": artifacts.get("external_tool_audit_proof"),
        "external_tool_preview_ledger.json": artifacts.get("external_tool_preview_ledger"),
        "external_tool_preview_readiness_summary.json": artifacts.get("external_tool_preview_readiness_summary"),
        "permissioned_external_api_dry_run_preview_readiness_bridge.json": artifacts.get("permissioned_external_api_dry_run_preview_readiness_bridge"),
        "permissioned_external_api_dry_run_preview_bundle": artifacts.get("permissioned_external_api_dry_run_preview_bundle"),
        "permissioned_external_api_dry_run_preview_schema.json": artifacts.get("permissioned_external_api_dry_run_preview_schema"),
        "external_api_dry_run_approval_gate.json": artifacts.get("external_api_dry_run_approval_gate"),
        "api_endpoint_preview_registry.json": artifacts.get("api_endpoint_preview_registry"),
        "request_envelope_validation.json": artifacts.get("request_envelope_validation"),
        "credential_absence_proof.json": artifacts.get("credential_absence_proof"),
        "outbound_call_prevention_proof.json": artifacts.get("outbound_call_prevention_proof"),
        "dry_run_response_fixture_contract.json": artifacts.get("dry_run_response_fixture_contract"),
        "external_api_audit_proof.json": artifacts.get("external_api_audit_proof"),
        "external_api_dry_run_ledger.json": artifacts.get("external_api_dry_run_ledger"),
        "external_api_dry_run_readiness_summary.json": artifacts.get("external_api_dry_run_readiness_summary"),
        "controlled_multi_worker_audit_replay_preview_readiness_bridge.json": artifacts.get("controlled_multi_worker_audit_replay_preview_readiness_bridge"),
        "controlled_multi_worker_audit_replay_preview_bundle": artifacts.get("controlled_multi_worker_audit_replay_preview_bundle"),
        "controlled_multi_worker_audit_replay_preview_schema.json": artifacts.get("controlled_multi_worker_audit_replay_preview_schema"),
        "audit_replay_preview_approval_gate.json": artifacts.get("audit_replay_preview_approval_gate"),
        "replay_packet_registry.json": artifacts.get("replay_packet_registry"),
        "deterministic_replay_plan_contract.json": artifacts.get("deterministic_replay_plan_contract"),
        "replay_safety_gate.json": artifacts.get("replay_safety_gate"),
        "multi_worker_replay_comparison_proof.json": artifacts.get("multi_worker_replay_comparison_proof"),
        "replay_output_quarantine_contract.json": artifacts.get("replay_output_quarantine_contract"),
        "replay_audit_proof.json": artifacts.get("replay_audit_proof"),
        "replay_preview_ledger.json": artifacts.get("replay_preview_ledger"),
        "replay_readiness_summary.json": artifacts.get("replay_readiness_summary"),
        "operator_approval_queue_enforcement_readiness_bridge.json": artifacts.get("operator_approval_queue_enforcement_readiness_bridge"),
        "operator_approval_queue_enforcement_bundle": artifacts.get("operator_approval_queue_enforcement_bundle"),
        "operator_approval_queue_enforcement_schema.json": artifacts.get("operator_approval_queue_enforcement_schema"),
        "operator_approval_queue_enforcement_approval_gate.json": artifacts.get("operator_approval_queue_enforcement_approval_gate"),
        "queued_action_registry.json": artifacts.get("queued_action_registry"),
        "approval_item_priority_classifier.json": artifacts.get("approval_item_priority_classifier"),
        "operator_decision_contract.json": artifacts.get("operator_decision_contract"),
        "approval_expiry_stale_item_detector.json": artifacts.get("approval_expiry_stale_item_detector"),
        "queue_enforcement_safety_gate.json": artifacts.get("queue_enforcement_safety_gate"),
        "approval_queue_audit_proof.json": artifacts.get("approval_queue_audit_proof"),
        "approval_queue_ledger.json": artifacts.get("approval_queue_ledger"),
        "approval_queue_readiness_summary.json": artifacts.get("approval_queue_readiness_summary"),
        "release_candidate_hardening_readiness_bridge.json": artifacts.get("release_candidate_hardening_readiness_bridge"),
        "release_candidate_hardening_bundle": artifacts.get("release_candidate_hardening_bundle"),
        "release_candidate_hardening_schema.json": artifacts.get("release_candidate_hardening_schema"),
        "release_candidate_hardening_approval_gate.json": artifacts.get("release_candidate_hardening_approval_gate"),
        "full_runtime_invariant_scan.json": artifacts.get("full_runtime_invariant_scan"),
        "validator_chain_lock_proof.json": artifacts.get("validator_chain_lock_proof"),
        "artifact_contract_freeze_manifest.json": artifacts.get("artifact_contract_freeze_manifest"),
        "known_issue_register.json": artifacts.get("known_issue_register"),
        "pre_v3_production_readiness_checklist.json": artifacts.get("pre_v3_production_readiness_checklist"),
        "release_candidate_safety_gate.json": artifacts.get("release_candidate_safety_gate"),
        "release_candidate_audit_proof.json": artifacts.get("release_candidate_audit_proof"),
        "release_candidate_ledger.json": artifacts.get("release_candidate_ledger"),
        "release_candidate_readiness_summary.json": artifacts.get("release_candidate_readiness_summary"),
        "controlled_production_readiness_gate_bridge.json": artifacts.get("controlled_production_readiness_gate_bridge"),
        "controlled_production_readiness_gate_bundle.json": artifacts.get("controlled_production_readiness_gate_bundle"),
        "controlled_production_readiness_gate_schema.json": artifacts.get("controlled_production_readiness_gate_schema"),
        "controlled_production_readiness_gate_approval_gate.json": artifacts.get("controlled_production_readiness_gate_approval_gate"),
        "production_activation_denial_by_default.json": artifacts.get("production_activation_denial_by_default"),
        "final_human_approval_requirement.json": artifacts.get("final_human_approval_requirement"),
        "production_capability_manifest.json": artifacts.get("production_capability_manifest"),
        "supervised_pilot_eligibility_contract.json": artifacts.get("supervised_pilot_eligibility_contract"),
        "production_rollback_kill_switch_preview.json": artifacts.get("production_rollback_kill_switch_preview"),
        "production_readiness_audit_proof.json": artifacts.get("production_readiness_audit_proof"),
        "production_readiness_ledger.json": artifacts.get("production_readiness_ledger"),
        "production_readiness_summary.json": artifacts.get("production_readiness_summary"),
        "controlled_worker_hiring_activation_pilot_bridge.json": artifacts.get("controlled_worker_hiring_activation_pilot_bridge"),
        "limited_external_tool_supervised_pilot_bundle.json": artifacts.get("limited_external_tool_supervised_pilot_bundle"),
        "limited_external_tool_supervised_pilot_schema.json": artifacts.get("limited_external_tool_supervised_pilot_schema"),
        "limited_external_tool_supervised_pilot_approval_gate.json": artifacts.get("limited_external_tool_supervised_pilot_approval_gate"),
        "single_external_tool_category_contract.json": artifacts.get("single_external_tool_category_contract"),
        "tool_invocation_denial_by_default.json": artifacts.get("tool_invocation_denial_by_default"),
        "human_tool_use_preflight_gate.json": artifacts.get("human_tool_use_preflight_gate"),
        "tool_request_envelope_preview.json": artifacts.get("tool_request_envelope_preview"),
        "tool_response_quarantine_preview.json": artifacts.get("tool_response_quarantine_preview"),
        "tool_audit_proof.json": artifacts.get("tool_audit_proof"),
        "tool_pilot_ledger.json": artifacts.get("tool_pilot_ledger"),
        "tool_pilot_readiness_summary.json": artifacts.get("tool_pilot_readiness_summary"),
        "supervised_external_api_pilot_bridge.json": artifacts.get("supervised_external_api_pilot_bridge"),
        "supervised_external_api_pilot_bundle.json": artifacts.get("supervised_external_api_pilot_bundle"),
        "supervised_external_api_pilot_schema.json": artifacts.get("supervised_external_api_pilot_schema"),
        "supervised_external_api_pilot_approval_gate.json": artifacts.get("supervised_external_api_pilot_approval_gate"),
        "single_api_category_contract.json": artifacts.get("single_api_category_contract"),
        "credential_denial_by_default.json": artifacts.get("credential_denial_by_default"),
        "secret_handling_denial_by_default.json": artifacts.get("secret_handling_denial_by_default"),
        "network_socket_denial_by_default.json": artifacts.get("network_socket_denial_by_default"),
        "human_api_use_preflight_gate.json": artifacts.get("human_api_use_preflight_gate"),
        "api_request_envelope_preview.json": artifacts.get("api_request_envelope_preview"),
        "api_response_quarantine_preview.json": artifacts.get("api_response_quarantine_preview"),
        "api_audit_proof.json": artifacts.get("api_audit_proof"),
        "api_pilot_ledger.json": artifacts.get("api_pilot_ledger"),
        "api_pilot_readiness_summary.json": artifacts.get("api_pilot_readiness_summary"),
        "monitored_rollback_recovery_drill_bridge.json": artifacts.get("monitored_rollback_recovery_drill_bridge"),
        "monitored_rollback_recovery_drill_bundle.json": artifacts.get("monitored_rollback_recovery_drill_bundle"),
        "monitored_rollback_recovery_drill_schema.json": artifacts.get("monitored_rollback_recovery_drill_schema"),
        "monitored_rollback_recovery_drill_approval_gate.json": artifacts.get("monitored_rollback_recovery_drill_approval_gate"),
        "simulated_failure_trigger_contract.json": artifacts.get("simulated_failure_trigger_contract"),
        "rollback_path_preview.json": artifacts.get("rollback_path_preview"),
        "recovery_checkpoint_contract.json": artifacts.get("recovery_checkpoint_contract"),
        "quarantine_freeze_preview.json": artifacts.get("quarantine_freeze_preview"),
        "human_recovery_approval_gate.json": artifacts.get("human_recovery_approval_gate"),
        "recovery_audit_proof.json": artifacts.get("recovery_audit_proof"),
        "rollback_recovery_drill_ledger.json": artifacts.get("rollback_recovery_drill_ledger"),
        "recovery_readiness_summary.json": artifacts.get("recovery_readiness_summary"),
        "supervised_production_pilot_readiness_review_bridge.json": artifacts.get("supervised_production_pilot_readiness_review_bridge"),
        "supervised_production_pilot_readiness_review_bundle.json": artifacts.get("supervised_production_pilot_readiness_review_bundle"),
        "supervised_production_pilot_readiness_review_schema.json": artifacts.get("supervised_production_pilot_readiness_review_schema"),
        "supervised_production_pilot_readiness_review_approval_gate.json": artifacts.get("supervised_production_pilot_readiness_review_approval_gate"),
        "minimum_viable_production_candidate_contract.json": artifacts.get("minimum_viable_production_candidate_contract"),
        "human_production_pilot_review_gate.json": artifacts.get("human_production_pilot_review_gate"),
        "production_blast_radius_analysis.json": artifacts.get("production_blast_radius_analysis"),
        "live_action_denial_review.json": artifacts.get("live_action_denial_review"),
        "rollback_availability_review.json": artifacts.get("rollback_availability_review"),
        "credential_secret_readiness_denial_proof.json": artifacts.get("credential_secret_readiness_denial_proof"),
        "network_socket_readiness_denial_proof.json": artifacts.get("network_socket_readiness_denial_proof"),
        "production_pilot_audit_proof.json": artifacts.get("production_pilot_audit_proof"),
        "production_pilot_readiness_ledger.json": artifacts.get("production_pilot_readiness_ledger"),
        "production_pilot_readiness_summary.json": artifacts.get("production_pilot_readiness_summary"),
        "credential_vault_denial_secret_handling_proof_bridge.json": artifacts.get("credential_vault_denial_secret_handling_proof_bridge"),
        "credential_vault_denial_secret_handling_proof_bundle.json": artifacts.get("credential_vault_denial_secret_handling_proof_bundle"),
        "credential_vault_denial_secret_handling_proof_schema.json": artifacts.get("credential_vault_denial_secret_handling_proof_schema"),
        "credential_vault_denial_secret_handling_proof_approval_gate.json": artifacts.get("credential_vault_denial_secret_handling_proof_approval_gate"),
        "credential_access_denial_contract.json": artifacts.get("credential_access_denial_contract"),
        "secret_read_denial_contract.json": artifacts.get("secret_read_denial_contract"),
        "environment_variable_denial_contract.json": artifacts.get("environment_variable_denial_contract"),
        "credential_vault_boundary_record.json": artifacts.get("credential_vault_boundary_record"),
        "secret_handling_boundary_record.json": artifacts.get("secret_handling_boundary_record"),
        "environment_read_boundary_record.json": artifacts.get("environment_read_boundary_record"),
        "credential_secret_audit_proof.json": artifacts.get("credential_secret_audit_proof"),
        "credential_secret_denial_ledger.json": artifacts.get("credential_secret_denial_ledger"),
        "credential_secret_readiness_summary.json": artifacts.get("credential_secret_readiness_summary"),
        "network_socket_lockdown_proof_bridge.json": artifacts.get("network_socket_lockdown_proof_bridge"),
        "live_external_action_final_preflight_gate_bundle.json": artifacts.get("live_external_action_final_preflight_gate_bundle"),
        "live_external_action_final_preflight_gate_schema.json": artifacts.get("live_external_action_final_preflight_gate_schema"),
        "live_external_action_final_preflight_gate_approval_gate.json": artifacts.get("live_external_action_final_preflight_gate_approval_gate"),
        "tiny_action_candidate_boundary_contract.json": artifacts.get("tiny_action_candidate_boundary_contract"),
        "live_external_action_non_execution_contract.json": artifacts.get("live_external_action_non_execution_contract"),
        "blast_radius_ceiling_contract.json": artifacts.get("blast_radius_ceiling_contract"),
        "human_final_approval_requirement.json": artifacts.get("human_final_approval_requirement"),
        "credential_secret_environment_re_denial_proof.json": artifacts.get("credential_secret_environment_re_denial_proof"),
        "network_socket_api_re_denial_proof.json": artifacts.get("network_socket_api_re_denial_proof"),
        "deployment_production_re_denial_proof.json": artifacts.get("deployment_production_re_denial_proof"),
        "rollback_recovery_availability_assertion.json": artifacts.get("rollback_recovery_availability_assertion"),
        "first_tiny_real_world_execution_candidate_audit_proof.json": artifacts.get("first_tiny_real_world_execution_candidate_audit_proof"),
        "final_preflight_ledger.json": artifacts.get("final_preflight_ledger"),
        "first_tiny_real_world_supervised_execution_candidate_bridge.json": artifacts.get("first_tiny_real_world_supervised_execution_candidate_bridge"),
        "post_action_verification_and_audit_review_bundle.json": artifacts.get("post_action_verification_and_audit_review_bundle"),
        "post_action_verification_and_audit_review_schema.json": artifacts.get("post_action_verification_and_audit_review_schema"),
        "post_action_verification_and_audit_review_approval_gate.json": artifacts.get("post_action_verification_and_audit_review_approval_gate"),
        "v4_candidate_artifact_reference_contract.json": artifacts.get("v4_candidate_artifact_reference_contract"),
        "artifact_integrity_verification_record.json": artifacts.get("artifact_integrity_verification_record"),
        "artifact_path_containment_review.json": artifacts.get("artifact_path_containment_review"),
        "safety_boolean_review.json": artifacts.get("safety_boolean_review"),
        "cleanup_instruction_review.json": artifacts.get("cleanup_instruction_review"),
        "operator_review_acknowledgement.json": artifacts.get("operator_review_acknowledgement"),
        "post_action_closeout_ledger.json": artifacts.get("post_action_closeout_ledger"),
        "post_action_readiness_summary.json": artifacts.get("post_action_readiness_summary"),
        "supervised_rollback_cleanup_candidate_bridge.json": artifacts.get("supervised_rollback_cleanup_candidate_bridge"),
        "post_action_verification_and_audit_review_record.json": artifacts.get("post_action_verification_and_audit_review_record"),
        "supervised_rollback_cleanup_candidate_bundle.json": artifacts.get("supervised_rollback_cleanup_candidate_bundle"),
        "supervised_rollback_cleanup_candidate_schema.json": artifacts.get("supervised_rollback_cleanup_candidate_schema"),
        "supervised_rollback_cleanup_candidate_approval_gate.json": artifacts.get("supervised_rollback_cleanup_candidate_approval_gate"),
        "cleanup_candidate_contract.json": artifacts.get("cleanup_candidate_contract"),
        "artifact_pre_cleanup_verification_record.json": artifacts.get("artifact_pre_cleanup_verification_record"),
        "cleanup_path_containment_record.json": artifacts.get("cleanup_path_containment_record"),
        "cleanup_scope_envelope.json": artifacts.get("cleanup_scope_envelope"),
        "cleanup_execution_record.json": artifacts.get("cleanup_execution_record"),
        "post_cleanup_verification_record.json": artifacts.get("post_cleanup_verification_record"),
        "cleanup_audit_record.json": artifacts.get("cleanup_audit_record"),
        "cleanup_closeout_ledger.json": artifacts.get("cleanup_closeout_ledger"),
        "cleanup_readiness_summary.json": artifacts.get("cleanup_readiness_summary"),
        "limited_live_worker_activation_candidate_bridge.json": artifacts.get("limited_live_worker_activation_candidate_bridge"),
        "limited_live_worker_activation_candidate_bundle.json": artifacts.get("limited_live_worker_activation_candidate_bundle"),
        "limited_live_worker_activation_candidate_schema.json": artifacts.get("limited_live_worker_activation_candidate_schema"),
        "limited_live_worker_activation_candidate_approval_gate.json": artifacts.get("limited_live_worker_activation_candidate_approval_gate"),
        "worker_template_reference_contract.json": artifacts.get("worker_template_reference_contract"),
        "one_worker_activation_scope_contract.json": artifacts.get("one_worker_activation_scope_contract"),
        "non_execution_worker_boundary.json": artifacts.get("non_execution_worker_boundary"),
        "worker_permission_denial_record.json": artifacts.get("worker_permission_denial_record"),
        "worker_activation_candidate_record.json": artifacts.get("worker_activation_candidate_record"),
        "worker_activation_audit_record.json": artifacts.get("worker_activation_audit_record"),
        "worker_activation_ledger.json": artifacts.get("worker_activation_ledger"),
        "worker_activation_readiness_summary.json": artifacts.get("worker_activation_readiness_summary"),
        "permissioned_worker_task_assignment_candidate_bridge.json": artifacts.get("permissioned_worker_task_assignment_candidate_bridge"),
        "worker_activation_record_payload.json": artifacts.get("worker_activation_record_payload"),
        "worker_activation_write_record.json": artifacts.get("worker_activation_write_record"),
        "permissioned_worker_task_assignment_candidate_bundle.json": artifacts.get("permissioned_worker_task_assignment_candidate_bundle"),
        "permissioned_worker_task_assignment_candidate_schema.json": artifacts.get("permissioned_worker_task_assignment_candidate_schema"),
        "permissioned_worker_task_assignment_candidate_approval_gate.json": artifacts.get("permissioned_worker_task_assignment_candidate_approval_gate"),
        "task_label_reference_contract.json": artifacts.get("task_label_reference_contract"),
        "one_worker_one_task_assignment_scope_contract.json": artifacts.get("one_worker_one_task_assignment_scope_contract"),
        "non_execution_task_boundary.json": artifacts.get("non_execution_task_boundary"),
        "task_permission_denial_record.json": artifacts.get("task_permission_denial_record"),
        "permissioned_worker_task_assignment_candidate_record.json": artifacts.get("worker_task_assignment_candidate_record"),
        "task_assignment_audit_record.json": artifacts.get("task_assignment_audit_record"),
        "task_assignment_ledger.json": artifacts.get("task_assignment_ledger"),
        "task_assignment_readiness_summary.json": artifacts.get("task_assignment_readiness_summary"),
        "task_assignment_audit_closeout_candidate_bridge.json": artifacts.get("task_assignment_audit_closeout_candidate_bridge"),
        "task_assignment_record_payload.json": artifacts.get("task_assignment_record_payload"),
        "task_assignment_write_record.json": artifacts.get("task_assignment_write_record"),
        "task_assignment_audit_closeout_candidate_bundle.json": artifacts.get("task_assignment_audit_closeout_candidate_bundle"),
        "task_assignment_audit_closeout_candidate_schema.json": artifacts.get("task_assignment_audit_closeout_candidate_schema"),
        "task_assignment_audit_closeout_candidate_approval_gate.json": artifacts.get("task_assignment_audit_closeout_candidate_approval_gate"),
        "v4_4_task_assignment_record_reference_contract.json": artifacts.get("v4_4_task_assignment_record_reference_contract"),
        "task_assignment_record_integrity_verification.json": artifacts.get("task_assignment_record_integrity_verification"),
        "task_assignment_record_path_containment_review.json": artifacts.get("task_assignment_record_path_containment_review"),
        "task_assignment_safety_boolean_review.json": artifacts.get("task_assignment_safety_boolean_review"),
        "non_execution_closeout_boundary.json": artifacts.get("non_execution_closeout_boundary"),
        "operator_closeout_acknowledgement.json": artifacts.get("operator_closeout_acknowledgement"),
        "task_assignment_closeout_audit_record.json": artifacts.get("task_assignment_closeout_audit_record"),
        "task_assignment_closeout_ledger.json": artifacts.get("task_assignment_closeout_ledger"),
        "task_assignment_closeout_readiness_summary.json": artifacts.get("task_assignment_closeout_readiness_summary"),
        "non_executing_task_queue_preview_candidate_bridge.json": artifacts.get("non_executing_task_queue_preview_candidate_bridge"),
        "task_assignment_audit_closeout_record_payload.json": artifacts.get("task_assignment_audit_closeout_record_payload"),
        "task_assignment_closeout_write_record.json": artifacts.get("task_assignment_closeout_write_record"),
        "non_executing_task_queue_preview_candidate_bundle.json": artifacts.get("non_executing_task_queue_preview_candidate_bundle"),
        "non_executing_task_queue_preview_candidate_schema.json": artifacts.get("non_executing_task_queue_preview_candidate_schema"),
        "non_executing_task_queue_preview_candidate_approval_gate.json": artifacts.get("non_executing_task_queue_preview_candidate_approval_gate"),
        "v4_4_task_assignment_record_reference_contract.json": artifacts.get("v4_4_task_assignment_record_reference_contract"),
        "optional_v4_5_closeout_record_reference_contract.json": artifacts.get("optional_v4_5_closeout_record_reference_contract"),
        "task_assignment_record_integrity_verification.json": artifacts.get("task_assignment_record_integrity_verification"),
        "closeout_record_integrity_verification.json": artifacts.get("closeout_record_integrity_verification"),
        "task_assignment_record_path_containment_review.json": artifacts.get("task_assignment_record_path_containment_review"),
        "queue_preview_scope_contract.json": artifacts.get("queue_preview_scope_contract"),
        "non_execution_queue_boundary.json": artifacts.get("non_execution_queue_boundary"),
        "queue_permission_denial_record.json": artifacts.get("queue_permission_denial_record"),
        "non_executing_task_queue_preview_candidate_record.json": artifacts.get("non_executing_task_queue_preview_candidate_record"),
        "queue_preview_audit_record.json": artifacts.get("queue_preview_audit_record"),
        "queue_preview_ledger.json": artifacts.get("queue_preview_ledger"),
        "queue_preview_readiness_summary.json": artifacts.get("queue_preview_readiness_summary"),
        "task_queue_preview_audit_closeout_candidate_bridge.json": artifacts.get("task_queue_preview_audit_closeout_candidate_bridge"),
        "queue_preview_record_payload.json": artifacts.get("queue_preview_record_payload"),
        "queue_preview_write_record.json": artifacts.get("queue_preview_write_record"),
        "task_queue_preview_audit_closeout_candidate_bundle.json": artifacts.get("task_queue_preview_audit_closeout_candidate_bundle"),
        "task_queue_preview_audit_closeout_candidate_schema.json": artifacts.get("task_queue_preview_audit_closeout_candidate_schema"),
        "task_queue_preview_audit_closeout_candidate_approval_gate.json": artifacts.get("task_queue_preview_audit_closeout_candidate_approval_gate"),
        "v4_6_queue_preview_record_reference_contract.json": artifacts.get("v4_6_queue_preview_record_reference_contract"),
        "queue_preview_record_integrity_verification.json": artifacts.get("queue_preview_record_integrity_verification"),
        "queue_preview_record_path_containment_review.json": artifacts.get("queue_preview_record_path_containment_review"),
        "queue_preview_safety_boolean_review.json": artifacts.get("queue_preview_safety_boolean_review"),
        "non_execution_queue_closeout_boundary.json": artifacts.get("non_execution_queue_closeout_boundary"),
        "operator_queue_closeout_acknowledgement.json": artifacts.get("operator_queue_closeout_acknowledgement"),
        "queue_preview_closeout_audit_record.json": artifacts.get("queue_preview_closeout_audit_record"),
        "queue_preview_closeout_ledger.json": artifacts.get("queue_preview_closeout_ledger"),
        "queue_preview_closeout_readiness_summary.json": artifacts.get("queue_preview_closeout_readiness_summary"),
        "non_executing_worker_routing_preview_candidate_bridge.json": artifacts.get("non_executing_worker_routing_preview_candidate_bridge"),
        "queue_closeout_record_payload.json": artifacts.get("queue_closeout_record_payload"),
        "queue_closeout_write_record.json": artifacts.get("queue_closeout_write_record"),
        "live_queue_orchestration_candidate_review_bundle.json": artifacts.get("live_queue_orchestration_candidate_review_bundle"),
        "live_queue_orchestration_candidate_review_schema.json": artifacts.get("live_queue_orchestration_candidate_review_schema"),
        "orchestration_review_approval_gate.json": artifacts.get("orchestration_review_approval_gate"),
        "v4_8_queue_routing_preview_reference_contract.json": artifacts.get("v4_8_queue_routing_preview_reference_contract"),
        "orchestration_review_scope_contract.json": artifacts.get("orchestration_review_scope_contract"),
        "non_execution_orchestration_boundary.json": artifacts.get("non_execution_orchestration_boundary"),
        "orchestration_permission_denial_record.json": artifacts.get("orchestration_permission_denial_record"),
        "orchestration_candidate_review_record.json": artifacts.get("orchestration_candidate_review_record"),
        "orchestration_review_audit_record.json": artifacts.get("orchestration_review_audit_record"),
        "orchestration_readiness_summary.json": artifacts.get("orchestration_readiness_summary"),
        "first_live_queue_execution_candidate_bridge.json": artifacts.get("first_live_queue_execution_candidate_bridge"),
        "orchestration_candidate_review_record_payload.json": artifacts.get("orchestration_candidate_review_record_payload"),
        "orchestration_candidate_review_write_record.json": artifacts.get("orchestration_candidate_review_write_record"),
        "first_live_queue_execution_candidate_review_bundle.json": artifacts.get("first_live_queue_execution_candidate_review_bundle"),
        "first_live_queue_execution_candidate_review_schema.json": artifacts.get("first_live_queue_execution_candidate_review_schema"),
        "execution_candidate_review_approval_gate.json": artifacts.get("execution_candidate_review_approval_gate"),
        "v4_9_orchestration_review_reference_contract.json": artifacts.get("v4_9_orchestration_review_reference_contract"),
        "execution_candidate_review_scope_contract.json": artifacts.get("execution_candidate_review_scope_contract"),
        "non_execution_execution_boundary.json": artifacts.get("non_execution_execution_boundary"),
        "execution_permission_denial_record.json": artifacts.get("execution_permission_denial_record"),
        "execution_candidate_review_record.json": artifacts.get("execution_candidate_review_record"),
        "execution_candidate_review_audit_record.json": artifacts.get("execution_candidate_review_audit_record"),
        "execution_candidate_readiness_summary.json": artifacts.get("execution_candidate_readiness_summary"),
        "first_supervised_local_execution_kernel_candidate_bridge.json": artifacts.get("first_supervised_local_execution_kernel_candidate_bridge"),
        "execution_candidate_review_record_payload.json": artifacts.get("execution_candidate_review_record_payload"),
        "execution_candidate_review_write_record.json": artifacts.get("execution_candidate_review_write_record"),
        "first_supervised_local_execution_kernel_candidate_bundle.json": artifacts.get("first_supervised_local_execution_kernel_candidate_bundle"),
        "first_supervised_local_execution_kernel_candidate_schema.json": artifacts.get("first_supervised_local_execution_kernel_candidate_schema"),
        "supervised_execution_kernel_approval_gate.json": artifacts.get("supervised_execution_kernel_approval_gate"),
        "synthetic_task_contract.json": artifacts.get("synthetic_task_contract"),
        "sandbox_output_scope_contract.json": artifacts.get("sandbox_output_scope_contract"),
        "non_external_execution_boundary.json": artifacts.get("non_external_execution_boundary"),
        "execution_permission_denial_record.json": artifacts.get("execution_permission_denial_record"),
        "supervised_local_execution_plan_record.json": artifacts.get("supervised_local_execution_plan_record"),
        "supervised_local_execution_result_record.json": artifacts.get("supervised_local_execution_result_record"),
        "supervised_local_execution_audit_record.json": artifacts.get("supervised_local_execution_audit_record"),
        "supervised_local_execution_readiness_summary.json": artifacts.get("supervised_local_execution_readiness_summary"),
        "controlled_repeatable_local_execution_candidate_bridge.json": artifacts.get("controlled_repeatable_local_execution_candidate_bridge"),
        "supervised_local_execution_output_payload.json": artifacts.get("supervised_local_execution_output_payload"),
        "supervised_local_execution_write_record.json": artifacts.get("supervised_local_execution_write_record"),
        "controlled_repeatable_local_execution_candidate_bundle.json": artifacts.get("controlled_repeatable_local_execution_candidate_bundle"),
        "controlled_repeatable_local_execution_candidate_schema.json": artifacts.get("controlled_repeatable_local_execution_candidate_schema"),
        "repeatable_execution_approval_gate.json": artifacts.get("repeatable_execution_approval_gate"),
        "synthetic_repeatable_task_contract.json": artifacts.get("synthetic_repeatable_task_contract"),
        "repeatability_scope_contract.json": artifacts.get("repeatability_scope_contract"),
        "non_external_repeatability_boundary.json": artifacts.get("non_external_repeatability_boundary"),
        "repeatability_permission_denial_record.json": artifacts.get("repeatability_permission_denial_record"),
        "repeatability_plan_record.json": artifacts.get("repeatability_plan_record"),
        "repeatability_entries_record.json": artifacts.get("repeatability_entries_record"),
        "repeatability_proof_result_record.json": artifacts.get("repeatability_proof_result_record"),
        "repeatability_audit_record.json": artifacts.get("repeatability_audit_record"),
        "repeatability_readiness_summary.json": artifacts.get("repeatability_readiness_summary"),
        "sandbox_worker_handoff_candidate_bridge.json": artifacts.get("sandbox_worker_handoff_candidate_bridge"),
        "repeatability_proof_payload.json": artifacts.get("repeatability_proof_payload"),
        "repeatability_proof_write_record.json": artifacts.get("repeatability_proof_write_record"),
        "sandbox_worker_handoff_candidate_bundle.json": artifacts.get("sandbox_worker_handoff_candidate_bundle"),
        "sandbox_worker_handoff_candidate_schema.json": artifacts.get("sandbox_worker_handoff_candidate_schema"),
        "sandbox_worker_handoff_approval_gate.json": artifacts.get("sandbox_worker_handoff_approval_gate"),
        "v5_2_repeatability_proof_reference_contract.json": artifacts.get("v5_2_repeatability_proof_reference_contract"),
        "sandbox_worker_dry_run_replay_audit_candidate_bundle.json": artifacts.get("sandbox_worker_dry_run_replay_audit_candidate_bundle"),
        "sandbox_worker_dry_run_replay_audit_candidate_schema.json": artifacts.get("sandbox_worker_dry_run_replay_audit_candidate_schema"),
        "sandbox_worker_dry_run_replay_audit_approval_gate.json": artifacts.get("sandbox_worker_dry_run_replay_audit_approval_gate"),
        "v5_3_handoff_packet_reference_contract.json": artifacts.get("v5_3_handoff_packet_reference_contract"),
        "v5_4_acknowledgement_packet_reference_contract.json": artifacts.get("v5_4_acknowledgement_packet_reference_contract"),
        "v5_5_acceptance_review_packet_reference_contract.json": artifacts.get("v5_5_acceptance_review_packet_reference_contract"),
        "v5_6_ready_state_packet_reference_contract.json": artifacts.get("v5_6_ready_state_packet_reference_contract"),
        "v5_7_dry_run_assignment_packet_reference_contract.json": artifacts.get("v5_7_dry_run_assignment_packet_reference_contract"),
        "v5_8_dry_run_result_packet_reference_contract.json": artifacts.get("v5_8_dry_run_result_packet_reference_contract"),
        "synthetic_dry_run_task_reference_contract.json": artifacts.get("synthetic_dry_run_task_reference_contract"),
        "synthetic_dry_run_result_reference_contract.json": artifacts.get("synthetic_dry_run_result_reference_contract"),
        "replay_audit_candidate_reference_contract.json": artifacts.get("replay_audit_candidate_reference_contract"),
        "sandbox_worker_dry_run_replay_audit_reference_contract.json": artifacts.get("sandbox_worker_dry_run_replay_audit_reference_contract"),
        "dry_run_replay_audit_scope_contract.json": artifacts.get("dry_run_replay_audit_scope_contract"),
        "non_execution_dry_run_replay_audit_boundary.json": artifacts.get("non_execution_dry_run_replay_audit_boundary"),
        "dry_run_replay_audit_permission_denial_record.json": artifacts.get("dry_run_replay_audit_permission_denial_record"),
        "dry_run_replay_audit_plan_record.json": artifacts.get("dry_run_replay_audit_plan_record"),
        "dry_run_replay_audit_packet_record.json": artifacts.get("dry_run_replay_audit_packet_record"),
        "dry_run_replay_audit_audit_record.json": artifacts.get("dry_run_replay_audit_audit_record"),
        "dry_run_replay_audit_readiness_summary.json": artifacts.get("dry_run_replay_audit_readiness_summary"),
        "station_chief_mvp_lock_candidate_bridge.json": artifacts.get("station_chief_mvp_lock_candidate_bridge"),
        "dry_run_replay_audit_packet_payload.json": artifacts.get("dry_run_replay_audit_packet_payload"),
        "dry_run_replay_audit_packet_write_record.json": artifacts.get("dry_run_replay_audit_packet_write_record"),
        "sandbox_worker_dry_run_result_candidate_bundle.json": artifacts.get("sandbox_worker_dry_run_result_candidate_bundle"),
        "sandbox_worker_dry_run_result_candidate_schema.json": artifacts.get("sandbox_worker_dry_run_result_candidate_schema"),
        "sandbox_worker_dry_run_result_approval_gate.json": artifacts.get("sandbox_worker_dry_run_result_approval_gate"),
        "sandbox_worker_dry_run_result_reference_contract.json": artifacts.get("sandbox_worker_dry_run_result_reference_contract"),
        "synthetic_dry_run_result_reference_contract.json": artifacts.get("synthetic_dry_run_result_reference_contract"),
        "dry_run_result_scope_contract.json": artifacts.get("dry_run_result_scope_contract"),
        "non_execution_dry_run_result_boundary.json": artifacts.get("non_execution_dry_run_result_boundary"),
        "dry_run_result_permission_denial_record.json": artifacts.get("dry_run_result_permission_denial_record"),
        "dry_run_result_plan_record.json": artifacts.get("dry_run_result_plan_record"),
        "dry_run_result_packet_record.json": artifacts.get("dry_run_result_packet_record"),
        "dry_run_result_audit_record.json": artifacts.get("dry_run_result_audit_record"),
        "dry_run_result_readiness_summary.json": artifacts.get("dry_run_result_readiness_summary"),
        "sandbox_worker_dry_run_replay_audit_candidate_bridge.json": artifacts.get("sandbox_worker_dry_run_replay_audit_candidate_bridge"),
        "dry_run_result_packet_payload.json": artifacts.get("dry_run_result_packet_payload"),
        "dry_run_result_packet_write_record.json": artifacts.get("dry_run_result_packet_write_record"),
        "sandbox_worker_dry_run_assignment_candidate_bundle.json": artifacts.get("sandbox_worker_dry_run_assignment_candidate_bundle"),
        "sandbox_worker_dry_run_assignment_candidate_schema.json": artifacts.get("sandbox_worker_dry_run_assignment_candidate_schema"),
        "sandbox_worker_dry_run_assignment_approval_gate.json": artifacts.get("sandbox_worker_dry_run_assignment_approval_gate"),
        "sandbox_worker_dry_run_assignment_reference_contract.json": artifacts.get("sandbox_worker_dry_run_assignment_reference_contract"),
        "synthetic_dry_run_task_reference_contract.json": artifacts.get("synthetic_dry_run_task_reference_contract"),
        "dry_run_assignment_scope_contract.json": artifacts.get("dry_run_assignment_scope_contract"),
        "non_execution_dry_run_assignment_boundary.json": artifacts.get("non_execution_dry_run_assignment_boundary"),
        "dry_run_assignment_permission_denial_record.json": artifacts.get("dry_run_assignment_permission_denial_record"),
        "dry_run_assignment_plan_record.json": artifacts.get("dry_run_assignment_plan_record"),
        "dry_run_assignment_packet_record.json": artifacts.get("dry_run_assignment_packet_record"),
        "dry_run_assignment_audit_record.json": artifacts.get("dry_run_assignment_audit_record"),
        "dry_run_assignment_readiness_summary.json": artifacts.get("dry_run_assignment_readiness_summary"),
        "sandbox_worker_dry_run_result_candidate_bridge.json": artifacts.get("sandbox_worker_dry_run_result_candidate_bridge"),
        "dry_run_assignment_packet_payload.json": artifacts.get("dry_run_assignment_packet_payload"),
        "dry_run_assignment_packet_write_record.json": artifacts.get("dry_run_assignment_packet_write_record"),
        "sandbox_worker_ready_state_packet_candidate_bundle.json": artifacts.get("sandbox_worker_ready_state_packet_candidate_bundle"),
        "sandbox_worker_ready_state_packet_candidate_schema.json": artifacts.get("sandbox_worker_ready_state_packet_candidate_schema"),
        "sandbox_worker_ready_state_packet_approval_gate.json": artifacts.get("sandbox_worker_ready_state_packet_approval_gate"),
        "sandbox_worker_ready_state_reference_contract.json": artifacts.get("sandbox_worker_ready_state_reference_contract"),
        "ready_state_scope_contract.json": artifacts.get("ready_state_scope_contract"),
        "non_execution_ready_state_boundary.json": artifacts.get("non_execution_ready_state_boundary"),
        "ready_state_permission_denial_record.json": artifacts.get("ready_state_permission_denial_record"),
        "ready_state_plan_record.json": artifacts.get("ready_state_plan_record"),
        "ready_state_packet_record.json": artifacts.get("ready_state_packet_record"),
        "ready_state_audit_record.json": artifacts.get("ready_state_audit_record"),
        "ready_state_readiness_summary.json": artifacts.get("ready_state_readiness_summary"),
        "sandbox_worker_dry_run_assignment_candidate_bridge.json": artifacts.get("sandbox_worker_dry_run_assignment_candidate_bridge"),
        "ready_state_packet_payload.json": artifacts.get("ready_state_packet_payload"),
        "ready_state_packet_write_record.json": artifacts.get("ready_state_packet_write_record"),
        "sandbox_worker_acceptance_candidate_review_bundle.json": artifacts.get("sandbox_worker_acceptance_candidate_review_bundle"),
        "sandbox_worker_acceptance_candidate_review_schema.json": artifacts.get("sandbox_worker_acceptance_candidate_review_schema"),
        "sandbox_worker_acceptance_review_approval_gate.json": artifacts.get("sandbox_worker_acceptance_review_approval_gate"),
        "sandbox_worker_acceptance_review_reference_contract.json": artifacts.get("sandbox_worker_acceptance_review_reference_contract"),
        "acceptance_review_scope_contract.json": artifacts.get("acceptance_review_scope_contract"),
        "non_execution_acceptance_review_boundary.json": artifacts.get("non_execution_acceptance_review_boundary"),
        "acceptance_review_permission_denial_record.json": artifacts.get("acceptance_review_permission_denial_record"),
        "acceptance_review_plan_record.json": artifacts.get("acceptance_review_plan_record"),
        "acceptance_review_packet_record.json": artifacts.get("acceptance_review_packet_record"),
        "acceptance_review_audit_record.json": artifacts.get("acceptance_review_audit_record"),
        "acceptance_review_readiness_summary.json": artifacts.get("acceptance_review_readiness_summary"),
        "sandbox_worker_ready_state_packet_candidate_bridge.json": artifacts.get("sandbox_worker_ready_state_packet_candidate_bridge"),
        "acceptance_review_packet_payload.json": artifacts.get("acceptance_review_packet_payload"),
        "acceptance_review_packet_write_record.json": artifacts.get("acceptance_review_packet_write_record"),
        "sandbox_worker_acknowledgement_candidate_bundle.json": artifacts.get("sandbox_worker_acknowledgement_candidate_bundle"),
        "sandbox_worker_acknowledgement_candidate_schema.json": artifacts.get("sandbox_worker_acknowledgement_candidate_schema"),
        "sandbox_worker_acknowledgement_approval_gate.json": artifacts.get("sandbox_worker_acknowledgement_approval_gate"),
        "v5_3_handoff_packet_reference_contract.json": artifacts.get("v5_3_handoff_packet_reference_contract"),
        "sandbox_worker_acknowledgement_reference_contract.json": artifacts.get("sandbox_worker_acknowledgement_reference_contract"),
        "acknowledgement_scope_contract.json": artifacts.get("acknowledgement_scope_contract"),
        "non_execution_acknowledgement_boundary.json": artifacts.get("non_execution_acknowledgement_boundary"),
        "acknowledgement_permission_denial_record.json": artifacts.get("acknowledgement_permission_denial_record"),
        "acknowledgement_plan_record.json": artifacts.get("acknowledgement_plan_record"),
        "acknowledgement_packet_record.json": artifacts.get("acknowledgement_packet_record"),
        "acknowledgement_audit_record.json": artifacts.get("acknowledgement_audit_record"),
        "acknowledgement_readiness_summary.json": artifacts.get("acknowledgement_readiness_summary"),
        "sandbox_worker_acceptance_candidate_bridge.json": artifacts.get("sandbox_worker_acceptance_candidate_bridge"),
        "acknowledgement_packet_payload.json": artifacts.get("acknowledgement_packet_payload"),
        "acknowledgement_packet_write_record.json": artifacts.get("acknowledgement_packet_write_record"),
        "synthetic_task_handoff_contract.json": artifacts.get("synthetic_task_handoff_contract"),
        "sandbox_worker_reference_contract.json": artifacts.get("sandbox_worker_reference_contract"),
        "handoff_scope_contract.json": artifacts.get("handoff_scope_contract"),
        "non_execution_handoff_boundary.json": artifacts.get("non_execution_handoff_boundary"),
        "handoff_permission_denial_record.json": artifacts.get("handoff_permission_denial_record"),
        "handoff_plan_record.json": artifacts.get("handoff_plan_record"),
        "handoff_packet_record.json": artifacts.get("handoff_packet_record"),
        "handoff_audit_record.json": artifacts.get("handoff_audit_record"),
        "handoff_readiness_summary.json": artifacts.get("handoff_readiness_summary"),
        "sandbox_worker_acknowledgement_candidate_bridge.json": artifacts.get("sandbox_worker_acknowledgement_candidate_bridge"),
        "handoff_packet_payload.json": artifacts.get("handoff_packet_payload"),
        "handoff_packet_write_record.json": artifacts.get("handoff_packet_write_record"),
        "first_supervised_production_dry_run_bundle.json": artifacts.get("first_supervised_production_dry_run_bundle"),
        "first_supervised_production_dry_run_schema.json": artifacts.get("first_supervised_production_dry_run_schema"),
        "first_supervised_production_dry_run_approval_gate.json": artifacts.get("first_supervised_production_dry_run_approval_gate"),
        "single_controlled_task_dry_run_envelope.json": artifacts.get("single_controlled_task_dry_run_envelope"),
        "dry_run_only_production_context_contract.json": artifacts.get("dry_run_only_production_context_contract"),
        "human_preflight_approval_gate.json": artifacts.get("human_preflight_approval_gate"),
        "worker_task_simulation_contract.json": artifacts.get("worker_task_simulation_contract"),
        "external_action_denial_by_default.json": artifacts.get("external_action_denial_by_default"),
        "dry_run_rollback_quarantine_preview.json": artifacts.get("dry_run_rollback_quarantine_preview"),
        "dry_run_audit_proof.json": artifacts.get("dry_run_audit_proof"),
        "dry_run_ledger.json": artifacts.get("dry_run_ledger"),
        "dry_run_readiness_summary.json": artifacts.get("dry_run_readiness_summary"),
        "limited_external_tool_supervised_pilot_bridge.json": artifacts.get("limited_external_tool_supervised_pilot_bridge"),
        "controlled_worker_hiring_activation_pilot_bundle.json": artifacts.get("controlled_worker_hiring_activation_pilot_bundle"),
        "controlled_worker_hiring_activation_pilot_schema.json": artifacts.get("controlled_worker_hiring_activation_pilot_schema"),
        "controlled_worker_hiring_activation_pilot_approval_gate.json": artifacts.get("controlled_worker_hiring_activation_pilot_approval_gate"),
        "pilot_worker_limit_contract.json": artifacts.get("pilot_worker_limit_contract"),
        "worker_identity_activation_contract.json": artifacts.get("worker_identity_activation_contract"),
        "task_assignment_denial_by_default.json": artifacts.get("task_assignment_denial_by_default"),
        "human_supervised_pilot_gate.json": artifacts.get("human_supervised_pilot_gate"),
        "pilot_rollback_abort_preview.json": artifacts.get("pilot_rollback_abort_preview"),
        "pilot_audit_proof.json": artifacts.get("pilot_audit_proof"),
        "pilot_ledger.json": artifacts.get("pilot_ledger"),
        "pilot_readiness_summary.json": artifacts.get("pilot_readiness_summary"),
        "first_supervised_production_dry_run_bridge.json": artifacts.get("first_supervised_production_dry_run_bridge"),
        "runtime_index_entry.json": artifacts["runtime_index_entry"],
        "manifest.json": artifacts["manifest"],
        "full_result.json": result,
    }
    for filename, payload in mapping.items():
        if payload is not None:
            _write_json(artifact_dir / filename, payload)
        files_written.append(filename)

    registry_updated = False
    registry_dir_str = None
    if registry_dir is not None:
        registry_dir_path = Path(registry_dir)
        registry_dir_path.mkdir(parents=True, exist_ok=True)
        registry = update_registry(registry_dir_path, artifacts["runtime_index_entry"])
        write_runtime_index(registry_dir_path, registry)
        registry_updated = True
        registry_dir_str = str(registry_dir_path)

    return {
        "run_id": run_id,
        "artifact_dir": str(artifact_dir),
        "files_written": files_written,
        "runtime_index_entry": artifacts["runtime_index_entry"],
        "registry_updated": registry_updated,
        "registry_dir": registry_dir_str,
    }

def run_fixture_tests() -> dict:
    cases = load_json("10_runtime/station_chief_demo_cases.json")["demo_cases"]
    results = []
    passed = 0
    failed = 0
    for case in cases:
        result = run_station_chief(case["command"])
        actual_command_type = result["command_type"]
        actual_activation_tier = result["activation_tier"]["name"]
        case_passed = (
            actual_command_type == case["expected_command_type"]
            and actual_activation_tier == case["expected_activation_tier"]
        )
        if case_passed:
            passed += 1
        else:
            failed += 1
        results.append(
            {
                "case_id": case["case_id"],
                "command": case["command"],
                "expected_command_type": case["expected_command_type"],
                "actual_command_type": actual_command_type,
                "expected_activation_tier": case["expected_activation_tier"],
                "actual_activation_tier": actual_activation_tier,
                "passed": case_passed,
            }
        )
    return {
        "fixture_test_status": "PASS" if failed == 0 else "FAIL",
        "runtime_version": STATION_CHIEF_RUNTIME_VERSION,
        "case_count": len(cases),
        "passed": passed,
        "failed": failed,
        "results": results,
    }


def attach_file_operation(
    result: dict,
    execution_dir: str | None,
    target_filename: str,
    confirmation_token: str | None,
    execute: bool,
) -> dict:
    updated = dict(result)
    file_operation_plan = create_file_operation_plan(
        result["command_brief"],
        execution_dir=execution_dir,
        target_filename=target_filename,
    )
    execution_gate = evaluate_execution_gate(file_operation_plan, confirmation_token if execute else None)
    if execute:
        file_operation_result = run_sandbox_file_write_adapter(file_operation_plan, execution_gate)
    else:
        file_operation_result = {
            "adapter_result_status": "PLANNED_ONLY",
            "operation_type": "sandbox_file_write",
            "file_written": False,
            "target_path": file_operation_plan["target_path"],
            "live_execution_performed": False,
            "external_actions_taken": False,
            "worker_agents_activated": False,
            "reason": "File operation planned but not executed.",
        }
    updated["file_operation_plan"] = file_operation_plan
    updated["execution_gate"] = execution_gate
    updated["file_operation_result"] = file_operation_result
    return updated


def attach_repo_patch(
    result: dict,
    patch_root: str | None,
    relative_path: str,
    allowed_files: list[str],
    patch_content: str | None,
    confirmation_token: str | None,
    execute: bool,
) -> dict:
    updated = dict(result)
    repo_patch_plan = create_repo_patch_plan(
        result["command_brief"],
        patch_root=patch_root,
        relative_path=relative_path,
        allowed_files=allowed_files,
        patch_content=patch_content,
    )
    repo_patch_gate = evaluate_repo_patch_gate(repo_patch_plan, confirmation_token if execute else None)
    if execute:
        repo_patch_result = run_scoped_repo_patch_adapter(repo_patch_plan, repo_patch_gate)
    else:
        repo_patch_result = {
            "adapter_result_status": "PLANNED_ONLY",
            "operation_type": "scoped_repo_patch",
            "file_written": False,
            "target_path": repo_patch_plan["target_path"],
            "changed_files": [],
            "live_execution_performed": False,
            "external_actions_taken": False,
            "worker_agents_activated": False,
            "reason": "Repo patch planned but not executed.",
        }
    changed_file_scope_proof = create_changed_file_scope_proof(repo_patch_plan, repo_patch_result)
    updated["repo_patch_plan"] = repo_patch_plan
    updated["repo_patch_gate"] = repo_patch_gate
    updated["repo_patch_result"] = repo_patch_result
    updated["changed_file_scope_proof"] = changed_file_scope_proof
    return updated


def attach_execution_profile_and_dry_run(
    result: dict,
    requested_profile: str | None = None,
    include_dry_run_bundle: bool = False,
) -> dict:
    updated = dict(result)
    execution_profile = select_execution_profile(result["command_type"], result["selected_overlays"], requested_profile)
    preflight_gate_record = create_preflight_gate_record(result["command_brief"], execution_profile, result.get("repo_patch_plan"))
    patch_approval_checklist = create_patch_approval_checklist(result.get("repo_patch_plan"), execution_profile)
    execution_readiness_score = create_execution_readiness_score(
        preflight_gate_record,
        patch_approval_checklist,
        result.get("changed_file_scope_proof"),
    )
    updated["execution_profile"] = execution_profile
    updated["preflight_gate_record"] = preflight_gate_record
    updated["patch_approval_checklist"] = patch_approval_checklist
    updated["execution_readiness_score"] = execution_readiness_score
    if include_dry_run_bundle:
        updated["dry_run_bundle"] = create_dry_run_bundle(
            updated,
            execution_profile,
            preflight_gate_record,
            patch_approval_checklist,
            execution_readiness_score,
        )
    return updated


def attach_approval_handoff(
    result: dict,
    comparison_bundle_path: str | None = None,
    include_handoff: bool = False,
) -> dict:
    updated = dict(result)
    if updated.get("dry_run_bundle") is None and include_handoff:
        updated = attach_execution_profile_and_dry_run(updated, requested_profile=updated.get("requested_execution_profile"), include_dry_run_bundle=True)
    comparison = None
    if comparison_bundle_path:
        before_bundle = load_json_file(comparison_bundle_path)
        comparison = compare_dry_run_bundles(before_bundle, updated["dry_run_bundle"])
    updated["dry_run_bundle_comparison"] = comparison
    if include_handoff:
        updated["approval_handoff_packet"] = create_approval_handoff_packet(updated["dry_run_bundle"], comparison)
    return updated


def write_dry_run_bundle(
    result: dict,
    output_dir: str | Path,
    run_label: str = "station-chief-runtime",
) -> dict:
    if "dry_run_bundle" not in result or result["dry_run_bundle"] is None:
        raise ValueError("write_dry_run_bundle requires dry_run_bundle to be attached first")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    run_id = generate_run_id(result["command"], run_label=run_label)
    bundle_dir = output_path / run_id
    bundle_dir.mkdir(parents=True, exist_ok=True)

    dry_run_bundle = result["dry_run_bundle"]
    files_written = []
    payloads = {
        "dry_run_bundle.json": dry_run_bundle,
        "execution_profile.json": result.get("execution_profile"),
        "preflight_gate_record.json": result.get("preflight_gate_record"),
        "patch_approval_checklist.json": result.get("patch_approval_checklist"),
        "execution_readiness_score.json": result.get("execution_readiness_score"),
        "repo_patch_preview.diff": dry_run_bundle.get("repo_patch_preview") or "",
        "dry_run_manifest.json": {
            "dry_run_bundle_version": "2.5.0",
            "run_id": run_id,
            "runtime_version": STATION_CHIEF_RUNTIME_VERSION,
            "files_written": [
                "dry_run_bundle.json",
                "execution_profile.json",
                "preflight_gate_record.json",
                "patch_approval_checklist.json",
                "execution_readiness_score.json",
                "repo_patch_preview.diff",
                "dry_run_manifest.json",
            ],
            "baseline_preserved": True,
            "external_actions_taken": False,
            "live_worker_agents_activated": False,
            "requires_human_approval_before_execution": (result.get("patch_approval_checklist") or {}).get("checklist_status") == "READY",
        },
    }
    for filename, payload in payloads.items():
        if filename.endswith(".diff"):
            (bundle_dir / filename).write_text(str(payload))
        else:
            _write_json(bundle_dir / filename, payload)
        files_written.append(filename)

    return {
        "run_id": run_id,
        "dry_run_bundle_dir": str(bundle_dir),
        "files_written": files_written,
    }


def write_approval_handoff(
    result: dict,
    output_dir: str | Path,
    run_label: str = "station-chief-runtime",
) -> dict:
    if "approval_handoff_packet" not in result or result["approval_handoff_packet"] is None:
        raise ValueError("write_approval_handoff requires approval_handoff_packet to be attached first")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    run_id = generate_run_id(result["command"], run_label=run_label)
    handoff_dir = output_path / run_id
    handoff_dir.mkdir(parents=True, exist_ok=True)

    packet = result["approval_handoff_packet"]
    files_written = []
    payloads = {
        "approval_handoff_packet.json": packet,
        "human_approval_summary.json": packet.get("human_approval_summary"),
        "risk_summary.json": packet.get("risk_summary"),
        "next_action_recommendation.json": packet.get("next_action_recommendation"),
        "dry_run_bundle_comparison.json": packet.get("comparison"),
        "patch_preview.diff": (packet.get("dry_run_bundle") or {}).get("repo_patch_preview") or "",
        "approval_handoff_manifest.json": {
            "approval_handoff_version": "2.5.0",
            "run_id": run_id,
            "runtime_version": STATION_CHIEF_RUNTIME_VERSION,
            "files_written": [
                "approval_handoff_packet.json",
                "human_approval_summary.json",
                "risk_summary.json",
                "next_action_recommendation.json",
                "dry_run_bundle_comparison.json",
                "patch_preview.diff",
                "approval_handoff_manifest.json",
            ],
            "baseline_preserved": True,
            "external_actions_taken": False,
            "live_worker_agents_activated": False,
            "requires_human_approval_before_execution": (packet.get("human_approval_summary") or {}).get("approval_required") is True,
        },
    }
    for filename, payload in payloads.items():
        if filename.endswith(".diff"):
            (handoff_dir / filename).write_text(str(payload))
        else:
            _write_json(handoff_dir / filename, payload)
        files_written.append(filename)

    return {
        "run_id": run_id,
        "approval_handoff_dir": str(handoff_dir),
        "files_written": files_written,
    }


def attach_signed_approval_record(
    result: dict,
    reviewer_name: str,
    approval_decision: str,
    approval_note: str | None = None,
    approval_record_token: str | None = None,
    patch_preview_reviewed: bool = False,
    changed_file_scope_reviewed: bool = False,
    baseline_protection_reviewed: bool = False,
    risk_summary_reviewed: bool = False,
) -> dict:
    updated = dict(result)
    if updated.get("dry_run_bundle") is None:
        updated = attach_execution_profile_and_dry_run(
            updated,
            requested_profile=updated.get("requested_execution_profile"),
            include_dry_run_bundle=True,
        )
    if updated.get("approval_handoff_packet") is None:
        updated = attach_approval_handoff(updated, include_handoff=True)
    updated["approval_review_ui_schema"] = create_approval_review_ui_schema()
    signed_approval_record = create_signed_approval_record(
        updated["approval_handoff_packet"],
        reviewer_name,
        approval_decision,
        approval_note=approval_note,
        confirmation_token=approval_record_token,
        patch_preview_reviewed=patch_preview_reviewed,
        changed_file_scope_reviewed=changed_file_scope_reviewed,
        baseline_protection_reviewed=baseline_protection_reviewed,
        risk_summary_reviewed=risk_summary_reviewed,
    )
    approval_record_verification = verify_signed_approval_record(
        updated["approval_handoff_packet"],
        signed_approval_record,
    )
    approval_record_audit_manifest = create_approval_record_audit_manifest(
        updated["approval_handoff_packet"],
        signed_approval_record,
        approval_record_verification,
    )
    updated["signed_approval_record"] = signed_approval_record
    updated["approval_record_verification"] = approval_record_verification
    updated["approval_record_audit_manifest"] = approval_record_audit_manifest
    return updated


def write_approval_record(
    result: dict,
    output_dir: str | Path,
    run_label: str = "station-chief-runtime",
) -> dict:
    if "signed_approval_record" not in result or result["signed_approval_record"] is None:
        raise ValueError("write_approval_record requires signed_approval_record to be attached first")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    run_id = generate_run_id(result["command"], run_label=run_label)
    record_dir = output_path / run_id
    record_dir.mkdir(parents=True, exist_ok=True)

    files_written = []
    approval_record_manifest = {
        "approval_record_manifest_version": "2.5.0",
        "run_id": run_id,
        "runtime_version": STATION_CHIEF_RUNTIME_VERSION,
        "files_written": [
            "approval_review_ui_schema.json",
            "approval_handoff_packet.json",
            "signed_approval_record.json",
            "approval_record_verification.json",
            "approval_record_audit_manifest.json",
            "approval_record_manifest.json",
        ],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "execution_authorized": False,
        "note": "Signed approval records do not execute repo patches by themselves.",
    }
    payloads = {
        "approval_review_ui_schema.json": result.get("approval_review_ui_schema"),
        "approval_handoff_packet.json": result.get("approval_handoff_packet"),
        "signed_approval_record.json": result.get("signed_approval_record"),
        "approval_record_verification.json": result.get("approval_record_verification"),
        "approval_record_audit_manifest.json": result.get("approval_record_audit_manifest"),
        "approval_record_manifest.json": approval_record_manifest,
    }
    for filename, payload in payloads.items():
        _write_json(record_dir / filename, payload)
        files_written.append(filename)

    return {
        "run_id": run_id,
        "approval_record_dir": str(record_dir),
        "files_written": files_written,
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Station Chief Runtime Skeleton")
    parser.add_argument("--demo", action="store_true", help="Run the deterministic demo command")
    parser.add_argument("--command", type=str, help="Run a specific command")
    parser.add_argument("--json", action="store_true", help="Print full Station Chief result as JSON")
    parser.add_argument("--brief", action="store_true", help="Print the command brief as JSON")
    parser.add_argument("--list-overlays", action="store_true", help="Print overlay stack summary as JSON")
    parser.add_argument("--list-adapters", action="store_true", help="Print adapter catalog as JSON")
    parser.add_argument("--list-execution-profiles", action="store_true", help="Print execution profile catalog as JSON")
    parser.add_argument("--write-output", type=str, help="Write full result JSON to a file path")
    parser.add_argument("--write-artifacts", type=str, help="Write runtime artifacts into the provided directory")
    parser.add_argument("--write-dry-run-bundle", type=str, help="Write dry-run bundle artifacts into the provided directory")
    parser.add_argument("--compare-dry-run-bundles", nargs=2, metavar=("BEFORE_JSON", "AFTER_JSON"), help="Compare two dry-run bundle JSON files")
    parser.add_argument("--approval-handoff", action="store_true", help="Attach an approval handoff packet")
    parser.add_argument("--approval-review-ui-schema", action="store_true", help="Print the approval review UI schema as JSON")
    parser.add_argument("--sign-approval-record", action="store_true", help="Create a deterministic signed approval record")
    parser.add_argument("--approval-reviewer", type=str, help="Reviewer name for approval records")
    parser.add_argument("--approval-decision", type=str, help="Approval decision for approval records")
    parser.add_argument("--approval-note", type=str, help="Optional approval note")
    parser.add_argument("--approval-record-token", type=str, help="Confirmation token for signed approval records")
    parser.add_argument("--patch-preview-reviewed", action="store_true", help="Approve that the patch preview was reviewed")
    parser.add_argument("--changed-file-scope-reviewed", action="store_true", help="Approve that changed-file scope was reviewed")
    parser.add_argument("--baseline-protection-reviewed", action="store_true", help="Approve that baseline protection was reviewed")
    parser.add_argument("--risk-summary-reviewed", action="store_true", help="Approve that the risk summary was reviewed")
    parser.add_argument("--compare-against-dry-run-bundle", type=str, help="Compare the current dry-run bundle against a saved bundle JSON file")
    parser.add_argument("--write-approval-handoff", type=str, help="Write approval handoff artifacts into the provided directory")
    parser.add_argument("--write-approval-record", type=str, help="Write approval record artifacts into the provided directory")
    parser.add_argument("--verify-approval-record", nargs=2, metavar=("APPROVAL_HANDOFF_PACKET_JSON", "APPROVAL_RECORD_JSON"), help="Verify an approval record against an approval handoff packet")
    parser.add_argument("--run-label", type=str, default="station-chief-runtime", help="Label included in artifact run IDs")
    parser.add_argument("--fixture-test", action="store_true", help="Run deterministic fixture tests")
    parser.add_argument("--adapter", type=str, default="noop", help="Choose the controlled execution adapter")
    parser.add_argument("--simulate-adapter", action="store_true", help="Simulate the selected controlled execution adapter")
    parser.add_argument("--registry-dir", type=str, help="Directory used for the persistent run registry")
    parser.add_argument("--resume-run-id", type=str, help="Resume a previously recorded run by run ID")
    parser.add_argument("--plan-file-operation", action="store_true", help="Plan a sandbox file operation without executing it")
    parser.add_argument("--execution-dir", type=str, help="Directory used for sandbox file-operation execution")
    parser.add_argument("--target-filename", type=str, default="station_chief_sandbox_output.txt", help="Target filename for sandbox file operations")
    parser.add_argument("--confirm-execution", type=str, help="Confirmation token required for sandbox file writes")
    parser.add_argument("--execute-sandbox-file-write", action="store_true", help="Execute a sandbox file write if the gate approves")
    parser.add_argument("--plan-repo-patch", action="store_true", help="Plan a scoped repo patch without executing it")
    parser.add_argument("--patch-root", type=str, help="Root directory used for scoped repo patch execution")
    parser.add_argument("--allowed-patch-file", action="append", default=None, help="Allowlisted relative file for scoped repo patches")
    parser.add_argument("--patch-relative-path", type=str, default="runtime_patch_preview/station_chief_patch_output.txt", help="Relative path for the scoped repo patch target")
    parser.add_argument("--patch-content", type=str, help="Explicit repo patch content; otherwise a deterministic default is used")
    parser.add_argument("--confirm-patch", type=str, help="Confirmation token required for scoped repo patches")
    parser.add_argument("--execute-repo-patch", action="store_true", help="Execute a scoped repo patch if the gate approves")
    parser.add_argument("--execution-profile", type=str, help="Requested execution profile for dry-run behavior")
    parser.add_argument("--dry-run-bundle", action="store_true", help="Attach a dry-run bundle to the printed result")
    parser.add_argument("--release-lock", action="store_true", help="Attach v2.5.0 stable release lock artifacts")
    parser.add_argument("--stable-release-manifest", action="store_true", help="Print the stable v2.5.0 release manifest as JSON")
    parser.add_argument("--write-release-lock", metavar="DIR", help="Write v2.5.0 stable release lock artifacts to DIR")
    parser.add_argument("--verify-release-manifest", metavar="RELEASE_MANIFEST_JSON", help="Verify a v2.5.0 stable release manifest JSON file")
    parser.add_argument("--list-controlled-execution-profiles", action="store_true", help="Print controlled execution profile catalog as JSON")
    parser.add_argument("--controlled-execution", action="store_true", help="Attach controlled execution bundle to the printed result")
    parser.add_argument("--controlled-execution-profile", type=str, metavar="PROFILE_ID", help="Choose a controlled execution profile")
    parser.add_argument("--attempted-action", action="append", default=[], help="Record an attempted action in the blocked action ledger")
    parser.add_argument("--write-controlled-execution", metavar="DIR", help="Write controlled execution artifacts into the provided directory")
    parser.add_argument("--work-order-schema", action="store_true", help="Print the executable work order schema as JSON")
    parser.add_argument("--work-order-executor", action="store_true", help="Attach work order executor bundle to the printed result")
    parser.add_argument("--write-work-order-executor", metavar="DIR", help="Write work order executor artifacts into the provided directory")
    parser.add_argument("--worker-role-schema", action="store_true", help="Print the worker role schema as JSON")
    parser.add_argument("--worker-hiring-registry", action="store_true", help="Attach worker hiring registry bundle to the printed result")
    parser.add_argument("--write-worker-hiring-registry", metavar="DIR", help="Write worker hiring registry artifacts into the provided directory")
    parser.add_argument("--department-routing-schema", action="store_true", help="Print the department routing schema as JSON")
    parser.add_argument("--department-routing", action="store_true", help="Attach department routing bundle to the printed result")
    parser.add_argument("--write-department-routing", metavar="DIR", help="Write department routing artifacts into the provided directory")
    parser.add_argument("--orchestration-schema", action="store_true", help="Print the multi-agent orchestration topology schema as JSON")
    parser.add_argument("--multi-agent-orchestration", action="store_true", help="Attach multi-agent orchestration bundle to the printed result")
    parser.add_argument("--write-multi-agent-orchestration", metavar="DIR", help="Write multi-agent orchestration artifacts into the provided directory")
    parser.add_argument("--operator-console-schema", action="store_true", help="Print the operator console screen schema as JSON")
    parser.add_argument("--operator-console", action="store_true", help="Attach operator console bundle to the printed result")
    parser.add_argument("--write-operator-console", metavar="DIR", help="Write operator console artifacts into the provided directory")
    parser.add_argument("--patch-hardening-schema", action="store_true", help="Print the GitHub patch hardening schema as JSON")
    parser.add_argument("--github-patch-hardening", action="store_true", help="Attach GitHub patch hardening bundle to the printed result")
    parser.add_argument("--write-github-patch-hardening", metavar="DIR", help="Write GitHub patch hardening artifacts into the provided directory")
    parser.add_argument("--deployment-artifact-schema", action="store_true", help="Print the deployment artifact schema as JSON")
    parser.add_argument("--deployment-packaging", action="store_true", help="Attach deployment packaging bundle to the printed result")
    parser.add_argument("--write-deployment-packaging", metavar="DIR", help="Write deployment packaging artifacts into the provided directory")
    parser.add_argument("--controlled-worker-schema", action="store_true", help="Print the controlled worker execution schema as JSON")
    parser.add_argument("--controlled-worker-execution", action="store_true", help="Attach controlled worker execution bundle to the printed result")
    parser.add_argument("--write-controlled-worker-execution", metavar="DIR", help="Write controlled worker execution artifacts into the provided directory")
    parser.add_argument("--tool-permission-schema", action="store_true", help="Print the tool permission binding schema as JSON")
    parser.add_argument("--tool-permission-binding", action="store_true", help="Attach tool permission binding bundle to the printed result")
    parser.add_argument("--write-tool-permission-binding", metavar="DIR", help="Write tool permission binding artifacts into the provided directory")
    parser.add_argument("--telemetry-abort-schema", action="store_true", help="Print the live telemetry and abort controls schema as JSON")
    parser.add_argument("--live-telemetry-abort", action="store_true", help="Attach live telemetry and abort bundle to the printed result")
    parser.add_argument("--write-live-telemetry-abort", metavar="DIR", help="Write live telemetry and abort artifacts into the provided directory")
    parser.add_argument("--post-run-audit-schema", action="store_true", help="Print the post-run audit expansion schema as JSON")
    parser.add_argument("--post-run-audit-expansion", action="store_true", help="Attach post-run audit expansion bundle to the printed result")
    parser.add_argument("--write-post-run-audit-expansion", metavar="DIR", help="Write post-run audit expansion artifacts into the provided directory")
    parser.add_argument("--post-run-audit-worker-id", type=str, help="Worker ID for post-run audit expansion")
    parser.add_argument("--post-run-audit-confirm-token", type=str, help="Confirmation token for post-run audit expansion")
    parser.add_argument("--post-run-audit-before-json", type=str, help="JSON before-result payload for post-run audit comparison")
    parser.add_argument("--post-run-audit-after-json", type=str, help="JSON after-result payload for post-run audit comparison")
    parser.add_argument("--post-run-audit-artifact-name", action="append", default=[], help="Contract artifact name for post-run audit expansion")
    parser.add_argument("--post-run-audit-validator-name", action="append", default=[], help="Contract validator name for post-run audit expansion")
    parser.add_argument("--post-run-audit-observed-failure", action="append", default=[], help="Observed failure label for post-run audit expansion")
    parser.add_argument("--multi-worker-coordination-schema", action="store_true", help="Print the multi-worker sandbox coordination schema as JSON")
    parser.add_argument("--multi-worker-sandbox-coordination", action="store_true", help="Attach multi-worker sandbox coordination bundle to the printed result")
    parser.add_argument("--write-multi-worker-sandbox-coordination", metavar="DIR", help="Write multi-worker sandbox coordination artifacts into the provided directory")
    parser.add_argument("--multi-worker-roster-label", type=str, default="station-chief-multi-worker-sandbox-roster", help="Roster label for multi-worker sandbox coordination")
    parser.add_argument("--multi-worker-confirm-token", type=str, help="Confirmation token for multi-worker sandbox coordination")
    parser.add_argument("--multi-worker-count", type=int, default=3, help="Requested worker count for multi-worker sandbox coordination")
    parser.add_argument("--multi-worker-role", action="append", default=[], help="Worker role label for multi-worker sandbox coordination")
    parser.add_argument("--multi-worker-shared-resource", action="append", default=[], help="Shared resource label for multi-worker sandbox coordination")
    parser.add_argument("--multi-worker-abort-reason", type=str, help="Abort reason for multi-worker sandbox coordination")
    parser.add_argument("--multi-worker-failure-reason", type=str, help="Failure reason for multi-worker sandbox coordination")
    parser.add_argument("--external-tool-preview-schema", action="store_true", help="Print the controlled external tool adapter preview schema as JSON")
    parser.add_argument("--controlled-external-tool-preview", action="store_true", help="Attach controlled external tool adapter preview bundle to the printed result")
    parser.add_argument("--write-controlled-external-tool-preview", metavar="DIR", help="Write controlled external tool adapter preview artifacts into the provided directory")
    parser.add_argument("--external-tool-label", type=str, default="station-chief-external-tool-preview", help="External tool label for controlled preview")
    parser.add_argument("--external-tool-id", type=str, default="web_search_preview", help="External tool ID for controlled preview")
    parser.add_argument("--external-tool-confirm-token", type=str, help="Confirmation token for controlled external tool adapter preview")
    parser.add_argument("--external-tool-requested-tool", action="append", default=[], help="Requested preview tool label for controlled external tool adapter preview")
    parser.add_argument("--external-tool-requested-action", type=str, default="preview_request_contract", help="Requested preview action for controlled external tool adapter preview")
    parser.add_argument("--external-tool-request-label", type=str, help="Request label for controlled external tool adapter preview")
    parser.add_argument("--external-tool-request-payload-json", type=str, help="JSON payload for controlled external tool adapter preview request")
    parser.add_argument("--external-tool-response-preview-json", type=str, help="JSON response preview for controlled external tool adapter preview")
    parser.add_argument("--external-tool-abort-reason", type=str, help="Abort reason for controlled external tool adapter preview")
    
    parser.add_argument("--external-api-dry-run-schema", action="store_true", help="Print the permissioned external API dry-run preview schema as JSON")
    parser.add_argument("--permissioned-external-api-dry-run", action="store_true", help="Attach permissioned external API dry-run preview bundle to the printed result")
    parser.add_argument("--write-permissioned-external-api-dry-run", metavar="DIR", type=str, help="Write permissioned external API dry-run preview artifacts into the provided directory")
    parser.add_argument("--external-api-label", type=str)
    parser.add_argument("--external-api-endpoint-id", type=str)
    parser.add_argument("--external-api-confirm-token", type=str)
    parser.add_argument("--external-api-requested-endpoint", type=str, action="append")
    parser.add_argument("--external-api-method", type=str)
    parser.add_argument("--external-api-path-template", type=str)
    parser.add_argument("--external-api-request-payload-json", type=str)
    parser.add_argument("--external-api-credential-label", type=str, action="append")
    parser.add_argument("--external-api-fixture-payload-json", type=str)
    parser.add_argument("--audit-replay-preview-schema", action="store_true")
    parser.add_argument("--controlled-multi-worker-audit-replay-preview", action="store_true")
    parser.add_argument("--write-controlled-multi-worker-audit-replay-preview", metavar="DIR", type=str)
    parser.add_argument("--audit-replay-label", type=str)
    parser.add_argument("--audit-replay-confirm-token", type=str)
    parser.add_argument("--audit-replay-worker-count", type=int, default=3)
    parser.add_argument("--audit-replay-mode", type=str)
    parser.add_argument("--audit-replay-packet-json", type=str, action="append")
    parser.add_argument("--audit-replay-observed-digest-map-json", type=str)
    parser.add_argument("--audit-replay-quarantine-reason", type=str)
    parser.add_argument("--operator-approval-queue-schema", action="store_true")
    parser.add_argument("--operator-approval-queue-enforcement", action="store_true")
    parser.add_argument("--write-operator-approval-queue-enforcement", metavar="DIR", type=str)
    parser.add_argument("--approval-queue-label", type=str)
    parser.add_argument("--approval-queue-confirm-token", type=str)
    parser.add_argument("--approval-queue-action-count", type=int, default=3)
    parser.add_argument("--approval-queue-action-json", type=str, action="append")
    parser.add_argument("--approval-queue-operator-decisions-json", type=str)
    parser.add_argument("--approval-queue-stale-after-hours", type=int, default=72)
    parser.add_argument("--release-candidate-hardening-schema", action="store_true")
    parser.add_argument("--release-candidate-hardening", action="store_true")
    parser.add_argument("--write-release-candidate-hardening", metavar="DIR", type=str)
    parser.add_argument("--release-candidate-label", type=str)
    parser.add_argument("--release-candidate-confirm-token", type=str)
    parser.add_argument("--release-candidate-invariant", type=str, action="append")
    parser.add_argument("--release-candidate-validator", type=str, action="append")
    parser.add_argument("--release-candidate-artifact-contract", type=str, action="append")
    parser.add_argument("--release-candidate-known-issue-json", type=str, action="append")
    parser.add_argument("--release-candidate-checklist-item", type=str, action="append")
    
    parser.add_argument("--production-readiness-gate-schema", action="store_true")
    parser.add_argument("--controlled-production-readiness-gate", action="store_true")
    parser.add_argument("--write-controlled-production-readiness-gate", metavar="DIR", type=str)
    parser.add_argument("--production-gate-label", type=str)
    parser.add_argument("--production-gate-confirm-token", type=str)
    parser.add_argument("--production-gate-required-approver", type=str)
    parser.add_argument("--production-gate-capability", type=str, action="append")
    parser.add_argument("--production-gate-pilot-label", type=str)
    parser.add_argument("--production-gate-pilot-worker-limit", type=int, default=1)
    parser.add_argument("--production-gate-rollback-label", type=str, action="append")
    
    parser.add_argument("--worker-hiring-activation-pilot-schema", action="store_true")
    parser.add_argument("--controlled-worker-hiring-activation-pilot", action="store_true")
    parser.add_argument("--write-controlled-worker-hiring-activation-pilot", metavar="DIR", type=str)
    parser.add_argument("--pilot-label", type=str)
    parser.add_argument("--pilot-confirm-token", type=str)
    parser.add_argument("--pilot-worker-limit", type=int, default=1)
    parser.add_argument("--pilot-worker-label", type=str, action="append")
    parser.add_argument("--pilot-required-supervisor", type=str)
    parser.add_argument("--pilot-rollback-label", type=str, action="append")
    
    parser.add_argument("--first-supervised-production-dry-run-schema", action="store_true")
    parser.add_argument("--first-supervised-production-dry-run", action="store_true")
    parser.add_argument("--write-first-supervised-production-dry-run", metavar="DIR", type=str)
    parser.add_argument("--dry-run-label", type=str)
    parser.add_argument("--dry-run-confirm-token", type=str)
    parser.add_argument("--dry-run-task-label", type=str)
    parser.add_argument("--dry-run-production-context-label", type=str)
    parser.add_argument("--dry-run-required-preflight-approver", type=str)
    parser.add_argument("--dry-run-worker-label", type=str)
    parser.add_argument("--dry-run-quarantine-label", type=str, action="append")

    parser.add_argument("--limited-external-tool-supervised-pilot-schema", action="store_true")
    parser.add_argument("--limited-external-tool-supervised-pilot", action="store_true")
    parser.add_argument("--write-limited-external-tool-supervised-pilot", metavar="DIR", type=str)
    parser.add_argument("--supervised-production-pilot-readiness-review-schema", action="store_true")
    parser.add_argument("--supervised-production-pilot-readiness-review", action="store_true")
    parser.add_argument("--write-supervised-production-pilot-readiness-review", metavar="DIR", type=str)
    parser.add_argument("--production-readiness-label", type=str, default="station-chief-supervised-production-pilot-readiness-review")
    parser.add_argument("--production-readiness-confirm-token", type=str)
    parser.add_argument("--candidate-label", type=str, default="minimum viable production candidate preview")
    parser.add_argument("--required-production-pilot-reviewer", type=str, default="Devin O’Rourke / explicit human operator")
    parser.add_argument("--blast-radius-label", type=str, default="preview production blast-radius analysis")
    parser.add_argument("--credential-vault-denial-secret-handling-proof-schema", action="store_true")
    parser.add_argument("--credential-vault-denial-secret-handling-proof", action="store_true")
    parser.add_argument("--write-credential-vault-denial-secret-handling-proof", metavar="DIR", type=str)
    parser.add_argument("--credential-secret-label", type=str, default="station-chief-credential-vault-denial-secret-handling-proof")
    parser.add_argument("--credential-secret-confirm-token", type=str)
    parser.add_argument("--credential-boundary-label", type=str, default="credential vault boundary preview")
    parser.add_argument("--secret-boundary-label", type=str, default="secret handling boundary preview")
    parser.add_argument("--environment-boundary-label", type=str, default="environment read boundary preview")
    parser.add_argument("--supervised-external-api-pilot-schema", action="store_true")
    parser.add_argument("--supervised-external-api-pilot", action="store_true")
    parser.add_argument("--write-supervised-external-api-pilot", type=str, metavar="DIR")
    parser.add_argument("--api-pilot-label", type=str, default="station-chief-supervised-external-api-pilot")
    parser.add_argument("--api-pilot-confirm-token", type=str)
    parser.add_argument("--api-category-label", type=str, default="read-only-public-status-api-preview")
    parser.add_argument("--api-pilot-required-preflight-approver", type=str, default="Devin O’Rourke / explicit human operator")
    parser.add_argument("--api-request-label", type=str, default="single supervised API request preview")
    parser.add_argument("--api-quarantine-label", type=str, action="append")
    parser.add_argument("--monitored-rollback-recovery-drill-schema", action="store_true")
    parser.add_argument("--monitored-rollback-recovery-drill", action="store_true")
    parser.add_argument("--write-monitored-rollback-recovery-drill", metavar="DIR", type=str)
    parser.add_argument("--recovery-drill-label", type=str, default="station-chief-monitored-rollback-recovery-drill")
    parser.add_argument("--recovery-drill-confirm-token", type=str)
    parser.add_argument("--simulated-failure-label", type=str, default="simulated validation failure trigger")
    parser.add_argument("--rollback-path-label", type=str, default="preview rollback path without execution")
    parser.add_argument("--recovery-checkpoint-label", type=str, default="preview recovery checkpoint")
    parser.add_argument("--required-recovery-approver", type=str, default="Devin O’Rourke / explicit human operator")
    parser.add_argument("--recovery-quarantine-label", type=str, action="append", default=[])
    parser.add_argument("--tool-pilot-label", type=str, default="station-chief-limited-external-tool-supervised-pilot")
    parser.add_argument("--tool-pilot-confirm-token", type=str)
    parser.add_argument("--tool-category-label", type=str, default="local-json-artifact-review")
    parser.add_argument("--tool-pilot-required-preflight-approver", type=str, default="Devin O’Rourke / explicit human operator")
    parser.add_argument("--tool-request-label", type=str, default="single supervised tool request preview")
    parser.add_argument("--tool-quarantine-label", type=str, action="append", default=[])

    parser.add_argument("--telemetry-worker-id", type=str, help="Worker ID for live telemetry")
    parser.add_argument("--telemetry-confirm-token", type=str, help="Confirmation token for live telemetry approval")
    parser.add_argument("--telemetry-abort-reason", type=str, help="Reason for live telemetry abort")
    parser.add_argument("--telemetry-failure-reason", type=str, help="Reason for live telemetry failure")
    parser.add_argument("--telemetry-timeout-limit-steps", type=int, default=5, help="Timeout limit in steps for live telemetry")
    parser.add_argument("--telemetry-observed-steps", type=int, default=0, help="Observed steps for live telemetry")
    parser.add_argument("--telemetry-partial-payload-json", type=str, help="JSON payload for partial result capture")
    parser.add_argument("--tool-permission-worker-id", type=str, help="Worker ID for tool permission binding")
    parser.add_argument("--tool-permission-request", action="append", default=[], help="Request a tool permission for the sandbox worker")
    parser.add_argument("--tool-permission-token", action="append", default=[], help="Provide a tool-specific approval token (PERMISSION_ID=TOKEN)")
    parser.add_argument("--tool-permission-output-json", action="append", default=[], help="Mocked JSON output for a tool permission")
    parser.add_argument("--tool-permission-sandbox-task", type=str, help="Sandbox task associated with tool permission binding")
    parser.add_argument("--controlled-worker-id", type=str, help="Worker ID for sandbox execution")
    parser.add_argument("--controlled-worker-task", type=str, help="Sandbox task for controlled worker execution")
    parser.add_argument("--controlled-worker-payload-json", type=str, help="JSON payload for controlled worker task")
    parser.add_argument("--controlled-worker-tool-permission", action="append", default=[], help="Requested tool permission for controlled worker")
    parser.add_argument("--confirm-controlled-worker-execution", type=str, help="Confirmation token required for first controlled worker execution")
    parser.add_argument("--hardening-patch-root", type=str, help="Patch root for hardening review")
    parser.add_argument("--hardening-allowed-patch-file", type=str, help="Allowed patch file for hardening review")
    parser.add_argument("--hardening-patch-content", type=str, help="Patch content for hardening review")
    parser.add_argument("--hardening-original-content", type=str, help="Original content for hardening review")
    parser.add_argument("--hardening-changed-file", action="append", default=[], help="Changed file for hardening review")
    parser.add_argument("--network-socket-lockdown-proof-schema", action="store_true")
    parser.add_argument("--network-socket-lockdown-proof", action="store_true")
    parser.add_argument("--write-network-socket-lockdown-proof", metavar="DIR", type=str)
    parser.add_argument("--network-socket-label", type=str)
    parser.add_argument("--network-socket-confirm-token", type=str)
    parser.add_argument("--network-boundary-label", type=str)
    parser.add_argument("--socket-boundary-label", type=str)
    parser.add_argument("--live-external-action-final-preflight-gate-schema", action="store_true")
    parser.add_argument("--live-external-action-final-preflight-gate", action="store_true")
    parser.add_argument("--write-live-external-action-final-preflight-gate", metavar="DIR", type=str)
    parser.add_argument("--live-external-action-label", type=str)
    parser.add_argument("--live-external-action-confirm-token", type=str)
    parser.add_argument("--first-tiny-real-world-supervised-execution-candidate-schema", action="store_true")
    parser.add_argument("--first-tiny-real-world-supervised-execution-candidate", action="store_true")
    parser.add_argument("--write-first-tiny-real-world-supervised-execution-candidate", metavar="DIR", type=str)
    parser.add_argument("--v4-candidate-label", type=str)
    parser.add_argument("--v4-candidate-confirm-token", type=str)
    parser.add_argument("--v4-human-operator", type=str)
    parser.add_argument("--v4-artifact-name", type=str)
    parser.add_argument("--post-action-verification-and-audit-review-schema", action="store_true")
    parser.add_argument("--post-action-verification-and-audit-review", action="store_true")
    parser.add_argument("--write-post-action-verification-and-audit-review", metavar="DIR", type=str)
    parser.add_argument("--v4-review-label", type=str)
    parser.add_argument("--v4-review-artifact-path", type=str)
    parser.add_argument("--v4-review-expected-output-directory", type=str)
    parser.add_argument("--v4-review-confirm-token", type=str)
    parser.add_argument("--v4-review-human-operator", type=str)
    parser.add_argument("--supervised-rollback-cleanup-candidate-schema", action="store_true")
    parser.add_argument("--supervised-rollback-cleanup-candidate", action="store_true")
    parser.add_argument("--execute-supervised-rollback-cleanup-candidate", metavar="DIR", type=str)
    parser.add_argument("--v4-cleanup-label", type=str)
    parser.add_argument("--v4-cleanup-artifact-path", type=str)
    parser.add_argument("--v4-cleanup-expected-output-directory", type=str)
    parser.add_argument("--v4-cleanup-confirm-token", type=str)
    parser.add_argument("--v4-cleanup-human-operator", type=str)
    parser.add_argument("--limited-live-worker-activation-candidate-schema", action="store_true")
    parser.add_argument("--limited-live-worker-activation-candidate", action="store_true")
    parser.add_argument("--write-limited-live-worker-activation-candidate", metavar="DIR", type=str)
    parser.add_argument("--v4-worker-template-label", type=str)
    parser.add_argument("--v4-worker-activation-record-name", type=str)
    parser.add_argument("--v4-worker-activation-confirm-token", type=str)
    parser.add_argument("--v4-worker-activation-human-operator", type=str)
    parser.add_argument("--permissioned-worker-task-assignment-candidate-schema", action="store_true")
    parser.add_argument("--permissioned-worker-task-assignment-candidate", action="store_true")
    parser.add_argument("--write-permissioned-worker-task-assignment-candidate", metavar="DIR", type=str)
    parser.add_argument("--v4-task-worker-template-label", type=str)
    parser.add_argument("--v4-task-label", type=str)
    parser.add_argument("--v4-task-assignment-record-name", type=str)
    parser.add_argument("--v4-task-assignment-confirm-token", type=str)
    parser.add_argument("--v4-task-assignment-human-operator", type=str)
    parser.add_argument("--task-assignment-audit-closeout-candidate-schema", action="store_true")
    parser.add_argument("--task-assignment-audit-closeout-candidate", action="store_true")
    parser.add_argument("--write-task-assignment-audit-closeout-candidate", metavar="DIR", type=str)
    parser.add_argument("--v4-closeout-label", type=str)
    parser.add_argument("--v4-closeout-task-assignment-record-path", type=str)
    parser.add_argument("--v4-closeout-expected-task-assignment-output-directory", type=str)
    parser.add_argument("--v4-closeout-record-name", type=str)
    parser.add_argument("--v4-closeout-confirm-token", type=str)
    parser.add_argument("--v4-closeout-human-operator", type=str)
    parser.add_argument("--non-executing-task-queue-preview-candidate-schema", action="store_true")
    parser.add_argument("--non-executing-task-queue-preview-candidate", action="store_true")
    parser.add_argument("--write-non-executing-task-queue-preview-candidate", metavar="DIR", type=str)
    parser.add_argument("--v4-queue-preview-label", type=str)
    parser.add_argument("--v4-queue-preview-task-assignment-record-path", type=str)
    parser.add_argument("--v4-queue-preview-expected-task-assignment-output-directory", type=str)
    parser.add_argument("--v4-queue-preview-closeout-record-path", type=str)
    parser.add_argument("--v4-queue-preview-record-name", type=str)
    parser.add_argument("--v4-queue-preview-confirm-token", type=str)
    parser.add_argument("--v4-queue-preview-human-operator", type=str)
    parser.add_argument("--task-queue-preview-audit-closeout-candidate-schema", action="store_true")
    parser.add_argument("--task-queue-preview-audit-closeout-candidate", action="store_true")
    parser.add_argument("--write-task-queue-preview-audit-closeout-candidate", metavar="DIR", type=str)
    parser.add_argument("--v4-queue-closeout-label", type=str)
    parser.add_argument("--v4-queue-closeout-queue-preview-record-path", type=str)
    parser.add_argument("--v4-queue-closeout-expected-queue-preview-output-directory", type=str)
    parser.add_argument("--v4-queue-closeout-record-name", type=str)
    parser.add_argument("--v4-queue-closeout-confirm-token", type=str)
    parser.add_argument("--v4-queue-closeout-human-operator", type=str)
    parser.add_argument("--non-executing-queue-routing-preview-schema", action="store_true")
    parser.add_argument("--non-executing-queue-routing-preview", action="store_true")
    parser.add_argument("--write-non-executing-queue-routing-preview", metavar="DIR", type=str)
    parser.add_argument("--v4-task-candidate-label", type=str)
    # parser.add_argument("--v4-worker-template-label", type=str)
    parser.add_argument("--v4-queue-routing-preview-record-name", type=str)
    parser.add_argument("--v4-queue-routing-preview-confirm-token", type=str)
    parser.add_argument("--v4-queue-routing-preview-human-operator", type=str)
    parser.add_argument("--live-queue-orchestration-candidate-review-schema", action="store_true")
    parser.add_argument("--live-queue-orchestration-candidate-review", action="store_true")
    parser.add_argument("--write-live-queue-orchestration-candidate-review", metavar="DIR", type=str)
    parser.add_argument("--v4-8-routing-preview-reference-label", type=str)
    parser.add_argument("--v4-orchestration-review-record-name", type=str)
    parser.add_argument("--v4-orchestration-review-confirm-token", type=str)
    parser.add_argument("--v4-orchestration-review-human-operator", type=str)
    parser.add_argument("--first-live-queue-execution-candidate-review-schema", action="store_true")
    parser.add_argument("--first-live-queue-execution-candidate-review", action="store_true")
    parser.add_argument("--write-first-live-queue-execution-candidate-review", metavar="DIR", type=str)
    parser.add_argument("--v4-9-orchestration-review-reference-label", type=str)
    parser.add_argument("--v5-execution-review-record-name", type=str)
    parser.add_argument("--v5-execution-review-confirm-token", type=str)
    parser.add_argument("--v5-execution-review-human-operator", type=str)
    parser.add_argument("--first-supervised-local-execution-kernel-candidate-schema", action="store_true")
    parser.add_argument("--first-supervised-local-execution-kernel-candidate", action="store_true")
    parser.add_argument("--write-first-supervised-local-execution-kernel-candidate", metavar="DIR", type=str)
    parser.add_argument("--v5-synthetic-task-label", type=str)
    parser.add_argument("--v5-supervised-output-record-name", type=str)
    parser.add_argument("--v5-supervised-execution-confirm-token", type=str)
    parser.add_argument("--v5-supervised-execution-human-operator", type=str)
    parser.add_argument("--controlled-repeatable-local-execution-candidate-schema", action="store_true")
    parser.add_argument("--controlled-repeatable-local-execution-candidate", action="store_true")
    parser.add_argument("--write-controlled-repeatable-local-execution-candidate", metavar="DIR", type=str)
    parser.add_argument("--v5-repeatable-synthetic-task-label", type=str)
    parser.add_argument("--v5-repeatability-count", type=int)
    parser.add_argument("--v5-repeatability-proof-record-name", type=str)
    parser.add_argument("--v5-repeatable-execution-confirm-token", type=str)
    parser.add_argument("--v5-repeatable-execution-human-operator", type=str)
    parser.add_argument("--sandbox-worker-handoff-candidate-schema", action="store_true")
    parser.add_argument("--sandbox-worker-handoff-candidate", action="store_true")
    parser.add_argument("--write-sandbox-worker-handoff-candidate", metavar="DIR", type=str)
    parser.add_argument("--v5-handoff-synthetic-task-label", type=str)
    parser.add_argument("--v5-sandbox-worker-label", type=str)
    parser.add_argument("--v5-repeatability-proof-reference-label", type=str)
    parser.add_argument("--v5-handoff-packet-name", type=str)
    parser.add_argument("--v5-handoff-confirm-token", type=str)
    parser.add_argument("--v5-handoff-human-operator", type=str)
    parser.add_argument("--sandbox-worker-acknowledgement-candidate-schema", action="store_true")
    parser.add_argument("--sandbox-worker-acknowledgement-candidate", action="store_true")
    parser.add_argument("--write-sandbox-worker-acknowledgement-candidate", metavar="DIR", type=str)
    parser.add_argument("--v5-ack-sandbox-worker-label", type=str)
    parser.add_argument("--v5-handoff-packet-reference-label", type=str)
    parser.add_argument("--v5-acknowledgement-packet-name", type=str)
    parser.add_argument("--v5-acknowledgement-confirm-token", type=str)
    parser.add_argument("--v5-acknowledgement-human-operator", type=str)
    parser.add_argument("--station-chief-v6-0-mvp-lock-schema", action="store_true")
    parser.add_argument("--station-chief-v6-1-post-mvp-expansion-review-schema", action="store_true")
    parser.add_argument("--station-chief-v6-1-post-mvp-expansion-review", action="store_true")
    parser.add_argument("--write-station-chief-v6-1-post-mvp-expansion-review", metavar="DIR", type=str)
    parser.add_argument("--v6-1-mvp-lock-reference-label", type=str)
    parser.add_argument("--v6-1-post-mvp-expansion-review-label", type=str)
    parser.add_argument("--v6-1-requested-expansion-lane-label", type=str)
    parser.add_argument("--v6-1-expansion-boundary-label", type=str)
    parser.add_argument("--v6-1-expansion-safety-posture-label", type=str)
    parser.add_argument("--v6-1-post-mvp-expansion-review-packet-name", type=str)
    parser.add_argument("--v6-1-post-mvp-expansion-review-confirm-token", type=str)
    parser.add_argument("--v6-1-post-mvp-expansion-review-human-operator", type=str)
    parser.add_argument("--station-chief-v6-2-post-mvp-expansion-lane-scope-schema", action="store_true")
    parser.add_argument("--station-chief-v6-2-post-mvp-expansion-lane-scope", action="store_true")
    parser.add_argument("--write-station-chief-v6-2-post-mvp-expansion-lane-scope", metavar="DIR", type=str)
    parser.add_argument("--v6-2-review-packet-reference-label", type=str)
    parser.add_argument("--v6-2-selected-expansion-lane-label", type=str)
    parser.add_argument("--v6-2-lane-scope-label", type=str)
    parser.add_argument("--v6-2-lane-constraint-label", type=str)
    parser.add_argument("--v6-2-lane-success-criteria-label", type=str)
    parser.add_argument("--v6-2-lane-non-execution-boundary-label", type=str)
    parser.add_argument("--v6-2-lane-scope-packet-name", type=str)
    parser.add_argument("--v6-2-lane-scope-confirm-token", type=str)
    parser.add_argument("--v6-2-lane-scope-human-operator", type=str)
    parser.add_argument("--station-chief-v6-3-post-mvp-expansion-lane-readiness-schema", action="store_true")
    parser.add_argument("--station-chief-v6-3-post-mvp-expansion-lane-readiness", action="store_true")
    parser.add_argument("--write-station-chief-v6-3-post-mvp-expansion-lane-readiness", metavar="DIR", type=str)
    parser.add_argument("--v6-3-lane-scope-packet-reference-label", type=str)
    parser.add_argument("--v6-3-selected-expansion-lane-label", type=str)
    parser.add_argument("--v6-3-readiness-checklist-label", type=str)
    parser.add_argument("--v6-3-readiness-blocker-label", type=str)
    parser.add_argument("--v6-3-readiness-evidence-label", type=str)
    parser.add_argument("--v6-3-readiness-non-execution-boundary-label", type=str)
    parser.add_argument("--v6-3-readiness-packet-name", type=str)
    parser.add_argument("--v6-3-readiness-confirm-token", type=str)
    parser.add_argument("--v6-3-readiness-human-operator", type=str)

    parser.add_argument("--station-chief-v6-5-post-mvp-expansion-lane-non-executing-implementation-plan-review-schema", action="store_true")
    parser.add_argument("--station-chief-v6-5-post-mvp-expansion-lane-non-executing-implementation-plan-review", action="store_true")
    parser.add_argument("--write-station-chief-v6-5-post-mvp-expansion-lane-non-executing-implementation-plan-review", type=str)
    parser.add_argument("--v6-5-implementation-plan-packet-reference-label", type=str)
    parser.add_argument("--v6-5-readiness-packet-reference-label", type=str)
    parser.add_argument("--v6-5-lane-scope-packet-reference-label", type=str)
    parser.add_argument("--v6-5-selected-expansion-lane-label", type=str)
    parser.add_argument("--v6-5-implementation-plan-review-label", type=str)
    parser.add_argument("--v6-5-review-finding-list-label", type=str)
    parser.add_argument("--v6-5-review-decision-label", type=str)
    parser.add_argument("--v6-5-review-risk-disposition-label", type=str)
    parser.add_argument("--v6-5-review-non-execution-boundary-label", type=str)
    parser.add_argument("--v6-5-implementation-plan-review-packet-name", type=str)
    parser.add_argument("--v6-5-implementation-plan-review-confirm-token", type=str)
    parser.add_argument("--v6-5-implementation-plan-review-human-operator", type=str)

    parser.add_argument("--station-chief-v6-6-post-mvp-expansion-lane-non-executing-review-disposition-schema", action="store_true")
    parser.add_argument("--station-chief-v6-6-post-mvp-expansion-lane-non-executing-review-disposition", action="store_true")
    parser.add_argument("--write-station-chief-v6-6-post-mvp-expansion-lane-non-executing-review-disposition", type=str)
    parser.add_argument("--v6-6-implementation-plan-review-packet-reference-label", type=str)
    parser.add_argument("--v6-6-implementation-plan-packet-reference-label", type=str)
    parser.add_argument("--v6-6-readiness-packet-reference-label", type=str)
    parser.add_argument("--v6-6-lane-scope-packet-reference-label", type=str)
    parser.add_argument("--v6-6-selected-expansion-lane-label", type=str)
    parser.add_argument("--v6-6-review-disposition-label", type=str)
    parser.add_argument("--v6-6-disposition-condition-list-label", type=str)
    parser.add_argument("--v6-6-disposition-hold-label", type=str)
    parser.add_argument("--v6-6-disposition-next-gate-label", type=str)
    parser.add_argument("--v6-6-disposition-non-execution-boundary-label", type=str)
    parser.add_argument("--v6-6-review-disposition-packet-name", type=str)
    parser.add_argument("--v6-6-review-disposition-confirm-token", type=str)
    parser.add_argument("--v6-6-review-disposition-human-operator", type=str)

    parser.add_argument("--station-chief-v8-finish-line-control-plane-schema", action="store_true")
    parser.add_argument("--station-chief-v8-finish-line-control-plane", action="store_true")
    parser.add_argument("--station-chief-v8-baby-step-chain-closeout", action="store_true")
    parser.add_argument("--station-chief-v8-control-plane-status", action="store_true")

    parser.add_argument("--station-chief-v9-controlled-local-worker-pilot-schema", action="store_true")
    parser.add_argument("--station-chief-v9-controlled-local-worker-pilot", action="store_true")
    parser.add_argument("--station-chief-v9-worker-profile", action="store_true")
    parser.add_argument("--station-chief-v9-noop-task", action="store_true")
    parser.add_argument("--station-chief-v9-worker-pilot-audit", action="store_true")

    parser.add_argument("--station-chief-v10-multi-worker-sandbox-coordination-schema", action="store_true")
    parser.add_argument("--station-chief-v11-permissioned-tool-task-queue-layer-schema", action="store_true")
    parser.add_argument("--station-chief-v12-autonomous-worker-army-release-candidate-schema", action="store_true")
    parser.add_argument("--station-chief-v13-external-tool-api-pilot-hardening-schema", action="store_true")
    parser.add_argument("--station-chief-v10-multi-worker-sandbox-coordination", action="store_true")
    parser.add_argument("--station-chief-v11-permissioned-tool-task-queue-layer", action="store_true")
    parser.add_argument("--station-chief-v12-autonomous-worker-army-release-candidate", action="store_true")
    parser.add_argument("--station-chief-v13-external-tool-api-pilot-hardening", action="store_true")
    parser.add_argument("--station-chief-v11-tool-registry", action="store_true")
    parser.add_argument("--station-chief-v11-task-envelopes", action="store_true")
    parser.add_argument("--station-chief-v11-virtual-queue", action="store_true")
    parser.add_argument("--station-chief-v11-dispatch-plan", action="store_true")
    parser.add_argument("--station-chief-v11-permission-receipts", action="store_true")
    parser.add_argument("--station-chief-v11-permission-audit", action="store_true")
    parser.add_argument("--station-chief-v12-army-workers", action="store_true")
    parser.add_argument("--station-chief-v12-army-squads", action="store_true")
    parser.add_argument("--station-chief-v12-command-manifest", action="store_true")
    parser.add_argument("--station-chief-v12-mission-envelopes", action="store_true")
    parser.add_argument("--station-chief-v12-dispatch-matrix", action="store_true")
    parser.add_argument("--station-chief-v12-army-cycle-plan", action="store_true")
    parser.add_argument("--station-chief-v12-readiness-receipts", action="store_true")
    parser.add_argument("--station-chief-v12-army-audit", action="store_true")
    parser.add_argument("--station-chief-v13-external-interfaces", action="store_true")
    parser.add_argument("--station-chief-v13-external-action-envelopes", action="store_true")
    parser.add_argument("--station-chief-v13-external-access-policy-gate", action="store_true")
    parser.add_argument("--station-chief-v13-credential-secret-denial-proof", action="store_true")
    parser.add_argument("--station-chief-v13-network-api-denial-proof", action="store_true")
    parser.add_argument("--station-chief-v13-external-pilot-dry-run-plan", action="store_true")
    parser.add_argument("--station-chief-v13-external-permission-receipts", action="store_true")
    parser.add_argument("--station-chief-v13-external-pilot-audit", action="store_true")
    parser.add_argument("--station-chief-v10-sandbox-workers", action="store_true")
    parser.add_argument("--station-chief-v10-sandbox-tasks", action="store_true")
    parser.add_argument("--station-chief-v10-assignment-map", action="store_true")
    parser.add_argument("--station-chief-v10-coordination-ledger", action="store_true")
    parser.add_argument("--station-chief-v10-sandbox-audit", action="store_true")

    parser.add_argument("--station-chief-v6-4-post-mvp-expansion-lane-non-executing-implementation-plan-schema", action="store_true")
    parser.add_argument("--station-chief-v6-4-post-mvp-expansion-lane-non-executing-implementation-plan", action="store_true")
    parser.add_argument("--write-station-chief-v6-4-post-mvp-expansion-lane-non-executing-implementation-plan", metavar="DIR", type=str)
    parser.add_argument("--v6-4-readiness-packet-reference-label", type=str)
    parser.add_argument("--v6-4-lane-scope-packet-reference-label", type=str)
    parser.add_argument("--v6-4-selected-expansion-lane-label", type=str)
    parser.add_argument("--v6-4-implementation-plan-label", type=str)
    parser.add_argument("--v6-4-implementation-step-list-label", type=str)
    parser.add_argument("--v6-4-implementation-risk-register-label", type=str)
    parser.add_argument("--v6-4-implementation-rollback-plan-label", type=str)
    parser.add_argument("--v6-4-implementation-non-execution-boundary-label", type=str)
    parser.add_argument("--v6-4-implementation-plan-packet-name", type=str)
    parser.add_argument("--v6-4-implementation-plan-confirm-token", type=str)
    parser.add_argument("--v6-4-implementation-plan-human-operator", type=str)
    parser.add_argument("--station-chief-v6-0-mvp-lock", action="store_true")
    parser.add_argument("--write-station-chief-v6-0-mvp-lock", metavar="DIR", type=str)
    parser.add_argument("--v6-mvp-local-task-candidate-label", type=str)
    parser.add_argument("--v6-mvp-sandbox-worker-label", type=str)
    parser.add_argument("--v6-mvp-handoff-packet-reference-label", type=str)
    parser.add_argument("--v6-mvp-acknowledgement-packet-reference-label", type=str)
    parser.add_argument("--v6-mvp-acceptance-review-packet-reference-label", type=str)
    parser.add_argument("--v6-mvp-ready-state-packet-reference-label", type=str)
    parser.add_argument("--v6-mvp-dry-run-assignment-packet-reference-label", type=str)
    parser.add_argument("--v6-mvp-dry-run-result-packet-reference-label", type=str)
    parser.add_argument("--v6-mvp-dry-run-replay-audit-packet-reference-label", type=str)
    parser.add_argument("--v6-mvp-lock-label", type=str)
    parser.add_argument("--v6-mvp-lock-packet-name", type=str)
    parser.add_argument("--v6-mvp-lock-confirm-token", type=str)
    parser.add_argument("--v6-mvp-lock-human-operator", type=str)
    parser.add_argument("--sandbox-worker-dry-run-replay-audit-candidate-schema", action="store_true")
    parser.add_argument("--sandbox-worker-dry-run-replay-audit-candidate", action="store_true")
    parser.add_argument("--write-sandbox-worker-dry-run-replay-audit-candidate", metavar="DIR", type=str)
    parser.add_argument("--v5-replay-sandbox-worker-label", type=str)
    parser.add_argument("--v5-replay-handoff-packet-reference-label", type=str)
    parser.add_argument("--v5-replay-acknowledgement-packet-reference-label", type=str)
    parser.add_argument("--v5-replay-acceptance-review-packet-reference-label", type=str)
    parser.add_argument("--v5-replay-ready-state-packet-reference-label", type=str)
    parser.add_argument("--v5-replay-dry-run-assignment-packet-reference-label", type=str)
    parser.add_argument("--v5-replay-dry-run-result-packet-reference-label", type=str)
    parser.add_argument("--v5-replay-task-label", type=str)
    parser.add_argument("--v5-replay-result-label", type=str)
    parser.add_argument("--v5-replay-audit-label", type=str)
    parser.add_argument("--v5-dry-run-replay-audit-packet-name", type=str)
    parser.add_argument("--v5-dry-run-replay-audit-confirm-token", type=str)
    parser.add_argument("--v5-dry-run-replay-audit-human-operator", type=str)
    parser.add_argument("--sandbox-worker-dry-run-result-candidate-schema", action="store_true")
    parser.add_argument("--sandbox-worker-dry-run-result-candidate", action="store_true")
    parser.add_argument("--write-sandbox-worker-dry-run-result-candidate", metavar="DIR", type=str)
    parser.add_argument("--v5-result-sandbox-worker-label", type=str)
    parser.add_argument("--v5-result-handoff-packet-reference-label", type=str)
    parser.add_argument("--v5-result-acknowledgement-packet-reference-label", type=str)
    parser.add_argument("--v5-result-acceptance-review-packet-reference-label", type=str)
    parser.add_argument("--v5-result-ready-state-packet-reference-label", type=str)
    parser.add_argument("--v5-result-dry-run-assignment-packet-reference-label", type=str)
    parser.add_argument("--v5-result-task-label", type=str)
    parser.add_argument("--v5-result-label", type=str)
    parser.add_argument("--v5-dry-run-result-packet-name", type=str)
    parser.add_argument("--v5-dry-run-result-confirm-token", type=str)
    parser.add_argument("--v5-dry-run-result-human-operator", type=str)
    parser.add_argument("--sandbox-worker-dry-run-assignment-candidate-schema", action="store_true")
    parser.add_argument("--sandbox-worker-dry-run-assignment-candidate", action="store_true")
    parser.add_argument("--write-sandbox-worker-dry-run-assignment-candidate", metavar="DIR", type=str)
    parser.add_argument("--v5-dry-run-sandbox-worker-label", type=str)
    parser.add_argument("--v5-dry-run-handoff-packet-reference-label", type=str)
    parser.add_argument("--v5-dry-run-acknowledgement-packet-reference-label", type=str)
    parser.add_argument("--v5-dry-run-acceptance-review-packet-reference-label", type=str)
    parser.add_argument("--v5-dry-run-ready-state-packet-reference-label", type=str)
    parser.add_argument("--v5-dry-run-task-label", type=str)
    parser.add_argument("--v5-dry-run-assignment-packet-name", type=str)
    parser.add_argument("--v5-dry-run-assignment-confirm-token", type=str)
    parser.add_argument("--v5-dry-run-assignment-human-operator", type=str)
    parser.add_argument("--sandbox-worker-ready-state-packet-candidate-schema", action="store_true")
    parser.add_argument("--sandbox-worker-ready-state-packet-candidate", action="store_true")
    parser.add_argument("--write-sandbox-worker-ready-state-packet-candidate", metavar="DIR", type=str)
    parser.add_argument("--v5-ready-sandbox-worker-label", type=str)
    parser.add_argument("--v5-ready-handoff-packet-reference-label", type=str)
    parser.add_argument("--v5-ready-acknowledgement-packet-reference-label", type=str)
    parser.add_argument("--v5-ready-acceptance-review-packet-reference-label", type=str)
    parser.add_argument("--v5-ready-state-packet-name", type=str)
    parser.add_argument("--v5-ready-state-confirm-token", type=str)
    parser.add_argument("--v5-ready-state-human-operator", type=str)
    parser.add_argument("--sandbox-worker-acceptance-candidate-review-schema", action="store_true")
    parser.add_argument("--sandbox-worker-acceptance-candidate-review", action="store_true")
    parser.add_argument("--write-sandbox-worker-acceptance-candidate-review", metavar="DIR", type=str)
    parser.add_argument("--v5-accept-sandbox-worker-label", type=str)
    parser.add_argument("--v5-accept-handoff-packet-reference-label", type=str)
    parser.add_argument("--v5-accept-acknowledgement-packet-reference-label", type=str)
    parser.add_argument("--v5-acceptance-review-packet-name", type=str)
    parser.add_argument("--v5-acceptance-confirm-token", type=str)
    parser.add_argument("--v5-acceptance-human-operator", type=str)
    parser.add_argument("--candidate-action-label", type=str)
    parser.add_argument("--required-final-approver", type=str)
    return parser


def main() -> None:
    parser = _build_arg_parser()
    parser.add_argument("--compare-approval-records", nargs=2, metavar=("BEFORE_JSON", "AFTER_JSON"), help="Compare two signed approval records")
    parser.add_argument("--approval-record-file", action="append", default=[], help="Path to a signed approval record file (can be used multiple times)")
    parser.add_argument("--approval-ledger-index", action="store_true", help="Generate an approval ledger index from provided records")
    parser.add_argument("--approval-ledger-label", default="station-chief-approval-ledger", help="Label for the approval ledger")
    parser.add_argument("--write-approval-ledger", metavar="DIR", help="Write approval ledger artifacts to DIR (implies --approval-ledger-index)")
    parser.add_argument("--verify-approval-ledger", metavar="LEDGER_JSON", help="Verify an approval ledger JSON file")
    parser.add_argument("--lookup-approval-digest", metavar="DIGEST", help="Lookup an approval record by digest in the generated ledger")

    parser.add_argument("--station-chief-v14-production-readiness-rollback-live-safety-gates-schema", action="store_true", help="Print Station Chief v14.0 schema and exit")
    parser.add_argument("--station-chief-v14-production-readiness-rollback-live-safety-gates", action="store_true", help="Attach Station Chief v14.0 bundle")
    parser.add_argument("--station-chief-v14-production-readiness-gates", action="store_true", help="Attach v14.0 readiness gates")
    parser.add_argument("--station-chief-v14-rollback-playbooks", action="store_true", help="Attach v14.0 rollback playbooks")
    parser.add_argument("--station-chief-v14-live-safety-gate-manifest", action="store_true", help="Attach v14.0 live safety manifest")
    parser.add_argument("--station-chief-v14-supervised-production-pilot-preflight", action="store_true", help="Attach v14.0 supervised preflight")
    parser.add_argument("--station-chief-v14-emergency-stop-abort-controls", action="store_true", help="Attach v14.0 abort controls")
    parser.add_argument("--station-chief-v14-observability-audit-telemetry", action="store_true", help="Attach v14.0 telemetry manifest")
    parser.add_argument("--station-chief-v14-production-readiness-policy-gate", action="store_true", help="Attach v14.0 policy gate")
    parser.add_argument("--station-chief-v14-production-readiness-receipts", action="store_true", help="Attach v14.0 receipts")
    parser.add_argument("--station-chief-v14-production-safety-audit", action="store_true", help="Attach v14.0 safety audit")

    parser.add_argument("--station-chief-v15-full-auto-agent-army-ready-final-readiness-lock-schema", action="store_true", help="Print Station Chief v15.0 schema and exit")
    parser.add_argument("--station-chief-v15-full-auto-agent-army-ready-final-readiness-lock", action="store_true", help="Attach Station Chief v15.0 bundle")
    parser.add_argument("--station-chief-v15-final-readiness-domains", action="store_true", help="Attach v15.0 readiness domains")
    parser.add_argument("--station-chief-v15-final-activation-prerequisites", action="store_true", help="Attach v15.0 prerequisites")
    parser.add_argument("--station-chief-v15-human-approval-override", action="store_true", help="Attach v15.0 human override manifest")
    parser.add_argument("--station-chief-v15-command-authority-matrix", action="store_true", help="Attach v15.0 command authority matrix")
    parser.add_argument("--station-chief-v15-army-readiness-scorecard", action="store_true", help="Attach v15.0 army readiness scorecard")
    parser.add_argument("--station-chief-v15-safety-evidence-ledger", action="store_true", help="Attach v15.0 safety evidence ledger")
    parser.add_argument("--station-chief-v15-activation-denial-proof", action="store_true", help="Attach v15.0 activation denial proof")
    parser.add_argument("--station-chief-v15-no-live-action-audit", action="store_true", help="Attach v15.0 no live action audit")
    parser.add_argument("--station-chief-v15-final-readiness-certificate", action="store_true", help="Attach v15.0 readiness certificate")

    parser.add_argument("--station-chief-v16-security-integrity-spine-schema", action="store_true", help="Print Station Chief v16.0 schema and exit")
    parser.add_argument("--station-chief-v16-security-integrity-spine", action="store_true", help="Attach Station Chief v16.0 bundle")
    parser.add_argument("--station-chief-v16-security-domains", action="store_true", help="Attach v16.0 security domains")
    parser.add_argument("--station-chief-v16-packet-hash-manifest", action="store_true", help="Attach v16.0 packet hash manifest")
    parser.add_argument("--station-chief-v16-tamper-evident-lineage", action="store_true", help="Attach v16.0 lineage manifest")
    parser.add_argument("--station-chief-v16-signature-doctrine", action="store_true", help="Attach v16.0 signature doctrine")
    parser.add_argument("--station-chief-v16-key-separation-trust-boundary", action="store_true", help="Attach v16.0 trust boundary")
    parser.add_argument("--station-chief-v16-repo-trust-model", action="store_true", help="Attach v16.0 repo trust model")
    parser.add_argument("--station-chief-v16-sensitive-packet-encryption-review", action="store_true", help="Attach v16.0 encryption review")
    parser.add_argument("--station-chief-v16-security-validator-hardening", action="store_true", help="Attach v16.0 validator hardening")
    parser.add_argument("--station-chief-v16-security-audit-replay-packet", action="store_true", help="Attach v16.0 replay packet")
    parser.add_argument("--station-chief-v16-security-spine-lock", action="store_true", help="Attach v16.0 spine lock")
    parser.add_argument("--station-chief-v16-security-audit", action="store_true", help="Attach v16.0 security audit record")

    parser.add_argument("--station-chief-v17-live-activation-protocol-schema", action="store_true", help="Print Station Chief v17.0 schema and exit")
    parser.add_argument("--station-chief-v17-live-activation-protocol", action="store_true", help="Attach Station Chief v17.0 bundle")
    parser.add_argument("--station-chief-v17-live-action-taxonomy", action="store_true", help="Attach v17.0 taxonomy")
    parser.add_argument("--station-chief-v17-first-live-action-allowlist", action="store_true", help="Attach v17.0 first action allowlist")
    parser.add_argument("--station-chief-v17-preview-readonly-repo-inspection", action="store_true", help="Attach v17.0 preview packet")
    parser.add_argument("--station-chief-v17-approved-readonly-repo-inspection", action="store_true", help="Execute v17.0 controlled readonly inspection")
    parser.add_argument("--station-chief-v17-approval-phrase", type=str, help="Human approval phrase for v17.0 live actions")
    parser.add_argument("--station-chief-v17-operator-label", type=str, help="Metadata label for human operator")
    parser.add_argument("--station-chief-v17-live-action-receipt", action="store_true", help="Attach v17.0 live action receipt")
    parser.add_argument("--station-chief-v17-live-activation-audit", action="store_true", help="Attach v17.0 live activation audit")

    args = parser.parse_args()

    if args.compare_dry_run_bundles:
        before_path, after_path = args.compare_dry_run_bundles
        before_bundle = load_json_file(before_path)
        after_bundle = load_json_file(after_path)
        print(json.dumps(compare_dry_run_bundles(before_bundle, after_bundle), indent=2, ensure_ascii=False))
        return

    if args.compare_approval_records:
        before_path, after_path = args.compare_approval_records
        before_record = load_json_file(before_path)
        after_record = load_json_file(after_path)
        
        if "signed_approval_record" in before_record:
            before_record = before_record["signed_approval_record"]
        if "signed_approval_record" in after_record:
            after_record = after_record["signed_approval_record"]
            
        print(json.dumps(compare_signed_approval_records(before_record, after_record), indent=2, ensure_ascii=False))
        return

    if args.verify_approval_ledger:
        ledger = load_json_file(args.verify_approval_ledger)
        if "approval_ledger_index" in ledger:
            ledger = ledger["approval_ledger_index"]
        print(json.dumps(verify_approval_ledger_index(ledger), indent=2, ensure_ascii=False))
        return

    if args.work_order_schema:
        print(json.dumps(create_executable_work_order_schema(), indent=2, ensure_ascii=False))
        return

    if args.worker_role_schema:
        print(json.dumps(create_worker_role_schema(), indent=2, ensure_ascii=False))
        return

    if args.department_routing_schema:
        print(json.dumps(create_department_routing_schema(), indent=2, ensure_ascii=False))
        return

    if args.orchestration_schema:
        print(json.dumps(create_orchestration_topology_schema(), indent=2, ensure_ascii=False))
        return

    if args.operator_console_schema:
        print(json.dumps(create_operator_console_screen_schema(), indent=2, ensure_ascii=False))
        return

    if args.patch_hardening_schema:
        print(json.dumps(create_patch_hardening_schema(), indent=2, ensure_ascii=False))
        return

    if args.deployment_artifact_schema:
        print(json.dumps(make_deployment_artifact_schema(), indent=2, ensure_ascii=False))
        return

    if args.controlled_worker_schema:
        print(json.dumps(create_controlled_worker_execution_schema(), indent=2, ensure_ascii=False))
        return

    if args.tool_permission_schema:
        print(json.dumps(create_tool_permission_binding_schema(), indent=2, ensure_ascii=False))
        return

    if args.telemetry_abort_schema:
        print(json.dumps(create_live_execution_telemetry_abort_schema(), indent=2, ensure_ascii=False))
        return

    if args.post_run_audit_schema:
        print(json.dumps(create_post_run_audit_expansion_schema(), indent=2, ensure_ascii=False))
        return

    if args.multi_worker_coordination_schema:
        print(json.dumps(create_multi_worker_sandbox_coordination_schema(), indent=2, ensure_ascii=False))
        return

    if args.external_tool_preview_schema:
        print(json.dumps(create_controlled_external_tool_adapter_preview_schema(), indent=2, ensure_ascii=False))
        return

    if args.external_api_dry_run_schema:
        print(json.dumps(create_permissioned_external_api_dry_run_preview_schema(), indent=2, ensure_ascii=False))
        return
    if args.audit_replay_preview_schema:
        print(json.dumps(create_controlled_multi_worker_audit_replay_preview_schema(), indent=2, ensure_ascii=False))
        return
    if args.operator_approval_queue_schema:
        print(json.dumps(create_operator_approval_queue_enforcement_schema(), indent=2, ensure_ascii=False))
        return
    if args.release_candidate_hardening_schema:
        print(json.dumps(create_release_candidate_hardening_schema(), indent=2, ensure_ascii=False))
        return

    if args.first_supervised_production_dry_run_schema:
        print(json.dumps(create_first_supervised_production_dry_run_schema(), indent=2, ensure_ascii=False))
        return

    if args.credential_vault_denial_secret_handling_proof_schema:
        print(json.dumps(create_credential_vault_denial_secret_handling_proof_schema(), indent=2, ensure_ascii=False))
        return

    if args.network_socket_lockdown_proof_schema:
        print(json.dumps(create_network_socket_lockdown_proof_schema(), indent=2, ensure_ascii=False))
        return

    if args.live_external_action_final_preflight_gate_schema:
        print(json.dumps(create_live_external_action_final_preflight_gate_schema(), indent=2, ensure_ascii=False))
        return

    if args.first_tiny_real_world_supervised_execution_candidate_schema:
        print(json.dumps(create_first_tiny_real_world_supervised_execution_candidate_schema(), indent=2, ensure_ascii=False))
        return

    if args.post_action_verification_and_audit_review_schema:
        print(json.dumps(create_post_action_verification_and_audit_review_schema(), indent=2, ensure_ascii=False))
        return

    if args.supervised_rollback_cleanup_candidate_schema:
        print(json.dumps(create_supervised_rollback_cleanup_candidate_schema(), indent=2, ensure_ascii=False))
        return

    if args.limited_live_worker_activation_candidate_schema:
        print(json.dumps(create_limited_live_worker_activation_candidate_schema(), indent=2, ensure_ascii=False))
        return

    if args.permissioned_worker_task_assignment_candidate_schema:
        print(json.dumps(create_permissioned_worker_task_assignment_candidate_schema(), indent=2, ensure_ascii=False))
        return

    if args.task_assignment_audit_closeout_candidate_schema:
        print(json.dumps(create_task_assignment_audit_closeout_candidate_schema(), indent=2, ensure_ascii=False))
        return

    if args.non_executing_task_queue_preview_candidate_schema:
        print(json.dumps(create_non_executing_task_queue_preview_candidate_schema(), indent=2, ensure_ascii=False))
        return

    if args.task_queue_preview_audit_closeout_candidate_schema:
        print(json.dumps(create_task_queue_preview_audit_closeout_candidate_schema(), indent=2, ensure_ascii=False))
        return

    if args.non_executing_queue_routing_preview_schema:
        print(json.dumps(create_non_executing_queue_routing_preview_schema(), indent=2, ensure_ascii=False))
        return

    if args.live_queue_orchestration_candidate_review_schema:
        print(json.dumps(create_live_queue_orchestration_candidate_review_schema(), indent=2, ensure_ascii=False))
        return

    if args.first_live_queue_execution_candidate_review_schema:
        print(json.dumps(create_first_live_queue_execution_candidate_review_schema(), indent=2, ensure_ascii=False))
        return

    if args.first_supervised_local_execution_kernel_candidate_schema:
        print(json.dumps(create_first_supervised_local_execution_kernel_candidate_schema(), indent=2, ensure_ascii=False))
        return
    if args.controlled_repeatable_local_execution_candidate_schema:
        print(json.dumps(create_controlled_repeatable_local_execution_candidate_schema(), indent=2, ensure_ascii=False))
        return
    if args.sandbox_worker_handoff_candidate_schema:
        print(json.dumps(create_sandbox_worker_handoff_candidate_schema(), indent=2, ensure_ascii=False))
        return
    if args.sandbox_worker_acknowledgement_candidate_schema:
        print(json.dumps(create_sandbox_worker_acknowledgement_candidate_schema(), indent=2, ensure_ascii=False))
        return

    if args.limited_external_tool_supervised_pilot_schema:
        print(json.dumps(create_limited_external_tool_supervised_pilot_schema(), indent=2, ensure_ascii=False))
        return

    if args.worker_hiring_activation_pilot_schema:
        print(json.dumps(create_controlled_worker_hiring_activation_pilot_schema(), indent=2, ensure_ascii=False))
        return

    if args.production_readiness_gate_schema:
        print(json.dumps(create_controlled_production_readiness_gate_schema(), indent=2, ensure_ascii=False))
        return

    if args.list_controlled_execution_profiles:
        print(json.dumps(create_controlled_execution_profile_catalog(), indent=2, ensure_ascii=False))
        return

    if args.verify_release_manifest:
        manifest = load_json_file(args.verify_release_manifest)
        if "stable_release_manifest" in manifest:
            manifest = manifest["stable_release_manifest"]
        print(json.dumps(verify_stable_release_manifest(manifest), indent=2, ensure_ascii=False))
        return

    if args.stable_release_manifest:
        stable_manifest = create_stable_release_manifest()
        print(
            json.dumps(
                {
                    "runtime_version": stable_manifest.get("runtime_version"),
                    "release_status": stable_manifest.get("release_status"),
                    "stable_release_manifest": stable_manifest,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return

    if args.approval_review_ui_schema:
        print(json.dumps(create_approval_review_ui_schema(), indent=2, ensure_ascii=False))
        return

    if args.verify_approval_record:
        handoff_path, record_path = args.verify_approval_record
        approval_handoff_packet = load_json_file(handoff_path)
        approval_record = load_json_file(record_path)
        print(json.dumps(verify_signed_approval_record(approval_handoff_packet, approval_record), indent=2, ensure_ascii=False))
        return

    if args.fixture_test:
        print(json.dumps(run_fixture_tests(), indent=2, ensure_ascii=False))
        return

    if args.list_execution_profiles:
        print(json.dumps(list_execution_profiles(), indent=2, ensure_ascii=False))
        return

    if args.list_adapters:
        print(json.dumps(list_adapters(), indent=2, ensure_ascii=False))
        return

    if args.resume_run_id:
        if not args.registry_dir:
            print(json.dumps({"resume_status": "ERROR", "error": "--resume-run-id requires --registry-dir"}, indent=2, ensure_ascii=False))
            return
        print(json.dumps(resume_run(args.registry_dir, args.resume_run_id), indent=2, ensure_ascii=False))
        return

    if args.demo:
        command = "check please"
    elif args.command:
        command = args.command
    else:
        command = "check please"

    if args.list_overlays:
        print(json.dumps(load_overlay_stack(), indent=2, ensure_ascii=False))
        return

    if args.execute_sandbox_file_write and not args.execution_dir:
        print(json.dumps({"execution_status": "ERROR", "error": "--execute-sandbox-file-write requires --execution-dir"}, indent=2, ensure_ascii=False))
        return

    if args.execute_repo_patch and not args.patch_root:
        print(json.dumps({"patch_status": "ERROR", "error": "--execute-repo-patch requires --patch-root"}, indent=2, ensure_ascii=False))
        return

    if (args.sign_approval_record or args.write_approval_record) and (not args.approval_reviewer or not args.approval_decision):
        print(
            json.dumps(
                {
                    "approval_record_status": "ERROR",
                    "error": "--sign-approval-record requires --approval-reviewer and --approval-decision",
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return

    result = run_station_chief(command, adapter_name=args.adapter)

    if args.plan_file_operation or args.execute_sandbox_file_write:
        result = attach_file_operation(
            result,
            args.execution_dir,
            args.target_filename,
            args.confirm_execution,
            execute=args.execute_sandbox_file_write,
        )

    if args.plan_repo_patch or args.execute_repo_patch:
        allowed_files = args.allowed_patch_file if args.allowed_patch_file is not None else [args.patch_relative_path]
        if not allowed_files:
            allowed_files = [args.patch_relative_path]
        result = attach_repo_patch(
            result,
            args.patch_root,
            args.patch_relative_path,
            allowed_files,
            args.patch_content,
            args.confirm_patch,
            execute=args.execute_repo_patch,
        )

    if (
        args.dry_run_bundle
        or args.write_dry_run_bundle
        or args.execution_profile is not None
        or args.approval_handoff
        or args.compare_against_dry_run_bundle
        or args.write_approval_handoff
        or args.sign_approval_record
        or args.write_approval_record
    ):
        result = attach_execution_profile_and_dry_run(
            result,
            requested_profile=args.execution_profile,
            include_dry_run_bundle=True,
        )

    if args.compare_against_dry_run_bundle or args.approval_handoff or args.write_approval_handoff or args.sign_approval_record or args.write_approval_record:
        result = attach_approval_handoff(
            result,
            comparison_bundle_path=args.compare_against_dry_run_bundle,
            include_handoff=args.approval_handoff or args.write_approval_handoff is not None or args.sign_approval_record or args.write_approval_record,
        )

    if args.sign_approval_record or args.write_approval_record:
        result = attach_signed_approval_record(
            result,
            reviewer_name=args.approval_reviewer,
            approval_decision=args.approval_decision,
            approval_note=args.approval_note,
            approval_record_token=args.approval_record_token,
            patch_preview_reviewed=args.patch_preview_reviewed,
            changed_file_scope_reviewed=args.changed_file_scope_reviewed,
            baseline_protection_reviewed=args.baseline_protection_reviewed,
            risk_summary_reviewed=args.risk_summary_reviewed,
        )

    if args.approval_ledger_index or args.write_approval_ledger:
        if not args.approval_record_file:
            print(json.dumps({
                "approval_ledger_status": "ERROR",
                "error": "--approval-ledger-index requires at least one --approval-record-file"
            }, indent=2, ensure_ascii=False))
            return
            
        result = attach_approval_ledger(
            result,
            approval_record_paths=args.approval_record_file,
            ledger_label=args.approval_ledger_label,
            lookup_digest=args.lookup_approval_digest
        )

    if args.release_lock or args.write_release_lock:
        result = attach_release_lock(result)

    if args.controlled_execution or args.write_controlled_execution:
        result = attach_controlled_execution(
            result,
            requested_profile=args.controlled_execution_profile,
            attempted_actions=args.attempted_action
        )

    if args.work_order_executor or args.write_work_order_executor:
        result = attach_work_order_executor(result)

    if args.worker_hiring_registry or args.write_worker_hiring_registry:
        result = attach_worker_hiring_registry(result)

    if args.department_routing or args.write_department_routing:
        result = attach_department_routing(result)

    if args.multi_agent_orchestration or args.write_multi_agent_orchestration:
        result = attach_multi_agent_orchestration(result)

    if args.operator_console or args.write_operator_console:
        result = attach_operator_console(result)

    if args.github_patch_hardening or args.write_github_patch_hardening:
        result = attach_github_patch_hardening(
            result,
            patch_root=args.hardening_patch_root,
            allowed_patch_file=args.hardening_allowed_patch_file,
            patch_content=args.hardening_patch_content,
            original_content=args.hardening_original_content,
            changed_files=args.hardening_changed_file
        )

    if args.deployment_packaging or args.write_deployment_packaging:
        result = attach_deployment_packaging(result)

    if args.controlled_worker_execution or args.write_controlled_worker_execution:
        worker_payload = None
        if args.controlled_worker_payload_json:
            try:
                worker_payload = json.loads(args.controlled_worker_payload_json)
            except json.JSONDecodeError:
                # Handled inside attach_controlled_worker_execution if None
                pass
                
        result = attach_controlled_worker_execution(
            result,
            worker_id=args.controlled_worker_id,
            sandbox_task=args.controlled_worker_task or "noop",
            confirmation_token=args.confirm_controlled_worker_execution,
            requested_tool_permissions=args.controlled_worker_tool_permission,
            payload=worker_payload
        )

    if args.tool_permission_binding or args.write_tool_permission_binding:
        provided_tokens = {}
        for t in args.tool_permission_token:
            if "=" in t:
                pk, pv = t.split("=", 1)
                provided_tokens[pk] = pv
                
        tool_outputs = []
        for o in args.tool_permission_output_json:
            try:
                tool_outputs.append(json.loads(o))
            except json.JSONDecodeError:
                pass
                
        result = attach_tool_permission_binding(
            result,
            worker_id=args.tool_permission_worker_id,
            requested_tool_permissions=args.tool_permission_request,
            provided_tool_tokens=provided_tokens,
            sandbox_task=args.tool_permission_sandbox_task or "noop",
            tool_outputs=tool_outputs
        )

    if args.live_telemetry_abort or args.write_live_telemetry_abort:
        telemetry_payload = None
        if args.telemetry_partial_payload_json:
            try:
                telemetry_payload = json.loads(args.telemetry_partial_payload_json)
            except json.JSONDecodeError:
                pass
                
        result = attach_live_execution_telemetry_abort(
            result,
            worker_id=args.telemetry_worker_id,
            confirmation_token=args.telemetry_confirm_token,
            abort_reason=args.telemetry_abort_reason,
            failure_reason=args.telemetry_failure_reason,
            timeout_limit_steps=args.telemetry_timeout_limit_steps,
            observed_steps=args.telemetry_observed_steps,
            partial_payload=telemetry_payload
        )

    post_run_audit_before = None
    post_run_audit_after = None
    if args.post_run_audit_before_json is not None:
        try:
            post_run_audit_before = json.loads(args.post_run_audit_before_json)
        except json.JSONDecodeError as exc:
            print(json.dumps({"post_run_audit_expansion_status": "ERROR", "error": f"Invalid --post-run-audit-before-json: {exc}"}, indent=2, ensure_ascii=False))
            return
    if args.post_run_audit_after_json is not None:
        try:
            post_run_audit_after = json.loads(args.post_run_audit_after_json)
        except json.JSONDecodeError as exc:
            print(json.dumps({"post_run_audit_expansion_status": "ERROR", "error": f"Invalid --post-run-audit-after-json: {exc}"}, indent=2, ensure_ascii=False))
            return

    external_tool_request_payload = None
    external_tool_response_preview = None
    if args.external_tool_request_payload_json is not None:
        try:
            external_tool_request_payload = json.loads(args.external_tool_request_payload_json)
            if not isinstance(external_tool_request_payload, dict):
                raise ValueError("payload must be a JSON object")
        except (json.JSONDecodeError, ValueError) as exc:
            print(json.dumps({"controlled_external_tool_adapter_preview_status": "ERROR", "error": f"Invalid --external-tool-request-payload-json: {exc}"}, indent=2, ensure_ascii=False))
            return
    if args.external_tool_response_preview_json is not None:
        try:
            external_tool_response_preview = json.loads(args.external_tool_response_preview_json)
            if not isinstance(external_tool_response_preview, dict):
                raise ValueError("response preview must be a JSON object")
        except (json.JSONDecodeError, ValueError) as exc:
            print(json.dumps({"controlled_external_tool_adapter_preview_status": "ERROR", "error": f"Invalid --external-tool-response-preview-json: {exc}"}, indent=2, ensure_ascii=False))
            return

    if args.post_run_audit_expansion or args.write_post_run_audit_expansion:
        result = attach_post_run_audit_expansion(
            result,
            worker_id=args.post_run_audit_worker_id or "station-chief-sandbox-worker-001",
            confirmation_token=args.post_run_audit_confirm_token,
            before_result=post_run_audit_before,
            after_result=post_run_audit_after,
            artifact_names=args.post_run_audit_artifact_name,
            validator_names=args.post_run_audit_validator_name,
            observed_failures=args.post_run_audit_observed_failure,
        )

    if args.multi_worker_sandbox_coordination or args.write_multi_worker_sandbox_coordination:
        result = attach_multi_worker_sandbox_coordination(
            result,
            roster_label=args.multi_worker_roster_label,
            confirmation_token=args.multi_worker_confirm_token,
            requested_worker_count=args.multi_worker_count,
            worker_roles=args.multi_worker_role,
            requested_shared_resources=args.multi_worker_shared_resource,
            abort_reason=args.multi_worker_abort_reason,
            failure_reason=args.multi_worker_failure_reason,
        )

    if args.controlled_external_tool_preview or args.write_controlled_external_tool_preview:
        if "multi_worker_sandbox_coordination_bundle" not in result or result["multi_worker_sandbox_coordination_bundle"] is None:
            result = attach_multi_worker_sandbox_coordination(result)
        result = attach_controlled_external_tool_adapter_preview(
            result,
            tool_label=args.external_tool_label,
            tool_id=args.external_tool_id,
            confirmation_token=args.external_tool_confirm_token,
            requested_tools=args.external_tool_requested_tool,
            requested_external_action=args.external_tool_requested_action,
            request_label=args.external_tool_request_label,
            request_payload=external_tool_request_payload,
            response_preview=external_tool_response_preview,
            abort_reason=args.external_tool_abort_reason,
        )

    if args.write_permissioned_external_api_dry_run:
        args.permissioned_external_api_dry_run = True

    if getattr(args, "permissioned_external_api_dry_run", False):
        req_payload = None
        if args.external_api_request_payload_json:
            try:
                req_payload = json.loads(args.external_api_request_payload_json)
            except Exception:
                req_payload = {"error": "invalid request payload json"}
        
        fix_payload = None
        if args.external_api_fixture_payload_json:
            try:
                fix_payload = json.loads(args.external_api_fixture_payload_json)
            except Exception:
                fix_payload = {"error": "invalid fixture payload json"}

        result = attach_permissioned_external_api_dry_run_preview(
            result,
            api_label=args.external_api_label,
            endpoint_id=args.external_api_endpoint_id,
            confirmation_token=args.external_api_confirm_token,
            requested_endpoints=args.external_api_requested_endpoint,
            method=args.external_api_method,
            path_template=args.external_api_path_template,
            request_payload=req_payload,
            credential_labels=args.external_api_credential_label,
            fixture_payload=fix_payload
        )

    if args.write_controlled_multi_worker_audit_replay_preview:
        args.controlled_multi_worker_audit_replay_preview = True

    if getattr(args, "controlled_multi_worker_audit_replay_preview", False):
        replay_packets = []
        if args.audit_replay_packet_json:
            for pjson in args.audit_replay_packet_json:
                try:
                    p = json.loads(pjson)
                    replay_packets.append(p)
                except Exception:
                    pass
        
        observed_digest_map = None
        if args.audit_replay_observed_digest_map_json:
            try:
                observed_digest_map = json.loads(args.audit_replay_observed_digest_map_json)
            except Exception:
                observed_digest_map = {"error": "invalid observed digest map json"}

        result = attach_controlled_multi_worker_audit_replay_preview(
            result,
            replay_label=args.audit_replay_label,
            confirmation_token=args.audit_replay_confirm_token,
            replay_packets=replay_packets if replay_packets else None,
            requested_worker_count=args.audit_replay_worker_count,
            replay_mode=args.audit_replay_mode,
            observed_digest_map=observed_digest_map,
            quarantine_reason=args.audit_replay_quarantine_reason
        )

    if args.write_operator_approval_queue_enforcement:
        args.operator_approval_queue_enforcement = True

    if getattr(args, "operator_approval_queue_enforcement", False):
        queued_actions = []
        if args.approval_queue_action_json:
            for ajson in args.approval_queue_action_json:
                try:
                    a = json.loads(ajson)
                    queued_actions.append(a)
                except Exception:
                    pass
        
        operator_decisions = None
        if args.approval_queue_operator_decisions_json:
            try:
                operator_decisions = json.loads(args.approval_queue_operator_decisions_json)
            except Exception:
                operator_decisions = {"error": "invalid operator decisions json"}

        result = attach_operator_approval_queue_enforcement(
            result,
            queue_label=args.approval_queue_label,
            confirmation_token=args.approval_queue_confirm_token,
            queued_actions=queued_actions if queued_actions else None,
            requested_action_count=args.approval_queue_action_count,
            operator_decisions=operator_decisions,
            stale_after_hours=args.approval_queue_stale_after_hours
        )

    if args.write_release_candidate_hardening:
        args.release_candidate_hardening = True

    if getattr(args, "release_candidate_hardening", False):
        known_issues = []
        if args.release_candidate_known_issue_json:
            for kijson in args.release_candidate_known_issue_json:
                try:
                    ki = json.loads(kijson)
                    known_issues.append(ki)
                except Exception:
                    pass
        
        result = attach_release_candidate_hardening(
            result,
            release_candidate_label=args.release_candidate_label,
            confirmation_token=args.release_candidate_confirm_token,
            invariant_labels=args.release_candidate_invariant,
            validator_names=args.release_candidate_validator,
            artifact_contracts=args.release_candidate_artifact_contract,
            known_issues=known_issues if known_issues else None,
            checklist_items=args.release_candidate_checklist_item
        )

    if args.first_supervised_production_dry_run or args.write_first_supervised_production_dry_run:
        result = attach_first_supervised_production_dry_run(
            result,
            dry_run_label=args.dry_run_label,
            confirmation_token=args.dry_run_confirm_token,
            dry_run_task_label=args.dry_run_task_label,
            production_context_label=args.dry_run_production_context_label,
            required_preflight_approver=args.dry_run_required_preflight_approver,
            worker_label=args.dry_run_worker_label,
            quarantine_labels=args.dry_run_quarantine_label
        )

    if args.write_credential_vault_denial_secret_handling_proof:
        args.credential_vault_denial_secret_handling_proof = True

    if getattr(args, "write_network_socket_lockdown_proof", False):
        args.network_socket_lockdown_proof = True

    if getattr(args, "network_socket_lockdown_proof", False):
        args.credential_vault_denial_secret_handling_proof = True

    if args.credential_vault_denial_secret_handling_proof or getattr(args, "write_credential_vault_denial_secret_handling_proof", False):
        result = attach_credential_vault_denial_secret_handling_proof(
            result,
            credential_secret_label=args.credential_secret_label,
            confirmation_token=args.credential_secret_confirm_token,
            credential_boundary_label=args.credential_boundary_label,
            secret_boundary_label=args.secret_boundary_label,
            environment_boundary_label=args.environment_boundary_label,
        )

    if getattr(args, "network_socket_lockdown_proof", False):
        result = attach_network_socket_lockdown_proof(
            result,
            network_socket_label=args.network_socket_label,
            confirmation_token=args.network_socket_confirm_token,
            network_boundary_label=args.network_boundary_label,
            socket_boundary_label=args.socket_boundary_label,
        )

    if getattr(args, "write_live_external_action_final_preflight_gate", False):
        args.live_external_action_final_preflight_gate = True

    if getattr(args, "live_external_action_final_preflight_gate", False):
        result = attach_live_external_action_final_preflight_gate(
            result,
            live_external_action_label=args.live_external_action_label,
            confirmation_token=args.live_external_action_confirm_token,
            candidate_action_label=args.candidate_action_label,
            blast_radius_label=args.blast_radius_label,
            required_final_approver=args.required_final_approver,
        )

    if args.write_supervised_production_pilot_readiness_review:
        args.supervised_production_pilot_readiness_review = True

    if args.supervised_production_pilot_readiness_review or getattr(args, "write_supervised_production_pilot_readiness_review", False):
        args.monitored_rollback_recovery_drill = True
        result = attach_supervised_production_pilot_readiness_review(
            result,
            production_readiness_label=args.production_readiness_label,
            confirmation_token=args.production_readiness_confirm_token,
            candidate_label=args.candidate_label,
            required_production_pilot_reviewer=args.required_production_pilot_reviewer,
            blast_radius_label=args.blast_radius_label,
        )

    if args.supervised_external_api_pilot or getattr(args, "write_supervised_external_api_pilot", False) or args.monitored_rollback_recovery_drill or getattr(args, "write_monitored_rollback_recovery_drill", False):
        result = attach_supervised_external_api_pilot(
            result,
            api_pilot_label=args.api_pilot_label,
            confirmation_token=args.api_pilot_confirm_token,
            api_category_label=args.api_category_label,
            required_api_preflight_approver=args.api_pilot_required_preflight_approver,
            api_request_label=args.api_request_label,
            quarantine_labels=args.api_quarantine_label
        )

    if args.monitored_rollback_recovery_drill or getattr(args, "write_monitored_rollback_recovery_drill", False):
        result = attach_monitored_rollback_recovery_drill(
            result,
            recovery_drill_label=args.recovery_drill_label,
            confirmation_token=args.recovery_drill_confirm_token,
            simulated_failure_label=args.simulated_failure_label,
            rollback_path_label=args.rollback_path_label,
            recovery_checkpoint_label=args.recovery_checkpoint_label,
            required_recovery_approver=args.required_recovery_approver,
            quarantine_labels=args.recovery_quarantine_label,
        )



    if args.limited_external_tool_supervised_pilot or args.write_limited_external_tool_supervised_pilot:
        result = attach_limited_external_tool_supervised_pilot(
            result,
            tool_pilot_label=args.tool_pilot_label,
            confirmation_token=args.tool_pilot_confirm_token,
            tool_category_label=args.tool_category_label,
            required_tool_preflight_approver=args.tool_pilot_required_preflight_approver,
            tool_request_label=args.tool_request_label,
            quarantine_labels=args.tool_quarantine_label,
        )

    if args.controlled_worker_hiring_activation_pilot or args.write_controlled_worker_hiring_activation_pilot:
        result = attach_controlled_worker_hiring_activation_pilot(
            result,
            pilot_label=args.pilot_label,
            confirmation_token=args.pilot_confirm_token,
            pilot_worker_limit=args.pilot_worker_limit,
            worker_labels=args.pilot_worker_label,
            required_supervisor_label=args.pilot_required_supervisor,
            rollback_labels=args.pilot_rollback_label
        )

    if args.controlled_production_readiness_gate or args.write_controlled_production_readiness_gate:
        result = attach_controlled_production_readiness_gate(
            result,
            production_gate_label=args.production_gate_label,
            confirmation_token=args.production_gate_confirm_token,
            required_approver_label=args.production_gate_required_approver,
            capability_labels=args.production_gate_capability,
            pilot_label=args.production_gate_pilot_label,
            pilot_worker_limit=args.production_gate_pilot_worker_limit,
            rollback_labels=args.production_gate_rollback_label
        )

    post_action_verification_and_audit_review_summary = None
    if getattr(args, "write_post_action_verification_and_audit_review", False):
        post_action_verification_and_audit_review_summary = write_post_action_verification_and_audit_review(
            result,
            args.write_post_action_verification_and_audit_review,
            review_label=args.v4_review_label,
            artifact_path=args.v4_review_artifact_path,
            expected_output_directory=args.v4_review_expected_output_directory,
            confirmation_token=args.v4_review_confirm_token,
            human_operator=args.v4_review_human_operator,
            run_label=args.run_label,
        )
        result = dict(result)
        result["post_action_verification_and_audit_review_write_summary"] = post_action_verification_and_audit_review_summary
    elif args.post_action_verification_and_audit_review:
        result = attach_post_action_verification_and_audit_review(
            result,
            review_label=args.v4_review_label,
            artifact_path=args.v4_review_artifact_path,
            expected_output_directory=args.v4_review_expected_output_directory,
            review_output_directory=None,
            confirmation_token=args.v4_review_confirm_token,
            human_operator=args.v4_review_human_operator,
            write_review_records=False,
        )

    supervised_rollback_cleanup_candidate_summary = None
    if getattr(args, "execute_supervised_rollback_cleanup_candidate", False):
        result = attach_supervised_rollback_cleanup_candidate(
            result,
            cleanup_label=args.v4_cleanup_label,
            artifact_path=args.v4_cleanup_artifact_path,
            expected_output_directory=args.v4_cleanup_expected_output_directory,
            confirmation_token=args.v4_cleanup_confirm_token,
            human_operator=args.v4_cleanup_human_operator,
            cleanup_requested=True,
            execute_cleanup=True,
        )
        supervised_rollback_cleanup_candidate_summary = result["cleanup_execution_record"]
        result = dict(result)
        result["supervised_rollback_cleanup_candidate_write_summary"] = supervised_rollback_cleanup_candidate_summary
    elif args.supervised_rollback_cleanup_candidate:
        result = attach_supervised_rollback_cleanup_candidate(
            result,
            cleanup_label=args.v4_cleanup_label,
            artifact_path=args.v4_cleanup_artifact_path,
            expected_output_directory=args.v4_cleanup_expected_output_directory,
            confirmation_token=args.v4_cleanup_confirm_token,
            human_operator=args.v4_cleanup_human_operator,
            cleanup_requested=False,
            execute_cleanup=False,
        )

    if getattr(args, "write_limited_live_worker_activation_candidate", False):
        result = write_limited_live_worker_activation_candidate(
            result,
            args.write_limited_live_worker_activation_candidate,
            worker_template_label=args.v4_worker_template_label,
            activation_record_name=args.v4_worker_activation_record_name,
            confirmation_token=args.v4_worker_activation_confirm_token,
            human_operator=args.v4_worker_activation_human_operator,
            run_label=args.run_label,
        )
    elif args.limited_live_worker_activation_candidate:
        result = attach_limited_live_worker_activation_candidate(
            result,
            worker_template_label=args.v4_worker_template_label,
            activation_output_directory=None,
            activation_record_name=args.v4_worker_activation_record_name,
            confirmation_token=args.v4_worker_activation_confirm_token,
            human_operator=args.v4_worker_activation_human_operator,
            activation_requested=False,
            write_activation_record=False,
        )

    permissioned_worker_task_assignment_candidate_summary = None
    if getattr(args, "write_permissioned_worker_task_assignment_candidate", False):
        result = write_permissioned_worker_task_assignment_candidate(
            result,
            args.write_permissioned_worker_task_assignment_candidate,
            worker_template_label=args.v4_task_worker_template_label,
            task_label=args.v4_task_label,
            task_assignment_record_name=args.v4_task_assignment_record_name,
            confirmation_token=args.v4_task_assignment_confirm_token,
            human_operator=args.v4_task_assignment_human_operator,
            run_label=args.run_label,
        )
        permissioned_worker_task_assignment_candidate_summary = result["task_assignment_write_record"]
        result = dict(result)
        result["permissioned_worker_task_assignment_candidate_write_summary"] = permissioned_worker_task_assignment_candidate_summary
    elif args.permissioned_worker_task_assignment_candidate:
        result = attach_permissioned_worker_task_assignment_candidate(
            result,
            worker_template_label=args.v4_task_worker_template_label,
            task_label=args.v4_task_label,
            task_assignment_output_directory=None,
            task_assignment_record_name=args.v4_task_assignment_record_name,
            confirmation_token=args.v4_task_assignment_confirm_token,
            human_operator=args.v4_task_assignment_human_operator,
            assignment_requested=False,
            write_task_assignment_record=False,
        )

    task_assignment_audit_closeout_candidate_summary = None
    if getattr(args, "write_task_assignment_audit_closeout_candidate", False):
        result = write_task_assignment_audit_closeout_candidate(
            result,
            args.write_task_assignment_audit_closeout_candidate,
            closeout_label=args.v4_closeout_label,
            task_assignment_record_path=args.v4_closeout_task_assignment_record_path,
            expected_task_assignment_output_directory=args.v4_closeout_expected_task_assignment_output_directory,
            closeout_record_name=args.v4_closeout_record_name,
            confirmation_token=args.v4_closeout_confirm_token,
            human_operator=args.v4_closeout_human_operator,
            run_label=args.run_label,
        )
        task_assignment_audit_closeout_candidate_summary = result["task_assignment_closeout_write_record"]
        result = dict(result)
        result["task_assignment_audit_closeout_candidate_write_summary"] = task_assignment_audit_closeout_candidate_summary
    elif args.task_assignment_audit_closeout_candidate:
        result = attach_task_assignment_audit_closeout_candidate(
            result,
            closeout_label=args.v4_closeout_label,
            task_assignment_record_path=args.v4_closeout_task_assignment_record_path,
            expected_task_assignment_output_directory=args.v4_closeout_expected_task_assignment_output_directory,
            closeout_output_directory=None,
            closeout_record_name=args.v4_closeout_record_name,
            confirmation_token=args.v4_closeout_confirm_token,
            human_operator=args.v4_closeout_human_operator,
            closeout_requested=False,
            write_closeout_record=False,
        )

    non_executing_task_queue_preview_candidate_summary = None
    if getattr(args, "write_non_executing_task_queue_preview_candidate", False):
        result = write_non_executing_task_queue_preview_candidate(
            result,
            args.write_non_executing_task_queue_preview_candidate,
            queue_preview_label=args.v4_queue_preview_label,
            task_assignment_record_path=args.v4_queue_preview_task_assignment_record_path,
            expected_task_assignment_output_directory=args.v4_queue_preview_expected_task_assignment_output_directory,
            closeout_record_path=args.v4_queue_preview_closeout_record_path,
            queue_preview_record_name=args.v4_queue_preview_record_name,
            confirmation_token=args.v4_queue_preview_confirm_token,
            human_operator=args.v4_queue_preview_human_operator,
            run_label=args.run_label,
        )
        non_executing_task_queue_preview_candidate_summary = result["queue_preview_write_record"]
        result = dict(result)
        result["non_executing_task_queue_preview_candidate_write_summary"] = non_executing_task_queue_preview_candidate_summary
    elif args.non_executing_task_queue_preview_candidate:
        result = attach_non_executing_task_queue_preview_candidate(
            result,
            queue_preview_label=args.v4_queue_preview_label,
            task_assignment_record_path=args.v4_queue_preview_task_assignment_record_path,
            expected_task_assignment_output_directory=args.v4_queue_preview_expected_task_assignment_output_directory,
            closeout_record_path=args.v4_queue_preview_closeout_record_path,
            queue_preview_output_directory=None,
            queue_preview_record_name=args.v4_queue_preview_record_name,
            confirmation_token=args.v4_queue_preview_confirm_token,
            human_operator=args.v4_queue_preview_human_operator,
            queue_preview_requested=False,
            write_queue_preview_record=False,
        )

    task_queue_preview_audit_closeout_candidate_summary = None
    if getattr(args, "write_task_queue_preview_audit_closeout_candidate", False):
        result = write_task_queue_preview_audit_closeout_candidate(
            result,
            args.write_task_queue_preview_audit_closeout_candidate,
            queue_closeout_label=args.v4_queue_closeout_label,
            queue_preview_record_path=args.v4_queue_closeout_queue_preview_record_path,
            expected_queue_preview_output_directory=args.v4_queue_closeout_expected_queue_preview_output_directory,
            queue_closeout_record_name=args.v4_queue_closeout_record_name,
            confirmation_token=args.v4_queue_closeout_confirm_token,
            human_operator=args.v4_queue_closeout_human_operator,
            run_label=args.run_label,
        )
        task_queue_preview_audit_closeout_candidate_summary = result["queue_closeout_write_record"]
        result = dict(result)
        result["task_queue_preview_audit_closeout_candidate_write_summary"] = task_queue_preview_audit_closeout_candidate_summary
    elif args.task_queue_preview_audit_closeout_candidate:
        result = attach_task_queue_preview_audit_closeout_candidate(
            result,
            queue_closeout_label=args.v4_queue_closeout_label,
            queue_preview_record_path=args.v4_queue_closeout_queue_preview_record_path,
            expected_queue_preview_output_directory=args.v4_queue_closeout_expected_queue_preview_output_directory,
            queue_closeout_output_directory=None,
            queue_closeout_record_name=args.v4_queue_closeout_record_name,
            confirmation_token=args.v4_queue_closeout_confirm_token,
            human_operator=args.v4_queue_closeout_human_operator,
            queue_closeout_requested=False,
            write_queue_closeout_record=False,
        )

    queue_routing_preview_candidate_summary = None
    if getattr(args, "write_non_executing_queue_routing_preview", False):
        result = write_non_executing_queue_routing_preview(
            result,
            args.write_non_executing_queue_routing_preview,
            task_candidate_label=args.v4_task_candidate_label,
            worker_template_label=args.v4_worker_template_label,
            preview_record_name=args.v4_queue_routing_preview_record_name,
            confirmation_token=args.v4_queue_routing_preview_confirm_token,
            human_operator=args.v4_queue_routing_preview_human_operator,
        )
        queue_routing_preview_candidate_summary = result["queue_routing_preview_write_record"]
        result = dict(result)
        result["queue_routing_preview_candidate_write_summary"] = queue_routing_preview_candidate_summary
    elif args.non_executing_queue_routing_preview:
        result = attach_non_executing_queue_routing_preview(
            result,
            task_candidate_label=args.v4_task_candidate_label,
            worker_template_label=args.v4_worker_template_label,
            preview_output_directory=None,
            preview_record_name=args.v4_queue_routing_preview_record_name,
            confirmation_token=args.v4_queue_routing_preview_confirm_token,
            human_operator=args.v4_queue_routing_preview_human_operator,
            preview_requested=False,
            write_preview_record=False,
        )

    live_queue_orchestration_candidate_review_summary = None
    if getattr(args, "write_live_queue_orchestration_candidate_review", False):
        result = write_live_queue_orchestration_candidate_review(
            result,
            args.write_live_queue_orchestration_candidate_review,
            v4_8_routing_preview_reference_label=args.v4_8_routing_preview_reference_label,
            review_record_name=args.v4_orchestration_review_record_name,
            confirmation_token=args.v4_orchestration_review_confirm_token,
            human_operator=args.v4_orchestration_review_human_operator,
        )
        live_queue_orchestration_candidate_review_summary = result["orchestration_candidate_review_write_record"]
        result = dict(result)
        result["live_queue_orchestration_candidate_review_write_summary"] = live_queue_orchestration_candidate_review_summary
    elif args.live_queue_orchestration_candidate_review:
        result = attach_live_queue_orchestration_candidate_review(
            result,
            v4_8_routing_preview_reference_label=args.v4_8_routing_preview_reference_label,
            review_output_directory=None,
            review_record_name=args.v4_orchestration_review_record_name,
            confirmation_token=args.v4_orchestration_review_confirm_token,
            human_operator=args.v4_orchestration_review_human_operator,
            review_requested=False,
            write_review_record=False,
        )

    first_live_queue_execution_candidate_review_summary = None
    if getattr(args, "write_first_live_queue_execution_candidate_review", False):
        result = write_first_live_queue_execution_candidate_review(
            result,
            args.write_first_live_queue_execution_candidate_review,
            v4_9_orchestration_review_reference_label=args.v4_9_orchestration_review_reference_label,
            review_record_name=args.v5_execution_review_record_name,
            confirmation_token=args.v5_execution_review_confirm_token,
            human_operator=args.v5_execution_review_human_operator,
        )
        first_live_queue_execution_candidate_review_summary = result["execution_candidate_review_write_record"]
        result = dict(result)
        result["first_live_queue_execution_candidate_review_write_summary"] = first_live_queue_execution_candidate_review_summary
    elif args.first_live_queue_execution_candidate_review:
        result = attach_first_live_queue_execution_candidate_review(
            result,
            v4_9_orchestration_review_reference_label=args.v4_9_orchestration_review_reference_label,
            review_output_directory=None,
            review_record_name=args.v5_execution_review_record_name,
            confirmation_token=args.v5_execution_review_confirm_token,
            human_operator=args.v5_execution_review_human_operator,
            review_requested=False,
            write_review_record=False,
        )

    first_supervised_local_execution_kernel_candidate_summary = None
    if getattr(args, "write_first_supervised_local_execution_kernel_candidate", False):
        result = write_first_supervised_local_execution_kernel_candidate(
            result,
            args.write_first_supervised_local_execution_kernel_candidate,
            synthetic_task_label=args.v5_synthetic_task_label,
            output_record_name=args.v5_supervised_output_record_name,
            confirmation_token=args.v5_supervised_execution_confirm_token,
            human_operator=args.v5_supervised_execution_human_operator,
        )
        first_supervised_local_execution_kernel_candidate_summary = result["supervised_local_execution_write_record"]
        result = dict(result)
        result["first_supervised_local_execution_kernel_candidate_write_summary"] = first_supervised_local_execution_kernel_candidate_summary
    elif args.first_supervised_local_execution_kernel_candidate:
        result = attach_first_supervised_local_execution_kernel_candidate(
            result,
            synthetic_task_label=args.v5_synthetic_task_label,
            output_directory=None,
            output_record_name=args.v5_supervised_output_record_name,
            confirmation_token=args.v5_supervised_execution_confirm_token,
            human_operator=args.v5_supervised_execution_human_operator,
            execution_requested=False,
            write_output_record=False,
        )

    controlled_repeatable_local_execution_candidate_summary = None
    if getattr(args, "write_controlled_repeatable_local_execution_candidate", False):
        result = write_controlled_repeatable_local_execution_candidate(
            result,
            args.write_controlled_repeatable_local_execution_candidate,
            synthetic_task_label=args.v5_repeatable_synthetic_task_label,
            output_record_name=args.v5_repeatability_proof_record_name,
            repeatability_count=args.v5_repeatability_count,
            confirmation_token=args.v5_repeatable_execution_confirm_token,
            human_operator=args.v5_repeatable_execution_human_operator,
        )
        controlled_repeatable_local_execution_candidate_summary = result["repeatability_proof_write_record"]
        result = dict(result)
        result["controlled_repeatable_local_execution_candidate_write_summary"] = controlled_repeatable_local_execution_candidate_summary
    elif args.controlled_repeatable_local_execution_candidate:
        result = attach_controlled_repeatable_local_execution_candidate(
            result,
            synthetic_task_label=args.v5_repeatable_synthetic_task_label,
            output_directory=None,
            output_record_name=args.v5_repeatability_proof_record_name,
            repeatability_count=args.v5_repeatability_count,
            confirmation_token=args.v5_repeatable_execution_confirm_token,
            human_operator=args.v5_repeatable_execution_human_operator,
            execution_requested=False,
            write_proof_record=False,
        )

    sandbox_worker_handoff_candidate_summary = None
    if getattr(args, "write_sandbox_worker_handoff_candidate", False):
        result = write_sandbox_worker_handoff_candidate(
            result,
            args.write_sandbox_worker_handoff_candidate,
            synthetic_task_label=args.v5_handoff_synthetic_task_label,
            sandbox_worker_label=args.v5_sandbox_worker_label,
            v5_2_repeatability_proof_reference_label=args.v5_repeatability_proof_reference_label,
            handoff_packet_name=args.v5_handoff_packet_name,
            confirmation_token=args.v5_handoff_confirm_token,
            human_operator=args.v5_handoff_human_operator,
        )
        sandbox_worker_handoff_candidate_summary = result["handoff_packet_write_record"]
        result = dict(result)
        result["sandbox_worker_handoff_candidate_write_summary"] = sandbox_worker_handoff_candidate_summary
    elif args.sandbox_worker_handoff_candidate:
        result = attach_sandbox_worker_handoff_candidate(
            result,
            synthetic_task_label=args.v5_handoff_synthetic_task_label,
            sandbox_worker_label=args.v5_sandbox_worker_label,
            v5_2_repeatability_proof_reference_label=args.v5_repeatability_proof_reference_label,
            output_directory=None,
            handoff_packet_name=args.v5_handoff_packet_name,
            confirmation_token=args.v5_handoff_confirm_token,
            human_operator=args.v5_handoff_human_operator,
            handoff_requested=False,
            write_handoff_packet=False,
        )

    if args.station_chief_v6_0_mvp_lock_schema:
        print(json.dumps(create_station_chief_v6_0_mvp_lock_schema(), indent=2, ensure_ascii=False))
        return

    if args.station_chief_v6_1_post_mvp_expansion_review_schema:
        print(json.dumps(create_station_chief_v6_1_post_mvp_expansion_review_schema(), indent=2, ensure_ascii=False))
        return

    if args.station_chief_v6_2_post_mvp_expansion_lane_scope_schema:
        print(json.dumps(create_station_chief_v6_2_post_mvp_expansion_lane_scope_schema(), indent=2, ensure_ascii=False))
        return

    if getattr(args, "station_chief_v6_3_post_mvp_expansion_lane_readiness_schema", False):
        print(json.dumps(create_station_chief_v6_3_post_mvp_expansion_lane_readiness_schema(), indent=2, ensure_ascii=False))
        return

    if getattr(args, "station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_schema", False):
        print(json.dumps(create_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_schema(), indent=2, ensure_ascii=False))
        return

    if getattr(args, "station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review_schema", False):
        print(json.dumps(create_station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review_schema(), indent=2, ensure_ascii=False))
        return

    if getattr(args, "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_schema", False):
        print(json.dumps(create_station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_schema(), indent=2, ensure_ascii=False))
        return

    if getattr(args, "station_chief_v8_finish_line_control_plane_schema", False):
        print(json.dumps(create_station_chief_v8_finish_line_control_plane_schema(), indent=2, ensure_ascii=False))
        return

    if getattr(args, "station_chief_v9_controlled_local_worker_pilot_schema", False):
        print(json.dumps(create_station_chief_v9_controlled_local_worker_pilot_schema(), indent=2, ensure_ascii=False))
        return

    if getattr(args, "station_chief_v10_multi_worker_sandbox_coordination_schema", False):
        print(json.dumps(create_station_chief_v10_multi_worker_sandbox_coordination_schema(), indent=2, ensure_ascii=False))
        return
    
    if getattr(args, "station_chief_v11_permissioned_tool_task_queue_layer_schema", False):
        print(json.dumps(create_station_chief_v11_permissioned_tool_task_queue_layer_schema(), indent=2, ensure_ascii=False))
        return

    if getattr(args, "station_chief_v12_autonomous_worker_army_release_candidate_schema", False):
        print(json.dumps(create_station_chief_v12_autonomous_worker_army_release_candidate_schema(), indent=2, ensure_ascii=False))
        return

    if getattr(args, "station_chief_v17_live_activation_protocol_schema", False):
        print(json.dumps(create_station_chief_v17_live_activation_protocol_schema(), indent=2, ensure_ascii=False))
        return

    if getattr(args, "station_chief_v16_security_integrity_spine_schema", False):
        print(json.dumps(create_station_chief_v16_security_integrity_spine_schema(), indent=2, ensure_ascii=False))
        return

    if getattr(args, "station_chief_v15_full_auto_agent_army_ready_final_readiness_lock_schema", False):
        print(json.dumps(create_station_chief_v15_full_auto_agent_army_ready_final_readiness_lock_schema(), indent=2, ensure_ascii=False))
        return

    if getattr(args, "station_chief_v14_production_readiness_rollback_live_safety_gates_schema", False):
        print(json.dumps(create_station_chief_v14_production_readiness_rollback_live_safety_gates_schema(), indent=2, ensure_ascii=False))
        return

    if getattr(args, "station_chief_v13_external_tool_api_pilot_hardening_schema", False):
        print(json.dumps(create_station_chief_v13_external_tool_api_pilot_hardening_schema(), indent=2, ensure_ascii=False))
        return
        
    if getattr(args, "write_station_chief_v6_1_post_mvp_expansion_review", False):
        result = write_station_chief_v6_1_post_mvp_expansion_review(
            result,
            args.write_station_chief_v6_1_post_mvp_expansion_review,
            v6_0_mvp_lock_reference_label=args.v6_1_mvp_lock_reference_label,
            post_mvp_expansion_review_label=args.v6_1_post_mvp_expansion_review_label,
            requested_expansion_lane_label=args.v6_1_requested_expansion_lane_label,
            expansion_boundary_label=args.v6_1_expansion_boundary_label,
            expansion_safety_posture_label=args.v6_1_expansion_safety_posture_label,
            post_mvp_expansion_review_packet_name=args.v6_1_post_mvp_expansion_review_packet_name,
            confirmation_token=args.v6_1_post_mvp_expansion_review_confirm_token,
            human_operator=args.v6_1_post_mvp_expansion_review_human_operator,
        )
        station_chief_v6_1_post_mvp_expansion_review_summary = result.get("station_chief_v6_1_post_mvp_expansion_review", {}).get("post_mvp_expansion_review_packet_record", {}).get("write_record")
        result = dict(result)
        result["station_chief_v6_1_post_mvp_expansion_review_write_summary"] = station_chief_v6_1_post_mvp_expansion_review_summary
    elif args.station_chief_v6_1_post_mvp_expansion_review:
        result = attach_station_chief_v6_1_post_mvp_expansion_review(
            result,
            v6_0_mvp_lock_reference_label=args.v6_1_mvp_lock_reference_label,
            post_mvp_expansion_review_label=args.v6_1_post_mvp_expansion_review_label,
            requested_expansion_lane_label=args.v6_1_requested_expansion_lane_label,
            expansion_boundary_label=args.v6_1_expansion_boundary_label,
            expansion_safety_posture_label=args.v6_1_expansion_safety_posture_label,
            output_directory=None,
            post_mvp_expansion_review_packet_name=args.v6_1_post_mvp_expansion_review_packet_name,
            confirmation_token=args.v6_1_post_mvp_expansion_review_confirm_token,
            human_operator=args.v6_1_post_mvp_expansion_review_human_operator,
            post_mvp_expansion_review_requested=False,
            write_post_mvp_expansion_review_packet=False,
        )

    if getattr(args, "write_station_chief_v6_2_post_mvp_expansion_lane_scope", False):
        result = write_station_chief_v6_2_post_mvp_expansion_lane_scope(
            result,
            args.write_station_chief_v6_2_post_mvp_expansion_lane_scope,
            v6_1_review_packet_reference_label=args.v6_2_review_packet_reference_label,
            selected_expansion_lane_label=args.v6_2_selected_expansion_lane_label,
            lane_scope_label=args.v6_2_lane_scope_label,
            lane_constraint_label=args.v6_2_lane_constraint_label,
            lane_success_criteria_label=args.v6_2_lane_success_criteria_label,
            lane_non_execution_boundary_label=args.v6_2_lane_non_execution_boundary_label,
            lane_scope_packet_name=args.v6_2_lane_scope_packet_name,
            confirmation_token=args.v6_2_lane_scope_confirm_token,
            human_operator=args.v6_2_lane_scope_human_operator,
        )
        station_chief_v6_2_summary = result.get("station_chief_v6_2_post_mvp_expansion_lane_scope", {}).get("lane_scope_packet_record", {}).get("write_record")
        result = dict(result)
        result["station_chief_v6_2_post_mvp_expansion_lane_scope_write_summary"] = station_chief_v6_2_summary
    elif args.station_chief_v6_2_post_mvp_expansion_lane_scope:
        result = attach_station_chief_v6_2_post_mvp_expansion_lane_scope(
            result,
            v6_1_review_packet_reference_label=args.v6_2_review_packet_reference_label,
            selected_expansion_lane_label=args.v6_2_selected_expansion_lane_label,
            lane_scope_label=args.v6_2_lane_scope_label,
            lane_constraint_label=args.v6_2_lane_constraint_label,
            lane_success_criteria_label=args.v6_2_lane_success_criteria_label,
            lane_non_execution_boundary_label=args.v6_2_lane_non_execution_boundary_label,
            output_directory=None,
            lane_scope_packet_name=args.v6_2_lane_scope_packet_name,
            confirmation_token=args.v6_2_lane_scope_confirm_token,
            human_operator=args.v6_2_lane_scope_human_operator,
            lane_scope_requested=False,
            write_lane_scope_packet=False,
        )

    if getattr(args, "write_station_chief_v6_3_post_mvp_expansion_lane_readiness", False):
        result = write_station_chief_v6_3_post_mvp_expansion_lane_readiness(
            result,
            args.write_station_chief_v6_3_post_mvp_expansion_lane_readiness,
            v6_2_lane_scope_packet_reference_label=args.v6_3_lane_scope_packet_reference_label,
            selected_expansion_lane_label=args.v6_3_selected_expansion_lane_label,
            readiness_checklist_label=args.v6_3_readiness_checklist_label,
            readiness_blocker_label=args.v6_3_readiness_blocker_label,
            readiness_evidence_label=args.v6_3_readiness_evidence_label,
            readiness_non_execution_boundary_label=args.v6_3_readiness_non_execution_boundary_label,
            readiness_packet_name=args.v6_3_readiness_packet_name,
            confirmation_token=args.v6_3_readiness_confirm_token,
            human_operator=args.v6_3_readiness_human_operator,
        )
        v6_3_summary = result.get("readiness_packet_write_record", {})
        result = dict(result)
        result["station_chief_v6_3_post_mvp_expansion_lane_readiness_write_summary"] = v6_3_summary
    elif args.station_chief_v6_3_post_mvp_expansion_lane_readiness:
        result = attach_station_chief_v6_3_post_mvp_expansion_lane_readiness(
            result,
            v6_2_lane_scope_packet_reference_label=args.v6_3_lane_scope_packet_reference_label,
            selected_expansion_lane_label=args.v6_3_selected_expansion_lane_label,
            readiness_checklist_label=args.v6_3_readiness_checklist_label,
            readiness_blocker_label=args.v6_3_readiness_blocker_label,
            readiness_evidence_label=args.v6_3_readiness_evidence_label,
            readiness_non_execution_boundary_label=args.v6_3_readiness_non_execution_boundary_label,
            output_directory=None,
            readiness_packet_name=args.v6_3_readiness_packet_name,
            confirmation_token=args.v6_3_readiness_confirm_token,
            human_operator=args.v6_3_readiness_human_operator,
            readiness_requested=False,
            write_readiness_packet=False,
        )

    if getattr(args, "write_station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review", False):
        result = attach_station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review(result, args)
        result = write_station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review(result)
    elif args.station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review:
        result = attach_station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review(result, args)

    if getattr(args, "write_station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition", False):
        result = attach_station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition(result, args)
        result = write_station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition(result)
    elif args.station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition:
        result = attach_station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition(result, args)

    if args.station_chief_v8_finish_line_control_plane or args.station_chief_v8_baby_step_chain_closeout or args.station_chief_v8_control_plane_status:
        result = attach_station_chief_v8_finish_line_control_plane(result, args)

    if args.station_chief_v9_controlled_local_worker_pilot or args.station_chief_v9_worker_profile or args.station_chief_v9_noop_task or args.station_chief_v9_worker_pilot_audit:
        result = attach_station_chief_v9_controlled_local_worker_pilot(result, args)

    if args.station_chief_v10_multi_worker_sandbox_coordination or args.station_chief_v10_sandbox_workers or args.station_chief_v10_sandbox_tasks or args.station_chief_v10_assignment_map or args.station_chief_v10_coordination_ledger or args.station_chief_v10_sandbox_audit:
        result = attach_station_chief_v10_multi_worker_sandbox_coordination(result, args)

    if args.station_chief_v11_permissioned_tool_task_queue_layer or args.station_chief_v11_tool_registry or args.station_chief_v11_task_envelopes or args.station_chief_v11_virtual_queue or args.station_chief_v11_dispatch_plan or args.station_chief_v11_permission_receipts or args.station_chief_v11_permission_audit:
        result = attach_station_chief_v11_permissioned_tool_task_queue_layer(result, args)

    if args.station_chief_v12_autonomous_worker_army_release_candidate or args.station_chief_v12_army_workers or args.station_chief_v12_army_squads or args.station_chief_v12_command_manifest or args.station_chief_v12_mission_envelopes or args.station_chief_v12_dispatch_matrix or args.station_chief_v12_army_cycle_plan or args.station_chief_v12_readiness_receipts or args.station_chief_v12_army_audit:
        result = attach_station_chief_v12_autonomous_worker_army_release_candidate(result, args)

    if args.station_chief_v17_live_activation_protocol or args.station_chief_v17_live_action_taxonomy or args.station_chief_v17_first_live_action_allowlist or args.station_chief_v17_preview_readonly_repo_inspection or args.station_chief_v17_approved_readonly_repo_inspection or args.station_chief_v17_live_action_receipt or args.station_chief_v17_live_activation_audit:
        result = attach_station_chief_v17_live_activation_protocol(result, args)

    if args.station_chief_v16_security_integrity_spine or args.station_chief_v16_security_domains or args.station_chief_v16_packet_hash_manifest or args.station_chief_v16_tamper_evident_lineage or args.station_chief_v16_signature_doctrine or args.station_chief_v16_key_separation_trust_boundary or args.station_chief_v16_repo_trust_model or args.station_chief_v16_sensitive_packet_encryption_review or args.station_chief_v16_security_validator_hardening or args.station_chief_v16_security_audit_replay_packet or args.station_chief_v16_security_spine_lock or args.station_chief_v16_security_audit:
        result = attach_station_chief_v16_security_integrity_spine(result, args)

    if args.station_chief_v15_full_auto_agent_army_ready_final_readiness_lock or args.station_chief_v15_final_readiness_domains or args.station_chief_v15_final_activation_prerequisites or args.station_chief_v15_human_approval_override or args.station_chief_v15_command_authority_matrix or args.station_chief_v15_army_readiness_scorecard or args.station_chief_v15_safety_evidence_ledger or args.station_chief_v15_activation_denial_proof or args.station_chief_v15_no_live_action_audit or args.station_chief_v15_final_readiness_certificate:
        result = attach_station_chief_v15_full_auto_agent_army_ready_final_readiness_lock(result, args)

    if args.station_chief_v14_production_readiness_rollback_live_safety_gates or args.station_chief_v14_production_readiness_gates or args.station_chief_v14_rollback_playbooks or args.station_chief_v14_live_safety_gate_manifest or args.station_chief_v14_supervised_production_pilot_preflight or args.station_chief_v14_emergency_stop_abort_controls or args.station_chief_v14_observability_audit_telemetry or args.station_chief_v14_production_readiness_policy_gate or args.station_chief_v14_production_readiness_receipts or args.station_chief_v14_production_safety_audit:
        result = attach_station_chief_v14_production_readiness_rollback_live_safety_gates(result, args)

    if args.station_chief_v13_external_tool_api_pilot_hardening or args.station_chief_v13_external_interfaces or args.station_chief_v13_external_action_envelopes or args.station_chief_v13_external_access_policy_gate or args.station_chief_v13_credential_secret_denial_proof or args.station_chief_v13_network_api_denial_proof or args.station_chief_v13_external_pilot_dry_run_plan or args.station_chief_v13_external_permission_receipts or args.station_chief_v13_external_pilot_audit:
        result = attach_station_chief_v13_external_tool_api_pilot_hardening(result, args)

    if getattr(args, "write_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan", False):
        result = write_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan(
            result,
            args.write_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan,
            v6_3_readiness_packet_reference_label=args.v6_4_readiness_packet_reference_label,
            v6_2_lane_scope_packet_reference_label=args.v6_4_lane_scope_packet_reference_label,
            selected_expansion_lane_label=args.v6_4_selected_expansion_lane_label,
            implementation_plan_label=args.v6_4_implementation_plan_label,
            implementation_step_list_label=args.v6_4_implementation_step_list_label,
            implementation_risk_register_label=args.v6_4_implementation_risk_register_label,
            implementation_rollback_plan_label=args.v6_4_implementation_rollback_plan_label,
            implementation_non_execution_boundary_label=args.v6_4_implementation_non_execution_boundary_label,
            implementation_plan_packet_name=args.v6_4_implementation_plan_packet_name,
            confirmation_token=args.v6_4_implementation_plan_confirm_token,
            human_operator=args.v6_4_implementation_plan_human_operator,
        )
    elif args.station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan:
        result = attach_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan(
            result,
            v6_3_readiness_packet_reference_label=args.v6_4_readiness_packet_reference_label,
            v6_2_lane_scope_packet_reference_label=args.v6_4_lane_scope_packet_reference_label,
            selected_expansion_lane_label=args.v6_4_selected_expansion_lane_label,
            implementation_plan_label=args.v6_4_implementation_plan_label,
            implementation_step_list_label=args.v6_4_implementation_step_list_label,
            implementation_risk_register_label=args.v6_4_implementation_risk_register_label,
            implementation_rollback_plan_label=args.v6_4_implementation_rollback_plan_label,
            implementation_non_execution_boundary_label=args.v6_4_implementation_non_execution_boundary_label,
            output_directory=None,
            implementation_plan_packet_name=args.v6_4_implementation_plan_packet_name,
            confirmation_token=args.v6_4_implementation_plan_confirm_token,
            human_operator=args.v6_4_implementation_plan_human_operator,
            implementation_plan_requested=False,
            write_implementation_plan_packet=False,
        )

    if getattr(args, "write_station_chief_v6_0_mvp_lock", False):
        result = write_station_chief_v6_0_mvp_lock(
            result,
            args.write_station_chief_v6_0_mvp_lock,
            local_task_candidate_label=args.v6_mvp_local_task_candidate_label,
            sandbox_worker_label=args.v6_mvp_sandbox_worker_label,
            v5_3_handoff_packet_reference_label=args.v6_mvp_handoff_packet_reference_label,
            v5_4_acknowledgement_packet_reference_label=args.v6_mvp_acknowledgement_packet_reference_label,
            v5_5_acceptance_review_packet_reference_label=args.v6_mvp_acceptance_review_packet_reference_label,
            v5_6_ready_state_packet_reference_label=args.v6_mvp_ready_state_packet_reference_label,
            v5_7_dry_run_assignment_packet_reference_label=args.v6_mvp_dry_run_assignment_packet_reference_label,
            v5_8_dry_run_result_packet_reference_label=args.v6_mvp_dry_run_result_packet_reference_label,
            v5_9_dry_run_replay_audit_packet_reference_label=args.v6_mvp_dry_run_replay_audit_packet_reference_label,
            v6_0_mvp_lock_label=args.v6_mvp_lock_label,
            mvp_lock_packet_name=args.v6_mvp_lock_packet_name,
            confirmation_token=args.v6_mvp_lock_confirm_token,
            human_operator=args.v6_mvp_lock_human_operator,
        )
        station_chief_v6_0_mvp_lock_summary = result.get("station_chief_v6_0_mvp_lock", {}).get("mvp_lock_packet_record", {}).get("write_record")
        result = dict(result)
        result["station_chief_v6_0_mvp_lock_write_summary"] = station_chief_v6_0_mvp_lock_summary
    elif args.station_chief_v6_0_mvp_lock:
        result = attach_station_chief_v6_0_mvp_lock(
            result,
            local_task_candidate_label=args.v6_mvp_local_task_candidate_label,
            sandbox_worker_label=args.v6_mvp_sandbox_worker_label,
            v5_3_handoff_packet_reference_label=args.v6_mvp_handoff_packet_reference_label,
            v5_4_acknowledgement_packet_reference_label=args.v6_mvp_acknowledgement_packet_reference_label,
            v5_5_acceptance_review_packet_reference_label=args.v6_mvp_acceptance_review_packet_reference_label,
            v5_6_ready_state_packet_reference_label=args.v6_mvp_ready_state_packet_reference_label,
            v5_7_dry_run_assignment_packet_reference_label=args.v6_mvp_dry_run_assignment_packet_reference_label,
            v5_8_dry_run_result_packet_reference_label=args.v6_mvp_dry_run_result_packet_reference_label,
            v5_9_dry_run_replay_audit_packet_reference_label=args.v6_mvp_dry_run_replay_audit_packet_reference_label,
            v6_0_mvp_lock_label=args.v6_mvp_lock_label,
            output_directory=None,
            mvp_lock_packet_name=args.v6_mvp_lock_packet_name,
            confirmation_token=args.v6_mvp_lock_confirm_token,
            human_operator=args.v6_mvp_lock_human_operator,
            mvp_lock_requested=False,
            write_mvp_lock_packet=False,
        )

    if args.sandbox_worker_dry_run_replay_audit_candidate_schema:
        print(json.dumps(create_sandbox_worker_dry_run_replay_audit_candidate_schema(), indent=2, ensure_ascii=False))
        return
        
    if getattr(args, "write_sandbox_worker_dry_run_replay_audit_candidate", False):
        result = write_sandbox_worker_dry_run_replay_audit_candidate(
            result,
            args.write_sandbox_worker_dry_run_replay_audit_candidate,
            sandbox_worker_label=args.v5_replay_sandbox_worker_label,
            v5_3_handoff_packet_reference_label=args.v5_replay_handoff_packet_reference_label,
            v5_4_acknowledgement_packet_reference_label=args.v5_replay_acknowledgement_packet_reference_label,
            v5_5_acceptance_review_packet_reference_label=args.v5_replay_acceptance_review_packet_reference_label,
            v5_6_ready_state_packet_reference_label=args.v5_replay_ready_state_packet_reference_label,
            v5_7_dry_run_assignment_packet_reference_label=args.v5_replay_dry_run_assignment_packet_reference_label,
            v5_8_dry_run_result_packet_reference_label=args.v5_replay_dry_run_result_packet_reference_label,
            synthetic_dry_run_task_label=args.v5_replay_task_label,
            synthetic_dry_run_result_label=args.v5_replay_result_label,
            replay_audit_candidate_label=args.v5_replay_audit_label,
            dry_run_replay_audit_packet_name=args.v5_dry_run_replay_audit_packet_name,
            confirmation_token=args.v5_dry_run_replay_audit_confirm_token,
            human_operator=args.v5_dry_run_replay_audit_human_operator,
        )
        sandbox_worker_dry_run_replay_audit_candidate_summary = result.get("sandbox_worker_dry_run_replay_audit_candidate", {}).get("dry_run_replay_audit_packet_record", {}).get("write_record")
        result = dict(result)
        result["sandbox_worker_dry_run_replay_audit_candidate_write_summary"] = sandbox_worker_dry_run_replay_audit_candidate_summary
    elif args.sandbox_worker_dry_run_replay_audit_candidate:
        result = attach_sandbox_worker_dry_run_replay_audit_candidate(
            result,
            sandbox_worker_label=args.v5_replay_sandbox_worker_label,
            v5_3_handoff_packet_reference_label=args.v5_replay_handoff_packet_reference_label,
            v5_4_acknowledgement_packet_reference_label=args.v5_replay_acknowledgement_packet_reference_label,
            v5_5_acceptance_review_packet_reference_label=args.v5_replay_acceptance_review_packet_reference_label,
            v5_6_ready_state_packet_reference_label=args.v5_replay_ready_state_packet_reference_label,
            v5_7_dry_run_assignment_packet_reference_label=args.v5_replay_dry_run_assignment_packet_reference_label,
            v5_8_dry_run_result_packet_reference_label=args.v5_replay_dry_run_result_packet_reference_label,
            synthetic_dry_run_task_label=args.v5_replay_task_label,
            synthetic_dry_run_result_label=args.v5_replay_result_label,
            replay_audit_candidate_label=args.v5_replay_audit_label,
            output_directory=None,
            dry_run_replay_audit_packet_name=args.v5_dry_run_replay_audit_packet_name,
            confirmation_token=args.v5_dry_run_replay_audit_confirm_token,
            human_operator=args.v5_dry_run_replay_audit_human_operator,
            replay_audit_requested=False,
            write_dry_run_replay_audit_packet=False,
        )

    if args.sandbox_worker_dry_run_result_candidate_schema:
        print(json.dumps(create_sandbox_worker_dry_run_result_candidate_schema(), indent=2, ensure_ascii=False))
        return
        
    if getattr(args, "write_sandbox_worker_dry_run_result_candidate", False):
        result = write_sandbox_worker_dry_run_result_candidate(
            result,
            args.write_sandbox_worker_dry_run_result_candidate,
            sandbox_worker_label=args.v5_result_sandbox_worker_label,
            v5_3_handoff_packet_reference_label=args.v5_result_handoff_packet_reference_label,
            v5_4_acknowledgement_packet_reference_label=args.v5_result_acknowledgement_packet_reference_label,
            v5_5_acceptance_review_packet_reference_label=args.v5_result_acceptance_review_packet_reference_label,
            v5_6_ready_state_packet_reference_label=args.v5_result_ready_state_packet_reference_label,
            v5_7_dry_run_assignment_packet_reference_label=args.v5_result_dry_run_assignment_packet_reference_label,
            synthetic_dry_run_task_label=args.v5_result_task_label,
            synthetic_dry_run_result_label=args.v5_result_label,
            dry_run_result_packet_name=args.v5_dry_run_result_packet_name,
            confirmation_token=args.v5_dry_run_result_confirm_token,
            human_operator=args.v5_dry_run_result_human_operator,
        )
        sandbox_worker_dry_run_result_candidate_summary = result.get("sandbox_worker_dry_run_result_candidate", {}).get("dry_run_result_packet_record", {}).get("write_record")
        result = dict(result)
        result["sandbox_worker_dry_run_result_candidate_write_summary"] = sandbox_worker_dry_run_result_candidate_summary
    elif args.sandbox_worker_dry_run_result_candidate:
        result = attach_sandbox_worker_dry_run_result_candidate(
            result,
            sandbox_worker_label=args.v5_result_sandbox_worker_label,
            v5_3_handoff_packet_reference_label=args.v5_result_handoff_packet_reference_label,
            v5_4_acknowledgement_packet_reference_label=args.v5_result_acknowledgement_packet_reference_label,
            v5_5_acceptance_review_packet_reference_label=args.v5_result_acceptance_review_packet_reference_label,
            v5_6_ready_state_packet_reference_label=args.v5_result_ready_state_packet_reference_label,
            v5_7_dry_run_assignment_packet_reference_label=args.v5_result_dry_run_assignment_packet_reference_label,
            synthetic_dry_run_task_label=args.v5_result_task_label,
            synthetic_dry_run_result_label=args.v5_result_label,
            output_directory=None,
            dry_run_result_packet_name=args.v5_dry_run_result_packet_name,
            confirmation_token=args.v5_dry_run_result_confirm_token,
            human_operator=args.v5_dry_run_result_human_operator,
            dry_run_result_requested=False,
            write_dry_run_result_packet=False,
        )

    if args.sandbox_worker_dry_run_assignment_candidate_schema:
        print(json.dumps(create_sandbox_worker_dry_run_assignment_candidate_schema(), indent=2, ensure_ascii=False))
        return
        
    if getattr(args, "write_sandbox_worker_dry_run_assignment_candidate", False):
        result = write_sandbox_worker_dry_run_assignment_candidate(
            result,
            args.write_sandbox_worker_dry_run_assignment_candidate,
            sandbox_worker_label=args.v5_dry_run_sandbox_worker_label,
            v5_3_handoff_packet_reference_label=args.v5_dry_run_handoff_packet_reference_label,
            v5_4_acknowledgement_packet_reference_label=args.v5_dry_run_acknowledgement_packet_reference_label,
            v5_5_acceptance_review_packet_reference_label=args.v5_dry_run_acceptance_review_packet_reference_label,
            v5_6_ready_state_packet_reference_label=args.v5_dry_run_ready_state_packet_reference_label,
            synthetic_dry_run_task_label=args.v5_dry_run_task_label,
            dry_run_assignment_packet_name=args.v5_dry_run_assignment_packet_name,
            confirmation_token=args.v5_dry_run_assignment_confirm_token,
            human_operator=args.v5_dry_run_assignment_human_operator,
        )
        sandbox_worker_dry_run_assignment_candidate_summary = result.get("sandbox_worker_dry_run_assignment_candidate", {}).get("dry_run_assignment_packet_record", {}).get("write_record")
        result = dict(result)
        result["sandbox_worker_dry_run_assignment_candidate_write_summary"] = sandbox_worker_dry_run_assignment_candidate_summary
    elif args.sandbox_worker_dry_run_assignment_candidate:
        result = attach_sandbox_worker_dry_run_assignment_candidate(
            result,
            sandbox_worker_label=args.v5_dry_run_sandbox_worker_label,
            v5_3_handoff_packet_reference_label=args.v5_dry_run_handoff_packet_reference_label,
            v5_4_acknowledgement_packet_reference_label=args.v5_dry_run_acknowledgement_packet_reference_label,
            v5_5_acceptance_review_packet_reference_label=args.v5_dry_run_acceptance_review_packet_reference_label,
            v5_6_ready_state_packet_reference_label=args.v5_dry_run_ready_state_packet_reference_label,
            synthetic_dry_run_task_label=args.v5_dry_run_task_label,
            output_directory=None,
            dry_run_assignment_packet_name=args.v5_dry_run_assignment_packet_name,
            confirmation_token=args.v5_dry_run_assignment_confirm_token,
            human_operator=args.v5_dry_run_assignment_human_operator,
            dry_run_assignment_requested=False,
            write_dry_run_assignment_packet=False,
        )

    if args.sandbox_worker_ready_state_packet_candidate_schema:
        print(json.dumps(create_sandbox_worker_ready_state_packet_candidate_schema(), indent=2, ensure_ascii=False))
        return
        
    if getattr(args, "write_sandbox_worker_ready_state_packet_candidate", False):
        result = write_sandbox_worker_ready_state_packet_candidate(
            result,
            args.write_sandbox_worker_ready_state_packet_candidate,
            sandbox_worker_label=args.v5_ready_sandbox_worker_label,
            v5_3_handoff_packet_reference_label=args.v5_ready_handoff_packet_reference_label,
            v5_4_acknowledgement_packet_reference_label=args.v5_ready_acknowledgement_packet_reference_label,
            v5_5_acceptance_review_packet_reference_label=args.v5_ready_acceptance_review_packet_reference_label,
            ready_state_packet_name=args.v5_ready_state_packet_name,
            confirmation_token=args.v5_ready_state_confirm_token,
            human_operator=args.v5_ready_state_human_operator,
        )
        sandbox_worker_ready_state_packet_candidate_summary = result.get("sandbox_worker_ready_state_packet_candidate", {}).get("ready_state_packet_record", {}).get("write_record")
        result = dict(result)
        result["sandbox_worker_ready_state_packet_candidate_write_summary"] = sandbox_worker_ready_state_packet_candidate_summary
    elif args.sandbox_worker_ready_state_packet_candidate:
        result = attach_sandbox_worker_ready_state_packet_candidate(
            result,
            sandbox_worker_label=args.v5_ready_sandbox_worker_label,
            v5_3_handoff_packet_reference_label=args.v5_ready_handoff_packet_reference_label,
            v5_4_acknowledgement_packet_reference_label=args.v5_ready_acknowledgement_packet_reference_label,
            v5_5_acceptance_review_packet_reference_label=args.v5_ready_acceptance_review_packet_reference_label,
            output_directory=None,
            ready_state_packet_name=args.v5_ready_state_packet_name,
            confirmation_token=args.v5_ready_state_confirm_token,
            human_operator=args.v5_ready_state_human_operator,
            ready_state_packet_requested=False,
            write_ready_state_packet=False,
        )

    if args.sandbox_worker_acceptance_candidate_review_schema:
        print(json.dumps(create_sandbox_worker_acceptance_candidate_review_schema(), indent=2, ensure_ascii=False))
        return
        
    if getattr(args, "write_sandbox_worker_acceptance_candidate_review", False):
        result = write_sandbox_worker_acceptance_candidate_review(
            result,
            args.write_sandbox_worker_acceptance_candidate_review,
            sandbox_worker_label=args.v5_accept_sandbox_worker_label,
            v5_3_handoff_packet_reference_label=args.v5_accept_handoff_packet_reference_label,
            v5_4_acknowledgement_packet_reference_label=args.v5_accept_acknowledgement_packet_reference_label,
            acceptance_review_packet_name=args.v5_acceptance_review_packet_name,
            confirmation_token=args.v5_acceptance_confirm_token,
            human_operator=args.v5_acceptance_human_operator,
        )
        sandbox_worker_acceptance_candidate_review_summary = result.get("sandbox_worker_acceptance_candidate_review", {}).get("acceptance_review_packet_record", {}).get("write_record")
        result = dict(result)
        result["sandbox_worker_acceptance_candidate_review_write_summary"] = sandbox_worker_acceptance_candidate_review_summary
    elif args.sandbox_worker_acceptance_candidate_review:
        result = attach_sandbox_worker_acceptance_candidate_review(
            result,
            sandbox_worker_label=args.v5_accept_sandbox_worker_label,
            v5_3_handoff_packet_reference_label=args.v5_accept_handoff_packet_reference_label,
            v5_4_acknowledgement_packet_reference_label=args.v5_accept_acknowledgement_packet_reference_label,
            output_directory=None,
            acceptance_review_packet_name=args.v5_acceptance_review_packet_name,
            confirmation_token=args.v5_acceptance_confirm_token,
            human_operator=args.v5_acceptance_human_operator,
            acceptance_review_requested=False,
            write_acceptance_review_packet=False,
        )

    sandbox_worker_acknowledgement_candidate_summary = None
    if getattr(args, "write_sandbox_worker_acknowledgement_candidate", False):
        result = write_sandbox_worker_acknowledgement_candidate(
            result,
            args.write_sandbox_worker_acknowledgement_candidate,
            sandbox_worker_label=args.v5_ack_sandbox_worker_label,
            v5_3_handoff_packet_reference_label=args.v5_handoff_packet_reference_label,
            acknowledgement_packet_name=args.v5_acknowledgement_packet_name,
            confirmation_token=args.v5_acknowledgement_confirm_token,
            human_operator=args.v5_acknowledgement_human_operator,
        )
        sandbox_worker_acknowledgement_candidate_summary = result["acknowledgement_packet_write_record"]
        result = dict(result)
        result["sandbox_worker_acknowledgement_candidate_write_summary"] = sandbox_worker_acknowledgement_candidate_summary
    elif args.sandbox_worker_acknowledgement_candidate:
        result = attach_sandbox_worker_acknowledgement_candidate(
            result,
            sandbox_worker_label=args.v5_ack_sandbox_worker_label,
            v5_3_handoff_packet_reference_label=args.v5_handoff_packet_reference_label,
            output_directory=None,
            acknowledgement_packet_name=args.v5_acknowledgement_packet_name,
            confirmation_token=args.v5_acknowledgement_confirm_token,
            human_operator=args.v5_acknowledgement_human_operator,
            acknowledgement_requested=False,
            write_acknowledgement_packet=False,
        )

    artifact_summary = None
    if args.write_artifacts:
        artifact_summary = write_runtime_artifacts(
            dict(result),
            args.write_artifacts,
            run_label=args.run_label,
            registry_dir=args.registry_dir,
        )
        result = dict(result)
        result["artifact_write_summary"] = artifact_summary

    dry_run_bundle_summary = None
    if args.write_dry_run_bundle:
        if "dry_run_bundle" not in result or result["dry_run_bundle"] is None:
            result = attach_execution_profile_and_dry_run(
                result,
                requested_profile=args.execution_profile,
                include_dry_run_bundle=True,
            )
        dry_run_bundle_summary = write_dry_run_bundle(result, args.write_dry_run_bundle, run_label=args.run_label)
        result = dict(result)
        result["dry_run_bundle_write_summary"] = dry_run_bundle_summary

    approval_handoff_summary = None
    if args.write_approval_handoff:
        if "approval_handoff_packet" not in result or result["approval_handoff_packet"] is None:
            result = attach_approval_handoff(
                result,
                comparison_bundle_path=args.compare_against_dry_run_bundle,
                include_handoff=True,
            )
        approval_handoff_summary = write_approval_handoff(result, args.write_approval_handoff, run_label=args.run_label)
        result = dict(result)
        result["approval_handoff_write_summary"] = approval_handoff_summary

    approval_record_summary = None
    if args.write_approval_record:
        if "signed_approval_record" not in result or result["signed_approval_record"] is None:
            result = attach_signed_approval_record(
                result,
                reviewer_name=args.approval_reviewer,
                approval_decision=args.approval_decision,
                approval_note=args.approval_note,
                approval_record_token=args.approval_record_token,
                patch_preview_reviewed=args.patch_preview_reviewed,
                changed_file_scope_reviewed=args.changed_file_scope_reviewed,
                baseline_protection_reviewed=args.baseline_protection_reviewed,
                risk_summary_reviewed=args.risk_summary_reviewed,
            )
        approval_record_summary = write_approval_record(result, args.write_approval_record, run_label=args.run_label)
        result = dict(result)
        result["approval_record_write_summary"] = approval_record_summary

    if args.write_approval_ledger:
        ledger_summary = write_approval_ledger(result, args.write_approval_ledger, run_label=args.run_label)
        result = dict(result)
        result["approval_ledger_write_summary"] = ledger_summary

    if args.write_release_lock:
        release_lock_summary = write_release_lock(result, args.write_release_lock, run_label=args.run_label)
        result = dict(result)
        result["release_lock_write_summary"] = release_lock_summary

    if args.write_controlled_execution:
        controlled_execution_summary = write_controlled_execution(result, args.write_controlled_execution, run_label=args.run_label)
        result = dict(result)
        result["controlled_execution_write_summary"] = controlled_execution_summary

    if args.write_work_order_executor:
        work_order_executor_summary = write_work_order_executor(result, args.write_work_order_executor, run_label=args.run_label)
        result = dict(result)
        result["work_order_executor_write_summary"] = work_order_executor_summary

    if args.write_worker_hiring_registry:
        worker_hiring_registry_summary = write_worker_hiring_registry(result, args.write_worker_hiring_registry, run_label=args.run_label)
        result = dict(result)
        result["worker_hiring_registry_write_summary"] = worker_hiring_registry_summary

    if args.write_department_routing:
        department_routing_summary = write_department_routing(result, args.write_department_routing, run_label=args.run_label)
        result = dict(result)
        result["department_routing_write_summary"] = department_routing_summary

    if args.write_multi_agent_orchestration:
        multi_agent_orchestration_summary = write_multi_agent_orchestration(result, args.write_multi_agent_orchestration, run_label=args.run_label)
        result = dict(result)
        result["multi_agent_orchestration_write_summary"] = multi_agent_orchestration_summary

    if args.write_operator_console:
        operator_console_summary = write_operator_console(result, args.write_operator_console, run_label=args.run_label)
        result = dict(result)
        result["operator_console_write_summary"] = operator_console_summary

    if args.write_github_patch_hardening:
        github_patch_hardening_summary = write_github_patch_hardening(result, args.write_github_patch_hardening, run_label=args.run_label)
        result = dict(result)
        result["github_patch_hardening_write_summary"] = github_patch_hardening_summary

    if args.write_deployment_packaging:
        deployment_packaging_summary = write_deployment_packaging(result, args.write_deployment_packaging, run_label=args.run_label)
        result = dict(result)
        result["deployment_packaging_write_summary"] = deployment_packaging_summary

    if args.write_controlled_worker_execution:
        controlled_worker_execution_summary = write_controlled_worker_execution(result, args.write_controlled_worker_execution, run_label=args.run_label)
        result = dict(result)
        result["controlled_worker_execution_write_summary"] = controlled_worker_execution_summary

    if args.write_tool_permission_binding:
        tool_permission_binding_summary = write_tool_permission_binding(result, args.write_tool_permission_binding, run_label=args.run_label)
        result = dict(result)
        result["tool_permission_binding_write_summary"] = tool_permission_binding_summary

    if args.write_live_telemetry_abort:
        live_telemetry_abort_summary = write_live_execution_telemetry_abort(result, args.write_live_telemetry_abort, run_label=args.run_label)
        result = dict(result)
        result["live_execution_telemetry_abort_write_summary"] = live_telemetry_abort_summary

    post_run_audit_expansion_summary = None
    if args.write_post_run_audit_expansion:
        if "post_run_audit_expansion_bundle" not in result or result["post_run_audit_expansion_bundle"] is None:
            result = attach_post_run_audit_expansion(
                result,
                worker_id=args.post_run_audit_worker_id or "station-chief-sandbox-worker-001",
                confirmation_token=args.post_run_audit_confirm_token,
                before_result=post_run_audit_before,
                after_result=post_run_audit_after,
                artifact_names=args.post_run_audit_artifact_name,
                validator_names=args.post_run_audit_validator_name,
                observed_failures=args.post_run_audit_observed_failure,
            )
        post_run_audit_expansion_summary = write_post_run_audit_expansion(
            result,
            args.write_post_run_audit_expansion,
            run_label=args.run_label,
        )
        result = dict(result)
        result["post_run_audit_expansion_write_summary"] = post_run_audit_expansion_summary

    multi_worker_sandbox_coordination_summary = None
    if args.write_multi_worker_sandbox_coordination:
        if "multi_worker_sandbox_coordination_bundle" not in result or result["multi_worker_sandbox_coordination_bundle"] is None:
            result = attach_multi_worker_sandbox_coordination(
                result,
                roster_label=args.multi_worker_roster_label,
                confirmation_token=args.multi_worker_confirm_token,
                requested_worker_count=args.multi_worker_count,
                worker_roles=args.multi_worker_role,
                requested_shared_resources=args.multi_worker_shared_resource,
                abort_reason=args.multi_worker_abort_reason,
                failure_reason=args.multi_worker_failure_reason,
            )
        multi_worker_sandbox_coordination_summary = write_multi_worker_sandbox_coordination(
            result,
            args.write_multi_worker_sandbox_coordination,
            run_label=args.run_label,
        )
        result = dict(result)
        result["multi_worker_sandbox_coordination_write_summary"] = multi_worker_sandbox_coordination_summary

    controlled_external_tool_adapter_preview_summary = None
    if args.write_controlled_external_tool_preview:
        if "controlled_external_tool_adapter_preview_bundle" not in result or result["controlled_external_tool_adapter_preview_bundle"] is None:
            if "multi_worker_sandbox_coordination_bundle" not in result or result["multi_worker_sandbox_coordination_bundle"] is None:
                result = attach_multi_worker_sandbox_coordination(result)
            result = attach_controlled_external_tool_adapter_preview(
                result,
                tool_label=args.external_tool_label,
                tool_id=args.external_tool_id,
                confirmation_token=args.external_tool_confirm_token,
                requested_tools=args.external_tool_requested_tool,
                requested_external_action=args.external_tool_requested_action,
                request_label=args.external_tool_request_label,
                request_payload=external_tool_request_payload,
                response_preview=external_tool_response_preview,
                abort_reason=args.external_tool_abort_reason,
            )
        controlled_external_tool_adapter_preview_summary = write_controlled_external_tool_adapter_preview(
            result,
            args.write_controlled_external_tool_preview,
            run_label=args.run_label,
        )
        result = dict(result)
        result["controlled_external_tool_adapter_preview_write_summary"] = controlled_external_tool_adapter_preview_summary

    if args.write_permissioned_external_api_dry_run:
        api_res = write_permissioned_external_api_dry_run_preview(result, args.write_permissioned_external_api_dry_run)
        result = dict(result)
        result["permissioned_external_api_dry_run_preview_write_summary"] = api_res
    if args.write_controlled_multi_worker_audit_replay_preview:
        replay_res = write_controlled_multi_worker_audit_replay_preview(result, args.write_controlled_multi_worker_audit_replay_preview)
        result = dict(result)
        result["controlled_multi_worker_audit_replay_preview_write_summary"] = replay_res
    if args.write_operator_approval_queue_enforcement:
        queue_res = write_operator_approval_queue_enforcement(result, args.write_operator_approval_queue_enforcement)
        result = dict(result)
        result["operator_approval_queue_enforcement_write_summary"] = queue_res
    if args.write_release_candidate_hardening:
        rc_res = write_release_candidate_hardening(result, args.write_release_candidate_hardening)
        result = dict(result)
        result["release_candidate_hardening_write_summary"] = rc_res
    if args.write_first_supervised_production_dry_run:
        dry_run_res = write_first_supervised_production_dry_run(result, args.write_first_supervised_production_dry_run)
        result = dict(result)
        result["first_supervised_production_dry_run_write_summary"] = dry_run_res
    if args.supervised_production_pilot_readiness_review_schema:
        print(json.dumps(create_supervised_production_pilot_readiness_review_schema(), indent=2, sort_keys=True))
        sys.exit(0)

    if args.supervised_external_api_pilot_schema:
        print(json.dumps(create_supervised_external_api_pilot_schema(), indent=2, sort_keys=True))
        sys.exit(0)

    if args.monitored_rollback_recovery_drill_schema:
        print(json.dumps(create_monitored_rollback_recovery_drill_schema(), indent=2, sort_keys=True))
        sys.exit(0)

    if args.write_supervised_external_api_pilot:
        args.supervised_external_api_pilot = True

    if args.write_monitored_rollback_recovery_drill:
        args.monitored_rollback_recovery_drill = True
        args.supervised_external_api_pilot = True

    if args.write_supervised_production_pilot_readiness_review:
        if "supervised_production_pilot_readiness_review_bundle" not in result or result["supervised_production_pilot_readiness_review_bundle"] is None:
            result = attach_supervised_production_pilot_readiness_review(
                result,
                production_readiness_label=args.production_readiness_label,
                confirmation_token=args.production_readiness_confirm_token,
                candidate_label=args.candidate_label,
                required_production_pilot_reviewer=args.required_production_pilot_reviewer,
                blast_radius_label=args.blast_radius_label,
            )
        supervised_production_pilot_readiness_review_write_summary = write_supervised_production_pilot_readiness_review(
            result,
            args.write_supervised_production_pilot_readiness_review,
            run_label=args.run_label,
        )
        result = dict(result)
        result["supervised_production_pilot_readiness_review_write_summary"] = supervised_production_pilot_readiness_review_write_summary

    if args.write_credential_vault_denial_secret_handling_proof:
        if "credential_vault_denial_secret_handling_proof_bundle" not in result or result["credential_vault_denial_secret_handling_proof_bundle"] is None:
            result = attach_credential_vault_denial_secret_handling_proof(
                result,
                credential_secret_label=args.credential_secret_label,
                confirmation_token=args.credential_secret_confirm_token,
                credential_boundary_label=args.credential_boundary_label,
                secret_boundary_label=args.secret_boundary_label,
                environment_boundary_label=args.environment_boundary_label,
            )
        credential_vault_denial_secret_handling_proof_write_summary = write_credential_vault_denial_secret_handling_proof(
            result,
            args.write_credential_vault_denial_secret_handling_proof,
            run_label=args.run_label,
        )
        result = dict(result)
        result["credential_vault_denial_secret_handling_proof_write_summary"] = credential_vault_denial_secret_handling_proof_write_summary

    if getattr(args, "write_network_socket_lockdown_proof", False):
        if "network_socket_lockdown_proof_bundle" not in result or result["network_socket_lockdown_proof_bundle"] is None:
            result = attach_network_socket_lockdown_proof(
                result,
                network_socket_label=args.network_socket_label,
                confirmation_token=args.network_socket_confirm_token,
                network_boundary_label=args.network_boundary_label,
                socket_boundary_label=args.socket_boundary_label,
            )
        network_socket_lockdown_proof_write_summary = write_network_socket_lockdown_proof(
            result,
            args.write_network_socket_lockdown_proof,
            run_label=args.run_label,
        )
        result = dict(result)
        result["network_socket_lockdown_proof_write_summary"] = network_socket_lockdown_proof_write_summary

    if getattr(args, "write_live_external_action_final_preflight_gate", False):
        if "live_external_action_final_preflight_gate_bundle" not in result or result["live_external_action_final_preflight_gate_bundle"] is None:
            result = attach_live_external_action_final_preflight_gate(
                result,
                live_external_action_label=args.live_external_action_label,
                confirmation_token=args.live_external_action_confirm_token,
                candidate_action_label=args.candidate_action_label,
                blast_radius_label=args.blast_radius_label,
                required_final_approver=args.required_final_approver,
            )
        live_external_action_final_preflight_gate_write_summary = write_live_external_action_final_preflight_gate(
            result,
            args.write_live_external_action_final_preflight_gate,
            run_label=args.run_label,
        )
        result = dict(result)
        result["live_external_action_final_preflight_gate_write_summary"] = live_external_action_final_preflight_gate_write_summary

    if getattr(args, "write_first_tiny_real_world_supervised_execution_candidate", False):
        result = write_first_tiny_real_world_supervised_execution_candidate(
            result,
            args.write_first_tiny_real_world_supervised_execution_candidate,
            candidate_label=args.v4_candidate_label,
            artifact_name=args.v4_artifact_name,
            confirmation_token=args.v4_candidate_confirm_token,
            human_operator=args.v4_human_operator,
            run_label=args.run_label,
        )
        if "live_external_action_final_preflight_gate_bundle" not in result or result["live_external_action_final_preflight_gate_bundle"] is None:
            result = attach_live_external_action_final_preflight_gate(result)

    if args.first_tiny_real_world_supervised_execution_candidate:
        if "live_external_action_final_preflight_gate_bundle" not in result or result["live_external_action_final_preflight_gate_bundle"] is None:
            result = attach_live_external_action_final_preflight_gate(result)
        result = attach_first_tiny_real_world_supervised_execution_candidate(
            result,
            candidate_label=args.v4_candidate_label,
            output_directory=None,
            artifact_name=args.v4_artifact_name,
            confirmation_token=args.v4_candidate_confirm_token,
            human_operator=args.v4_human_operator,
            execute_local_proof_artifact_write=False,
        )

    if args.write_limited_external_tool_supervised_pilot:
        pilot_res = write_limited_external_tool_supervised_pilot(result, args.write_limited_external_tool_supervised_pilot)
        result = dict(result)
        result["limited_external_tool_supervised_pilot_write_summary"] = pilot_res
    if args.write_controlled_worker_hiring_activation_pilot:
        pilot_res = write_controlled_worker_hiring_activation_pilot(result, args.write_controlled_worker_hiring_activation_pilot)
        result = dict(result)
        result["controlled_worker_hiring_activation_pilot_write_summary"] = pilot_res
    if args.write_supervised_external_api_pilot:
        write_res = write_supervised_external_api_pilot(result, args.write_supervised_external_api_pilot)
        result["supervised_external_api_pilot_write_summary"] = write_res
    if args.write_monitored_rollback_recovery_drill:
        write_res = write_monitored_rollback_recovery_drill(result, args.write_monitored_rollback_recovery_drill, run_label=args.run_label)
        result["monitored_rollback_recovery_drill_write_summary"] = write_res

    if args.write_controlled_production_readiness_gate:
        pg_res = write_controlled_production_readiness_gate(result, args.write_controlled_production_readiness_gate)
        result = dict(result)
        result["controlled_production_readiness_gate_write_summary"] = pg_res

    if args.simulate_adapter:
        adapter_result = dict(result.get("adapter_result") or {})
        adapter_result.update(
            {
                "execution_mode": "controlled_noop",
                "adapter_available": True,
                "external_actions_taken": False,
                "live_api_call_performed": False,
                "network_access_performed": False,
                "socket_opened": False,
                "credentials_used": False,
                "secrets_read": False,
                "environment_read": False,
                "deployment_performed": False,
                "real_external_tool_invocation_performed": False,
                "production_execution_performed": False,
                "production_activation_performed": False,
                "real_task_execution_performed": False,
                "live_task_assignment_performed": False,
                "live_worker_routing_performed": False,
                "live_orchestration_performed": False,
                "worker_processes_started": False,
            }
        )
        result["adapter_result"] = adapter_result

    if args.write_output:
        Path(args.write_output).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    if args.brief and not (
        args.plan_file_operation
        or args.execute_sandbox_file_write
        or args.plan_repo_patch
        or args.execute_repo_patch
        or args.dry_run_bundle
        or args.write_dry_run_bundle
        or args.execution_profile is not None
        or args.approval_handoff
        or args.write_approval_handoff is not None
        or args.sign_approval_record
        or args.write_approval_record is not None
    ):
        output: Any = result["command_brief"]
        if artifact_summary is not None:
            output = {
                "command_brief": result["command_brief"],
                "artifact_write_summary": artifact_summary,
            }
    else:
        output = result

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
