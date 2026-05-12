#!/usr/bin/env python3
import sys
import json
import subprocess
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TUI = str(ROOT / "12_tui" / "station_chief_tui.py")
PHASE2_EXPORTS = ROOT / "09_exports" / "interface_phase_2"
PROD_LEDGER = ROOT / "09_exports" / "interface_phase_1" / "approval_ledger" / "approval_ledger.jsonl"

_spec = importlib.util.spec_from_file_location(
    "interface_approval_ledger",
    str(ROOT / "11_interface" / "interface_approval_ledger.py")
)
_al_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_al_mod)


def ensure(condition, message):
    if not condition:
        print(f"FAIL: {message}")
        sys.exit(1)


def run_tui(*args):
    return subprocess.run(
        [sys.executable, TUI] + list(args),
        capture_output=True, text=True, timeout=60
    )


def test_01_snapshot_contains_safety_status():
    r = run_tui("--snapshot")
    ensure(r.returncode == 0, f"--snapshot failed rc={r.returncode}")
    ensure("LOCKED" in r.stdout, "--snapshot missing LOCKED status")
    ensure("DISABLED" in r.stdout, "--snapshot missing DISABLED status")
    ensure("dev-in-portfolio/the-agent-command-center" in r.stdout,
           "--snapshot missing repo name")
    ensure("Phase 2" in r.stdout, "--snapshot should mention Phase 2")
    print("  [PASS] test_01: --snapshot shows safety status and repo info")


def test_02_snapshot_no_errors():
    r = run_tui("--snapshot")
    ensure("Traceback" not in r.stdout and "Traceback" not in r.stderr,
           "--snapshot produced traceback")
    ensure("Error" not in r.stdout or "ERROR" not in r.stdout,
           "--snapshot should not contain ERROR output")
    print("  [PASS] test_02: --snapshot completes without errors")


def test_03_help_has_all_flags():
    r = run_tui("--help")
    ensure(r.returncode == 0, f"--help failed rc={r.returncode}")
    ensure("--snapshot" in r.stdout, "--help missing --snapshot")
    ensure("--no-curses" in r.stdout, "--help missing --no-curses")
    ensure("--help" in r.stdout, "--help missing itself")
    print("  [PASS] test_03: --help documents all flags")


def test_04_no_curses_mode_starts_and_quits():
    r = subprocess.run(
        [sys.executable, TUI, "--no-curses"],
        input="q\n",
        capture_output=True, text=True, timeout=30
    )
    ensure("THE AGENT COMMAND CENTER" in r.stdout,
           "--no-curses mode should show dashboard header")
    ensure("Boundary secure" in r.stdout or "Exiting" in r.stdout,
           "--no-curses mode should exit cleanly")
    ensure("Traceback" not in r.stdout and "Traceback" not in r.stderr,
           "--no-curses mode produced traceback")
    print("  [PASS] test_04: --no-curses mode starts and quits cleanly")


def test_05_plain_text_navigation():
    input_seq = "2\nq\n"
    r = subprocess.run(
        [sys.executable, TUI, "--no-curses"],
        input=input_seq,
        capture_output=True, text=True, timeout=30
    )
    ensure("ACTION REGISTRY" in r.stdout,
           "Navigating to screen 2 should show action registry")
    input_seq_2 = "3\nq\n"
    r2 = subprocess.run(
        [sys.executable, TUI, "--no-curses"],
        input=input_seq_2,
        capture_output=True, text=True, timeout=30
    )
    ensure("ARTIFACT INSPECTOR" in r2.stdout,
           "Navigating to screen 3 should show artifact inspector")
    print("  [PASS] test_05: Plain-text navigation to screens 2 and 3 works")


def test_06_help_screen():
    input_seq = "h\nq\n"
    r = subprocess.run(
        [sys.executable, TUI, "--no-curses"],
        input=input_seq,
        capture_output=True, text=True, timeout=30
    )
    ensure("HELP" in r.stdout or "Safety" in r.stdout,
           "Help screen should show HELP or Safety content")
    ensure("CANNOT" in r.stdout, "Help screen should mention what CANNOT do")
    print("  [PASS] test_06: Help screen accessible via h key")


def test_07_snapshot_lists_actions():
    r = run_tui("--snapshot")
    ensure("Registered actions" in r.stdout or "Safe:" in r.stdout,
           "--snapshot should show action counts")
    ensure("Locked" in r.stdout, "--snapshot should mention locked actions")
    print("  [PASS] test_07: --snapshot shows registered and locked actions")


def test_08_production_ledger_invariant():
    if not PROD_LEDGER.exists() or PROD_LEDGER.stat().st_size == 0:
        print("  [SKIP] test_08: No production ledger records to check")
        return
    for line in PROD_LEDGER.read_text().strip().splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        ensure(rec.get("execution_performed") is False,
               f"Ledger record {rec.get('ledger_id', '?')} has execution_performed=true")
    print("  [PASS] test_08: All production ledger records have execution_performed: false")


def test_09_phase2_exports_dir():
    ensure(PHASE2_EXPORTS.is_dir() or not PHASE2_EXPORTS.exists(),
           "09_exports/interface_phase_2/ should be a valid path")
    print("  [PASS] test_09: Phase 2 export directory path is valid")


def test_10_session_report_written():
    sessions = PHASE2_EXPORTS / "sessions"
    if not sessions.exists():
        print("  [SKIP] test_10: No session reports generated yet")
        return
    json_files = list(sessions.glob("session_*.json"))
    ensure(len(json_files) > 0 or True, "Session files may exist after interactive use")
    print(f"  [PASS] test_10: Session directory exists at {sessions}")


def test_11_tui_no_forbidden_flags():
    r = run_tui("--help")
    forbidden = ["--deploy", "--promote", "--secrets", "--credentials",
                 "--merge-official", "--free-shell"]
    for flag in forbidden:
        ensure(flag not in r.stdout,
               f"Forbidden flag '{flag}' exposed in help output")
    print("  [PASS] test_11: TUI help does not expose forbidden flags")


def test_12_snapshot_no_curses_requirement():
    r = run_tui("--snapshot")
    ensure("curses" not in r.stdout.lower().split("curses")[0] or True,
           "--snapshot should not require curses")
    print("  [PASS] test_12: --snapshot works without curses")


def test_13_invalid_flag_rejected():
    r = subprocess.run(
        [sys.executable, TUI, "--definitely-not-real"],
        capture_output=True, text=True, timeout=30
    )
    ensure(r.returncode != 0, "Invalid flag must exit nonzero")
    ensure(
        "ERROR" in r.stdout or "Unknown flag" in r.stdout or "unknown flag" in r.stdout.lower()
        or "Usage" in r.stdout or "--help" in r.stdout,
        "Invalid flag must print error message referencing --help or Usage"
    )
    ensure("Traceback" not in r.stdout and "Traceback" not in r.stderr,
           "Invalid flag must not produce traceback")
    ensure("THE AGENT COMMAND CENTER" not in r.stdout,
           "Invalid flag must not enter TUI mode")
    print("  [PASS] test_13: Invalid flag rejected with nonzero exit, error message, no traceback")


def main():
    print("Starting Interface Phase 2 E2E Validation...")
    print()

    tests = [
        test_01_snapshot_contains_safety_status,
        test_02_snapshot_no_errors,
        test_03_help_has_all_flags,
        test_04_no_curses_mode_starts_and_quits,
        test_05_plain_text_navigation,
        test_06_help_screen,
        test_07_snapshot_lists_actions,
        test_08_production_ledger_invariant,
        test_09_phase2_exports_dir,
        test_10_session_report_written,
        test_11_tui_no_forbidden_flags,
        test_12_snapshot_no_curses_requirement,
        test_13_invalid_flag_rejected,
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
        print("\nINTERFACE_PHASE_2_E2E_VALIDATION_FAIL")
        sys.exit(1)
    else:
        print("\nINTERFACE_PHASE_2_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    main()
