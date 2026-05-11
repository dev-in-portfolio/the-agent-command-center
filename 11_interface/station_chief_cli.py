#!/usr/bin/env python3
"""
The Agent Command Center -- Station Chief v25
Interface Phase 1: CLI Operator Console

Usage:
  python3 11_interface/station_chief_cli.py              # Interactive mode
  python3 11_interface/station_chief_cli.py --status     # Non-interactive
  python3 11_interface/station_chief_cli.py --validator-wall
  python3 11_interface/station_chief_cli.py --list-artifacts
  python3 11_interface/station_chief_cli.py --show-summaries
  python3 11_interface/station_chief_cli.py --show-locked
  python3 11_interface/station_chief_cli.py --session-state
  python3 11_interface/station_chief_cli.py --prepare-packet <type>
  python3 11_interface/station_chief_cli.py --generate-session-report
"""
import sys
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def _load_sibling(name):
    path = HERE / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


policy = _load_sibling("interface_policy")
session_log_module = _load_sibling("interface_session_log")
actions = _load_sibling("interface_actions")

InterfaceSessionLog = session_log_module.InterfaceSessionLog

MENU_OPTIONS = {
    "1": ("Show system status", actions.action_show_status, "safe"),
    "2": ("Run validator wall", actions.action_run_validator_wall, "controlled"),
    "3": ("List artifact packages", actions.action_list_artifact_packages, "safe"),
    "4": ("Show latest trial / gauntlet summaries", actions.action_show_summaries, "safe"),
    "5": ("Generate operator session report", actions.action_generate_session_report, "controlled"),
    "6": ("Show locked actions", actions.action_show_locked_actions, "safe"),
    "7": ("Prepare command packet", actions.action_prepare_command_packet, "controlled"),
    "8": ("Show current session state", actions.action_show_session_state, "safe"),
    "9": ("Exit", None, "exit"),
}

VALID_PACKET_TYPES = [
    "validator_wall", "artifact_audit", "non_repo_gauntlet_review",
    "trial_v3_review", "migration_review", "merge_review_packet",
    "interface_phase_1_merge_review", "interface_phase_2_planning",
    "artifact_integrity_audit", "release_readiness_review",
    "cleanup_branch_review", "branch_delete_review",
]


def show_header():
    print("=" * 60)
    print("  AGENT COMMAND CENTER -- STATION CHIEF v25")
    print("  The Agent Command Center")
    print("  Interface Phase 1: CLI Operator Console")
    print("=" * 60)
    print()


def show_menu():
    print()
    for key in sorted(MENU_OPTIONS.keys()):
        label, _, category = MENU_OPTIONS[key]
        tag = ""
        if category == "safe":
            tag = " [safe]"
        elif category == "controlled":
            tag = " [controlled]"
        print(f"  {key}. {label}{tag}")
    print()


def interactive_mode(session_log):
    show_header()
    while True:
        show_menu()
        try:
            choice = input("  Enter choice: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            choice = "9"

        if choice == "9":
            has_report = len(session_log.reports_generated) > 0
            if not has_report and len(session_log.actions_completed) > 0:
                print("\n  Session report has not been written.")
                try:
                    resp = input("  Write session report before exit? (y/n): ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    resp = "n"
                if resp == "y" or resp == "yes":
                    actions.action_generate_session_report(session_log)
            print("\n  Exiting. Boundary secure.")
            session_log.close()
            sys.exit(0)

        if choice not in MENU_OPTIONS:
            print("  Invalid choice. Enter 1-9.")
            continue

        label, action_fn, category = MENU_OPTIONS[choice]
        if category == "exit":
            continue

        print(f"\n  --- {label} ---\n")
        try:
            action_fn(session_log)
        except Exception as e:
            print(f"  ERROR: {e}")
            session_log.record_error(str(e))

        print()
        try:
            input("  Press Enter to continue...")
        except (EOFError, KeyboardInterrupt):
            pass
        print()


def non_interactive_mode(session_log):
    args = sys.argv[1:]

    if not args:
        print("Usage: see --help for non-interactive flags")
        sys.exit(1)

    flag = args[0]

    if flag == "--status":
        actions.action_show_status(session_log)
    elif flag == "--validator-wall":
        actions.action_run_validator_wall(session_log)
    elif flag == "--list-artifacts":
        actions.action_list_artifact_packages(session_log)
    elif flag == "--show-summaries":
        actions.action_show_summaries(session_log)
    elif flag == "--show-locked":
        actions.action_show_locked_actions(session_log)
    elif flag == "--session-state":
        actions.action_show_session_state(session_log)
    elif flag == "--generate-session-report":
        actions.action_generate_session_report(session_log)
    elif flag == "--prepare-packet":
        if len(args) < 2:
            print("  ERROR: --prepare-packet requires a packet type argument.")
            print(f"  Valid types: {', '.join(VALID_PACKET_TYPES)}")
            sys.exit(1)
        ptype = args[1]
        if ptype not in VALID_PACKET_TYPES:
            print(f"  ERROR: Invalid packet type '{ptype}'.")
            print(f"  Valid types: {', '.join(VALID_PACKET_TYPES)}")
            sys.exit(1)
        # Use actions module directly (already loaded via importlib)
        actions.COMMAND_PACKETS.mkdir(parents=True, exist_ok=True)
        packet_path = actions.COMMAND_PACKETS / f"{ptype}_packet.md"
        content, packet_id, approval_phrase = actions._write_packet(ptype, session_log)
        packet_path.write_text(content)
        session_log.record_command_packet(str(packet_path))
        print(f"  [PASS] Packet prepared: {packet_path}")
        print(f"  Packet ID: {packet_id}")
        print(f"  Status: prepared_not_executed")
    elif flag in ("--help", "-h"):
        print(__doc__)
    else:
        print(f"  ERROR: Unknown flag '{flag}'.")
        print("  Usage: python3 11_interface/station_chief_cli.py [--flag]")
        print("  Flags: --status, --validator-wall, --list-artifacts, --show-summaries,")
        print("         --show-locked, --session-state, --generate-session-report,")
        print("         --prepare-packet <type>")
        sys.exit(1)

    session_log.close()


def main():
    session_log = InterfaceSessionLog(repo_name="dev-in-portfolio/the-agent-command-center")

    if len(sys.argv) > 1:
        non_interactive_mode(session_log)
    else:
        interactive_mode(session_log)


if __name__ == "__main__":
    main()
