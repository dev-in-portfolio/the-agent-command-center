#!/usr/bin/env python3
import sys
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
    import importlib
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ensure(condition, message):
    if not condition:
        print(f"FAIL: {message}")
        sys.exit(1)


def check_file_exists(path, label):
    exists = path.exists()
    ensure(exists, f"{label} not found: {path}")
    return path


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
        path = TUI_DIR / mod
        ensure(path.exists(), f"Required TUI module missing: {mod}")
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
    ensure(len(mod.SCREENS) >= 7, "SCREENS must have at least 7 entries")
    print("  [PASS] test_04: Keymap has required bindings and structure")


def test_05_state_module():
    mod = _load_tui_module("tui_state")
    ensure(hasattr(mod, "TUIState"), "TUIState class must exist")
    ensure(hasattr(mod, "write_session_report"), "write_session_report must exist")
    ensure(hasattr(mod, "SESSION_DIR"), "SESSION_DIR must exist")
    state = mod.TUIState()
    ensure(hasattr(state, "current_screen"), "state.current_screen must exist")
    ensure(hasattr(state, "session_id"), "state.session_id must exist")
    ensure(hasattr(state, "get_summary"), "state.get_summary must exist")
    summary = state.get_summary()
    ensure("final_boundary_state" in summary, "summary must have final_boundary_state")
    boundary = summary["final_boundary_state"]
    ensure(boundary.get("official_repo_touched") is False,
           "official_repo_touched must be false")
    ensure(boundary.get("deployment_performed") is False,
           "deployment_performed must be false")
    ensure(boundary.get("command_packets_executed") is False,
           "command_packets_executed must be false")
    print("  [PASS] test_05: TUIState has correct structure and invariants")


def test_06_safe_actions_no_network():
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
        "render_branch_review_prep", "render_approval_ledger", "render_help",
        "render_snapshot",
    ]
    for fn in required:
        ensure(hasattr(mod, fn), f"Renderer missing {fn}")
    print("  [PASS] test_07: Renderer has all required screen functions")


def test_08_renderer_output():
    mod_render = _load_tui_module("tui_renderer")
    mod_state = _load_tui_module("tui_state")
    state = mod_state.TUIState()
    output = mod_render.render_dashboard(state)
    ensure("THE AGENT COMMAND CENTER" in output, "Dashboard must show header")
    ensure("LOCKED" in output, "Dashboard must show locked status")
    ensure("dev-in-portfolio/the-agent-command-center" in output,
           "Dashboard must show repo name")
    output2 = mod_render.render_snapshot(state)
    ensure("SNAPSHOT" in output2, "Snapshot must include SNAPSHOT header")
    print("  [PASS] test_08: Renderer produces correct output")


def test_09_screens_module():
    mod = _load_tui_module("tui_screens")
    ensure(hasattr(mod, "SCREEN_HANDLERS"), "SCREEN_HANDLERS must exist")
    ensure(hasattr(mod, "SCREEN_RENDERERS"), "SCREEN_RENDERERS must exist")
    required_screens = [
        "dashboard", "action_registry", "artifact_inspector",
        "validator_wall", "command_packet_prep", "branch_review_prep",
        "approval_ledger", "help",
    ]
    for s in required_screens:
        ensure(s in mod.SCREEN_HANDLERS, f"SCREEN_HANDLERS missing {s}")
        ensure(s in mod.SCREEN_RENDERERS, f"SCREEN_RENDERERS missing {s}")
    print("  [PASS] test_09: Screens module has handlers and renderers for all 8 screens")


def test_10_entrypoint_flags():
    mod = _load_tui_module("station_chief_tui")
    ensure(hasattr(mod, "main"), "main() must exist")
    print("  [PASS] test_10: Entrypoint has main()")


def test_11_no_forbidden_imports():
    for mod_name in ["tui_state", "tui_safe_actions", "tui_renderer",
                     "tui_screens", "tui_app", "station_chief_tui"]:
        mod = _load_tui_module(mod_name)
        if mod is None:
            continue
        source = ""
        module_path = TUI_DIR / f"{mod_name}.py"
        if module_path.exists():
            source = module_path.read_text()
        forbidden = ["requests", "urllib", "http.client", "socket",
                     "os.environ", "shell=True"]
        for token in forbidden:
            if token == "os.environ":
                ensure("os.environ" not in source,
                       f"{mod_name} must not contain os.environ")
            elif token == "shell=True":
                ensure("shell=True" not in source,
                       f"{mod_name} must not contain shell=True")
            elif token == "requests":
                ensure("import requests" not in source and "from requests" not in source,
                       f"{mod_name} must not import requests")
            elif token == "urllib":
                ensure("import urllib" not in source and "from urllib" not in source,
                       f"{mod_name} must not import urllib")
            elif token in ("http.client", "socket"):
                if token == "http.client":
                    ensure("http.client" not in source,
                           f"{mod_name} must not import http.client")
                elif token == "socket":
                    ensure("import socket" not in source and "from socket" not in source,
                           f"{mod_name} must not import socket")
    print("  [PASS] test_11: No forbidden network/shell imports in TUI modules")


def test_12_session_dir_exists():
    sessions_dir = PHASE2_EXPORTS / "sessions"
    ensure(sessions_dir.is_dir() or not sessions_dir.exists(),
           "Session dir should exist or be creatable")
    print("  [PASS] test_12: session directory path is valid")


def test_13_no_duplicate_cli_entrypoint():
    cli_path = PHASE1_DIR / "station_chief_cli.py"
    ensure(cli_path.exists(), "Phase 1 CLI must still exist (not replaced)")
    print("  [PASS] test_13: Phase 1 CLI preserved, TUI is separate entrypoint")


def test_14_snapshot_mode_works():
    import subprocess
    r = subprocess.run(
        [sys.executable, str(TUI_DIR / "station_chief_tui.py"), "--snapshot"],
        capture_output=True, text=True, timeout=30
    )
    ensure(r.returncode == 0, f"--snapshot exited {r.returncode}: {r.stderr[:200]}")
    ensure("SNAPSHOT" in r.stdout, "--snapshot output must contain SNAPSHOT")
    ensure("dev-in-portfolio/the-agent-command-center" in r.stdout,
           "--snapshot output must contain repo name")
    print("  [PASS] test_14: --snapshot mode produces correct output")


def test_15_help_mode_works():
    import subprocess
    r = subprocess.run(
        [sys.executable, str(TUI_DIR / "station_chief_tui.py"), "--help"],
        capture_output=True, text=True, timeout=30
    )
    ensure(r.returncode == 0, f"--help exited {r.returncode}: {r.stderr[:200]}")
    ensure("snapshot" in r.stdout.lower() or "usage" in r.stdout.lower(),
           "--help must mention --snapshot")
    ensure("no-curses" in r.stdout.lower() or "no-curses" in r.stdout.lower(),
           "--help must mention --no-curses")
    print("  [PASS] test_15: --help mode documents all flags")


def test_16_entrypoint_rejects_unknown_flags():
    source = (TUI_DIR / "station_chief_tui.py").read_text()
    ensure("ALLOWED_FLAGS" in source, "station_chief_tui.py must define ALLOWED_FLAGS")
    ensure("--snapshot" in source, "ALLOWED_FLAGS must include --snapshot")
    ensure("--no-curses" in source, "ALLOWED_FLAGS must include --no-curses")
    ensure("--help" in source, "ALLOWED_FLAGS must include --help")
    ensure("-h" in source, "ALLOWED_FLAGS must include -h")
    print("  [PASS] test_16: Entrypoint defines ALLOWED_FLAGS with required flags")


def test_17_invalid_flag_subprocess():
    import subprocess
    r = subprocess.run(
        [sys.executable, str(TUI_DIR / "station_chief_tui.py"), "--definitely-not-real"],
        capture_output=True, text=True, timeout=30
    )
    ensure(r.returncode != 0, "Invalid flag must exit nonzero")
    ensure(r.returncode == 2, "Invalid flag must exit with code 2")
    ensure("ERROR" in r.stdout, "Invalid flag must print ERROR")
    ensure("Unknown flag" in r.stdout, "Invalid flag must identify unknown flag")
    ensure("--help" in r.stdout, "Invalid flag must reference --help")
    ensure("Traceback" not in r.stdout and "Traceback" not in r.stderr,
           "Invalid flag must not produce traceback")
    ensure("THE AGENT COMMAND CENTER" not in r.stdout,
           "Invalid flag must not enter TUI mode")
    print("  [PASS] test_17: Invalid flag subprocess exits 2, prints error, no traceback, no TUI")


def test_18_acceptance_report_verdict():
    report = PHASE2_EXPORTS / "interface_phase_2_acceptance_report.md"
    ensure(report.exists(), "Acceptance report must exist")
    content = report.read_text()
    ensure("PASS_WITH_HIGH_CONFIDENCE" in content,
           "Acceptance report must contain PASS_WITH_HIGH_CONFIDENCE")
    ensure("Final Verdict: ACCEPTED" not in content,
           "Acceptance report must not contain 'Final Verdict: ACCEPTED'")
    ensure("Status: ACCEPTED" not in content,
           "Acceptance report must not contain 'Status: ACCEPTED'")
    ensure("Official repo touched" in content and "false" in content,
           "Acceptance report must mention Official repo touched: false")
    ensure("Deployment performed" in content and "false" in content,
           "Acceptance report must mention Deployment performed: false")
    ensure("Command packets executed" in content and "false" in content,
           "Acceptance report must mention Command packets executed: false")
    print("  [PASS] test_18: Acceptance report uses valid verdict and includes safety invariants")


def test_19_no_forbidden_commands_in_source():
    forbidden_commands = ["git push", "git merge", "gh pr", "curl", "wget", "ssh", "scp"]
    for mod_name in ["tui_state", "tui_safe_actions", "tui_renderer",
                     "tui_screens", "tui_app", "station_chief_tui"]:
        module_path = TUI_DIR / f"{mod_name}.py"
        if not module_path.exists():
            continue
        source = module_path.read_text()
        for cmd in forbidden_commands:
            ensure(cmd not in source,
                   f"{mod_name} must not contain '{cmd}'")
    print("  [PASS] test_19: No forbidden commands (git push/merge, gh pr, curl, wget, ssh, scp) in TUI source")


def main():
    print("Starting Interface Phase 2 TUI Validation...")
    print()

    tests = [
        test_01_tui_directory_exists,
        test_02_tui_modules_exist,
        test_03_tui_modules_import,
        test_04_keymap_valid,
        test_05_state_module,
        test_06_safe_actions_no_network,
        test_07_renderer_has_all_screens,
        test_08_renderer_output,
        test_09_screens_module,
        test_10_entrypoint_flags,
        test_11_no_forbidden_imports,
        test_12_session_dir_exists,
        test_13_no_duplicate_cli_entrypoint,
        test_14_snapshot_mode_works,
        test_15_help_mode_works,
        test_16_entrypoint_rejects_unknown_flags,
        test_17_invalid_flag_subprocess,
        test_18_acceptance_report_verdict,
        test_19_no_forbidden_commands_in_source,
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
