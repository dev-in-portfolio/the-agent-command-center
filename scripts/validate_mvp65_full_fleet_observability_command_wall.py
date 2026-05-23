import os
import sys

def run_validation():
    print("Validating MVP-65 Full-Fleet Observability Command Wall...")
    
    # 1. Prerequisite
    mvp64_validator = "scripts/validate_mvp64_full_fleet_load_test_failure_recovery.py"
    if not os.path.exists(mvp64_validator):
        print(f"FAILED: Missing {mvp64_validator}")
        return False
    
    if os.system(f"python3 {mvp64_validator} > /dev/null 2>&1") != 0:
        print("FAILED: MVP-64 prerequisite validation failed.")
        return False

    # 2. Check Migration
    migration_file = "supabase/migrations/20260522_mvp65_full_fleet_observability_command_wall.sql"
    if not os.path.exists(migration_file):
        print(f"FAILED: Missing migration {migration_file}")
        return False
        
    with open(migration_file, 'r') as f:
        mig_content = f.read()
        
    tables = [
        "runtime_observability_snapshots",
        "runtime_observability_events",
        "runtime_observability_notes",
        "runtime_observability_state_flags"
    ]
    for tbl in tables:
        if f"CREATE TABLE IF NOT EXISTS {tbl}" not in mig_content:
            print(f"FAILED: Missing table {tbl} in migration")
            return False

    rpcs = [
        "create_full_fleet_observability_snapshot",
        "create_observability_note",
        "export_observability_report"
    ]
    for rpc in rpcs:
        if rpc not in mig_content:
            print(f"FAILED: Missing RPC {rpc} in migration")
            return False
            
    # 3. Check Netlify Functions
    funcs = [
        "full-fleet-observability-snapshot.js",
        "full-fleet-observability-events.js",
        "create-observability-note.js",
        "export-observability-report.js"
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
    ui_file = "13_web_dashboard/dist/demo/observability-command-wall.html"
    if not os.path.exists(ui_file):
        print(f"FAILED: Missing {ui_file}")
        return False
        
    with open(ui_file, 'r') as f:
        ui_content = f.read()
        
    ui_checks = [
        "This wall observes and summarizes the control plane. It does not execute commands.",
        "Status flags are not external alerts.",
        "Rollback status is observed only; no rollback execution occurs here.",
        "Full-fleet observability is not raw activate-all.",
        "Total registered agents: 47,979",
        "Total departments: 1,777",
        "Total units: 5,331",
        "Total families: 175",
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
    if "./observability-command-wall.html" not in demo_content:
        print("FAILED: Missing link to observability-command-wall.html in Demo Hub")
        return False

    print("MVP65_FULL_FLEET_OBSERVABILITY_COMMAND_WALL_VALIDATION_PASS")
    return True

if __name__ == "__main__":
    if not run_validation():
        sys.exit(1)
    sys.exit(0)
