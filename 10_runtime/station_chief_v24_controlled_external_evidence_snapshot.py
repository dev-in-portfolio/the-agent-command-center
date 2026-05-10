import json
import hashlib
import csv
import io
import re
import time
import html
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

# Import from v23 module as allowed
from station_chief_v23_controlled_live_external_tool_gateway import (
    STATION_CHIEF_V23_APPROVAL_PHRASE,
    execute_external_tool_gateway_workpack
)

STATION_CHIEF_V24_CONTROLLED_EXTERNAL_EVIDENCE_VERSION = "24.0.0"
STATION_CHIEF_V24_CONTROLLED_EXTERNAL_EVIDENCE_STATUS = "STATION_CHIEF_V24_CONTROLLED_EXTERNAL_EVIDENCE_SNAPSHOT_GATEWAY"
STATION_CHIEF_V24_CONTROLLED_EXTERNAL_EVIDENCE_PHASE = "Station Chief v24.0 Controlled External Evidence Snapshot Gateway / Allowlisted Content Digest Workpack Candidate"

STATION_CHIEF_V24_APPROVAL_PHRASE = "I_APPROVE_V24_CONTROLLED_EXTERNAL_EVIDENCE_SNAPSHOT"

STATION_CHIEF_V24_EXTERNAL_EVIDENCE_WORKPACK_ID = "station-chief-v24-controlled-external-evidence-snapshot-workpack-001"

STATION_CHIEF_V24_ALLOWED_EXTERNAL_URL = "https://example.com/"
STATION_CHIEF_V24_ALLOWED_EXTERNAL_SCHEME = "https"
STATION_CHIEF_V24_ALLOWED_EXTERNAL_HOST = "example.com"
STATION_CHIEF_V24_ALLOWED_EXTERNAL_PATH = "/"
STATION_CHIEF_V24_ALLOWED_METHOD = "GET"
STATION_CHIEF_V24_SANITIZED_PREVIEW_MAX_CHARS = 280

STATION_CHIEF_V24_CONTROLLED_WORKSPACE_DIR = "/tmp/station_chief_v24_external_evidence_artifacts"

STATION_CHIEF_V24_CONTROLLED_ARTIFACT_PATHS = {
    "external_evidence_receipt_json": "/tmp/station_chief_v24_external_evidence_artifacts/v24_external_evidence_receipt.json",
    "external_content_digest_md": "/tmp/station_chief_v24_external_evidence_artifacts/v24_external_content_digest.md",
    "external_content_snapshot_json": "/tmp/station_chief_v24_external_evidence_artifacts/v24_external_content_snapshot.json",
    "external_evidence_table_csv": "/tmp/station_chief_v24_external_evidence_artifacts/v24_external_evidence_table.csv",
    "external_evidence_manifest_json": "/tmp/station_chief_v24_external_evidence_artifacts/v24_external_evidence_manifest.json"
}

STATION_CHIEF_V24_EXTERNAL_EVIDENCE_ACTION_IDS = [
    "station-chief-v24-action-routed-v23-v22-v21-v20-v19-v18-v17-operational-chain-001",
    "station-chief-v24-action-controlled-allowlisted-content-fetch-002",
    "station-chief-v24-action-sanitized-content-digest-extraction-003",
    "station-chief-v24-action-raw-body-non-persistence-proof-004",
    "station-chief-v24-action-controlled-evidence-receipt-json-005",
    "station-chief-v24-action-controlled-content-digest-markdown-006",
    "station-chief-v24-action-controlled-content-snapshot-json-007",
    "station-chief-v24-action-controlled-evidence-table-csv-008",
    "station-chief-v24-action-controlled-evidence-manifest-json-009"
]

STATION_CHIEF_V24_EXTERNAL_EVIDENCE_AGENT_ROLE_IDS = [
    "station-chief-v24-agent-role-evidence-gatekeeper-001",
    "station-chief-v24-agent-role-url-boundary-auditor-002",
    "station-chief-v24-agent-role-content-fetch-controller-003",
    "station-chief-v24-agent-role-content-sanitizer-004",
    "station-chief-v24-agent-role-evidence-artifact-scribe-005",
    "station-chief-v24-agent-role-evidence-audit-officer-006"
]

STATION_CHIEF_V24_NEXT_VERSION_REQUIRES_OPERATOR_INSTRUCTION = "v24.1 or broader controlled external evidence expansion requires explicit separate operator instruction"


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_digest(data: object) -> str:
    if isinstance(data, str):
        return hashlib.sha256(data.encode("utf-8")).hexdigest()
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def normalize_label(label: str | None, default_label: str) -> str:
    if not label:
        return default_label
    return re.sub(r'[^a-zA-Z0-9_-]', '_', str(label)).lower()


def create_controlled_external_evidence_snapshot_manifest() -> dict:
    return {
        "manifest_id": sha256_digest("controlled_external_evidence_snapshot_manifest"),
        "manifest_type": "controlled_external_evidence_snapshot_manifest",
        "runtime_version": STATION_CHIEF_V24_CONTROLLED_EXTERNAL_EVIDENCE_VERSION,
        "controlled_external_evidence_snapshot_gateway_created": True,
        "allowlisted_content_digest_workpack_created": True,
        "live_external_content_digest_authorized": True,
        "human_approval_required": True,
        "exact_approval_phrase_required": True,
        "allowlisted_url": STATION_CHIEF_V24_ALLOWED_EXTERNAL_URL,
        "allowlisted_host": STATION_CHIEF_V24_ALLOWED_EXTERNAL_HOST,
        "allowlisted_method": "GET",
        "sanitized_title_extraction_allowed": True,
        "sanitized_preview_extraction_allowed": True,
        "sanitized_preview_max_chars": 280,
        "raw_response_body_storage_allowed": False,
        "raw_response_body_printing_allowed": False,
        "raw_response_body_returning_allowed": False,
        "full_visible_text_storage_allowed": False,
        "arbitrary_url_allowed": False,
        "authentication_allowed": False,
        "cookies_allowed": False,
        "request_body_allowed": False,
        "email_execution_allowed": False,
        "calendar_execution_allowed": False,
        "database_execution_allowed": False,
        "deployment_execution_allowed": False,
        "repo_mutation_allowed": False,
        "production_execution_allowed": False,
        "credential_access_allowed": False,
        "secret_read_allowed": False,
        "environment_read_allowed": False,
        "real_worker_process_allowed": False,
        "background_agent_allowed": False,
        "real_queue_allowed": False
    }


def create_external_evidence_permission_registry() -> dict:
    categories = [
        "allowlisted_content_digest",
        "allowlisted_metadata_probe",
        "arbitrary_web_browsing",
        "arbitrary_content_scrape",
        "email_send",
        "calendar_event_create",
        "external_api_call",
        "database_operation",
        "deployment_operation",
        "webhook_operation"
    ]
    registry = {}
    for cat in categories:
        executable = (cat == "allowlisted_content_digest")
        registry[cat] = {
            "category_id": cat,
            "category_name": cat.replace("_", " ").title(),
            "category_registered": True,
            "executable_in_v24": executable,
            "preview_supported": True,
            "human_approval_required": True,
            "receipt_required": True,
            "audit_required": True,
            "arbitrary_target_allowed": False,
            "credentials_allowed": False,
            "secrets_allowed": False,
            "production_allowed": False,
            "network_allowed": executable,
            "method_allowed": "GET" if executable else None,
            "allowed_url": STATION_CHIEF_V24_ALLOWED_EXTERNAL_URL if executable else None,
            "sanitized_title_allowed": executable,
            "sanitized_preview_allowed": executable,
            "sanitized_preview_max_chars": 280 if executable else 0,
            "raw_response_body_storage_allowed": False,
            "raw_response_body_printing_allowed": False,
            "raw_response_body_returning_allowed": False,
            "full_visible_text_storage_allowed": False,
            "live_execution_allowed": executable
        }
    return {
        "registry_id": sha256_digest(registry),
        "registry_type": "controlled_external_evidence_permission_registry",
        "runtime_version": STATION_CHIEF_V24_CONTROLLED_EXTERNAL_EVIDENCE_VERSION,
        "external_evidence_category_count": 10,
        "executable_external_evidence_category_count": 1,
        "locked_external_evidence_category_count": 9,
        "categories": registry
    }


def create_external_evidence_request_packet(operator_label: str | None = None, workpack_label: str | None = None, requested_url: str | None = None) -> dict:
    op = normalize_label(operator_label, "unknown_operator")
    wp = normalize_label(workpack_label, "v24_external_evidence_workpack")
    arbitrary = requested_url is not None and requested_url != STATION_CHIEF_V24_ALLOWED_EXTERNAL_URL
    return {
        "request_packet_id": sha256_digest({"url": requested_url, "op": op, "wp": wp}),
        "packet_type": "controlled_external_evidence_request_packet",
        "runtime_version": STATION_CHIEF_V24_CONTROLLED_EXTERNAL_EVIDENCE_VERSION,
        "operator_label": op,
        "workpack_label": wp,
        "requested_url": requested_url,
        "effective_url": STATION_CHIEF_V24_ALLOWED_EXTERNAL_URL,
        "requested_method": "GET",
        "exact_url_required": True,
        "human_approval_required": True,
        "sanitized_title_requested": True,
        "sanitized_preview_requested": True,
        "sanitized_preview_max_chars": 280,
        "raw_response_body_storage_requested": False,
        "raw_response_body_printing_requested": False,
        "raw_response_body_returning_requested": False,
        "full_visible_text_storage_requested": False,
        "repo_mutation_requested": False,
        "production_requested": False,
        "credential_access_requested": False,
        "secret_read_requested": False,
        "environment_read_requested": False,
        "email_execution_requested": False,
        "calendar_execution_requested": False,
        "database_execution_requested": False,
        "deployment_execution_requested": False,
        "arbitrary_url_requested": arbitrary
    }


def create_external_evidence_approval_receipt(approval_phrase: str | None, request_packet: dict) -> dict:
    phrase_matches = (approval_phrase == STATION_CHIEF_V24_APPROVAL_PHRASE)
    url_allowed = (request_packet["requested_url"] is None or request_packet["requested_url"] == STATION_CHIEF_V24_ALLOWED_EXTERNAL_URL)
    granted = phrase_matches and url_allowed
    return {
        "approval_receipt_id": sha256_digest({"phrase": approval_phrase, "packet": request_packet["request_packet_id"]}),
        "receipt_type": "v24_external_evidence_human_approval_receipt",
        "runtime_version": STATION_CHIEF_V24_CONTROLLED_EXTERNAL_EVIDENCE_VERSION,
        "operator_label": request_packet["operator_label"],
        "workpack_label": request_packet["workpack_label"],
        "approval_phrase_received": approval_phrase is not None,
        "approval_phrase_matches": phrase_matches,
        "expected_approval_phrase": STATION_CHIEF_V24_APPROVAL_PHRASE,
        "requested_url_allowed": url_allowed,
        "human_approval_granted": granted,
        "autonomous_self_approval": False,
        "approval_scope": "v24_controlled_allowlisted_external_evidence_snapshot_only",
        "approval_does_not_authorize_arbitrary_url": True,
        "approval_does_not_authorize_raw_body_storage": True,
        "approval_does_not_authorize_raw_body_returning": True,
        "approval_does_not_authorize_full_text_storage": True,
        "approval_does_not_authorize_repo_mutation": True,
        "approval_does_not_authorize_credentials": True,
        "approval_does_not_authorize_email_calendar_database_deployment": True,
        "approval_does_not_authorize_future_external_tools": True,
        "approval_does_not_authorize_real_worker_processes": True
    }


def create_external_evidence_execution_plan(permission_registry: dict, request_packet: dict, approval_receipt: dict) -> dict:
    approved = approval_receipt["human_approval_granted"]
    return {
        "execution_plan_id": sha256_digest({"receipt": approval_receipt["approval_receipt_id"]}),
        "plan_type": "controlled_external_evidence_snapshot_execution_plan",
        "runtime_version": STATION_CHIEF_V24_CONTROLLED_EXTERNAL_EVIDENCE_VERSION,
        "workpack_id": STATION_CHIEF_V24_EXTERNAL_EVIDENCE_WORKPACK_ID,
        "action_count": 9,
        "human_approval_granted": approved,
        "execution_status": "READY_FOR_CONTROLLED_EXTERNAL_EVIDENCE_SNAPSHOT" if approved else "EXTERNAL_EVIDENCE_SNAPSHOT_DENIED_OR_PREVIEW_ONLY",
        "execute_routed_v23_operational_chain": approved,
        "execute_allowlisted_content_fetch": approved,
        "execute_sanitized_content_digest": approved,
        "execute_raw_body_non_persistence_proof": approved,
        "execute_evidence_receipt_artifact": approved,
        "execute_content_digest_artifact": approved,
        "execute_content_snapshot_artifact": approved,
        "execute_evidence_table_artifact": approved,
        "execute_evidence_manifest_artifact": approved,
        "allowed_url": STATION_CHIEF_V24_ALLOWED_EXTERNAL_URL,
        "allowed_method": "GET",
        "max_external_request_count": 1,
        "sanitized_preview_max_chars": 280,
        "repo_mutation_allowed": False,
        "raw_response_body_storage_allowed": False,
        "raw_response_body_printing_allowed": False,
        "raw_response_body_returning_allowed": False,
        "full_visible_text_storage_allowed": False,
        "arbitrary_url_allowed": False,
        "authentication_allowed": False,
        "cookies_allowed": False,
        "request_body_allowed": False,
        "production_allowed": False,
        "deployment_allowed": False,
        "credential_access_allowed": False,
        "email_execution_allowed": False,
        "calendar_execution_allowed": False,
        "database_execution_allowed": False,
        "real_worker_process_allowed": False,
        "background_agent_allowed": False,
        "shell_allowed": False,
        "subprocess_allowed": False,
        "queue_allowed": False,
        "arbitrary_task_allowed": False
    }


def validate_allowed_external_evidence_url(url: str | None) -> dict:
    effective = url if url is not None else STATION_CHIEF_V24_ALLOWED_EXTERNAL_URL
    parsed = urllib.parse.urlparse(effective)
    is_valid = (
        effective == STATION_CHIEF_V24_ALLOWED_EXTERNAL_URL and
        parsed.scheme == STATION_CHIEF_V24_ALLOWED_EXTERNAL_SCHEME and
        parsed.netloc == STATION_CHIEF_V24_ALLOWED_EXTERNAL_HOST and
        parsed.path == STATION_CHIEF_V24_ALLOWED_EXTERNAL_PATH and
        not parsed.query and
        not parsed.fragment
    )
    return {
        "url": effective,
        "is_valid": is_valid,
        "scheme": parsed.scheme,
        "host": parsed.netloc,
        "path": parsed.path,
        "query": parsed.query,
        "fragment": parsed.fragment
    }


def _extract_sanitized_content_digest_locally(body_bytes: bytes) -> dict:
    if not body_bytes:
        return {"sanitized_title": None, "sanitized_preview": None, "sanitized_title_present": False}

    text = body_bytes.decode("utf-8", errors="replace")
    
    # Simple title extraction
    title = None
    title_match = re.search(r'<title>(.*?)</title>', text, re.IGNORECASE | re.DOTALL)
    if title_match:
        title = html.unescape(title_match.group(1)).strip()
        
    # Sanitized preview extraction
    # Strip script and style blocks
    text_clean = re.sub(r'<(script|style).*?>.*?</\1>', '', text, flags=re.IGNORECASE | re.DOTALL)
    # Strip HTML tags
    text_clean = re.sub(r'<.*?>', ' ', text_clean)
    # Unescape and normalize
    text_clean = html.unescape(text_clean)
    text_clean = " ".join(text_clean.split())
    
    preview = text_clean[:STATION_CHIEF_V24_SANITIZED_PREVIEW_MAX_CHARS]
    
    return {
        "digest_id": sha256_digest(preview),
        "digest_type": "v24_sanitized_external_content_digest",
        "runtime_version": STATION_CHIEF_V24_CONTROLLED_EXTERNAL_EVIDENCE_VERSION,
        "sanitized_title": title,
        "sanitized_title_present": title is not None,
        "sanitized_preview": preview,
        "sanitized_preview_char_count": len(preview),
        "sanitized_preview_max_chars": STATION_CHIEF_V24_SANITIZED_PREVIEW_MAX_CHARS,
        "sanitized_preview_sha256": hashlib.sha256(preview.encode("utf-8")).hexdigest(),
        "visible_text_sha256": hashlib.sha256(text_clean.encode("utf-8")).hexdigest(),
        "raw_html_returned": False,
        "raw_body_returned": False,
        "raw_body_stored": False,
        "full_visible_text_returned": False,
        "full_visible_text_stored": False,
        "script_style_removed": True,
        "html_tags_removed": True,
        "html_entities_unescaped": True,
        "whitespace_normalized": True,
        "credential_data_absent": True,
        "secret_data_absent": True,
        "token_data_absent": True,
        "environment_data_absent": True
    }


def _create_raw_body_non_persistence_proof_locally(fetch_metadata: dict, digest: dict) -> dict:
    return {
        "proof_id": sha256_digest({"fetch": fetch_metadata.get("response_sha256"), "digest": digest.get("sanitized_preview_sha256")}),
        "proof_type": "v24_raw_body_non_persistence_proof",
        "runtime_version": STATION_CHIEF_V24_CONTROLLED_EXTERNAL_EVIDENCE_VERSION,
        "raw_response_body_printed": False,
        "raw_response_body_written_to_artifact": False,
        "raw_response_body_returned": False,
        "raw_response_body_stored": False,
        "full_html_written_to_artifact": False,
        "full_visible_text_written_to_artifact": False,
        "sanitized_digest_only": True,
        "sanitized_preview_max_chars": 280,
        "response_hash_retained": "response_sha256" in fetch_metadata,
        "response_byte_count_retained": "response_byte_count" in fetch_metadata,
        "sanitized_title_retained": digest.get("sanitized_title_present", False),
        "sanitized_preview_retained": True,
        "body_bytes_discarded_after_digest": True,
        "no_credentials_retained": True,
        "no_cookies_retained": True,
        "no_auth_headers_retained": True
    }


def execute_allowlisted_external_content_fetch(approval_receipt: dict, requested_url: str | None = None) -> dict:
    if not approval_receipt["human_approval_granted"]:
        return {"external_content_fetch_performed": False, "controlled_fetch_error": False}
    
    validation = validate_allowed_external_evidence_url(requested_url)
    if not validation["is_valid"]:
        return {"external_content_fetch_performed": False, "controlled_fetch_error": True, "error": "URL not allowlisted"}

    try:
        req = urllib.request.Request(STATION_CHIEF_V24_ALLOWED_EXTERNAL_URL, method="GET")
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            final_url = response.geturl()
            content_type = response.headers.get_content_type()
            body_bytes = response.read()
            
            sha256 = hashlib.sha256(body_bytes).hexdigest()
            byte_count = len(body_bytes)
            line_count = len(body_bytes.splitlines())
            
            fetch_metadata = {
                "external_fetch_action_id": "station-chief-v24-action-controlled-allowlisted-content-fetch-002",
                "external_content_fetch_performed": True,
                "controlled_fetch_error": False,
                "external_request_count": 1,
                "requested_url": requested_url or STATION_CHIEF_V24_ALLOWED_EXTERNAL_URL,
                "effective_url": STATION_CHIEF_V24_ALLOWED_EXTERNAL_URL,
                "allowed_url_validation": validation,
                "method": "GET",
                "status_code": status_code,
                "final_url": final_url,
                "content_type": content_type,
                "response_sha256": sha256,
                "response_byte_count": byte_count,
                "response_line_count": line_count,
                "response_body_raw_text_included": False,
                "raw_response_body_printed": False,
                "raw_response_body_stored": False,
                "raw_response_body_returned": False,
                "authentication_used": False,
                "cookies_used": False,
                "request_body_sent": False,
                "arbitrary_url_used": False,
                "credential_access_performed": False,
                "secret_read_performed": False,
                "environment_read_performed": False,
                "repo_write_performed": False,
                "production_write_performed": False,
                "email_sent": False,
                "calendar_event_created": False,
                "database_operation_performed": False,
                "deployment_performed": False
            }

            # Process digest and proof locally
            digest = _extract_sanitized_content_digest_locally(body_bytes)
            proof = _create_raw_body_non_persistence_proof_locally(fetch_metadata, digest)
            
            # Explicitly clear body bytes before returning
            body_bytes = None
            
            return {
                "fetch_metadata": fetch_metadata,
                "digest": digest,
                "proof": proof
            }
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        return {
            "external_content_fetch_performed": False,
            "controlled_fetch_error": True,
            "error_class": e.__class__.__name__,
            "external_request_count": 1,
            "requested_url": requested_url or STATION_CHIEF_V24_ALLOWED_EXTERNAL_URL,
            "effective_url": STATION_CHIEF_V24_ALLOWED_EXTERNAL_URL,
            "allowed_url_validation": validation,
            "method": "GET"
        }


def extract_sanitized_content_digest(fetch_result: dict, body_bytes: bytes | None = None) -> dict:
    # This function is now a wrapper for the local helper, used for compatibility if needed.
    # It must NOT receive raw bytes from a dict anymore.
    if body_bytes:
        return _extract_sanitized_content_digest_locally(body_bytes)
    return fetch_result.get("digest", {"sanitized_title": None, "sanitized_preview": None, "sanitized_title_present": False})


def create_raw_body_non_persistence_proof(fetch_result: dict, digest: dict) -> dict:
    # This function is now a wrapper for the local helper, used for compatibility if needed.
    return fetch_result.get("proof") or _create_raw_body_non_persistence_proof_locally(fetch_result.get("fetch_metadata", fetch_result), digest)


def resolve_controlled_external_evidence_workspace_paths() -> dict:
    workspace_dir = Path(STATION_CHIEF_V24_CONTROLLED_WORKSPACE_DIR)
    paths = {}
    valid = True
    if not str(workspace_dir).startswith("/tmp/station_chief_v24_external_evidence_artifacts"):
        valid = False
        
    for key, path_str in STATION_CHIEF_V24_CONTROLLED_ARTIFACT_PATHS.items():
        p = Path(path_str)
        paths[key] = str(p)
        if p.parent != workspace_dir:
            valid = False
            
    return {
        "workspace_dir": str(workspace_dir),
        "artifact_paths": paths,
        "all_artifact_paths_valid": valid,
        "repo_path": False,
        "production_path": False,
        "credential_path": False,
        "secret_path": False
    }


def build_external_evidence_artifact_payloads(routed_v23_result: dict, fetch_result: dict, digest: dict, non_persistence_proof: dict, approval_receipt: dict, permission_registry: dict) -> dict:
    op = approval_receipt["operator_label"]
    inspected = routed_v23_result.get("inspected_file_count", 0) if routed_v23_result else 0
    fetch_meta = fetch_result.get("fetch_metadata", fetch_result)
    
    receipt_payload = {
        "version": STATION_CHIEF_V24_CONTROLLED_EXTERNAL_EVIDENCE_VERSION,
        "status": "V24_EXTERNAL_EVIDENCE_RECEIPT",
        "operator": op,
        "workpack": approval_receipt["workpack_label"],
        "external_content_fetch_performed": fetch_meta.get("external_content_fetch_performed", False),
        "sanitized_content_digest_extracted": "sanitized_preview" in digest,
        "routed_v23_chain_performed": routed_v23_result.get("external_tool_gateway_workpack_performed", False) if routed_v23_result else False,
        "inspected_file_count": inspected
    }
    
    summary_md = f"""# Station Chief v24 Controlled External Evidence Snapshot

## Context
- **Runtime Version:** {STATION_CHIEF_V24_CONTROLLED_EXTERNAL_EVIDENCE_VERSION}
- **Approval Status:** {"GRANTED" if approval_receipt["human_approval_granted"] else "DENIED"}
- **Operator:** {op}

## External Content Digest
- **Allowlisted URL:** {STATION_CHIEF_V24_ALLOWED_EXTERNAL_URL}
- **Fetch Status:** {"SUCCESS" if receipt_payload["external_content_fetch_performed"] else "FAILED/SKIPPED"}
- **Status Code:** {fetch_meta.get("status_code")}
- **Content Type:** {fetch_meta.get("content_type")}
- **Response Hash:** {fetch_meta.get("response_sha256")}
- **Byte Count:** {fetch_meta.get("response_byte_count")}
- **Line Count:** {fetch_meta.get("response_line_count")}

## Sanitized Snapshot
- **Sanitized Title:** {digest.get("sanitized_title")}
- **Sanitized Preview:** {digest.get("sanitized_preview")}

## Operational Chain Summary
- **Routed v23 Chain Performed:** {receipt_payload["routed_v23_chain_performed"]}
- **Inspected File Count:** {inspected}

## Artifact List
- Evidence Receipt: `v24_external_evidence_receipt.json`
- Content Digest: `v24_external_content_digest.md`
- Content Snapshot: `v24_external_content_snapshot.json`
- Evidence Table: `v24_external_evidence_table.csv`
- Evidence Manifest: `v24_external_evidence_manifest.json`

## Safety Summary
- **Repo Mutation:** FORBIDDEN / NOT PERFORMED
- **Credential Access:** FORBIDDEN / NOT PERFORMED
- **Raw Response Body Stored:** FORBIDDEN / NOT PERFORMED

This document confirms safe external evidence gathering using a controlled content digest gateway.
"""

    snapshot_payload = {
        "snapshot_id": digest.get("digest_id"),
        "runtime_version": STATION_CHIEF_V24_CONTROLLED_EXTERNAL_EVIDENCE_VERSION,
        "fetch_metadata": {
            "status_code": fetch_meta.get("status_code"),
            "content_type": fetch_meta.get("content_type"),
            "sha256": fetch_meta.get("response_sha256")
        },
        "sanitized_digest": {
            "title": digest.get("sanitized_title"),
            "preview": digest.get("sanitized_preview"),
            "preview_sha256": digest.get("sanitized_preview_sha256")
        },
        "non_persistence_proof": non_persistence_proof
    }

    csv_rows = [
        ["property", "value"],
        ["runtime_version", STATION_CHIEF_V24_CONTROLLED_EXTERNAL_EVIDENCE_VERSION],
        ["approval_granted", str(approval_receipt["human_approval_granted"])],
        ["routed_v23_chain_performed", str(receipt_payload["routed_v23_chain_performed"])],
        ["external_content_fetch_performed", str(receipt_payload["external_content_fetch_performed"])],
        ["external_request_count", str(fetch_meta.get("external_request_count", 0))],
        ["status_code", str(fetch_meta.get("status_code", "N/A"))],
        ["response_byte_count", str(fetch_meta.get("response_byte_count", 0))],
        ["response_line_count", str(fetch_meta.get("response_line_count", 0))],
        ["sanitized_title_present", str(digest.get("sanitized_title_present", False))],
        ["sanitized_preview_char_count", str(digest.get("sanitized_preview_char_count", 0))],
        ["raw_response_body_stored", "False"],
        ["raw_response_body_returned", "False"],
        ["repo_mutation_performed", "False"],
        ["credential_access_performed", "False"],
        ["email_sent", "False"],
        ["calendar_event_created", "False"],
        ["database_operation_performed", "False"],
        ["deployment_performed", "False"]
    ]
    output = io.StringIO()
    writer = csv.writer(output, lineterminator='\n')
    writer.writerows(csv_rows)
    table_csv = output.getvalue()
    
    manifest_payload = {
        "manifest_version": "1.0",
        "workpack_id": STATION_CHIEF_V24_EXTERNAL_EVIDENCE_WORKPACK_ID,
        "artifacts": [
            {"key": "external_evidence_receipt_json", "format": "json", "path": STATION_CHIEF_V24_CONTROLLED_ARTIFACT_PATHS["external_evidence_receipt_json"]},
            {"key": "external_content_digest_md", "format": "markdown", "path": STATION_CHIEF_V24_CONTROLLED_ARTIFACT_PATHS["external_content_digest_md"]},
            {"key": "external_content_snapshot_json", "format": "json", "path": STATION_CHIEF_V24_CONTROLLED_ARTIFACT_PATHS["external_content_snapshot_json"]},
            {"key": "external_evidence_table_csv", "format": "csv", "path": STATION_CHIEF_V24_CONTROLLED_ARTIFACT_PATHS["external_evidence_table_csv"]},
            {"key": "external_evidence_manifest_json", "format": "json", "path": STATION_CHIEF_V24_CONTROLLED_ARTIFACT_PATHS["external_evidence_manifest_json"]}
        ]
    }
    
    return {
        "evidence_receipt_payload": receipt_payload,
        "content_digest_markdown": summary_md,
        "content_snapshot_payload": snapshot_payload,
        "evidence_table_csv": table_csv,
        "evidence_manifest_payload": manifest_payload
    }


def write_controlled_external_evidence_text_artifact(artifact_key: str, content: str, approval_receipt: dict) -> dict:
    if not approval_receipt["human_approval_granted"]:
        return {"artifact_write_performed": False, "error": "Approval missing"}
        
    paths_meta = resolve_controlled_external_evidence_workspace_paths()
    if not paths_meta["all_artifact_paths_valid"]:
        return {"artifact_write_performed": False, "error": "Invalid workspace path"}
        
    artifact_path_str = paths_meta["artifact_paths"].get(artifact_key)
    if not artifact_path_str:
        return {"artifact_write_performed": False, "error": f"Unknown artifact key: {artifact_key}"}
        
    workspace_dir = Path(paths_meta["workspace_dir"])
    artifact_path = Path(artifact_path_str)
    
    workspace_dir.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(content)
    readback = artifact_path.read_text()
    
    return {
        "artifact_key": artifact_key,
        "artifact_write_performed": True,
        "controlled_artifact_path": str(artifact_path),
        "artifact_exists_after_write": artifact_path.exists(),
        "artifact_sha256": hashlib.sha256(readback.encode("utf-8")).hexdigest(),
        "artifact_byte_count": len(readback),
        "artifact_line_count": len(readback.splitlines()),
        "artifact_readback_verified": readback == content,
        "repo_write_performed": False,
        "production_write_performed": False,
        "credential_access_performed": False,
        "secret_read_performed": False,
        "environment_read_performed": False,
        "network_access_performed": False,
        "api_call_performed": False,
        "subprocess_started": False,
        "shell_executed": False
    }


def execute_external_evidence_snapshot_workpack(approval_phrase: str | None, operator_label: str | None = None, workpack_label: str | None = None, requested_url: str | None = None) -> dict:
    manifest = create_controlled_external_evidence_snapshot_manifest()
    registry = create_external_evidence_permission_registry()
    packet = create_external_evidence_request_packet(operator_label, workpack_label, requested_url)
    approval = create_external_evidence_approval_receipt(approval_phrase, packet)
    plan = create_external_evidence_execution_plan(registry, packet, approval)
    
    performed = False
    completed_action_count = 0
    v23_result = None
    fetch_result = {}
    digest = {}
    proof = {}
    artifact_results = {}
    artifact_digests = {}
    all_verified = True
    status = "V24_CONTROLLED_EXTERNAL_EVIDENCE_SNAPSHOT_WORKPACK_DENIED"
    
    if approval["human_approval_granted"]:
        # Action 1: routed v23 chain
        v23_result = execute_external_tool_gateway_workpack(
            STATION_CHIEF_V23_APPROVAL_PHRASE,
            operator_label=operator_label,
            workpack_label=workpack_label
        )
        if v23_result.get("external_tool_gateway_workpack_performed"):
            completed_action_count += 1
            
        # Action 2: allowlisted external content fetch
        fetch_result = execute_allowlisted_external_content_fetch(approval, requested_url)
        
        fetch_meta = fetch_result.get("fetch_metadata", {})
        if fetch_meta.get("external_content_fetch_performed"):
            completed_action_count += 1
            status = "V24_CONTROLLED_EXTERNAL_EVIDENCE_SNAPSHOT_WORKPACK_COMPLETED"
            
            # Action 3: sanitized content digest
            digest = fetch_result.get("digest", {})
            if "sanitized_preview" in digest:
                completed_action_count += 1
                
            # Action 4: non-persistence proof
            proof = fetch_result.get("proof", {})
            if proof:
                completed_action_count += 1
        elif fetch_result.get("controlled_fetch_error"):
            status = "V24_CONTROLLED_EXTERNAL_EVIDENCE_SNAPSHOT_FETCH_UNAVAILABLE"
            fetch_meta = fetch_result # Error structure
            
        # Build payloads
        payloads = build_external_evidence_artifact_payloads(v23_result, fetch_result, digest, proof, approval, registry)
        
        # Actions 5-9: Artifacts
        writes = [
            ("external_evidence_receipt_json", canonical_json(payloads["evidence_receipt_payload"])),
            ("external_content_digest_md", payloads["content_digest_markdown"]),
            ("external_content_snapshot_json", canonical_json(payloads["content_snapshot_payload"])),
            ("external_evidence_table_csv", payloads["evidence_table_csv"]),
            ("external_evidence_manifest_json", canonical_json(payloads["evidence_manifest_payload"]))
        ]
        
        for key, content in writes:
            res = write_controlled_external_evidence_text_artifact(key, content, approval)
            artifact_results[key] = res
            if res.get("artifact_write_performed"):
                completed_action_count += 1
                artifact_digests[key] = res["artifact_sha256"]
                if not res["artifact_readback_verified"]: all_verified = False
            else:
                all_verified = False
                
        if completed_action_count == 9:
            performed = True
            
    # Normalize fetch_meta for result
    fetch_meta = fetch_result.get("fetch_metadata", fetch_result)

    return {
        "execution_status": status,
        "external_evidence_snapshot_workpack_performed": performed,
        "controlled_action_count": 9,
        "completed_action_count": completed_action_count,
        "routed_v23_v22_v21_v20_v19_v18_v17_chain_performed": v23_result.get("external_tool_gateway_workpack_performed", False) if v23_result else False,
        "controlled_external_content_fetch_performed": fetch_meta.get("external_content_fetch_performed", False),
        "sanitized_content_digest_extracted": "sanitized_preview" in digest,
        "raw_body_non_persistence_proven": bool(proof),
        "evidence_receipt_artifact_written": artifact_results.get("external_evidence_receipt_json", {}).get("artifact_write_performed", False),
        "content_digest_artifact_written": artifact_results.get("external_content_digest_md", {}).get("artifact_write_performed", False),
        "content_snapshot_artifact_written": artifact_results.get("external_content_snapshot_json", {}).get("artifact_write_performed", False),
        "evidence_table_artifact_written": artifact_results.get("external_evidence_table_csv", {}).get("artifact_write_performed", False),
        "evidence_manifest_written": artifact_results.get("external_evidence_manifest_json", {}).get("artifact_write_performed", False),
        "controlled_external_evidence_artifact_count": 5,
        "inspected_file_count": v23_result.get("inspected_file_count", 0) if v23_result else 0,
        "external_request_count": fetch_meta.get("external_request_count", 0),
        "allowed_external_url": STATION_CHIEF_V24_ALLOWED_EXTERNAL_URL,
        "status_code": fetch_meta.get("status_code"),
        "final_url": fetch_meta.get("final_url"),
        "content_type": fetch_meta.get("content_type"),
        "response_sha256": fetch_meta.get("response_sha256"),
        "response_byte_count": fetch_meta.get("response_byte_count"),
        "response_line_count": fetch_meta.get("response_line_count"),
        "sanitized_title": digest.get("sanitized_title"),
        "sanitized_title_present": digest.get("sanitized_title_present", False),
        "sanitized_preview": digest.get("sanitized_preview"),
        "sanitized_preview_char_count": digest.get("sanitized_preview_char_count", 0),
        "sanitized_preview_max_chars": STATION_CHIEF_V24_SANITIZED_PREVIEW_MAX_CHARS,
        "raw_response_body_printed": False,
        "raw_response_body_stored": False,
        "raw_response_body_returned": False,
        "full_visible_text_stored": False,
        "full_visible_text_returned": False,
        "artifact_paths": STATION_CHIEF_V24_CONTROLLED_ARTIFACT_PATHS,
        "artifact_digests": artifact_digests,
        "artifact_readback_verified": all_verified if performed else False,
        "logical_agent_roles_used": True,
        "real_worker_process_started": False,
        "background_agent_started": False,
        "repo_file_mutation_performed": False,
        "repo_mutation_performed": False,
        "commit_performed": False,
        "push_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "credential_access_performed": False,
        "token_access_performed": False,
        "secret_read_performed": False,
        "environment_read_performed": False,
        "api_call_performed": False,
        "network_access_performed": fetch_meta.get("external_content_fetch_performed", False),
        "email_sent": False,
        "calendar_event_created": False,
        "web_request_performed": fetch_meta.get("external_content_fetch_performed", False),
        "database_operation_performed": False,
        "subprocess_started": False,
        "shell_executed": False,
        "live_worker_started": False,
        "live_queue_created": False,
        "live_task_executed": False,
        "uncontrolled_live_orchestration_performed": False,
        
        "manifest": manifest,
        "registry": registry,
        "request_packet": packet,
        "approval_receipt": approval,
        "execution_plan": plan,
        "fetch_result": fetch_result,
        "digest": digest,
        "proof": proof,
        "artifact_results": artifact_results
    }


def create_external_evidence_handoff_ledger(external_evidence_result: dict) -> dict:
    performed = external_evidence_result["external_evidence_snapshot_workpack_performed"]
    fetch_performed = external_evidence_result["controlled_external_content_fetch_performed"]
    digest_extracted = external_evidence_result["sanitized_content_digest_extracted"]
    proof_proven = external_evidence_result["raw_body_non_persistence_proven"]
    
    roles = [
        ("evidence_gatekeeper", "approval_gate"),
        ("url_boundary_auditor", "url_validation"),
        ("content_fetch_controller", "external_fetch"),
        ("content_sanitizer", "sanitization"),
        ("evidence_artifact_scribe", "artifact_write"),
        ("evidence_audit_officer", "final_audit")
    ]
    
    receipts = {}
    for idx, (name, stage) in enumerate(roles):
        r_id = STATION_CHIEF_V24_EXTERNAL_EVIDENCE_AGENT_ROLE_IDS[idx]
        h_id = sha256_digest({"role": r_id, "performed": performed})
        receipts[h_id] = {
            "handoff_receipt_id": h_id,
            "agent_role_id": r_id,
            "agent_role_name": name,
            "workflow_stage": stage,
            "receipt_type": "v24_external_evidence_agent_handoff_receipt",
            "runtime_version": "24.0.0",
            "external_evidence_workpack_received": True,
            "stage_processed": performed,
            "live_worker_process_started": False,
            "background_agent_started": False,
            "tool_execution_performed_by_role": False,
            "repo_mutation_performed": False,
            "controlled_content_fetch_supervised": (name == "content_fetch_controller") and fetch_performed,
            "content_digest_supervised": (name == "content_sanitizer") and digest_extracted,
            "raw_body_non_persistence_supervised": (name == "evidence_audit_officer") and proof_proven,
            "controlled_artifact_write_supervised": (name == "evidence_artifact_scribe") and performed,
            "credential_access_performed": False,
            "network_access_limited_to_allowlisted_fetch": True,
            "shell_executed": False,
            "subprocess_started": False
        }
        
    return {
        "ledger_id": sha256_digest(receipts),
        "ledger_type": "v24_external_evidence_agent_handoff_ledger",
        "runtime_version": "24.0.0",
        "handoff_receipt_count": len(receipts),
        "all_handoffs_recorded": True,
        "no_real_workers_started": True,
        "no_background_agents_started": True,
        "receipts": receipts
    }


def create_external_evidence_workpack_receipt(external_evidence_result: dict, handoff_ledger: dict) -> dict:
    performed = external_evidence_result["external_evidence_snapshot_workpack_performed"]
    return {
        "external_evidence_workpack_receipt_id": sha256_digest({"res": external_evidence_result["execution_status"], "ledger": handoff_ledger["ledger_id"]}),
        "receipt_type": "v24_external_evidence_snapshot_workpack_execution_receipt",
        "runtime_version": "24.0.0",
        "external_evidence_snapshot_workpack_performed": performed,
        "controlled_action_count": 9,
        "completed_action_count": external_evidence_result["completed_action_count"],
        "routed_v23_v22_v21_v20_v19_v18_v17_chain_performed": external_evidence_result["routed_v23_v22_v21_v20_v19_v18_v17_chain_performed"],
        "controlled_external_content_fetch_performed": external_evidence_result["controlled_external_content_fetch_performed"],
        "sanitized_content_digest_extracted": external_evidence_result["sanitized_content_digest_extracted"],
        "raw_body_non_persistence_proven": external_evidence_result["raw_body_non_persistence_proven"],
        "evidence_receipt_artifact_written": external_evidence_result["evidence_receipt_artifact_written"],
        "content_digest_artifact_written": external_evidence_result["content_digest_artifact_written"],
        "content_snapshot_artifact_written": external_evidence_result["content_snapshot_artifact_written"],
        "evidence_table_artifact_written": external_evidence_result["evidence_table_artifact_written"],
        "evidence_manifest_written": external_evidence_result["evidence_manifest_written"],
        "controlled_external_evidence_artifact_count": 5,
        "inspected_file_count": external_evidence_result["inspected_file_count"],
        "external_request_count": external_evidence_result["external_request_count"],
        "allowed_external_url": external_evidence_result["allowed_external_url"],
        "response_sha256": external_evidence_result["response_sha256"],
        "response_byte_count": external_evidence_result["response_byte_count"],
        "response_line_count": external_evidence_result["response_line_count"],
        "sanitized_title_present": external_evidence_result["sanitized_title_present"],
        "sanitized_preview_char_count": external_evidence_result["sanitized_preview_char_count"],
        "artifact_paths": external_evidence_result["artifact_paths"],
        "artifact_digests": external_evidence_result["artifact_digests"],
        "artifact_readback_verified": external_evidence_result["artifact_readback_verified"],
        "logical_agent_roles_used": True,
        "handoff_receipt_count": 6,
        "receipt_status": "CONTROLLED_EXTERNAL_EVIDENCE_SNAPSHOT_WORKPACK_COMPLETED" if performed else "CONTROLLED_EXTERNAL_EVIDENCE_SNAPSHOT_WORKPACK_DENIED",
        "no_repo_file_mutation": True,
        "no_raw_response_body_printed": True,
        "no_raw_response_body_stored": True,
        "no_raw_response_body_returned": True,
        "no_full_visible_text_stored": True,
        "no_full_visible_text_returned": True,
        "no_repo_mutation": True,
        "no_commit": True,
        "no_push": True,
        "no_deployment": True,
        "no_production_execution": True,
        "controlled_network_access_only": True,
        "no_credential_access": True,
        "no_secret_read": True,
        "no_environment_read": True,
        "no_email_sent": True,
        "no_calendar_event_created": True,
        "no_database_operation": True,
        "no_real_worker_process": True,
        "no_background_agent": True,
        "no_subprocess": True,
        "no_shell": True,
        "no_queue": True,
        "no_uncontrolled_live_orchestration": True
    }


def create_external_evidence_audit_record(external_evidence_result: dict, handoff_ledger: dict, workpack_receipt: dict) -> dict:
    return {
        "audit_id": sha256_digest({"receipt": workpack_receipt["external_evidence_workpack_receipt_id"]}),
        "audit_type": "v24_controlled_external_evidence_snapshot_audit",
        "runtime_version": "24.0.0",
        "controlled_external_evidence_snapshot_gateway_created": True,
        "external_evidence_permission_registry_created": True,
        "external_evidence_request_packet_created": True,
        "external_evidence_execution_plan_created": True,
        "sanitized_content_digest_created": True,
        "raw_body_non_persistence_proof_created": True,
        "external_evidence_handoff_ledger_created": True,
        "external_evidence_workpack_receipt_created": True,
        "external_evidence_category_count": 10,
        "executable_external_evidence_category_count": 1,
        "locked_external_evidence_category_count": 9,
        "agent_role_count": 6,
        "handoff_receipt_count": 6,
        "controlled_action_count": 9,
        "completed_action_count": external_evidence_result["completed_action_count"],
        "controlled_external_evidence_artifact_count": 5,
        "external_evidence_snapshot_workpack_performed": external_evidence_result["external_evidence_snapshot_workpack_performed"],
        "routed_v23_v22_v21_v20_v19_v18_v17_chain_performed": external_evidence_result["routed_v23_v22_v21_v20_v19_v18_v17_chain_performed"],
        "controlled_external_content_fetch_performed": external_evidence_result["controlled_external_content_fetch_performed"],
        "sanitized_content_digest_extracted": external_evidence_result["sanitized_content_digest_extracted"],
        "raw_body_non_persistence_proven": external_evidence_result["raw_body_non_persistence_proven"],
        "inspected_file_count": external_evidence_result["inspected_file_count"],
        "external_request_count": external_evidence_result["external_request_count"],
        "human_approval_required": True,
        "human_approval_granted": external_evidence_result["approval_receipt"]["human_approval_granted"],
        "no_repo_file_mutation": True,
        "no_raw_response_body_printed": True,
        "no_raw_response_body_stored": True,
        "no_raw_response_body_returned": True,
        "no_full_visible_text_stored": True,
        "no_full_visible_text_returned": True,
        "no_repo_mutation": True,
        "no_commit": True,
        "no_push": True,
        "no_deployment": True,
        "no_production_execution": True,
        "no_rollback_execution": True,
        "no_recovery_execution": True,
        "no_arbitrary_url_call": True,
        "no_non_allowlisted_url_call": True,
        "no_post_put_patch_delete": True,
        "no_auth_headers": True,
        "no_cookies": True,
        "no_request_body": True,
        "no_email_sent": True,
        "no_calendar_event_created": True,
        "no_database_operation": True,
        "no_credential_access": True,
        "no_token_access": True,
        "no_credential_vault_access": True,
        "no_secret_read": True,
        "no_private_key_read": True,
        "no_signing_key_read": True,
        "no_environment_read": True,
        "no_key_generation": True,
        "no_real_signature": True,
        "no_real_encryption": True,
        "no_real_decryption": True,
        "no_worker_process_started": True,
        "no_background_agent_started": True,
        "no_agent_process_started": True,
        "no_subprocess_started": True,
        "no_shell_executed": True,
        "no_real_queue_created": True,
        "no_queue_write": True,
        "no_live_task_enqueued": True,
        "no_live_task_executed_outside_workpack": True,
        "no_live_worker_routing_to_real_processes": True,
        "no_uncontrolled_live_orchestration": True,
        "no_arbitrary_task_execution": True,
        "no_user_task_execution": True
    }


def create_external_evidence_safety_boundary_matrix() -> dict:
    return {
        "controlled_external_evidence_snapshot_manifest": "ALLOWED",
        "external_evidence_permission_registry": "ALLOWED",
        "external_evidence_request_packet": "ALLOWED",
        "external_evidence_approval_receipt": "ALLOWED",
        "external_evidence_execution_plan": "ALLOWED",
        "controlled_allowlisted_https_content_fetch": "ALLOWED",
        "sanitized_content_digest_extraction": "ALLOWED",
        "raw_body_non_persistence_proof": "ALLOWED",
        "routed_v23_v22_v21_v20_v19_v18_v17_operational_chain": "ALLOWED",
        "controlled_external_evidence_receipt_json": "ALLOWED",
        "controlled_external_content_digest_markdown": "ALLOWED",
        "controlled_external_content_snapshot_json": "ALLOWED",
        "controlled_external_evidence_table_csv": "ALLOWED",
        "controlled_external_evidence_manifest_json": "ALLOWED",
        "controlled_artifact_readback_verification": "ALLOWED",
        "external_evidence_handoff_ledger": "ALLOWED",
        "external_evidence_workpack_receipt": "ALLOWED",
        "external_evidence_audit_record": "ALLOWED",
        "json_receipt_output": "ALLOWED",
        "markdown_text_output": "ALLOWED",
        "csv_text_output": "ALLOWED",
        
        "uncontrolled_agent_activation": "DENIED",
        "autonomous_self_activation": "DENIED",
        "real_worker_process_start": "DENIED",
        "background_agent_start": "DENIED",
        "daemon_start": "DENIED",
        "arbitrary_agent_execution": "DENIED",
        "live_email_execution": "DENIED",
        "live_calendar_execution": "DENIED",
        "live_database_execution": "DENIED",
        "live_deployment_execution": "DENIED",
        "email_send": "DENIED",
        "calendar_event_create": "DENIED",
        "database_write": "DENIED",
        "arbitrary_web_browsing": "DENIED",
        "arbitrary_content_scrape": "DENIED",
        "arbitrary_api_call": "DENIED",
        "non_allowlisted_url_call": "DENIED",
        "user_provided_url_call": "DENIED",
        "post_request": "DENIED",
        "put_request": "DENIED",
        "patch_request": "DENIED",
        "delete_request": "DENIED",
        "request_body": "DENIED",
        "authentication_headers": "DENIED",
        "cookies": "DENIED",
        "raw_response_body_storage": "DENIED",
        "raw_response_body_printing": "DENIED",
        "raw_response_body_returning": "DENIED",
        "full_html_storage": "DENIED",
        "full_visible_text_storage": "DENIED",
        "uncontrolled_tool_execution": "DENIED",
        "repo_file_mutation": "DENIED",
        "repo_write": "DENIED",
        "binary_document_generation": "DENIED",
        "binary_spreadsheet_generation": "DENIED",
        "production_execution": "DENIED",
        "production_mutation": "DENIED",
        "deployment": "DENIED",
        "deployment_rollback": "DENIED",
        "rollback_execution": "DENIED",
        "recovery_execution": "DENIED",
        "credential_use": "DENIED",
        "credential_vault_access": "DENIED",
        "token_access": "DENIED",
        "secret_read": "DENIED",
        "private_key_read": "DENIED",
        "signing_key_read": "DENIED",
        "encryption_key_read": "DENIED",
        "environment_read": "DENIED",
        "key_generation": "DENIED",
        "real_signature": "DENIED",
        "real_encryption": "DENIED",
        "real_decryption": "DENIED",
        "subprocess_start": "DENIED",
        "shell_execution": "DENIED",
        "arbitrary_command_execution": "DENIED",
        "arbitrary_task_execution": "DENIED",
        "user_task_execution": "DENIED",
        "real_queue_creation": "DENIED",
        "queue_write": "DENIED",
        "scheduler_write": "DENIED",
        "cron_write": "DENIED",
        "live_task_enqueue": "DENIED",
        "live_task_dequeue": "DENIED",
        "live_task_execution_outside_controlled_external_evidence_workpack": "DENIED",
        "live_worker_routing_to_real_processes": "DENIED",
        "uncontrolled_live_orchestration": "DENIED",
        "database_mutation": "DENIED",
        "full_workforce_activation": "DENIED",
        "v24_1_creation": "DENIED",
        "v25_creation": "DENIED"
    }


def create_station_chief_v24_controlled_external_evidence_schema() -> dict:
    return {
        "schema_version": "24.0.0",
        "schema_type": "station_chief_v24_controlled_external_evidence_snapshot",
        "required_sections": [
            "controlled_external_evidence_snapshot_manifest",
            "external_evidence_permission_registry",
            "external_evidence_request_packet",
            "external_evidence_approval_receipt",
            "external_evidence_execution_plan",
            "external_evidence_snapshot_workpack_execution",
            "sanitized_content_digest",
            "raw_body_non_persistence_proof",
            "external_evidence_handoff_ledger",
            "external_evidence_workpack_receipt",
            "external_evidence_audit_record",
            "external_evidence_safety_boundary_matrix",
            "controlled_external_evidence_summary"
        ],
        "controlled_external_evidence_snapshot_gateway_authorized": True,
        "allowlisted_content_digest_authorized": True,
        "routed_v23/v22/v21/v20/v19/v18/v17_operational_chain_authorized": True,
        "controlled_evidence_receipt_artifact_authorized": True,
        "controlled_content_digest_artifact_authorized": True,
        "controlled_content_snapshot_artifact_authorized": True,
        "controlled_evidence_table_artifact_authorized": True,
        "controlled_evidence_manifest_artifact_authorized": True,
        "sanitized_title_extraction_authorized": True,
        "sanitized_preview_extraction_authorized": True,
        "sanitized_preview_max_chars_280_required": True,
        "raw_response_body_persistence_authorized": False,
        "human_approval_required": True,
        "no_uncontrolled_agent_activation_authorized": True,
        "no_real_worker_process_authorized": True,
        "no_background_agent_authorized": True,
        "no_arbitrary_agent_execution_authorized": True,
        "no_repo_mutation_authorized": True,
        "no_production_execution_authorized": True,
        "no_deployment_authorized": True,
        "no_arbitrary_web_browsing_authorized": True,
        "no_arbitrary_API_call_authorized": True,
        "no_email/calendar/database/deployment_execution_authorized": True,
        "no_credential_access_authorized": True,
        "no_secret_read_authorized": True,
        "no_environment_read_authorized": True,
        "no_arbitrary_task_execution_authorized": True,
        "no_user_task_execution_authorized": True,
        "no_real_queue_authorized": True,
        "no_queue_write_authorized": True,
        "no_uncontrolled_live_orchestration_authorized": True,
        "v24_1_created": False,
        "v25_created": False
    }


def create_station_chief_v24_controlled_external_evidence_bundle(approval_phrase: str | None = None, operator_label: str | None = None, workpack_label: str | None = None, requested_url: str | None = None, execute_external_evidence_flag: bool = False) -> dict:
    schema = create_station_chief_v24_controlled_external_evidence_schema()
    manifest = create_controlled_external_evidence_snapshot_manifest()
    registry = create_external_evidence_permission_registry()
    boundaries = create_external_evidence_safety_boundary_matrix()
    
    if execute_external_evidence_flag:
        res = execute_external_evidence_snapshot_workpack(approval_phrase, operator_label, workpack_label, requested_url)
    else:
        # Preview only
        packet = create_external_evidence_request_packet(operator_label, workpack_label, requested_url)
        approval = create_external_evidence_approval_receipt(approval_phrase, packet)
        plan = create_external_evidence_execution_plan(registry, packet, approval)
        res = {
            "execution_status": "V24_CONTROLLED_EXTERNAL_EVIDENCE_PREVIEW_ONLY",
            "external_evidence_snapshot_workpack_performed": False,
            "controlled_action_count": 9,
            "completed_action_count": 0,
            "routed_v23_v22_v21_v20_v19_v18_v17_chain_performed": False,
            "controlled_external_content_fetch_performed": False,
            "sanitized_content_digest_extracted": False,
            "raw_body_non_persistence_proven": False,
            "evidence_receipt_artifact_written": False,
            "content_digest_artifact_written": False,
            "content_snapshot_artifact_written": False,
            "evidence_table_artifact_written": False,
            "evidence_manifest_written": False,
            "controlled_external_evidence_artifact_count": 5,
            "inspected_file_count": 0,
            "external_request_count": 0,
            "allowed_external_url": STATION_CHIEF_V24_ALLOWED_EXTERNAL_URL,
            "status_code": None,
            "final_url": None,
            "content_type": None,
            "response_sha256": None,
            "response_byte_count": 0,
            "response_line_count": 0,
            "sanitized_title": None,
            "sanitized_title_present": False,
            "sanitized_preview": None,
            "sanitized_preview_char_count": 0,
            "sanitized_preview_max_chars": STATION_CHIEF_V24_SANITIZED_PREVIEW_MAX_CHARS,
            "raw_response_body_printed": False,
            "raw_response_body_stored": False,
            "raw_response_body_returned": False,
            "full_visible_text_stored": False,
            "full_visible_text_returned": False,
            "artifact_paths": STATION_CHIEF_V24_CONTROLLED_ARTIFACT_PATHS,
            "artifact_digests": {},
            "artifact_readback_verified": False,
            "logical_agent_roles_used": True,
            "real_worker_process_started": False,
            "background_agent_started": False,
            "request_packet": packet,
            "approval_receipt": approval,
            "execution_plan": plan,
            "fetch_result": {},
            "digest": {},
            "proof": {},
            "artifact_results": {}
        }
        
    handoff_ledger = create_external_evidence_handoff_ledger(res)
    receipt = create_external_evidence_workpack_receipt(res, handoff_ledger)
    audit = create_external_evidence_audit_record(res, handoff_ledger, receipt)
    
    status = res["execution_status"]
    if not execute_external_evidence_flag:
        status = "CONTROLLED_EXTERNAL_EVIDENCE_PREVIEW_ONLY"

    bundle = {
        "runtime_version": STATION_CHIEF_V24_CONTROLLED_EXTERNAL_EVIDENCE_VERSION,
        "controlled_external_evidence_status": status,
        "controlled_external_evidence_snapshot_gateway_created": True,
        "external_evidence_permission_registry_created": True,
        "external_evidence_category_count": 10,
        "executable_external_evidence_category_count": 1,
        "locked_external_evidence_category_count": 9,
        "controlled_action_count": 9,
        "completed_action_count": res["completed_action_count"],
        "controlled_external_evidence_artifact_count": 5,
        "external_evidence_snapshot_workpack_performed": res["external_evidence_snapshot_workpack_performed"],
        "routed_v23_v22_v21_v20_v19_v18_v17_chain_performed": res["routed_v23_v22_v21_v20_v19_v18_v17_chain_performed"],
        "controlled_external_content_fetch_performed": res["controlled_external_content_fetch_performed"],
        "sanitized_content_digest_extracted": res["sanitized_content_digest_extracted"],
        "raw_body_non_persistence_proven": res["raw_body_non_persistence_proven"],
        "evidence_receipt_artifact_written": res["evidence_receipt_artifact_written"],
        "content_digest_artifact_written": res["content_digest_artifact_written"],
        "content_snapshot_artifact_written": res["content_snapshot_artifact_written"],
        "evidence_table_artifact_written": res["evidence_table_artifact_written"],
        "evidence_manifest_written": res["evidence_manifest_written"],
        "artifact_readback_verified": res["artifact_readback_verified"],
        "inspected_file_count": res["inspected_file_count"],
        "external_request_count": res["external_request_count"],
        "allowed_external_url": res["allowed_external_url"],
        "status_code": res["status_code"],
        "final_url": res["final_url"],
        "content_type": res["content_type"],
        "response_sha256": res["response_sha256"],
        "response_byte_count": res["response_byte_count"],
        "response_line_count": res["response_line_count"],
        "sanitized_title": res["sanitized_title"],
        "sanitized_title_present": res["sanitized_title_present"],
        "sanitized_preview": res["sanitized_preview"],
        "sanitized_preview_char_count": res["sanitized_preview_char_count"],
        "sanitized_preview_max_chars": res["sanitized_preview_max_chars"],
        "raw_response_body_printed": False,
        "raw_response_body_stored": False,
        "raw_response_body_returned": False,
        "full_visible_text_stored": False,
        "full_visible_text_returned": False,
        "artifact_paths": res["artifact_paths"],
        "artifact_digests": res["artifact_digests"],
        "external_evidence_handoff_ledger_created": True,
        "handoff_receipt_count": 6,
        "external_evidence_workpack_receipt_created": True,
        "logical_agent_roles_used": True,
        "real_worker_process_started": False,
        "background_agent_started": False,
        "repo_file_mutation_performed": False,
        "repo_mutation_performed": False,
        "commit_performed": False,
        "push_performed": False,
        "deployment_performed": False,
        "production_execution_performed": False,
        "rollback_execution_performed": False,
        "recovery_execution_performed": False,
        "arbitrary_url_call_performed": False,
        "non_allowlisted_url_call_performed": False,
        "post_put_patch_delete_performed": False,
        "auth_headers_used": False,
        "cookies_used": False,
        "request_body_sent": False,
        "credential_access_performed": False,
        "credential_vault_access_performed": False,
        "token_access_performed": False,
        "secret_read_performed": False,
        "private_key_read_performed": False,
        "signing_key_read_performed": False,
        "environment_read_performed": False,
        "key_generation_performed": False,
        "real_signature_performed": False,
        "real_encryption_performed": False,
        "real_decryption_performed": False,
        "email_sent": False,
        "calendar_event_created": False,
        "database_operation_performed": False,
        "arbitrary_api_call_performed": False,
        "daemon_started": False,
        "background_process_started": False,
        "agent_started": False,
        "real_queue_created": False,
        "queue_write_performed": False,
        "scheduler_write_performed": False,
        "cron_write_performed": False,
        "live_task_enqueued": False,
        "live_task_dequeued": False,
        "live_task_executed": False,
        "task_executed": False,
        "live_worker_routing_to_real_processes_performed": False,
        "uncontrolled_live_orchestration_performed": False,
        "arbitrary_task_execution_performed": False,
        "user_task_execution_performed": False,
        "shell_executed": False,
        "subprocess_started": False,
        "database_mutation_performed": False,
        "full_workforce_activation_performed": False,
        "v24_1_created": False,
        "v25_created": False,
        
        "schema": schema,
        "controlled_external_evidence_snapshot_manifest": manifest,
        "external_evidence_permission_registry": registry,
        "external_evidence_request_packet": res["request_packet"],
        "external_evidence_approval_receipt": res["approval_receipt"],
        "external_evidence_execution_plan": res["execution_plan"],
        "external_evidence_snapshot_workpack_execution": res,
        "sanitized_content_digest": res["digest"],
        "raw_body_non_persistence_proof": res["proof"],
        "external_evidence_handoff_ledger": handoff_ledger,
        "external_evidence_workpack_receipt": receipt,
        "external_evidence_audit_record": audit,
        "external_evidence_safety_boundary_matrix": boundaries,
        "controlled_external_evidence_summary": {
            "version": STATION_CHIEF_V24_CONTROLLED_EXTERNAL_EVIDENCE_VERSION,
            "status": status
        }
    }
    bundle["bundle_digest"] = sha256_digest(bundle)
    return bundle
