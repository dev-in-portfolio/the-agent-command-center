#!/usr/bin/env python3
# MVP45_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT
# MVP45_NO_REAL_AUDIT_EVENT_WRITES_CHECK
# MVP45_NO_REAL_AUDIT_PERSISTENCE_CHECK
# MVP45_NO_DATABASE_WRITES_CHECK
# MVP45_NO_SUPABASE_WRITES_CHECK
# MVP45_NO_PUBLIC_WRITES_CHECK
# MVP45_NO_LIVE_AUDIT_LOGGING_CHECK
# MVP45_NO_AUDIT_EVENT_MUTATION_CHECK
# MVP45_NO_AUDIT_EVENT_DELETION_CHECK
# MVP45_NO_COMMAND_EXECUTION_CHECK
# MVP45_NO_APPROVAL_EXECUTION_CHECK
# MVP45_NO_DEPLOY_MERGE_PUSH_PR_CONTROLS_CHECK
# MVP45_NO_GITHUB_NETLIFY_MUTATION_CHECK
# MVP45_NO_AUTOMATION_CHECK
# MVP45_NO_SERVICE_ROLE_CHECK
# MVP45_NO_SERVICE_ROLE_IN_BROWSER_CHECK
# MVP45_NO_TOKEN_INPUT_CHECK
# MVP45_NO_BROWSER_PERSISTENCE_CHECK
# MVP45_NO_MIGRATION_APPLY_CHECK
# MVP45_IMMUTABLE_AUDIT_EVENT_LEDGER_EXPORT_ARTIFACTS_CHECK
# MVP45_NO_WHOLE_FILE_SAFETY_LABEL_SKIP

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.validation_helpers_control_scan import scan_text_for_dangerous_controls

FAILURES = []

def fail(message: str) -> None:
    FAILURES.append(message)
    print(f"  [FAIL] {message}")

def check(condition: bool, message: str) -> None:
    if not condition:
        fail(message)

def scan_text(path: Path, text: str) -> None:
    findings = scan_text_for_dangerous_controls(str(path.relative_to(ROOT)), text)
    if findings:
        fail(f"{path.relative_to(ROOT)}: {findings}")

def main():
    models = [
        "14_backend/product_runtime/ui_models/immutable_audit_event_ledger_model.json",
        "14_backend/product_runtime/ui_models/audit_event_data_model.json",
        "14_backend/product_runtime/ui_models/append_only_ledger_contract_model.json",
        "14_backend/product_runtime/ui_models/audit_event_taxonomy_model.json",
        "14_backend/product_runtime/ui_models/actor_action_resource_schema_model.json",
        "14_backend/product_runtime/ui_models/before_after_snapshot_blueprint_model.json",
        "14_backend/product_runtime/ui_models/audit_integrity_tamper_resistance_plan_model.json",
        "14_backend/product_runtime/ui_models/audit_retention_export_blueprint_model.json",
    ]
    for model in models:
        check((ROOT / model).exists(), f"missing UI model: {model}")

    reports = [
        "09_exports/mvp_product_track/mvp45_immutable_audit_event_ledger_report.md",
        "09_exports/mvp_product_track/mvp45_audit_event_data_model_report.md",
        "09_exports/mvp_product_track/mvp45_append_only_ledger_contract_report.md",
        "09_exports/mvp_product_track/mvp45_audit_event_taxonomy_report.md",
        "09_exports/mvp_product_track/mvp45_actor_action_resource_schema_report.md",
        "09_exports/mvp_product_track/mvp45_before_after_snapshot_blueprint_report.md",
        "09_exports/mvp_product_track/mvp45_audit_integrity_tamper_resistance_plan_report.md",
        "09_exports/mvp_product_track/mvp45_audit_retention_export_blueprint_report.md",
        "09_exports/mvp_product_track/mvp45_security_boundary_report.md",
        "09_exports/mvp_product_track/mvp45_next_product_step_report.md",
        "09_exports/mvp_product_track/mvp45_validator_quality_report.md",
        "09_exports/mvp_product_track/mvp45_acceptance_report.md",
        "09_exports/mvp_product_track/mvp45_validator_wall_review.md",
        "09_exports/mvp_product_track/mvp45_validation_stewardship_report.md",
    ]
    for rep in reports:
        check((ROOT / rep).exists(), f"missing report: {rep}")

    artifacts = [
        "09_exports/release_package/mvp45_immutable_audit_event_ledger.md",
        "09_exports/release_package/mvp45_audit_event_data_model.md",
        "09_exports/release_package/mvp45_append_only_ledger_contract.md",
        "09_exports/release_package/mvp45_audit_event_taxonomy.md",
        "09_exports/release_package/mvp45_actor_action_resource_schema.md",
        "09_exports/release_package/mvp45_before_after_snapshot_blueprint.md",
        "09_exports/release_package/mvp45_audit_integrity_tamper_resistance_plan.md",
        "09_exports/release_package/mvp45_audit_retention_export_blueprint.md",
        "09_exports/release_package/mvp45_immutable_audit_event_ledger_manifest.json",
    ]
    for artifact in artifacts:
        check((ROOT / artifact).exists(), f"missing artifact: {artifact}")
        
    manifest = ROOT / "09_exports/release_package/mvp45_immutable_audit_event_ledger_manifest.json"
    if manifest.exists():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            check(data.get("name") == "MVP-45 Immutable Audit Event Ledger", "manifest name incorrect")
        except json.JSONDecodeError:
            fail("manifest JSON invalid")

    index_path = ROOT / "13_web_dashboard/dist/index.html"
    if index_path.exists():
        text = index_path.read_text(encoding="utf-8")
        scan_text(index_path, text)
        
        markers = [
            "MVP-45",
            "IMMUTABLE AUDIT EVENT LEDGER",
            "AUDIT EVENT DATA MODEL",
            "APPEND ONLY LEDGER CONTRACT",
            "AUDIT EVENT TAXONOMY",
            "ACTOR ACTION RESOURCE SCHEMA",
            "BEFORE AFTER SNAPSHOT BLUEPRINT",
            "AUDIT INTEGRITY TAMPER RESISTANCE PLAN",
            "AUDIT RETENTION EXPORT BLUEPRINT",
            "AUDIT LEDGER FOUNDATION ONLY",
            "SCHEMA READINESS ONLY",
            "REVIEW ONLY",
            "FUTURE IMPLEMENTATION ONLY",
            "NO REAL AUDIT EVENT WRITES",
            "NO REAL AUDIT PERSISTENCE",
            "NO DATABASE WRITES",
            "NO SUPABASE WRITES",
            "NO PUBLIC WRITES",
            "NO LIVE AUDIT LOGGING",
            "NO AUDIT EVENT MUTATION",
            "NO AUDIT EVENT DELETION",
            "NO COMMAND EXECUTION",
            "NO APPROVAL EXECUTION",
            "NO DEPLOY CONTROLS",
            "NO MERGE CONTROLS",
            "NO PUSH CONTROLS",
            "NO PR CONTROLS",
            "NO GITHUB MUTATION",
            "NO NETLIFY MUTATION",
            "AUTOMATION DISABLED",
            "SERVICE ROLE NOT USED",
            "SERVICE ROLE NOT IN BROWSER",
            "NO TOKEN INPUT",
            "NO BROWSER PERSISTENCE",
            "NO MIGRATION APPLY",
            "NEXT_STEP_BUILD_APPROVAL_GATE_STORAGE",
            "NOT_READY_FOR_REAL_AUTOMATION"
        ]
        for m in markers:
            check(m in text, f"missing dashboard marker: {m}")
            
    acc_report = ROOT / "09_exports/mvp_product_track/mvp45_acceptance_report.md"
    if acc_report.exists():
        text = acc_report.read_text(encoding="utf-8")
        acc_markers = [
            "IMMUTABLE_AUDIT_EVENT_LEDGER_READY",
            "PASS_WITH_AUDIT_LEDGER_FOUNDATION_ONLY"
        ]
        for m in acc_markers:
            check(m in text, f"missing acceptance marker: {m}")
            
    # Check semantic posture
    model_json = ROOT / "14_backend/product_runtime/ui_models/immutable_audit_event_ledger_model.json"
    if model_json.exists():
        data = json.loads(model_json.read_text(encoding="utf-8"))
        check(data.get("immutable_audit_event_ledger_ready") == "true", "expected true")
        check(data.get("audit_ledger_foundation_only") == "true", "expected true")
        check(data.get("schema_readiness_only") == "true", "expected true")
        check(data.get("real_audit_event_writes_enabled") == "false", "expected false")
        check(data.get("real_audit_persistence_enabled") == "false", "expected false")
        check(data.get("database_write_enabled") == "false", "expected false")
        check(data.get("supabase_write_enabled") == "false", "expected false")
        check(data.get("public_write_enabled") == "false", "expected false")
        check(data.get("live_audit_logging_enabled") == "false", "expected false")
        check(data.get("audit_event_mutation_enabled") == "false", "expected false")
        check(data.get("audit_event_deletion_enabled") == "false", "expected false")
        check(data.get("command_execution_enabled") == "false", "expected false")
        check(data.get("approval_execution_enabled") == "false", "expected false")
        check(data.get("deploy_controls_enabled") == "false", "expected false")
        check(data.get("merge_controls_enabled") == "false", "expected false")
        check(data.get("push_controls_enabled") == "false", "expected false")
        check(data.get("pr_controls_enabled") == "false", "expected false")
        check(data.get("github_mutation_enabled") == "false", "expected false")
        check(data.get("netlify_mutation_enabled") == "false", "expected false")
        check(data.get("automation_enabled") == "false", "expected false")
        
    # check no new Netlify functions added compared to origin/master
    added_functions = subprocess.run(
        ["git", "diff", "--name-only", "origin/master..HEAD", "--", "netlify/functions"],
        capture_output=True, text=True, cwd=ROOT
    ).stdout.strip().splitlines()
    check(not any(f.endswith(".js") for f in added_functions), "no new function files added")
    
    if FAILURES:
        print("MVP45_IMMUTABLE_AUDIT_EVENT_LEDGER_VALIDATION_FAIL")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)
        
    print("MVP45_IMMUTABLE_AUDIT_EVENT_LEDGER_VALIDATION_PASS")

if __name__ == "__main__":
    main()
