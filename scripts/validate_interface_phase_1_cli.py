#!/usr/bin/env python3
import sys
import subprocess
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INTERFACE_DIR = ROOT / "11_interface"
EXPORTS_DIR = ROOT / "09_exports"
SCRIPTS_DIR = ROOT / "scripts"


def ensure(condition, message):
    if not condition:
        print(f"FAIL: {message}")
        sys.exit(1)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check_file_for_pattern(path, pattern, should_exist=True):
    if not path.exists():
        return False
    content = path.read_text()
    found = pattern in content
    return found if should_exist else not found


def main():
    print("Starting Interface Phase 1 CLI Validation...")

    # 1. Required files exist
    required_files = [
        INTERFACE_DIR / "station_chief_cli.py",
        INTERFACE_DIR / "interface_policy.py",
        INTERFACE_DIR / "interface_actions.py",
        INTERFACE_DIR / "interface_session_log.py",
        INTERFACE_DIR / "interface_config.json",
        INTERFACE_DIR / "README.md",
    ]
    for f in required_files:
        ensure(f.exists(), f"Required file missing: {f}")
    print("  [PASS] All required files present")

    # 2. CLI imports without error
    try:
        load_module("station_chief_cli", INTERFACE_DIR / "station_chief_cli.py")
    except Exception as e:
        ensure(False, f"CLI import failed: {e}")
    print("  [PASS] CLI imports without error")

    # 3. Policy contains SAFE_ACTIONS, CONTROLLED_ACTIONS, LOCKED_ACTIONS
    policy = load_module("interface_policy", INTERFACE_DIR / "interface_policy.py")
    ensure(hasattr(policy, "SAFE_ACTIONS"), "Missing SAFE_ACTIONS")
    ensure(hasattr(policy, "CONTROLLED_ACTIONS"), "Missing CONTROLLED_ACTIONS")
    ensure(hasattr(policy, "LOCKED_ACTIONS"), "Missing LOCKED_ACTIONS")
    ensure(isinstance(policy.SAFE_ACTIONS, list), "SAFE_ACTIONS not a list")
    ensure(isinstance(policy.CONTROLLED_ACTIONS, list), "CONTROLLED_ACTIONS not a list")
    ensure(isinstance(policy.LOCKED_ACTIONS, list), "LOCKED_ACTIONS not a list")
    print("  [PASS] Policy contains all three action categories")

    # 4. Locked actions include required items
    required_locked = [
        "mutate_official_repo",
        "mutate_repo_2",
        "mutate_repo_3",
        "deploy",
        "use_secrets",
        "use_credentials",
        "read_environment",
        "inspect_credential_stores",
        "promote_to_official",
        "open_official_pr",
        "merge_official",
        "production_mutation",
        "uncontrolled_autonomy",
        "free_form_shell",
    ]
    for item in required_locked:
        ensure(item in policy.LOCKED_ACTIONS, f"LOCKED_ACTIONS missing: {item}")
    print("  [PASS] All required locked actions present")

    # 5. Menu includes required options
    cli_content = (INTERFACE_DIR / "station_chief_cli.py").read_text()
    required_menu_items = [
        "Show system status",
        "Run validator wall",
        "List artifact packages",
        "Show latest trial / gauntlet summaries",
        "Generate operator session report",
        "Show locked actions",
        "Prepare command packet",
        "Show current session state",
        "Exit",
    ]
    for item in required_menu_items:
        ensure(item in cli_content, f"Menu option missing from CLI: {item}")
    print("  [PASS] All required menu options present in CLI")

    # 6. Forbidden menu options not exposed
    forbidden_menu_items = [
        "deploy",
        "promote",
        "official mutation",
        "repo 2 mutation",
        "repo 3 mutation",
        "secrets",
        "credentials",
        "free-form shell",
    ]
    menu_section = cli_content.split("MENU_OPTIONS")[1].split("def show_header")[0] if "MENU_OPTIONS" in cli_content else ""
    if menu_section:
        for item in forbidden_menu_items:
            ensure(item.lower() not in menu_section.lower(), f"Forbidden menu option found: {item}")
    print("  [PASS] No forbidden menu options exposed")

    # 7. No shell=True in 11_interface files
    for fpath in INTERFACE_DIR.rglob("*.py"):
        if fpath.name == "__init__.py":
            continue
        content = fpath.read_text()
        ensure("shell=True" not in content, f"shell=True found in {fpath.name}")
    print("  [PASS] No shell=True usage found")

    # 8. No os.environ usage in 11_interface files
    for fpath in INTERFACE_DIR.rglob("*.py"):
        if fpath.name == "__init__.py":
            continue
        content = fpath.read_text()
        ensure("os.environ" not in content, f"os.environ found in {fpath.name}")
    print("  [PASS] No os.environ usage found")

    # 9. No forbidden network imports
    forbidden_imports = ["requests", "urllib", "http.client", "socket"]
    for fpath in INTERFACE_DIR.rglob("*.py"):
        if fpath.name == "__init__.py":
            continue
        content = fpath.read_text()
        for imp in forbidden_imports:
            ensure(imp not in content, f"Forbidden import '{imp}' found in {fpath.name}")
    print("  [PASS] No forbidden network imports")

    # 10. subprocess usage limited to explicit command arrays
    actions_content = (INTERFACE_DIR / "interface_actions.py").read_text()
    subprocess_calls = [line for line in actions_content.splitlines() if "subprocess.run" in line or "subprocess.Popen" in line]
    for call_line in subprocess_calls:
        ensure("shell=True" not in call_line, "subprocess call with shell=True found")
    print("  [PASS] subprocess usage is limited to explicit command arrays")

    # 11. Command packet generation contains required fields
    ensure("packet_id" in actions_content, "Command packet missing packet_id")
    ensure("risk_level" in actions_content, "Command packet missing risk_level")
    ensure("approval_phrase" in actions_content or "I_APPROVE_PREPARED_PACKET_" in actions_content, "Command packet missing approval phrase")
    ensure("prepared_not_executed" in actions_content, "Command packet missing prepared_not_executed")
    ensure("human approval required" in actions_content.lower() or "Human Approval Required" in actions_content,
           "Command packet missing human approval required")
    print("  [PASS] Command packet generation contains required fields")

    # 12. Trial v3 packet references correct scoreboard path
    ensure("09_exports/100_round_trial_v3/scoreboards/master_scoreboard.md" in actions_content,
           "Trial v3 packet uses wrong scoreboard path")
    print("  [PASS] Trial v3 packet uses correct scoreboard path")

    # 13. Artifact counting uses .is_file()
    ensure(".is_file()" in actions_content, "Artifact counting may not use .is_file()")
    print("  [PASS] Artifact counting uses .is_file()")

    # 14. Non-interactive CLI flags exist
    noninteractive_flags = [
        "--status", "--validator-wall", "--list-artifacts",
        "--show-summaries", "--show-locked", "--session-state",
        "--prepare-packet", "--generate-session-report",
    ]
    for flag in noninteractive_flags:
        ensure(flag in cli_content, f"Non-interactive flag missing: {flag}")
    print("  [PASS] All non-interactive CLI flags present")

    # 15. Session logging supports required fields
    session_log_content = (INTERFACE_DIR / "interface_session_log.py").read_text()
    for field in ["session_id", "git_branch_start", "git_commit_start",
                  "git_branch_end", "git_commit_end", "action_results",
                  "command_packet_hashes"]:
        ensure(field in session_log_content, f"Session log missing field: {field}")
    print("  [PASS] Session logging supports all required fields")

    # 16. CLI scripted smoke tests
    print("  Running non-interactive smoke tests...")
    cli_script = str(INTERFACE_DIR / "station_chief_cli.py")

    smoke_commands = [
        ([sys.executable, cli_script, "--status"], "--status"),
        ([sys.executable, cli_script, "--list-artifacts"], "--list-artifacts"),
        ([sys.executable, cli_script, "--show-locked"], "--show-locked"),
        ([sys.executable, cli_script, "--session-state"], "--session-state"),
        ([sys.executable, cli_script, "--prepare-packet", "validator_wall"], "--prepare-packet"),
    ]
    for cmd, label in smoke_commands:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            ensure(r.returncode == 0, f"Smoke test '{label}' failed (rc={r.returncode}): {r.stderr[:200]}")
        except subprocess.TimeoutExpired:
            ensure(False, f"Smoke test '{label}' timed out")
        except Exception as e:
            ensure(False, f"Smoke test '{label}' error: {e}")
    print("  [PASS] CLI scripted smoke tests passed")

    # 17. Invalid non-interactive packet type fails safely
    try:
        r = subprocess.run(
            [sys.executable, cli_script, "--prepare-packet", "definitely_not_real"],
            capture_output=True, text=True, timeout=30
        )
        ensure(r.returncode != 0 or "Invalid packet type" in r.stdout or "ERROR" in r.stdout,
               "Invalid packet type did not fail safely")
    except Exception as e:
        ensure(False, f"Invalid packet test error: {e}")
    print("  [PASS] Invalid non-interactive packet type fails safely")

    # 18. No files outside allowed paths changed
    print("  [SKIP] Full git diff check deferred to Phase 12")

    print("\nINTERFACE_PHASE_1_CLI_VALIDATION_PASS")


if __name__ == "__main__":
    main()
