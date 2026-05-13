#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_TOP_LEVEL_FLAGS = {
    "schema_mode": "static_inert_schema_preview",
    "live_external_api_calls": False,
    "github_api_calls": False,
    "netlify_api_calls": False,
    "browser_external_fetches": False,
    "secrets_used": False,
    "tokens_used": False,
    "environment_variables_read": False,
    "command_execution": False,
    "github_mutation": False,
    "netlify_mutation": False,
    "deploy_controls": False,
    "merge_controls": False,
    "push_controls": False,
    "pr_controls": False,
    "action_execution": False,
    "action_queue_live": False,
}

SOURCE_DIST_PAIRS = [
    ("14_backend/schemas/phase4d_identity_schema.json", "13_web_dashboard/dist/phase4d_identity_schema.json"),
    ("14_backend/schemas/phase4d_action_schema.json", "13_web_dashboard/dist/phase4d_action_schema.json"),
    ("14_backend/schemas/phase4d_audit_schema.json", "13_web_dashboard/dist/phase4d_audit_schema.json"),
    ("14_backend/schemas/phase4d_approval_schema.json", "13_web_dashboard/dist/phase4d_approval_schema.json"),
    ("14_backend/schemas/phase4d_risk_model.json", "13_web_dashboard/dist/phase4d_risk_model.json"),
]


def _fail(message):
    print(f"ERROR: {message}")
    sys.exit(1)


def _validate_top_level_flags(source_rel, payload):
    for key, expected_value in REQUIRED_TOP_LEVEL_FLAGS.items():
        if payload.get(key) != expected_value:
            _fail(f"Schema top-level flag mismatch: {source_rel}::{key}")


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
        source_text = source_path.read_text(encoding="utf-8")
        dist_text = dist_path.read_text(encoding="utf-8")
        source_payload = json.loads(source_text)
        dist_payload = json.loads(dist_text)
        if source_payload != dist_payload:
            _fail(f"Dist schema does not match source: {dist_rel}")
        _validate_top_level_flags(source_rel, source_payload)
        for token in [
            "github_pat",
            "ghp_",
            "netlify_auth",
            "deploy hook",
            "deploy_hook",
            "secret_",
            "credential_",
            "access_token",
            "refresh_token",
            "private_key",
        ]:
            if token in source_text.lower() or token in dist_text.lower():
                _fail(f"Forbidden secret-like token found in schema: {source_rel}::{token}")

    print("BACKEND_PHASE_4D_SCHEMA_PREVIEW_VALIDATION_PASS")


if __name__ == "__main__":
    main()
