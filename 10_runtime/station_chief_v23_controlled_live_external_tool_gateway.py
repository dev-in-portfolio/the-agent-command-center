import json
import hashlib
import csv
import io
import re
import time
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

# Import from v22 module as allowed
from station_chief_v22_controlled_business_workflow_workpack import (
    STATION_CHIEF_V22_APPROVAL_PHRASE,
    execute_business_workflow_workpack
)

STATION_CHIEF_V23_CONTROLLED_EXTERNAL_TOOL_VERSION = "23.0.0"
STATION_CHIEF_V23_CONTROLLED_EXTERNAL_TOOL_STATUS = "STATION_CHIEF_V23_CONTROLLED_LIVE_EXTERNAL_TOOL_GATEWAY"
STATION_CHIEF_V23_CONTROLLED_EXTERNAL_TOOL_PHASE = "Station Chief v23.0 Controlled Live External Tool Gateway / Allowlisted Web Probe Workpack Candidate"

STATION_CHIEF_V23_APPROVAL_PHRASE = "I_APPROVE_V23_CONTROLLED_EXTERNAL_WEB_PROBE"

STATION_CHIEF_V23_EXTERNAL_TOOL_WORKPACK_ID = "station-chief-v23-controlled-live-external-tool-gateway-workpack-001"

STATION_CHIEF_V23_ALLOWED_EXTERNAL_URL = "https://example.com/"
STATION_CHIEF_V23_ALLOWED_EXTERNAL_SCHEME = "https"
STATION_CHIEF_V23_ALLOWED_EXTERNAL_HOST = "example.com"
STATION_CHIEF_V23_ALLOWED_EXTERNAL_PATH = "/"
STATION_CHIEF_V23_ALLOWED_METHOD = "GET"

STATION_CHIEF_V23_CONTROLLED_WORKSPACE_DIR = "/tmp/station_chief_v23_external_tool_artifacts"

STATION_CHIEF_V23_CONTROLLED_ARTIFACT_PATHS = {
    "external_probe_receipt_json": "/tmp/station_chief_v23_external_tool_artifacts/v23_external_tool_probe_receipt.json",
    "external_probe_summary_md": "/tmp/station_chief_v23_external_tool_artifacts/v23_external_tool_probe_summary.md",
    "external_probe_table_csv": "/tmp/station_chief_v23_external_tool_artifacts/v23_external_tool_probe_table.csv",
    "external_tool_manifest_json": "/tmp/station_chief_v23_external_tool_artifacts/v23_external_tool_manifest.json"
}

STATION_CHIEF_V23_EXTERNAL_ACTION_IDS = [
    "station-chief-v23-action-routed-v22-v21-v20-v19-v18-v17-operational-chain-001",
    "station-chief-v23-action-controlled-allowlisted-https-get-probe-002",
    "station-chief-v23-action-controlled-external-probe-receipt-json-003",
    "station-chief-v23-action-controlled-external-probe-summary-markdown-004",
    "station-chief-v23-action-controlled-external-probe-table-csv-005",
    "station-chief-v23-action-controlled-external-tool-manifest-json-006"
]

STATION_CHIEF_V23_EXTERNAL_AGENT_ROLE_IDS = [
    "station-chief-v23-agent-role-external-gatekeeper-001",
    "station-chief-v23-agent-role-url-scope-auditor-002",
    "station-chief-v23-agent-role-probe-controller-003",
    "station-chief-v23-agent-role-response-sanitizer-004",
    "station-chief-v23-agent-role-external-artifact-scribe-005",
    "station-chief-v23-agent-role-external-audit-officer-006"
]

STATION_CHIEF_V23_NEXT_VERSION_REQUIRES_OPERATOR_INSTRUCTION = "v23.1 or broader live external tool expansion requires explicit separate operator instruction"


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


def create_controlled_live_external_tool_gateway_manifest() -> dict:
    return {
        "manifest_id": sha256_digest("controlled_live_external_tool_gateway_manifest"),
        "manifest_type": "controlled_live_external_tool_gateway_manifest",
        "runtime_version": STATION_CHIEF_V23_CONTROLLED_EXTERNAL_TOOL_VERSION,
        "controlled_live_external_tool_gateway_created": True,
        "allowlisted_web_probe_workpack_created": True,
        "live_external_readonly_probe_authorized": True,
        "human_approval_required": True,
        "exact_approval_phrase_required": True,
        "allowlisted_url": STATION_CHIEF_V23_ALLOWED_EXTERNAL_URL,
        "allowlisted_host": STATION_CHIEF_V23_ALLOWED_EXTERNAL_HOST,
        "allowlisted_method": "GET",
        "response_body_storage_allowed": False,
        "response_body_printing_allowed": False,
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


def create_external_tool_permission_registry() -> dict:
    categories = [
        "allowlisted_web_probe",
        "arbitrary_web_browsing",
        "email_send",
        "calendar_event_create",
        "external_api_call",
        "database_operation",
        "deployment_operation",
        "webhook_operation"
    ]
    registry = {}
    for cat in categories:
        executable = (cat == "allowlisted_web_probe")
        registry[cat] = {
            "category_id": cat,
            "category_name": cat.replace("_", " ").title(),
            "category_registered": True,
            "executable_in_v23": executable,
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
            "allowed_url": STATION_CHIEF_V23_ALLOWED_EXTERNAL_URL if executable else None,
            "response_body_storage_allowed": False,
            "response_body_printing_allowed": False,
            "live_execution_allowed": executable
        }
    return {
        "registry_id": sha256_digest(registry),
        "registry_type": "controlled_external_tool_permission_registry",
        "runtime_version": STATION_CHIEF_V23_CONTROLLED_EXTERNAL_TOOL_VERSION,
        "external_tool_category_count": 8,
        "executable_external_tool_count": 1,
        "locked_external_tool_count": 7,
        "categories": registry
    }


def create_external_tool_request_packet(operator_label: str | None = None, workpack_label: str | None = None, requested_url: str | None = None) -> dict:
    op = normalize_label(operator_label, "unknown_operator")
    wp = normalize_label(workpack_label, "v23_external_tool_workpack")
    arbitrary = requested_url is not None and requested_url != STATION_CHIEF_V23_ALLOWED_EXTERNAL_URL
    return {
        "request_packet_id": sha256_digest({"url": requested_url, "op": op, "wp": wp}),
        "packet_type": "controlled_external_tool_request_packet",
        "runtime_version": STATION_CHIEF_V23_CONTROLLED_EXTERNAL_TOOL_VERSION,
        "operator_label": op,
        "workpack_label": wp,
        "requested_url": requested_url,
        "effective_url": STATION_CHIEF_V23_ALLOWED_EXTERNAL_URL,
        "requested_method": "GET",
        "exact_url_required": True,
        "human_approval_required": True,
        "response_body_storage_requested": False,
        "response_body_printing_requested": False,
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


def create_external_tool_approval_receipt(approval_phrase: str | None, request_packet: dict) -> dict:
    phrase_matches = (approval_phrase == STATION_CHIEF_V23_APPROVAL_PHRASE)
    url_allowed = (request_packet["requested_url"] is None or request_packet["requested_url"] == STATION_CHIEF_V23_ALLOWED_EXTERNAL_URL)
    granted = phrase_matches and url_allowed
    return {
        "approval_receipt_id": sha256_digest({"phrase": approval_phrase, "packet": request_packet["request_packet_id"]}),
        "receipt_type": "v23_external_tool_human_approval_receipt",
        "runtime_version": STATION_CHIEF_V23_CONTROLLED_EXTERNAL_TOOL_VERSION,
        "operator_label": request_packet["operator_label"],
        "workpack_label": request_packet["workpack_label"],
        "approval_phrase_received": approval_phrase is not None,
        "approval_phrase_matches": phrase_matches,
        "expected_approval_phrase": STATION_CHIEF_V23_APPROVAL_PHRASE,
        "requested_url_allowed": url_allowed,
        "human_approval_granted": granted,
        "autonomous_self_approval": False,
        "approval_scope": "v23_controlled_allowlisted_external_web_probe_only",
        "approval_does_not_authorize_arbitrary_url": True,
        "approval_does_not_authorize_response_body_storage": True,
        "approval_does_not_authorize_repo_mutation": True,
        "approval_does_not_authorize_credentials": True,
        "approval_does_not_authorize_email_calendar_database_deployment": True,
        "approval_does_not_authorize_future_external_tools": True,
        "approval_does_not_authorize_real_worker_processes": True
    }


def create_external_probe_execution_plan(permission_registry: dict, request_packet: dict, approval_receipt: dict) -> dict:
    approved = approval_receipt["human_approval_granted"]
    return {
        "execution_plan_id": sha256_digest({"receipt": approval_receipt["approval_receipt_id"]}),
        "plan_type": "controlled_external_web_probe_execution_plan",
        "runtime_version": STATION_CHIEF_V23_CONTROLLED_EXTERNAL_TOOL_VERSION,
        "workpack_id": STATION_CHIEF_V23_EXTERNAL_TOOL_WORKPACK_ID,
        "action_count": 6,
        "human_approval_granted": approved,
        "execution_status": "READY_FOR_CONTROLLED_EXTERNAL_WEB_PROBE" if approved else "EXTERNAL_WEB_PROBE_DENIED_OR_PREVIEW_ONLY",
        "execute_routed_v22_operational_chain": approved,
        "execute_allowlisted_https_get_probe": approved,
        "execute_external_probe_receipt_artifact": approved,
        "execute_external_probe_summary_artifact": approved,
        "execute_external_probe_table_artifact": approved,
        "execute_external_tool_manifest_artifact": approved,
        "allowed_url": STATION_CHIEF_V23_ALLOWED_EXTERNAL_URL,
        "allowed_method": "GET",
        "max_external_request_count": 1,
        "repo_mutation_allowed": False,
        "response_body_storage_allowed": False,
        "response_body_printing_allowed": False,
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


def validate_allowed_external_url(url: str | None) -> dict:
    effective = url if url is not None else STATION_CHIEF_V23_ALLOWED_EXTERNAL_URL
    parsed = urllib.parse.urlparse(effective)
    is_valid = (
        effective == STATION_CHIEF_V23_ALLOWED_EXTERNAL_URL and
        parsed.scheme == STATION_CHIEF_V23_ALLOWED_EXTERNAL_SCHEME and
        parsed.netloc == STATION_CHIEF_V23_ALLOWED_EXTERNAL_HOST and
        parsed.path == STATION_CHIEF_V23_ALLOWED_EXTERNAL_PATH and
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


def execute_allowlisted_external_web_probe(approval_receipt: dict, requested_url: str | None = None) -> dict:
    if not approval_receipt["human_approval_granted"]:
        return {"external_probe_performed": False, "controlled_probe_error": False}
    
    validation = validate_allowed_external_url(requested_url)
    if not validation["is_valid"]:
        return {"external_probe_performed": False, "controlled_probe_error": True, "error": "URL not allowlisted"}

    start_time = time.time()
    try:
        req = urllib.request.Request(STATION_CHIEF_V23_ALLOWED_EXTERNAL_URL, method="GET")
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            final_url = response.geturl()
            content_type = response.headers.get_content_type()
            body_bytes = response.read()
            
            elapsed = time.time() - start_time
            elapsed_class = "FAST" if elapsed < 1.0 else "NORMAL" if elapsed < 5.0 else "SLOW"
            
            sha256 = hashlib.sha256(body_bytes).hexdigest()
            byte_count = len(body_bytes)
            line_count = len(body_bytes.splitlines())
            
            return {
                "external_probe_action_id": "station-chief-v23-action-controlled-allowlisted-https-get-probe-002",
                "external_probe_performed": True,
                "controlled_probe_error": False,
                "external_request_count": 1,
                "requested_url": requested_url or STATION_CHIEF_V23_ALLOWED_EXTERNAL_URL,
                "effective_url": STATION_CHIEF_V23_ALLOWED_EXTERNAL_URL,
                "allowed_url_validation": validation,
                "method": "GET",
                "status_code": status_code,
                "final_url": final_url,
                "content_type": content_type,
                "response_sha256": sha256,
                "response_byte_count": byte_count,
                "response_line_count": line_count,
                "elapsed_seconds": round(elapsed, 4),
                "elapsed_classification": elapsed_class,
                "response_body_printed": False,
                "response_body_stored": False,
                "response_body_returned": False,
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
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        return {
            "external_probe_performed": False,
            "controlled_probe_error": True,
            "error_class": e.__class__.__name__,
            "external_request_count": 1,
            "requested_url": requested_url or STATION_CHIEF_V23_ALLOWED_EXTERNAL_URL,
            "effective_url": STATION_CHIEF_V23_ALLOWED_EXTERNAL_URL,
            "allowed_url_validation": validation,
            "method": "GET"
        }


def create_response_metadata_sanitizer(probe_result: dict) -> dict:
    sanitized = {}
    fields = ["status_code", "final_url", "content_type", "response_sha256", "response_byte_count", "response_line_count", "external_request_count", "elapsed_classification"]
    for f in fields:
        sanitized[f] = probe_result.get(f)
        
    return {
        "sanitizer_id": sha256_digest(sanitized),
        "sanitizer_type": "v23_response_metadata_sanitizer",
        "runtime_version": STATION_CHIEF_V23_CONTROLLED_EXTERNAL_TOOL_VERSION,
        "response_body_removed": True,
        "response_body_never_returned": True,
        "response_body_never_written": True,
        "response_body_never_printed": True,
        "only_metadata_retained": True,
        "retained_fields": fields,
        "sanitized_probe_metadata": sanitized,
        "credential_data_absent": True,
        "secret_data_absent": True,
        "token_data_absent": True,
        "environment_data_absent": True
    }


def resolve_controlled_external_tool_workspace_paths() -> dict:
    workspace_dir = Path(STATION_CHIEF_V23_CONTROLLED_WORKSPACE_DIR)
    paths = {}
    valid = True
    if not str(workspace_dir).startswith("/tmp/station_chief_v23_external_tool_artifacts"):
        valid = False
        
    for key, path_str in STATION_CHIEF_V23_CONTROLLED_ARTIFACT_PATHS.items():
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


def build_external_tool_artifact_payloads(routed_v22_result: dict, probe_result: dict, sanitizer: dict, approval_receipt: dict, permission_registry: dict) -> dict:
    meta = sanitizer["sanitized_probe_metadata"]
    op = approval_receipt["operator_label"]
    inspected = routed_v22_result.get("inspected_file_count", 0) if routed_v22_result else 0
    
    receipt_payload = {
        "version": STATION_CHIEF_V23_CONTROLLED_EXTERNAL_TOOL_VERSION,
        "status": "V23_EXTERNAL_PROBE_RECEIPT",
        "operator": op,
        "workpack": approval_receipt["workpack_label"],
        "external_probe_performed": probe_result.get("external_probe_performed", False),
        "probe_metadata": meta,
        "routed_v22_chain_performed": routed_v22_result.get("business_workflow_workpack_performed", False) if routed_v22_result else False,
        "inspected_file_count": inspected
    }
    
    summary_md = f"""# Station Chief v23 Controlled Live External Tool Gateway

## Context
- **Runtime Version:** {STATION_CHIEF_V23_CONTROLLED_EXTERNAL_TOOL_VERSION}
- **Approval Status:** {"GRANTED" if approval_receipt["human_approval_granted"] else "DENIED"}
- **Operator:** {op}

## External Web Probe Summary
- **Allowlisted URL:** {STATION_CHIEF_V23_ALLOWED_EXTERNAL_URL}
- **Probe Status:** {"SUCCESS" if receipt_payload["external_probe_performed"] else "FAILED/SKIPPED"}
- **Status Code:** {meta.get("status_code")}
- **Content Type:** {meta.get("content_type")}
- **Response Bytes:** {meta.get("response_byte_count")}
- **Response Lines:** {meta.get("response_line_count")}
- **Response Hash:** {meta.get("response_sha256")}

## Operational Chain Summary
- **Routed v22 Chain Performed:** {receipt_payload["routed_v22_chain_performed"]}
- **Inspected File Count:** {inspected}

## Artifact List
- Probe Receipt: `v23_external_tool_probe_receipt.json`
- Probe Summary: `v23_external_tool_probe_summary.md`
- Probe Table: `v23_external_tool_probe_table.csv`
- Tool Manifest: `v23_external_tool_manifest.json`

## Safety Summary
- **Repo Mutation:** FORBIDDEN / NOT PERFORMED
- **Credential Access:** FORBIDDEN / NOT PERFORMED
- **Private Data Access:** FORBIDDEN / NOT PERFORMED
- **Response Body Stored:** FORBIDDEN / NOT PERFORMED

This document confirms safe live external tool access using a controlled gateway.
"""

    csv_rows = [
        ["property", "value"],
        ["runtime_version", STATION_CHIEF_V23_CONTROLLED_EXTERNAL_TOOL_VERSION],
        ["approval_granted", str(approval_receipt["human_approval_granted"])],
        ["routed_v22_chain_performed", str(receipt_payload["routed_v22_chain_performed"])],
        ["external_probe_performed", str(receipt_payload["external_probe_performed"])],
        ["external_request_count", str(meta.get("external_request_count", 0))],
        ["status_code", str(meta.get("status_code", "N/A"))],
        ["response_byte_count", str(meta.get("response_byte_count", 0))],
        ["response_line_count", str(meta.get("response_line_count", 0))],
        ["response_body_stored", "False"],
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
        "workpack_id": STATION_CHIEF_V23_EXTERNAL_TOOL_WORKPACK_ID,
        "artifacts": [
            {"key": "external_probe_receipt_json", "format": "json", "path": STATION_CHIEF_V23_CONTROLLED_ARTIFACT_PATHS["external_probe_receipt_json"]},
            {"key": "external_probe_summary_md", "format": "markdown", "path": STATION_CHIEF_V23_CONTROLLED_ARTIFACT_PATHS["external_probe_summary_md"]},
            {"key": "external_probe_table_csv", "format": "csv", "path": STATION_CHIEF_V23_CONTROLLED_ARTIFACT_PATHS["external_probe_table_csv"]},
            {"key": "external_tool_manifest_json", "format": "json", "path": STATION_CHIEF_V23_CONTROLLED_ARTIFACT_PATHS["external_tool_manifest_json"]}
        ]
    }
    
    return {
        "external_probe_receipt_payload": receipt_payload,
        "external_probe_summary_markdown": summary_md,
        "external_probe_table_csv": table_csv,
        "external_tool_manifest_payload": manifest_payload
    }


def write_controlled_external_tool_text_artifact(artifact_key: str, content: str, approval_receipt: dict) -> dict:
    if not approval_receipt["human_approval_granted"]:
        return {"artifact_write_performed": False, "error": "Approval missing"}
        
    paths_meta = resolve_controlled_external_tool_workspace_paths()
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


def execute_external_tool_gateway_workpack(approval_phrase: str | None, operator_label: str | None = None, workpack_label: str | None = None, requested_url: str | None = None) -> dict:
    manifest = create_controlled_live_external_tool_gateway_manifest()
    registry = create_external_tool_permission_registry()
    packet = create_external_tool_request_packet(operator_label, workpack_label, requested_url)
    approval = create_external_tool_approval_receipt(approval_phrase, packet)
    plan = create_external_probe_execution_plan(registry, packet, approval)
    
    performed = False
    completed_action_count = 0
    v22_result = None
    probe_result = {}
    sanitizer = {}
    artifact_results = {}
    artifact_digests = {}
    all_verified = True
    status = "V23_CONTROLLED_EXTERNAL_TOOL_GATEWAY_WORKPACK_DENIED"
    
    if approval["human_approval_granted"]:
        # Action 1: routed v22 chain
        v22_result = execute_business_workflow_workpack(
            STATION_CHIEF_V22_APPROVAL_PHRASE,
            operator_label=operator_label,
            workpack_label=workpack_label
        )
        if v22_result.get("business_workflow_workpack_performed"):
            completed_action_count += 1
            
        # Action 2: allowlisted external probe
        probe_result = execute_allowlisted_external_web_probe(approval, requested_url)
        if probe_result.get("external_probe_performed"):
            completed_action_count += 1
            status = "V23_CONTROLLED_EXTERNAL_TOOL_GATEWAY_WORKPACK_COMPLETED"
        elif probe_result.get("controlled_probe_error"):
            status = "V23_CONTROLLED_EXTERNAL_TOOL_GATEWAY_PROBE_UNAVAILABLE"
            
        # Response sanitization
        sanitizer = create_response_metadata_sanitizer(probe_result)
        
        # Build payloads
        payloads = build_external_tool_artifact_payloads(v22_result, probe_result, sanitizer, approval, registry)
        
        # Actions 3-6: Artifacts
        writes = [
            ("external_probe_receipt_json", canonical_json(payloads["external_probe_receipt_payload"])),
            ("external_probe_summary_md", payloads["external_probe_summary_markdown"]),
            ("external_probe_table_csv", payloads["external_probe_table_csv"]),
            ("external_tool_manifest_json", canonical_json(payloads["external_tool_manifest_payload"]))
        ]
        
        for key, content in writes:
            res = write_controlled_external_tool_text_artifact(key, content, approval)
            artifact_results[key] = res
            if res.get("artifact_write_performed"):
                completed_action_count += 1
                artifact_digests[key] = res["artifact_sha256"]
                if not res["artifact_readback_verified"]: all_verified = False
            else:
                all_verified = False
                
        if completed_action_count == 6:
            performed = True
            
    return {
        "execution_status": status,
        "external_tool_gateway_workpack_performed": performed,
        "controlled_action_count": 6,
        "completed_action_count": completed_action_count,
        "routed_v22_v21_v20_v19_v18_v17_chain_performed": v22_result.get("business_workflow_workpack_performed", False) if v22_result else False,
        "controlled_external_web_probe_performed": probe_result.get("external_probe_performed", False),
        "response_metadata_sanitized": sanitizer.get("response_body_removed", False),
        "external_probe_receipt_artifact_written": artifact_results.get("external_probe_receipt_json", {}).get("artifact_write_performed", False),
        "external_probe_summary_artifact_written": artifact_results.get("external_probe_summary_md", {}).get("artifact_write_performed", False),
        "external_probe_table_artifact_written": artifact_results.get("external_probe_table_csv", {}).get("artifact_write_performed", False),
        "external_tool_manifest_written": artifact_results.get("external_tool_manifest_json", {}).get("artifact_write_performed", False),
        "controlled_external_artifact_count": 4,
        "inspected_file_count": v22_result.get("inspected_file_count", 0) if v22_result else 0,
        "external_request_count": probe_result.get("external_request_count", 0),
        "allowed_external_url": STATION_CHIEF_V23_ALLOWED_EXTERNAL_URL,
        "status_code": probe_result.get("status_code"),
        "response_sha256": probe_result.get("response_sha256"),
        "response_byte_count": probe_result.get("response_byte_count"),
        "response_line_count": probe_result.get("response_line_count"),
        "response_body_printed": False,
        "response_body_stored": False,
        "response_body_returned": False,
        "artifact_paths": STATION_CHIEF_V23_CONTROLLED_ARTIFACT_PATHS,
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
        "network_access_performed": probe_result.get("external_probe_performed", False),
        "email_sent": False,
        "calendar_event_created": False,
        "web_request_performed": probe_result.get("external_probe_performed", False),
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
        "probe_result": probe_result,
        "sanitizer": sanitizer,
        "artifact_results": artifact_results
    }


def create_external_tool_handoff_ledger(external_tool_result: dict) -> dict:
    performed = external_tool_result["external_tool_gateway_workpack_performed"]
    probe_performed = external_tool_result["controlled_external_web_probe_performed"]
    sanitized = external_tool_result["response_metadata_sanitized"]
    
    roles = [
        ("external_gatekeeper", "approval_gate"),
        ("url_scope_auditor", "url_validation"),
        ("probe_controller", "external_probe"),
        ("response_sanitizer", "sanitization"),
        ("external_artifact_scribe", "artifact_write"),
        ("external_audit_officer", "final_audit")
    ]
    
    receipts = {}
    for idx, (name, stage) in enumerate(roles):
        r_id = STATION_CHIEF_V23_EXTERNAL_AGENT_ROLE_IDS[idx]
        h_id = sha256_digest({"role": r_id, "performed": performed})
        receipts[h_id] = {
            "handoff_receipt_id": h_id,
            "agent_role_id": r_id,
            "agent_role_name": name,
            "workflow_stage": stage,
            "receipt_type": "v23_external_tool_agent_handoff_receipt",
            "runtime_version": "23.0.0",
            "external_tool_workpack_received": True,
            "stage_processed": performed,
            "live_worker_process_started": False,
            "background_agent_started": False,
            "tool_execution_performed_by_role": False,
            "repo_mutation_performed": False,
            "controlled_external_probe_supervised": (name == "probe_controller") and probe_performed,
            "response_sanitization_supervised": (name == "response_sanitizer") and sanitized,
            "controlled_artifact_write_supervised": (name == "external_artifact_scribe") and performed,
            "credential_access_performed": False,
            "network_access_limited_to_allowlisted_probe": True,
            "shell_executed": False,
            "subprocess_started": False
        }
        
    return {
        "ledger_id": sha256_digest(receipts),
        "ledger_type": "v23_external_tool_agent_handoff_ledger",
        "runtime_version": "23.0.0",
        "handoff_receipt_count": len(receipts),
        "all_handoffs_recorded": True,
        "no_real_workers_started": True,
        "no_background_agents_started": True,
        "receipts": receipts
    }


def create_external_tool_workpack_receipt(external_tool_result: dict, handoff_ledger: dict) -> dict:
    performed = external_tool_result["external_tool_gateway_workpack_performed"]
    return {
        "external_tool_workpack_receipt_id": sha256_digest({"res": external_tool_result["execution_status"], "ledger": handoff_ledger["ledger_id"]}),
        "receipt_type": "v23_external_tool_gateway_workpack_execution_receipt",
        "runtime_version": "23.0.0",
        "external_tool_gateway_workpack_performed": performed,
        "controlled_action_count": 6,
        "completed_action_count": external_tool_result["completed_action_count"],
        "routed_v22_v21_v20_v19_v18_v17_chain_performed": external_tool_result["routed_v22_v21_v20_v19_v18_v17_chain_performed"],
        "controlled_external_web_probe_performed": external_tool_result["controlled_external_web_probe_performed"],
        "response_metadata_sanitized": external_tool_result["response_metadata_sanitized"],
        "external_probe_receipt_artifact_written": external_tool_result["external_probe_receipt_artifact_written"],
        "external_probe_summary_artifact_written": external_tool_result["external_probe_summary_artifact_written"],
        "external_probe_table_artifact_written": external_tool_result["external_probe_table_artifact_written"],
        "external_tool_manifest_written": external_tool_result["external_tool_manifest_written"],
        "controlled_external_artifact_count": 4,
        "inspected_file_count": external_tool_result["inspected_file_count"],
        "external_request_count": external_tool_result["external_request_count"],
        "allowed_external_url": external_tool_result["allowed_external_url"],
        "response_sha256": external_tool_result["response_sha256"],
        "response_byte_count": external_tool_result["response_byte_count"],
        "response_line_count": external_tool_result["response_line_count"],
        "artifact_paths": external_tool_result["artifact_paths"],
        "artifact_digests": external_tool_result["artifact_digests"],
        "artifact_readback_verified": external_tool_result["artifact_readback_verified"],
        "logical_agent_roles_used": True,
        "handoff_receipt_count": 6,
        "receipt_status": "CONTROLLED_EXTERNAL_TOOL_GATEWAY_WORKPACK_COMPLETED" if performed else "CONTROLLED_EXTERNAL_TOOL_GATEWAY_WORKPACK_DENIED",
        "no_repo_file_mutation": True,
        "no_response_body_printed": True,
        "no_response_body_stored": True,
        "no_response_body_returned": True,
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


def create_external_tool_gateway_audit_record(external_tool_result: dict, handoff_ledger: dict, workpack_receipt: dict) -> dict:
    return {
        "audit_id": sha256_digest({"receipt": workpack_receipt["external_tool_workpack_receipt_id"]}),
        "audit_type": "v23_controlled_live_external_tool_gateway_audit",
        "runtime_version": "23.0.0",
        "controlled_live_external_tool_gateway_created": True,
        "external_tool_permission_registry_created": True,
        "external_tool_request_packet_created": True,
        "external_probe_execution_plan_created": True,
        "response_metadata_sanitizer_created": True,
        "external_tool_handoff_ledger_created": True,
        "external_tool_workpack_receipt_created": True,
        "external_tool_category_count": 8,
        "executable_external_tool_count": 1,
        "locked_external_tool_count": 7,
        "agent_role_count": 6,
        "handoff_receipt_count": 6,
        "controlled_action_count": 6,
        "completed_action_count": external_tool_result["completed_action_count"],
        "controlled_external_artifact_count": 4,
        "external_tool_gateway_workpack_performed": external_tool_result["external_tool_gateway_workpack_performed"],
        "routed_v22_v21_v20_v19_v18_v17_chain_performed": external_tool_result["routed_v22_v21_v20_v19_v18_v17_chain_performed"],
        "controlled_external_web_probe_performed": external_tool_result["controlled_external_web_probe_performed"],
        "response_metadata_sanitized": external_tool_result["response_metadata_sanitized"],
        "inspected_file_count": external_tool_result["inspected_file_count"],
        "external_request_count": external_tool_result["external_request_count"],
        "human_approval_required": True,
        "human_approval_granted": external_tool_result["approval_receipt"]["human_approval_granted"],
        "no_repo_file_mutation": True,
        "no_response_body_printed": True,
        "no_response_body_stored": True,
        "no_response_body_returned": True,
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


def create_external_tool_safety_boundary_matrix() -> dict:
    return {
        "controlled_live_external_tool_gateway_manifest": "ALLOWED",
        "external_tool_permission_registry": "ALLOWED",
        "external_tool_request_packet": "ALLOWED",
        "external_tool_approval_receipt": "ALLOWED",
        "external_probe_execution_plan": "ALLOWED",
        "controlled_allowlisted_https_get_probe": "ALLOWED",
        "response_metadata_sanitizer": "ALLOWED",
        "routed_v22_v21_v20_v19_v18_v17_operational_chain": "ALLOWED",
        "controlled_external_probe_receipt_json": "ALLOWED",
        "controlled_external_probe_summary_markdown": "ALLOWED",
        "controlled_external_probe_table_csv": "ALLOWED",
        "controlled_external_tool_manifest_json": "ALLOWED",
        "controlled_artifact_readback_verification": "ALLOWED",
        "external_tool_handoff_ledger": "ALLOWED",
        "external_tool_workpack_receipt": "ALLOWED",
        "external_tool_gateway_audit_record": "ALLOWED",
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
        "response_body_storage": "DENIED",
        "response_body_printing": "DENIED",
        "response_body_returning": "DENIED",
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
        "live_task_execution_outside_controlled_external_tool_workpack": "DENIED",
        "live_worker_routing_to_real_processes": "DENIED",
        "uncontrolled_live_orchestration": "DENIED",
        "database_mutation": "DENIED",
        "full_workforce_activation": "DENIED",
        "v23_1_creation": "DENIED",
        "v24_creation": "DENIED"
    }


def create_station_chief_v23_controlled_external_tool_schema() -> dict:
    return {
        "schema_version": STATION_CHIEF_V23_CONTROLLED_EXTERNAL_TOOL_VERSION,
        "schema_type": "station_chief_v23_controlled_live_external_tool_gateway",
        "required_sections": [
            "controlled_live_external_tool_gateway_manifest",
            "external_tool_permission_registry",
            "external_tool_request_packet",
            "external_tool_approval_receipt",
            "external_probe_execution_plan",
            "external_tool_gateway_workpack_execution",
            "response_metadata_sanitizer",
            "external_tool_handoff_ledger",
            "external_tool_workpack_receipt",
            "external_tool_gateway_audit_record",
            "external_tool_safety_boundary_matrix",
            "controlled_external_tool_summary"
        ],
        "controlled_live_external_tool_gateway_authorized": True,
        "allowlisted_web_probe_authorized": True,
        "routed_v22/v21/v20/v19/v18/v17_operational_chain_authorized": True,
        "controlled_external_probe_receipt_artifact_authorized": True,
        "controlled_external_probe_summary_artifact_authorized": True,
        "controlled_external_probe_CSV_artifact_authorized": True,
        "controlled_external_tool_manifest_artifact_authorized": True,
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
        "v23_1_created": False,
        "v24_created": False
    }


def create_station_chief_v23_controlled_external_tool_bundle(approval_phrase: str | None = None, operator_label: str | None = None, workpack_label: str | None = None, requested_url: str | None = None, execute_external_tool_flag: bool = False) -> dict:
    schema = create_station_chief_v23_controlled_external_tool_schema()
    manifest = create_controlled_live_external_tool_gateway_manifest()
    registry = create_external_tool_permission_registry()
    boundaries = create_external_tool_safety_boundary_matrix()
    
    if execute_external_tool_flag:
        res = execute_external_tool_gateway_workpack(approval_phrase, operator_label, workpack_label, requested_url)
    else:
        # Preview only
        packet = create_external_tool_request_packet(operator_label, workpack_label, requested_url)
        approval = create_external_tool_approval_receipt(approval_phrase, packet)
        plan = create_external_probe_execution_plan(registry, packet, approval)
        res = {
            "execution_status": "V23_CONTROLLED_EXTERNAL_TOOL_GATEWAY_NOT_ATTEMPTED",
            "external_tool_gateway_workpack_performed": False,
            "controlled_action_count": 6,
            "completed_action_count": 0,
            "routed_v22_v21_v20_v19_v18_v17_chain_performed": False,
            "controlled_external_web_probe_performed": False,
            "response_metadata_sanitized": False,
            "external_probe_receipt_artifact_written": False,
            "external_probe_summary_artifact_written": False,
            "external_probe_table_artifact_written": False,
            "external_tool_manifest_written": False,
            "controlled_external_artifact_count": 4,
            "inspected_file_count": 0,
            "external_request_count": 0,
            "allowed_external_url": STATION_CHIEF_V23_ALLOWED_EXTERNAL_URL,
            "status_code": None,
            "response_sha256": None,
            "response_byte_count": 0,
            "response_line_count": 0,
            "response_body_printed": False,
            "response_body_stored": False,
            "response_body_returned": False,
            "artifact_paths": STATION_CHIEF_V23_CONTROLLED_ARTIFACT_PATHS,
            "artifact_digests": {},
            "artifact_readback_verified": False,
            "logical_agent_roles_used": True,
            "real_worker_process_started": False,
            "background_agent_started": False,
            "request_packet": packet,
            "approval_receipt": approval,
            "execution_plan": plan,
            "probe_result": {},
            "sanitizer": {},
            "artifact_results": {}
        }
        
    handoff_ledger = create_external_tool_handoff_ledger(res)
    receipt = create_external_tool_workpack_receipt(res, handoff_ledger)
    audit = create_external_tool_gateway_audit_record(res, handoff_ledger, receipt)
    
    status = "CONTROLLED_EXTERNAL_TOOL_GATEWAY_PREVIEW_ONLY"
    if execute_external_tool_flag:
        status = res["execution_status"].replace("V23_", "")

    bundle = {
        "runtime_version": STATION_CHIEF_V23_CONTROLLED_EXTERNAL_TOOL_VERSION,
        "controlled_external_tool_status": status,
        "controlled_live_external_tool_gateway_created": True,
        "external_tool_permission_registry_created": True,
        "external_tool_category_count": 8,
        "executable_external_tool_count": 1,
        "locked_external_tool_count": 7,
        "controlled_action_count": 6,
        "completed_action_count": res["completed_action_count"],
        "controlled_external_artifact_count": 4,
        "external_tool_gateway_workpack_performed": res["external_tool_gateway_workpack_performed"],
        "routed_v22_v21_v20_v19_v18_v17_chain_performed": res["routed_v22_v21_v20_v19_v18_v17_chain_performed"],
        "controlled_external_web_probe_performed": res["controlled_external_web_probe_performed"],
        "response_metadata_sanitized": res["response_metadata_sanitized"],
        "external_probe_receipt_artifact_written": res["external_probe_receipt_artifact_written"],
        "external_probe_summary_artifact_written": res["external_probe_summary_artifact_written"],
        "external_probe_table_artifact_written": res["external_probe_table_artifact_written"],
        "external_tool_manifest_written": res["external_tool_manifest_written"],
        "artifact_readback_verified": res["artifact_readback_verified"],
        "inspected_file_count": res["inspected_file_count"],
        "external_request_count": res["external_request_count"],
        "allowed_external_url": res["allowed_external_url"],
        "status_code": res["status_code"],
        "response_sha256": res["response_sha256"],
        "response_byte_count": res["response_byte_count"],
        "response_line_count": res["response_line_count"],
        "response_body_printed": False,
        "response_body_stored": False,
        "response_body_returned": False,
        "artifact_paths": res["artifact_paths"],
        "artifact_digests": res["artifact_digests"],
        "external_tool_handoff_ledger_created": True,
        "handoff_receipt_count": 6,
        "external_tool_workpack_receipt_created": True,
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
        "v23_1_created": False,
        "v24_created": False,
        
        "schema": schema,
        "controlled_live_external_tool_gateway_manifest": manifest,
        "external_tool_permission_registry": registry,
        "external_tool_request_packet": res["request_packet"],
        "external_tool_approval_receipt": res["approval_receipt"],
        "external_probe_execution_plan": res["execution_plan"],
        "external_tool_gateway_workpack_execution": res,
        "response_metadata_sanitizer": res["sanitizer"],
        "external_tool_handoff_ledger": handoff_ledger,
        "external_tool_workpack_receipt": receipt,
        "external_tool_gateway_audit_record": audit,
        "external_tool_safety_boundary_matrix": boundaries,
        "controlled_external_tool_summary": {
            "version": STATION_CHIEF_V23_CONTROLLED_EXTERNAL_TOOL_VERSION,
            "status": status
        }
    }
    bundle["bundle_digest"] = sha256_digest(bundle)
    return bundle
