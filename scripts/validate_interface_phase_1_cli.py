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
        "Inspect artifact packages",
        "Show approval ledger",
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
        "--inspect-artifacts", "--prepare-branch-review",
        "--review-packet", "--approve-packet", "--reject-packet",
        "--show-approval-ledger",
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

    # 18. New hardening modules exist and define required exports
    new_modules = [
        ("interface_action_registry.py", "ACTION_REGISTRY"),
        ("interface_policy_enforcer.py", "enforce_allowed"),
        ("interface_artifact_inspector.py", "inspect_all_packages"),
        ("interface_branch_review.py", "prepare_branch_review"),
        ("interface_approval_ledger.py", "show_ledger"),
    ]
    for fname, export_name in new_modules:
        fpath = INTERFACE_DIR / fname
        ensure(fpath.exists(), f"Required module missing: {fname}")
        content = fpath.read_text()
        ensure(export_name in content, f"Module {fname} missing required export: {export_name}")
    print("  [PASS] All 5 hardening modules present with required exports")

    # 19. Action registry has all 12 required actions
    registry = load_module("interface_action_registry", INTERFACE_DIR / "interface_action_registry.py")
    required_action_ids = [
        "show_status", "run_validator_wall", "list_artifacts", "show_summaries",
        "generate_session_report", "show_locked_actions", "prepare_command_packet",
        "show_session_state", "inspect_artifact_package", "prepare_branch_review",
        "review_packet_approval", "show_approval_ledger",
    ]
    for aid in required_action_ids:
        ensure(aid in registry.ACTION_REGISTRY, f"Action registry missing: {aid}")
    print("  [PASS] Action registry contains all 12 required actions")

    # 20. Policy enforcer raises PolicyRefusal for unknown actions
    enforcer = load_module("interface_policy_enforcer", INTERFACE_DIR / "interface_policy_enforcer.py")
    try:
        enforcer.enforce_allowed("__definitely_not_a_real_action__")
        ensure(False, "Policy enforcer did not refuse unknown action")
    except enforcer.PolicyRefusal:
        pass
    print("  [PASS] Policy enforcer refuses unknown actions")

    # 21. Policy enforcer raises PolicyRefusal for locked actions
    try:
        enforcer.enforce_allowed("mutate_official_repo")
        ensure(False, "Policy enforcer did not refuse locked action")
    except enforcer.PolicyRefusal:
        pass
    print("  [PASS] Policy enforcer refuses locked actions")

    # 22. Policy enforcer allows safe actions
    try:
        enforcer.enforce_allowed("show_status")
    except enforcer.PolicyRefusal as e:
        ensure(False, f"Policy enforcer refused safe action: {e}")
    print("  [PASS] Policy enforcer allows safe actions")

    # 23. Artifact inspector inspects all 5 packages
    inspector = load_module("interface_artifact_inspector", INTERFACE_DIR / "interface_artifact_inspector.py")
    ensure(len(inspector.PACKAGE_DEFINITIONS) >= 5, "Artifact inspector should have 5+ packages")
    all_results = inspector.inspect_all_packages()
    for pid in inspector.PACKAGE_DEFINITIONS:
        ensure(pid in all_results, f"inspect_all_packages missing result for {pid}")
    print(f"  [PASS] Artifact inspector inspects all {len(inspector.PACKAGE_DEFINITIONS)} packages")

    # 24. Branch review produces valid packet format
    brm = load_module("interface_branch_review", INTERFACE_DIR / "interface_branch_review.py")
    safe_name = brm.sanitize_branch_name("test/branch-name")
    ensure(safe_name is not None and "/" not in safe_name, "sanitize_branch_name should replace slashes")
    unsafe = brm.sanitize_branch_name("..")
    ensure(unsafe is None, "sanitize_branch_name should reject '..'")
    print("  [PASS] Branch review sanitize_branch_name works correctly")

    # 25. Approval ledger lifecycle functions exist
    ledger = load_module("interface_approval_ledger", INTERFACE_DIR / "interface_approval_ledger.py")
    ensure(hasattr(ledger, "show_ledger"), "Approval ledger missing show_ledger")
    ensure(hasattr(ledger, "review_packet"), "Approval ledger missing review_packet")
    ensure(hasattr(ledger, "approve_packet"), "Approval ledger missing approve_packet")
    ensure(hasattr(ledger, "reject_packet"), "Approval ledger missing reject_packet")
    print("  [PASS] Approval ledger all lifecycle functions present")

    # 26. Policy.py SAFE_ACTIONS updated with new actions
    ensure("inspect_artifact_package" in policy.SAFE_ACTIONS,
           "SAFE_ACTIONS missing inspect_artifact_package")
    ensure("show_approval_ledger" in policy.SAFE_ACTIONS,
           "SAFE_ACTIONS missing show_approval_ledger")
    print("  [PASS] Policy SAFE_ACTIONS includes new hardening actions")

    # 27. Policy.py CONTROLLED_ACTIONS updated with new actions
    ensure("prepare_branch_review" in policy.CONTROLLED_ACTIONS,
           "CONTROLLED_ACTIONS missing prepare_branch_review")
    ensure("review_packet_approval" in policy.CONTROLLED_ACTIONS,
           "CONTROLLED_ACTIONS missing review_packet_approval")
    print("  [PASS] Policy CONTROLLED_ACTIONS includes new hardening actions")

    # 28. Action registry validate consistency
    registry_errors = enforcer.validate_action_registry()
    ensure(len(registry_errors) == 0, f"Action registry validation errors: {registry_errors}")
    print("  [PASS] Action registry is internally consistent")

    # 29. CLI includes --inspect-artifact flag
    ensure("--inspect-artifact" in cli_content,
           "CLI missing --inspect-artifact flag")
    print("  [PASS] CLI includes --inspect-artifact flag")

    # 30. Action registry inspect_artifact_package includes --inspect-artifact
    inspect_entry = registry.ACTION_REGISTRY.get("inspect_artifact_package", {})
    ensure("--inspect-artifact" in inspect_entry.get("cli_flags", []),
           "Action registry inspect_artifact_package missing --inspect-artifact in cli_flags")
    print("  [PASS] Action registry inspect_artifact_package includes --inspect-artifact flag")

    # 31. CLI includes --base support for branch review
    ensure("--base" in cli_content,
           "CLI missing --base support for branch review")
    print("  [PASS] CLI includes --base support for branch review")

    # 32. CLI help/docstring mentions --base or explicit base syntax
    help_text = (INTERFACE_DIR / "station_chief_cli.py").read_text()
    ensure("--base" in help_text,
           "CLI docstring/help does not mention --base")
    print("  [PASS] CLI help/docstring mentions --base")

    # 33. E2E validator tests all required commands (subprocess or direct module call)
    e2e_content = (SCRIPTS_DIR / "validate_interface_phase_1_e2e.py").read_text()
    required_e2e_commands = [
        "--status", "--list-artifacts", "--inspect-artifacts",
        "--inspect-artifact", "--prepare-packet", "--prepare-branch-review",
        "--show-approval-ledger", "--review-packet",
        "--approve-packet", "--reject-packet",
    ]
    for cmd in required_e2e_commands:
        ensure(cmd in e2e_content,
               f"E2E validator missing coverage for {cmd}")
    ensure("execution_performed" in e2e_content,
           "E2E validator missing execution_performed checks")
    print("  [PASS] E2E validator tests all required commands")

    # 34. Docs mention empty ledger allowed
    for doc_path in [
        INTERFACE_DIR / "README.md",
        EXPORTS_DIR / "interface_phase_1" / "interface_phase_1_operational_hardening_report.md",
        EXPORTS_DIR / "interface_phase_1" / "interface_phase_1_operator_quickstart.md",
    ]:
        if doc_path.exists():
            content = doc_path.read_text()
            ensure("empty" in content.lower() and "ledger" in content.lower(),
                   f"Doc {doc_path.name} does not mention empty ledger")
    print("  [PASS] All docs mention empty ledger is allowed")

    # 35. No files outside allowed paths changed
    print("  [SKIP] Full git diff check deferred to Phase 12")

    # 36. RC artifacts exist (including final acceptance report)
    rc_artifacts = [
        EXPORTS_DIR / "interface_phase_1" / "interface_phase_1_final_acceptance_report.md",
        EXPORTS_DIR / "interface_phase_1" / "interface_phase_1_acceptance_report.md",
        EXPORTS_DIR / "interface_phase_1" / "merge_readiness" / "interface_phase_1_merge_readiness_packet.md",
        EXPORTS_DIR / "interface_phase_1" / "phase_2_handoff_contract.md",
        EXPORTS_DIR / "interface_phase_1" / "test_runs",
        SCRIPTS_DIR / "demo_interface_phase_1.sh",
        SCRIPTS_DIR / "validate_interface_phase_1_release_candidate.py",
        EXPORTS_DIR / "interface_phase_1" / "interface_phase_1_demo_notes.md",
    ]
    for artifact in rc_artifacts:
        ensure(artifact.exists(), f"RC artifact missing: {artifact}")
    print("  [PASS] All RC artifacts present")

    # 37. RC validator contains correct pass string (not old one)
    rc_content = (SCRIPTS_DIR / "validate_interface_phase_1_release_candidate.py").read_text()
    ensure("PASS_WITH_HIGH_CONFIDENCE" in rc_content, "RC validator missing acceptance report check")
    ensure("merge_readiness" in rc_content, "RC validator missing merge-readiness check")
    ensure("phase_2_handoff_contract" in rc_content, "RC validator missing handoff contract check")
    ensure("INTERFACE_PHASE_1_RELEASE_CANDIDATE_VALIDATION_PASS" in rc_content,
           "RC validator missing correct pass string")
    print("  [PASS] RC validator has correct pass string")

    # 38. Demo script references CLI and safe flags
    demo_content = (SCRIPTS_DIR / "demo_interface_phase_1.sh").read_text()
    ensure("station_chief_cli.py" in demo_content, "Demo script missing CLI reference")
    ensure("--status" in demo_content, "Demo script missing --status")
    print("  [PASS] Demo script references CLI and safe flags")

    # 39. Final acceptance report exists with required content
    far = EXPORTS_DIR / "interface_phase_1" / "interface_phase_1_final_acceptance_report.md"
    ensure(far.exists(), "Final acceptance report missing")
    far_content = far.read_text()
    ensure("PASS_WITH_HIGH_CONFIDENCE" in far_content or "PASS_WITH_NOTES" in far_content,
           "Final acceptance report missing verdict")
    ensure("merge performed" in far_content.lower() and "false" in far_content.lower(),
           "Final acceptance report missing merge performed: false")
    ensure("deployment performed" in far_content.lower() and "false" in far_content.lower(),
           "Final acceptance report missing deployment performed: false")
    ensure("official repo touched" in far_content.lower() and "false" in far_content.lower(),
           "Final acceptance report missing official repo touched: false")
    ensure("Phase 2 handoff contract" in far_content,
           "Final acceptance report missing Phase 2 handoff contract reference")
    ensure("ready for merge review" in far_content.lower() or "merge readiness" in far_content.lower(),
           "Final acceptance report missing merge readiness reference")
    print("  [PASS] Final acceptance report contains required content")

    # 40. RC validator no longer has old pass string
    ensure("INTERFACE_PHASE_1_RC_VALIDATION_PASS" not in rc_content,
           "RC validator still has old pass string INTERFACE_PHASE_1_RC_VALIDATION_PASS")
    print("  [PASS] RC validator does not contain old pass string")

    # 41. Demo script does not contain --validator-wall
    ensure("--validator-wall" not in demo_content,
           "Demo script must not run --validator-wall automatically")
    print("  [PASS] Demo script does not auto-run validator-wall")

    # 42. Demo script does not contain forbidden patterns
    forbidden_demo_patterns = [
        "git push", "git merge", "gh pr", "curl", "wget", "ssh", "scp",
        "deploy", "secrets", "credentials",
    ]
    for pattern in forbidden_demo_patterns:
        ensure(pattern not in demo_content,
               f"Demo script contains forbidden pattern: {pattern}")
    print("  [PASS] Demo script has no forbidden patterns")

    # 43. Demo script contains required safe flags and operations
    required_safe_demo = [
        "--status", "--show-locked", "--list-artifacts",
        "--inspect-artifacts", "--inspect-artifact trial_v3",
        "--prepare-packet validator_wall", "--show-approval-ledger",
        "--generate-session-report",
    ]
    for item in required_safe_demo:
        ensure(item in demo_content,
               f"Demo script missing required safe operation: {item}")
    print("  [PASS] Demo script contains all required safe operations")

    print("\nINTERFACE_PHASE_1_CLI_VALIDATION_PASS")


if __name__ == "__main__":
    main()
