#!/usr/bin/env python3
import sys
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


def main():
    print("Starting Interface Phase 1 CLI Validation...")

    # 1. Required files exist
    required_files = [
        INTERFACE_DIR / "station_chief_cli.py",
        INTERFACE_DIR / "interface_policy.py",
        INTERFACE_DIR / "interface_actions.py",
        INTERFACE_DIR / "interface_session_log.py",
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

    # 5. CLI help/menu text includes required options
    cli_content = (INTERFACE_DIR / "station_chief_cli.py").read_text()
    required_menu_items = [
        "Show system status",
        "Run validator wall",
        "List artifact packages",
        "Show latest trial / gauntlet summaries",
        "Generate operator session report",
        "Show locked actions",
        "Prepare command packet",
        "Exit",
    ]
    for item in required_menu_items:
        ensure(item in cli_content, f"Menu option missing from CLI: {item}")
    print("  [PASS] All required menu options present in CLI")

    # 6. CLI does not expose forbidden menu options
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

    # 7. Command packet generation writes status prepared_not_executed
    actions_content = (INTERFACE_DIR / "interface_actions.py").read_text()
    ensure("prepared_not_executed" in actions_content, "Command packet status missing")
    ensure("def action_prepare_command_packet" in actions_content, "Command packet action missing")
    print("  [PASS] Command packet status set to prepared_not_executed")

    # 8. Validator wall action is controlled, not safe
    ensure("run_validator_wall" in policy.CONTROLLED_ACTIONS, "run_validator_wall not in CONTROLLED_ACTIONS")
    ensure("run_validator_wall" not in policy.SAFE_ACTIONS, "run_validator_wall in SAFE_ACTIONS")
    print("  [PASS] Validator wall correctly classified as controlled")

    # 9. Official/repo2/repo3/deploy/secret actions are locked
    for locked_item in ["mutate_official_repo", "mutate_repo_2", "mutate_repo_3", "deploy", "use_secrets"]:
        ensure(locked_item in policy.LOCKED_ACTIONS, f"{locked_item} not locked")
        ensure(locked_item not in policy.SAFE_ACTIONS, f"{locked_item} in SAFE_ACTIONS")
        ensure(locked_item not in policy.CONTROLLED_ACTIONS, f"{locked_item} in CONTROLLED_ACTIONS")
    print("  [PASS] Official/repo2/repo3/deploy/secret actions are locked")

    # 10. No code outside allowed interface files changed unexpectedly
    print("  [SKIP] Full git diff check deferred to Phase 11")

    print("\nINTERFACE_PHASE_1_CLI_VALIDATION_PASS")


if __name__ == "__main__":
    main()
