#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def _fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)

def main():
    required_docs = [
        "14_backend/phase_4d_gate_review.md",
        "14_backend/phase_4d_gate_decision_matrix.md",
        "14_backend/phase_4d_action_request_readiness_checklist.md",
        "14_backend/phase_4d_forbidden_until_approved.md",
        "14_backend/phase_4d_human_approval_contract.md",
        "14_backend/phase_4d_audit_requirements.md",
        "14_backend/phase_4d_safe_next_steps.md",
    ]
    for f in required_docs:
        if not (ROOT / f).exists():
            _fail(f"Required file missing: {f}")

    # Content checks
    review_content = (ROOT / "14_backend/phase_4d_gate_review.md").read_text()
    if "NOT_APPROVED_FOR_MUTATION" not in review_content:
        _fail("Gate review missing NOT_APPROVED_FOR_MUTATION state")

    matrix_content = (ROOT / "14_backend/phase_4d_gate_decision_matrix.md").read_text()
    if "Verdict" not in matrix_content or "NOT_APPROVED_FOR_MUTATION" not in matrix_content:
        _fail("Gate matrix missing verdict")

    print("BACKEND_PHASE_4D_GATE_REVIEW_VALIDATION_PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
