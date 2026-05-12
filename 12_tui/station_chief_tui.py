#!/usr/bin/env python3
"""
The Agent Command Center -- Station Chief TUI v25
Interface Phase 2: TUI Operator Dashboard

Usage:
  python3 12_tui/station_chief_tui.py                # Interactive (curses preferred, plain fallback)
  python3 12_tui/station_chief_tui.py --snapshot      # Print snapshot and exit
  python3 12_tui/station_chief_tui.py --no-curses     # Force plain-text interactive mode
  python3 12_tui/station_chief_tui.py --help          # Print this help and exit
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "12_tui"))


def main():
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print(__doc__)
        sys.exit(0)

    from tui_state import TUIState

    state = TUIState()

    if "--snapshot" in args:
        from tui_app import run_snapshot
        run_snapshot(state)
        sys.exit(0)

    no_curses = "--no-curses" in args

    if not no_curses:
        try:
            import curses
            curses  # silence unused
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
