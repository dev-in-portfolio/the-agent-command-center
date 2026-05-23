import os
import sys

def run_validation():
    print("Validating MVP-64 Full-Fleet Load Test, Failure Simulation, and Recovery Drill...")
    
    # 1. Prerequisite
    mvp63_validator = "scripts/validate_mvp63_full_47979_agent_department_gated_runtime_fleet.py"
    if not os.path.exists(mvp63_validator):
        print(f"FAILED: Missing {mvp63_validator}")
        return False
    
    if os.system(f"python3 {mvp63_validator} > /dev/null 2>&1") != 0:
        print("FAILED: MVP-63 prerequisite validation failed.")
        return False

    # 2. Check Migration
    migration_file = "supabase/migrations/20260522_mvp64_full_fleet_load_test_failure_recovery.sql"
    if not os.path.exists(migration_file):
        print(f"FAILED: Missing migration {migration_file}")
        return False
        
    with open(migration_file, 'r') as f:
        mig_content = f.read()
        
    tables = [
        "runtime_fleet_load_tests",
        "runtime_fleet_failure_scenarios",
        "runtime_fleet_recovery_drills",
        "runtime_fleet_load_test_events",
        "runtime_fleet_load_test_rollups",
        "runtime_fleet_load_test_reports"
    ]
    for tbl in tables:
        if f"CREATE TABLE IF NOT EXISTS {tbl}" not in mig_content:
            print(f"FAILED: Missing table {tbl} in migration")
            return False

    scenarios = [
        "heartbeat_drop",
        "department_gate_mismatch",
        "cohort_over_cap_attempt",
        "stage_unlock_failure",
        "circuit_breaker_trigger",
        "recovery_safe_state",
        "audit_gap_detection",
        "readiness_rollup_degraded",
        "continual_harness_degraded",
        "raw_activate_all_attempt_blocked"
    ]
    for scenario in scenarios:
        if scenario not in mig_content:
            print(f"FAILED: Missing failure scenario {scenario} in migration")
            return False

    rpcs = [
        "start_fleet_load_test",
        "pause_fleet_load_test",
        "complete_fleet_load_test",
        "simulate_fleet_failure",
        "trigger_recovery_drill",
        "verify_recovery_drill",
        "export_fleet_load_test_report"
    ]
    for rpc in rpcs:
        if rpc not in mig_content:
            print(f"FAILED: Missing RPC {rpc} in migration")
            return False
            
    # 3. Check Netlify Functions
    funcs = [
        "list-fleet-load-tests.js",
        "start-fleet-load-test.js",
        "pause-fleet-load-test.js",
        "complete-fleet-load-test.js",
        "simulate-fleet-failure.js",
        "trigger-recovery-drill.js",
        "verify-recovery-drill.js",
        "fleet-load-test-rollup.js",
        "export-fleet-load-test-report.js"
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
    ui_file = "13_web_dashboard/dist/demo/full-fleet-load-test.html"
    if not os.path.exists(ui_file):
        print(f"FAILED: Missing {ui_file}")
        return False
        
    with open(ui_file, 'r') as f:
        ui_content = f.read()
        
    ui_checks = [
        "This is a control-plane load test, not raw fleet activation",
        "Failure simulation does not execute destructive actions",
        "Recovery drill verification does not perform rollback execution",
        "Safe-state restoration means the control system returns to a blocked/paused/audited state",
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
                if forb in content:
                    print(f"FAILED: Found forbidden '{forb}' in {func}")
                    return False
                    
    # Demo hub check
    demo_hub = "13_web_dashboard/dist/demo/index.html"
    with open(demo_hub, 'r') as f:
        demo_content = f.read()
    if "./full-fleet-load-test.html" not in demo_content:
        print("FAILED: Missing link to full-fleet-load-test.html in Demo Hub")
        return False

    print("MVP64_FULL_FLEET_LOAD_TEST_FAILURE_RECOVERY_VALIDATION_PASS")
    return True

if __name__ == "__main__":
    if not run_validation():
        sys.exit(1)
    sys.exit(0)
