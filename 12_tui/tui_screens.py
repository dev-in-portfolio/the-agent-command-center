import sys
from tui_state import TUIState, write_session_report
from tui_renderer import (
    render_dashboard, render_action_registry, render_artifact_inspector,
    render_validator_wall, render_command_packet_prep, render_branch_review_prep,
    render_approval_ledger, render_help, SEPARATOR,
)
from tui_safe_actions import (
    run_validator_wall, prepare_command_packet,
    prepare_branch_review, review_packet, approve_packet, reject_packet,
)
from tui_keymap import KEY_TO_SCREEN, is_valid_key, get_screen_for_key


def handle_dashboard_input(state, key, get_input_fn):
    return get_screen_for_key(key)


def handle_action_registry_input(state, key, get_input_fn):
    return get_screen_for_key(key)


def handle_artifact_inspector_input(state, key, get_input_fn):
    return get_screen_for_key(key)


def handle_validator_wall_input(state, key, get_input_fn):
    if key == "4":
        print()
        print("  Enter RUN_VALIDATOR_WALL to confirm, or anything else to cancel.")
        confirmation = get_input_fn("  > ")
        if confirmation.strip() == "RUN_VALIDATOR_WALL":
            print()
            print("  Running validator wall...")
            results = run_validator_wall()
            state.last_validator_results = results
            for name, status in results.items():
                state.record_validator_run(name, status)
                outcome = "PASS" if status == "PASS" else "FAIL"
                s = f"  [{outcome}] {name}"
                if status != "PASS":
                    s += f" ({status})"
                print(s)
            state.record_action_completed("validator_wall")
        else:
            print("  Cancelled.")
    return get_screen_for_key(key)


def handle_command_packet_prep_input(state, key, get_input_fn):
    if key == "5":
        print()
        print("  Enter packet type number (1-7) or 0 to cancel:")
        packet_types = [
            "validator_wall", "artifact_audit", "trial_v3_review",
            "migration_review", "merge_review_packet",
            "artifact_integrity_audit", "cleanup_branch_review",
        ]
        choice = get_input_fn("  > ").strip()
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(packet_types):
                ptype = packet_types[idx - 1]
                result = prepare_command_packet(ptype)
                if result.get("status") == "PASS":
                    print(f"  [PASS] Packet prepared: {ptype}")
                    state.record_packet_prepared(ptype)
                    state.record_action_completed(f"prepare_packet_{ptype}")
                else:
                    print(f"  [FAIL] {result.get('error', 'unknown error')}")
                    state.record_action_refused(f"prepare_packet_{ptype}",
                                                result.get('error', 'unknown'))
            else:
                print("  Invalid choice.")
        else:
            print("  Cancelled.")
    return get_screen_for_key(key)


def handle_branch_review_prep_input(state, key, get_input_fn):
    if key == "6":
        print()
        print("  Enter branch name and optional base branch.")
        print("  Format: <branch> [base_branch]")
        print("  Example: interface/phase-2-tui-operator-dashboard master")
        raw = get_input_fn("  > ").strip()
        parts = raw.split()
        if not parts:
            print("  Cancelled.")
            return get_screen_for_key(key)
        branch = parts[0]
        base = parts[1] if len(parts) > 1 else None
        result = prepare_branch_review(branch, base)
        if result.get("status") == "PASS":
            print(f"  [PASS] Branch review prepared for {branch}")
            state.record_branch_review(branch, base or "master")
            state.record_action_completed(f"branch_review_{branch}")
        else:
            print(f"  [FAIL] {result.get('error', 'unknown error')}")
            state.record_action_refused(f"branch_review_{branch}",
                                        result.get('error', 'unknown'))
    return get_screen_for_key(key)


def handle_approval_ledger_input(state, key, get_input_fn):
    if key == "7":
        print()
        print("  Approval Ledger options:")
        print("  1. Review a packet")
        print("  2. Approve a packet (by phrase)")
        print("  3. Reject a packet (by note)")
        opt = get_input_fn("  Enter option (1-3, or 0 to cancel): ").strip()
        if opt == "1":
            p = get_input_fn("  Packet path: ").strip()
            if p:
                result = review_packet(p)
                if result.get("status") == "PASS":
                    print("  [PASS] Packet reviewed.")
                    state.record_ledger_write()
                    state.record_action_completed("review_packet")
                else:
                    print(f"  [FAIL] {result.get('error', 'unknown')}")
                    state.record_action_refused("review_packet",
                                                result.get('error', 'unknown'))
        elif opt == "2":
            p = get_input_fn("  Packet path: ").strip()
            phrase = get_input_fn("  Approval phrase: ").strip()
            if p and phrase:
                result = approve_packet(p, phrase)
                if result.get("status") in ("PASS", "WARNING"):
                    print(f"  [{result['status']}] Packet approval processed.")
                    state.record_ledger_write()
                    state.record_action_completed("approve_packet")
                else:
                    print(f"  [FAIL] {result.get('error', 'unknown')}")
                    state.record_action_refused("approve_packet",
                                                result.get('error', 'unknown'))
        elif opt == "3":
            p = get_input_fn("  Packet path: ").strip()
            note = get_input_fn("  Reason (optional): ").strip()
            if p:
                result = reject_packet(p, note)
                if result.get("status") == "PASS":
                    print("  [PASS] Packet rejected.")
                    state.record_ledger_write()
                    state.record_action_completed("reject_packet")
                else:
                    print(f"  [FAIL] {result.get('error', 'unknown')}")
                    state.record_action_refused("reject_packet",
                                                result.get('error', 'unknown'))
        else:
            print("  Cancelled.")
    return get_screen_for_key(key)


def handle_help_input(state, key, get_input_fn):
    return get_screen_for_key(key)


SCREEN_HANDLERS = {
    "dashboard": handle_dashboard_input,
    "action_registry": handle_action_registry_input,
    "artifact_inspector": handle_artifact_inspector_input,
    "validator_wall": handle_validator_wall_input,
    "command_packet_prep": handle_command_packet_prep_input,
    "branch_review_prep": handle_branch_review_prep_input,
    "approval_ledger": handle_approval_ledger_input,
    "help": handle_help_input,
}

SCREEN_RENDERERS = {
    "dashboard": render_dashboard,
    "action_registry": render_action_registry,
    "artifact_inspector": render_artifact_inspector,
    "validator_wall": render_validator_wall,
    "command_packet_prep": render_command_packet_prep,
    "branch_review_prep": render_branch_review_prep,
    "approval_ledger": render_approval_ledger,
    "help": render_help,
}
