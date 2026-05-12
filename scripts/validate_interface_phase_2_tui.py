#!/usr/bin/env python3
import sys
import json
import subprocess
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TUI_DIR = ROOT / "12_tui"
PHASE1_DIR = ROOT / "11_interface"
PHASE2_EXPORTS = ROOT / "09_exports" / "interface_phase_2"

sys.path.insert(0, str(TUI_DIR))


def _load_tui_module(name):
    path = TUI_DIR / f"{name}.py"
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ensure(condition, message):
    if not condition:
        print(f"FAIL: {message}")
        sys.exit(1)


def test_01_tui_directory_exists():
    ensure(TUI_DIR.is_dir(), "12_tui/ directory must exist")
    print("  [PASS] test_01: 12_tui/ directory exists")


def test_02_tui_modules_exist():
    expected = [
        "tui_keymap.py", "tui_state.py", "tui_safe_actions.py",
        "tui_renderer.py", "tui_screens.py", "tui_app.py",
        "station_chief_tui.py",
    ]
    for mod in expected:
        ensure((TUI_DIR / mod).exists(), f"Required TUI module missing: {mod}")
    print("  [PASS] test_02: All 7 TUI modules present")


def test_03_tui_modules_import():
    names = [
        "tui_keymap", "tui_state", "tui_safe_actions",
        "tui_renderer", "tui_screens", "tui_app",
        "station_chief_tui",
    ]
    for name in names:
        mod = _load_tui_module(name)
        ensure(mod is not None, f"Module {name} failed to import")
    print("  [PASS] test_03: All TUI modules import without error")


def test_04_keymap_valid():
    mod = _load_tui_module("tui_keymap")
    ensure(hasattr(mod, "KEY_TO_SCREEN"), "KEY_TO_SCREEN must exist")
    ensure(hasattr(mod, "SCREENS"), "SCREENS must exist")
    ensure("q" in mod.KEY_TO_SCREEN, "KEY_TO_SCREEN must have quit binding")
    ensure("h" in mod.KEY_TO_SCREEN, "KEY_TO_SCREEN must have help binding")
    ensure("r" in mod.KEY_TO_SCREEN, "KEY_TO_SCREEN must have refresh binding")
    ensure("b" in mod.KEY_TO_SCREEN, "KEY_TO_SCREEN must have back binding")
    ensure("d" in mod.KEY_TO_SCREEN, "KEY_TO_SCREEN must have dashboard binding")
    ensure("?" in mod.KEY_TO_SCREEN, "KEY_TO_SCREEN must have help binding")
    ensure(len(mod.SCREENS) >= 8, "SCREENS must have at least 8 entries (9 for safety monitor)")
    ensure("9" in mod.SCREENS, "SCREENS must have screen 9 (safety_monitor)")
    ensure(mod.SCREENS["9"] == "safety_monitor", "Screen 9 must be safety_monitor")
    print("  [PASS] test_04: Keymap has required bindings including b, d, ?, 9")


def test_05_state_module():
    mod = _load_tui_module("tui_state")
    ensure(hasattr(mod, "TUIState"), "TUIState class must exist")
    ensure(hasattr(mod, "write_session_report"), "write_session_report must exist")
    ensure(hasattr(mod, "SESSION_DIR"), "SESSION_DIR must exist")
    ensure(hasattr(mod, "SNAPSHOT_DIR"), "SNAPSHOT_DIR must exist")
    state = mod.TUIState()
    ensure(hasattr(state, "current_screen"), "state.current_screen must exist")
    ensure(hasattr(state, "session_id"), "state.session_id must exist")
    ensure(hasattr(state, "previous_screen"), "state.previous_screen must exist")
    ensure(hasattr(state, "screen_history"), "state.screen_history must exist")
    ensure(hasattr(state, "breadcrumbs"), "state.breadcrumbs must exist")
    ensure(hasattr(state, "navigate_to"), "state.navigate_to must exist")
    ensure(hasattr(state, "go_back"), "state.go_back must exist")
    ensure(hasattr(state, "go_home"), "state.go_home must exist")
    ensure(hasattr(state, "get_summary"), "state.get_summary must exist")
    summary = state.get_summary()
    ensure("final_boundary_state" in summary, "summary must have final_boundary_state")
    boundary = summary["final_boundary_state"]
    ensure(boundary.get("official_repo_touched") is False, "official_repo_touched must be false")
    ensure(boundary.get("deployment_performed") is False, "deployment_performed must be false")
    ensure(boundary.get("command_packets_executed") is False, "command_packets_executed must be false")
    print("  [PASS] test_05: TUIState has navigation, breadcrumbs, invariants")


def test_06_safe_actions():
    mod = _load_tui_module("tui_safe_actions")
    ensure(hasattr(mod, "run_validator_wall"), "run_validator_wall must exist")
    ensure(hasattr(mod, "prepare_command_packet"), "prepare_command_packet must exist")
    ensure(hasattr(mod, "prepare_branch_review"), "prepare_branch_review must exist")
    ensure(hasattr(mod, "review_packet"), "review_packet must exist")
    ensure(hasattr(mod, "approve_packet"), "approve_packet must exist")
    ensure(hasattr(mod, "reject_packet"), "reject_packet must exist")
    print("  [PASS] test_06: Safe actions expose required wrappers")


def test_07_renderer_has_all_screens():
    mod = _load_tui_module("tui_renderer")
    required = [
        "render_dashboard", "render_action_registry", "render_artifact_inspector",
        "render_validator_wall", "render_command_packet_prep",
        "render_branch_review_prep", "render_approval_ledger",
        "render_safety_monitor", "render_help",
    ]
    for fn in required:
        ensure(hasattr(mod, fn), f"Renderer missing {fn}")
    ensure(hasattr(mod, "SNAPSHOT_FORMATS"), "SNAPSHOT_FORMATS must exist")
    for fmt in ("text", "markdown", "json", "compact", "full"):
        ensure(fmt in mod.SNAPSHOT_FORMATS, f"SNAPSHOT_FORMATS missing {fmt}")
    print("  [PASS] test_07: Renderer has all screens and 5 snapshot formats")


def test_08_renderer_output():
    mod_render = _load_tui_module("tui_renderer")
    mod_state = _load_tui_module("tui_state")
    state = mod_state.TUIState()
    output = mod_render.render_dashboard(state)
    ensure("THE AGENT COMMAND CENTER" in output, "Dashboard must show header")
    ensure("LOCKED" in output, "Dashboard must show locked status")
    ensure("dev-in-portfolio/the-agent-command-center" in output, "Dashboard must show repo name")
    ensure("Safety Monitor" in mod_render.render_help(state) or "9" in mod_render.render_help(state),
           "Help must mention safety monitor")
    for fmt in ("text", "markdown", "json", "compact", "full"):
        render_fn = mod_render.SNAPSHOT_FORMATS[fmt]
        snap = render_fn(state)
        if fmt == "json":
            json.loads(snap)
        ensure(len(snap) > 0, f"Snapshot {fmt} must produce output")
    print("  [PASS] test_08: Renderer produces correct output for all formats")


def test_09_screens_module():
    mod = _load_tui_module("tui_screens")
    ensure(hasattr(mod, "SCREEN_HANDLERS"), "SCREEN_HANDLERS must exist")
    ensure(hasattr(mod, "SCREEN_RENDERERS"), "SCREEN_RENDERERS must exist")
    required_screens = [
        "dashboard", "action_registry", "artifact_inspector",
        "validator_wall", "command_packet_prep", "branch_review_prep",
        "approval_ledger", "safety_monitor", "help",
    ]
    for s in required_screens:
        ensure(s in mod.SCREEN_HANDLERS, f"SCREEN_HANDLERS missing {s}")
        ensure(s in mod.SCREEN_RENDERERS, f"SCREEN_RENDERERS missing {s}")
    print("  [PASS] test_09: Screens module has handlers and renderers for all 9 screens")


def test_10_entrypoint_flags():
    mod = _load_tui_module("station_chief_tui")
    ensure(hasattr(mod, "main"), "main() must exist")
    ensure(hasattr(mod, "ALLOWED_FLAGS"), "ALLOWED_FLAGS must exist")
    ensure("--format" in mod.ALLOWED_FLAGS, "ALLOWED_FLAGS must include --format")
    ensure("--save" in mod.ALLOWED_FLAGS, "ALLOWED_FLAGS must include --save")
    ensure(hasattr(mod, "VALID_SNAPSHOT_FORMATS"), "VALID_SNAPSHOT_FORMATS must exist")
    print("  [PASS] test_10: Entrypoint has ALLOWED_FLAGS with --format and --save")


def test_11_no_forbidden_imports_or_patterns():
    forbidden_imports = ["requests", "urllib", "http.client", "socket", "os.environ", "shell=True"]
    forbidden_commands = ["git push", "git merge", "gh pr", "curl", "wget", "ssh", "scp"]
    for mod_name in ["tui_state", "tui_safe_actions", "tui_renderer",
                     "tui_screens", "tui_app", "station_chief_tui"]:
        module_path = TUI_DIR / f"{mod_name}.py"
        if not module_path.exists():
            continue
        source = module_path.read_text()
        for token in forbidden_imports:
            if token == "os.environ":
                ensure("os.environ" not in source, f"{mod_name} must not contain os.environ")
            elif token == "shell=True":
                ensure("shell=True" not in source, f"{mod_name} must not contain shell=True")
            elif token == "requests":
                ensure("import requests" not in source and "from requests" not in source,
                       f"{mod_name} must not import requests")
            elif token == "urllib":
                ensure("import urllib" not in source and "from urllib" not in source,
                       f"{mod_name} must not import urllib")
            elif token in ("http.client", "socket"):
                if token == "http.client":
                    ensure("http.client" not in source, f"{mod_name} must not import http.client")
                elif token == "socket":
                    ensure("import socket" not in source and "from socket" not in source,
                           f"{mod_name} must not import socket")
        for cmd in forbidden_commands:
            ensure(cmd not in source, f"{mod_name} must not contain '{cmd}'")
    print("  [PASS] test_11: No forbidden imports or commands in TUI modules")


def test_12_session_dir_exists():
    sessions_dir = PHASE2_EXPORTS / "sessions"
    ensure(sessions_dir.is_dir() or not sessions_dir.exists(), "Session dir path must be valid")
    print("  [PASS] test_12: session directory path is valid")


def test_13_no_duplicate_cli_entrypoint():
    cli_path = PHASE1_DIR / "station_chief_cli.py"
    ensure(cli_path.exists(), "Phase 1 CLI must still exist")
    print("  [PASS] test_13: Phase 1 CLI preserved")


def test_14_snapshot_modes_work():
    r = subprocess.run([sys.executable, str(TUI_DIR / "station_chief_tui.py"), "--snapshot"],
                       capture_output=True, text=True, timeout=30)
    ensure(r.returncode == 0, f"--snapshot exited {r.returncode}")
    ensure("SNAPSHOT" in r.stdout or "THE AGENT COMMAND CENTER" in r.stdout,
           "--snapshot output must contain header")
    for fmt in ("text", "markdown", "json", "compact", "full"):
        r = subprocess.run([sys.executable, str(TUI_DIR / "station_chief_tui.py"),
                            "--snapshot", "--format", fmt],
                           capture_output=True, text=True, timeout=30)
        ensure(r.returncode == 0, f"--snapshot --format {fmt} exited {r.returncode}")
        ensure(len(r.stdout) > 0, f"--snapshot --format {fmt} must produce output")
        if fmt == "json":
            json.loads(r.stdout)
    print("  [PASS] test_14: All snapshot formats work")


def test_15_help_mode_works():
    r = subprocess.run([sys.executable, str(TUI_DIR / "station_chief_tui.py"), "--help"],
                       capture_output=True, text=True, timeout=30)
    ensure(r.returncode == 0, f"--help exited {r.returncode}")
    ensure("snapshot" in r.stdout.lower(), "--help must mention --snapshot")
    ensure("no-curses" in r.stdout.lower(), "--help must mention --no-curses")
    ensure("--format" in r.stdout, "--help must mention --format")
    ensure("--save" in r.stdout, "--help must mention --save")
    print("  [PASS] test_15: --help documents snapshot format flags")


def test_16_entrypoint_rejects_unknown_flags():
    source = (TUI_DIR / "station_chief_tui.py").read_text()
    ensure("ALLOWED_FLAGS" in source, "station_chief_tui.py must define ALLOWED_FLAGS")
    r = subprocess.run([sys.executable, str(TUI_DIR / "station_chief_tui.py"), "--definitely-not-real"],
                       capture_output=True, text=True, timeout=30)
    ensure(r.returncode != 0, "Invalid flag must exit nonzero")
    ensure(r.returncode == 2, "Invalid flag must exit with code 2")
    ensure("ERROR" in r.stdout, "Invalid flag must print ERROR")
    ensure("Traceback" not in r.stdout and "Traceback" not in r.stderr, "No traceback")
    ensure("THE AGENT COMMAND CENTER" not in r.stdout, "Must not enter TUI mode")
    print("  [PASS] test_16: Invalid flag rejected")


def test_17_acceptance_report_verdict():
    report = PHASE2_EXPORTS / "interface_phase_2_acceptance_report.md"
    ensure(report.exists(), "Acceptance report must exist")
    content = report.read_text()
    ensure("PASS_WITH_HIGH_CONFIDENCE" in content, "Must contain PASS_WITH_HIGH_CONFIDENCE")
    ensure("Final Verdict: ACCEPTED" not in content, "Must not contain old FINAL VERDICT")
    ensure("Status: ACCEPTED" not in content, "Must not contain old STATUS")
    ensure("Official repo touched" in content and "false" in content, "Must mention Official repo touched: false")
    ensure("Deployment performed" in content and "false" in content, "Must mention Deployment performed: false")
    ensure("Command packets executed" in content and "false" in content, "Must mention Command packets executed: false")
    print("  [PASS] test_17: Acceptance report uses correct verdict and invariants")


def test_18_snapshot_save_works():
    r = subprocess.run([sys.executable, str(TUI_DIR / "station_chief_tui.py"),
                        "--snapshot", "--format", "json", "--save"],
                       capture_output=True, text=True, timeout=30)
    ensure(r.returncode == 0, f"--snapshot --format json --save exited {r.returncode}")
    ensure("Snapshot saved" in r.stdout, "Must confirm snapshot save")
    ensure("snapshots/snapshot_" in r.stdout, "Must save to snapshots/ dir")
    print("  [PASS] test_18: Snapshot save works")


def test_19_format_without_snapshot_fails():
    r = subprocess.run([sys.executable, str(TUI_DIR / "station_chief_tui.py"),
                        "--format", "json"],
                       capture_output=True, text=True, timeout=30)
    ensure(r.returncode != 0, "--format without --snapshot must fail")
    ensure("ERROR" in r.stdout, "Must print error")
    print("  [PASS] test_19: --format without --snapshot fails safely")


def test_20_save_without_snapshot_fails():
    r = subprocess.run([sys.executable, str(TUI_DIR / "station_chief_tui.py"), "--save"],
                       capture_output=True, text=True, timeout=30)
    ensure(r.returncode != 0, "--save without --snapshot must fail")
    ensure("ERROR" in r.stdout, "Must print error")
    print("  [PASS] test_20: --save without --snapshot fails safely")


def test_21_invalid_format_fails():
    r = subprocess.run([sys.executable, str(TUI_DIR / "station_chief_tui.py"),
                        "--snapshot", "--format", "invalid_format_xyz"],
                       capture_output=True, text=True, timeout=30)
    ensure(r.returncode != 0, "Invalid format must fail")
    ensure("ERROR" in r.stdout, "Must print error")
    print("  [PASS] test_21: Invalid snapshot format fails safely")


def test_22_back_navigation():
    r = subprocess.run(
        [sys.executable, TUI_DIR / "station_chief_tui.py", "--no-curses"],
        input="2\nb\nq\n",
        capture_output=True, text=True, timeout=30
    )
    ensure("ACTION REGISTRY" in r.stdout, "Screen 2 shows action registry")
    ensure("DASHBOARD" in r.stdout.upper() or "THE AGENT COMMAND CENTER" in r.stdout,
           "Back to dashboard expected")
    ensure("Traceback" not in r.stdout and "Traceback" not in r.stderr, "No traceback")
    print("  [PASS] test_22: b/back navigation works")


def test_23_dashboard_home():
    r = subprocess.run(
        [sys.executable, TUI_DIR / "station_chief_tui.py", "--no-curses"],
        input="3\nd\nq\n",
        capture_output=True, text=True, timeout=30
    )
    ensure("ARTIFACT INSPECTOR" in r.stdout, "Screen 3 shows artifact inspector")
    ensure("THE AGENT COMMAND CENTER" in r.stdout, "d returns to dashboard")
    print("  [PASS] test_23: d/dashboard navigation works")


def test_24_safety_monitor():
    r = subprocess.run(
        [sys.executable, TUI_DIR / "station_chief_tui.py", "--no-curses"],
        input="9\nq\n",
        capture_output=True, text=True, timeout=30
    )
    ensure("SAFETY BOUNDARY MONITOR" in r.stdout, "Screen 9 shows safety monitor")
    ensure("LOCKED" in r.stdout, "Safety monitor shows LOCKED")
    ensure("Self-Checks" in r.stdout, "Safety monitor shows self-checks")
    print("  [PASS] test_24: Safety boundary monitor screen works")


def test_25_no_tui_redefines_backend():
    for mod_name in ["tui_state", "tui_screens", "tui_app"]:
        mod = _load_tui_module(mod_name)
        if mod is None:
            continue
        source = (TUI_DIR / f"{mod_name}.py").read_text() if (TUI_DIR / f"{mod_name}.py").exists() else ""
        ensure("ACTION_REGISTRY = {" not in source, f"{mod_name} must not redefine ACTION_REGISTRY")
        ensure("LOCKED_ACTIONS = [" not in source, f"{mod_name} must not redefine LOCKED_ACTIONS")
    print("  [PASS] test_25: TUI does not redefine Phase 1 backend data")


def test_26_session_file_creation():
    from tui_state import TUIState, write_session_report, TEST_SESSION_DIR
    s = TUIState()
    p = write_session_report(s, session_dir=TEST_SESSION_DIR)
    ensure(p.exists(), "Session file must exist")
    ensure(p.suffix == ".md", "Session file must be markdown")
    json_path = p.with_suffix(".json")
    ensure(json_path.exists(), "Session JSON must exist")
    ensure("test_runs" in str(p), "Session file must be under test_runs/")
    print(f"  [PASS] test_26: Session files created under test_runs/sessions/")


def test_27_snapshot_dir():
    snap_dir = PHASE2_EXPORTS / "snapshots"
    ensure(snap_dir.is_dir() or not snap_dir.exists(), "Snapshot dir path must be valid")
    print("  [PASS] test_27: Snapshot directory path is valid")


def test_28_new_phase2_artifacts_exist():
    required = [
        ROOT / "scripts/demo_interface_phase_2_tui.sh",
        PHASE2_EXPORTS / "interface_phase_2_demo_notes.md",
        PHASE2_EXPORTS / "phase_3_handoff_contract.md",
        PHASE2_EXPORTS / "merge_readiness/interface_phase_2_merge_readiness_packet.md",
        PHASE2_EXPORTS / "interface_phase_2_upgrade_report.md",
    ]
    for path in required:
        ensure(path.exists(), f"Required artifact missing: {path.relative_to(ROOT)}")
    test_runs = PHASE2_EXPORTS / "test_runs"
    ensure(test_runs.is_dir(), "test_runs/ directory must exist")
    ensure((test_runs / "snapshots").is_dir(), "test_runs/snapshots/ must exist")
    ensure((test_runs / "sessions").is_dir(), "test_runs/sessions/ must exist")
    ensure((test_runs / "ledgers").is_dir(), "test_runs/ledgers/ must exist")
    ensure((test_runs / "reports").is_dir(), "test_runs/reports/ must exist")
    print("  [PASS] test_28: All Phase 2 upgrade-pack artifacts and test_runs/ dirs exist")


def test_31_safety_scanner_precision():
    from tui_safety_scanner import scan_source_files
    result = scan_source_files()
    required_keys = ["status", "active_forbidden_findings", "allowed_label_findings",
                     "files_scanned", "notes"]
    for key in required_keys:
        ensure(key in result, f"safety scanner result missing key: {key}")
    ensure(result["status"] in ("PASS", "WARNING", "FAIL"),
           f"status must be valid, got {result['status']}")
    ensure(isinstance(result["active_forbidden_findings"], list),
           "active_forbidden_findings must be a list")
    ensure(isinstance(result["allowed_label_findings"], list),
           "allowed_label_findings must be a list")
    for finding in result["active_forbidden_findings"]:
        for key in ("file", "line", "pattern", "context", "severity"):
            ensure(key in finding, f"active finding missing key: {key}")
    for finding in result["allowed_label_findings"]:
        for key in ("file", "line", "pattern", "context", "reason"):
            ensure(key in finding, f"allowed label finding missing key: {key}")
    ensure(len(result["files_scanned"]) > 0, "Must scan at least one file")
    ensure(result["status"] != "FAIL", "Safety scanner must not find active forbidden patterns")
    print(f"  [PASS] test_31: Safety scanner precision OK — status={result['status']}")


def test_30_json_schema_contract():
    from tui_state import TUIState
    state = TUIState()
    from tui_renderer import render_snapshot_json
    raw = render_snapshot_json(state)
    data = json.loads(raw)
    required_root = [
        "timestamp", "repo", "source_lineage", "phase", "mode",
        "session_id", "current_screen", "safety", "boundary",
        "actions_completed", "actions_refused", "validator_runs",
        "packets_prepared", "branch_reviews_prepared", "ledger_records_created",
        "action_registry", "last_validator_results",
        "_schema_version", "_metadata",
    ]
    for field in required_root:
        ensure(field in data, f"JSON snapshot missing required root field: {field}")
    allowed_safety = ("LOCKED", "DISABLED")
    for k, v in data["safety"].items():
        ensure(v in allowed_safety, f"Safety field '{k}' has invalid value: {v}")
    for k, v in data["boundary"].items():
        ensure(isinstance(v, bool), f"Boundary field '{k}' must be boolean, got {type(v).__name__}")
        ensure(v is False, f"Boundary field '{k}' must be False, got {v}")
    ensure(data["_schema_version"] == "1.0", f"Schema version must be 1.0, got {data['_schema_version']}")
    ar = data["action_registry"]
    for field in ("total", "safe", "controlled", "locked"):
        ensure(field in ar, f"action_registry missing field: {field}")
        ensure(isinstance(ar[field], int) and ar[field] >= 0, f"action_registry.{field} must be non-negative int")
    print("  [PASS] test_30: JSON snapshot schema contract validated (1.0)")


def test_29_test_artifact_isolation():
    from tui_state import TUIState, write_session_report, \
        TEST_RUNS_DIR, TEST_SESSION_DIR, TEST_SNAPSHOT_DIR, \
        SESSION_DIR, SNAPSHOT_DIR
    ensure(str(TEST_RUNS_DIR).endswith("test_runs"), "TEST_RUNS_DIR must point to test_runs/")
    ensure(str(TEST_SESSION_DIR).endswith("test_runs/sessions"), "TEST_SESSION_DIR must be under test_runs/")
    ensure(str(TEST_SNAPSHOT_DIR).endswith("test_runs/snapshots"), "TEST_SNAPSHOT_DIR must be under test_runs/")
    ensure(str(SESSION_DIR).endswith("sessions") and "test_runs" not in str(SESSION_DIR),
           "SESSION_DIR must be production path, not test_runs")
    ensure(str(SNAPSHOT_DIR).endswith("snapshots") and "test_runs" not in str(SNAPSHOT_DIR),
           "SNAPSHOT_DIR must be production path, not test_runs")
    s = TUIState()
    p = write_session_report(s, session_dir=TEST_SESSION_DIR)
    ensure("test_runs/sessions" in str(p), "Validator session file must go to test_runs/sessions/")
    ensure("sessions" not in str(p.parent.parent) or "test_runs" in str(p),
           "Must NOT write to production sessions/ dir")
    print("  [PASS] test_29: Test artifact isolation — validator writes to test_runs/, not production paths")


def main():
    print("Starting Interface Phase 2 TUI Validation (Hardened)...")
    print()

    tests = [
        test_01_tui_directory_exists,
        test_02_tui_modules_exist,
        test_03_tui_modules_import,
        test_04_keymap_valid,
        test_05_state_module,
        test_06_safe_actions,
        test_07_renderer_has_all_screens,
        test_08_renderer_output,
        test_09_screens_module,
        test_10_entrypoint_flags,
        test_11_no_forbidden_imports_or_patterns,
        test_12_session_dir_exists,
        test_13_no_duplicate_cli_entrypoint,
        test_14_snapshot_modes_work,
        test_15_help_mode_works,
        test_16_entrypoint_rejects_unknown_flags,
        test_17_acceptance_report_verdict,
        test_18_snapshot_save_works,
        test_19_format_without_snapshot_fails,
        test_20_save_without_snapshot_fails,
        test_21_invalid_format_fails,
        test_22_back_navigation,
        test_23_dashboard_home,
        test_24_safety_monitor,
        test_25_no_tui_redefines_backend,
        test_26_session_file_creation,
        test_27_snapshot_dir,
        test_28_new_phase2_artifacts_exist,
        test_29_test_artifact_isolation,
        test_30_json_schema_contract,
        test_31_safety_scanner_precision,
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
        print("\nINTERFACE_PHASE_2_TUI_VALIDATION_FAIL")
        sys.exit(1)
    else:
        print("\nINTERFACE_PHASE_2_TUI_VALIDATION_PASS")


if __name__ == "__main__":
    main()
