from datetime import datetime, timezone

SEPARATOR = "=" * 72
SUB_SEP = "-" * 72


def render_dashboard(state):
    lines = []
    lines.append(SEPARATOR)
    lines.append("  THE AGENT COMMAND CENTER")
    lines.append("  Station Chief v25")
    lines.append("  Interface Phase 2: TUI Operator Dashboard")
    lines.append(f"  Repo: dev-in-portfolio/the-agent-command-center")
    lines.append(f"  Source Lineage: dev-in-portfolio/agent-command-center-3")
    lines.append(f"  Session: {state.session_id}")
    lines.append(SEPARATOR)
    lines.append("")
    lines.append("--- Safety Status ---")
    lines.append("  Official repo: LOCKED")
    lines.append("  Repo 2: LOCKED")
    lines.append("  Repo 3: LOCKED")
    lines.append("  Deployment: DISABLED")
    lines.append("  Secrets: DISABLED")
    lines.append("  Credentials: DISABLED")
    lines.append("  Command packet execution: DISABLED")
    lines.append("  Free-form shell: DISABLED")
    lines.append("")
    registry = _get_registry()
    lines.append(f"--- Action Registry ({len(registry)} actions) ---")
    for aid, info in sorted(registry.items())[:8]:
        cat = info.get("category", "unknown")
        risk = info.get("risk_level", "unknown")
        lines.append(f"  {aid}: [{cat}] risk={risk}")
    active = len(state.actions_completed)
    refused = len(state.actions_refused)
    lines.append(f"  Actions completed: {active}")
    lines.append(f"  Actions refused: {refused}")
    lines.append("")
    lines.append("--- Validator Status ---")
    if state.last_validator_results:
        for name, status in state.last_validator_results.items():
            lines.append(f"  {name}: {status}")
    else:
        lines.append("  (no validators run yet)")
    lines.append("")
    lines.append("--- Approval Ledger ---")
    lines.append(f"  Path: 09_exports/interface_phase_1/approval_ledger/approval_ledger.jsonl")
    lines.append(f"  Records created this session: {state.ledger_records_created}")
    lines.append("")
    lines.append("--- Session Info ---")
    lines.append(f"  ID: {state.session_id}")
    lines.append(f"  Started: {state.started_at}")
    lines.append("")
    lines.append("--- Keymap ---")
    lines.append("  q=quit  1=dashboard  2=actions  3=artifacts  4=validator")
    lines.append("  5=packet  6=branch review  7=ledger  8=help  r=refresh")
    lines.append(SEPARATOR)
    return "\n".join(lines)


def render_action_registry(state):
    lines = []
    lines.append(SEPARATOR)
    lines.append("  ACTION REGISTRY")
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
    lines.append("--- SAFE ---")
    for aid, info in safe_actions:
        risk = info.get("risk_level", "unknown")
        label = info.get("label", aid)
        lines.append(f"  [{risk}] {aid} ({label})")
    lines.append("")
    lines.append("--- CONTROLLED ---")
    for aid, info in controlled_actions:
        risk = info.get("risk_level", "unknown")
        label = info.get("label", aid)
        lines.append(f"  [{risk}] {aid} ({label})")
    lines.append("")
    lines.append("--- LOCKED (refused by policy) ---")
    for action in locked_actions:
        lines.append(f"  {action} -- no key binding, no access")
    lines.append("")
    lines.append(SUB_SEP)
    lines.append("  q=back  r=refresh")
    lines.append(SEPARATOR)
    return "\n".join(lines)


def render_artifact_inspector(state):
    lines = []
    lines.append(SEPARATOR)
    lines.append("  ARTIFACT INSPECTOR")
    lines.append(SEPARATOR)
    lines.append("")
    try:
        mod = _get_artifact_inspector()
        packages = mod.inspect_all_packages() if hasattr(mod, "inspect_all_packages") else {}
        for pid, info in packages.items():
            name = info.get("name", pid)
            exists = info.get("exists", False)
            verdict = info.get("verdict", "none")
            missing = info.get("missing_files", 0)
            zero = info.get("zero_byte_files", 0)
            warnings = info.get("warnings", 0)
            exists_str = "Y" if exists else "N"
            lines.append(f"  {pid}: exists={exists_str} verdict={verdict} missing={missing} zero={zero} warnings={warnings}")
    except Exception as e:
        lines.append(f"  (error loading artifact data: {e})")
    lines.append("")
    lines.append(SUB_SEP)
    lines.append("  q=back  r=refresh")
    lines.append(SEPARATOR)
    return "\n".join(lines)


def render_validator_wall(state):
    lines = []
    lines.append(SEPARATOR)
    lines.append("  VALIDATOR WALL")
    lines.append(SEPARATOR)
    lines.append("")
    lines.append("  WARNING: Validator wall may depend on local repo/runtime state.")
    lines.append("  This action runs local Python scripts only. No network calls.")
    lines.append("")
    lines.append("  Validators to run:")
    lines.append("    1. validate_interface_phase_1_cli.py")
    lines.append("    2. validate_interface_phase_1_command_packets.py")
    lines.append("    3. validate_interface_phase_1_e2e.py")
    lines.append("    4. validate_interface_phase_1_release_candidate.py")
    lines.append("")
    lines.append("  Type RUN_VALIDATOR_WALL to confirm, or anything else to cancel.")
    lines.append("")
    if state.last_validator_results:
        lines.append("--- Last Results ---")
        for name, status in state.last_validator_results.items():
            lines.append(f"  {name}: {status}")
    lines.append("")
    lines.append(SUB_SEP)
    lines.append("  q=back  r=refresh")
    lines.append(SEPARATOR)
    return "\n".join(lines)


def render_command_packet_prep(state):
    lines = []
    lines.append(SEPARATOR)
    lines.append("  COMMAND PACKET PREP")
    lines.append(SEPARATOR)
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
    lines.append("  WARNING: This only PREPARES the packet. No commands are executed.")
    lines.append("")
    if state.packets_prepared:
        lines.append("--- Prepared this session ---")
        for pt in state.packets_prepared:
            lines.append(f"  {pt}")
    lines.append("")
    lines.append(SUB_SEP)
    lines.append("  q=back  r=refresh")
    lines.append(SEPARATOR)
    return "\n".join(lines)


def render_branch_review_prep(state):
    lines = []
    lines.append(SEPARATOR)
    lines.append("  BRANCH REVIEW PREP")
    lines.append(SEPARATOR)
    lines.append("")
    lines.append("  Prepare a branch review packet.")
    lines.append("  This creates a review packet at 09_exports/interface_phase_1/branch_reviews/")
    lines.append("  No merge, push, or delete is performed.")
    lines.append("")
    lines.append("  Format: <branch> [base_branch]")
    lines.append("  Example: interface/phase-2-tui-operator-dashboard master")
    lines.append("")
    if state.branch_reviews_prepared:
        lines.append("--- Prepared this session ---")
        for br in state.branch_reviews_prepared:
            lines.append(f"  branch={br['branch']} base={br['base']}")
    lines.append("")
    lines.append(SUB_SEP)
    lines.append("  q=back  r=refresh")
    lines.append(SEPARATOR)
    return "\n".join(lines)


def render_approval_ledger(state):
    lines = []
    lines.append(SEPARATOR)
    lines.append("  APPROVAL LEDGER")
    lines.append(SEPARATOR)
    lines.append("")
    lines.append("  Production ledger: 09_exports/interface_phase_1/approval_ledger/approval_ledger.jsonl")
    lines.append("")
    try:
        mod = _get_approval_ledger()
        records = mod._read_ledger() if hasattr(mod, "_read_ledger") else []
        lines.append(f"  Record count: {len(records)}")
        if records:
            last = records[-1]
            lines.append(f"  Last record:")
            lines.append(f"    state: {last.get('state', 'unknown')}")
            lines.append(f"    packet_id: {last.get('packet_id', 'unknown')}")
            lines.append(f"    execution_performed: {last.get('execution_performed', 'unknown')}")
            all_exec_false = all(r.get("execution_performed") is False for r in records)
            lines.append(f"  All records exec=false: {all_exec_false}")
        else:
            lines.append("  (empty ledger is allowed)")
        lines.append("")
        lines.append("  Options: review packet | approve by phrase | reject by note")
        lines.append("  All operations preserve execution_performed: false")
    except Exception as e:
        lines.append(f"  (error loading ledger: {e})")
    lines.append("")
    lines.append(SUB_SEP)
    lines.append("  q=back  r=refresh")
    lines.append(SEPARATOR)
    return "\n".join(lines)


def render_help(state):
    lines = []
    lines.append(SEPARATOR)
    lines.append("  HELP / SAFETY RULES")
    lines.append(SEPARATOR)
    lines.append("")
    lines.append("  Interface Phase 2: TUI Operator Dashboard")
    lines.append("")
    lines.append("  What Phase 2 CAN do:")
    lines.append("    - Show dashboard with safety status")
    lines.append("    - Show action registry (safe/controlled/locked)")
    lines.append("    - Inspect artifact packages (read-only)")
    lines.append("    - Run validator wall (controlled, requires confirmation)")
    lines.append("    - Prepare command packets (controlled, no execution)")
    lines.append("    - Prepare branch review packets (controlled, no merge)")
    lines.append("    - View approval ledger and create review records")
    lines.append("    - Log session activity")
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
    lines.append(SUB_SEP)
    lines.append("  q=back  r=refresh  h=help")
    lines.append(SEPARATOR)
    return "\n".join(lines)


def render_snapshot(state):
    lines = []
    lines.append(SEPARATOR)
    lines.append("  THE AGENT COMMAND CENTER -- SNAPSHOT")
    lines.append(f"  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append(SEPARATOR)
    lines.append("  Repo: dev-in-portfolio/the-agent-command-center")
    lines.append("  Interface Phase 2: TUI Operator Dashboard")
    lines.append("")
    lines.append("  Safety Status:")
    lines.append("    Official repo: LOCKED")
    lines.append("    Repo 2: LOCKED")
    lines.append("    Repo 3: LOCKED")
    lines.append("    Deployment: DISABLED")
    lines.append("    Secrets: DISABLED")
    lines.append("    Credentials: DISABLED")
    lines.append("    Command packet execution: DISABLED")
    lines.append("    Free-form shell: DISABLED")
    lines.append("")
    registry = _get_registry()
    lines.append(f"  Registered actions: {len(registry)}")
    safe_count = sum(1 for a in registry.values() if a.get("category") == "safe")
    ctrl_count = sum(1 for a in registry.values() if a.get("category") == "controlled")
    locked = _get_locked_actions()
    lines.append(f"    Safe: {safe_count}  Controlled: {ctrl_count}  Locked: {len(locked)}")
    lines.append("")
    lines.append("  Approval Ledger:")
    lines.append(f"    Records this session: {state.ledger_records_created}")
    lines.append("")
    lines.append("  Session:")
    lines.append(f"    ID: {state.session_id}")
    lines.append(f"    Actions completed: {len(state.actions_completed)}")
    lines.append(f"    Actions refused: {len(state.actions_refused)}")
    lines.append("")
    lines.append("  Locked actions summary:")
    for action in locked[:8]:
        lines.append(f"    {action}")
    lines.append("")
    lines.append("  Phase 2 status: ACTIVE. No curses required for snapshot.")
    lines.append(SEPARATOR)
    return "\n".join(lines)


def render_plain_text_dashboard(state):
    return render_dashboard(state)


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
