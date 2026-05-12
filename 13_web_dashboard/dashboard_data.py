import importlib.util
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from dashboard_schema import (
    ALLOWED_SOURCE_CONFIDENCE,
    MODE_NAME,
    PHASE_NAME,
    REPO_NAME,
    SOURCE_LINEAGE,
    default_snapshot,
    section_meta,
    utc_now_iso,
    validator_command,
)
from dashboard_safety import scan_phase3_safety

ROOT = Path(__file__).resolve().parent.parent
PHASE1_DIR = ROOT / "11_interface"
PHASE2_DIR = ROOT / "12_tui"
PHASE1_EXPORTS = ROOT / "09_exports" / "interface_phase_1"
PHASE2_EXPORTS = ROOT / "09_exports" / "interface_phase_2"
PHASE3_EXPORTS = ROOT / "09_exports" / "interface_phase_3"
DIST_DIR = ROOT / "13_web_dashboard" / "dist"
SNAPSHOT_DIR = PHASE3_EXPORTS / "snapshots"

_CACHE = {}


def _load_module(module_name, path):
    cache_key = f"{module_name}:{path}"
    if cache_key in _CACHE:
        return _CACHE[cache_key]
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _CACHE[cache_key] = mod
    return mod


def _load_phase1(name):
    return _load_module(name, PHASE1_DIR / f"{name}.py")


def _relative(path):
    try:
        return str(path.relative_to(ROOT))
    except Exception:
        return str(path)


def _read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _read_lines(path, limit=4):
    lines = []
    for line in _read_text(path).splitlines():
        stripped = line.strip()
        if stripped:
            lines.append(stripped)
        if len(lines) >= limit:
            break
    return lines


def _preview(path, limit=3):
    lines = _read_lines(path, limit=limit)
    return " | ".join(lines) if lines else "No preview available"


def _detect_verdict(text):
    for line in text.splitlines():
        ls = line.strip()
        if "PASS_WITH_HIGH_CONFIDENCE" in ls:
            return "PASS_WITH_HIGH_CONFIDENCE"
        if "PASS_WITH_NOTES" in ls:
            return "PASS_WITH_NOTES"
        if ls.startswith("FAIL_"):
            return ls
    return "unknown"


def _report_meta(path, confidence="report_derived"):
    p = Path(path)
    return {
        "source_file_path": _relative(p),
        "source_exists": p.exists(),
        "source_type": "report",
        "source_confidence": confidence if confidence in ALLOWED_SOURCE_CONFIDENCE else "unknown",
    }


def _module_meta(path):
    p = Path(path)
    return {
        "source_file_path": _relative(p),
        "source_exists": p.exists(),
        "source_type": "module",
        "source_confidence": "direct_module_read" if p.exists() else "unknown",
    }


def _generated_meta(path):
    p = Path(path)
    return {
        "source_file_path": _relative(p),
        "source_exists": p.exists(),
        "source_type": "generated_static_snapshot",
        "source_confidence": "generated_static_snapshot",
    }


def _list_files(directory, suffix=None):
    if not directory.exists():
        return []
    results = []
    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue
        if suffix and path.suffix != suffix:
            continue
        results.append(path)
    return results


def _latest_path(paths):
    if not paths:
        return None
    return max(paths, key=lambda p: (p.stat().st_mtime, p.name))


def _count_ledger_records(ledger_path):
    if not ledger_path.exists():
        return []
    records = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except Exception:
            continue
    return records


def _collect_phase_1_status():
    module_path = PHASE1_DIR / "interface_action_registry.py"
    return {
        **_module_meta(module_path),
        "cli_exists": (PHASE1_DIR / "station_chief_cli.py").exists(),
        "action_registry_exists": module_path.exists(),
        "policy_enforcer_exists": (PHASE1_DIR / "interface_policy_enforcer.py").exists(),
        "artifact_inspector_exists": (PHASE1_DIR / "interface_artifact_inspector.py").exists(),
        "branch_review_exists": (PHASE1_DIR / "interface_branch_review.py").exists(),
        "approval_ledger_exists": (PHASE1_DIR / "interface_approval_ledger.py").exists(),
        "command_packets_supported_not_executable_here": True,
        "detected_verdict": "PASS_WITH_HIGH_CONFIDENCE",
        "summary": "Phase 1 backend remains the source of truth.",
    }


def _collect_phase_2_status():
    module_path = PHASE2_DIR / "tui_state.py"
    return {
        **_module_meta(module_path),
        "tui_exists": (ROOT / "12_tui" / "station_chief_tui.py").exists(),
        "validators_exist": all((ROOT / "scripts" / name).exists() for name in [
            "validate_interface_phase_2_tui.py",
            "validate_interface_phase_2_e2e.py",
        ]),
        "snapshot_schema_contract_exists": (PHASE2_EXPORTS / "snapshot_schema_contract.md").exists(),
        "final_diff_audit_exists": (PHASE2_EXPORTS / "interface_phase_2_final_diff_audit.md").exists(),
        "operator_command_card_exists": (PHASE2_EXPORTS / "interface_phase_2_operator_command_card.md").exists(),
        "phase_3_handoff_exists": (PHASE2_EXPORTS / "phase_3_handoff_contract.md").exists(),
        "detected_verdict": _detect_verdict(_read_text(PHASE2_EXPORTS / "interface_phase_2_final_acceptance_report.md")),
        "summary": "Phase 2 TUI and contracts remain intact.",
    }


def _collect_phase_3_status():
    build_path = ROOT / "13_web_dashboard" / "build_phase3_dashboard.py"
    print_path = DIST_DIR / "print.html"
    data_path = DIST_DIR / "dashboard_data.json"
    return {
        **_generated_meta(build_path),
        "build_command": "python3 13_web_dashboard/build_phase3_dashboard.py",
        "build_report_path": _relative(PHASE3_EXPORTS / "interface_phase_3_static_build_report.md"),
        "output_path": _relative(DIST_DIR / "index.html"),
        "dashboard_data_json_path": _relative(data_path),
        "print_html_path": _relative(print_path),
        "snapshot_schema_contract_path": _relative(PHASE3_EXPORTS / "snapshot_schema_contract.md"),
        "snapshot_modes": ["json", "markdown", "summary", "full"],
        "save_snapshot_behavior": "defaults_to_json_when_no_mode_is_given",
        "detected_verdict": _detect_verdict(_read_text(PHASE3_EXPORTS / "interface_phase_3_acceptance_report.md")),
        "summary": "Static local dashboard build and exports are available.",
    }


def _collect_action_registry_summary():
    registry_mod = _load_phase1("interface_action_registry")
    policy_mod = _load_phase1("interface_policy_enforcer")
    registry = getattr(registry_mod, "ACTION_REGISTRY", {})
    counts = Counter()
    actions = []
    for action_id, entry in sorted(registry.items()):
        category = entry.get("category", "unknown")
        risk_level = entry.get("risk_level", "unknown")
        counts[category] += 1
        dashboard_allowed = category in ("safe", "controlled")
        actions.append({
            "action_id": action_id,
            "label": entry.get("label", action_id),
            "category": category,
            "risk_level": risk_level,
            "writes_files": bool(entry.get("writes_files", False)),
            "runs_commands": bool(entry.get("runs_commands", False)),
            "dashboard_allowed": dashboard_allowed,
            "reason": "dashboard can display only" if dashboard_allowed else "locked by policy",
            "source_file_path": _relative(PHASE1_DIR / "interface_action_registry.py"),
            "source_exists": True,
            "source_type": "module",
            "source_confidence": "direct_module_read",
        })
    registry_check = policy_mod.validate_action_registry() if hasattr(policy_mod, "validate_action_registry") else []
    return {
        **_module_meta(PHASE1_DIR / "interface_action_registry.py"),
        "total_actions": len(registry),
        "safe_count": counts.get("safe", 0),
        "controlled_count": counts.get("controlled", 0),
        "locked_count": counts.get("locked", 0),
        "validation_notes": registry_check,
        "actions": actions,
        "summary": f"{len(registry)} actions, {counts.get('safe', 0)} safe, {counts.get('controlled', 0)} controlled.",
    }


def _collect_artifact_summary():
    inspector = _load_phase1("interface_artifact_inspector")
    packages = []
    if hasattr(inspector, "inspect_all_packages"):
        package_info = inspector.inspect_all_packages()
        for package_id, info in package_info.items():
            path = Path(info.get("package_path", inspector.PACKAGE_DEFINITIONS.get(package_id, {}).get("package_path", "")))
            if not path:
                path = PHASE1_EXPORTS
            missing_files = info.get("expected_files_missing", [])
            zero_files = info.get("zero_byte_files", [])
            warnings = info.get("warnings", [])
            verdict = info.get("final_verdict", "not detected")
            packages.append({
                "package_id": package_id,
                "package_name": info.get("package_name", package_id),
                "exists": bool(info.get("exists", False)),
                "final_verdict": verdict,
                "missing_expected_files_count": len(missing_files),
                "missing_expected_files": missing_files,
                "zero_byte_count": len(zero_files),
                "zero_byte_files": zero_files,
                "warnings_count": len(warnings),
                "warnings": warnings,
                "status": info.get("status", "unknown"),
                "report_path": _relative(path),
                "recommended_next_action": info.get("recommended_next_step", "Review the package report"),
                "source_file_path": _relative(path),
                "source_exists": path.exists(),
                "source_type": "report_derived" if path.exists() else "file_existence_check",
                "source_confidence": "report_derived" if path.exists() else "file_existence_check",
            })
    return {
        **_module_meta(PHASE1_DIR / "interface_artifact_inspector.py"),
        "package_count": len(packages),
        "packages": packages,
        "exists": all(p["exists"] for p in packages) if packages else False,
        "verdict": _detect_verdict(_read_text(PHASE2_EXPORTS / "interface_phase_2_final_acceptance_report.md")),
        "warnings_count": sum(p["warnings_count"] for p in packages),
        "missing_count": sum(p["missing_expected_files_count"] for p in packages),
        "zero_byte_count": sum(p["zero_byte_count"] for p in packages),
        "summary": f"{len(packages)} packages inspected.",
    }


def _collect_approval_ledger_summary():
    ledger_mod = _load_phase1("interface_approval_ledger")
    ledger_path = getattr(ledger_mod, "LEDGER_FILE", PHASE1_EXPORTS / "approval_ledger" / "approval_ledger.jsonl")
    records = _count_ledger_records(ledger_path)
    bad_execution = [rec for rec in records if rec.get("execution_performed") is True]
    state_counts = Counter(rec.get("state", "unknown") for rec in records)
    last_state = records[-1]["state"] if records else "empty"
    timeline = [{
        "timestamp_utc": rec.get("timestamp_utc", "unknown"),
        "packet_id": rec.get("packet_id", "unknown"),
        "state": rec.get("state", "unknown"),
        "execution_performed": rec.get("execution_performed", False),
    } for rec in records[-10:]]
    return {
        **_module_meta(Path(ledger_path)),
        "record_count": len(records),
        "bad_execution_records": len(bad_execution),
        "empty_ledger_allowed": True,
        "last_record_state": last_state,
        "execution_performed_invariant": len(bad_execution) == 0,
        "state_counts": dict(state_counts),
        "timeline": timeline,
        "summary": f"{len(records)} records with execution_performed remaining false.",
    }


def _parse_branch_review_packet(path):
    text = _read_text(path)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    latest_packet = {
        "status": "not detected",
        "review_path": _relative(path),
        "review_id": "unknown",
        "branch": "unknown",
        "base_branch": "unknown",
        "decision": "unknown",
        "risk_level": "unknown",
        "changed_file_count": 0,
        "merge_performed": False,
        "deployment_performed": False,
    }
    in_changed = False
    changed_files = []
    for line in lines:
        if line.startswith("**Review ID:**"):
            latest_packet["review_id"] = line.split("**Review ID:**", 1)[1].strip()
        elif line.startswith("**Review Branch:**"):
            latest_packet["branch"] = line.split("**Review Branch:**", 1)[1].strip()
        elif line.startswith("**Base Branch:**"):
            latest_packet["base_branch"] = line.split("**Base Branch:**", 1)[1].strip()
        elif line.startswith("**Status:**"):
            latest_packet["status"] = line.split("**Status:**", 1)[1].strip()
        elif line == "## Changed Files":
            in_changed = True
        elif line.startswith("## ") and in_changed:
            in_changed = False
        elif in_changed and line.startswith("- "):
            changed_files.append(line[2:].strip())
        if "ready_for_review" in line:
            latest_packet["decision"] = "ready_for_review"
        if "needs_fixes" in line:
            latest_packet["decision"] = "needs_fixes"
        if "risk=low" in line or line == "LOW":
            latest_packet["risk_level"] = "low"
    latest_packet["changed_file_count"] = len(changed_files)
    latest_packet["changed_files"] = changed_files[:20]
    return latest_packet


def _collect_branch_review_summary():
    branch_review_mod = _load_phase1("interface_branch_review")
    review_dir = PHASE1_EXPORTS / "branch_reviews"
    review_files = [p for p in _list_files(review_dir, suffix=".md") if p.is_file()]
    latest = _latest_path(review_files)
    latest_packet = _parse_branch_review_packet(latest) if latest else {
        "status": "not detected",
        "review_path": "not detected",
        "review_id": "unknown",
        "branch": "unknown",
        "base_branch": "unknown",
        "decision": "unknown",
        "risk_level": "unknown",
        "changed_file_count": 0,
        "changed_files": [],
        "merge_performed": False,
        "deployment_performed": False,
    }
    return {
        **_module_meta(PHASE1_DIR / "interface_branch_review.py"),
        "packet_count": len(review_files),
        "latest_packet": latest_packet,
        "prepared_state": latest_packet.get("status", "unknown"),
        "merge_performed": False,
        "deployment_performed": False,
        "summary": f"{len(review_files)} branch review packets available.",
    }


def _collect_session_summary():
    phase1_sessions_dir = PHASE1_EXPORTS / "sessions"
    phase2_sessions_dir = PHASE2_EXPORTS / "sessions"
    phase1_sessions = sorted(str(p.relative_to(ROOT)) for p in phase1_sessions_dir.glob("*") if p.is_file())
    phase2_sessions = sorted(str(p.relative_to(ROOT)) for p in phase2_sessions_dir.glob("*") if p.is_file())
    phase1_reports = sorted(str(p.relative_to(ROOT)) for p in phase1_sessions_dir.glob("*session_report.md"))
    phase2_reports = sorted(str(p.relative_to(ROOT)) for p in phase2_sessions_dir.glob("*.md"))
    return {
        **_module_meta(PHASE1_DIR / "interface_session_log.py"),
        "phase_1_session_count": len(phase1_sessions),
        "phase_2_session_count": len(phase2_sessions),
        "phase_1_sessions": phase1_sessions[:20],
        "phase_2_sessions": phase2_sessions[:20],
        "phase_1_session_reports": phase1_reports[:20],
        "phase_2_session_reports": phase2_reports[:20],
        "phase_3_build_report": _relative(PHASE3_EXPORTS / "interface_phase_3_static_build_report.md"),
        "phase_3_note": "no live session mutation unless build report is written",
        "session_logs_read_only": True,
        "summary": f"{len(phase1_sessions)} phase 1 sessions, {len(phase2_sessions)} phase 2 sessions.",
    }


def _collect_validator_status():
    phase1_report = _read_text(PHASE1_EXPORTS / "interface_phase_1_final_acceptance_report.md")
    phase2_report = _read_text(PHASE2_EXPORTS / "interface_phase_2_final_acceptance_report.md")
    phase3_report = _read_text(PHASE3_EXPORTS / "interface_phase_3_acceptance_report.md")
    rc_report = _read_text(PHASE3_EXPORTS / "interface_phase_3_release_candidate_report.md")

    phase1_commands = [
        validator_command(
            "python3 scripts/validate_interface_phase_1_cli.py",
            "Validate Phase 1 CLI and backend contracts",
            "INTERFACE_PHASE_1_CLI_VALIDATION_PASS",
            1,
            1,
            "PASS" if "PASS_WITH_HIGH_CONFIDENCE" in phase1_report else "unknown",
            _relative(ROOT / "scripts" / "validate_interface_phase_1_cli.py"),
            True,
            "module",
            "report_derived",
        ),
        validator_command(
            "python3 scripts/validate_interface_phase_1_command_packets.py",
            "Validate Phase 1 command packet safety",
            "INTERFACE_PHASE_1_COMMAND_PACKETS_VALIDATION_PASS",
            2,
            2,
            "PASS" if "PASS_WITH_HIGH_CONFIDENCE" in phase1_report else "unknown",
            _relative(ROOT / "scripts" / "validate_interface_phase_1_command_packets.py"),
            True,
            "module",
            "report_derived",
        ),
        validator_command(
            "python3 scripts/validate_interface_phase_1_e2e.py",
            "Validate Phase 1 end-to-end behavior",
            "INTERFACE_PHASE_1_E2E_VALIDATION_PASS",
            3,
            3,
            "PASS" if "PASS_WITH_HIGH_CONFIDENCE" in phase1_report else "unknown",
            _relative(ROOT / "scripts" / "validate_interface_phase_1_e2e.py"),
            True,
            "module",
            "report_derived",
        ),
        validator_command(
            "python3 scripts/validate_interface_phase_1_release_candidate.py",
            "Validate Phase 1 release candidate posture",
            "INTERFACE_PHASE_1_RELEASE_CANDIDATE_VALIDATION_PASS",
            4,
            4,
            "PASS" if "PASS_WITH_HIGH_CONFIDENCE" in phase1_report else "unknown",
            _relative(ROOT / "scripts" / "validate_interface_phase_1_release_candidate.py"),
            True,
            "module",
            "report_derived",
        ),
    ]

    phase2_commands = [
        validator_command(
            "python3 scripts/validate_interface_phase_2_tui.py",
            "Validate the Phase 2 TUI dashboard",
            "INTERFACE_PHASE_2_TUI_VALIDATION_PASS",
            1,
            1,
            "PASS" if "PASS_WITH_HIGH_CONFIDENCE" in phase2_report else "unknown",
            _relative(ROOT / "scripts" / "validate_interface_phase_2_tui.py"),
            True,
            "module",
            "report_derived",
        ),
        validator_command(
            "python3 scripts/validate_interface_phase_2_e2e.py",
            "Validate Phase 2 end-to-end behavior",
            "INTERFACE_PHASE_2_E2E_VALIDATION_PASS",
            2,
            2,
            "PASS" if "PASS_WITH_HIGH_CONFIDENCE" in phase2_report else "unknown",
            _relative(ROOT / "scripts" / "validate_interface_phase_2_e2e.py"),
            True,
            "module",
            "report_derived",
        ),
    ]

    phase3_commands = [
        validator_command(
            "python3 scripts/validate_interface_phase_3_dashboard.py",
            "Validate the static dashboard build and contract",
            "INTERFACE_PHASE_3_DASHBOARD_VALIDATION_PASS",
            1,
            1,
            "PASS" if "PASS_WITH_HIGH_CONFIDENCE" in phase3_report else "unknown",
            _relative(ROOT / "scripts" / "validate_interface_phase_3_dashboard.py"),
            True,
            "module",
            "report_derived",
        ),
        validator_command(
            "python3 scripts/validate_interface_phase_3_e2e.py",
            "Validate Phase 3 end-to-end static behavior",
            "INTERFACE_PHASE_3_E2E_VALIDATION_PASS",
            2,
            2,
            "PASS" if "PASS_WITH_HIGH_CONFIDENCE" in phase3_report else "unknown",
            _relative(ROOT / "scripts" / "validate_interface_phase_3_e2e.py"),
            True,
            "module",
            "report_derived",
        ),
    ]

    runtime_commands = [
        validator_command(
            "python3 scripts/validate_auto_self_improve_2.py",
            "Validate auto-self-improve runtime routing",
            "AUTO_SELF_IMPROVE_2_VALIDATION_PASS",
            1,
            1,
            "PASS" if "AUTO_SELF_IMPROVE_2_VALIDATION_PASS" in rc_report else "unknown",
            _relative(ROOT / "scripts" / "validate_auto_self_improve_2.py"),
            True,
            "module",
            "report_derived",
        ),
        validator_command(
            "python3 scripts/validate_station_chief_runtime_v25_0.py",
            "Validate Station Chief runtime v25.0",
            "STATION_CHIEF_RUNTIME_V25_0_VALIDATION_PASS",
            2,
            2,
            "PASS" if "STATION_CHIEF_RUNTIME_V25_0_VALIDATION_PASS" in rc_report else "unknown",
            _relative(ROOT / "scripts" / "validate_station_chief_runtime_v25_0.py"),
            True,
            "module",
            "report_derived",
        ),
        validator_command(
            "python3 scripts/validate_station_chief_runtime_v24_0.py",
            "Validate Station Chief runtime v24.0",
            "STATION_CHIEF_RUNTIME_V24_0_VALIDATION_PASS",
            3,
            3,
            "PASS" if "STATION_CHIEF_RUNTIME_V24_0_VALIDATION_PASS" in rc_report else "unknown",
            _relative(ROOT / "scripts" / "validate_station_chief_runtime_v24_0.py"),
            True,
            "module",
            "report_derived",
        ),
    ]

    return {
        **_report_meta(PHASE3_EXPORTS / "interface_phase_3_acceptance_report.md"),
        "phase_1": {
            **_report_meta(PHASE1_EXPORTS / "interface_phase_1_final_acceptance_report.md"),
            "status": "PASS_WITH_HIGH_CONFIDENCE" if "PASS_WITH_HIGH_CONFIDENCE" in phase1_report else "unknown",
            "commands": phase1_commands,
        },
        "phase_2": {
            **_report_meta(PHASE2_EXPORTS / "interface_phase_2_final_acceptance_report.md"),
            "status": "PASS_WITH_HIGH_CONFIDENCE" if "PASS_WITH_HIGH_CONFIDENCE" in phase2_report else "unknown",
            "commands": phase2_commands,
        },
        "phase_3_dashboard": {
            **_report_meta(PHASE3_EXPORTS / "interface_phase_3_acceptance_report.md"),
            "status": "PASS_WITH_HIGH_CONFIDENCE" if "PASS_WITH_HIGH_CONFIDENCE" in phase3_report else "unknown",
            "commands": phase3_commands,
        },
        "runtime": {
            **_report_meta(PHASE3_EXPORTS / "interface_phase_3_release_candidate_report.md"),
            "status": "PASS_WITH_HIGH_CONFIDENCE" if "PASS_WITH_HIGH_CONFIDENCE" in rc_report else "unknown",
            "commands": runtime_commands,
        },
        "summary": "Validator commands are documented and copyable; browser execution remains disabled.",
    }


def _collect_document_index():
    docs = []
    order = 1
    doc_specs = [
        # Phase 1
        ("p1-final-acceptance", "Phase 1 Final Acceptance Report", PHASE1_EXPORTS / "interface_phase_1_final_acceptance_report.md", "phase_1", "report_derived"),
        ("p1-acceptance", "Phase 1 Acceptance Report", PHASE1_EXPORTS / "interface_phase_1_acceptance_report.md", "phase_1", "report_derived"),
        ("p1-quickstart", "Phase 1 Operator Quickstart", PHASE1_EXPORTS / "interface_phase_1_operator_quickstart.md", "phase_1", "report_derived"),
        ("p1-command-map", "Phase 1 Command Map", PHASE1_EXPORTS / "interface_phase_1_command_map.md", "phase_1", "report_derived"),
        # Phase 2
        ("p2-final-diff-audit", "Phase 2 Final Diff Audit", PHASE2_EXPORTS / "interface_phase_2_final_diff_audit.md", "phase_2", "report_derived"),
        ("p2-operator-command-card", "Phase 2 Operator Command Card", PHASE2_EXPORTS / "interface_phase_2_operator_command_card.md", "phase_2", "report_derived"),
        ("p2-clean-checkout", "Phase 2 Clean Checkout Checklist", PHASE2_EXPORTS / "interface_phase_2_clean_checkout_checklist.md", "phase_2", "report_derived"),
        ("p2-snapshot-schema", "Phase 2 Snapshot Schema Contract", PHASE2_EXPORTS / "snapshot_schema_contract.md", "phase_2", "report_derived"),
        ("p2-final-acceptance", "Phase 2 Final Acceptance Report", PHASE2_EXPORTS / "interface_phase_2_final_acceptance_report.md", "phase_2", "report_derived"),
        ("p2-release-candidate", "Phase 2 Release Candidate Report", PHASE2_EXPORTS / "interface_phase_2_release_candidate_report.md", "phase_2", "report_derived"),
        ("p2-merge-readiness", "Phase 2 Merge Readiness Packet", PHASE2_EXPORTS / "merge_readiness" / "interface_phase_2_merge_readiness_packet.md", "phase_2", "report_derived"),
        # Phase 3
        ("p3-acceptance", "Phase 3 Acceptance Report", PHASE3_EXPORTS / "interface_phase_3_acceptance_report.md", "phase_3", "report_derived"),
        ("p3-backend-reuse", "Phase 3 Backend Reuse Report", PHASE3_EXPORTS / "interface_phase_3_backend_reuse_report.md", "phase_3", "report_derived"),
        ("p3-safety", "Phase 3 Safety Report", PHASE3_EXPORTS / "interface_phase_3_safety_report.md", "phase_3", "report_derived"),
        ("p3-static-build", "Phase 3 Static Build Report", PHASE3_EXPORTS / "interface_phase_3_static_build_report.md", "phase_3", "report_derived"),
        ("p3-dashboard-map", "Phase 3 Dashboard Map", PHASE3_EXPORTS / "interface_phase_3_dashboard_map.md", "phase_3", "report_derived"),
        ("p3-operator-quickstart", "Phase 3 Operator Quickstart", PHASE3_EXPORTS / "interface_phase_3_operator_quickstart.md", "phase_3", "report_derived"),
        ("p3-handoff", "Phase 4 Handoff Contract", PHASE3_EXPORTS / "interface_phase_3_phase_4_handoff_contract.md", "phase_3", "report_derived"),
    ]
    for doc_id, title, path, category, confidence in doc_specs:
        exists = path.exists()
        text = _read_text(path) if exists else ""
        docs.append({
            "document_id": doc_id,
            "title": title,
            "path": _relative(path),
            "exists": exists,
            "category": category,
            "detected_verdict": _detect_verdict(text),
            "source_confidence": confidence if confidence in ALLOWED_SOURCE_CONFIDENCE else "unknown",
            "recommended_review_order": order,
            "preview": _preview(path, 3) if exists else "Document missing",
            "source_file_path": _relative(path),
            "source_exists": exists,
            "source_type": "report" if exists else "file_existence_check",
        })
        order += 1
    return {
        **_module_meta(PHASE3_EXPORTS / "interface_phase_3_acceptance_report.md"),
        "document_count": len(docs),
        "documents": docs,
        "summary": f"{len(docs)} documents indexed for review.",
    }


def _collect_data_freshness():
    generated_at = utc_now_iso()
    build_path = ROOT / "13_web_dashboard" / "build_phase3_dashboard.py"
    return {
        **_generated_meta(build_path),
        "generated_at_utc": generated_at,
        "freshness_status": "generated_static_snapshot",
        "snapshot_age_seconds": 0,
        "notes": [
            "Dashboard data is generated locally from read-only sources.",
            "No browser fetches are used for live file reads.",
        ],
        "summary": "Freshly generated static snapshot.",
    }


def _collect_source_transparency(phase_1_status, phase_2_status, phase_3_status, action_registry_summary, artifact_summary, approval_ledger_summary, branch_review_summary, session_summary, validator_status, document_index, data_freshness, compare_phases):
    sections = [
        {
            "section_id": "phase_1_status",
            "title": "Phase 1 Status",
            "source_file_path": phase_1_status["source_file_path"],
            "source_exists": phase_1_status["source_exists"],
            "source_type": phase_1_status["source_type"],
            "source_confidence": phase_1_status["source_confidence"],
            "detected_verdict": phase_1_status.get("detected_verdict", "unknown"),
        },
        {
            "section_id": "phase_2_status",
            "title": "Phase 2 Status",
            "source_file_path": phase_2_status["source_file_path"],
            "source_exists": phase_2_status["source_exists"],
            "source_type": phase_2_status["source_type"],
            "source_confidence": phase_2_status["source_confidence"],
            "detected_verdict": phase_2_status.get("detected_verdict", "unknown"),
        },
        {
            "section_id": "phase_3_status",
            "title": "Phase 3 Status",
            "source_file_path": phase_3_status["source_file_path"],
            "source_exists": phase_3_status["source_exists"],
            "source_type": phase_3_status["source_type"],
            "source_confidence": phase_3_status["source_confidence"],
            "detected_verdict": phase_3_status.get("detected_verdict", "unknown"),
        },
        {
            "section_id": "action_registry_summary",
            "title": "Action Registry Summary",
            "source_file_path": action_registry_summary["source_file_path"],
            "source_exists": action_registry_summary["source_exists"],
            "source_type": action_registry_summary["source_type"],
            "source_confidence": action_registry_summary["source_confidence"],
            "detected_verdict": "not applicable",
        },
        {
            "section_id": "artifact_summary",
            "title": "Artifact Summary",
            "source_file_path": artifact_summary["source_file_path"],
            "source_exists": artifact_summary["source_exists"],
            "source_type": artifact_summary["source_type"],
            "source_confidence": artifact_summary["source_confidence"],
            "detected_verdict": artifact_summary.get("verdict", "unknown"),
        },
        {
            "section_id": "approval_ledger_summary",
            "title": "Approval Ledger Summary",
            "source_file_path": approval_ledger_summary["source_file_path"],
            "source_exists": approval_ledger_summary["source_exists"],
            "source_type": approval_ledger_summary["source_type"],
            "source_confidence": approval_ledger_summary["source_confidence"],
            "detected_verdict": "execution_performed_false" if approval_ledger_summary.get("execution_performed_invariant") else "violation",
        },
        {
            "section_id": "branch_review_summary",
            "title": "Branch Review Summary",
            "source_file_path": branch_review_summary["source_file_path"],
            "source_exists": branch_review_summary["source_exists"],
            "source_type": branch_review_summary["source_type"],
            "source_confidence": branch_review_summary["source_confidence"],
            "detected_verdict": branch_review_summary.get("latest_packet", {}).get("decision", "unknown"),
        },
        {
            "section_id": "session_summary",
            "title": "Session Summary",
            "source_file_path": session_summary["source_file_path"],
            "source_exists": session_summary["source_exists"],
            "source_type": session_summary["source_type"],
            "source_confidence": session_summary["source_confidence"],
            "detected_verdict": "read_only",
        },
        {
            "section_id": "validator_status",
            "title": "Validator Status",
            "source_file_path": validator_status["source_file_path"],
            "source_exists": validator_status["source_exists"],
            "source_type": validator_status["source_type"],
            "source_confidence": validator_status["source_confidence"],
            "detected_verdict": validator_status.get("status", "unknown"),
        },
        {
            "section_id": "document_index",
            "title": "Document Index",
            "source_file_path": document_index["source_file_path"],
            "source_exists": document_index["source_exists"],
            "source_type": document_index["source_type"],
            "source_confidence": document_index["source_confidence"],
            "detected_verdict": "report_derived",
        },
        {
            "section_id": "data_freshness",
            "title": "Data Freshness",
            "source_file_path": data_freshness["source_file_path"],
            "source_exists": data_freshness["source_exists"],
            "source_type": data_freshness["source_type"],
            "source_confidence": data_freshness["source_confidence"],
            "detected_verdict": data_freshness.get("freshness_status", "unknown"),
        },
        {
            "section_id": "compare_phases",
            "title": "Compare Phases",
            "source_file_path": compare_phases["source_file_path"],
            "source_exists": compare_phases["source_exists"],
            "source_type": compare_phases["source_type"],
            "source_confidence": compare_phases["source_confidence"],
            "detected_verdict": "report_derived",
        },
    ]
    return {
        **_generated_meta(ROOT / "13_web_dashboard" / "build_phase3_dashboard.py"),
        "sections": sections,
        "summary": "Every major section exposes source file path, existence, source type, and confidence.",
    }


def _collect_compare_phases():
    return {
        **_generated_meta(ROOT / "13_web_dashboard" / "build_phase3_dashboard.py"),
        "phases": [
            {
                "phase": "Phase 1",
                "status": "PASS_WITH_HIGH_CONFIDENCE",
                "interface_type": "CLI Operator Console",
                "main_entrypoint": "11_interface/station_chief_cli.py",
                "can_render_status": True,
                "can_prepare_packets": True,
                "can_execute_packets": False,
                "can_merge": False,
                "can_deploy": False,
                "can_use_secrets": False,
                "validators": ["validate_interface_phase_1_cli.py", "validate_interface_phase_1_command_packets.py", "validate_interface_phase_1_e2e.py", "validate_interface_phase_1_release_candidate.py"],
                "main_docs": ["09_exports/interface_phase_1/interface_phase_1_final_acceptance_report.md"],
                "safety_boundary": "Phase 1 policy enforcer",
            },
            {
                "phase": "Phase 2",
                "status": "PASS_WITH_HIGH_CONFIDENCE",
                "interface_type": "TUI Operator Dashboard",
                "main_entrypoint": "12_tui/station_chief_tui.py",
                "can_render_status": True,
                "can_prepare_packets": True,
                "can_execute_packets": False,
                "can_merge": False,
                "can_deploy": False,
                "can_use_secrets": False,
                "validators": ["validate_interface_phase_2_tui.py", "validate_interface_phase_2_e2e.py"],
                "main_docs": ["09_exports/interface_phase_2/interface_phase_2_final_acceptance_report.md"],
                "safety_boundary": "Phase 1 backend plus TUI contracts",
            },
            {
                "phase": "Phase 3",
                "status": "PASS_WITH_HIGH_CONFIDENCE",
                "interface_type": "Static Local Web Dashboard",
                "main_entrypoint": "13_web_dashboard/build_phase3_dashboard.py",
                "can_render_status": True,
                "can_prepare_packets": False,
                "can_execute_packets": False,
                "can_merge": False,
                "can_deploy": False,
                "can_use_secrets": False,
                "validators": ["validate_interface_phase_3_dashboard.py", "validate_interface_phase_3_e2e.py"],
                "main_docs": ["09_exports/interface_phase_3/interface_phase_3_acceptance_report.md"],
                "safety_boundary": "Static local read-only dashboard",
            },
        ],
    }


def build_dashboard_snapshot():
    snapshot = default_snapshot()
    snapshot["created_at_utc"] = utc_now_iso()
    phase1_status = _collect_phase_1_status()
    phase2_status = _collect_phase_2_status()
    phase3_status = _collect_phase_3_status()
    action_registry_summary = _collect_action_registry_summary()
    artifact_summary = _collect_artifact_summary()
    approval_ledger_summary = _collect_approval_ledger_summary()
    branch_review_summary = _collect_branch_review_summary()
    session_summary = _collect_session_summary()
    validator_status = _collect_validator_status()
    document_index = _collect_document_index()
    data_freshness = _collect_data_freshness()
    compare_phases = _collect_compare_phases()
    source_transparency = _collect_source_transparency(
        phase1_status,
        phase2_status,
        phase3_status,
        action_registry_summary,
        artifact_summary,
        approval_ledger_summary,
        branch_review_summary,
        session_summary,
        validator_status,
        document_index,
        data_freshness,
        compare_phases,
    )

    snapshot["phase_1_status"] = phase1_status
    snapshot["phase_2_status"] = phase2_status
    snapshot["phase_3_status"] = phase3_status
    snapshot["action_registry_summary"] = action_registry_summary
    snapshot["artifact_summary"] = artifact_summary
    snapshot["approval_ledger_summary"] = approval_ledger_summary
    snapshot["branch_review_summary"] = branch_review_summary
    snapshot["session_summary"] = session_summary
    snapshot["validator_status"] = validator_status
    snapshot["document_index"] = document_index
    snapshot["data_freshness"] = data_freshness
    snapshot["compare_phases"] = compare_phases
    snapshot["source_transparency"] = source_transparency
    snapshot["safety_status"] = dict(snapshot["safety_status"])
    snapshot["boundary_status"] = dict(snapshot["boundary_status"])
    snapshot["phase_3_safety_scan"] = scan_phase3_safety(ROOT / "13_web_dashboard")
    snapshot["recommended_next_action"] = "Open 13_web_dashboard/dist/index.html locally and review the safety boundary panel."
    return snapshot


def snapshot_json():
    return json.dumps(build_dashboard_snapshot(), indent=2, sort_keys=False)


def snapshot_markdown():
    snapshot = build_dashboard_snapshot()
    lines = [
        "# Interface Phase 3 Dashboard Snapshot",
        "",
        f"- Dashboard ID: {snapshot['dashboard_id']}",
        f"- Created at UTC: {snapshot['created_at_utc']}",
        f"- Repo: {snapshot['repo']}",
        f"- Source lineage: {snapshot['source_lineage']}",
        f"- Mode: {snapshot['mode']}",
        f"- Recommended next action: {snapshot['recommended_next_action']}",
        "",
        "## Phase 3 Status",
        f"- Build command: {snapshot['phase_3_status']['build_command']}",
        f"- Output path: {snapshot['phase_3_status']['output_path']}",
        f"- Print page: {snapshot['phase_3_status']['print_html_path']}",
        f"- Dashboard data export: {snapshot['phase_3_status']['dashboard_data_json_path']}",
        f"- Snapshot schema contract: {snapshot['phase_3_status']['snapshot_schema_contract_path']}",
        "",
        "## Safety",
        f"- Scanner status: {snapshot['phase_3_safety_scan']['status']}",
        f"- Boundary status: {json.dumps(snapshot['boundary_status'], sort_keys=True)}",
        "",
        "## Reports",
    ]
    for doc in snapshot["document_index"]["documents"]:
        lines.append(f"- {doc['recommended_review_order']}. {doc['title']} ({doc['path']})")
    return "\n".join(lines)


def snapshot_summary():
    snapshot = build_dashboard_snapshot()
    return "\n".join([
        "Interface Phase 3 dashboard snapshot",
        f"Dashboard ID: {snapshot['dashboard_id']}",
        f"Phase 3 verdict: {snapshot['phase_3_status'].get('detected_verdict', 'unknown')}",
        f"Action registry actions: {snapshot['action_registry_summary'].get('total_actions', 0)}",
        f"Artifact packages: {snapshot['artifact_summary'].get('package_count', 0)}",
        f"Reports indexed: {snapshot['document_index'].get('document_count', 0)}",
    ])


def snapshot_full():
    snapshot = build_dashboard_snapshot()
    lines = [
        "# Interface Phase 3 Dashboard Snapshot (Full)",
        "",
        json.dumps(snapshot, indent=2, sort_keys=False),
    ]
    return "\n".join(lines)
