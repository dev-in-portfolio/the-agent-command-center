#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SOURCE_DIST_PAIRS = [
    ("14_backend/schemas/phase4d_identity_schema.json", "13_web_dashboard/dist/phase4d_identity_schema.json"),
    ("14_backend/schemas/phase4d_action_schema.json", "13_web_dashboard/dist/phase4d_action_schema.json"),
    ("14_backend/schemas/phase4d_audit_schema.json", "13_web_dashboard/dist/phase4d_audit_schema.json"),
    ("14_backend/schemas/phase4d_risk_model.json", "13_web_dashboard/dist/phase4d_risk_model.json"),
]


def _fail(message):
    print(f"ERROR: {message}")
    sys.exit(1)


def _false_flags(payload, found=None):
    if found is None:
        found = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key.endswith("_implemented") or key.endswith("_added") or key.endswith("_read"):
                if isinstance(value, dict) and "const" in value:
                    found.append((key, value.get("const")))
                else:
                    found.append((key, value))
            _false_flags(value, found)
    elif isinstance(payload, list):
        for item in payload:
            _false_flags(item, found)
    return found


def main():
    required_docs = [
        "14_backend/phase_4d_identity_selection_recommendation.md",
        "14_backend/phase_4d_action_request_queue_schema.md",
        "14_backend/phase_4d_audit_event_schema.md",
        "14_backend/phase_4d_human_approval_schema.md",
        "14_backend/phase_4d_risk_classification_model.md",
    ]
    for rel in required_docs:
        if not (ROOT / rel).exists():
            _fail(f"Required file missing: {rel}")

    for source_rel, dist_rel in SOURCE_DIST_PAIRS:
        source_path = ROOT / source_rel
        dist_path = ROOT / dist_rel
        if not source_path.exists() or not dist_path.exists():
            _fail(f"Missing schema preview pair: {source_rel} -> {dist_rel}")
        source_payload = json.loads(source_path.read_text(encoding="utf-8"))
        dist_payload = json.loads(dist_path.read_text(encoding="utf-8"))
        if source_payload != dist_payload:
            _fail(f"Dist schema does not match source: {dist_rel}")
        for key, value in _false_flags(source_payload):
            if value is not False:
                _fail(f"Schema flag must be false: {source_rel}::{key}")

    approval_schema = ROOT / "14_backend/schemas/phase4d_approval_schema.json"
    if not approval_schema.exists():
        _fail("Required file missing: 14_backend/schemas/phase4d_approval_schema.json")
    approval_payload = json.loads(approval_schema.read_text(encoding="utf-8"))
    if approval_payload.get("schema_id") != "phase4d_approval_schema_v1":
        _fail("Approval schema id mismatch")

    print("BACKEND_PHASE_4D_SCHEMA_PREVIEW_VALIDATION_PASS")


if __name__ == "__main__":
    main()
