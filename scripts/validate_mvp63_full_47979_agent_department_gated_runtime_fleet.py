import os
import sys

def run_validation():
    print("Validating MVP-63 Full 47,979-Agent Department-Gated Runtime Fleet...")
    
    # 1. Prerequisite
    mvp62_validator = "scripts/validate_mvp62_20000_agent_department_gated_runtime_army.py"
    if not os.path.exists(mvp62_validator):
        print(f"FAILED: Missing {mvp62_validator}")
        return False
    
    if os.system(f"python3 {mvp62_validator} > /dev/null 2>&1") != 0:
        print("FAILED: MVP-62 prerequisite validation failed.")
        return False

    # 2. Check Migration
    migration_file = "supabase/migrations/20260522_mvp63_full_47979_agent_department_gated_runtime_fleet.sql"
    if not os.path.exists(migration_file):
        print(f"FAILED: Missing migration {migration_file}")
        return False
        
    with open(migration_file, 'r') as f:
        mig_content = f.read()
        
    tables = [
        "runtime_fleet_limits",
        "runtime_fleet_stages",
        "runtime_fleet_cohorts",
        "runtime_fleet_circuit_breakers",
        "runtime_fleet_health_rollups",
        "runtime_fleet_department_coverage",
        "runtime_fleet_events"
    ]
    for tbl in tables:
        if f"CREATE TABLE IF NOT EXISTS {tbl}" not in mig_content:
            print(f"FAILED: Missing table {tbl} in migration")
            return False

    checks = [
        "mvp63_global_live_agent_cap",
        "47979",
        "max_cohort_activation_size",
        "2500",
        "max_operation_chunk_size",
        "500",
        "staged_activation_required",
        "circuit_breaker_required",
        "department_gated_activation_required",
        "continual_harness_supervision_required",
        "raw_activate_all_route_enabled",
        "command_execution_enabled",
        "deploy_execution_enabled",
        "rollback_execution_enabled",
        "alert_sending_enabled",
        "arbitrary_shell_execution_enabled",
        "unlock_runtime_fleet_stage",
        "activate_runtime_fleet_cohort",
        "deactivate_runtime_fleet_cohort",
        "activate_approved_department_fleet_cohort",
        "deactivate_approved_department_fleet_cohort",
        "trigger_runtime_fleet_circuit_breaker",
        "clear_runtime_fleet_circuit_breaker",
        "runtime_fleet_kill_switch",
        "stage_1_5000",
        "stage_2_10000",
        "stage_3_20000",
        "stage_4_30000",
        "stage_5_40000",
        "stage_6_47979",
        "1777",
        "5331",
        "175"
    ]
    for check in checks:
        if check not in mig_content:
            print(f"FAILED: Missing {check} in migration")
            return False
            
    # 3. Check Netlify Functions
    funcs = [
        "list-runtime-fleet.js",
        "unlock-runtime-fleet-stage.js",
        "activate-runtime-fleet-cohort.js",
        "deactivate-runtime-fleet-cohort.js",
        "activate-approved-department-fleet-cohort.js",
        "deactivate-approved-department-fleet-cohort.js",
        "runtime-fleet-heartbeat.js",
        "create-runtime-fleet-readiness-note.js",
        "runtime-fleet-circuit-breaker.js",
        "runtime-fleet-rollup.js",
        "runtime-fleet-kill-switch.js"
    ]
    for func in funcs:
        p = f"netlify/functions/{func}"
        if not os.path.exists(p):
            print(f"FAILED: Missing {p}")
            return False
        with open(p, 'r') as f:
            content = f.read()
            if "SUPABASE_SERVICE_ROLE_KEY" not in content:
                print(f"FAILED: Missing service role key in {func}")
                return False

    # 4. Check UI
    ui_file = "13_web_dashboard/dist/demo/runtime-fleet.html"
    if not os.path.exists(ui_file):
        print(f"FAILED: Missing {ui_file}")
        return False
        
    with open(ui_file, 'r') as f:
        ui_content = f.read()
        
    ui_checks = [
        "47,979 is the full fleet cap, not an automatic startup target",
        "Department-gated activation is required",
        "Staged unlocks are required",
        "Raw activate all is disabled",
        "Circuit breakers pause further activation",
        "The kill switch pauses runtime activation; it does not execute rollback commands",
        "Total registered agents",
        "Total departments",
        "Total units",
        "Total families",
        "SUPABASE_SERVICE_ROLE_KEY"
    ]
    
    for check in ui_checks:
        if check == "SUPABASE_SERVICE_ROLE_KEY":
            if check in ui_content:
                print(f"FAILED: Found {check} in browser UI! This is forbidden.")
                return False
        else:
            if check not in ui_content:
                print(f"FAILED: Missing '{check}' in {ui_file}")
                return False
                
    # Check for forbidden routes and configs
    forbidden = [
        "activate-all",
        "activate-all-departments",
        "activate-47979",
        "child_process",
        "exec(",
        "spawn(",
        "eval(",
        "new Function"
    ]
    for func in funcs:
        with open(f"netlify/functions/{func}", 'r') as f:
            content = f.read()
            for forb in forbidden:
                if (forb in content) and ("activate-all" not in forb or ("activate-all" in forb and "raw_activate_all_route_enabled" not in content)):
                    print(f"FAILED: Found forbidden '{forb}' in {func}")
                    return False
                    
    # Demo hub check
    demo_hub = "13_web_dashboard/dist/demo/index.html"
    with open(demo_hub, 'r') as f:
        demo_content = f.read()
    if "./runtime-fleet.html" not in demo_content:
        print("FAILED: Missing link to runtime-fleet.html in Demo Hub")
        return False

    print("MVP63_FULL_47979_AGENT_DEPARTMENT_GATED_RUNTIME_FLEET_VALIDATION_PASS")
    return True

if __name__ == "__main__":
    if not run_validation():
        sys.exit(1)
    sys.exit(0)
