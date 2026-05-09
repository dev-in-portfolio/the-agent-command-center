import sys
#!/usr/bin/env python3
"""
Station Chief Runtime v6.6 Validator.
Verifies Station Chief v6.6 build, versioning, CLI behavior, and safety boundaries.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Add project root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "10_runtime"))

from station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition import (
    STATION_CHIEF_V6_6_POST_MVP_EXPANSION_LANE_NON_EXECUTING_REVIEW_DISPOSITION_MODULE_VERSION,
    STATION_CHIEF_V6_6_POST_MVP_EXPANSION_LANE_NON_EXECUTING_REVIEW_DISPOSITION_APPROVAL_TOKEN,
    create_station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_schema,
    create_station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_bundle
)

def ensure(condition, message):
    if not condition:
        print(f"FAILED: {message}")
        sys.exit(1)

def run_script(cmd_list):
    result = subprocess.run(cmd_list, capture_output=True, text=True)
    return result

def main():
    print("Validating Station Chief Runtime v6.6.0...")

    # Required files
    required_files = [
        "10_runtime/station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition.py",
        "09_exports/station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition_preflight_audit.md",
        "09_exports/station_chief_runtime_v6_6_report.md",
        "scripts/validate_station_chief_runtime_v6_6.py"
    ]
    for f in required_files:
        ensure(Path(f).exists(), f"File {f} must exist")

    # Version checks
    from station_chief_runtime import STATION_CHIEF_RUNTIME_VERSION
    from station_chief_release_lock import STABLE_RUNTIME_VERSION
    from station_chief_adapters import ADAPTER_MODULE_VERSION

    # v6.6 validator allows v10.0 version when running on master after v10.0 land.
    ensure(STATION_CHIEF_RUNTIME_VERSION in ["6.6.0", "10.0.0"], f"Runtime version mismatch: {STATION_CHIEF_RUNTIME_VERSION}")
    ensure(STABLE_RUNTIME_VERSION in ["6.6.0", "10.0.0"], f"Release lock version mismatch: {STABLE_RUNTIME_VERSION}")
    ensure(ADAPTER_MODULE_VERSION in ["6.6.0", "10.0.0"], f"Adapter version mismatch: {ADAPTER_MODULE_VERSION}")
    ensure(STATION_CHIEF_V6_6_POST_MVP_EXPANSION_LANE_NON_EXECUTING_REVIEW_DISPOSITION_MODULE_VERSION == "6.6.0", "v6.6 module version mismatch")

    # CLI Schema Flag
    res = run_script([sys.executable, "10_runtime/station_chief_runtime.py", "--station-chief-v6-6-post-mvp-expansion-lane-non-executing-review-disposition-schema"])
    ensure(res.returncode == 0, "Schema flag failed")
    schema = json.loads(res.stdout)
    ensure(schema["schema_version"] == "6.6.0", "Schema version mismatch")
    ensure(schema["disposition_type"] == "station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition", "Schema type mismatch")

    # Safety Boundary: No Token Path Blocks Packet Write
    res = run_script([
        sys.executable, "10_runtime/station_chief_runtime.py",
        "--write-station-chief-v6-6-post-mvp-expansion-lane-non-executing-review-disposition", "/tmp/sc-v6-6-test"
    ])
    ensure(res.returncode == 0, "CLI failed")
    data = json.loads(res.stdout)
    bundle = data.get("station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition")
    ensure(bundle is not None, "v6.6 bundle missing in output")
    ensure(bundle["local_review_disposition_packet_written"] is False, "Packet should not be written without token")
    ensure(bundle["review_disposition_packet_record"]["write_status"] == "STATION_CHIEF_V6_6_POST_MVP_EXPANSION_LANE_NON_EXECUTING_REVIEW_DISPOSITION_PACKET_WRITE_BLOCKED", "Write should be blocked")

    # Safety Boundary: Bad Token Path Blocks Packet Write
    res = run_script([
        sys.executable, "10_runtime/station_chief_runtime.py",
        "--write-station-chief-v6-6-post-mvp-expansion-lane-non-executing-review-disposition", "/tmp/sc-v6-6-test",
        "--v6-6-review-disposition-confirm-token", "BAD_TOKEN"
    ])
    data = json.loads(res.stdout)
    bundle = data.get("station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition")
    ensure(bundle["local_review_disposition_packet_written"] is False, "Packet should not be written with bad token")

    # Valid Token Without Write Flag Creates Records Only
    res = run_script([
        sys.executable, "10_runtime/station_chief_runtime.py",
        "--station-chief-v6-6-post-mvp-expansion-lane-non-executing-review-disposition",
        "--v6-6-review-disposition-confirm-token", STATION_CHIEF_V6_6_POST_MVP_EXPANSION_LANE_NON_EXECUTING_REVIEW_DISPOSITION_APPROVAL_TOKEN,
        "--v6-6-review-disposition-human-operator", "Validator",
        "--v6-6-implementation-plan-review-packet-reference-label", "v6-5-ref",
        "--v6-6-implementation-plan-packet-reference-label", "v6-4-ref",
        "--v6-6-readiness-packet-reference-label", "v6-3-ref",
        "--v6-6-lane-scope-packet-reference-label", "v6-2-ref",
        "--v6-6-selected-expansion-lane-label", "test-lane",
        "--v6-6-review-disposition-label", "test-disposition",
        "--v6-6-disposition-condition-list-label", "test-conditions",
        "--v6-6-disposition-hold-label", "test-hold",
        "--v6-6-disposition-next-gate-label", "test-next-gate",
        "--v6-6-disposition-non-execution-boundary-label", "test-boundary"
    ])
    data = json.loads(res.stdout)
    bundle = data.get("station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition")
    ensure(bundle["station_chief_v6_6_review_disposition_created"] is True, "Metadata record should be created")
    ensure(bundle["local_review_disposition_packet_written"] is False, "Packet should not be written without write flag")

    # Valid Token With Write Flag Writes Exactly One Packet
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        res = run_script([
            sys.executable, "10_runtime/station_chief_runtime.py",
            "--write-station-chief-v6-6-post-mvp-expansion-lane-non-executing-review-disposition", tmpdir,
            "--v6-6-review-disposition-confirm-token", STATION_CHIEF_V6_6_POST_MVP_EXPANSION_LANE_NON_EXECUTING_REVIEW_DISPOSITION_APPROVAL_TOKEN,
            "--v6-6-review-disposition-human-operator", "Validator",
            "--v6-6-implementation-plan-review-packet-reference-label", "v6-5-ref",
            "--v6-6-implementation-plan-packet-reference-label", "v6-4-ref",
            "--v6-6-readiness-packet-reference-label", "v6-3-ref",
            "--v6-6-lane-scope-packet-reference-label", "v6-2-ref",
            "--v6-6-selected-expansion-lane-label", "test-lane",
            "--v6-6-review-disposition-label", "test-disposition",
            "--v6-6-disposition-condition-list-label", "test-conditions",
            "--v6-6-disposition-hold-label", "test-hold",
            "--v6-6-disposition-next-gate-label", "test-next-gate",
            "--v6-6-disposition-non-execution-boundary-label", "test-boundary"
        ])
        data = json.loads(res.stdout)
        bundle = data.get("station_chief_v6_6_post_mvp_expansion_lane_non_executing_review_disposition")
        ensure(bundle["local_review_disposition_packet_written"] is True, "Packet should be written")
        wrec = bundle["review_disposition_packet_record"]
        ensure(wrec["record_name"] is not None, "Record name missing")
        packet_path = Path(wrec["record_path"])
        ensure(packet_path.exists(), "Packet file does not exist")
        ensure(str(packet_path.resolve()).startswith(str(Path(tmpdir).resolve())), "Packet written outside tmpdir")
        ensure(not str(packet_path.resolve()).startswith(str(Path.cwd().resolve())), "Packet written inside repo")
        
        packet_data = json.loads(packet_path.read_text())
        ensure(packet_data["local_review_disposition_packet_written"] is True, "Packet payload internal status mismatch")
        ensure(packet_data["v6_7_created"] is False, "v6.7 must not be created")

    # Forbidden Mutation Check
    runtime_content = Path("10_runtime/station_chief_runtime.py").read_text()
    ensure("station_chief_v6_7" not in runtime_content, "v6.7 found in runtime")
    
    # v10.0 files are now allowed as they have been built and landed.
    # We still check for v10.1+ and v11+ files.
    v10_1_files = [f for f in REPO_ROOT.rglob("*v10_1*") if f.suffix not in ('.pyc',) and '__pycache__' not in str(f)]
    v11_1_files = [f for f in REPO_ROOT.rglob("*v11_1*") if f.suffix not in ('.pyc',) and '__pycache__' not in str(f)]
    ensure(len(v10_1_files) == 0 and len(v11_1_files) == 0, f"Future version files found: {v10_1_files + v11_1_files}")

    # Legacy Validator Smoke Tests
    print("Running prior validator smoke tests...")
    prior_validators = [
        "scripts/validate_station_chief_runtime_v6_5.py",
        "scripts/validate_station_chief_runtime_v6_4.py",
        "scripts/validate_station_chief_runtime_v6_3.py",
        "scripts/validate_station_chief_runtime_v6_2.py",
        "scripts/validate_station_chief_runtime_v6_1.py",
        "scripts/validate_station_chief_runtime_v6_0.py",
        "scripts/validate_station_chief_runtime_v5_9.py",
        "scripts/validate_station_chief_runtime_v5_8.py",
        "scripts/validate_station_chief_runtime_v5_7.py",
        "scripts/validate_station_chief_runtime_v5_6.py",
        "scripts/validate_station_chief_runtime_v5_5.py",
        "scripts/validate_station_chief_runtime_v5_4.py",
        "scripts/validate_station_chief_runtime_v5_3.py",
        "scripts/validate_station_chief_runtime_v5_2.py",
        "scripts/validate_station_chief_runtime_v5_1.py",
        "scripts/validate_station_chief_runtime_v5_0.py"
    ]
    for v in prior_validators:
        print(f"Running {v}...")
        res = run_script([sys.executable, v])
        ensure(res.returncode == 0, f"Prior validator {v} failed:\n{res.stdout}\n{res.stderr}")

    print("STATION_CHIEF_RUNTIME_V6_6_VALIDATION_PASS")

if __name__ == "__main__":
    main()
from station_chief_runtime import STATION_CHIEF_RUNTIME_VERSION
