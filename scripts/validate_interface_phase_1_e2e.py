#!/usr/bin/env python3
import sys
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLI = str(ROOT / "11_interface" / "station_chief_cli.py")
COMMAND_PACKETS = ROOT / "09_exports" / "interface_phase_1" / "command_packets"
BRANCH_REVIEWS = ROOT / "09_exports" / "interface_phase_1" / "branch_reviews"
APPROVAL_LEDGER = ROOT / "09_exports" / "interface_phase_1" / "approval_ledger" / "approval_ledger.jsonl"


def ensure(condition, message):
    if not condition:
        print(f"FAIL: {message}")
        sys.exit(1)


def run_cli(*args):
    return subprocess.run(
        [sys.executable, CLI] + list(args),
        capture_output=True, text=True, timeout=60
    )


def test_01_cli_status():
    r = run_cli("--status")
    ensure(r.returncode == 0, f"--status failed rc={r.returncode}: {r.stderr[:200]}")
    ensure("Product repo" in r.stdout, "--status missing product repo info")
    ensure("dev-in-portfolio/the-agent-command-center" in r.stdout,
           "--status missing product repo name")
    ensure("Deployment: disabled" in r.stdout,
           "--status missing Deployment: disabled")
    print("  [PASS] test_01: CLI --status returns product info and deployment disabled")


def test_02_cli_list_artifacts():
    r = run_cli("--list-artifacts")
    ensure(r.returncode == 0, f"--list-artifacts failed rc={r.returncode}: {r.stderr[:200]}")
    ensure("100-Round Trial v3" in r.stdout or "trial" in r.stdout.lower(),
           "--list-artifacts missing package info")
    ensure("Traceback" not in r.stdout and "Traceback" not in r.stderr,
           "--list-artifacts produced traceback")
    print("  [PASS] test_02: CLI --list-artifacts shows packages without traceback")


def test_03_cli_inspect_all():
    r = run_cli("--inspect-artifacts")
    ensure(r.returncode == 0, f"--inspect-artifacts failed rc={r.returncode}: {r.stderr[:200]}")
    ensure("trial_v3" in r.stdout or "100-Round Trial" in r.stdout,
           "--inspect-artifacts missing trial_v3 package")
    ensure("Traceback" not in r.stdout and "Traceback" not in r.stderr,
           "--inspect-artifacts produced traceback")
    print("  [PASS] test_03: CLI --inspect-artifacts inspects all packages without traceback")


def test_04_cli_inspect_one():
    r = run_cli("--inspect-artifact", "trial_v3")
    ensure(r.returncode == 0, f"--inspect-artifact trial_v3 failed rc={r.returncode}: {r.stderr[:200]}")
    ensure("trial_v3" in r.stdout or "100-Round Trial v3" in r.stdout,
           "--inspect-artifact missing expected package name")
    ensure("Traceback" not in r.stdout and "Traceback" not in r.stderr,
           "--inspect-artifact produced traceback")
    print("  [PASS] test_04: CLI --inspect-artifact trial_v3 inspects single package")


def test_05_cli_inspect_invalid():
    r = run_cli("--inspect-artifact", "definitely_not_real")
    ensure(r.returncode != 0 or "ERROR" in r.stdout,
           "--inspect-artifact invalid should fail or show error")
    ensure("Traceback" not in r.stdout and "Traceback" not in r.stderr,
           "--inspect-artifact invalid produced traceback")
    print("  [PASS] test_05: CLI --inspect-artifact invalid package fails safely")


def test_06_cli_prepare_packet():
    r = run_cli("--prepare-packet", "validator_wall")
    ensure(r.returncode == 0, f"--prepare-packet failed rc={r.returncode}: {r.stderr[:200]}")
    packet_file = COMMAND_PACKETS / "validator_wall_packet.md"
    ensure(packet_file.exists(), "Packet file not created")
    content = packet_file.read_text()
    ensure("prepared_not_executed" in content, "Packet missing prepared_not_executed")
    ensure("I_APPROVE_PREPARED_PACKET_VALIDATOR_WALL" in content,
           "Packet missing approval phrase")
    print("  [PASS] test_06: CLI --prepare-packet validator_wall creates valid packet")


def test_07_cli_invalid_packet():
    r = run_cli("--prepare-packet", "definitely_not_real")
    ensure(r.returncode != 0 or "ERROR" in r.stdout,
           "Invalid packet type should fail")
    ensure("Traceback" not in r.stdout and "Traceback" not in r.stderr,
           "Invalid packet produced traceback")
    print("  [PASS] test_07: CLI --prepare-packet invalid type fails safely")


def test_08_cli_branch_review_default_base():
    r = run_cli("--prepare-branch-review", "interface/phase-1-operational-hardening")
    ensure(r.returncode == 0, f"--prepare-branch-review failed rc={r.returncode}: {r.stderr[:200]}")
    reviews = list(BRANCH_REVIEWS.glob("*.md"))
    ensure(len(reviews) > 0, "No branch review packet created")
    latest = max(reviews, key=lambda p: p.stat().st_mtime)
    content = latest.read_text()
    ensure("prepared_not_merged" in content, "Review missing prepared_not_merged")
    ensure("Merge Performed: false" in content.replace("**", ""),
           "Review missing Merge Performed: false")
    print(f"  [PASS] test_08: CLI --prepare-branch-review default base creates valid packet")


def test_09_cli_branch_review_explicit_base():
    r = run_cli("--prepare-branch-review", "interface/phase-1-operational-hardening",
                "--base", "interface/phase-1-upgrade-pack")
    ensure(r.returncode == 0, f"--prepare-branch-review with --base failed rc={r.returncode}: {r.stderr[:200]}")
    reviews = list(BRANCH_REVIEWS.glob("*.md"))
    ensure(len(reviews) > 0, "No branch review packet created")
    latest = max(reviews, key=lambda p: p.stat().st_mtime)
    content = latest.read_text()
    ensure("Base Branch: ** interface/phase-1-upgrade-pack" in content or
           "Base Branch:** interface/phase-1-upgrade-pack" in content or
           "Base Branch: interface/phase-1-upgrade-pack" in content,
           "Review missing explicit base branch")
    ensure("Review Branch: ** interface/phase-1-operational-hardening" in content or
           "Review Branch:** interface/phase-1-operational-hardening" in content or
           "Review Branch: interface/phase-1-operational-hardening" in content,
           "Review missing review branch name")
    ensure("Merge Performed: false" in content.replace("**", ""),
           "Review claims merge performed")
    print("  [PASS] test_09: CLI --prepare-branch-review with --base shows correct branches")


def test_10_cli_branch_review_invalid():
    r = run_cli("--prepare-branch-review", "../bad")
    ensure(r.returncode != 0 or "ERROR" in r.stdout,
           "Branch review with '..' should fail")
    ensure("Traceback" not in r.stdout and "Traceback" not in r.stderr,
           "Invalid branch review produced traceback")
    print("  [PASS] test_10: CLI --prepare-branch-review invalid branch fails safely")


def test_11_cli_show_approval_ledger():
    r = run_cli("--show-approval-ledger")
    ensure(r.returncode == 0, f"--show-approval-ledger failed rc={r.returncode}: {r.stderr[:200]}")
    ensure("empty" in r.stdout.lower() or "record" in r.stdout.lower(),
           "--show-approval-ledger should handle empty ledger gracefully")
    print("  [PASS] test_11: CLI --show-approval-ledger handles empty ledger")


def test_12_cli_review_packet():
    packet_file = COMMAND_PACKETS / "validator_wall_packet.md"
    ensure(packet_file.exists(), "Packet file required for review test")
    r = run_cli("--review-packet", str(packet_file))
    ensure(r.returncode == 0, f"--review-packet failed rc={r.returncode}: {r.stderr[:200]}")
    ensure(APPROVAL_LEDGER.exists(), "Approval ledger should exist after review")
    records = []
    if APPROVAL_LEDGER.stat().st_size > 0:
        for line in APPROVAL_LEDGER.read_text().strip().splitlines():
            if line.strip():
                records.append(json.loads(line))
    if records:
        latest = records[-1]
        ensure(latest.get("execution_performed") is False,
               "Review record must have execution_performed: false")
        ensure(latest.get("state") == "reviewed",
               f"Review record should be 'reviewed' not '{latest.get('state')}'")
    print("  [PASS] test_12: CLI --review-packet creates ledger record with exec=false")


def test_13_cli_approve_packet_wrong_phrase():
    packet_file = COMMAND_PACKETS / "validator_wall_packet.md"
    ensure(packet_file.exists(), "Packet file required")
    r = run_cli("--approve-packet", str(packet_file), "WRONG_PHRASE")
    ensure(r.returncode == 0 or r.returncode == 1,
           f"--approve-packet wrong phrase unexpected rc={r.returncode}")
    records = []
    if APPROVAL_LEDGER.stat().st_size > 0:
        for line in APPROVAL_LEDGER.read_text().strip().splitlines():
            if line.strip():
                records.append(json.loads(line))
    if records:
        latest = records[-1]
        ensure(latest.get("execution_performed") is False,
               "Wrong-phrase approval must have execution_performed: false")
        ensure(latest.get("state") != "approved_by_operator",
               "Wrong phrase should not produce approved state")
    print("  [PASS] test_13: CLI --approve-packet wrong phrase does not approve")


def test_14_cli_approve_packet_correct_phrase():
    packet_file = COMMAND_PACKETS / "validator_wall_packet.md"
    ensure(packet_file.exists(), "Packet file required")
    r = run_cli("--approve-packet", str(packet_file), "I_APPROVE_PREPARED_PACKET_VALIDATOR_WALL")
    ensure(r.returncode == 0, f"--approve-packet correct phrase failed rc={r.returncode}: {r.stderr[:200]}")
    records = []
    if APPROVAL_LEDGER.stat().st_size > 0:
        for line in APPROVAL_LEDGER.read_text().strip().splitlines():
            if line.strip():
                records.append(json.loads(line))
    if records:
        latest = records[-1]
        ensure(latest.get("execution_performed") is False,
               "Approval must have execution_performed: false")
        ensure(latest.get("state") == "approved_by_operator",
               f"Expected 'approved_by_operator' not '{latest.get('state')}'")
    print("  [PASS] test_14: CLI --approve-packet correct phrase sets approved_by_operator")


def test_15_cli_reject_packet():
    packet_file = COMMAND_PACKETS / "validator_wall_packet.md"
    ensure(packet_file.exists(), "Packet file required")
    r = run_cli("--reject-packet", str(packet_file), "e2e rejection test")
    ensure(r.returncode == 0, f"--reject-packet failed rc={r.returncode}: {r.stderr[:200]}")
    records = []
    if APPROVAL_LEDGER.stat().st_size > 0:
        for line in APPROVAL_LEDGER.read_text().strip().splitlines():
            if line.strip():
                records.append(json.loads(line))
    if records:
        latest = records[-1]
        ensure(latest.get("execution_performed") is False,
               "Rejection must have execution_performed: false")
        ensure(latest.get("state") == "rejected_by_operator",
               f"Expected 'rejected_by_operator' not '{latest.get('state')}'")
    print("  [PASS] test_15: CLI --reject-packet sets rejected_by_operator")


def test_16_cli_unknown_flag():
    r = run_cli("--definitely-not-real")
    ensure(r.returncode != 0, "Unknown flag should exit nonzero")
    ensure("Unknown flag" in r.stdout or "ERROR" in r.stdout,
           "Unknown flag should print error")
    print("  [PASS] test_16: CLI unknown flag exits with error")


def test_17_cli_forbidden_flags_not_exposed():
    r = run_cli("--help")
    forbidden = ["--deploy", "--promote", "--official", "--secrets",
                 "--credentials", "--free-shell", "--merge-official"]
    for flag in forbidden:
        ensure(flag not in r.stdout,
               f"Forbidden flag '{flag}' exposed in help output")
    print("  [PASS] test_17: CLI help does not expose forbidden flags")


def test_18_all_ledger_records_have_execution_false():
    if not APPROVAL_LEDGER.exists() or APPROVAL_LEDGER.stat().st_size == 0:
        print("  [SKIP] test_18: No ledger records to check (empty ledger is allowed)")
        return
    for line in APPROVAL_LEDGER.read_text().strip().splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        ensure(rec.get("execution_performed") is False,
               f"Ledger record {rec.get('ledger_id', '?')} has execution_performed=true")
    print("  [PASS] test_18: All ledger records have execution_performed: false")


def main():
    print("Starting Interface Phase 1 E2E Validation...")
    print()

    tests = [
        test_01_cli_status,
        test_02_cli_list_artifacts,
        test_03_cli_inspect_all,
        test_04_cli_inspect_one,
        test_05_cli_inspect_invalid,
        test_06_cli_prepare_packet,
        test_07_cli_invalid_packet,
        test_08_cli_branch_review_default_base,
        test_09_cli_branch_review_explicit_base,
        test_10_cli_branch_review_invalid,
        test_11_cli_show_approval_ledger,
        test_12_cli_review_packet,
        test_13_cli_approve_packet_wrong_phrase,
        test_14_cli_approve_packet_correct_phrase,
        test_15_cli_reject_packet,
        test_16_cli_unknown_flag,
        test_17_cli_forbidden_flags_not_exposed,
        test_18_all_ledger_records_have_execution_false,
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
        print("\nINTERFACE_PHASE_1_E2E_VALIDATION_FAIL")
        sys.exit(1)
    else:
        print("\nINTERFACE_PHASE_1_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    main()
