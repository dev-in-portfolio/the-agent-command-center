import subprocess
import sys
import json
import hashlib
import importlib.util
from pathlib import Path
from datetime import datetime, timezone, timedelta
from shutil import copy2

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCRIPTS = ROOT / "scripts"
EXPORTS = ROOT / "09_exports"
INTERFACE_EXPORTS = EXPORTS / "interface_phase_1"
SESSIONS_DIR = INTERFACE_EXPORTS / "sessions"
COMMAND_PACKETS = INTERFACE_EXPORTS / "command_packets"


def _load_config():
    config_path = HERE / "interface_config.json"
    if not config_path.exists():
        return {
            "product_repo": "dev-in-portfolio/the-agent-command-center",
            "source_lineage": "dev-in-portfolio/agent-command-center-3",
            "runtime_version_expected": "25.0.0",
            "interface_phase": "1",
            "mode": "CLI operator console",
        }
    try:
        return json.loads(config_path.read_text())
    except Exception:
        return {
            "product_repo": "dev-in-portfolio/the-agent-command-center",
            "source_lineage": "dev-in-portfolio/agent-command-center-3",
            "runtime_version_expected": "25.0.0",
            "interface_phase": "1",
            "mode": "CLI operator console",
        }


def _load_policy():
    path = HERE / "interface_policy.py"
    spec = importlib.util.spec_from_file_location("interface_policy", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_policy = _load_policy()
_config = _load_config()
LOCKED_ACTIONS = _policy.LOCKED_ACTIONS
LOCKED_ACTION_LABELS = _policy.LOCKED_ACTION_LABELS
REPO_NAME = _config.get("product_repo", "dev-in-portfolio/the-agent-command-center")
SOURCE_LINEAGE = _config.get("source_lineage", "dev-in-portfolio/agent-command-center-3")
RUNTIME_VERSION = _config.get("runtime_version_expected", "25.0.0")
INTERFACE_PHASE = _config.get("interface_phase", "1")


def _make_result(action, status, title, details=None, artifacts=None, recommended_next=None):
    return {
        "action": action,
        "status": status,
        "title": title,
        "details": details or [],
        "artifacts": artifacts or [],
        "recommended_next_action": recommended_next or "",
    }


def _banner(status, message):
    print(f"\n  [{status}] {message}\n")


def _write_session_files(session_log):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    session_dir = SESSIONS_DIR / f"session_{ts}"
    session_dir.mkdir(parents=True, exist_ok=True)

    report = session_log.generate_report()
    report_path = session_dir / "session_report.md"
    report_path.write_text(report)

    json_path = session_dir / "session_result.json"
    json_path.write_text(json.dumps(session_log.to_dict(), indent=2))

    requested = session_log.actions_requested
    if any("validator_wall" in a for a in requested):
        stdout_lines = []
        vw_path = session_dir / "validator_wall_stdout.txt"
        for v in session_log.validator_results:
            stdout_lines.append(f"=== {v['name']} ===")
            stdout_lines.append(v["stdout"])
        vw_path.write_text("\n".join(stdout_lines))

        vwj_path = session_dir / "validator_wall_result.json"
        vwj_path.write_text(json.dumps(session_log.validator_results, indent=2))

    if session_log.command_packets_prepared:
        pp_dir = session_dir / "prepared_packets"
        pp_dir.mkdir(parents=True, exist_ok=True)
        for cp in session_log.command_packets_prepared:
            src = Path(cp)
            if src.exists():
                copy2(str(src), str(pp_dir / src.name))

    latest_path = INTERFACE_EXPORTS / "operator_session_report.md"
    latest_path.write_text(report)

    return str(session_dir)


def _make_packet_id(packet_type):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"PKT-{packet_type.upper()}-{ts}"


def _write_packet(packet_type, session_log):
    packet_id = _make_packet_id(packet_type)
    ts = datetime.now(timezone.utc).isoformat()
    approval_phrase = f"I_APPROVE_PREPARED_PACKET_{packet_type.upper()}"

    templates = {
        "validator_wall": {
            "risk_level": "low",
            "purpose": "Run all three validators to confirm system integrity before any operation.",
            "scope": "scripts/validate_auto_self_improve_2.py, validate_station_chief_runtime_v25_0.py, validate_station_chief_runtime_v24_0.py",
            "allowed_actions": ["Run validator wall from CLI menu option 2 or --validator-wall"],
            "forbidden_actions": ["Skip validation", "Ignore failures", "Modify validators"],
            "exact_commands": [
                "python3 scripts/validate_auto_self_improve_2.py",
                "python3 scripts/validate_station_chief_runtime_v25_0.py",
                "python3 scripts/validate_station_chief_runtime_v24_0.py",
            ],
            "expected_output_files": ["stdout from each validator showing PASS/FAIL"],
            "preflight_checklist": ["Master branch is up to date", "No dirty tracked files",
                                    "No unexpected changes staged"],
            "validator_requirements_before": ["INTERFACE_PHASE_1_CLI_VALIDATION_PASS"],
            "validator_requirements_after": ["AUTO_SELF_IMPROVE_2_VALIDATION_PASS",
                                              "STATION_CHIEF_RUNTIME_V25_0_VALIDATION_PASS",
                                              "STATION_CHIEF_RUNTIME_V24_0_VALIDATION_PASS"],
            "rollback_notes": "Validator wall is read-only. No rollback needed.",
            "do_not_run_if": ["Validators already passed in current session",
                              "Network is required but unavailable (v24 validator fetches example.com)"],
        },
        "artifact_audit": {
            "risk_level": "low",
            "purpose": "Audit all artifact packages for completeness, integrity, and stale claims.",
            "scope": "09_exports/100_round_trial_v3/, 09_exports/non_repo_gauntlet_001/",
            "allowed_actions": ["List artifact packages from CLI menu option 3",
                                "Inspect key report files"],
            "forbidden_actions": ["Modify artifacts during audit", "Delete reports", "Skip missing file checks"],
            "exact_commands": [
                "python3 scripts/validate_exports.py",
                "ls -la 09_exports/100_round_trial_v3/",
                "ls -la 09_exports/non_repo_gauntlet_001/",
            ],
            "expected_output_files": ["audit report listing present/missing files"],
            "preflight_checklist": ["Artifact directories exist", "No concurrent modification in progress"],
            "validator_requirements_before": [],
            "validator_requirements_after": [],
            "rollback_notes": "Audit is read-only. No rollback needed.",
            "do_not_run_if": ["Artifact directories are being modified"],
        },
        "non_repo_gauntlet_review": {
            "risk_level": "low",
            "purpose": "Review non-repo extreme work gauntlet #1 outputs and final verdict.",
            "scope": "09_exports/non_repo_gauntlet_001/",
            "allowed_actions": ["View executive summary", "Inspect task outputs",
                                "Review hallucination audit", "Review completeness audit"],
            "forbidden_actions": ["Regenerate artifacts", "Modify acceptance report", "Delete audit trails"],
            "exact_commands": [
                "cat 09_exports/non_repo_gauntlet_001/outputs/executive_summary_packet.md",
                "cat 09_exports/non_repo_gauntlet_001/final_non_repo_gauntlet_001_acceptance_report.md",
            ],
            "expected_output_files": ["Printed report contents (stdout)"],
            "preflight_checklist": ["Gauntlet output directory exists"],
            "validator_requirements_before": [],
            "validator_requirements_after": [],
            "rollback_notes": "Review is read-only. No rollback needed.",
            "do_not_run_if": ["Gauntlet artifacts are mid-update"],
        },
        "trial_v3_review": {
            "risk_level": "low",
            "purpose": "Review 100-round trial v3 evidence and acceptance verdict.",
            "scope": "09_exports/100_round_trial_v3/",
            "allowed_actions": ["View final acceptance report", "Inspect scoreboard", "Inspect audit log"],
            "forbidden_actions": ["Regenerate rounds", "Modify evidence files", "Alter scoreboard"],
            "exact_commands": [
                "cat 09_exports/100_round_trial_v3/final_100_round_trial_v3_acceptance_report.md",
                "cat 09_exports/100_round_trial_v3/scoreboards/master_scoreboard.md",
            ],
            "expected_output_files": ["Printed report contents (stdout)"],
            "preflight_checklist": ["Trial v3 output directory exists"],
            "validator_requirements_before": [],
            "validator_requirements_after": [],
            "rollback_notes": "Review is read-only. No rollback needed.",
            "do_not_run_if": ["Trial evidence is mid-update"],
        },
        "migration_review": {
            "risk_level": "low",
            "purpose": "Review repo migration report for The Agent Command Center.",
            "scope": "09_exports/repo_migration/",
            "allowed_actions": ["View migration report", "Confirm source lineage", "Check preserved evidence"],
            "forbidden_actions": ["Revert migration", "Delete migration report", "Modify source remote"],
            "exact_commands": [
                "cat 09_exports/repo_migration/the_agent_command_center_migration_report.md",
                "git remote -v",
            ],
            "expected_output_files": ["Printed report contents (stdout)"],
            "preflight_checklist": ["Migration report exists"],
            "validator_requirements_before": [],
            "validator_requirements_after": [],
            "rollback_notes": "Review is read-only. No rollback needed.",
            "do_not_run_if": ["Remotes have been changed since migration"],
        },
        "merge_review_packet": {
            "risk_level": "medium",
            "purpose": "Review changeset before merging a branch into master.",
            "scope": "Full repo diff against base branch",
            "allowed_actions": ["View diff", "Check for unexpected file changes", "Run validator wall"],
            "forbidden_actions": ["Merge without review", "Skip validators", "Force push"],
            "exact_commands": [
                "git diff --name-only master..HEAD",
                "git diff master..HEAD --stat",
                "python3 scripts/validate_auto_self_improve_2.py",
            ],
            "expected_output_files": ["Diff output", "Validator results"],
            "preflight_checklist": ["All changes committed", "No dirty tracked files",
                                    "Validators pass before merge"],
            "validator_requirements_before": ["AUTO_SELF_IMPROVE_2_VALIDATION_PASS",
                                              "STATION_CHIEF_RUNTIME_V25_0_VALIDATION_PASS",
                                              "STATION_CHIEF_RUNTIME_V24_0_VALIDATION_PASS"],
            "validator_requirements_after": ["Same validators still pass after merge"],
            "rollback_notes": "If merge causes issues, use git reset --hard ORIG_HEAD on master.",
            "do_not_run_if": ["Working tree is dirty", "Validators are failing",
                              "Unexpected files would be committed"],
        },
        "interface_phase_1_merge_review": {
            "risk_level": "medium",
            "purpose": "Review and merge Interface Phase 1 CLI into master.",
            "scope": "11_interface/**, scripts/validate_interface_phase_1_cli.py, 09_exports/interface_phase_1/**",
            "allowed_actions": ["View diff", "Run validator wall", "Run interface validator",
                                "Confirm no code/runtime/validator changes beyond interface"],
            "forbidden_actions": ["Merge without all validators passing", "Skip review",
                                  "Modify runtime files"],
            "exact_commands": [
                "git diff --name-only master..HEAD",
                "python3 scripts/validate_interface_phase_1_cli.py",
                "python3 scripts/validate_auto_self_improve_2.py",
            ],
            "expected_output_files": ["Diff confirming only interface files changed",
                                      "INTERFACE_PHASE_1_CLI_VALIDATION_PASS"],
            "preflight_checklist": ["All interface validators pass", "No runtime files modified",
                                    "No existing validator files modified"],
            "validator_requirements_before": ["INTERFACE_PHASE_1_CLI_VALIDATION_PASS",
                                              "AUTO_SELF_IMPROVE_2_VALIDATION_PASS",
                                              "STATION_CHIEF_RUNTIME_V25_0_VALIDATION_PASS",
                                              "STATION_CHIEF_RUNTIME_V24_0_VALIDATION_PASS"],
            "validator_requirements_after": ["Same validators still pass post-merge"],
            "rollback_notes": "Use git reset --hard ORIG_HEAD if merge causes issues.",
            "do_not_run_if": ["Runtime files modified", "Existing validators modified"],
        },
        "interface_phase_2_planning": {
            "risk_level": "informational",
            "purpose": "Plan and prepare for Interface Phase 2 TUI development.",
            "scope": "Planning document and research only",
            "allowed_actions": ["Review Phase 1 lessons", "Research TUI frameworks",
                                "Draft Phase 2 requirements"],
            "forbidden_actions": ["Begin Phase 2 implementation without approval",
                                  "Modify Phase 1 files outside planning scope"],
            "exact_commands": ["cat 11_interface/README.md"],
            "expected_output_files": ["Phase 2 planning document"],
            "preflight_checklist": ["Phase 1 is stable and merged"],
            "validator_requirements_before": [],
            "validator_requirements_after": [],
            "rollback_notes": "Planning is read-only. No rollback needed.",
            "do_not_run_if": ["Phase 1 is not yet merged to master"],
        },
        "artifact_integrity_audit": {
            "risk_level": "low",
            "purpose": "Deep integrity audit of all artifact packages.",
            "scope": "09_exports/100_round_trial_v3/, 09_exports/non_repo_gauntlet_001/",
            "allowed_actions": ["Verify SHA256 checksums", "Confirm file counts",
                                "Check for zero-byte files", "Validate manifests"],
            "forbidden_actions": ["Modify artifacts", "Delete artifacts", "Skip integrity checks"],
            "exact_commands": [
                "find 09_exports/ -type f -size 0 -exec echo 'ZERO:' {} ;",
                "find 09_exports/ -type f | wc -l",
            ],
            "expected_output_files": ["Integrity audit report"],
            "preflight_checklist": ["All artifact directories present"],
            "validator_requirements_before": [],
            "validator_requirements_after": [],
            "rollback_notes": "Audit is read-only. No rollback needed.",
            "do_not_run_if": ["Artifacts are being modified concurrently"],
        },
        "release_readiness_review": {
            "risk_level": "medium",
            "purpose": "Review release readiness before promoting interface to production use.",
            "scope": "Full repo, all validators, all artifact packages",
            "allowed_actions": ["Run all validators", "Review all artifacts",
                                "Confirm locked actions", "Review session history"],
            "forbidden_actions": ["Promote without human approval", "Deploy without review",
                                  "Skip any validator"],
            "exact_commands": [
                "python3 scripts/validate_interface_phase_1_cli.py",
                "python3 scripts/validate_auto_self_improve_2.py",
                "python3 scripts/validate_station_chief_runtime_v25_0.py",
                "python3 scripts/validate_station_chief_runtime_v24_0.py",
            ],
            "expected_output_files": ["All validator PASS outputs"],
            "preflight_checklist": ["All validators pass", "No dirty tracked files",
                                    "All interface tests pass", "No locked actions bypassed"],
            "validator_requirements_before": ["INTERFACE_PHASE_1_CLI_VALIDATION_PASS",
                                              "AUTO_SELF_IMPROVE_2_VALIDATION_PASS",
                                              "STATION_CHIEF_RUNTIME_V25_0_VALIDATION_PASS",
                                              "STATION_CHIEF_RUNTIME_V24_0_VALIDATION_PASS"],
            "validator_requirements_after": ["Same validators still pass"],
            "rollback_notes": "Promotion is irreversible once approved. Ensure all criteria met.",
            "do_not_run_if": ["Any validator fails", "Boundary violations exist"],
        },
        "cleanup_branch_review": {
            "risk_level": "low",
            "purpose": "Review a feature branch for safe cleanup after merge.",
            "scope": "Local and remote branches",
            "allowed_actions": ["List branches", "Check if merged", "Review diff against master"],
            "forbidden_actions": ["Delete branches without confirmation", "Force delete"],
            "exact_commands": [
                "git branch --merged master | grep -v master",
                "git branch -r --merged origin/master | grep -v master",
            ],
            "expected_output_files": ["List of merged branches eligible for cleanup"],
            "preflight_checklist": ["Branch has been merged", "No unmerged work remains"],
            "validator_requirements_before": [],
            "validator_requirements_after": [],
            "rollback_notes": "Deleted branches can be recovered from reflog for 90 days.",
            "do_not_run_if": ["Branch has not been merged", "Branch contains unmerged work"],
        },
        "branch_delete_review": {
            "risk_level": "high",
            "purpose": "Review and approve deletion of a specific branch.",
            "scope": "Single branch deletion",
            "allowed_actions": ["Confirm branch is merged", "Confirm no data loss"],
            "forbidden_actions": ["Delete master or main", "Delete without confirmation",
                                  "Delete remote branch without local backup"],
            "exact_commands": [
                "git branch --merged master | grep <branch-name>",
                "git log --oneline master..<branch-name> | head -20",
            ],
            "expected_output_files": ["Confirmation that branch is fully merged"],
            "preflight_checklist": ["Branch is fully merged", "No uncommitted work",
                                    "Remote and local are in sync"],
            "validator_requirements_before": [],
            "validator_requirements_after": [],
            "rollback_notes": "Deleted local branches can be recovered from reflog. "
                             "Deleted remote branches may not be recoverable.",
            "do_not_run_if": ["Branch is not fully merged", "Branch is master/main",
                              "Unmerged work would be lost"],
        },
    }

    tpl = templates.get(packet_type, {
        "risk_level": "unknown",
        "purpose": "Review and analysis packet.",
        "scope": "As defined by operator",
        "allowed_actions": ["Review", "Analyze"],
        "forbidden_actions": ["Execute without approval"],
        "exact_commands": [],
        "expected_output_files": [],
        "preflight_checklist": [],
        "validator_requirements_before": [],
        "validator_requirements_after": [],
        "rollback_notes": "No automated rollback defined.",
        "do_not_run_if": [],
    })

    lines = []
    lines.append(f"# Command Packet: {packet_type}")
    lines.append("")
    lines.append(f"**Packet ID:** {packet_id}")
    lines.append(f"**Packet Type:** {packet_type}")
    lines.append(f"**Created At (UTC):** {ts}")
    lines.append(f"**Repo:** {REPO_NAME}")
    lines.append(f"**Source Lineage:** {SOURCE_LINEAGE}")
    lines.append(f"**Risk Level:** {tpl['risk_level']}")
    lines.append("")
    lines.append(f"**Status:** prepared_not_executed")
    lines.append(f"**Purpose:** {tpl['purpose']}")
    lines.append(f"**Scope:** {tpl['scope']}")
    lines.append("")
    lines.append("## Allowed Actions")
    for a in tpl["allowed_actions"]:
        lines.append(f"- {a}")
    lines.append("")
    lines.append("## Forbidden Actions")
    for f in tpl["forbidden_actions"]:
        lines.append(f"- {f}")
    lines.append("")
    if tpl["exact_commands"]:
        lines.append("## Exact Commands to Run Later")
        for cmd in tpl["exact_commands"]:
            lines.append("```")
            lines.append(cmd)
            lines.append("```")
        lines.append("")
    if tpl["expected_output_files"]:
        lines.append("## Expected Output Files")
        for e in tpl["expected_output_files"]:
            lines.append(f"- {e}")
        lines.append("")
    if tpl["preflight_checklist"]:
        lines.append("## Preflight Checklist")
        for item in tpl["preflight_checklist"]:
            lines.append(f"- [ ] {item}")
        lines.append("")
    if tpl["validator_requirements_before"]:
        lines.append("## Validator Requirements (Before)")
        for vr in tpl["validator_requirements_before"]:
            lines.append(f"- {vr}")
        lines.append("")
    if tpl["validator_requirements_after"]:
        lines.append("## Validator Requirements (After)")
        for vr in tpl["validator_requirements_after"]:
            lines.append(f"- {vr}")
        lines.append("")
    if tpl["rollback_notes"]:
        lines.append("## Rollback Notes")
        lines.append(tpl["rollback_notes"])
        lines.append("")
    if tpl["do_not_run_if"]:
        lines.append("## Do Not Run If")
        for dnr in tpl["do_not_run_if"]:
            lines.append(f"- {dnr}")
        lines.append("")

    lines.append("## Human Approval Required")
    lines.append("Yes.")
    lines.append("")
    lines.append(f"## Required Approval Phrase")
    lines.append(f"`{approval_phrase}`")
    lines.append("")
    lines.append("## Execution Status")
    lines.append("This packet has been prepared but NOT executed.")
    lines.append("An operator must review and explicitly approve before any command is run.")

    return "\n".join(lines), packet_id, approval_phrase


def _check_package_expected(package_label, path, expected_files):
    result = {
        "package": package_label,
        "exists": path.exists(),
        "file_count": 0,
        "dir_count": 0,
        "key_reports": [],
        "missing_expected": [],
        "zero_byte_files": [],
        "detected_verdict": None,
        "manifest_status": None,
    }
    if not path.exists():
        return result

    all_items = list(path.rglob("*"))
    result["file_count"] = len([f for f in all_items if f.is_file()])
    result["dir_count"] = len([d for d in all_items if d.is_dir()])

    for fname, label in expected_files:
        fpath = path / fname if not (path.parent / fname).exists() else path.parent / fname
        apath = path / fname
        if apath.exists():
            result["key_reports"].append({"path": str(apath.relative_to(EXPORTS)), "label": label, "present": True})
            if apath.stat().st_size == 0:
                result["zero_byte_files"].append(str(apath))
            content = apath.read_text()
            for verdict_key in ["PASS_WITH_HIGH_CONFIDENCE", "PASS_WITH_NOTES",
                                "PARTIAL_PASS", "FAIL_", "VERDICT"]:
                if verdict_key in content:
                    for line in content.splitlines():
                        if "PASS_WITH" in line or verdict_key in line:
                            result["detected_verdict"] = line.strip()
                            break
        else:
            result["missing_expected"].append(fname)
            result["key_reports"].append({"path": fname, "label": label, "present": False})

    for f in all_items:
        if f.is_file() and f.stat().st_size == 0:
            rel = str(f.relative_to(EXPORTS))
            if rel not in result["zero_byte_files"]:
                result["zero_byte_files"].append(rel)

    return result


def _display_package_status(status_result):
    pkg = status_result["package"]
    print(f"  {pkg}:")
    if not status_result["exists"]:
        print("    Exists: no")
        return
    print(f"    Exists: yes")
    print(f"    File count: {status_result['file_count']}")
    print(f"    Directory count: {status_result['dir_count']}")
    if status_result["detected_verdict"]:
        print(f"    Detected verdict: {status_result['detected_verdict']}")
    if status_result["key_reports"]:
        print(f"    Key reports:")
        for kr in status_result["key_reports"]:
            mark = "+" if kr["present"] else "MISSING"
            print(f"      [{mark}] {kr['label']}: {kr['path']}")
    if status_result["missing_expected"]:
        print(f"    WARNING: {len(status_result['missing_expected'])} expected file(s) missing")
    if status_result["zero_byte_files"]:
        print(f"    WARNING: {len(status_result['zero_byte_files'])} zero-byte file(s) detected")


# ---------------------------------------------------------------------------
# Action implementations
# ---------------------------------------------------------------------------

def action_show_status(session_log):
    lines = []
    lines.append("=== System Status ===")
    lines.append(f"Product repo: {REPO_NAME}")
    lines.append(f"Source lineage: {SOURCE_LINEAGE}")
    lines.append(f"Runtime version expected: {RUNTIME_VERSION}")
    lines.append("Repo role: product/interface workspace")
    lines.append("Official repo status: locked / not touched")
    lines.append("Repo 2 status: locked / not touched")
    lines.append("Repo 3 status: source lineage only / not mutated")
    lines.append("Deployment: disabled")
    lines.append("Secrets: disabled")
    lines.append("Credentials: disabled")
    lines.append("Promotion: disabled")
    lines.append(f"Interface phase: {INTERFACE_PHASE}")
    lines.append("Mode: CLI operator console")
    lines.append("")
    print("\n".join(lines))

    result = _make_result("show_status", "PASS", lines[0][4:-4])
    session_log.record_action("show_status", result)
    _banner("INFO", "All systems nominal. Continue with safe or controlled actions.")


def action_run_validator_wall(session_log):
    _banner("INFO", "Starting validator wall...")

    validators = [
        ("auto-self-improve-2", SCRIPTS / "validate_auto_self_improve_2.py"),
        ("station-chief-runtime-v25-0", SCRIPTS / "validate_station_chief_runtime_v25_0.py"),
        ("station-chief-runtime-v24-0", SCRIPTS / "validate_station_chief_runtime_v24_0.py"),
    ]
    all_passed = True
    results = []

    for name, path in validators:
        if not path.exists():
            _banner("WARNING", f"{name}: script not found")
            session_log.record_validator_result(name, -1, "script not found", datetime.now(timezone.utc).isoformat())
            all_passed = False
            continue

        print(f"  Running {name}...")
        ts = datetime.now(timezone.utc).isoformat()
        start = datetime.now()

        try:
            result = subprocess.run(
                [sys.executable, str(path)],
                capture_output=True, text=True, timeout=120
            )
            elapsed = (datetime.now() - start).total_seconds()
            passed = result.returncode == 0
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {name} (rc={result.returncode}, {elapsed:.1f}s)")
            if result.stdout:
                for line in result.stdout.strip().splitlines():
                    print(f"    {line}")
            if result.stderr:
                _banner("WARNING", f"{name} stderr output")
                for line in result.stderr.strip().splitlines():
                    print(f"    {line}")
            session_log.record_validator_result(name, result.returncode, result.stdout, ts)
            session_log.record_action_duration(name, elapsed)
            if not passed:
                all_passed = False
        except subprocess.TimeoutExpired:
            _banner("WARNING", f"{name} timed out after 120s")
            session_log.record_validator_result(name, -1, "timeout", ts)
            all_passed = False
        except Exception as e:
            _banner("ERROR", f"{name}: {e}")
            session_log.record_validator_result(name, -1, str(e), ts)
            all_passed = False

    final = "ALL PASS" if all_passed else "SOME FAILED"
    next_action = "Generate operator session report or prepare a merge review packet."
    _banner("PASS" if all_passed else "FAIL", f"Validator wall result: {final}")
    print(f"  Recommended next action: {next_action}")

    result = _make_result("run_validator_wall", "PASS" if all_passed else "FAIL",
                          f"Validator wall: {final}", results, recommended_next=next_action)
    session_log.record_action("run_validator_wall", result, next_action)


def action_list_artifact_packages(session_log):
    _banner("INFO", "Inspecting artifact packages...")

    packages = [
        ("100-Round Trial v3", EXPORTS / "100_round_trial_v3", [
            ("final_100_round_trial_v3_acceptance_report.md", "Final acceptance report"),
            ("scoreboards/master_scoreboard.md", "Master scoreboard"),
            ("audits/evidence_integrity_audit.md", "Evidence integrity audit"),
            ("audits/integrity_checker_result.json", "Integrity checker result"),
        ]),
        ("Non-Repo Gauntlet #1", EXPORTS / "non_repo_gauntlet_001", [
            ("final_non_repo_gauntlet_001_acceptance_report.md", "Final acceptance report"),
            ("outputs/executive_summary_packet.md", "Executive summary"),
            ("audits/artifact_manifest.json", "Artifact manifest"),
            ("audits/hallucination_audit.md", "Hallucination audit"),
        ]),
        ("Repo Migration", EXPORTS / "repo_migration", [
            ("the_agent_command_center_migration_report.md", "Migration report"),
        ]),
        ("Interface Phase 1", INTERFACE_EXPORTS, [
            ("interface_phase_1_acceptance_report.md", "Phase 1 acceptance report"),
            ("interface_phase_1_operator_quickstart.md", "Operator quickstart"),
            ("interface_phase_1_command_map.md", "Command map"),
        ]),
        ("Interface Phase 1 Sessions", SESSIONS_DIR, []),
    ]

    for label, path, expected in packages:
        status = _check_package_expected(label, path, expected)
        _display_package_status(status)
        session_log.record_artifact_inspection(label, "present" if status["exists"] else "missing")
        if status["missing_expected"]:
            session_log.record_warning(f"{label}: missing {status['missing_expected']}")
        print()

    next_action = "Review latest summaries or run validator wall."
    print(f"  Recommended next action: {next_action}")
    result = _make_result("list_artifacts", "PASS", "Artifact packages inspected",
                          recommended_next=next_action)
    session_log.record_action("list_artifacts", result, next_action)


def action_show_summaries(session_log):
    _banner("INFO", "Loading latest summaries...")

    reports = [
        ("100-round trial v3",
         EXPORTS / "100_round_trial_v3" / "final_100_round_trial_v3_acceptance_report.md"),
        ("non-repo gauntlet #1",
         EXPORTS / "non_repo_gauntlet_001" / "final_non_repo_gauntlet_001_acceptance_report.md"),
        ("repo migration",
         EXPORTS / "repo_migration" / "the_agent_command_center_migration_report.md"),
    ]

    for label, path in reports:
        if path.exists():
            content = path.read_text()
            preview_lines = content.splitlines()[:12]
            print(f"  {label}:")
            for pl in preview_lines:
                print(f"    {pl}")
            print("    (...)")
        else:
            print(f"  {label}: report not found")
        print()

    next_action = "Generate operator session report or prepare a command packet."
    print(f"  Recommended next action: {next_action}")
    result = _make_result("show_summaries", "PASS", "Summaries displayed",
                          recommended_next=next_action)
    session_log.record_action("show_summaries", result, next_action)


def action_generate_session_report(session_log):
    _banner("INFO", "Generating operator session report...")

    session_log.record_action("generate_session_report")
    session_log.close()
    session_dir = _write_session_files(session_log)
    session_log.record_report(session_dir)

    _banner("PASS", f"Session report written")
    print(f"  Session directory: {session_dir}")
    print(f"  Location: 09_exports/interface_phase_1/sessions/")
    print(f"  Latest: 09_exports/interface_phase_1/operator_session_report.md")
    print(f"  Result JSON: {session_dir}/session_result.json")
    if session_log.command_packets_prepared:
        print(f"  Packets: {session_dir}/prepared_packets/")
    if session_log.validator_results:
        print(f"  Validator logs: {session_dir}/validator_wall_stdout.txt")
        print(f"  Validator results: {session_dir}/validator_wall_result.json")

    next_action = "Review session report or continue with another action."
    print(f"  Recommended next action: {next_action}")
    result = _make_result("generate_session_report", "PASS", "Session report generated",
                          recommended_next=next_action)
    session_log.record_action("generate_session_report", result, next_action)


def action_show_locked_actions(session_log):
    _banner("INFO", "Locked actions summary")

    print("  The following actions are permanently locked and cannot be performed:")
    for action_key in LOCKED_ACTIONS:
        label = LOCKED_ACTION_LABELS.get(action_key, action_key)
        print(f"    - {label}")
    print("")
    print("  Interface Phase 1 refuses all locked actions.")
    print("  No bypass, override, or escalation path exists.")

    next_action = "Continue only with safe or controlled actions."
    print(f"\n  Recommended next action: {next_action}")
    result = _make_result("show_locked_actions", "PASS", "Locked actions displayed",
                          recommended_next=next_action)
    session_log.record_action("show_locked_actions", result, next_action)


def action_prepare_command_packet(session_log):
    _banner("INFO", "Prepare command packet")

    packet_types = [
        "validator_wall",
        "artifact_audit",
        "non_repo_gauntlet_review",
        "trial_v3_review",
        "migration_review",
        "merge_review_packet",
        "interface_phase_1_merge_review",
        "interface_phase_2_planning",
        "artifact_integrity_audit",
        "release_readiness_review",
        "cleanup_branch_review",
        "branch_delete_review",
    ]

    print("  Select packet type:")
    for i, pt in enumerate(packet_types, 1):
        print(f"  {i}. {pt}")
    print("  0. Cancel")

    try:
        choice = input("\n  Enter choice: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n  Cancelled.")
        return

    if choice == "0" or choice == "":
        print("  Cancelled.")
        return

    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(packet_types):
            print("  Invalid choice.")
            return
        packet_type = packet_types[idx]
    except ValueError:
        print("  Invalid input.")
        return

    COMMAND_PACKETS.mkdir(parents=True, exist_ok=True)
    packet_path = COMMAND_PACKETS / f"{packet_type}_packet.md"

    content, packet_id, approval_phrase = _write_packet(packet_type, session_log)
    packet_path.write_text(content)

    session_log.record_command_packet(str(packet_path))
    _banner("PASS", f"Command packet prepared")
    print(f"  Packet ID: {packet_id}")
    print(f"  Packet: {packet_path}")
    print(f"  Status: prepared_not_executed")
    print(f"  Approval phrase: {approval_phrase}")
    print("  NOTE: This packet has NOT been executed.")

    next_action = "Review the prepared packet, or generate a session report."
    print(f"  Recommended next action: {next_action}")
    result = _make_result("prepare_command_packet", "PASS",
                          f"Packet prepared: {packet_type}",
                          recommended_next=next_action)
    session_log.record_action("prepare_command_packet", result, next_action)


def action_show_session_state(session_log):
    _banner("INFO", "Current session state")
    print(f"  Session ID: {session_log.session_id}")
    print(f"  Started: {session_log.started_at_utc}")
    print(f"  Branch: {session_log.git_branch_start} @ {session_log.git_commit_start}")
    print(f"  Actions requested: {len(session_log.actions_requested)}")
    print(f"  Actions completed: {len(session_log.actions_completed)}")
    print(f"  Actions refused: {len(session_log.actions_refused)}")
    print(f"  Validator runs: {len(session_log.validator_results)}")
    print(f"  Reports generated: {len(session_log.reports_generated)}")
    print(f"  Command packets prepared: {len(session_log.command_packets_prepared)}")
    print(f"  Artifacts inspected: {len(session_log.artifacts_inspected)}")
    print(f"  Errors: {len(session_log.errors)}")
    if session_log.last_action_name:
        print(f"  Last action: {session_log.last_action_name} [{session_log.last_action_status}]")
    if session_log.recommended_next_action:
        print(f"  Recommended next: {session_log.recommended_next_action}")
    print(f"  Boundary state: {session_log.final_boundary_state}")

    result = _make_result("show_session_state", "PASS", "Session state displayed")
    session_log.record_action("show_session_state", result)


def _load_artifact_inspector():
    path = HERE / "interface_artifact_inspector.py"
    spec = importlib.util.spec_from_file_location("interface_artifact_inspector", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_branch_review():
    path = HERE / "interface_branch_review.py"
    spec = importlib.util.spec_from_file_location("interface_branch_review", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_approval_ledger():
    path = HERE / "interface_approval_ledger.py"
    spec = importlib.util.spec_from_file_location("interface_approval_ledger", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def action_inspect_artifact_packages(session_log):
    _banner("INFO", "Deep artifact inspection...")
    inspector = _load_artifact_inspector()
    results = inspector.inspect_all_packages()

    counts = {"PASS": 0, "WARNING": 0, "MISSING": 0}
    for pid, result in results.items():
        st = result.get("status", "UNKNOWN")
        counts[st] = counts.get(st, 0) + 1
        print(f"  [{st}] {result['package_name']} ({pid})")
        print(f"        Files: {result.get('file_count', '?')}, "
              f"Dirs: {result.get('directory_count', '?')}, "
              f"Verdict: {result.get('final_verdict', 'not detected')}")
        if result.get("expected_files_missing"):
            print(f"        Missing: {', '.join(result['expected_files_missing'])}")
        if result.get("zero_byte_files"):
            print(f"        Zero-byte files: {len(result['zero_byte_files'])}")
        if result.get("warnings"):
            for w in result["warnings"]:
                print(f"        Warning: {w}")
        print()

    summary = f"{counts.get('PASS', 0)} PASS, {counts.get('WARNING', 0)} WARNING, {counts.get('MISSING', 0)} MISSING"
    _banner("INFO", f"Artifact inspection complete: {summary}")

    next_action = "Generate session report or show summaries."
    print(f"  Recommended next action: {next_action}")
    result_rec = _make_result("inspect_artifact_packages", "PASS",
                              f"Artifact inspection: {summary}",
                              recommended_next=next_action)
    session_log.record_action("inspect_artifact_packages", result_rec, next_action)


def action_prepare_branch_review(session_log, review_branch=None, base_branch="master"):
    _banner("INFO", "Preparing branch review packet...")
    brm = _load_branch_review()

    if not review_branch:
        print("  ERROR: Branch name required.")
        print("  Usage: --prepare-branch-review <branch-name> [base-branch]")
        return

    result = brm.prepare_branch_review(review_branch, base_branch)
    if result.get("status") == "FAIL":
        _banner("FAIL", f"Branch review failed: {result.get('error', 'unknown')}")
        return

    _banner("PASS", f"Branch review packet generated")
    print(f"  Review ID: {result['review_id']}")
    print(f"  Path: {result['review_path']}")
    print(f"  Risk level: {result['risk_level']}")
    print(f"  Changed files: {result['changed_files']}")
    print(f"  Decision: {result['decision']}")
    print("  Status: prepared_not_merged | Merge Performed: false")
    print("  Deployment Performed: false | Official Repo Touched: false")

    next_action = "Review the branch review packet, or run approval ledger."
    print(f"  Recommended next action: {next_action}")
    result_rec = _make_result("prepare_branch_review", "PASS",
                              f"Branch review: {result['review_id']}",
                              recommended_next=next_action)
    session_log.record_action("prepare_branch_review", result_rec, next_action)


def action_review_packet(session_log, packet_path_arg=None):
    _banner("INFO", "Reviewing command packet...")
    al = _load_approval_ledger()

    if not packet_path_arg:
        print("  ERROR: Packet path required.")
        print("  Usage: --review-packet <packet-path>")
        return

    result = al.review_packet(packet_path_arg)
    if result.get("status") == "FAIL":
        _banner("FAIL", f"Packet review failed: {result.get('error', 'unknown')}")
        return

    next_action = "Approve or reject the packet using --approve-packet or --reject-packet."
    print(f"  Recommended next action: {next_action}")
    result_rec = _make_result("review_packet", "PASS", "Packet reviewed",
                              recommended_next=next_action)
    session_log.record_action("review_packet_approval", result_rec, next_action)


def action_approve_packet(session_log, packet_path_arg=None, phrase=None):
    _banner("INFO", "Approving command packet...")
    al = _load_approval_ledger()

    if not packet_path_arg or not phrase:
        print("  ERROR: Packet path and approval phrase required.")
        print("  Usage: --approve-packet <packet-path> <approval-phrase>")
        return

    result = al.approve_packet(packet_path_arg, phrase)
    if result.get("status") == "FAIL":
        _banner("FAIL", f"Packet approval failed: {result.get('error', 'unknown')}")
        return

    next_action = "Check the approval ledger with --show-approval-ledger."
    print(f"  Recommended next action: {next_action}")
    result_rec = _make_result("approve_packet", result["status"],
                              "Packet approval processed",
                              recommended_next=next_action)
    session_log.record_action("review_packet_approval", result_rec, next_action)


def action_reject_packet(session_log, packet_path_arg=None, reason=None):
    _banner("INFO", "Rejecting command packet...")
    al = _load_approval_ledger()

    if not packet_path_arg:
        print("  ERROR: Packet path required.")
        print("  Usage: --reject-packet <packet-path> [reason]")
        return

    result = al.reject_packet(packet_path_arg, reason or "Rejected by operator via CLI.")
    if result.get("status") == "FAIL":
        _banner("FAIL", f"Packet rejection failed: {result.get('error', 'unknown')}")
        return

    next_action = "Check the approval ledger with --show-approval-ledger."
    print(f"  Recommended next action: {next_action}")
    result_rec = _make_result("reject_packet", "PASS", "Packet rejected",
                              recommended_next=next_action)
    session_log.record_action("review_packet_approval", result_rec, next_action)


def action_show_approval_ledger(session_log):
    _banner("INFO", "Approval ledger")
    al = _load_approval_ledger()
    al.show_ledger()

    next_action = "Review or approve/reject a packet."
    print(f"  Recommended next action: {next_action}")
    result_rec = _make_result("show_approval_ledger", "PASS", "Approval ledger displayed",
                              recommended_next=next_action)
    session_log.record_action("show_approval_ledger", result_rec, next_action)
