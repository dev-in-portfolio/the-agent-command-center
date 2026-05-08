#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNTIME = REPO_ROOT / "10_runtime" / "station_chief_runtime.py"
V5_9_MODULE = REPO_ROOT / "10_runtime" / "station_chief_sandbox_worker_dry_run_replay_audit_candidate.py"
README = REPO_ROOT / "10_runtime" / "station_chief_runtime_readme.md"
SKELETON = REPO_ROOT / "09_exports" / "station_chief_runtime_skeleton_report.md"
REPORT = REPO_ROOT / "09_exports" / "station_chief_runtime_v5_9_report.md"
AUDIT = REPO_ROOT / "09_exports" / "station_chief_v5_9_sandbox_worker_dry_run_replay_audit_candidate_preflight_audit.md"
ADAPTERS = REPO_ROOT / "10_runtime" / "station_chief_adapters.py"
RELEASE_LOCK = REPO_ROOT / "10_runtime" / "station_chief_release_lock.py"

EXPECTED_TOKEN = "YES_I_APPROVE_SANDBOX_WORKER_DRY_RUN_REPLAY_AUDIT_CANDIDATE"
HUMAN_OPERATOR = "Devin"
SANDBOX_WORKER_LABEL = "sandbox worker alpha"
V5_3_REFERENCE_LABEL = "handoff packet reference alpha"
V5_4_REFERENCE_LABEL = "acknowledgement packet reference alpha"
V5_5_REFERENCE_LABEL = "acceptance review packet reference alpha"
V5_6_REFERENCE_LABEL = "ready state packet reference alpha"
V5_7_REFERENCE_LABEL = "dry run assignment packet reference alpha"
V5_8_REFERENCE_LABEL = "dry run result packet reference alpha"
DRY_RUN_TASK_LABEL = "synthetic dry run task alpha"
DRY_RUN_RESULT_LABEL = "synthetic dry run result alpha"
REPLAY_AUDIT_LABEL = "synthetic replay audit candidate alpha"
DEFAULT_PACKET_NAME = "sandbox_worker_dry_run_replay_audit_candidate_packet.json"

FORBIDDEN_REGEXES = [
    r"import\s+requests\b",
    r"from\s+requests\b",
    r"urllib\.request",
    r"import\s+urllib\.request",
    r"import\s+socket\b",
    r"from\s+socket\b",
    r"socket\.socket\(",
    r"subprocess\.run\(",
    r"subprocess\.Popen\(",
    r"import\s+subprocess\b",
    r"os\.system\(",
    r"eval\(",
    r"exec\(",
    r"compile\(",
    r"__import__\(",
    r"os\.getenv\b",
    r"os\.environ\b",
    r"getenv\(",
    r"environ\[",
    r"open\(",
    r"gh api",
    r"git push",
    r"create_deployment",
    r"create_commit",
    r"update_ref",
    r"threading\b",
    r"multiprocessing\b",
    r"queue\.Queue\(",
    r"asyncio\b",
    r"kill\(",
    r"terminate\(",
    r"pip install",
    r"npm install",
    r"worker\.start\(",
    r"start_worker\(",
    r"start_process\(",
    r"daemon\(",
    r"scheduler\(",
    r"enqueue\(",
    r"dispatch\(",
    r"route_live\(",
    r"execute_task\(",
    r"run_task\(",
    r"assign_live_task\(",
    r"orchestrate\(",
    r"orchestrate_live\(",
    r"live_orchestration\(",
    r"create_queue\(",
    r"write_queue\(",
    r"arbitrary_task_execution\(",
    r"user_task_execution\(",
    r"execute_user\(",
    r"shlex\b",
    r"system\(",
]

def ensure(condition: bool, message: str) -> None:
    if not condition:
        print(f"VALIDATION_FAILURE: {message}")
        sys.exit(1)

def run_json(script_path: Path, args: list[str]) -> dict:
    cmd = [sys.executable, str(script_path)] + args
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"DEBUG: Failed to parse JSON from: {result.stdout}")
        raise

def validate_v5_9() -> None:
    print("Validating Station Chief Runtime v5.9.0...")
    
    ensure(RUNTIME.exists(), "runtime.py missing")
    ensure(V5_9_MODULE.exists(), "v5.9 module missing")
    ensure(README.exists(), "README missing")
    ensure(SKELETON.exists(), "skeleton report missing")
    ensure(REPORT.exists(), "v5.9 report missing")
    ensure(AUDIT.exists(), "v5.9 audit missing")
    ensure(ADAPTERS.exists(), "adapters missing")
    ensure(RELEASE_LOCK.exists(), "release lock missing")
    
    # Version checks
    runtime_code = RUNTIME.read_text(encoding="utf-8")
    ensure('STATION_CHIEF_RUNTIME_VERSION = "5.9.0"' in runtime_code, "runtime version mismatch")
    
    adapters_code = ADAPTERS.read_text(encoding="utf-8")
    ensure('ADAPTER_MODULE_VERSION = "5.9.0"' in adapters_code, "adapter version mismatch")
    
    lock_code = RELEASE_LOCK.read_text(encoding="utf-8")
    ensure('STABLE_RUNTIME_VERSION = "5.9.0"' in lock_code, "release lock version mismatch")
    
    # Module constants
    module_code = V5_9_MODULE.read_text(encoding="utf-8")
    ensure('SANDBOX_WORKER_DRY_RUN_REPLAY_AUDIT_CANDIDATE_MODULE_VERSION = "5.9.0"' in module_code, "module version mismatch")
    
    # Implementation safety
    for pattern in FORBIDDEN_REGEXES:
        ensure(not re.search(pattern, module_code), f"forbidden implementation pattern found: {pattern}")
        
    # Schema check
    schema = run_json(RUNTIME, ["--sandbox-worker-dry-run-replay-audit-candidate-schema"])
    ensure(schema["schema_version"] == "5.9.0", "schema version mismatch")
    
    # No-token block
    no_token_res = run_json(RUNTIME, [
        "--command", "check please",
        "--sandbox-worker-dry-run-replay-audit-candidate",
        "--json"
    ])
    gate = no_token_res.get("sandbox_worker_dry_run_replay_audit_approval_gate", {})
    ensure(gate.get("status") == "BLOCKED_PENDING_V5_9_SANDBOX_WORKER_DRY_RUN_REPLAY_AUDIT_CANDIDATE_APPROVAL", "no-token path should block")
    
    # Bad-token block
    bad_token_res = run_json(RUNTIME, [
        "--command", "check please",
        "--sandbox-worker-dry-run-replay-audit-candidate",
        "--v5-dry-run-replay-audit-confirm-token", "WRONG_TOKEN",
        "--v5-dry-run-replay-audit-human-operator", HUMAN_OPERATOR,
        "--json"
    ])
    gate = bad_token_res.get("sandbox_worker_dry_run_replay_audit_approval_gate", {})
    ensure(gate.get("status") == "BLOCKED_PENDING_V5_9_SANDBOX_WORKER_DRY_RUN_REPLAY_AUDIT_CANDIDATE_APPROVAL", "bad-token path should block")
    
    # Valid token, no write
    valid_res = run_json(RUNTIME, [
        "--command", "check please",
        "--sandbox-worker-dry-run-replay-audit-candidate",
        "--v5-replay-sandbox-worker-label", SANDBOX_WORKER_LABEL,
        "--v5-replay-handoff-packet-reference-label", V5_3_REFERENCE_LABEL,
        "--v5-replay-acknowledgement-packet-reference-label", V5_4_REFERENCE_LABEL,
        "--v5-replay-acceptance-review-packet-reference-label", V5_5_REFERENCE_LABEL,
        "--v5-replay-ready-state-packet-reference-label", V5_6_REFERENCE_LABEL,
        "--v5-replay-dry-run-assignment-packet-reference-label", V5_7_REFERENCE_LABEL,
        "--v5-replay-dry-run-result-packet-reference-label", V5_8_REFERENCE_LABEL,
        "--v5-replay-task-label", DRY_RUN_TASK_LABEL,
        "--v5-replay-result-label", DRY_RUN_RESULT_LABEL,
        "--v5-replay-audit-label", REPLAY_AUDIT_LABEL,
        "--v5-dry-run-replay-audit-confirm-token", EXPECTED_TOKEN,
        "--v5-dry-run-replay-audit-human-operator", HUMAN_OPERATOR,
        "--json"
    ])
    ensure(valid_res.get("local_dry_run_replay_audit_packet_written") is False, "no-write path should not write")
    ensure(valid_res.get("sandbox_worker_dry_run_replay_audit_candidate_created") is False, "no-write path should not create")
    
    # Write path
    with tempfile.TemporaryDirectory() as tmp_dir:
        write_res = run_json(RUNTIME, [
            "--command", "check please",
            "--write-sandbox-worker-dry-run-replay-audit-candidate", tmp_dir,
            "--v5-replay-sandbox-worker-label", SANDBOX_WORKER_LABEL,
            "--v5-replay-handoff-packet-reference-label", V5_3_REFERENCE_LABEL,
            "--v5-replay-acknowledgement-packet-reference-label", V5_4_REFERENCE_LABEL,
            "--v5-replay-acceptance-review-packet-reference-label", V5_5_REFERENCE_LABEL,
            "--v5-replay-ready-state-packet-reference-label", V5_6_REFERENCE_LABEL,
            "--v5-replay-dry-run-assignment-packet-reference-label", V5_7_REFERENCE_LABEL,
            "--v5-replay-dry-run-result-packet-reference-label", V5_8_REFERENCE_LABEL,
            "--v5-replay-task-label", DRY_RUN_TASK_LABEL,
            "--v5-replay-result-label", DRY_RUN_RESULT_LABEL,
            "--v5-replay-audit-label", REPLAY_AUDIT_LABEL,
            "--v5-dry-run-replay-audit-confirm-token", EXPECTED_TOKEN,
            "--v5-dry-run-replay-audit-human-operator", HUMAN_OPERATOR,
            "--v5-dry-run-replay-audit-packet-name", DEFAULT_PACKET_NAME,
            "--json"
        ])
        
        ensure(write_res.get("local_dry_run_replay_audit_packet_written") is True, "write path should mark written")
        ensure(write_res.get("sandbox_worker_dry_run_replay_audit_candidate_created") is True, "write path should mark created")
        
        written_files = list(Path(tmp_dir).iterdir())
        ensure(len(written_files) == 1, "exactly one file should be written")
        packet_path = written_files[0]
        ensure(packet_path.name == DEFAULT_PACKET_NAME, "packet name mismatch")
        
        packet_payload = json.loads(packet_path.read_text(encoding="utf-8"))
        ensure(packet_payload["runtime_version"] == "5.9.0", "payload version mismatch")
        ensure(packet_payload["replay_audit_type"] == "sandbox_worker_dry_run_replay_audit_candidate", "payload type mismatch")
        ensure(packet_payload["local_dry_run_replay_audit_packet_written"] is True, "payload write flag mismatch")
        
    # Safety booleans
    for key in [
        "dry_run_task_executed", "real_worker_result_created", "live_replay_performed",
        "production_audit_performed", "rollback_performed", "recovery_performed",
        "mvp_lock_created", "v6_0_created", "worker_process_started", "agent_started"
    ]:
        ensure(write_res.get(key) is False, f"dangerous flag must be false: {key}")
        
    # V6.0 absence
    v6_0_files = list(REPO_ROOT.rglob("*v6_0*")) + list(REPO_ROOT.rglob("*v6.0*")) + list(REPO_ROOT.rglob("*mvp*lock*"))
    ensure(len(v6_0_files) == 0, f"unexpected v6.0/MVP lock files found: {v6_0_files}")
    
    print("STATION_CHIEF_RUNTIME_V5_9_VALIDATION_PASS")

if __name__ == "__main__":
    validate_v5_9()
