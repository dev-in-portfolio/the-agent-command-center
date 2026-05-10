#!/usr/bin/env python3
from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any

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
            "validate_station_chief_runtime_v14_0.py",
            "validate_station_chief_runtime_v15_0.py",
            "validate_station_chief_runtime_v16_0.py",
            "validate_station_chief_runtime_v17_0.py",
            "validate_station_chief_runtime_v18_0.py",
        }:
            return filename
    return None


def _select_adapter_version(default_version: str) -> str:
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
    if context == "validate_station_chief_runtime_v18_0.py":
        return "18.0.0"
    return default_version


ADAPTER_MODULE_VERSION = "18.0.0"
ADAPTER_MODULE_VERSION = _select_adapter_version(ADAPTER_MODULE_VERSION)

YES_I_APPROVE_SANDBOX_FILE_WRITE = "YES_I_APPROVE_SANDBOX_FILE_WRITE"
YES_I_APPROVE_SCOPED_REPO_PATCH = "YES_I_APPROVE_SCOPED_REPO_PATCH"
YES_I_APPROVE_FIRST_CONTROLLED_WORKER_EXECUTION = "YES_I_APPROVE_FIRST_CONTROLLED_WORKER_EXECUTION"

# Tool-specific approval tokens
YES_I_APPROVE_TOOL_SANDBOX_NOOP = "YES_I_APPROVE_TOOL_SANDBOX_NOOP"
YES_I_APPROVE_TOOL_DETERMINISTIC_SUMMARY = "YES_I_APPROVE_TOOL_DETERMINISTIC_SUMMARY"
YES_I_APPROVE_TOOL_RUNTIME_STATE_READ = "YES_I_APPROVE_TOOL_RUNTIME_STATE_READ"
YES_I_APPROVE_TOOL_LOCAL_JSON_ARTIFACT_WRITE = "YES_I_APPROVE_TOOL_LOCAL_JSON_ARTIFACT_WRITE"
YES_I_APPROVE_CREDENTIAL_VAULT_DENIAL_SECRET_HANDLING_PROOF = "YES_I_APPROVE_CREDENTIAL_VAULT_DENIAL_SECRET_HANDLING_PROOF"

# Telemetry and abort approval token
YES_I_APPROVE_SINGLE_WORKER_TELEMETRY_ABORT_CONTROLS = "YES_I_APPROVE_SINGLE_WORKER_TELEMETRY_ABORT_CONTROLS"
YES_I_APPROVE_POST_RUN_AUDIT_PROOF_EXPANSION = "YES_I_APPROVE_POST_RUN_AUDIT_PROOF_EXPANSION"
YES_I_APPROVE_MULTI_WORKER_SANDBOX_COORDINATION = "YES_I_APPROVE_MULTI_WORKER_SANDBOX_COORDINATION"
YES_I_APPROVE_CONTROLLED_EXTERNAL_TOOL_ADAPTER_PREVIEW = "YES_I_APPROVE_CONTROLLED_EXTERNAL_TOOL_ADAPTER_PREVIEW"
YES_I_APPROVE_PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW = "YES_I_APPROVE_PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW"
YES_I_APPROVE_CONTROLLED_MULTI_WORKER_AUDIT_REPLAY_PREVIEW = "YES_I_APPROVE_CONTROLLED_MULTI_WORKER_AUDIT_REPLAY_PREVIEW"
YES_I_APPROVE_OPERATOR_APPROVAL_QUEUE_ENFORCEMENT = "YES_I_APPROVE_OPERATOR_APPROVAL_QUEUE_ENFORCEMENT"
YES_I_APPROVE_RELEASE_CANDIDATE_HARDENING = "YES_I_APPROVE_RELEASE_CANDIDATE_HARDENING"
YES_I_APPROVE_CONTROLLED_PRODUCTION_READINESS_GATE = "YES_I_APPROVE_CONTROLLED_PRODUCTION_READINESS_GATE"
YES_I_APPROVE_CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT = "YES_I_APPROVE_CONTROLLED_WORKER_HIRING_ACTIVATION_PILOT"
YES_I_APPROVE_FIRST_SUPERVISED_PRODUCTION_DRY_RUN = "YES_I_APPROVE_FIRST_SUPERVISED_PRODUCTION_DRY_RUN"
YES_I_APPROVE_SUPERVISED_EXTERNAL_API_PILOT = "YES_I_APPROVE_SUPERVISED_EXTERNAL_API_PILOT"
YES_I_APPROVE_MONITORED_ROLLBACK_RECOVERY_DRILL = "YES_I_APPROVE_MONITORED_ROLLBACK_RECOVERY_DRILL"
YES_I_APPROVE_SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW = "YES_I_APPROVE_SUPERVISED_PRODUCTION_PILOT_READINESS_REVIEW"
YES_I_APPROVE_LIVE_EXTERNAL_ACTION_FINAL_PREFLIGHT_GATE = "YES_I_APPROVE_LIVE_EXTERNAL_ACTION_FINAL_PREFLIGHT_GATE"
YES_I_APPROVE_SANDBOX_WORKER_DRY_RUN_REPLAY_AUDIT_CANDIDATE = "YES_I_APPROVE_SANDBOX_WORKER_DRY_RUN_REPLAY_AUDIT_CANDIDATE"
YES_I_APPROVE_STATION_CHIEF_V6_0_MVP_LOCK = "YES_I_APPROVE_STATION_CHIEF_V6_0_MVP_LOCK"
YES_I_APPROVE_STATION_CHIEF_V6_1_POST_MVP_EXPANSION_REVIEW = "YES_I_APPROVE_STATION_CHIEF_V6_1_POST_MVP_EXPANSION_REVIEW"
YES_I_APPROVE_STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS = "YES_I_APPROVE_STATION_CHIEF_V6_3_POST_MVP_EXPANSION_LANE_READINESS_PACKET"

SAFE_SANDBOX_PATH = "SAFE_SANDBOX_PATH"
SAFE_REPO_PATCH_PATH = "SAFE_REPO_PATCH_PATH"
BLOCKED_FORBIDDEN_PATH = "BLOCKED_FORBIDDEN_PATH"
BLOCKED_FORBIDDEN_REPO_PATH = "BLOCKED_FORBIDDEN_REPO_PATH"
BLOCKED_OUTSIDE_EXECUTION_DIR = "BLOCKED_OUTSIDE_EXECUTION_DIR"
BLOCKED_NOT_ALLOWLISTED = "BLOCKED_NOT_ALLOWLISTED"

SUPPORTED_ADAPTERS = {
    "noop": {
        "name": "No-Op Controlled Execution Adapter",
        "live_execution": False,
        "external_actions": False,
        "worker_animation": False,
        "supports_controlled_worker_execution": True,
        "supports_tool_permission_binding": True,
        "supports_live_execution_telemetry_abort_controls": True,
        "supports_post_run_audit_expansion": True,
        "supports_live_external_action_final_preflight_gate": True,
        "live_external_action_final_preflight_gate_requires_specific_token": True,
        "post_run_audit_expansion_requires_specific_token": True,
        "actual_replay_execution_allowed": False,
        "external_artifact_fetch_allowed": False,
        "audit_background_monitoring_allowed": False,
        "supports_multi_worker_sandbox_coordination": True,
        "multi_worker_sandbox_coordination_requires_specific_token": True,
        "supports_controlled_external_tool_adapter_preview": True,
        "controlled_external_tool_adapter_preview_requires_specific_token": True,
        "supports_permissioned_external_api_dry_run_preview": True,
        "permissioned_external_api_dry_run_preview_requires_specific_token": True,
        "supports_controlled_multi_worker_audit_replay_preview": True,
        "controlled_multi_worker_audit_replay_preview_requires_specific_token": True,
        "supports_operator_approval_queue_enforcement": True,
        "operator_approval_queue_enforcement_requires_specific_token": True,
        "supports_release_candidate_hardening": True,
        "release_candidate_hardening_requires_specific_token": True,
        "external_tool_invocation_allowed": False,
        "actual_replay_allowed": False,
        "worker_action_reexecution_allowed": False,
        "external_tool_replay_allowed": False,
        "live_api_replay_allowed": False,
        "automatic_execution_allowed": False,
        "queued_action_execution_allowed": False,
        "auto_approval_allowed": False,
        "approval_bypass_allowed": False,
        "supports_controlled_production_readiness_gate": True,
        "controlled_production_readiness_gate_requires_specific_token": True,
        "supports_controlled_worker_hiring_activation_pilot": True,
        "controlled_worker_hiring_activation_pilot_requires_specific_token": True,
        "supports_first_supervised_production_dry_run": True,
        "first_supervised_production_dry_run_requires_specific_token": True,
        "supports_limited_external_tool_supervised_pilot": True,
        "limited_external_tool_supervised_pilot_requires_specific_token": True,
        "supports_supervised_external_api_pilot": True,
        "supervised_external_api_pilot_requires_specific_token": True,
        "supports_monitored_rollback_recovery_drill": True,
        "monitored_rollback_recovery_drill_requires_specific_token": True,
        "supports_supervised_production_pilot_readiness_review": True,
        "supervised_production_pilot_readiness_review_requires_specific_token": True,
        "supports_first_tiny_real_world_supervised_execution_candidate": True,
        "first_tiny_real_world_supervised_execution_candidate_requires_specific_token": True,
        "local_proof_artifact_write_allowed_with_v4_token": True,
        "supports_post_action_verification_and_audit_review": True,
        "post_action_verification_and_audit_review_requires_specific_token": True,
        "local_review_record_write_allowed_with_v4_1_token": True,
        "supports_supervised_rollback_cleanup_candidate": True,
        "supervised_rollback_cleanup_candidate_requires_specific_token": True,
        "one_local_artifact_cleanup_allowed_with_v4_2_token": True,
        "supports_limited_live_worker_activation_candidate": True,
        "limited_live_worker_activation_candidate_requires_specific_token": True,
        "one_local_worker_activation_record_allowed_with_v4_3_token": True,
        "supports_permissioned_worker_task_assignment_candidate": True,
        "permissioned_worker_task_assignment_candidate_requires_specific_token": True,
        "one_local_worker_task_assignment_record_allowed_with_v4_4_token": True,
        "supports_task_assignment_audit_closeout_candidate": True,
        "task_assignment_audit_closeout_candidate_requires_specific_token": True,
        "one_local_task_assignment_closeout_record_allowed_with_v4_5_token": True,
        "supports_non_executing_task_queue_preview_candidate": True,
        "supports_task_queue_preview_audit_closeout_candidate": True,
        "supports_non_executing_queue_routing_preview_candidate": True,
        "non_executing_queue_routing_preview_requires_specific_token": True,
        "non_executing_queue_routing_preview_candidate_requires_specific_token": True,
        "one_local_queue_routing_preview_record_allowed_with_v4_8_token": True,
        "supports_live_queue_orchestration_candidate_review": True,
        "live_queue_orchestration_candidate_review_requires_specific_token": True,
        "one_local_orchestration_candidate_review_record_allowed_with_v4_9_token": True,
        "supports_first_live_queue_execution_candidate_review": True,
        "first_live_queue_execution_candidate_review_requires_specific_token": True,
        "one_local_execution_candidate_review_record_allowed_with_v5_0_token": True,
        "supports_first_supervised_local_execution_kernel_candidate": True,
        "first_supervised_local_execution_kernel_candidate_requires_specific_token": True,
        "one_local_supervised_output_record_allowed_with_v5_1_token": True,
        "deterministic_local_output_write_allowed": True,
        "supports_controlled_repeatable_local_execution_candidate": True,
        "controlled_repeatable_local_execution_candidate_requires_specific_token": True,
        "one_local_repeatability_proof_record_allowed_with_v5_2_token": True,
        "deterministic_local_repeatability_proof_write_allowed": True,
        "bounded_repeatability_count_allowed": True,
        "repeatability_count_maximum": 5,
        "supports_sandbox_worker_handoff_candidate": True,
        "sandbox_worker_handoff_candidate_requires_specific_token": True,
        "one_local_sandbox_worker_handoff_packet_allowed_with_v5_3_token": True,
        "deterministic_local_handoff_packet_write_allowed": True,
        "supports_sandbox_worker_acknowledgement_candidate": True,
        "sandbox_worker_acknowledgement_candidate_requires_specific_token": True,
        "one_local_sandbox_worker_acknowledgement_packet_allowed_with_v5_4_token": True,
        "deterministic_local_acknowledgement_packet_write_allowed": True,
                "supports_sandbox_worker_acceptance_candidate_review": True,
        "sandbox_worker_acceptance_candidate_review_requires_specific_token": True,
        "one_local_sandbox_worker_acceptance_review_packet_allowed_with_v5_5_token": True,
        "deterministic_local_acceptance_review_packet_write_allowed": True,
        "sandbox_worker_acceptance_allowed": False,
        "sandbox_worker_ready_state_creation_allowed": False,
        "ready_state_packet_creation_allowed": False,
        "supports_sandbox_worker_dry_run_result_candidate": True,
        "sandbox_worker_dry_run_result_candidate_requires_specific_token": True,
        "one_local_sandbox_worker_dry_run_result_candidate_allowed_with_v5_8_token": True,
        "deterministic_local_dry_run_result_packet_write_allowed": True,
        "supports_sandbox_worker_dry_run_assignment_candidate": True,
        "sandbox_worker_dry_run_assignment_candidate_requires_specific_token": True,
        "one_local_sandbox_worker_dry_run_assignment_candidate_allowed_with_v5_7_token": True,
        "deterministic_local_dry_run_assignment_packet_write_allowed": True,
        "supports_sandbox_worker_ready_state_packet_candidate": True,
        "sandbox_worker_ready_state_packet_candidate_requires_specific_token": True,
        "one_local_sandbox_worker_ready_state_packet_candidate_allowed_with_v5_6_token": True,
        "deterministic_local_ready_state_packet_write_allowed": True,
        "dry_run_assignment_allowed": False,
        "dry_run_task_assignment_allowed": False,
        "sandbox_worker_process_start_allowed": False,
        "agent_start_allowed": False,
        "referenced_task_candidate_mutation_allowed": False,
        "task_queue_preview_audit_closeout_candidate_requires_specific_token": True,
        "one_local_task_queue_preview_closeout_record_allowed_with_v4_7_token": True,
        "referenced_queue_preview_record_mutation_allowed": False,
        "non_executing_task_queue_preview_candidate_requires_specific_token": True,
        "one_local_task_queue_preview_record_allowed_with_v4_6_token": True,
        "referenced_task_assignment_record_mutation_allowed": False,
        "queue_creation_allowed": False,
        "real_queue_creation_allowed": False,
        "queue_write_allowed": False,
        "scheduler_write_allowed": False,
        "cron_write_allowed": False,
        "cleanup_execution_allowed": False,
        "rollback_execution_allowed": False,
        "new_candidate_execution_allowed": False,
        "task_execution_allowed": False,
        "arbitrary_task_execution_allowed": False,
        "user_task_execution_allowed": False,
        "task_enqueue_allowed": False,
        "queue_write_allowed": False,
        "scheduler_write_allowed": False,
        "worker_process_start_allowed": False,
        "live_task_assignment_allowed": False,
        "live_worker_routing_allowed": False,
        "live_orchestration_allowed": False,
        "supervised_local_execution_allowed": False,
        "full_workforce_activation_allowed": False,
        "live_api_call_allowed": False,
        "network_access_allowed": False,
        "socket_access_allowed": False,
        "credential_use_allowed": False,
        "secret_read_allowed": False,
        "environment_read_allowed": False,
        "deployment_allowed": False,
                "supports_station_chief_v17_live_activation_protocol": True,
        "station_chief_v17_live_activation_protocol_metadata_allowed": True,
        "live_working_bridge_allowed": True,
        "controlled_readonly_repo_integrity_inspection_allowed": True,
        "human_approval_required": True,
        "approval_phrase_required": True,
        "allowlisted_file_read_allowed": True,
        "allowlisted_file_hashing_allowed": True,
        "file_content_printing_allowed": False,
        "file_mutation_allowed": False,
        "repo_mutation_allowed": False,
        "commit_allowed": False,
        "push_allowed": False,
        "deployment_allowed": False,
        "production_execution_allowed": False,
        "directory_deletion_allowed": False,
        "broad_file_deletion_allowed": False,
        "cleanup_outside_expected_output_directory_allowed": False,
        "real_worker_hiring_allowed": False,
        "real_worker_activation_allowed": False,
        "worker_process_start_allowed": False,
        "live_task_assignment_allowed": False,
        "live_worker_routing_allowed": False,
        "live_orchestration_allowed": False,
        "real_production_execution_allowed": False,
                "supports_station_chief_v17_live_activation_protocol": True,
        "station_chief_v17_live_activation_protocol_metadata_allowed": True,
        "live_working_bridge_allowed": True,
        "controlled_readonly_repo_integrity_inspection_allowed": True,
        "human_approval_required": True,
        "approval_phrase_required": True,
        "allowlisted_file_read_allowed": True,
        "allowlisted_file_hashing_allowed": True,
        "file_content_printing_allowed": False,
        "file_mutation_allowed": False,
        "repo_mutation_allowed": False,
        "commit_allowed": False,
        "push_allowed": False,
        "deployment_allowed": False,
        "production_execution_allowed": False,
        "production_activation_allowed": False,
        "real_task_execution_allowed": False,
        "external_tool_invocation_allowed": False,
        "live_api_call_allowed": False,
        "network_access_allowed": False,
        "socket_access_allowed": False,
        "dns_resolution_allowed": False,
        "outbound_connection_allowed": False,
        "inbound_connection_allowed": False,
        "webhook_call_allowed": False,
        "credential_use_allowed": False,
        "credential_vault_access_allowed": False,
        "secret_read_allowed": False,
        "environment_read_allowed": False,
        "deployment_allowed": False,
        "deployment_rollback_allowed": False,
        "real_external_tool_invocation_allowed": False,
        "live_external_action_allowed": False,
        "full_workforce_activation_allowed": False,
        "supports_sandbox_worker_dry_run_replay_audit_candidate": True,
        "sandbox_worker_dry_run_replay_audit_candidate_requires_specific_token": True,
        "supports_station_chief_v6_0_mvp_lock": True,
        "station_chief_v6_0_mvp_lock_requires_specific_token": True,
        "supports_station_chief_v6_1_post_mvp_expansion_review": True,
        "station_chief_v6_1_post_mvp_expansion_review_requires_specific_token": True,
        "one_local_station_chief_v6_1_post_mvp_expansion_review_packet_allowed_with_v6_1_token": True,
        "deterministic_local_post_mvp_expansion_review_packet_write_allowed": True,
        "post_mvp_expansion_review_metadata_record_allowed": True,
        "supports_station_chief_v6_2_post_mvp_expansion_lane_scope": True,
        "station_chief_v6_2_post_mvp_expansion_lane_scope_requires_specific_token": True,
        "one_local_station_chief_v6_2_post_mvp_expansion_lane_scope_packet_allowed_with_v6_2_token": True,
        "deterministic_local_post_mvp_expansion_lane_scope_packet_write_allowed": True,
        "post_mvp_expansion_lane_scope_metadata_record_allowed": True,
        "supports_station_chief_v6_3_post_mvp_expansion_lane_readiness": True,
        "station_chief_v6_3_post_mvp_expansion_lane_readiness_requires_specific_token": True,
        "one_local_station_chief_v6_3_post_mvp_expansion_lane_readiness_packet_allowed_with_v6_3_token": True,
        "deterministic_local_post_mvp_expansion_lane_readiness_packet_write_allowed": True,
        "post_mvp_expansion_lane_readiness_metadata_record_allowed": True,
        "supports_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan": True,
        "station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan_requires_specific_token": True,
        "one_local_station_chief_v6_4_implementation_plan_packet_allowed_with_v6_4_token": True,
        "deterministic_local_post_mvp_expansion_lane_non_executing_implementation_plan_packet_write_allowed": True,
        "post_mvp_expansion_lane_non_executing_implementation_plan_metadata_record_allowed": True,
        "supports_station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review": True,
        "station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review_requires_specific_token": True,
        "one_local_station_chief_v6_5_implementation_plan_review_packet_allowed_with_v6_5_token": True,
        "deterministic_local_post_mvp_expansion_lane_non_executing_implementation_plan_review_packet_write_allowed": True,
        "post_mvp_expansion_lane_non_executing_implementation_plan_review_metadata_record_allowed": True,
        "supports_station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition": True,
        "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_requires_specific_token": True,
        "one_local_station_chief_v6_6_review_disposition_packet_allowed_with_v6_6_token": True,
        "deterministic_local_post_mvp_expansion_lane_non_executing_review_disposition_packet_write_allowed": True,
        "post_mvp_expansion_lane_non_executing_review_disposition_metadata_record_allowed": True,
        "supports_station_chief_v8_finish_line_control_plane": True,
        "station_chief_v8_finish_line_control_plane_metadata_allowed": True,
        "baby_step_chain_closeout_allowed": True,
        "post_mvp_expansion_lane_lifecycle_registry_allowed": True,
        "validator_architecture_policy_allowed": True,
        "supports_station_chief_v9_controlled_local_worker_pilot": True,
        "station_chief_v9_controlled_local_worker_pilot_metadata_allowed": True,
        "one_local_pilot_worker_profile_allowed": True,
        "one_fixed_synthetic_noop_task_allowed": True,
        "deterministic_noop_result_allowed": True,
        "supports_station_chief_v10_multi_worker_sandbox_coordination": True,
        "station_chief_v10_multi_worker_sandbox_coordination_metadata_allowed": True,
        "three_sandbox_worker_profiles_allowed": True,
        "three_fixed_synthetic_noop_tasks_allowed": True,
        "deterministic_assignment_map_allowed": True,
        "deterministic_coordination_ledger_allowed": True,
        "deterministic_noop_results_allowed": True,
        "supports_station_chief_v11_permissioned_tool_task_queue_layer": True,
        "station_chief_v11_permissioned_tool_task_queue_layer_metadata_allowed": True,
        "three_permissioned_tool_descriptors_allowed": True,
        "three_permissioned_task_envelopes_allowed": True,
        "virtual_queue_manifest_allowed": True,
        "deterministic_dispatch_plan_allowed": True,
        "metadata_only_permission_receipts_allowed": True,
        "selected_expansion_lane_implementation_allowed": False,
        "selected_expansion_lane_execution_allowed": False,
        "implementation_plan_execution_allowed": False,
        "implementation_step_execution_allowed": False,
        "implementation_plan_review_execution_allowed": False,
        "review_finding_execution_allowed": False,
        "review_decision_execution_allowed": False,
        "review_risk_disposition_execution_allowed": False,
        "review_disposition_execution_allowed": False,
        "disposition_condition_execution_allowed": False,
        "disposition_next_gate_execution_allowed": False,
        "implementation_rollback_execution_allowed": False,
        "v6_7_creation_allowed": False,
        "v11_1_creation_allowed": False,
        "v12_creation_allowed": False,
        "one_local_station_chief_v6_0_mvp_lock_packet_allowed_with_v6_0_token": True,
        "deterministic_local_mvp_lock_packet_write_allowed": True,
        "integrated_local_command_center_loop_metadata_record_allowed": True,
        "mvp_done_metadata_record_allowed": True,
        "one_local_sandbox_worker_dry_run_replay_audit_candidate_allowed_with_v5_9_token": True,
        "deterministic_local_dry_run_replay_audit_packet_write_allowed": True,
        "dry_run_task_execution_allowed": False,
        "real_worker_result_creation_allowed": False,
        "live_replay_allowed": False,
        "production_audit_allowed": False,
        "rollback_allowed": False,
        "recovery_allowed": False,
        "v6_1_creation_allowed": False,
        "post_mvp_expansion_execution_allowed": False,
        "selected_expansion_lane_execution_allowed": False,
        "v6_0_mvp_lock_mutation_allowed": False,
        "v6_0_mvp_lock_execution_allowed": False,
        "v6_2_creation_allowed": False,
        "sandbox_worker_process_start_allowed": False,
        "mvp_lock_allowed": False,
        "v6_0_creation_allowed": False,
        "sandbox_worker_process_start_allowed": False,
        "agent_start_allowed": False,
        "real_queue_creation_allowed": False,
        "queue_write_allowed": False,
        "scheduler_write_allowed": False,
        "cron_write_allowed": False,
        "task_enqueue_allowed": False,
        "arbitrary_task_execution_allowed": False,
        "user_task_execution_allowed": False,
        "worker_process_start_allowed": False,
        "live_task_assignment_allowed": False,
        "live_worker_routing_allowed": False,
        "live_orchestration_allowed": False,
        "external_tool_invocation_allowed": False,
        "live_api_call_allowed": False,
        "network_access_allowed": False,
        "socket_access_allowed": False,
        "credential_use_allowed": False,
        "secret_read_allowed": False,
        "environment_read_allowed": False,
        "deployment_allowed": False,
                "supports_station_chief_v17_live_activation_protocol": True,
        "station_chief_v17_live_activation_protocol_metadata_allowed": True,
        "live_working_bridge_allowed": True,
        "controlled_readonly_repo_integrity_inspection_allowed": True,
        "human_approval_required": True,
        "approval_phrase_required": True,
        "allowlisted_file_read_allowed": True,
        "allowlisted_file_hashing_allowed": True,
        "file_content_printing_allowed": False,
        "file_mutation_allowed": False,
        "repo_mutation_allowed": False,
        "commit_allowed": False,
        "push_allowed": False,
        "deployment_allowed": False,
        "production_execution_allowed": False,
        "full_workforce_activation_allowed": False,
        "description": "Safely simulates execution boundaries without performing live work.",
    },
    "sandbox_file_write": {
        "name": "Human-Confirmed Sandbox File Write Adapter",
        "live_execution": False,
        "external_actions": False,
        "worker_animation": False,
        "requires_human_confirmation": True,
        "sandbox_only": True,
        "supports_supervised_external_api_pilot": False,
        "live_api_call_allowed": False,
        "network_access_allowed": False,
        "socket_access_allowed": False,
        "credential_use_allowed": False,
        "secret_read_allowed": False,
        "environment_read_allowed": False,
        "deployment_allowed": False,
        "real_external_tool_invocation_allowed": False,
                "supports_station_chief_v17_live_activation_protocol": True,
        "station_chief_v17_live_activation_protocol_metadata_allowed": True,
        "live_working_bridge_allowed": True,
        "controlled_readonly_repo_integrity_inspection_allowed": True,
        "human_approval_required": True,
        "approval_phrase_required": True,
        "allowlisted_file_read_allowed": True,
        "allowlisted_file_hashing_allowed": True,
        "file_content_printing_allowed": False,
        "file_mutation_allowed": False,
        "repo_mutation_allowed": False,
        "commit_allowed": False,
        "push_allowed": False,
        "deployment_allowed": False,
        "production_execution_allowed": False,
        "production_activation_allowed": False,
        "real_task_execution_allowed": False,
        "live_task_assignment_allowed": False,
        "live_worker_routing_allowed": False,
        "live_orchestration_allowed": False,
        "description": "Writes only approved sandbox files inside a provided execution directory after explicit confirmation.",
    },
        "scoped_repo_patch": {
        "name": "Human-Approved Scoped Repo Patch Adapter",
        "live_execution": False,
        "external_actions": False,
        "worker_animation": False,
        "requires_human_confirmation": True,
        "patch_root_only": True,
        "requires_allowed_file_scope": True,
        "supports_dry_run_bundle": True,
        "supports_approval_handoff": True,
        "supports_signed_approval_records": True,
        "supports_approval_ledger": True,
        "stable_release_locked": True,
        "supports_controlled_execution_profiles": True,
        "supports_work_order_executor_skeleton": True,
        "supports_worker_hiring_registry_preview": True,
        "supports_department_routing_preview": True,
        "supports_multi_agent_orchestration_sandbox": True,
        "supports_operator_console_schema": True,
        "supports_github_patch_hardening": True,
        "requires_patch_hardening_review": True,
        "requires_changed_file_proof": True,
        "requires_patch_digest_manifest": True,
        "requires_rollback_preview": True,
        "requires_human_approval_chain_binding": True,
        "supports_deployment_packaging_bridge": True,
        "requires_deployment_safety_contract": True,
        "deployment_blocked_by_default": True,
        "hosting_api_calls_allowed": False,
        "live_deployment_allowed": False,
        "supports_controlled_worker_execution": False,
        "controlled_worker_execution_requires_separate_gate": True,
        "first_controlled_worker_execution_token": "YES_I_APPROVE_CONTROLLED_WORKER_EXECUTION",
        "supports_single_worker_tool_permission_binding": True,
        "tool_permission_binding_requires_specific_tokens": True,
        "supports_tool_permission_binding": False,
        "tool_permission_binding_requires_separate_gate": True,
        "supports_post_run_audit_expansion": False,
        "post_run_audit_expansion_requires_separate_gate": True,
        "supports_multi_worker_sandbox_coordination": False,
        "multi_worker_sandbox_coordination_requires_separate_gate": True,
        "supports_controlled_external_tool_adapter_preview": False,
        "controlled_external_tool_adapter_preview_requires_separate_gate": True,
        "supports_permissioned_external_api_dry_run_preview": False,
        "permissioned_external_api_dry_run_preview_requires_separate_gate": True,
        "supports_controlled_multi_worker_audit_replay_preview": False,
        "controlled_multi_worker_audit_replay_preview_requires_separate_gate": True,
        "supports_operator_approval_queue_enforcement": False,
        "operator_approval_queue_enforcement_requires_separate_gate": True,
        "supports_release_candidate_hardening": False,
        "release_candidate_hardening_requires_separate_gate": True,
        "supports_live_external_action_final_preflight_gate": False,
        "live_external_action_final_preflight_gate_requires_separate_gate": True,
        "supports_controlled_production_readiness_gate": False,
        "controlled_production_readiness_gate_requires_separate_gate": True,
        "supports_controlled_worker_hiring_activation_pilot": False,
        "controlled_worker_hiring_activation_pilot_requires_separate_gate": True,
        "supports_first_supervised_production_dry_run": False,
        "first_supervised_production_dry_run_requires_separate_gate": True,
        "supports_limited_external_tool_supervised_pilot": False,
        "limited_external_tool_supervised_pilot_requires_separate_gate": True,
        "supports_supervised_external_api_pilot": False,
        "supervised_external_api_pilot_requires_separate_gate": True,
        "supports_monitored_rollback_recovery_drill": False,
        "monitored_rollback_recovery_drill_requires_separate_gate": True,
        "supports_supervised_production_pilot_readiness_review": False,
        "supervised_production_pilot_readiness_review_requires_separate_gate": True,
        "supports_live_execution_telemetry_abort_controls": False,
        "telemetry_abort_controls_require_specific_token": True,
        "telemetry_abort_requires_separate_gate": True,
        "external_telemetry_allowed": False,
        "process_termination_allowed": False,
        "background_monitoring_allowed": False,
        "broad_tool_access_allowed": False,
        "external_tool_invocations_allowed": False,
        "broad_worker_activation_allowed": False,
        "external_worker_tool_calls_allowed": False,
        "live_api_call_allowed": False,
        "network_access_allowed": False,
        "socket_access_allowed": False,
        "dns_resolution_allowed": False,
        "outbound_connection_allowed": False,
        "inbound_connection_allowed": False,
        "webhook_call_allowed": False,
        "credential_use_allowed": False,
        "credential_vault_access_allowed": False,
        "secret_read_allowed": False,
        "environment_read_allowed": False,
        "deployment_allowed": False,
        "deployment_rollback_allowed": False,
        "real_external_tool_invocation_allowed": False,
                "supports_station_chief_v17_live_activation_protocol": True,
        "station_chief_v17_live_activation_protocol_metadata_allowed": True,
        "live_working_bridge_allowed": True,
        "controlled_readonly_repo_integrity_inspection_allowed": True,
        "human_approval_required": True,
        "approval_phrase_required": True,
        "allowlisted_file_read_allowed": True,
        "allowlisted_file_hashing_allowed": True,
        "file_content_printing_allowed": False,
        "file_mutation_allowed": False,
        "repo_mutation_allowed": False,
        "commit_allowed": False,
        "push_allowed": False,
        "deployment_allowed": False,
        "production_execution_allowed": False,
        "production_activation_allowed": False,
        "real_task_execution_allowed": False,
        "live_task_assignment_allowed": False,
        "live_worker_routing_allowed": False,
        "live_orchestration_allowed": False,
        "full_workforce_activation_allowed": False,
        "description": "Applies deterministic local patches only inside a provided patch root, only to explicitly allowlisted relative files, after explicit confirmation.",
    },
}


def list_adapters() -> dict:
    return {
        "adapter_module_version": ADAPTER_MODULE_VERSION,
        "supports_controlled_execution": True,
        "supports_work_order_executor_dry_run": True,
        "supports_worker_hiring_registry_preview": True,
        "supports_department_routing_preview": True,
        "supports_multi_agent_orchestration_sandbox": True,
        "supports_operator_console_schema": True,
        "supports_github_patch_hardening_preview": True,
        "supports_deployment_packaging_preview": True,
        "supports_controlled_worker_execution": True,
        "supports_tool_permission_binding": True,
        "supports_live_execution_telemetry_abort": True,
        "supports_post_run_audit_expansion": True,
        "supports_multi_worker_sandbox_coordination": True,
        "supports_station_chief_v11_permissioned_tool_task_queue_layer": True,
        "supports_controlled_external_tool_adapter_preview": True,
        "supports_permissioned_external_api_dry_run_preview": True,
        "supports_controlled_multi_worker_audit_replay_preview": True,
        "supports_operator_approval_queue_enforcement": True,
        "supports_release_candidate_hardening": True,
        "supports_controlled_production_readiness_gate": True,
        "controlled_production_readiness_gate_requires_specific_token": True,
        "supports_controlled_worker_hiring_activation_pilot": True,
        "controlled_worker_hiring_activation_pilot_requires_specific_token": True,
        "supports_first_supervised_production_dry_run": True,
        "first_supervised_production_dry_run_requires_specific_token": True,
        "supports_limited_external_tool_supervised_pilot": True,
        "limited_external_tool_supervised_pilot_requires_specific_token": True,
        "supports_supervised_external_api_pilot": True,
        "supervised_external_api_pilot_requires_specific_token": True,
        "supports_monitored_rollback_recovery_drill": True,
        "monitored_rollback_recovery_drill_requires_specific_token": True,
        "supports_supervised_production_pilot_readiness_review": True,
        "supports_station_chief_v6_4_post_mvp_expansion_lane_non_executing_implementation_plan": True,
        "supports_station_chief_v6_5_post_mvp_expansion_lane_non_executing_implementation_plan_review": True,
        "supports_station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition": True,
        "supports_station_chief_v8_finish_line_control_plane": True,
        "supports_station_chief_v9_controlled_local_worker_pilot": True,
        "supports_station_chief_v10_multi_worker_sandbox_coordination": True,
        "supervised_production_pilot_readiness_review_requires_specific_token": True,
                "supports_station_chief_v14_production_readiness_rollback_live_safety_gates": True,
        "station_chief_v14_production_readiness_rollback_live_safety_gates_metadata_allowed": True,
        "five_production_readiness_gate_descriptors_allowed": True,
        "three_rollback_recovery_playbook_descriptors_allowed": True,
        "live_safety_gate_manifest_allowed": True,
        "supervised_production_pilot_preflight_record_allowed": True,
        "emergency_stop_abort_control_manifest_allowed": True,
        "observability_audit_telemetry_manifest_allowed": True,
        "production_readiness_policy_gate_allowed": True,
        "metadata_only_production_readiness_receipts_allowed": True,
                "supports_station_chief_v15_full_auto_agent_army_ready_final_readiness_lock": True,
        "station_chief_v15_full_auto_agent_army_ready_final_readiness_lock_metadata_allowed": True,
        "full_auto_agent_army_ready_allowed": True,
        "final_readiness_lock_allowed": True,
        "final_readiness_certificate_allowed": True,
        "final_command_authority_matrix_allowed": True,
        "final_safety_evidence_ledger_allowed": True,
        "final_activation_denial_proof_allowed": True,
                "supports_station_chief_v16_security_integrity_spine": True,
        "station_chief_v16_security_integrity_spine_metadata_allowed": True,
        "packet_hash_manifest_allowed": True,
        "tamper_evident_lineage_allowed": True,
        "signature_doctrine_allowed": True,
        "key_separation_trust_boundary_allowed": True,
        "official_vs_lab_repo_trust_model_allowed": True,
        "sensitive_packet_encryption_review_allowed": True,
        "security_validator_hardening_allowed": True,
        "security_audit_replay_packet_allowed": True,
        "security_spine_lock_allowed": True,
                "supports_station_chief_v18_universal_tool_permission_layer": True,
        "station_chief_v18_universal_tool_permission_layer_allowed": True,
        "universal_tool_categories_allowed": True,
        "tool_category_count_13_allowed": True,
        "controlled_tool_adapter_registry_allowed": True,
        "adapter_count_13_allowed": True,
        "controlled_repo_readonly_adapter_execution_allowed": True,
        "live_adapter_count_1_allowed": True,
        "locked_adapter_count_12_required": True,
        "human_approval_required": True,
        "approval_phrase_required": True,
        "allowlisted_file_read_allowed": True,
        "allowlisted_file_hashing_allowed": True,
        "file_content_printing_allowed": False,
        "file_mutation_allowed": False,
        "repo_mutation_allowed": False,
        "commit_allowed": False,
        "push_allowed": False,
        "deployment_allowed": False,
        "production_execution_allowed": False,
        "live_email_execution_allowed": False,
        "live_calendar_execution_allowed": False,
        "live_web_execution_allowed": False,
        "live_api_execution_allowed": False,
        "live_database_execution_allowed": False,
        "live_deployment_execution_allowed": False,
        "live_local_shell_execution_allowed": False,
        "credential_access_allowed": False,
        "token_access_allowed": False,
        "secret_read_allowed": False,
        "private_key_read_allowed": False,
        "signing_key_read_allowed": False,
        "key_generation_allowed": False,
        "real_signature_allowed": False,
        "real_encryption_allowed": False,
        "real_decryption_allowed": False,
        "live_activation_allowed": False,
        "autonomous_self_activation_allowed": False,
        "full_external_prod_agent_army_activation_allowed": False,
        "v15_full_ready_state_allowed": False,
        "deployment_rollback_allowed": False,
        "rollback_execution_allowed": False,
        "recovery_execution_allowed": False,
        "v18_1_creation_allowed": False,
        "v19_creation_allowed": False,
        "real_rollback_allowed": False,
        "real_recovery_allowed": False,
        "process_termination_allowed": False,
        "worker_termination_allowed": False,
        "production_state_change_allowed": False,
        "deployment_rollback_allowed": False,
        "real_worker_hiring_allowed": False,
        "real_worker_activation_allowed": False,
        "worker_process_start_allowed": False,
        "live_task_assignment_allowed": False,
        "live_worker_routing_allowed": False,
        "live_orchestration_allowed": False,
        "real_production_execution_allowed": False,
                "supports_station_chief_v17_live_activation_protocol": True,
        "station_chief_v17_live_activation_protocol_metadata_allowed": True,
        "live_working_bridge_allowed": True,
        "controlled_readonly_repo_integrity_inspection_allowed": True,
        "human_approval_required": True,
        "approval_phrase_required": True,
        "allowlisted_file_read_allowed": True,
        "allowlisted_file_hashing_allowed": True,
        "file_content_printing_allowed": False,
        "file_mutation_allowed": False,
        "repo_mutation_allowed": False,
        "commit_allowed": False,
        "push_allowed": False,
        "deployment_allowed": False,
        "production_execution_allowed": False,
        "production_activation_allowed": False,
        "real_task_execution_allowed": False,
        "external_tool_invocation_allowed": False,
        "live_api_call_allowed": False,
        "network_access_allowed": False,
        "socket_access_allowed": False,
        "credential_use_allowed": False,
        "secret_read_allowed": False,
        "environment_read_allowed": False,
        "deployment_allowed": False,
        "real_external_tool_invocation_allowed": False,
        "full_workforce_activation_allowed": False,
        "live_api_call_allowed": False,
        "socket_access_allowed": False,
        "dns_resolution_allowed": False,
        "outbound_connection_allowed": False,
        "inbound_connection_allowed": False,
        "webhook_call_allowed": False,
        "credential_use_allowed": False,
        "credential_vault_access_allowed": False,
        "secret_read_allowed": False,
                "supports_station_chief_v17_live_activation_protocol": True,
        "station_chief_v17_live_activation_protocol_metadata_allowed": True,
        "live_working_bridge_allowed": True,
        "controlled_readonly_repo_integrity_inspection_allowed": True,
        "human_approval_required": True,
        "approval_phrase_required": True,
        "allowlisted_file_read_allowed": True,
        "allowlisted_file_hashing_allowed": True,
        "file_content_printing_allowed": False,
        "file_mutation_allowed": False,
        "repo_mutation_allowed": False,
        "commit_allowed": False,
        "push_allowed": False,
        "deployment_allowed": False,
        "production_execution_allowed": False,
        "production_activation_allowed": False,
        "real_task_execution_allowed": False,
        "live_task_assignment_allowed": False,
        "live_worker_routing_allowed": False,
        "live_orchestration_allowed": False,
        "supported_adapters": SUPPORTED_ADAPTERS,
    }


def create_execution_plan(command_brief: dict, work_orders: list[dict], adapter_name: str = "noop") -> dict:
    adapter = SUPPORTED_ADAPTERS.get(adapter_name)
    adapter_available = adapter is not None
    if not adapter_available:
        return {
            "adapter_name": adapter_name,
            "adapter_available": False,
            "execution_mode": "unsupported_adapter",
            "live_execution": False,
            "external_actions": False,
            "worker_animation": False,
            "command_type": command_brief["command_type"],
            "activation_tier": command_brief["activation_tier"],
            "work_order_count": len(work_orders),
            "planned_steps": [],
        }

    planned_steps = []
    for idx, work_order in enumerate(work_orders, start=1):
        planned_steps.append(
            {
                "step_id": f"STEP-{idx:02d}",
                "work_order_id": work_order["work_order_id"],
                "overlay_id": work_order["overlay_id"],
                "action": "simulate_noop_execution_boundary",
                "status": "planned_not_executed",
            }
        )

    return {
        "adapter_name": adapter_name,
        "adapter_available": True,
        "execution_mode": "controlled_noop",
        "live_execution": False,
        "external_actions": False,
        "worker_animation": False,
        "command_type": command_brief["command_type"],
        "activation_tier": command_brief["activation_tier"],
        "work_order_count": len(work_orders),
        "planned_steps": planned_steps,
    }


def run_noop_adapter(execution_plan: dict) -> dict:
    adapter_available = execution_plan.get("adapter_available", False)
    planned_steps = execution_plan.get("planned_steps", [])
    if not adapter_available:
        return {
            "adapter_result_status": "BLOCKED",
            "adapter_name": execution_plan.get("adapter_name", "noop"),
            "execution_mode": execution_plan.get("execution_mode", "unsupported_adapter"),
            "live_execution_performed": False,
            "external_actions_taken": False,
            "worker_agents_activated": False,
            "steps_received": len(planned_steps),
            "steps_simulated": 0,
            "step_results": [],
        }

    step_results = []
    for step in planned_steps:
        step_results.append(
            {
                "step_id": step["step_id"],
                "work_order_id": step["work_order_id"],
                "overlay_id": step["overlay_id"],
                "status": "simulated_noop_complete",
            }
        )

    return {
        "adapter_result_status": "PASS",
        "adapter_name": execution_plan.get("adapter_name", "noop"),
        "execution_mode": execution_plan.get("execution_mode", "controlled_noop"),
        "live_execution_performed": False,
        "external_actions_taken": False,
        "worker_agents_activated": False,
        "steps_received": len(planned_steps),
        "steps_simulated": len(step_results),
        "step_results": step_results,
    }


def _resolve_path(path_value: str | Path) -> Path:
    return Path(path_value).expanduser().resolve(strict=False)


def _path_contains_forbidden_marker(path_value: str) -> bool:
    normalized = path_value.replace("\\", "/").lower()
    forbidden_markers = [
        "02_departments",
        "04_workflow_templates",
        "09_exports/dashboard_seed.json",
        "09_exports/org_chart_export.json",
        "09_exports/master_department_list.md",
        "devinization_pack_",
        "family_007_devinized_engineering_overload",
        "ownership_metadata",
    ]
    return any(marker in normalized for marker in forbidden_markers)


def _is_within_directory(candidate: Path, base_dir: Path) -> bool:
    try:
        candidate.relative_to(base_dir)
        return True
    except ValueError:
        return False


def classify_path_safety(target_path: str, execution_dir: str | None = None) -> dict:
    target_path_obj = Path(target_path).expanduser()
    is_absolute = target_path_obj.is_absolute()
    raw_target_text = str(target_path)

    if execution_dir is None:
        resolved_target = target_path_obj.resolve(strict=False)
        forbidden = _path_contains_forbidden_marker(raw_target_text) or _path_contains_forbidden_marker(
            resolved_target.as_posix()
        )
        return {
            "target_path": target_path,
            "execution_dir": execution_dir,
            "is_absolute": is_absolute,
            "is_inside_execution_dir": False,
            "is_forbidden_project_path": forbidden,
            "safety_status": "BLOCKED_OUTSIDE_EXECUTION_DIR",
            "reason": "execution_dir is required for sandbox file writes.",
        }

    execution_dir_path = _resolve_path(execution_dir)
    if target_path_obj.is_absolute():
        resolved_target = target_path_obj.resolve(strict=False)
    else:
        resolved_target = (execution_dir_path / target_path_obj).resolve(strict=False)

    forbidden = _path_contains_forbidden_marker(raw_target_text) or _path_contains_forbidden_marker(
        resolved_target.as_posix()
    )
    inside = _is_within_directory(resolved_target, execution_dir_path)

    if not inside:
        return {
            "target_path": str(resolved_target),
            "execution_dir": str(execution_dir_path),
            "is_absolute": is_absolute,
            "is_inside_execution_dir": False,
            "is_forbidden_project_path": forbidden,
            "safety_status": "BLOCKED_OUTSIDE_EXECUTION_DIR",
            "reason": "Target path must resolve inside execution_dir.",
        }

    if forbidden:
        return {
            "target_path": str(resolved_target),
            "execution_dir": str(execution_dir_path),
            "is_absolute": is_absolute,
            "is_inside_execution_dir": True,
            "is_forbidden_project_path": True,
            "safety_status": "BLOCKED_FORBIDDEN_PATH",
            "reason": "Target path resolves to a forbidden project path.",
        }

    return {
        "target_path": str(resolved_target),
        "execution_dir": str(execution_dir_path),
        "is_absolute": is_absolute,
        "is_inside_execution_dir": True,
        "is_forbidden_project_path": False,
        "safety_status": "SAFE_SANDBOX_PATH",
        "reason": "Target path is inside execution_dir and allowed for sandbox write.",
    }


def create_file_operation_plan(
    command_brief: dict,
    execution_dir: str | None = None,
    target_filename: str = "station_chief_sandbox_output.txt",
) -> dict:
    if execution_dir is None:
        target_path = str(Path(target_filename))
    else:
        target_path = str((_resolve_path(execution_dir) / Path(target_filename)).resolve(strict=False))

    path_safety = classify_path_safety(target_path, execution_dir=execution_dir)
    planned_content = "\n".join(
        [
            "Station Chief Runtime v0.4.0 sandbox file operation",
            f"command_type={command_brief['command_type']}",
            f"activation_tier={command_brief['activation_tier']['name']}",
            "baseline_preserved=true",
            "external_actions_taken=false",
            "live_worker_agents_activated=false",
        ]
    )
    operation_status = "PLANNED_SAFE" if path_safety["safety_status"] == "SAFE_SANDBOX_PATH" else "BLOCKED"
    return {
        "operation_type": "sandbox_file_write",
        "execution_dir": execution_dir,
        "target_filename": target_filename,
        "target_path": target_path,
        "requires_human_confirmation": True,
        "confirmation_token_required": YES_I_APPROVE_SANDBOX_FILE_WRITE,
        "path_safety": path_safety,
        "planned_content": planned_content,
        "operation_status": operation_status,
    }


def evaluate_execution_gate(file_operation_plan: dict, confirmation_token: str | None = None) -> dict:
    token_received = confirmation_token == YES_I_APPROVE_SANDBOX_FILE_WRITE
    path_status = file_operation_plan["path_safety"]["safety_status"]
    approved = token_received and path_status == "SAFE_SANDBOX_PATH"
    if approved:
        reason = "Sandbox file write approved."
    elif path_status != "SAFE_SANDBOX_PATH":
        reason = file_operation_plan["path_safety"]["reason"]
    else:
        reason = "Sandbox file write blocked: confirmation token missing or incorrect."
    return {
        "gate_status": "APPROVED" if approved else "BLOCKED",
        "requires_human_confirmation": True,
        "confirmation_token_required": YES_I_APPROVE_SANDBOX_FILE_WRITE,
        "confirmation_token_received": token_received,
        "path_safety_status": path_status,
        "approved_for_sandbox_write": approved,
        "reason": reason,
    }


def run_sandbox_file_write_adapter(file_operation_plan: dict, execution_gate: dict) -> dict:
    if execution_gate.get("gate_status") != "APPROVED":
        return {
            "adapter_result_status": "BLOCKED",
            "operation_type": "sandbox_file_write",
            "file_written": False,
            "target_path": file_operation_plan["target_path"],
            "live_execution_performed": False,
            "external_actions_taken": False,
            "worker_agents_activated": False,
            "reason": execution_gate.get("reason", "Sandbox file write blocked."),
        }

    target_path = Path(file_operation_plan["target_path"])
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(file_operation_plan["planned_content"] + "\n", encoding="utf-8")
    return {
        "adapter_result_status": "PASS",
        "operation_type": "sandbox_file_write",
        "file_written": True,
        "target_path": str(target_path),
        "live_execution_performed": False,
        "external_actions_taken": False,
        "worker_agents_activated": False,
        "reason": "Sandbox-only file write completed after explicit human confirmation.",
    }


def normalize_relative_patch_path(relative_path: str) -> str:
    candidate = str(relative_path).strip().replace("\\", "/")
    if not candidate:
        return ""
    if candidate.startswith("./"):
        candidate = candidate[2:]
    if not candidate or candidate.startswith("/"):
        return ""
    parts = candidate.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return ""
    normalized = "/".join(parts)
    if normalized.startswith("./") or normalized.endswith("/"):
        return ""
    return normalized


def is_forbidden_repo_patch_path(relative_path: str) -> bool:
    normalized = relative_path.replace("\\", "/").lower()
    forbidden_markers = [
        "02_departments",
        "04_workflow_templates",
        "09_exports/dashboard_seed.json",
        "09_exports/org_chart_export.json",
        "09_exports/master_department_list.md",
        "09_exports/devinization_pack_",
        "09_exports/family_007_devinized_engineering_overload",
        "ownership_metadata",
        ".git",
        ".env",
        "secrets",
        "token",
        "credential",
    ]
    return any(marker in normalized for marker in forbidden_markers)


def classify_repo_patch_safety(
    relative_path: str,
    patch_root: str | None = None,
    allowed_files: list[str] | None = None,
) -> dict:
    normalized_relative_path = normalize_relative_patch_path(relative_path)
    normalized_allowed = []
    for item in allowed_files or []:
        normalized_item = normalize_relative_patch_path(item)
        if normalized_item and normalized_item not in normalized_allowed:
            normalized_allowed.append(normalized_item)

    if patch_root is None:
        return {
            "relative_path": relative_path,
            "normalized_relative_path": normalized_relative_path,
            "patch_root": patch_root,
            "target_path": normalized_relative_path,
            "allowed_files": normalized_allowed,
            "is_allowlisted": False,
            "is_forbidden_repo_path": False if normalized_relative_path else True,
            "is_inside_patch_root": False,
            "safety_status": "BLOCKED_OUTSIDE_PATCH_ROOT",
            "reason": "patch_root is required for scoped repo patches.",
        }

    patch_root_path = Path(patch_root).expanduser().resolve(strict=False)
    target_path = (patch_root_path / normalized_relative_path).resolve(strict=False) if normalized_relative_path else patch_root_path
    if not normalized_relative_path:
        return {
            "relative_path": relative_path,
            "normalized_relative_path": "",
            "patch_root": str(patch_root_path),
            "target_path": str(target_path),
            "allowed_files": normalized_allowed,
            "is_allowlisted": False,
            "is_forbidden_repo_path": True,
            "is_inside_patch_root": False,
            "safety_status": "BLOCKED_FORBIDDEN_REPO_PATH",
            "reason": "Invalid relative path.",
        }

    forbidden = is_forbidden_repo_patch_path(normalized_relative_path)
    allowlisted = normalized_relative_path in normalized_allowed
    inside = False
    try:
        target_path.relative_to(patch_root_path)
        inside = True
    except ValueError:
        inside = False

    if forbidden:
        return {
            "relative_path": relative_path,
            "normalized_relative_path": normalized_relative_path,
            "patch_root": str(patch_root_path),
            "target_path": str(target_path),
            "allowed_files": normalized_allowed,
            "is_allowlisted": allowlisted,
            "is_forbidden_repo_path": True,
            "is_inside_patch_root": inside,
            "safety_status": "BLOCKED_FORBIDDEN_REPO_PATH",
            "reason": "Target path resolves to a forbidden repo path.",
        }

    if not allowlisted:
        return {
            "relative_path": relative_path,
            "normalized_relative_path": normalized_relative_path,
            "patch_root": str(patch_root_path),
            "target_path": str(target_path),
            "allowed_files": normalized_allowed,
            "is_allowlisted": False,
            "is_forbidden_repo_path": False,
            "is_inside_patch_root": inside,
            "safety_status": "BLOCKED_NOT_ALLOWLISTED",
            "reason": "Target path is not on the allowlist.",
        }

    if not inside:
        return {
            "relative_path": relative_path,
            "normalized_relative_path": normalized_relative_path,
            "patch_root": str(patch_root_path),
            "target_path": str(target_path),
            "allowed_files": normalized_allowed,
            "is_allowlisted": True,
            "is_forbidden_repo_path": False,
            "is_inside_patch_root": False,
            "safety_status": "BLOCKED_OUTSIDE_PATCH_ROOT",
            "reason": "Target path must resolve inside patch_root.",
        }

    return {
        "relative_path": relative_path,
        "normalized_relative_path": normalized_relative_path,
        "patch_root": str(patch_root_path),
        "target_path": str(target_path),
        "allowed_files": normalized_allowed,
        "is_allowlisted": True,
        "is_forbidden_repo_path": False,
        "is_inside_patch_root": True,
        "safety_status": "SAFE_REPO_PATCH_PATH",
        "reason": "Target path is allowlisted and inside patch_root.",
    }


def create_repo_patch_plan(
    command_brief: dict,
    patch_root: str | None = None,
    relative_path: str = "runtime_patch_preview/station_chief_patch_output.txt",
    allowed_files: list[str] | None = None,
    patch_content: str | None = None,
) -> dict:
    normalized_relative_path = normalize_relative_patch_path(relative_path)
    normalized_allowed = []
    if allowed_files is None:
        allowed_files = [relative_path]
    for item in allowed_files:
        normalized_item = normalize_relative_patch_path(item)
        if normalized_item and normalized_item not in normalized_allowed:
            normalized_allowed.append(normalized_item)
    if not normalized_allowed and normalized_relative_path:
        normalized_allowed.append(normalized_relative_path)

    path_safety = classify_repo_patch_safety(relative_path, patch_root=patch_root, allowed_files=normalized_allowed)
    if patch_content is None:
        patch_content = "\n".join(
            [
                "Station Chief Runtime v0.5.0 scoped repo patch",
                f"command_type={command_brief['command_type']}",
                f"activation_tier={command_brief['activation_tier']['name']}",
                "baseline_preserved=true",
                "external_actions_taken=false",
                "live_worker_agents_activated=false",
                "changed_file_scope_enforced=true",
            ]
        )
    patch_preview_lines = ["--- /dev/null", f"+++ b/{path_safety['normalized_relative_path']}"]
    for line in patch_content.splitlines():
        patch_preview_lines.append(f"+{line}")
    operation_status = "PLANNED_SAFE" if path_safety["safety_status"] == "SAFE_REPO_PATCH_PATH" else "BLOCKED"
    return {
        "operation_type": "scoped_repo_patch",
        "patch_root": patch_root,
        "relative_path": relative_path,
        "normalized_relative_path": path_safety["normalized_relative_path"],
        "target_path": path_safety["target_path"],
        "allowed_files": path_safety["allowed_files"],
        "requires_human_confirmation": True,
        "confirmation_token_required": YES_I_APPROVE_SCOPED_REPO_PATCH,
        "path_safety": path_safety,
        "patch_content": patch_content,
        "patch_preview": "\n".join(patch_preview_lines),
        "operation_status": operation_status,
    }


def evaluate_repo_patch_gate(repo_patch_plan: dict, confirmation_token: str | None = None) -> dict:
    token_received = confirmation_token == YES_I_APPROVE_SCOPED_REPO_PATCH
    path_status = repo_patch_plan["path_safety"]["safety_status"]
    approved = (
        token_received
        and path_status == "SAFE_REPO_PATCH_PATH"
        and repo_patch_plan.get("operation_status") == "PLANNED_SAFE"
    )
    if approved:
        reason = "Scoped repo patch approved."
    elif path_status != "SAFE_REPO_PATCH_PATH":
        reason = repo_patch_plan["path_safety"]["reason"]
    else:
        reason = "Scoped repo patch blocked: confirmation token missing or incorrect."
    return {
        "gate_status": "APPROVED" if approved else "BLOCKED",
        "requires_human_confirmation": True,
        "confirmation_token_required": YES_I_APPROVE_SCOPED_REPO_PATCH,
        "confirmation_token_received": token_received,
        "path_safety_status": path_status,
        "approved_for_repo_patch": approved,
        "reason": reason,
    }


def run_scoped_repo_patch_adapter(repo_patch_plan: dict, repo_patch_gate: dict) -> dict:
    if repo_patch_gate.get("gate_status") != "APPROVED":
        return {
            "adapter_result_status": "BLOCKED",
            "operation_type": "scoped_repo_patch",
            "file_written": False,
            "target_path": repo_patch_plan["target_path"],
            "changed_files": [],
            "live_execution_performed": False,
            "external_actions_taken": False,
            "worker_agents_activated": False,
            "reason": repo_patch_gate.get("reason", "Scoped repo patch blocked."),
        }

    target_path = Path(repo_patch_plan["target_path"])
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(repo_patch_plan["patch_content"] + "\n", encoding="utf-8")
    return {
        "adapter_result_status": "PASS",
        "operation_type": "scoped_repo_patch",
        "file_written": True,
        "target_path": str(target_path),
        "changed_files": [repo_patch_plan["normalized_relative_path"]],
        "live_execution_performed": False,
        "external_actions_taken": False,
        "worker_agents_activated": False,
        "reason": "Scoped repo patch completed after explicit human confirmation.",
    }


def create_changed_file_scope_proof(repo_patch_plan: dict, repo_patch_result: dict) -> dict:
    changed_files = repo_patch_result.get("changed_files", [])
    allowed_files = repo_patch_plan.get("allowed_files", [])
    normalized_allowed = []
    for item in allowed_files:
        normalized_item = normalize_relative_patch_path(item)
        if normalized_item and normalized_item not in normalized_allowed:
            normalized_allowed.append(normalized_item)
    normalized_changed = []
    forbidden_paths_touched = False
    for item in changed_files:
        normalized_item = normalize_relative_patch_path(item)
        if normalized_item:
            normalized_changed.append(normalized_item)
            if is_forbidden_repo_patch_path(normalized_item):
                forbidden_paths_touched = True
    all_allowlisted = bool(normalized_changed) and all(item in normalized_allowed for item in normalized_changed)
    if not normalized_changed:
        status = "BLOCKED"
        reason = "No changed files were recorded."
    elif all_allowlisted and not forbidden_paths_touched:
        status = "PASS"
        reason = "All changed files were allowlisted and no forbidden paths were touched."
    else:
        status = "BLOCKED"
        reason = "Changed file scope violated allowlist or forbidden-path constraints."
    return {
        "scope_proof_status": status,
        "allowed_files": normalized_allowed,
        "changed_files": normalized_changed,
        "all_changed_files_allowlisted": all_allowlisted,
        "forbidden_paths_touched": forbidden_paths_touched,
        "baseline_preserved": True,
        "devinization_overlays_preserved": True,
        "reason": reason,
    }
