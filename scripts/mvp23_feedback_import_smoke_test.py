#!/usr/bin/env python3
import os
import json
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULT_MD = ROOT / "09_exports" / "mvp_product_track" / "mvp23_feedback_import_smoke_test_result.md"
RESULT_JSON = ROOT / "09_exports" / "mvp_product_track" / "mvp23_feedback_import_smoke_test_result.json"

# GATES
TOKEN = os.environ.get("SUPABASE_TEST_ACCESS_TOKEN")
CONFIRMED = os.environ.get("MVP23_FEEDBACK_SMOKE_TEST_CONFIRMED") == "true"
TARGET_URL = os.environ.get("FEEDBACK_IMPORT_SMOKE_URL")


def redact(val):
    if not val: return "NOT_PROVIDED"
    return "*" * 8


def write_result(data):
    RESULT_JSON.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    md = f"""# MVP-23 Feedback Import Smoke Test Result

## Status
{data['status']}

## Verdict
{data['verdict']}

## Configuration
- **Target Host:** {data['target_url_host_only']}
- **Endpoint Status:** {data['endpoint_status']}
- **Feature Flag State:** {data['feature_flag_state_label']}
- **Import Attempted:** {data['import_attempted']}
- **Confirmation Set:** {CONFIRMED}
- **Token Present:** {bool(TOKEN)}

## Execution Details
- **Timestamp:** {data['timestamp']}
- **Import Result:** {data['import_result']}
- **Inserted ID Present:** {data['inserted_id_present']}

## Next Operator Step
{data['next_operator_step']}
"""
    RESULT_MD.write_text(md, encoding="utf-8")


def main():
    timestamp = datetime.now().isoformat()
    host = "NOT_PROVIDED"
    if TARGET_URL:
        from urllib.parse import urlparse
        host = urlparse(TARGET_URL).netloc

    result = {
        "status": "NOT_RUN",
        "verdict": "SKIPPED",
        "target_url_host_only": host,
        "endpoint_status": "UNKNOWN",
        "feature_flag_state_label": "UNKNOWN",
        "import_attempted": False,
        "import_result": "NONE",
        "inserted_id_present": False,
        "timestamp": timestamp,
        "next_operator_step": "set_env_vars_then_retry"
    }

    if not TARGET_URL:
        result["status"] = "TARGET_URL_NOT_PROVIDED"
        write_result(result)
        return

    # 1. Check Endpoint Status (GET action=status)
    try:
        url = f"{TARGET_URL}?action=status"
        with urllib.request.urlopen(url, timeout=10) as response:
            status_data = json.loads(response.read().decode("utf-8"))
            result["endpoint_status"] = status_data.get("status", "FAIL")
            result["feature_flag_state_label"] = status_data.get("persistence_gate", "UNKNOWN")
    except Exception as exc:
        result["status"] = "ENDPOINT_NOT_READY"
        result["import_result"] = str(exc)
        write_result(result)
        return

    # 2. Check Feature Flag
    if result["feature_flag_state_label"] != "ENABLED":
        result["status"] = "FEATURE_FLAG_DISABLED"
        result["next_operator_step"] = "enable_persistence_flag_for_test_path"
        write_result(result)
        return

    # 3. Check Confirmation and Token
    if not CONFIRMED:
        result["status"] = "SKIPPED_CONFIRMATION_NOT_SET"
        result["next_operator_step"] = "set_MVP23_FEEDBACK_SMOKE_TEST_CONFIRMED_to_true"
        write_result(result)
        return

    if not TOKEN:
        result["status"] = "TOKEN_NOT_PROVIDED"
        result["next_operator_step"] = "set_SUPABASE_TEST_ACCESS_TOKEN"
        write_result(result)
        return

    # 4. Perform Import (POST action=import)
    result["import_attempted"] = True
    payload = {
        "reviewer_persona": "mvp23_smoke_test_operator",
        "reviewer_context": "Controlled MVP-23 smoke test",
        "clarity_rating": 5,
        "confidence_rating": 5,
        "demo_readiness_rating": 5,
        "pitchability_rating": 5,
        "strongest_parts": "Smoke test verifies controlled feedback import path.",
        "confusing_parts": "None in smoke test.",
        "blockers": "None in smoke test.",
        "trust_concerns": "No secrets or tokens included.",
        "suggested_next_step": "Review smoke result and decide next product phase.",
        "would_share": False,
        "raw_packet": {"smoke_test": True, "phase": "MVP-23"},
        "source": "mvp23_smoke_test"
    }

    try:
        url = f"{TARGET_URL}?action=import"
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {TOKEN}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            res_body = json.loads(response.read().decode("utf-8"))
            if response.status == 201 and res_body.get("status") == "SUCCESS":
                result["status"] = "IMPORT_SMOKE_TEST_PASS"
                result["verdict"] = "PASS"
                result["import_result"] = "SUCCESS_201"
                result["inserted_id_present"] = "data" in res_body and "id" in res_body["data"]
                result["next_operator_step"] = "review_inserted_data_in_supabase_then_promote"
            else:
                result["status"] = "IMPORT_SMOKE_TEST_FAIL"
                result["import_result"] = f"UNEXPECTED_RESPONSE: {response.status}"
    except urllib.error.HTTPError as exc:
        result["status"] = "IMPORT_SMOKE_TEST_FAIL"
        result["import_result"] = f"HTTP_{exc.code}: {exc.read().decode('utf-8')}"
    except Exception as exc:
        result["status"] = "IMPORT_SMOKE_TEST_FAIL"
        result["import_result"] = str(exc)

    write_result(result)


if __name__ == "__main__":
    main()
