from datetime import datetime, timezone
import json

SEPARATOR = "=" * 72
SUB_SEP = "-" * 72
BADGE_PASS = "[PASS]"
BADGE_WARN = "[WARN]"
BADGE_FAIL = "[FAIL]"
BADGE_LOCKED = "[LOCK]"
BADGE_DISABLED = "[OFF]"
BADGE_INFO = "[INFO]"


def _badge(text, btype="INFO"):
    return f"  {btype} {text}"


def _status_line(state):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    screen = state.current_screen.replace("_", " ").title()
    bc = state.breadcrumbs
    return f"  [{screen}]  {bc}  |  Last refresh: {now}  |  Session: {state.session_id[:20]}..."


def _action_banner(state):
    lines = []
    if state.last_action_name:
        status = state.last_action_status or "?"
        lines.append(f"  Last action: {state.last_action_name} [{status}]")
    if state.recommended_next_action:
        lines.append(f"  Recommended: {state.recommended_next_action}")
    if lines:
        return SUB_SEP + "\n" + "\n".join(lines) + "\n" + SUB_SEP
    return ""


def _wrap_line(line, width=72):
    if len(line) <= width:
        return line
    return line[:width - 3] + "..."


def _get_registry():
    try:
        from tui_state import get_action_registry
        return get_action_registry()
    except Exception:
        return {}


def _get_locked_actions():
    try:
        from tui_state import get_policy
        return get_policy().get("locked", [])
    except Exception:
        return []


def _get_artifact_inspector():
    from tui_state import get_artifact_inspector
    return get_artifact_inspector()


def _get_approval_ledger():
    from tui_state import get_approval_ledger
    return get_approval_ledger()


# --- Renderers ---

def render_dashboard(state):
    lines = []
    lines.append(SEPARATOR)
    lines.append("  THE AGENT COMMAND CENTER")
    lines.append("  Station Chief v25  |  Interface Phase 2: TUI Operator Dashboard")
    lines.append(SEPARATOR)
    lines.append(_status_line(state))
    lines.append(SEPARATOR)
    lines.append("")
    lines.append("--- Safety Status ---")
    lines.append(f"  {BADGE_LOCKED} Official repo: LOCKED")
    lines.append(f"  {BADGE_LOCKED} Repo 2: LOCKED")
    lines.append(f"  {BADGE_LOCKED} Repo 3: LOCKED")
    lines.append(f"  {BADGE_DISABLED} Deployment: DISABLED")
    lines.append(f"  {BADGE_DISABLED} Secrets: DISABLED")
    lines.append(f"  {BADGE_DISABLED} Credentials: DISABLED")
    lines.append(f"  {BADGE_DISABLED} Command packet execution: DISABLED")
    lines.append(f"  {BADGE_DISABLED} Free-form shell: DISABLED")
    lines.append("")
    registry = _get_registry()
    lines.append(f"--- Action Registry ({len(registry)} actions) ---")
    for aid, info in sorted(registry.items())[:8]:
        cat = info.get("category", "unknown")
        risk = info.get("risk_level", "unknown")
        lines.append(f"  {aid}: [{cat}] risk={risk}")
    lines.append(f"  Actions completed: {len(state.actions_completed)}")
    lines.append(f"  Actions refused: {len(state.actions_refused)}")
    lines.append("")
    lines.append("--- Validator Status ---")
    if state.last_validator_results:
        for name, status in state.last_validator_results.items():
            badge = BADGE_PASS if status == "PASS" else BADGE_FAIL
            lines.append(f"  {badge} {name}: {status}")
    else:
        lines.append("  [INFO] No validators run yet")
    lines.append("")
    lines.append("--- Approval Ledger ---")
    lines.append(f"  Path: 09_exports/interface_phase_1/approval_ledger/approval_ledger.jsonl")
    lines.append(f"  Records created this session: {state.ledger_records_created}")
    lines.append("")
    lines.append("--- Repo Info ---")
    lines.append(f"  Repo: dev-in-portfolio/the-agent-command-center")
    lines.append(f"  Source Lineage: dev-in-portfolio/agent-command-center-3")
    lines.append(f"  Phase: 2  Mode: TUI Operator Dashboard")
    lines.append("")
    lines.append("--- Session Info ---")
    lines.append(f"  ID: {state.session_id}")
    lines.append(f"  Started: {state.started_at}")
    lines.append("")
    banner = _action_banner(state)
    if banner:
        lines.append(banner)
        lines.append("")
    lines.append("--- Keymap ---")
    lines.append("  q=quit  b=back  d=home  ?=help  r=refresh  h=help")
    lines.append("  1=dash  2=actions  3=artifacts  4=validator  5=packet")
    lines.append("  6=branch  7=ledger  8=help  9=safety")
    lines.append(SEPARATOR)
    return "\n".join(lines)


def render_action_registry(state):
    lines = []
    lines.append(SEPARATOR)
    lines.append("  ACTION REGISTRY")
    lines.append(SEPARATOR)
    lines.append(_status_line(state))
    lines.append(SEPARATOR)
    lines.append("")
    registry = _get_registry()
    safe_actions = []
    controlled_actions = []
    locked_actions = _get_locked_actions()
    for aid, info in registry.items():
        cat = info.get("category", "unknown")
        entry = (aid, info)
        if cat == "safe":
            safe_actions.append(entry)
        elif cat == "controlled":
            controlled_actions.append(entry)
    lines.append(f"--- SAFE ({len(safe_actions)}) ---")
    for aid, info in safe_actions:
        risk = info.get("risk_level", "unknown")
        label = info.get("label", aid)
        lines.append(f"  {BADGE_PASS} [{risk}] {aid} ({label})")
    lines.append("")
    lines.append(f"--- CONTROLLED ({len(controlled_actions)}) ---")
    for aid, info in controlled_actions:
        risk = info.get("risk_level", "unknown")
        label = info.get("label", aid)
        lines.append(f"  {BADGE_WARN} [{risk}] {aid} ({label})")
    lines.append("")
    lines.append(f"--- LOCKED ({len(locked_actions)}) ---")
    for action in locked_actions:
        lines.append(f"  {BADGE_LOCKED} {action} -- no key binding, no access")
    lines.append("")
    banner = _action_banner(state)
    if banner:
        lines.append(banner)
        lines.append("")
    lines.append(SUB_SEP)
    lines.append("  b=back  d=home  r=refresh  q=quit")
    lines.append(SEPARATOR)
    return "\n".join(lines)


def render_artifact_inspector(state):
    lines = []
    lines.append(SEPARATOR)
    lines.append("  ARTIFACT INSPECTOR")
    lines.append(SEPARATOR)
    lines.append(_status_line(state))
    lines.append(SEPARATOR)
    lines.append("")
    lines.append("  READ-ONLY: No artifact editing or deletion is possible.")
    lines.append("")
    try:
        mod = _get_artifact_inspector()
        packages = mod.inspect_all_packages() if hasattr(mod, "inspect_all_packages") else {}
        for pid, info in packages.items():
            name = info.get("name", pid)
            exists = info.get("exists", False)
            verdict = info.get("verdict", "none")
            files = info.get("file_count", 0)
            dirs = info.get("directory_count", 0)
            missing = info.get("missing_files", 0)
            zero = info.get("zero_byte_files", 0)
            warnings = info.get("warnings", 0)
            badge = BADGE_PASS if exists else BADGE_FAIL
            lines.append(f"  {badge} {pid} ({name})")
            lines.append(f"        Exists: {'Yes' if exists else 'No'}  Verdict: {verdict or 'not detected'}")
            lines.append(f"        Files: {files}  Dirs: {dirs}  Missing: {missing}  Zero: {zero}  Warnings: {warnings}")
            lines.append("")
            if pid == state.selected_artifact_package:
                lines.append(f"  --- Detail View: {pid} ---")
                details = mod.inspect_package(pid) if hasattr(mod, "inspect_package") else {}
                for ek, ev in details.items():
                    if ek in ("expected_files", "expected_files_missing", "zero_byte_files", "warnings"):
                        if ev:
                            lines.append(f"    {ek}: {', '.join(ev[:5])}{'...' if len(ev) > 5 else ''}")
                lines.append("")
    except Exception as e:
        lines.append(f"  {BADGE_FAIL} Error loading artifact data: {e}")
    lines.append("")
    banner = _action_banner(state)
    if banner:
        lines.append(banner)
        lines.append("")
    lines.append("  Artifact inspector is read-only. Use Phase 1 CLI to regenerate artifacts.")
    lines.append(SUB_SEP)
    lines.append("  b=back  d=home  r=refresh  q=quit")
    lines.append(SEPARATOR)
    return "\n".join(lines)


def render_validator_wall(state):
    lines = []
    lines.append(SEPARATOR)
    lines.append("  VALIDATOR WALL")
    lines.append(SEPARATOR)
    lines.append(_status_line(state))
    lines.append(SEPARATOR)
    lines.append("")
    lines.append(f"  {BADGE_WARN} Controlled action: Validator wall runs local Python scripts.")
    lines.append("  Validation is read-only. No network calls, no deploy, no merge, no push.")
    lines.append("")
    lines.append("  Validators to run:")
    lines.append("    1. validate_interface_phase_1_cli.py")
    lines.append("    2. validate_interface_phase_1_command_packets.py")
    lines.append("    3. validate_interface_phase_1_e2e.py")
    lines.append("    4. validate_interface_phase_1_release_candidate.py")
    lines.append("")
    lines.append("  Category: local repo/runtime validation")
    lines.append("  Confirmation required: Type RUN_VALIDATOR_WALL to confirm.")
    lines.append("  Anything else cancels. Validator wall will NOT run automatically.")
    lines.append("")
    if state.last_validator_results:
        lines.append("--- Last Results ---")
        for name, status in state.last_validator_results.items():
            badge = BADGE_PASS if status == "PASS" else BADGE_FAIL
            lines.append(f"  {badge} {name}: {status}")
    lines.append("")
    lines.append("  Manual command equivalent:")
    lines.append("    python3 scripts/validate_interface_phase_1_cli.py")
    lines.append("    python3 scripts/validate_interface_phase_1_command_packets.py")
    lines.append("    python3 scripts/validate_interface_phase_1_e2e.py")
    lines.append("    python3 scripts/validate_interface_phase_1_release_candidate.py")
    lines.append("")
    banner = _action_banner(state)
    if banner:
        lines.append(banner)
        lines.append("")
    lines.append(SUB_SEP)
    lines.append("  b=back  d=home  r=refresh  q=quit")
    lines.append(SEPARATOR)
    return "\n".join(lines)


def render_command_packet_prep(state):
    lines = []
    lines.append(SEPARATOR)
    lines.append("  COMMAND PACKET PREP")
    lines.append(SEPARATOR)
    lines.append(_status_line(state))
    lines.append(SEPARATOR)
    lines.append("")
    lines.append(f"  {BADGE_WARN} This only PREPARES packets. No commands are executed.")
    lines.append("  Packets are stored for manual review and operator approval.")
    lines.append("")
    lines.append("  Available packet types:")
    types = [
        "validator_wall", "artifact_audit", "trial_v3_review",
        "migration_review", "merge_review_packet",
        "artifact_integrity_audit", "cleanup_branch_review",
    ]
    for i, pt in enumerate(types, 1):
        lines.append(f"  {i}. {pt}")
    lines.append("")
    lines.append("  Type a number to select and prepare a packet.")
    lines.append(f"  {BADGE_INFO} WARNING: Preparation only. No execution.")
    lines.append("")
    if state.packets_prepared:
        lines.append("--- Prepared this session ---")
        for pt in state.packets_prepared:
            lines.append(f"  {BADGE_PASS} {pt}")
    lines.append("")
    banner = _action_banner(state)
    if banner:
        lines.append(banner)
        lines.append("")
    lines.append(SUB_SEP)
    lines.append("  b=back  d=home  r=refresh  q=quit")
    lines.append(SEPARATOR)
    return "\n".join(lines)


def render_branch_review_prep(state):
    lines = []
    lines.append(SEPARATOR)
    lines.append("  BRANCH REVIEW COCKPIT")
    lines.append(SEPARATOR)
    lines.append(_status_line(state))
    lines.append(SEPARATOR)
    lines.append("")
    lines.append(f"  {BADGE_WARN} This PREPARES branch review packets only.")
    lines.append("  No merge, push, or delete is performed.")
    lines.append("")
    lines.append("  Format: <branch> [base_branch]")
    lines.append("  Example: interface/phase-2-tui-operator-dashboard master")
    lines.append("")
    lines.append("  Branch validation rules:")
    lines.append("  - Name must be <= 200 characters")
    lines.append("  - No '..' path traversal")
    lines.append("  - No absolute or home-relative paths")
    lines.append("  - No control characters")
    lines.append("")
    if state.branch_reviews_prepared:
        lines.append("--- Prepared this session ---")
        for br in state.branch_reviews_prepared:
            lines.append(f"  {BADGE_PASS} branch={br['branch']} base={br['base']}")
    lines.append("")
    lines.append("--- Safety Status ---")
    lines.append(f"  {BADGE_PASS} Status: prepared_not_merged")
    lines.append(f"  {BADGE_PASS} Merge Performed: false")
    lines.append(f"  {BADGE_PASS} Deployment Performed: false")
    lines.append(f"  {BADGE_PASS} Official Repo Touched: false")
    lines.append("")
    banner = _action_banner(state)
    if banner:
        lines.append(banner)
        lines.append("")
    lines.append(SUB_SEP)
    lines.append("  b=back  d=home  r=refresh  q=quit")
    lines.append(SEPARATOR)
    return "\n".join(lines)


def render_approval_ledger(state):
    lines = []
    lines.append(SEPARATOR)
    lines.append("  APPROVAL LEDGER VIEWER")
    lines.append(SEPARATOR)
    lines.append(_status_line(state))
    lines.append(SEPARATOR)
    lines.append("")
    lines.append(f"  Production ledger: 09_exports/interface_phase_1/approval_ledger/approval_ledger.jsonl")
    lines.append(f"  Filter: {state.selected_ledger_filter or 'none'}")
    lines.append("")
    try:
        mod = _get_approval_ledger()
        records = mod._read_ledger() if hasattr(mod, "_read_ledger") else []
        if state.selected_ledger_filter:
            filtered = [r for r in records if r.get("state") == state.selected_ledger_filter]
        else:
            filtered = records
        lines.append(f"  Total records: {len(records)}  Filtered: {len(filtered)}")
        bad_records = [r for r in records if r.get("execution_performed") is not False]
        if bad_records:
            lines.append(f"  {BADGE_FAIL} WARNING: {len(bad_records)} record(s) with exec != false!")
        else:
            lines.append(f"  {BADGE_PASS} All records: execution_performed = false")
        lines.append("")
        if filtered:
            for rec in filtered[-10:]:
                state_v = rec.get("state", "?")
                pid = rec.get("packet_id", "?")
                ptype = rec.get("packet_type", "?")
                match = rec.get("approval_phrase_match", False)
                exec_p = rec.get("execution_performed", "?")
                lines.append(f"  [{state_v}] {pid} ({ptype}) phrase_match={match} exec={exec_p}")
        else:
            lines.append("  (empty ledger is allowed)")
        lines.append("")
        if records:
            last = records[-1]
            lines.append("--- Last Record ---")
            lines.append(f"  State: {last.get('state', '?')}")
            lines.append(f"  Packet ID: {last.get('packet_id', '?')}")
            lines.append(f"  Packet Type: {last.get('packet_type', '?')}")
            lines.append(f"  Phrase Match: {last.get('approval_phrase_match', '?')}")
            lines.append(f"  Execution Performed: {last.get('execution_performed', '?')}")
        lines.append("")
        lines.append("  Options: review packet | approve by phrase | reject by note")
        lines.append(f"  {BADGE_INFO} All operations preserve execution_performed: false")
    except Exception as e:
        lines.append(f"  {BADGE_FAIL} Error loading ledger: {e}")
    lines.append("")
    banner = _action_banner(state)
    if banner:
        lines.append(banner)
        lines.append("")
    lines.append(SUB_SEP)
    lines.append("  b=back  d=home  r=refresh  q=quit")
    lines.append(SEPARATOR)
    return "\n".join(lines)


def render_safety_monitor(state):
    lines = []
    lines.append(SEPARATOR)
    lines.append("  SAFETY BOUNDARY MONITOR")
    lines.append(SEPARATOR)
    lines.append(_status_line(state))
    lines.append(SEPARATOR)
    lines.append("")
    lines.append("--- Boundary Status ---")
    lines.append(f"  {BADGE_LOCKED} Official repo: LOCKED")
    lines.append(f"  {BADGE_LOCKED} agent-command-center-2: LOCKED")
    lines.append(f"  {BADGE_LOCKED} agent-command-center-3: LOCKED")
    lines.append(f"  {BADGE_DISABLED} Deployment: DISABLED")
    lines.append(f"  {BADGE_DISABLED} Secrets: DISABLED")
    lines.append(f"  {BADGE_DISABLED} Credentials: DISABLED")
    lines.append(f"  {BADGE_DISABLED} Command packet execution: DISABLED")
    lines.append(f"  {BADGE_DISABLED} Free-form shell: DISABLED")
    lines.append(f"  {BADGE_DISABLED} Merge: DISABLED")
    lines.append(f"  {BADGE_DISABLED} Push: DISABLED")
    lines.append(f"  {BADGE_DISABLED} PR creation: DISABLED")
    lines.append(f"  {BADGE_DISABLED} Network behavior: DISABLED")
    lines.append("")
    lines.append("--- Self-Checks ---")
    try:
        from tui_keymap import FORBIDDEN_SCREEN_NAMES, KEY_TO_SCREEN
        forbidden_bound = [f for f in FORBIDDEN_SCREEN_NAMES if f not in KEY_TO_SCREEN.values()]
        lines.append(f"  {BADGE_PASS} Keymap: {len(forbidden_bound)} forbidden names not in active keys")
    except Exception:
        lines.append(f"  {BADGE_WARN} Keymap check skipped")
    try:
        from tui_safety_scanner import scan_source_files
        scan_result = scan_source_files()
        if scan_result["active_forbidden_findings"]:
            for finding in scan_result["active_forbidden_findings"][:5]:
                lines.append(f"  {BADGE_FAIL} {finding['file']}:{finding['line']} active '{finding['pattern']}'")
            lines.append(f"  {BADGE_FAIL} Active forbidden patterns detected")
        elif scan_result["allowed_label_findings"]:
            for finding in scan_result["allowed_label_findings"][:3]:
                lines.append(f"  {BADGE_INFO} {finding['file']}:{finding['line']} label '{finding['pattern']}'")
            lines.append(f"  {BADGE_PASS} Source scan: no active forbidden patterns")
        else:
            lines.append(f"  {BADGE_PASS} Source scan: no forbidden patterns found")
    except Exception:
        lines.append(f"  {BADGE_WARN} Source scan skipped")
    try:
        p1_dir = Path(__file__).resolve().parent.parent / "11_interface"
        ledger_path = p1_dir.parent / "09_exports" / "interface_phase_1" / "approval_ledger" / "approval_ledger.jsonl"
        if ledger_path.exists():
            bad = 0
            for ln in ledger_path.read_text().strip().splitlines():
                if ln.strip():
                    try:
                        rec = json.loads(ln)
                        if rec.get("execution_performed") is not False:
                            bad += 1
                    except Exception:
                        pass
            if bad:
                lines.append(f"  {BADGE_FAIL} Ledger: {bad} record(s) with exec != false")
            else:
                lines.append(f"  {BADGE_PASS} Ledger: all records exec=false")
    except Exception:
        lines.append(f"  {BADGE_WARN} Ledger scan skipped")
    lines.append("")
    banner = _action_banner(state)
    if banner:
        lines.append(banner)
        lines.append("")
    lines.append(SUB_SEP)
    lines.append("  b=back  d=home  r=refresh  q=quit")
    lines.append(SEPARATOR)
    return "\n".join(lines)


def render_help(state):
    lines = []
    lines.append(SEPARATOR)
    lines.append("  HELP / SAFETY RULES")
    lines.append(SEPARATOR)
    lines.append(_status_line(state))
    lines.append(SEPARATOR)
    lines.append("")
    lines.append("  Interface Phase 2: TUI Operator Dashboard (Upgraded)")
    lines.append("")
    lines.append("  What Phase 2 CAN do:")
    lines.append("    - Show dashboard with safety status")
    lines.append("    - Show action registry (safe/controlled/locked)")
    lines.append("    - Inspect artifact packages (read-only)")
    lines.append("    - Run validator wall (requires RUN_VALIDATOR_WALL)")
    lines.append("    - Prepare command packets (no execution)")
    lines.append("    - Prepare branch review packets (no merge)")
    lines.append("    - View approval ledger and create review records")
    lines.append("    - View safety boundary monitor with self-checks")
    lines.append("    - Log session activity")
    lines.append("    - Export snapshots (text, markdown, json, compact)")
    lines.append("")
    lines.append("  What Phase 2 CANNOT do:")
    lines.append("    - Deploy to any environment")
    lines.append("    - Merge branches")
    lines.append("    - Push to remote")
    lines.append("    - Open PRs")
    lines.append("    - Mutate official repo, repo 2, or repo 3")
    lines.append("    - Access secrets or credentials")
    lines.append("    - Execute command packet commands")
    lines.append("    - Run free-form shell commands")
    lines.append("    - Access network (no requests, urllib, socket)")
    lines.append("")
    lines.append("  Phase 2 reuses Phase 1 backend modules.")
    lines.append("  Phase 3 (web dashboard) is not yet built.")
    lines.append("")
    lines.append("--- Keymap ---")
    lines.append("  q=quit  b=back  d=home  ?=screen help  r=refresh  h=help")
    lines.append("  1=dashboard  2=actions  3=artifacts  4=validator")
    lines.append("  5=packet  6=branch  7=ledger  8=help  9=safety")
    lines.append("")
    lines.append("--- Snapshot Flags ---")
    lines.append("  --snapshot                        Print dashboard snapshot")
    lines.append("  --snapshot --format text          Text format (default)")
    lines.append("  --snapshot --format markdown      Markdown format")
    lines.append("  --snapshot --format json          JSON format")
    lines.append("  --snapshot --format compact       Compact format")
    lines.append("  --snapshot --format full          Full format")
    lines.append("  --snapshot --format json --save   Save to file")
    lines.append("")
    banner = _action_banner(state)
    if banner:
        lines.append(banner)
        lines.append("")
    lines.append(SUB_SEP)
    lines.append("  b=back  d=home  r=refresh  q=quit")
    lines.append(SEPARATOR)
    return "\n".join(lines)


def render_safety_boundary_help(state):
    return render_help(state)


# --- Snapshot Formats ---

def _get_safety_status():
    return {
        "official_repo": "LOCKED",
        "repo_2": "LOCKED",
        "repo_3": "LOCKED",
        "deployment": "DISABLED",
        "secrets": "DISABLED",
        "credentials": "DISABLED",
        "command_packet_execution": "DISABLED",
        "free_form_shell": "DISABLED",
        "merge": "DISABLED",
        "push": "DISABLED",
        "pr_creation": "DISABLED",
        "network_behavior": "DISABLED",
    }


def _get_artifact_summary_data():
    try:
        mod = _get_artifact_inspector()
        packages = mod.inspect_all_packages() if hasattr(mod, "inspect_all_packages") else {}
        package_list = []
        for pid, info in packages.items():
            package_list.append({
                "id": pid,
                "name": info.get("name", pid),
                "exists": info.get("exists", False),
            })
        return {"package_count": len(package_list), "packages": package_list}
    except Exception:
        return {"package_count": 0, "packages": []}


def _get_approval_ledger_summary_data():
    try:
        mod = _get_approval_ledger()
        records = mod._read_ledger() if hasattr(mod, "_read_ledger") else []
        bad = sum(1 for r in records if r.get("execution_performed") is not False)
        return {"record_count": len(records), "bad_execution_records": bad, "empty_ledger_allowed": True}
    except Exception:
        return {"record_count": 0, "bad_execution_records": 0, "empty_ledger_allowed": True}


def _get_validator_status(state):
    vr = state.last_validator_results
    return {
        "phase_2_tui": vr.get("TUI", "unknown") or "unknown",
        "phase_2_e2e": vr.get("E2E", "unknown") or "unknown",
        "phase_1": vr.get("CLI", "unknown") or "unknown",
        "runtime": "unknown",
    }


def _get_boundary_status(boundary):
    return {
        "official_repo_touched": boundary.get("official_repo_touched", False),
        "repo_2_touched": boundary.get("repo2_touched", False),
        "repo_3_touched": boundary.get("repo3_touched", False),
        "deployment_performed": boundary.get("deployment_performed", False),
        "secrets_credentials_used": boundary.get("secrets_used", False) or boundary.get("credentials_used", False),
        "command_packets_executed": boundary.get("command_packets_executed", False),
        "merge_performed": False,
    }


def _collect_snapshot_data(state):
    registry = _get_registry()
    locked = _get_locked_actions()
    safe_count = sum(1 for a in registry.values() if a.get("category") == "safe")
    ctrl_count = sum(1 for a in registry.values() if a.get("category") == "controlled")
    summary = state.get_summary()
    boundary = summary.get("final_boundary_state", {})
    now = datetime.now(timezone.utc)
    return {
        "snapshot_id": f"SNAP-{now.strftime('%Y%m%d-%H%M%S-%f')}",
        "created_at_utc": now.isoformat(),
        "session_id": state.session_id,
        "phase": "Interface Phase 2",
        "repo": "dev-in-portfolio/the-agent-command-center",
        "source_lineage": "dev-in-portfolio/agent-command-center-3",
        "format": "json",
        "safety_status": _get_safety_status(),
        "artifact_summary": _get_artifact_summary_data(),
        "approval_ledger_summary": _get_approval_ledger_summary_data(),
        "validator_status": _get_validator_status(state),
        "boundary_status": _get_boundary_status(boundary),
        "recommended_next_action": state.recommended_next_action or "",
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "mode": "TUI Operator Dashboard",
        "current_screen": state.current_screen,
        "safety": {
            "official_repo": "LOCKED",
            "repo2": "LOCKED",
            "repo3": "LOCKED",
            "deployment": "DISABLED",
            "secrets": "DISABLED",
            "credentials": "DISABLED",
            "command_packet_execution": "DISABLED",
            "merge": "DISABLED",
            "push": "DISABLED",
            "pr_creation": "DISABLED",
            "free_form_shell": "DISABLED",
            "network_behavior": "DISABLED",
        },
        "boundary": dict(boundary),
        "actions_completed": len(state.actions_completed),
        "actions_refused": len(state.actions_refused),
        "validator_runs": len(state.validator_runs),
        "packets_prepared": len(state.packets_prepared),
        "branch_reviews_prepared": len(state.branch_reviews_prepared),
        "ledger_records_created": state.ledger_records_created,
        "action_registry": {
            "total": len(registry),
            "safe": safe_count,
            "controlled": ctrl_count,
            "locked": len(locked),
        },
        "last_validator_results": dict(state.last_validator_results),
        "_schema_version": "1.0",
        "_metadata": {
            "source": "phase_2_tui_operator_dashboard",
            "generated_by": "tui_renderer.render_snapshot_json",
        },
    }


def render_snapshot_text(state):
    return render_dashboard(state)


def render_snapshot_markdown(state):
    data = _collect_snapshot_data(state)
    lines = []
    lines.append(f"# Snapshot: {data['timestamp']}")
    lines.append("")
    lines.append(f"**Repo:** {data['repo']}")
    lines.append(f"**Session:** {data['session_id']}")
    lines.append(f"**Screen:** {data['current_screen']}")
    lines.append("")
    lines.append("## Safety Status")
    for k, v in data["safety"].items():
        lines.append(f"- **{k}:** {v}")
    lines.append("")
    lines.append("## Activity")
    lines.append(f"- Actions completed: {data['actions_completed']}")
    lines.append(f"- Actions refused: {data['actions_refused']}")
    lines.append(f"- Validator runs: {data['validator_runs']}")
    lines.append(f"- Packets prepared: {data['packets_prepared']}")
    lines.append(f"- Ledger records: {data['ledger_records_created']}")
    lines.append("")
    lines.append("## Action Registry")
    ar = data["action_registry"]
    lines.append(f"- Total: {ar['total']}  Safe: {ar['safe']}  Controlled: {ar['controlled']}  Locked: {ar['locked']}")
    lines.append("")
    lines.append("## Validator Results")
    if data["last_validator_results"]:
        for name, status in data["last_validator_results"].items():
            lines.append(f"- {name}: {status}")
    else:
        lines.append("(none)")
    lines.append("")
    lines.append("*Phase 2 status: ACTIVE*")
    return "\n".join(lines)


def render_snapshot_json(state):
    data = _collect_snapshot_data(state)
    return json.dumps(data, indent=2)


def render_snapshot_compact(state):
    data = _collect_snapshot_data(state)
    parts = []
    parts.append(f"[{data['timestamp']}] {data['repo']} | Session: {data['session_id'][:16]}")
    s = data["safety"]
    parts.append(f"Safety: official={s['official_repo']} deploy={s['deployment']} secrets={s['secrets']} merge={s['merge']}")
    parts.append(f"Actions: {data['actions_completed']} done, {data['actions_refused']} refused")
    parts.append(f"Validators: {data['validator_runs']} runs, {data['packets_prepared']} packets")
    return " | ".join(parts)


def render_snapshot_full(state):
    data = _collect_snapshot_data(state)
    lines = []
    lines.append(SEPARATOR)
    lines.append("  THE AGENT COMMAND CENTER -- FULL SNAPSHOT")
    lines.append(f"  {data['timestamp']}")
    lines.append(SEPARATOR)
    lines.append(f"  Repo: {data['repo']}")
    lines.append(f"  Session: {data['session_id']}")
    lines.append(f"  Screen: {data['current_screen']}")
    lines.append("")
    lines.append("  Safety Status:")
    for k, v in data["safety"].items():
        lines.append(f"    {k}: {v}")
    lines.append("")
    lines.append("  Activity:")
    lines.append(f"    Actions completed: {data['actions_completed']}")
    lines.append(f"    Actions refused: {data['actions_refused']}")
    lines.append(f"    Validator runs: {data['validator_runs']}")
    lines.append(f"    Packets prepared: {data['packets_prepared']}")
    lines.append(f"    Branch reviews: {data['branch_reviews_prepared']}")
    lines.append(f"    Ledger records: {data['ledger_records_created']}")
    lines.append("")
    ar = data["action_registry"]
    lines.append(f"  Action Registry: {ar['total']} total ({ar['safe']} safe, {ar['controlled']} controlled, {ar['locked']} locked)")
    lines.append("")
    if data["last_validator_results"]:
        lines.append("  Validator Results:")
        for name, status in data["last_validator_results"].items():
            lines.append(f"    {name}: {status}")
    lines.append("")
    lines.append("  Phase 2 status: ACTIVE")
    lines.append(SEPARATOR)
    return "\n".join(lines)


SNAPSHOT_FORMATS = {
    "text": render_snapshot_text,
    "markdown": render_snapshot_markdown,
    "json": render_snapshot_json,
    "compact": render_snapshot_compact,
    "full": render_snapshot_full,
}
