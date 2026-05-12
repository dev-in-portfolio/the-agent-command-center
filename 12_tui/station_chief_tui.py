#!/usr/bin/env python3
"""
The Agent Command Center -- Station Chief TUI v25
Interface Phase 2: TUI Operator Dashboard (Upgraded)

Usage:
  python3 12_tui/station_chief_tui.py                          # Interactive (curses/plain)
  python3 12_tui/station_chief_tui.py --snapshot                # Snapshot (text, default)
  python3 12_tui/station_chief_tui.py --snapshot --format text  # Snapshot (text)
  python3 12_tui/station_chief_tui.py --snapshot --format md    # Snapshot (markdown)
  python3 12_tui/station_chief_tui.py --snapshot --format json  # Snapshot (json)
  python3 12_tui/station_chief_tui.py --snapshot --format compact
  python3 12_tui/station_chief_tui.py --snapshot --format full
  python3 12_tui/station_chief_tui.py --snapshot --format json --save
  python3 12_tui/station_chief_tui.py --no-curses               # Force plain text
  python3 12_tui/station_chief_tui.py --help                    # Help
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "12_tui"))

ALLOWED_FLAGS = {
    "--snapshot", "--no-curses", "--help", "-h",
    "--format", "--save",
}
VALID_SNAPSHOT_FORMATS = {"text", "markdown", "md", "json", "compact", "full"}


def main():
    args = sys.argv[1:]

    for a in args:
        if a.startswith("-") and a not in ALLOWED_FLAGS:
            print(f"ERROR: Unknown flag: {a}")
            print("Run with --help for usage.")
            sys.exit(2)

    skip_next = False
    non_flag_args = []
    for a in args:
        if skip_next:
            skip_next = False
            continue
        if a == "--format":
            skip_next = True
            continue
        if not a.startswith("-"):
            non_flag_args.append(a)
    if non_flag_args:
        print(f"ERROR: Unexpected argument: {non_flag_args[0]}")
        print("Run with --help for usage.")
        sys.exit(2)

    if "--help" in args or "-h" in args:
        print(__doc__)
        sys.exit(0)

    has_snapshot = "--snapshot" in args
    has_format = "--format" in args
    has_save = "--save" in args

    if has_save and not has_snapshot:
        print("ERROR: --save only works with --snapshot")
        sys.exit(2)

    if has_format and not has_snapshot:
        print("ERROR: --format only works with --snapshot")
        sys.exit(2)

    snapshot_fmt = "text"
    if has_format:
        idx = args.index("--format")
        if idx + 1 >= len(args):
            print("ERROR: --format requires a format argument (text, markdown, json, compact, full)")
            sys.exit(2)
        snapshot_fmt = args[idx + 1].lower()
        if snapshot_fmt == "md":
            snapshot_fmt = "markdown"
        if snapshot_fmt not in VALID_SNAPSHOT_FORMATS:
            print(f"ERROR: Unknown snapshot format: {snapshot_fmt}")
            print("Supported: text, markdown, json, compact, full")
            sys.exit(2)

    if has_snapshot:
        from tui_state import TUIState
        from tui_app import run_snapshot
        state = TUIState()
        run_snapshot(state, fmt=snapshot_fmt, save=has_save)
        sys.exit(0)

    from tui_state import TUIState

    state = TUIState()

    no_curses = "--no-curses" in args

    if not no_curses:
        try:
            import curses
            curses
            from tui_app import run_curses
            run_curses()
            sys.exit(0)
        except ImportError:
            print("  [INFO] curses not available. Falling back to plain-text mode.")
        except Exception as e:
            print(f"  [INFO] curses error: {e}. Falling back to plain-text mode.")

    from tui_app import run_plain_text
    run_plain_text(state)


if __name__ == "__main__":
    main()
