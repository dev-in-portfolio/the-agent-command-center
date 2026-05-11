#!/usr/bin/env python3
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
    "8": ("Exit", None, "exit"),
}


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
        elif category == "exit":
            tag = ""
        print(f"  {key}. {label}{tag}")
    print()


def main():
    session_log = InterfaceSessionLog(repo_name="dev-in-portfolio/the-agent-command-center")
    show_header()

    while True:
        show_menu()
        try:
            choice = input("  Enter choice: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            choice = "8"

        if choice == "8":
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
            print("  Invalid choice. Enter 1-8.")
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


if __name__ == "__main__":
    main()
