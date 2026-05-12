from pathlib import Path

EXPORTS = Path(__file__).resolve().parent.parent / "09_exports"

PACKAGE_DEFINITIONS = {
    "trial_v3": {
        "package_id": "trial_v3",
        "package_name": "100-Round Trial v3",
        "package_path": EXPORTS / "100_round_trial_v3",
        "expected_files": [
            "final_100_round_trial_v3_acceptance_report.md",
            "scoreboards/master_scoreboard.md",
            "audits/evidence_integrity_audit.md",
        ],
        "optional_files": [
            "audits/integrity_checker_result.json",
        ],
        "known_manifest_files": [],
        "known_final_report_files": ["final_100_round_trial_v3_acceptance_report.md"],
        "known_scoreboard_files": ["scoreboards/master_scoreboard.md"],
        "known_audit_files": ["audits/evidence_integrity_audit.md"],
    },
    "non_repo_gauntlet_001": {
        "package_id": "non_repo_gauntlet_001",
        "package_name": "Non-Repo Gauntlet #1",
        "package_path": EXPORTS / "non_repo_gauntlet_001",
        "expected_files": [
            "final_non_repo_gauntlet_001_acceptance_report.md",
            "outputs/executive_summary_packet.md",
            "audits/artifact_manifest.json",
            "audits/hallucination_audit.md",
        ],
        "optional_files": [
            "audits/artifact_completeness_audit.md",
            "audits/unsupported_claims_report.md",
        ],
        "known_manifest_files": ["audits/artifact_manifest.json"],
        "known_final_report_files": ["final_non_repo_gauntlet_001_acceptance_report.md"],
        "known_scoreboard_files": [],
        "known_audit_files": ["audits/hallucination_audit.md", "audits/artifact_completeness_audit.md"],
    },
    "repo_migration": {
        "package_id": "repo_migration",
        "package_name": "Repo Migration",
        "package_path": EXPORTS / "repo_migration",
        "expected_files": [
            "the_agent_command_center_migration_report.md",
        ],
        "optional_files": [],
        "known_manifest_files": [],
        "known_final_report_files": ["the_agent_command_center_migration_report.md"],
        "known_scoreboard_files": [],
        "known_audit_files": [],
    },
    "interface_phase_1": {
        "package_id": "interface_phase_1",
        "package_name": "Interface Phase 1",
        "package_path": EXPORTS / "interface_phase_1",
        "expected_files": [
            "interface_phase_1_acceptance_report.md",
            "interface_phase_1_operator_quickstart.md",
            "interface_phase_1_command_map.md",
        ],
        "optional_files": [
            "interface_phase_1_upgrade_report.md",
            "interface_phase_1_operational_hardening_report.md",
        ],
        "known_manifest_files": [],
        "known_final_report_files": ["interface_phase_1_acceptance_report.md"],
        "known_scoreboard_files": [],
        "known_audit_files": [],
    },
    "interface_sessions": {
        "package_id": "interface_sessions",
        "package_name": "Interface Phase 1 Sessions",
        "package_path": EXPORTS / "interface_phase_1" / "sessions",
        "expected_files": [],
        "optional_files": [],
        "known_manifest_files": [],
        "known_final_report_files": [],
        "known_scoreboard_files": [],
        "known_audit_files": [],
    },
}


def inspect_package(package_id):
    pdef = PACKAGE_DEFINITIONS.get(package_id)
    if not pdef:
        return {
            "package_id": package_id,
            "package_name": package_id,
            "exists": False,
            "status": "MISSING",
            "error": f"Unknown package_id: {package_id}",
        }

    path = pdef["package_path"]
    if not path.exists():
        return {
            "package_id": package_id,
            "package_name": pdef["package_name"],
            "exists": False,
            "file_count": 0,
            "directory_count": 0,
            "expected_files_present": [],
            "expected_files_missing": pdef["expected_files"],
            "zero_byte_files": [],
            "final_verdict": "not detected",
            "recommended_next_step": "not detected",
            "manifest_status": "not detected",
            "warnings": ["Package directory not found"],
            "status": "MISSING",
        }

    all_items = list(path.rglob("*"))
    file_count = len([f for f in all_items if f.is_file()])
    dir_count = len([d for d in all_items if d.is_dir()])

    expected_present = []
    expected_missing = []

    for rel_path in pdef["expected_files"]:
        full = path / rel_path
        if full.exists():
            expected_present.append(rel_path)
        else:
            expected_missing.append(rel_path)

    for rel_path in pdef["optional_files"]:
        full = path / rel_path
        if full.exists():
            expected_present.append(rel_path)

    zero_byte = [str(f.relative_to(EXPORTS)) for f in all_items if f.is_file() and f.stat().st_size == 0]

    final_verdict = "not detected"
    recommended_next_step = "not detected"
    manifest_status = "not detected"
    warnings = []

    for report_rel in pdef["known_final_report_files"]:
        rpath = path / report_rel
        if rpath.exists():
            content = rpath.read_text()
            for line in content.splitlines():
                ls = line.strip()
                if "PASS_WITH_HIGH_CONFIDENCE" in ls or "PASS_WITH_NOTES" in ls:
                    final_verdict = ls
                if "Recommended" in ls and "next" in ls.lower():
                    recommended_next_step = ls
                    break

    for manifest_rel in pdef["known_manifest_files"]:
        mpath = path / manifest_rel
        if mpath.exists():
            try:
                import json
                mdata = json.loads(mpath.read_text())
                total_expected = mdata.get("total_expected", "?")
                total_present = mdata.get("total_present", "?")
                total_missing = mdata.get("total_missing", "?")
                manifest_status = f"{total_present}/{total_expected} present, {total_missing} missing"
            except Exception:
                manifest_status = "unreadable"
        else:
            manifest_status = "file not found"

    if expected_missing:
        warnings.append(f"Missing expected files: {', '.join(expected_missing)}")
    if zero_byte:
        warnings.append(f"Zero-byte files: {len(zero_byte)} detected")

    status = "PASS"
    if expected_missing:
        status = "WARNING"
    if not path.exists():
        status = "MISSING"
    if zero_byte and status == "PASS":
        status = "WARNING"

    return {
        "package_id": package_id,
        "package_name": pdef["package_name"],
        "exists": True,
        "file_count": file_count,
        "directory_count": dir_count,
        "expected_files_present": expected_present,
        "expected_files_missing": expected_missing,
        "zero_byte_files": zero_byte,
        "final_verdict": final_verdict,
        "recommended_next_step": recommended_next_step,
        "manifest_status": manifest_status,
        "warnings": warnings,
        "status": status,
    }


def inspect_all_packages():
    results = {}
    for pid in PACKAGE_DEFINITIONS:
        results[pid] = inspect_package(pid)
    return results


def extract_final_verdict(report_path):
    p = Path(report_path)
    if not p.exists():
        return "not detected"
    for line in p.read_text().splitlines():
        ls = line.strip()
        if "PASS_WITH_HIGH_CONFIDENCE" in ls or "PASS_WITH_NOTES" in ls or "PARTIAL_PASS" in ls or "FAIL_" in ls:
            return ls
    return "not detected"


def extract_recommended_next_step(report_path):
    p = Path(report_path)
    if not p.exists():
        return "not detected"
    for line in p.read_text().splitlines():
        ls = line.strip()
        if "Recommended" in ls and "next" in ls.lower():
            return ls
    return "not detected"


def find_zero_byte_files(package_path):
    p = Path(package_path)
    if not p.exists():
        return []
    return [str(f.relative_to(EXPORTS)) for f in p.rglob("*") if f.is_file() and f.stat().st_size == 0]


def find_missing_expected_files(package_id):
    pdef = PACKAGE_DEFINITIONS.get(package_id)
    if not pdef:
        return []
    path = pdef["package_path"]
    return [r for r in pdef["expected_files"] if not (path / r).exists()]


def count_files(package_path):
    p = Path(package_path)
    if not p.exists():
        return 0
    return len([f for f in p.rglob("*") if f.is_file()])


def count_directories(package_path):
    p = Path(package_path)
    if not p.exists():
        return 0
    return len([d for d in p.rglob("*") if d.is_dir()])


def detect_manifest_status(package_id):
    pdef = PACKAGE_DEFINITIONS.get(package_id)
    if not pdef:
        return "not detected"
    path = pdef["package_path"]
    for manifest_rel in pdef["known_manifest_files"]:
        mpath = path / manifest_rel
        if mpath.exists():
            try:
                import json
                mdata = json.loads(mpath.read_text())
                te = mdata.get("total_expected", "?")
                tp = mdata.get("total_present", "?")
                tm = mdata.get("total_missing", "?")
                return f"{tp}/{te} present, {tm} missing"
            except Exception:
                return "unreadable"
    return "file not found"


def detect_stale_claims(package_id):
    pdef = PACKAGE_DEFINITIONS.get(package_id)
    if not pdef:
        return []
    path = pdef["package_path"]
    warnings = []
    for report_rel in pdef["known_final_report_files"]:
        rpath = path / report_rel
        if rpath.exists():
            content = rpath.read_text()
            if "MISSING" in content or "0 bytes" in content:
                warnings.append(f"Stale claim detected in {report_rel}: references missing/zero-byte")
    return warnings
