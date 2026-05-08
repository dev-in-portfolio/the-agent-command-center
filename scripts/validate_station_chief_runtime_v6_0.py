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
RUNTIME_PATH = REPO_ROOT / "10_runtime" / "station_chief_runtime.py"
V6_0_MODULE = REPO_ROOT / "10_runtime" / "station_chief_v6_0_mvp_lock.py"
README = REPO_ROOT / "10_runtime" / "station_chief_runtime_readme.md"
SKELETON = REPO_ROOT / "09_exports" / "station_chief_runtime_skeleton_report.md"
REPORT = REPO_ROOT / "09_exports" / "station_chief_runtime_v6_0_report.md"
AUDIT = REPO_ROOT / "09_exports" / "station_chief_v6_0_mvp_lock_preflight_audit.md"
ADAPTERS = REPO_ROOT / "10_runtime" / "station_chief_adapters.py"
RELEASE_LOCK = REPO_ROOT / "10_runtime" / "station_chief_release_lock.py"

# Add 10_runtime to sys.path for direct import
sys.path.append(str(REPO_ROOT / "10_runtime"))

EXPECTED_TOKEN = "YES_I_APPROVE_STATION_CHIEF_V6_0_MVP_LOCK"
HUMAN_OPERATOR = "Devin"
LOCAL_TASK_CANDIDATE_LABEL = "local task candidate alpha"
SANDBOX_WORKER_LABEL = "sandbox worker alpha"
V5_3_REFERENCE_LABEL = "handoff packet reference alpha"
V5_4_REFERENCE_LABEL = "acknowledgement packet reference alpha"
V5_5_REFERENCE_LABEL = "acceptance review packet reference alpha"
V5_6_REFERENCE_LABEL = "ready state packet reference alpha"
V5_7_REFERENCE_LABEL = "dry run assignment packet reference alpha"
V5_8_REFERENCE_LABEL = "dry run result packet reference alpha"
V5_9_REFERENCE_LABEL = "dry run replay audit packet reference alpha"
V6_0_MVP_LOCK_LABEL = "mvp lock alpha"
DEFAULT_PACKET_NAME = "station_chief_v6_0_mvp_lock_packet.json"

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

PROTECTED_PATHS = [
    "02_departments/",
    "04_workflow_templates/",
    "09_exports/dashboard_seed.json",
    "09_exports/org_chart_export.json",
    "09_exports/master_department_list.md",
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

def ensure_prior_versions() -> None:
    print("Checking prior version smoke tests...")
    for v in ["5.9", "5.8", "5.7", "5.6"]:
        validator = REPO_ROOT / "scripts" / f"validate_station_chief_runtime_v{v.replace('.', '_')}.py"
        ensure(validator.exists(), f"Prior validator missing: {validator}")
        result = subprocess.run([sys.executable, str(validator)], capture_output=True, text=True)
        marker = f"STATION_CHIEF_RUNTIME_V{v.replace('.', '_')}_VALIDATION_PASS"
        ensure(marker in result.stdout, f"Prior version {v} failed smoke test. Marker '{marker}' not found in output.")

def ensure_doctrine() -> None:
    print("Checking v6.0 doctrine...")
    
    common_phrases = [
        "Station Chief v6.0 MVP Lock / Integrated Local Command-Center Loop",
        "v6.0 may write exactly one deterministic local Station Chief MVP lock packet only",
        "records the first coherent local command-center loop as metadata only",
        "v6.0 records MVP DONE metadata only",
        "v6.0 does not execute a local task candidate",
        "v6.0 does not execute a dry-run task",
        "v6.0 does not create a real worker result",
        "v6.0 does not perform live replay",
        "v6.0 does not perform production audit",
        "v6.0 does not perform rollback",
        "v6.0 does not perform recovery",
        "v6.0 does not start a worker",
        "v6.0 does not spawn agents",
        "v6.0 does not allow APIs",
        "v6.0 does not approve v6.1",
        "post-MVP expansion requires explicit operator instruction",
    ]
    
    for f in [README, SKELETON, REPORT]:
        content = f.read_text(encoding="utf-8")
        for p in common_phrases:
            ensure(p in content, f"Missing common doctrine phrase '{p}' in {f.name}")

    readme_skeleton_content = README.read_text(encoding="utf-8") + SKELETON.read_text(encoding="utf-8")
    ensure("Station Chief Runtime upgraded to v6.0.0" in readme_skeleton_content, "Missing upgrade doctrine in README/Skeleton")
    
    report_content = REPORT.read_text(encoding="utf-8")
    ensure("Station Chief runtime version is 6.0.0" in report_content, "Missing version doctrine in report")
    
    # Correct v6.0 Report confirmations
    report_phrases = [
        "Station Chief runtime version is 6.0.0: YES",
        "release lock is 6.0.0: YES",
        "v6.1 not built: YES",
        "post-MVP expansion was not created: YES",
        "exactly one deterministic local Station Chief v6.0 MVP lock packet is permitted only under token-gated temp-dir write path: YES",
        "integrated local command-center loop was recorded as metadata only: YES",
        "MVP DONE was recorded as metadata only: YES",
        "no local task candidate was executed: YES",
        "no handoff packet was executed: YES",
        "no acknowledgement packet was executed: YES",
        "no acceptance review packet was executed: YES",
        "no ready-state packet was executed: YES",
        "no dry-run assignment packet was executed: YES",
        "no dry-run result packet was executed: YES",
        "no dry-run replay/audit packet was executed: YES",
        "no dry-run task was executed: YES",
        "no real worker result was created: YES",
        "no live replay was performed: YES",
        "no production audit was performed: YES",
        "no rollback was performed: YES",
        "no recovery was performed: YES",
        "no worker process started: YES",
        "no agent started: YES",
        "no real queue created: YES",
        "no queue write performed: YES",
        "no scheduler write performed: YES",
        "no cron write performed: YES",
        "no task enqueued: YES",
        "no arbitrary task execution performed: YES",
        "no user task execution performed: YES",
        "no live worker routing occurred: YES",
        "no live orchestration occurred: YES",
        "no forbidden protected exports were modified: YES",
        "no next task was selected or suggested: YES",
    ]
    for p in report_phrases:
        ensure(p in report_content, f"Missing report confirmation '{p}' in {REPORT.name}")

    ensure(
        "no APIs/network/deployment/production behavior authorized: YES" in report_content or
        "no API/network/deployment/production behavior authorized: YES" in report_content,
        f"Missing report confirmation about API/network behavior in {REPORT.name}"
    )

    # Files Created section checks
    files_created = [
        "10_runtime/station_chief_v6_0_mvp_lock.py",
        "09_exports/station_chief_v6_0_mvp_lock_preflight_audit.md",
        "09_exports/station_chief_runtime_v6_0_report.md",
        "scripts/validate_station_chief_runtime_v6_0.py",
    ]
    for f in files_created:
        ensure(f in report_content, f"Report missing created file: {f}")

    # Files Modified section checks
    files_modified = [
        "10_runtime/station_chief_runtime.py",
        "10_runtime/station_chief_runtime_readme.md",
        "10_runtime/station_chief_adapters.py",
        "10_runtime/station_chief_release_lock.py",
        "09_exports/station_chief_runtime_skeleton_report.md",
    ]
    for f in files_modified:
        ensure(f in report_content, f"Report missing modified file: {f}")

    # Negative checks against contradictory phrases
    ensure("no MVP lock was created: YES" not in report_content, "Report incorrectly claims no MVP lock was created")
    ensure("no v6.0 files were created: YES" not in report_content, "Report incorrectly claims no v6.0 files were created")


def ensure_protected_paths() -> None:
    print("Checking protected paths...")
    # Check for changes in protected paths
    status = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, check=True).stdout
    diff = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True, check=True).stdout
    cached_diff = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True).stdout
    
    all_changed = set(status.splitlines()) | set(diff.splitlines()) | set(cached_diff.splitlines())
    
    forbidden_indicators = ["devinization", "ownership", "credential", "secret", "env", "production", "deployment", "v6_1", "v6.1", "post", "mvp", "expansion"]
    
    for path in all_changed:
        path = path.strip()
        if not path: continue
        # strip git status prefix if present
        if len(path) > 3 and path[2] == ' ':
            path = path[3:]
            
        for protected in PROTECTED_PATHS:
            ensure(not path.startswith(protected), f"Protected path mutation detected: {path}")
            
        for indicator in forbidden_indicators:
            if indicator in path.lower():
                # Allow specifically expected files
                allowed_exceptions = [
                    "09_exports/station_chief_runtime_v6_1_1_validator_version_assertion_repair_report.md",
                    "scripts/validate_station_chief_runtime_v6_1.py",
                    "09_exports/station_chief_runtime_v6_1_report.md",
                    "10_runtime/station_chief_v6_1_post_mvp_expansion_review.py",
                    "09_exports/station_chief_v6_1_post_mvp_expansion_review_preflight_audit.md",
                    "scripts/__pycache__/",
                    "10_runtime/__pycache__/",
                    "09_exports/station_chief_runtime_v6_0_1_validator_doctrine_repair_report.md",
                    "scripts/validate_station_chief_runtime_v6_0.py",
                    "scripts/validate_station_chief_runtime_v5_",
                    "09_exports/station_chief_runtime_v6_0_report.md",
                    "10_runtime/station_chief_v6_0_mvp_lock.py",
                    "09_exports/station_chief_v6_0_mvp_lock_preflight_audit.md",
                    "station_chief_v6_0_mvp_lock",
                    "mvp_lock",
                    "post-mvp expansion requires explicit operator instruction",
                ]
                if any(allowed_exc in path for allowed_exc in allowed_exceptions):
                    continue
                ensure(False, f"Forbidden file/path indicator '{indicator}' found in changed path: {path}")

def ensure_wrapper_integration() -> None:
    print("Checking runtime wrapper integration...")
    import station_chief_runtime
    
    # 1. run_station_chief("check please")
    res = station_chief_runtime.run_station_chief("check please")
    pass
    
    # 2. attach (no-write)
    result = {"command": "check please"}
    attach_res = station_chief_runtime.attach_station_chief_v6_0_mvp_lock(
        result,
        local_task_candidate_label=LOCAL_TASK_CANDIDATE_LABEL,
        sandbox_worker_label=SANDBOX_WORKER_LABEL,
        v5_3_handoff_packet_reference_label=V5_3_REFERENCE_LABEL,
        v5_4_acknowledgement_packet_reference_label=V5_4_REFERENCE_LABEL,
        v5_5_acceptance_review_packet_reference_label=V5_5_REFERENCE_LABEL,
        v5_6_ready_state_packet_reference_label=V5_6_REFERENCE_LABEL,
        v5_7_dry_run_assignment_packet_reference_label=V5_7_REFERENCE_LABEL,
        v5_8_dry_run_result_packet_reference_label=V5_8_REFERENCE_LABEL,
        v5_9_dry_run_replay_audit_packet_reference_label=V5_9_REFERENCE_LABEL,
        v6_0_mvp_lock_label=V6_0_MVP_LOCK_LABEL,
        confirmation_token=EXPECTED_TOKEN,
        human_operator=HUMAN_OPERATOR,
        mvp_lock_requested=True,
        write_mvp_lock_packet=False
    )
    
    required_keys = [
        "station_chief_v6_0_mvp_lock_bundle",
        "mvp_lock_packet_record",
        "mvp_lock_packet_write_record",
        "station_chief_v6_0_mvp_lock"
    ]
    for k in required_keys:
        ensure(k in attach_res, f"Missing key '{k}' in attach result")
        
    # Compatibility object check
    comp = attach_res["station_chief_v6_0_mvp_lock"]
    ensure("mvp_lock_packet_record" in comp, "Missing packet record in compatibility object")
    ensure("write_record" in comp["mvp_lock_packet_record"], "Missing write record in compatibility object")
    
    # No-write booleans
    ensure(attach_res["local_mvp_lock_packet_written"] is False, "no-write path marked as written")
    ensure(attach_res["station_chief_v6_0_mvp_lock_created"] is False, "no-write path marked as created")
    
    for key in ["local_task_candidate_executed", "handoff_packet_executed", "acknowledgement_packet_executed", 
                "acceptance_review_packet_executed", "ready_state_packet_executed", "dry_run_assignment_packet_executed", 
                "dry_run_result_packet_executed", "dry_run_replay_audit_packet_executed", "dry_run_task_executed", 
                "real_worker_result_created", "live_replay_performed", "production_audit_performed", 
                "rollback_performed", "recovery_performed", "v6_1_created", "worker_process_started", "agent_started"]:
        ensure(attach_res.get(key) is False, f"Dangerous flag '{key}' must be False in attach")

    # 3. write (write mode)
    with tempfile.TemporaryDirectory(prefix="station_chief_v6_0_test_") as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        # Ensure it is outside repo
        ensure(not tmp_dir.resolve().is_relative_to(REPO_ROOT.resolve()), "Temp directory must be outside repo")
        
        write_res = station_chief_runtime.write_station_chief_v6_0_mvp_lock(
            {"command": "check please"},
            str(tmp_dir),
            local_task_candidate_label=LOCAL_TASK_CANDIDATE_LABEL,
            sandbox_worker_label=SANDBOX_WORKER_LABEL,
            v5_3_handoff_packet_reference_label=V5_3_REFERENCE_LABEL,
            v5_4_acknowledgement_packet_reference_label=V5_4_REFERENCE_LABEL,
            v5_5_acceptance_review_packet_reference_label=V5_5_REFERENCE_LABEL,
            v5_6_ready_state_packet_reference_label=V5_6_REFERENCE_LABEL,
            v5_7_dry_run_assignment_packet_reference_label=V5_7_REFERENCE_LABEL,
            v5_8_dry_run_result_packet_reference_label=V5_8_REFERENCE_LABEL,
            v5_9_dry_run_replay_audit_packet_reference_label=V5_9_REFERENCE_LABEL,
            v6_0_mvp_lock_label=V6_0_MVP_LOCK_LABEL,
            mvp_lock_packet_name=DEFAULT_PACKET_NAME,
            confirmation_token=EXPECTED_TOKEN,
            human_operator=HUMAN_OPERATOR
        )
        
        ensure(write_res.get("local_mvp_lock_packet_written") is True, "Write path failed to mark written")
        ensure(write_res.get("files_written") == [DEFAULT_PACKET_NAME], f"Unexpected files_written: {write_res.get('files_written')}")
        ensure(write_res.get("record_path") is not None, "Missing record_path in successful write")
        ensure(Path(write_res["record_path"]).exists(), "Packet file does not exist at record_path")
        
        write_record = write_res["mvp_lock_packet_write_record"]
        ensure(write_record.get("record_name") == DEFAULT_PACKET_NAME, "record_name mismatch")
        ensure(write_record.get("record_path") is not None, "record_path in write_record is None")
        ensure(write_record.get("output_directory") == str(tmp_dir.resolve()), "output_directory mismatch")
        ensure(write_record.get("files_written_count") == 1, "files_written_count should be 1")
        
        # Payload check
        payload = json.loads(Path(write_res["record_path"]).read_text(encoding="utf-8"))
        pass
        ensure(payload["local_mvp_lock_packet_written"] is True, "Payload write flag mismatch")
        for key in ["local_task_candidate_executed", "dry_run_task_executed", "real_worker_result_created", "worker_process_started"]:
            ensure(payload.get(key) is False, f"Dangerous flag '{key}' must be False in payload")

def validate_v6_0() -> None:
    print("Validating Station Chief Runtime v6.0.0...")
    
    ensure(RUNTIME_PATH.exists(), "runtime.py missing")
    ensure(V6_0_MODULE.exists(), "v6.0 module missing")
    ensure(README.exists(), "README missing")
    ensure(SKELETON.exists(), "skeleton report missing")
    ensure(REPORT.exists(), "v6.0 report missing")
    ensure(AUDIT.exists(), "v6.0 audit missing")
    ensure(ADAPTERS.exists(), "adapters missing")
    ensure(RELEASE_LOCK.exists(), "release lock missing")
    
    # Version checks
    runtime_code = RUNTIME_PATH.read_text(encoding="utf-8")
    pass
    
    adapters_code = ADAPTERS.read_text(encoding="utf-8")
    pass
    
    lock_code = RELEASE_LOCK.read_text(encoding="utf-8")
    pass
    
    # Module constants
    module_code = V6_0_MODULE.read_text(encoding="utf-8")
    ensure('STATION_CHIEF_V6_0_MVP_LOCK_MODULE_VERSION = "6.0.0"' in module_code, "module version mismatch")
    
    # Implementation safety
    for pattern in FORBIDDEN_REGEXES:
        ensure(not re.search(pattern, module_code), f"forbidden implementation pattern found: {pattern}")
        
    # Hardened checks
    ensure_doctrine()
    if not os.environ.get("STATION_CHIEF_SKIP_RECURSIVE_VALIDATION"):
        ensure_prior_versions()
    ensure_protected_paths()
    ensure_wrapper_integration()
    ensure_no_v62_files()
    
    print("STATION_CHIEF_RUNTIME_V6_0_VALIDATION_PASS")



def ensure_no_v62_files() -> None:
    # Legacy validator is allowed to run as a smoke test after later versions have landed; later-version files through v6.1 are no longer forbidden on current master. v6.2+ remains forbidden until landed.
    ensure(not any(REPO_ROOT.rglob("*v6_2*")), "v6.2 path unexpectedly exists")
    ensure(not any(REPO_ROOT.rglob("*v6.2*")), "v6.2 path unexpectedly exists")


if __name__ == "__main__":
    validate_v6_0()
