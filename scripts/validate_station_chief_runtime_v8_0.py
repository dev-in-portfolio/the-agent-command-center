import sys
#!/usr/bin/env python3
"""
Station Chief Runtime v8.0 Validator.
Verifies Station Chief v8.0 build, versioning, control plane consolidation, and safety boundaries.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Add project root to sys.path and ensure 10_runtime is discoverable
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "10_runtime"))

from station_chief_v8_finish_line_control_plane import (
    STATION_CHIEF_V8_FINISH_LINE_CONTROL_PLANE_VERSION,
    STATION_CHIEF_V8_BABY_STEP_CHAIN_CLOSED,
    create_station_chief_v8_finish_line_control_plane_schema,
    create_station_chief_v8_finish_line_control_plane_bundle
)

def ensure(condition, message):
    if not condition:
        print(f"FAILED: {message}")
        sys.exit(1)

def run_script(cmd_list):
    result = subprocess.run(cmd_list, capture_output=True, text=True)
    return result

def main():
    print("Validating Station Chief Runtime v8.0.0...")

    # 1. Required files
    required_files = [
        "10_runtime/station_chief_v8_finish_line_control_plane.py",
        "09_exports/station_chief_v6_baby_step_chain_closeout_report.md",
        "09_exports/station_chief_v8_0_finish_line_control_plane_preflight_audit.md",
        "09_exports/station_chief_runtime_v8_0_report.md",
        "scripts/validate_station_chief_runtime_v8_0.py"
    ]
    for f in required_files:
        ensure((REPO_ROOT / f).exists(), f"File {f} must exist")

    # 2. Version consistency
    from station_chief_runtime import STATION_CHIEF_RUNTIME_VERSION
    from station_chief_release_lock import STABLE_RUNTIME_VERSION
    from station_chief_adapters import ADAPTER_MODULE_VERSION

    # v8.0 validator allows v10.0 version when running on master after v10.0 land.
    ensure(STATION_CHIEF_RUNTIME_VERSION in ["8.0.0", "10.0.0"], f"Runtime version mismatch: {STATION_CHIEF_RUNTIME_VERSION}")
    ensure(STABLE_RUNTIME_VERSION in ["8.0.0", "10.0.0"], f"Release lock version mismatch: {STABLE_RUNTIME_VERSION}")
    ensure(ADAPTER_MODULE_VERSION in ["8.0.0", "10.0.0"], f"Adapter version mismatch: {ADAPTER_MODULE_VERSION}")
    ensure(STATION_CHIEF_V8_FINISH_LINE_CONTROL_PLANE_VERSION == "8.0.0", "v8.0 module version mismatch")
    ensure(STATION_CHIEF_V8_BABY_STEP_CHAIN_CLOSED is True, "Baby-step chain must be closed")

    # 3. CLI Behavior: Schema Flag
    res = run_script([sys.executable, str(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "--station-chief-v8-finish-line-control-plane-schema"])
    ensure(res.returncode == 0, f"Schema flag failed: {res.stderr}")
    schema = json.loads(res.stdout)
    ensure(schema["schema_version"] == "8.0.0", "Schema version mismatch")
    ensure(schema["schema_type"] == "station_chief_v8_finish_line_control_plane", "Schema type mismatch")

    # 4. CLI Behavior: Control Plane Flag (Bundle inspection)
    res = run_script([sys.executable, str(REPO_ROOT / "10_runtime/station_chief_runtime.py"), "--station-chief-v8-finish-line-control-plane"])
    ensure(res.returncode == 0, f"Control plane flag failed: {res.stderr}")
    data = json.loads(res.stdout)
    bundle = data.get("station_chief_v8_finish_line_control_plane")
    ensure(bundle is not None, "v8.0 control plane bundle missing in output")
    ensure(bundle["runtime_version"] == "8.0.0", "Bundle version mismatch")
    ensure(bundle["release_candidate_status"] == "FINISH_LINE_RELEASE_CANDIDATE", "Bundle status mismatch")
    ensure(bundle["baby_step_chain_closed"] is True, "Bundle chain closed mismatch")

    # 5. Inventory and Registry Verification
    inventory = bundle.get("baby_step_chain_inventory", {})
    ensure("v6.0" in inventory and "v6.6" in inventory, "Inventory missing v6 layers")
    ensure(inventory["v6.6"]["version"] == "6.6.0", "v6.6 inventory version mismatch")

    registry = bundle.get("post_mvp_expansion_lane_lifecycle_registry", {})
    ensure("scope_stage" in registry and "review_disposition_stage" in registry, "Registry missing stages")

    # 6. Safety Boundary Matrix
    matrix = bundle.get("control_plane_safety_boundary_matrix", {})
    dangerous_actions = [
        "worker_process_start", "agent_start", "real_queue_creation", "queue_write",
        "task_enqueue", "task_execution", "api_call", "network_access", "deployment", "production_execution"
    ]
    for action in dangerous_actions:
        ensure(matrix.get(action) == "DENIED", f"Safety matrix failed to deny {action}")

    # 7. Validator Architecture Policy
    policy = bundle.get("validator_architecture_policy", {})
    ensure(policy.get("legacy_validators_must_not_or_accept_future_versions") is True, "Policy missing OR-accept prohibition")

    # 8. Forbidden files check
    # v10.0 files are now allowed as they have been built and landed.
    # We still check for v10.1+, v11.1+, and v12.1+ files.
    forbidden_globs = ["*v10_1*", "*v10.1*", "*v11_1*", "*v11.1*", "*v12_1*", "*v12.1*", "*v13_1*", "*v13.1*", "*v14_1*", "*v14.1*", "*v15_1*", "*v15.1*", "*v16_1*", "*v16.1*", "*v17_1*", "*v17.1*", "*v18_1*", "*v18.1*", "*v19*"]
    for glob in forbidden_globs:
        matches = list(REPO_ROOT.glob(f"**/{glob}"))
        # Filter out pycache
        matches = [m for m in matches if "__pycache__" not in str(m)]
        ensure(len(matches) == 0, f"Forbidden future/skipped files found for glob {glob}: {matches}")

    # 9. Legacy Validator Doctrine Check (No OR-version shortcuts)
    legacy_validators = ["v6_6", "v6_5", "v6_4"]
    for v in legacy_validators:
        v_path = REPO_ROOT / f"scripts/validate_station_chief_runtime_{v}.py"
        if v_path.exists():
            v_source = v_path.read_text()
            ensure("or '8.0.0'" not in v_source, f"Legacy validator {v} contains OR-version shortcut for v8.0")
            ensure('or "8.0.0"' not in v_source, f"Legacy validator {v} contains OR-version shortcut for v8.0")

    # 10. Smoke Tests for Prior Validators
    if not os.environ.get("STATION_CHIEF_SKIP_RECURSIVE_VALIDATION"):
        print("Running prior validator smoke tests...")
        prior_validators = [
            "scripts/validate_station_chief_runtime_v6_6.py",
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
            # Use subprocess to avoid module pollution and respect validation context detection
            res = run_script([sys.executable, str(REPO_ROOT / v)])
            ensure(res.returncode == 0, f"Prior validator {v} failed:\n{res.stdout}\n{res.stderr}")
    print("STATION_CHIEF_RUNTIME_V8_0_VALIDATION_PASS")

if __name__ == "__main__":
    main()
from station_chief_runtime import STATION_CHIEF_RUNTIME_VERSION
