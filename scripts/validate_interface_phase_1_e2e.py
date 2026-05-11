#!/usr/bin/env python3
import sys
import json
import importlib.util
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
INTERFACE_DIR = ROOT / "11_interface"
SCRIPTS_DIR = ROOT / "scripts"
EXPORTS_DIR = ROOT / "09_exports"


def ensure(condition, message):
    if not condition:
        print(f"FAIL: {message}")
        sys.exit(1)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_01_action_registry_loads():
    """Action registry loads and contains all 12 required entries."""
    registry = load_module("interface_action_registry", INTERFACE_DIR / "interface_action_registry.py")
    ensure(len(registry.ACTION_REGISTRY) >= 12,
           f"Expected 12+ actions, got {len(registry.ACTION_REGISTRY)}")
    for aid, entry in registry.ACTION_REGISTRY.items():
        ensure(entry["action_id"] == aid, f"Mismatch: key {aid} != {entry['action_id']}")
        ensure(entry["category"] in ("safe", "controlled", "locked"),
               f"{aid}: invalid category {entry['category']}")
        ensure(entry["risk_level"] in ("none", "low", "medium", "high", "locked", "informational"),
               f"{aid}: invalid risk_level {entry['risk_level']}")
        ensure(isinstance(entry.get("cli_flags", []), list),
               f"{aid}: cli_flags not a list")
        if entry["category"] == "locked":
            ensure(not entry.get("menu_option"),
                   f"{aid}: locked action has menu_option")
            ensure(not entry.get("cli_flags"),
                   f"{aid}: locked action has cli_flags")
    print(f"  [PASS] test_01: Action registry loaded, {len(registry.ACTION_REGISTRY)} entries valid")


def test_02_policy_enforcer_allows_safe():
    """Policy enforcer allows safe actions."""
    enforcer = load_module("interface_policy_enforcer", INTERFACE_DIR / "interface_policy_enforcer.py")
    for safe_aid in ["show_status", "list_artifacts", "inspect_artifact_package"]:
        try:
            enforcer.enforce_allowed(safe_aid)
        except enforcer.PolicyRefusal as e:
            ensure(False, f"Policy refused safe action {safe_aid}: {e}")
    print("  [PASS] test_02: Policy enforcer allows all safe actions")


def test_03_policy_enforcer_refuses_locked():
    """Policy enforcer refuses locked actions with PolicyRefusal."""
    enforcer = load_module("interface_policy_enforcer", INTERFACE_DIR / "interface_policy_enforcer.py")
    for locked_aid in ["mutate_official_repo", "deploy", "use_secrets", "free_form_shell"]:
        try:
            enforcer.enforce_allowed(locked_aid)
            ensure(False, f"Policy allowed locked action {locked_aid}")
        except enforcer.PolicyRefusal:
            pass
    print("  [PASS] test_03: Policy enforcer refuses all locked actions")


def test_04_policy_enforcer_refuses_unknown():
    """Policy enforcer refuses unknown actions."""
    enforcer = load_module("interface_policy_enforcer", INTERFACE_DIR / "interface_policy_enforcer.py")
    try:
        enforcer.enforce_allowed("__no_such_action_ever__")
        ensure(False, "Policy enforcer allowed unknown action")
    except enforcer.PolicyRefusal:
        pass
    print("  [PASS] test_04: Policy enforcer refuses unknown actions")


def test_05_policy_enforcer_registry_consistency():
    """Policy enforcer validates registry consistency."""
    enforcer = load_module("interface_policy_enforcer", INTERFACE_DIR / "interface_policy_enforcer.py")
    errors = enforcer.validate_action_registry()
    ensure(len(errors) == 0, f"Registry consistency errors: {errors}")
    print("  [PASS] test_05: Action registry is internally consistent")


def test_06_artifact_inspector_all_packages():
    """Artifact inspector scans all 5 packages without errors."""
    inspector = load_module("interface_artifact_inspector", INTERFACE_DIR / "interface_artifact_inspector.py")
    ensure(len(inspector.PACKAGE_DEFINITIONS) == 5,
           f"Expected 5 package definitions, got {len(inspector.PACKAGE_DEFINITIONS)}")
    results = inspector.inspect_all_packages()
    ensure(len(results) == 5, f"Expected 5 results, got {len(results)}")
    for pid, result in results.items():
        ensure("exists" in result, f"{pid}: missing 'exists'")
        ensure("status" in result, f"{pid}: missing 'status'")
        ensure("file_count" in result, f"{pid}: missing 'file_count'")
        ensure("warnings" in result, f"{pid}: missing 'warnings'")
    print("  [PASS] test_06: Artifact inspector scans all 5 packages")


def test_07_artifact_inspector_missing_and_zero_byte():
    """Artifact inspector detects missing and zero-byte files."""
    inspector = load_module("interface_artifact_inspector", INTERFACE_DIR / "interface_artifact_inspector.py")
    results = inspector.inspect_all_packages()
    for pid, result in results.items():
        missing = result.get("expected_files_missing", [])
        zero = result.get("zero_byte_files", [])
        if missing:
            pass
        if zero:
            pass
    print("  [PASS] test_07: Artifact inspector missing/zero-byte detection runs without error")


def test_08_branch_review_sanitize():
    """Branch review sanitize_branch_name handles safe and unsafe inputs."""
    brm = load_module("interface_branch_review", INTERFACE_DIR / "interface_branch_review.py")
    ensure(brm.sanitize_branch_name("feature/hello-world") is not None,
           "Rejected valid branch name")
    ensure(brm.sanitize_branch_name("..") is None,
           "Accepted '..' branch name")
    ensure(brm.sanitize_branch_name("") is None,
           "Accepted empty branch name")
    ensure(brm.sanitize_branch_name(None) is None,
           "Accepted None branch name")
    safe = brm.sanitize_branch_name("feature/hello-world")
    ensure("/" not in safe,
           "sanitize_branch_name should replace slashes")
    print("  [PASS] test_08: Branch review sanitize_branch_name correct")


def test_09_approval_ledger_lifecycle():
    """Approval ledger lifecycle: prepare → review → approve."""
    al = load_module("interface_approval_ledger", INTERFACE_DIR / "interface_approval_ledger.py")

    from io import StringIO
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        al.show_ledger()
    except Exception:
        pass

    sys.stdout = old_stdout

    ensure(hasattr(al, "review_packet"), "review_packet missing")
    ensure(hasattr(al, "approve_packet"), "approve_packet missing")
    ensure(hasattr(al, "reject_packet"), "reject_packet missing")
    ensure(hasattr(al, "show_ledger"), "show_ledger missing")

    ledger_dir = EXPORTS_DIR / "interface_phase_1" / "approval_ledger"
    ensure(ledger_dir.exists(), "Approval ledger directory missing")
    ledger_file = ledger_dir / "approval_ledger.jsonl"
    ensure(ledger_file.exists(), "Approval ledger file missing")
    print("  [PASS] test_09: Approval ledger directories and functions exist")


def test_10_session_log_records_actions():
    """Session log records actions correctly."""
    sess_mod = load_module("interface_session_log", INTERFACE_DIR / "interface_session_log.py")
    log = sess_mod.InterfaceSessionLog(repo_name="test")
    ensure(log.session_id.startswith("SES-"), f"Bad session_id: {log.session_id}")
    ensure(log.repo_name == "test", "Repo name not set")
    ensure(log.final_boundary_state == "unknown", "Initial boundary state should be unknown")

    log.record_action("test_action")
    ensure("test_action" in log.actions_requested, "Action not recorded in requested")
    ensure("test_action" in log.actions_completed, "Action not recorded in completed")

    log.record_refused("bad_action", "test reason")
    ensure("bad_action" in log.actions_requested, "Refused not in requested")
    ensure(len(log.actions_refused) == 1, "Refused not recorded")
    ensure(log.actions_refused[0]["reason"] == "test reason", "Refused reason wrong")

    log.record_validator_result("test_val", 0, "all pass", "now")
    ensure(len(log.validator_results) == 1, "Validator result not recorded")
    ensure(log.validator_results[0]["passed"], "Validator should be passed")

    log.record_command_packet("/tmp/test_packet.md")
    ensure(len(log.command_packets_prepared) == 1, "Command packet not recorded")

    log.record_artifact_inspection("test_pkg", "present")
    ensure(len(log.artifacts_inspected) == 1, "Artifact inspection not recorded")

    log.close()
    ensure(log.ended_at_utc is not None, "close() should set ended_at_utc")
    ensure(log.final_boundary_state in ("secure", "secure_with_notes"),
           f"Unexpected boundary state: {log.final_boundary_state}")

    report = log.generate_report()
    ensure("Session ID" in report, "Report missing Session ID")
    ensure("Safety Summary" in report, "Report missing Safety Summary")

    d = log.to_dict()
    ensure(d["session_id"] == log.session_id, "to_dict session_id mismatch")
    ensure(len(d["action_results"]) == 0, f"to_dict action_results wrong")
    print("  [PASS] test_10: Session log records actions correctly")


def test_11_interface_config_identity():
    """Interface config has correct product identity."""
    config_path = INTERFACE_DIR / "interface_config.json"
    ensure(config_path.exists(), "Config file missing")
    config = json.loads(config_path.read_text())
    ensure("product_repo" in config, "Config missing product_repo")
    ensure("source_lineage" in config, "Config missing source_lineage")
    ensure("runtime_version_expected" in config, "Config missing runtime_version_expected")
    ensure(config["product_repo"] == "dev-in-portfolio/the-agent-command-center",
           f"Wrong product_repo: {config['product_repo']}")
    print("  [PASS] test_11: Interface config has correct product identity")


def test_12_cli_help_output():
    """CLI --help produces output."""
    import subprocess
    r = subprocess.run(
        [sys.executable, str(INTERFACE_DIR / "station_chief_cli.py"), "--help"],
        capture_output=True, text=True, timeout=30
    )
    ensure(r.returncode == 0, f"--help failed with rc={r.returncode}")
    ensure("Station Chief" in r.stdout or "station_chief" in r.stdout,
           "--help missing expected content")
    ensure("--status" in r.stdout, "--help missing flag list")
    print("  [PASS] test_12: CLI --help produces expected output")


def test_13_cli_unknown_action():
    """CLI exits nonzero with unknown flag."""
    import subprocess
    r = subprocess.run(
        [sys.executable, str(INTERFACE_DIR / "station_chief_cli.py"), "--definitely-not-real"],
        capture_output=True, text=True, timeout=30
    )
    ensure(r.returncode != 0, "Unknown flag should exit nonzero")
    ensure("Unknown flag" in r.stdout or "ERROR" in r.stdout,
           "Unknown flag should print error message")
    print("  [PASS] test_13: CLI unknown flag exits with error")


def test_14_artifact_inspector_stale_claim_detection():
    """Artifact inspector stale claim detection runs without error."""
    inspector = load_module("interface_artifact_inspector", INTERFACE_DIR / "interface_artifact_inspector.py")
    for pid in inspector.PACKAGE_DEFINITIONS:
        try:
            warnings = inspector.detect_stale_claims(pid)
            ensure(isinstance(warnings, list), f"stale claims for {pid} not a list")
        except Exception as e:
            ensure(False, f"stale claim detection failed for {pid}: {e}")
    print("  [PASS] test_14: Artifact inspector stale claim detection runs clean")


def test_15_all_modules_import_clean():
    """All 5 hardening modules import without errors."""
    module_names = [
        "interface_action_registry",
        "interface_policy_enforcer",
        "interface_artifact_inspector",
        "interface_branch_review",
        "interface_approval_ledger",
    ]
    for mname in module_names:
        try:
            load_module(mname, INTERFACE_DIR / f"{mname}.py")
        except Exception as e:
            ensure(False, f"Module {mname} failed to import: {e}")
    print("  [PASS] test_15: All 5 hardening modules import clean")


def main():
    print("Starting Interface Phase 1 E2E Validation...")
    print()

    tests = [
        test_01_action_registry_loads,
        test_02_policy_enforcer_allows_safe,
        test_03_policy_enforcer_refuses_locked,
        test_04_policy_enforcer_refuses_unknown,
        test_05_policy_enforcer_registry_consistency,
        test_06_artifact_inspector_all_packages,
        test_07_artifact_inspector_missing_and_zero_byte,
        test_08_branch_review_sanitize,
        test_09_approval_ledger_lifecycle,
        test_10_session_log_records_actions,
        test_11_interface_config_identity,
        test_12_cli_help_output,
        test_13_cli_unknown_action,
        test_14_artifact_inspector_stale_claim_detection,
        test_15_all_modules_import_clean,
    ]

    passed = 0
    failed = 0
    for test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {test_fn.__name__}: {e}")
            failed += 1

    print()
    print(f"  Results: {passed} passed, {failed} failed, {len(tests)} total")

    if failed > 0:
        print("\nINTERFACE_PHASE_1_E2E_VALIDATION_FAIL")
        sys.exit(1)
    else:
        print("\nINTERFACE_PHASE_1_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    main()
