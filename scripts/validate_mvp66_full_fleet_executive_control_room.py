import os
import sys

def run_validation():
    print("Validating MVP-66 Full-Fleet Executive Control Room...")
    
    # 1. Prerequisite
    mvp65_validator = "scripts/validate_mvp65_full_fleet_observability_command_wall.py"
    if not os.path.exists(mvp65_validator):
        print(f"FAILED: Missing {mvp65_validator}")
        return False
    
    if os.system(f"python3 {mvp65_validator} > /dev/null 2>&1") != 0:
        print("FAILED: MVP-65 prerequisite validation failed.")
        return False

    # 2. Check Migration
    migration_file = "supabase/migrations/20260522_mvp66_full_fleet_executive_control_room.sql"
    if not os.path.exists(migration_file):
        print(f"FAILED: Missing migration {migration_file}")
        return False
        
    with open(migration_file, 'r') as f:
        mig_content = f.read()
        
    tables = [
        "runtime_executive_control_room_snapshots",
        "runtime_executive_control_room_notes",
        "runtime_executive_review_questions",
        "runtime_executive_decision_log"
    ]
    for tbl in tables:
        if f"CREATE TABLE IF NOT EXISTS {tbl}" not in mig_content:
            print(f"FAILED: Missing table {tbl} in migration")
            return False

    rpcs = [
        "create_executive_control_room_snapshot",
        "create_executive_control_room_note",
        "export_executive_control_room_report"
    ]
    for rpc in rpcs:
        if rpc not in mig_content:
            print(f"FAILED: Missing RPC {rpc} in migration")
            return False
            
    # 3. Check Netlify Functions
    funcs = [
        "executive-control-room-snapshot.js",
        "executive-control-room-mode.js",
        "create-executive-control-room-note.js",
        "export-executive-control-room-report.js"
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
    ui_file = "13_web_dashboard/dist/demo/executive-control-room.html"
    if not os.path.exists(ui_file):
        print(f"FAILED: Missing {ui_file}")
        return False
        
    with open(ui_file, 'r') as f:
        ui_content = f.read()
        
    ui_checks = [
        "This room summarizes the system for review. It does not execute commands.",
        "Role modes change the explanation, not the underlying facts.",
        "Executive readiness is not runtime permission.",
        "No page in this control room runs shell commands, deploys, rollbacks, alerts, or arbitrary actions.",
        "Total registered agents: 47,979",
        "Total departments: 1,777",
        "Total units: 5,331",
        "Total families: 175",
        "executive", "operator", "security_risk", "technical", "investor_recruiter", "skeptical_reviewer"
    ]
    
    for check in ui_checks:
        if check not in ui_content:
            print(f"FAILED: Missing '{check}' in {ui_file}")
            return False
            
    if "SUPABASE_SERVICE_ROLE_KEY" in ui_content:
         print(f"FAILED: Found SUPABASE_SERVICE_ROLE_KEY in browser UI! This is forbidden.")
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
    if "./executive-control-room.html" not in demo_content:
        print("FAILED: Missing link to executive-control-room.html in Demo Hub")
        return False

    # Root link check
    root_hub = "13_web_dashboard/dist/index.html"
    with open(root_hub, 'r') as f:
        root_content = f.read()
    if "./demo/executive-control-room.html" not in root_content:
        print("FAILED: Missing link to executive-control-room.html in Root Index")
        return False

    print("MVP66_FULL_FLEET_EXECUTIVE_CONTROL_ROOM_VALIDATION_PASS")
    return True

if __name__ == "__main__":
    if not run_validation():
        sys.exit(1)
    sys.exit(0)
