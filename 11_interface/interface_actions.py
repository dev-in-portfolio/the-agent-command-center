import subprocess
import sys
import importlib.util
from pathlib import Path
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCRIPTS = ROOT / "scripts"
EXPORTS = ROOT / "09_exports"
INTERFACE_EXPORTS = EXPORTS / "interface_phase_1"
COMMAND_PACKETS = INTERFACE_EXPORTS / "command_packets"
REPO_NAME = "dev-in-portfolio/the-agent-command-center"
SOURCE_LINEAGE = "dev-in-portfolio/agent-command-center-3"


def _load_policy():
    path = HERE / "interface_policy.py"
    spec = importlib.util.spec_from_file_location("interface_policy", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_session_log():
    path = HERE / "interface_session_log.py"
    spec = importlib.util.spec_from_file_location("interface_session_log", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_policy = _load_policy()
LOCKED_ACTIONS = _policy.LOCKED_ACTIONS
LOCKED_ACTION_LABELS = _policy.LOCKED_ACTION_LABELS


def action_show_status(session_log):
    lines = []
    lines.append("=== System Status ===")
    lines.append(f"Product repo: {REPO_NAME}")
    lines.append(f"Source lineage: {SOURCE_LINEAGE}")
    lines.append("Runtime version expected: 25.0.0")
    lines.append("Repo role: product/interface workspace")
    lines.append("Official repo status: locked / not touched")
    lines.append("Repo 2 status: locked / not touched")
    lines.append("Repo 3 status: source lineage only / not mutated")
    lines.append("Deployment: disabled")
    lines.append("Secrets: disabled")
    lines.append("Credentials: disabled")
    lines.append("Promotion: disabled")
    lines.append("Interface phase: 1")
    lines.append("Mode: CLI operator console")
    lines.append("")
    print("\n".join(lines))
    session_log.record_action("show_status")


def action_run_validator_wall(session_log):
    print("=== Validator Wall ===")
    validators = [
        ("auto-self-improve-2", SCRIPTS / "validate_auto_self_improve_2.py"),
        ("station-chief-runtime-v25-0", SCRIPTS / "validate_station_chief_runtime_v25_0.py"),
        ("station-chief-runtime-v24-0", SCRIPTS / "validate_station_chief_runtime_v24_0.py"),
    ]
    all_passed = True
    for name, path in validators:
        if not path.exists():
            print(f"  [SKIP] {name}: script not found at {path}")
            session_log.record_validator_result(name, -1, "script not found", datetime.now(timezone.utc).isoformat())
            all_passed = False
            continue
        print(f"  Running {name}...")
        ts = datetime.now(timezone.utc).isoformat()
        try:
            result = subprocess.run(
                [sys.executable, str(path)],
                capture_output=True, text=True, timeout=120
            )
            passed = result.returncode == 0
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {name} (rc={result.returncode})")
            if result.stdout:
                for line in result.stdout.strip().splitlines():
                    print(f"    {line}")
            if result.stderr:
                for line in result.stderr.strip().splitlines():
                    print(f"    stderr: {line}")
            session_log.record_validator_result(name, result.returncode, result.stdout, ts)
            if not passed:
                all_passed = False
        except subprocess.TimeoutExpired:
            print(f"  [TIMEOUT] {name}")
            session_log.record_validator_result(name, -1, "timeout", ts)
            all_passed = False
        except Exception as e:
            print(f"  [ERROR] {name}: {e}")
            session_log.record_validator_result(name, -1, str(e), ts)
            all_passed = False
    print(f"\nValidator wall result: {'ALL PASS' if all_passed else 'SOME FAILED'}")
    session_log.record_action("run_validator_wall")


def action_list_artifact_packages(session_log):
    print("=== Artifact Packages ===")
    packages = [
        ("100_round_trial_v3", EXPORTS / "100_round_trial_v3"),
        ("non_repo_gauntlet_001", EXPORTS / "non_repo_gauntlet_001"),
        ("repo_migration", EXPORTS / "repo_migration"),
        ("interface_phase_1", INTERFACE_EXPORTS),
    ]
    for label, path in packages:
        exists = path.exists()
        if exists:
            files = list(path.rglob("*"))
            file_count = len(files)
            key_reports = sorted(
                [str(f.relative_to(EXPORTS)) for f in files
                 if f.suffix in (".md", ".json") and f.parent == path]
            )
            print(f"  {label}:")
            print(f"    Exists: yes")
            print(f"    File count: {file_count}")
            if key_reports:
                print(f"    Key reports:")
                for kr in key_reports[:5]:
                    print(f"      - {kr}")
                if len(key_reports) > 5:
                    print(f"      ... and {len(key_reports) - 5} more")
        else:
            print(f"  {label}: not present")
    session_log.record_action("list_artifacts")


def action_show_summaries(session_log):
    print("=== Latest Trial / Gauntlet Summaries ===")
    reports = [
        ("100-round trial v3", EXPORTS / "100_round_trial_v3" / "final_100_round_trial_v3_acceptance_report.md"),
        ("non-repo gauntlet #1", EXPORTS / "non_repo_gauntlet_001" / "final_non_repo_gauntlet_001_acceptance_report.md"),
        ("repo migration", EXPORTS / "repo_migration" / "the_agent_command_center_migration_report.md"),
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
    session_log.record_action("show_summaries")


def action_generate_session_report(session_log):
    print("=== Generate Operator Session Report ===")
    INTERFACE_EXPORTS.mkdir(parents=True, exist_ok=True)
    session_log.close()
    report = session_log.generate_report()
    report_path = INTERFACE_EXPORTS / "operator_session_report.md"
    report_path.write_text(report)
    session_log.record_report(str(report_path))
    print(f"  Session report written: {report_path}")
    session_log.record_action("generate_session_report")


def action_show_locked_actions(session_log):
    print("=== Locked Actions ===")
    print("  The following actions are permanently locked and cannot be performed:")
    for action_key in LOCKED_ACTIONS:
        label = LOCKED_ACTION_LABELS.get(action_key, action_key)
        print(f"    - {label}")
    print("")
    print("  Interface Phase 1 refuses all locked actions.")
    print("  No bypass, override, or escalation path exists.")
    session_log.record_action("show_locked_actions")


def action_prepare_command_packet(session_log):
    print("=== Prepare Command Packet ===")
    print("\n  Select packet type:")
    packet_types = [
        "validator_wall",
        "artifact_audit",
        "non_repo_gauntlet_review",
        "trial_v3_review",
        "migration_review",
        "merge_review_packet",
    ]
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

    allowed_actions = []
    forbidden_actions = []
    exact_commands = []

    if packet_type == "validator_wall":
        purpose = "Run all three validators to confirm system integrity before any operation."
        scope = "scripts/validate_auto_self_improve_2.py, validate_station_chief_runtime_v25_0.py, validate_station_chief_runtime_v24_0.py"
        allowed_actions = ["Run validator wall from CLI menu option 2"]
        forbidden_actions = ["Skip validation", "Ignore failures", "Modify validators"]
        exact_commands = [
            "python3 scripts/validate_auto_self_improve_2.py",
            "python3 scripts/validate_station_chief_runtime_v25_0.py",
            "python3 scripts/validate_station_chief_runtime_v24_0.py",
        ]
    elif packet_type == "artifact_audit":
        purpose = "Audit all artifact packages for completeness, integrity, and stale claims."
        scope = "09_exports/100_round_trial_v3/, 09_exports/non_repo_gauntlet_001/"
        allowed_actions = [
            "List artifact packages from CLI menu option 3",
            "Inspect key report files",
        ]
        forbidden_actions = ["Modify artifacts during audit", "Delete reports", "Skip missing file checks"]
        exact_commands = [
            "python3 scripts/validate_exports.py",
            "ls -la 09_exports/100_round_trial_v3/",
            "ls -la 09_exports/non_repo_gauntlet_001/",
        ]
    elif packet_type == "non_repo_gauntlet_review":
        purpose = "Review non-repo extreme work gauntlet #1 outputs and final verdict."
        scope = "09_exports/non_repo_gauntlet_001/"
        allowed_actions = [
            "View executive summary",
            "Inspect task outputs",
            "Review hallucination audit",
            "Review completeness audit",
        ]
        forbidden_actions = ["Regenerate artifacts", "Modify acceptance report", "Delete audit trails"]
        exact_commands = [
            "cat 09_exports/non_repo_gauntlet_001/outputs/executive_summary_packet.md",
            "cat 09_exports/non_repo_gauntlet_001/final_non_repo_gauntlet_001_acceptance_report.md",
        ]
    elif packet_type == "trial_v3_review":
        purpose = "Review 100-round trial v3 evidence and acceptance verdict."
        scope = "09_exports/100_round_trial_v3/"
        allowed_actions = [
            "View final acceptance report",
            "Inspect scoreboard",
            "Inspect audit log",
        ]
        forbidden_actions = ["Regenerate rounds", "Modify evidence files", "Alter scoreboard"]
        exact_commands = [
            "cat 09_exports/100_round_trial_v3/final_100_round_trial_v3_acceptance_report.md",
            "cat 09_exports/100_round_trial_v3/master_scoreboard.md",
        ]
    elif packet_type == "migration_review":
        purpose = "Review repo migration report for The Agent Command Center."
        scope = "09_exports/repo_migration/"
        allowed_actions = [
            "View migration report",
            "Confirm source lineage",
            "Check preserved evidence",
        ]
        forbidden_actions = ["Revert migration", "Delete migration report", "Modify source remote"]
        exact_commands = [
            "cat 09_exports/repo_migration/the_agent_command_center_migration_report.md",
            "git remote -v",
        ]
    elif packet_type == "merge_review_packet":
        purpose = "Review changeset before merging a branch into master."
        scope = "Full repo diff against base branch"
        allowed_actions = [
            "View diff",
            "Check for unexpected file changes",
            "Run validator wall",
        ]
        forbidden_actions = ["Merge without review", "Skip validators", "Force push"]
        exact_commands = [
            "git diff --name-only master..HEAD",
            "git diff master..HEAD --stat",
            "python3 scripts/validate_auto_self_improve_2.py",
        ]

    lines = []
    lines.append(f"# Command Packet: {packet_type}")
    lines.append("")
    lines.append("**Status:** prepared_not_executed")
    lines.append(f"**Purpose:** {purpose}")
    lines.append(f"**Scope:** {scope}")
    lines.append("")
    lines.append("## Allowed Actions")
    for a in allowed_actions:
        lines.append(f"- {a}")
    lines.append("")
    lines.append("## Forbidden Actions")
    for f in forbidden_actions:
        lines.append(f"- {f}")
    lines.append("")
    lines.append("## Exact Commands to Run Later")
    for cmd in exact_commands:
        lines.append("```")
        lines.append(cmd)
        lines.append("```")
    lines.append("")
    lines.append("## Human Approval Required")
    lines.append("Yes.")
    lines.append("")
    lines.append("## Execution Status")
    lines.append("This packet has been prepared but NOT executed.")
    lines.append("An operator must review and explicitly approve before any command is run.")

    packet_path.write_text("\n".join(lines))
    session_log.record_command_packet(str(packet_path))
    print(f"\n  Command packet written: {packet_path}")
    print("  Status: prepared_not_executed")
    session_log.record_action("prepare_command_packet")
