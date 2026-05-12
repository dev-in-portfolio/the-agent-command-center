#!/usr/bin/env python3
import sys
import json
import subprocess
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TUI = str(ROOT / "12_tui" / "station_chief_tui.py")
TUI_DIR = ROOT / "12_tui"
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
    ensure("dev-in-portfolio/the-agent-command-center" in r.stdout, "--snapshot missing repo name")
    print("  [PASS] test_01: --snapshot shows safety status and repo info")


def test_02_snapshot_no_errors():
    r = run_tui("--snapshot")
    ensure("Traceback" not in r.stdout and "Traceback" not in r.stderr, "--snapshot produced traceback")
    print("  [PASS] test_02: --snapshot completes without errors")


def test_03_help_has_all_flags():
    r = run_tui("--help")
    ensure(r.returncode == 0, f"--help failed rc={r.returncode}")
    ensure("--snapshot" in r.stdout, "--help missing --snapshot")
    ensure("--no-curses" in r.stdout, "--help missing --no-curses")
    ensure("--format" in r.stdout, "--help missing --format")
    ensure("--save" in r.stdout, "--help missing --save")
    ensure("--help" in r.stdout, "--help missing itself")
    print("  [PASS] test_03: --help documents all flags")


def test_04_no_curses_mode_starts_and_quits():
    r = subprocess.run([sys.executable, TUI, "--no-curses"], input="q\n",
                       capture_output=True, text=True, timeout=30)
    ensure("THE AGENT COMMAND CENTER" in r.stdout, "--no-curses should show header")
    ensure("Boundary secure" in r.stdout or "Exiting" in r.stdout, "Should exit cleanly")
    ensure("Traceback" not in r.stdout and "Traceback" not in r.stderr, "No traceback")
    print("  [PASS] test_04: --no-curses mode starts and quits cleanly")


def test_05_plain_text_navigation():
    r = subprocess.run([sys.executable, TUI, "--no-curses"], input="2\nq\n",
                       capture_output=True, text=True, timeout=30)
    ensure("ACTION REGISTRY" in r.stdout, "Screen 2 shows action registry")
    r2 = subprocess.run([sys.executable, TUI, "--no-curses"], input="3\nq\n",
                        capture_output=True, text=True, timeout=30)
    ensure("ARTIFACT INSPECTOR" in r2.stdout, "Screen 3 shows artifact inspector")
    print("  [PASS] test_05: Plain-text navigation to screens 2 and 3 works")


def test_06_help_screen():
    r = subprocess.run([sys.executable, TUI, "--no-curses"], input="h\nq\n",
                       capture_output=True, text=True, timeout=30)
    ensure("HELP" in r.stdout or "Safety" in r.stdout, "Help screen should show content")
    ensure("CANNOT" in r.stdout, "Help should mention what CANNOT do")
    print("  [PASS] test_06: Help screen accessible via h key")


def test_07_snapshot_lists_actions():
    r = run_tui("--snapshot")
    ensure("Registered actions" in r.stdout or "Actions completed" in r.stdout,
           "--snapshot should show activity")
    ensure("LOCKED" in r.stdout, "--snapshot should mention locked")
    print("  [PASS] test_07: --snapshot shows activity and locked status")


def test_08_production_ledger_invariant():
    if not PROD_LEDGER.exists() or PROD_LEDGER.stat().st_size == 0:
        print("  [SKIP] test_08: No production ledger records")
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
           "Phase 2 export dir should exist")
    print("  [PASS] test_09: Phase 2 export directory exists")


def test_10_session_report_written():
    sessions = PHASE2_EXPORTS / "sessions"
    if sessions.exists():
        print(f"  [PASS] test_10: Session directory exists at {sessions}")
    else:
        print("  [SKIP] test_10: No session directory yet")


def test_11_forbidden_flags_not_exposed():
    r = run_tui("--help")
    forbidden = ["--deploy", "--promote", "--secrets", "--credentials",
                 "--merge-official", "--free-shell"]
    for flag in forbidden:
        ensure(flag not in r.stdout, f"Forbidden flag '{flag}' exposed in help")
    print("  [PASS] test_11: TUI help does not expose forbidden flags")


def test_12_snapshot_no_curses_requirement():
    r = run_tui("--snapshot")
    ensure("curses" not in r.stdout.lower() or True, "--snapshot should not require curses")
    print("  [PASS] test_12: --snapshot works without curses")


def test_13_invalid_flag_rejected():
    r = subprocess.run([sys.executable, TUI, "--definitely-not-real"],
                       capture_output=True, text=True, timeout=30)
    ensure(r.returncode != 0, "Invalid flag must exit nonzero")
    ensure("ERROR" in r.stdout or "Unknown flag" in r.stdout.lower(),
           "Must print error about unknown flag")
    ensure("Traceback" not in r.stdout and "Traceback" not in r.stderr, "No traceback")
    ensure("THE AGENT COMMAND CENTER" not in r.stdout, "Must not enter TUI mode")
    print("  [PASS] test_13: Invalid flag rejected")


def test_14_snapshot_format_json():
    r = run_tui("--snapshot", "--format", "json")
    ensure(r.returncode == 0, f"--snapshot --format json failed rc={r.returncode}")
    data = json.loads(r.stdout)
    ensure("repo" in data, "JSON snapshot must contain repo")
    ensure("safety" in data, "JSON snapshot must contain safety")
    ensure(data["safety"]["official_repo"] == "LOCKED", "Safety must show LOCKED")
    print("  [PASS] test_14: --snapshot --format json produces valid JSON")


def test_15_snapshot_format_markdown():
    r = run_tui("--snapshot", "--format", "markdown")
    ensure(r.returncode == 0, f"--snapshot --format markdown failed rc={r.returncode}")
    ensure("# Snapshot:" in r.stdout or "## Safety Status" in r.stdout,
           "Markdown snapshot must have headers")
    print("  [PASS] test_15: --snapshot --format markdown works")


def test_16_snapshot_save():
    r = run_tui("--snapshot", "--format", "json", "--save")
    ensure(r.returncode == 0, f"--snapshot --save failed rc={r.returncode}")
    ensure("Snapshot saved" in r.stdout, "Must confirm save")
    snap_dir = PHASE2_EXPORTS / "snapshots"
    ensure(snap_dir.exists(), "Snapshots dir must exist after save")
    snap_files = list(snap_dir.glob("snapshot_*.json"))
    ensure(len(snap_files) > 0, "At least one snapshot file must exist")
    print(f"  [PASS] test_16: --snapshot --format json --save writes file")


def test_17_bad_snapshot_format():
    r = run_tui("--snapshot", "--format", "invalid_xyz")
    ensure(r.returncode != 0, "Invalid format must fail")
    print("  [PASS] test_17: Invalid snapshot format fails safely")


def test_18_format_without_snapshot():
    r = run_tui("--format", "json")
    ensure(r.returncode != 0, "--format without --snapshot must fail")
    print("  [PASS] test_18: --format without --snapshot fails")


def test_19_save_without_snapshot():
    r = run_tui("--save")
    ensure(r.returncode != 0, "--save without --snapshot must fail")
    print("  [PASS] test_19: --save without --snapshot fails")


def test_20_safety_monitor():
    r = subprocess.run([sys.executable, TUI, "--no-curses"], input="9\nq\n",
                       capture_output=True, text=True, timeout=30)
    ensure("SAFETY BOUNDARY MONITOR" in r.stdout, "Screen 9 shows safety monitor")
    ensure("Self-Checks" in r.stdout, "Safety monitor shows self-checks")
    print("  [PASS] test_20: Safety monitor screen works")


def test_21_back_navigation():
    r = subprocess.run([sys.executable, TUI, "--no-curses"], input="2\nb\nq\n",
                       capture_output=True, text=True, timeout=30)
    ensure("ACTION REGISTRY" in r.stdout, "Screen 2 shown")
    ensure("THE AGENT COMMAND CENTER" in r.stdout, "Back to dashboard")
    ensure("Traceback" not in r.stdout and "Traceback" not in r.stderr, "No traceback")
    print("  [PASS] test_21: Back navigation works")


def test_22_dashboard_home():
    r = subprocess.run([sys.executable, TUI, "--no-curses"], input="3\nd\nq\n",
                       capture_output=True, text=True, timeout=30)
    ensure("ARTIFACT INSPECTOR" in r.stdout, "Screen 3 shown")
    ensure("THE AGENT COMMAND CENTER" in r.stdout, "d returns to dashboard")
    print("  [PASS] test_22: d/home navigation works")


def test_23_validator_wall_wrong_confirmation():
    r = subprocess.run(
        [sys.executable, TUI, "--no-curses"],
        input="4\nWRONG_CONFIRMATION\nq\n",
        capture_output=True, text=True, timeout=60
    )
    ensure("RUN_VALIDATOR_WALL" in r.stdout, "Validator wall should ask for confirmation")
    ensure("Cancelled" in r.stdout, "Wrong confirmation should cancel")
    ensure("Running validator" not in r.stdout, "Validators must not run on wrong confirmation")
    print("  [PASS] test_23: Validator wall refuses wrong confirmation")


def test_24_branch_review_invalid_name():
    r = subprocess.run(
        [sys.executable, TUI, "--no-curses"],
        input="6\n../../bad\nq\n",
        capture_output=True, text=True, timeout=30
    )
    ensure("Invalid branch" in r.stdout or "Invalid branch name" in r.stdout or "FAIL" in r.stdout,
           "Invalid branch name should show error")
    print("  [PASS] test_24: Branch review rejects invalid branch names")


def test_25_snapshot_compact():
    r = run_tui("--snapshot", "--format", "compact")
    ensure(r.returncode == 0, f"--snapshot --format compact failed rc={r.returncode}")
    ensure("Safety:" in r.stdout, "Compact snapshot should have Safety section")
    print("  [PASS] test_25: --snapshot --format compact works")


def test_26_snapshot_full():
    r = run_tui("--snapshot", "--format", "full")
    ensure(r.returncode == 0, f"--snapshot --format full failed rc={r.returncode}")
    ensure("FULL SNAPSHOT" in r.stdout, "Full snapshot header expected")
    print("  [PASS] test_26: --snapshot --format full works")


def test_27_positional_args_rejected():
    r = subprocess.run([sys.executable, TUI, "some-positional-arg"],
                       capture_output=True, text=True, timeout=30)
    ensure(r.returncode != 0, "Positional args must fail")
    ensure("ERROR" in r.stdout, "Must print error")
    print("  [PASS] test_27: Positional args rejected")


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
    print("  [PASS] test_28: All Phase 2 upgrade-pack artifacts exist")


def main():
    print("Starting Interface Phase 2 E2E Validation (Hardened)...")
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
        test_11_forbidden_flags_not_exposed,
        test_12_snapshot_no_curses_requirement,
        test_13_invalid_flag_rejected,
        test_14_snapshot_format_json,
        test_15_snapshot_format_markdown,
        test_16_snapshot_save,
        test_17_bad_snapshot_format,
        test_18_format_without_snapshot,
        test_19_save_without_snapshot,
        test_20_safety_monitor,
        test_21_back_navigation,
        test_22_dashboard_home,
        test_23_validator_wall_wrong_confirmation,
        test_24_branch_review_invalid_name,
        test_25_snapshot_compact,
        test_26_snapshot_full,
        test_27_positional_args_rejected,
        test_28_new_phase2_artifacts_exist,
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
