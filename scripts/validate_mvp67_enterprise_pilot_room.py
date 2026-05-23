import os
import sys

def run_validation():
    print("Validating MVP-67 Enterprise Pilot Room...")
    
    # 1. Prerequisite
    mvp66_validator = "scripts/validate_mvp66_full_fleet_executive_control_room.py"
    if not os.path.exists(mvp66_validator):
        print(f"FAILED: Missing {mvp66_validator}")
        return False
    
    if os.system(f"python3 {mvp66_validator} > /dev/null 2>&1") != 0:
        print("FAILED: MVP-66 prerequisite validation failed.")
        return False

    # 2. Check Migration
    migration_file = "supabase/migrations/20260522_mvp67_enterprise_pilot_room.sql"
    if not os.path.exists(migration_file):
        print(f"FAILED: Missing migration {migration_file}")
        return False
        
    with open(migration_file, 'r') as f:
        mig_content = f.read()
        
    tables = [
        "enterprise_pilot_snapshots",
        "enterprise_pilot_stakeholder_roles",
        "enterprise_pilot_success_criteria",
        "enterprise_pilot_risk_register",
        "enterprise_pilot_review_notes",
        "enterprise_pilot_decision_log"
    ]
    for tbl in tables:
        if f"CREATE TABLE IF NOT EXISTS {tbl}" not in mig_content:
            print(f"FAILED: Missing table {tbl} in migration")
            return False

    rpcs = [
        "create_enterprise_pilot_snapshot",
        "create_enterprise_pilot_note",
        "create_enterprise_pilot_decision",
        "export_enterprise_pilot_report"
    ]
    for rpc in rpcs:
        if rpc not in mig_content:
            print(f"FAILED: Missing RPC {rpc} in migration")
            return False
            
    # 3. Check Netlify Functions
    funcs = [
        "enterprise-pilot-room-snapshot.js",
        "enterprise-pilot-room-package.js",
        "create-enterprise-pilot-note.js",
        "create-enterprise-pilot-decision.js",
        "export-enterprise-pilot-report.js"
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
    ui_file = "13_web_dashboard/dist/demo/enterprise-pilot-room.html"
    if not os.path.exists(ui_file):
        print(f"FAILED: Missing {ui_file}")
        return False
        
    with open(ui_file, 'r') as f:
        ui_content = f.read()
        
    ui_checks = [
        "This room prepares an enterprise pilot review. It does not grant runtime permission.",
        "Pilot approval is not command execution.",
        "Limited pilot approval does not activate the full fleet.",
        "Any future runtime authorization must be explicit, scoped, logged, and separately approved.",
        "No page in this pilot room runs shell commands, deploys, rollbacks, alerts, or arbitrary actions.",
        "Total registered agents: 47,979",
        "Total departments: 1,777",
        "Total units: 5,331",
        "Total families: 175",
        "pilot_runtime_permission_granted",
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
    if "./enterprise-pilot-room.html" not in demo_content:
        print("FAILED: Missing link to enterprise-pilot-room.html in Demo Hub")
        return False

    # Root link check
    root_hub = "13_web_dashboard/dist/index.html"
    with open(root_hub, 'r') as f:
        root_content = f.read()
    if "./demo/enterprise-pilot-room.html" not in root_content:
        print("FAILED: Missing link to enterprise-pilot-room.html in Root Index")
        return False

    print("MVP67_ENTERPRISE_PILOT_ROOM_VALIDATION_PASS")
    return True

if __name__ == "__main__":
    if not run_validation():
        sys.exit(1)
    sys.exit(0)
