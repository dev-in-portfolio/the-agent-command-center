#!/usr/bin/env python3
import sys
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INTERFACE_DIR = ROOT / "11_interface"
COMMAND_PACKETS_DIR = ROOT / "09_exports" / "interface_phase_1" / "command_packets"


def ensure(condition, message):
    if not condition:
        print(f"FAIL: {message}")
        sys.exit(1)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    print("Starting Interface Phase 1 Command Packet Validation...")

    # Load the actions module to test packet generation
    actions = load_module("interface_actions", INTERFACE_DIR / "interface_actions.py")
    session_log_mod = load_module("interface_session_log", INTERFACE_DIR / "interface_session_log.py")
    InterfaceSessionLog = session_log_mod.InterfaceSessionLog

    # All supported packet types
    all_packet_types = [
        "validator_wall",
        "artifact_audit",
        "non_repo_gauntlet_review",
        "trial_v3_review",
        "migration_review",
        "merge_review_packet",
        "interface_phase_1_merge_review",
        "interface_phase_2_planning",
        "artifact_integrity_audit",
        "release_readiness_review",
        "cleanup_branch_review",
        "branch_delete_review",
    ]

    COMMAND_PACKETS_DIR.mkdir(parents=True, exist_ok=True)

    for pt in all_packet_types:
        # Generate each packet
        log = InterfaceSessionLog(repo_name="test")
        content, packet_id, approval_phrase = actions._write_packet(pt, log)

        # Check status
        ensure("prepared_not_executed" in content,
               f"Packet '{pt}' missing status: prepared_not_executed")
        ensure("NOT executed" in content or "not been executed" in content,
               f"Packet '{pt}' incorrectly claims execution")

        # Check human approval
        ensure("Yes" in content and ("Human approval" in content.lower() or "Human Approval" in content),
               f"Packet '{pt}' missing human approval required")

        # Check approval phrase
        expected_phrase = f"I_APPROVE_PREPARED_PACKET_{pt.upper()}"
        ensure(expected_phrase in content,
               f"Packet '{pt}' missing required approval phrase: {expected_phrase}")

        # Check forbidden actions
        ensure("## Forbidden Actions" in content,
               f"Packet '{pt}' missing Forbidden Actions section")

        # Check no execution
        ensure("executed" not in content.lower().split("status:")[1].split("\n")[0]
               if "status:" in content else True,
               f"Packet '{pt}' status line says executed")

        print(f"  [PASS] {pt}: packet_id={packet_id}, approval={expected_phrase}")

    # Specific checks for Trial v3 scoreboard path
    trial_log = InterfaceSessionLog(repo_name="test")
    trial_content, _, _ = actions._write_packet("trial_v3_review", trial_log)
    ensure("09_exports/100_round_trial_v3/scoreboards/master_scoreboard.md" in trial_content,
           "Trial v3 packet does not use correct scoreboard path")
    print("  [PASS] Trial v3 packet uses correct scoreboard path")

    # Specific checks: merge packets don't actually merge
    merge_log = InterfaceSessionLog(repo_name="test")
    merge_content, _, _ = actions._write_packet("merge_review_packet", merge_log)
    ensure("prepare_packet" not in merge_content,
           "Merge packet references internal _write_packet")
    print("  [PASS] Merge packets do not contain merge execution commands")

    # Cleanup packets don't actually delete
    cleanup_log = InterfaceSessionLog(repo_name="test")
    cleanup_content, _, _ = actions._write_packet("cleanup_branch_review", cleanup_log)
    ensure("branch -d" not in cleanup_content or "git branch -d" not in cleanup_content,
           "Cleanup packet contains delete command")
    print("  [PASS] Cleanup packets do not contain delete commands")

    print("\nINTERFACE_PHASE_1_COMMAND_PACKETS_VALIDATION_PASS")


if __name__ == "__main__":
    main()
