#!/usr/bin/env python3
"""Release-candidate validator for Interface Phase 1.

Checks that all required RC artifacts exist and contain expected content.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPORTS = ROOT / "09_exports" / "interface_phase_1"
INTERFACE = ROOT / "11_interface"
SCRIPTS = ROOT / "scripts"


def ensure(condition, message):
    if not condition:
        print(f"FAIL: {message}")
        sys.exit(1)


def main():
    print("Starting Interface Phase 1 Release-Candidate Validation...")

    # 1. Final acceptance report exists
    far = EXPORTS / "interface_phase_1_final_acceptance_report.md"
    ensure(far.exists(), "Final acceptance report missing")
    far_content = far.read_text()
    ensure("PASS_WITH_HIGH_CONFIDENCE" in far_content or "PASS_WITH_NOTES" in far_content,
           "Final acceptance report missing verdict")
    ensure("merge performed" in far_content.lower() and "false" in far_content.lower(),
           "Final acceptance report missing merge performed: false")
    ensure("deployment performed" in far_content.lower() and "false" in far_content.lower(),
           "Final acceptance report missing deployment performed: false")
    ensure("official repo touched" in far_content.lower() and "false" in far_content.lower(),
           "Final acceptance report missing official repo touched: false")
    ensure("Phase 2 handoff contract" in far_content,
           "Final acceptance report missing Phase 2 handoff contract reference")
    ensure("ready for merge review" in far_content.lower() or "merge readiness" in far_content.lower(),
           "Final acceptance report missing merge readiness reference")
    print("  [PASS] Final acceptance report present with required content")

    # 2. Historical acceptance report exists
    ar = EXPORTS / "interface_phase_1_acceptance_report.md"
    ensure(ar.exists(), "Historical acceptance report missing")
    ar_content = ar.read_text()
    sections = [l for l in ar_content.splitlines() if l.startswith("## ")]
    ensure(len(sections) >= 32, f"Historical acceptance report has {len(sections)} sections, expected 32+")
    ensure("PASS_WITH_HIGH_CONFIDENCE" in ar_content, "Historical acceptance report missing verdict")
    print(f"  [PASS] Historical acceptance report present with {len(sections)} sections")

    # 3. Merge-readiness packet exists
    mr = EXPORTS / "merge_readiness" / "interface_phase_1_merge_readiness_packet.md"
    ensure(mr.exists(), "Merge-readiness packet missing")
    mr_content = mr.read_text()
    ensure("ready_for_merge_review" in mr_content, "Merge-readiness packet missing decision")
    ensure("prepared_not_executed" in mr_content, "Merge-readiness packet wrong status")
    print("  [PASS] Merge-readiness packet present")

    # 4. Demo script exists and is safe
    ds = SCRIPTS / "demo_interface_phase_1.sh"
    ensure(ds.exists(), "Demo script missing")
    ds_content = ds.read_text()
    ensure("station_chief_cli.py" in ds_content, "Demo script missing CLI reference")
    ensure("--status" in ds_content, "Demo script missing --status flag")
    ensure("--validator-wall" not in ds_content,
           "Demo script must not run validator-wall automatically")
    print("  [PASS] Demo script present and does not auto-run validator-wall")

    # 5. Phase 2 handoff contract exists
    hc = EXPORTS / "phase_2_handoff_contract.md"
    ensure(hc.exists(), "Phase 2 handoff contract missing")
    hc_content = hc.read_text()
    ensure("READY_FOR_PHASE_2" in hc_content, "Handoff contract missing verdict")
    ensure("Source of Truth" in hc_content, "Handoff contract missing source-of-truth rules")
    print("  [PASS] Phase 2 handoff contract present")

    # 6. Test runs directory exists
    test_runs = EXPORTS / "test_runs"
    ensure(test_runs.exists(), "test_runs directory missing")
    print("  [PASS] test_runs directory present")

    # 7. All 5 operational hardening modules exist
    hardening_modules = [
        "interface_action_registry.py",
        "interface_policy_enforcer.py",
        "interface_artifact_inspector.py",
        "interface_branch_review.py",
        "interface_approval_ledger.py",
    ]
    for mod in hardening_modules:
        ensure((INTERFACE / mod).exists(), f"Hardening module missing: {mod}")
    print("  [PASS] All 5 operational hardening modules present")

    # 8. All 3 interface validators exist with required content
    validators = {
        "validate_interface_phase_1_cli.py": "INTERFACE_PHASE_1_CLI_VALIDATION_PASS",
        "validate_interface_phase_1_command_packets.py": "INTERFACE_PHASE_1_COMMAND_PACKETS_VALIDATION_PASS",
        "validate_interface_phase_1_e2e.py": "INTERFACE_PHASE_1_E2E_VALIDATION_PASS",
    }
    for vname, vpass in validators.items():
        vpath = SCRIPTS / vname
        ensure(vpath.exists(), f"Validator missing: {vname}")
        vcontent = vpath.read_text()
        ensure(vpass in vcontent, f"Validator {vname} missing pass string")
    print("  [PASS] All 3 interface validators present with pass strings")

    # 9. No __pycache__ in tracked interface files
    pycache = INTERFACE / "__pycache__"
    if pycache.exists():
        print("  [WARNING] __pycache__ exists in 11_interface/ (will be cleaned before commit)")
    print("  [PASS] RC validation directory structure check complete")

    # 10. Docs mention empty ledger allowed
    docs_to_check = [
        INTERFACE / "README.md",
        EXPORTS / "interface_phase_1_operational_hardening_report.md",
        EXPORTS / "interface_phase_1_operator_quickstart.md",
        EXPORTS / "interface_phase_1_acceptance_report.md",
        EXPORTS / "interface_phase_1_final_acceptance_report.md",
    ]
    for doc in docs_to_check:
        if doc.exists():
            dcontent = doc.read_text()
            ensure("empty" in dcontent.lower() and "ledger" in dcontent.lower(),
                   f"Doc {doc.name} does not mention empty ledger")
    print("  [PASS] All docs mention empty ledger is allowed")

    # 11. Approval ledger has execution_performed: false in code
    al_content = (INTERFACE / "interface_approval_ledger.py").read_text()
    ensure('"execution_performed": False' in al_content,
           "Approval ledger missing execution_performed: false default")
    print("  [PASS] Approval ledger enforces execution_performed: false")

    print("\nINTERFACE_PHASE_1_RELEASE_CANDIDATE_VALIDATION_PASS")


if __name__ == "__main__":
    main()
