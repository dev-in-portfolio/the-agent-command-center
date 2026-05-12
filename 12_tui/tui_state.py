import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PHASE1 = ROOT / "11_interface"
PHASE2_EXPORTS = ROOT / "09_exports" / "interface_phase_2"
SESSION_DIR = PHASE2_EXPORTS / "sessions"
SNAPSHOT_DIR = PHASE2_EXPORTS / "snapshots"

_loaded_modules = {}


def _load_p1_module(name):
    if name in _loaded_modules:
        return _loaded_modules[name]
    import importlib.util
    path = PHASE1 / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _loaded_modules[name] = mod
    return mod


def get_action_registry():
    mod = _load_p1_module("interface_action_registry")
    return getattr(mod, "ACTION_REGISTRY", {})


def get_policy():
    mod = _load_p1_module("interface_policy")
    return {
        "safe": getattr(mod, "SAFE_ACTIONS", []),
        "controlled": getattr(mod, "CONTROLLED_ACTIONS", []),
        "locked": getattr(mod, "LOCKED_ACTIONS", []),
    }


def get_artifact_inspector():
    mod = _load_p1_module("interface_artifact_inspector")
    return mod


def get_branch_review():
    mod = _load_p1_module("interface_branch_review")
    return mod


def get_approval_ledger():
    mod = _load_p1_module("interface_approval_ledger")
    return mod


def get_session_log():
    mod = _load_p1_module("interface_session_log")
    return mod


def get_actions():
    mod = _load_p1_module("interface_actions")
    return mod


class TUIState:
    def __init__(self):
        self.current_screen = "dashboard"
        self.previous_screen = None
        self.screen_history = []
        self.session_id = f"TUI-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.last_refreshed_at = self.started_at
        self.screens_viewed = []
        self.actions_requested = []
        self.actions_completed = []
        self.actions_refused = []
        self.validator_runs = []
        self.packets_prepared = []
        self.branch_reviews_prepared = []
        self.ledger_records_created = 0
        self.errors = []
        self.refresh_counter = 0
        self.last_validator_results = {}
        self.artifact_cache = None
        self.ledger_cache = None
        self.selected_artifact_package = None
        self.selected_packet_type = None
        self.selected_branch_review = None
        self.selected_ledger_filter = None
        self.last_action_name = None
        self.last_action_status = None
        self.recommended_next_action = None

    @property
    def breadcrumbs(self):
        crumbs = []
        for s in self.screen_history:
            crumbs.append(s.replace("_", " ").title())
        crumbs.append(self.current_screen.replace("_", " ").title())
        return " > ".join(crumbs)

    def navigate_to(self, screen_name):
        if screen_name == self.current_screen:
            return
        self.previous_screen = self.current_screen
        self.screen_history.append(self.current_screen)
        if len(self.screen_history) > 20:
            self.screen_history = self.screen_history[-20:]
        self.current_screen = screen_name
        self.record_screen(screen_name)

    def go_back(self):
        if self.screen_history:
            prev = self.screen_history.pop()
            self.previous_screen = self.current_screen
            self.current_screen = prev
            return True
        return False

    def go_home(self):
        self.screen_history.clear()
        self.previous_screen = self.current_screen
        self.current_screen = "dashboard"

    def record_screen(self, screen_name):
        if screen_name not in self.screens_viewed:
            self.screens_viewed.append(screen_name)

    def record_action_requested(self, action):
        self.actions_requested.append(action)

    def record_action_completed(self, action):
        self.actions_completed.append(action)
        self.last_action_name = action
        self.last_action_status = "PASS"

    def record_action_refused(self, action, reason):
        self.actions_refused.append({"action": action, "reason": reason})
        self.last_action_name = action
        self.last_action_status = "REFUSED"

    def record_validator_run(self, name, status):
        self.validator_runs.append({
            "name": name, "status": status,
            "ts": datetime.now(timezone.utc).isoformat()
        })
        self.last_validator_results[name] = status

    def record_packet_prepared(self, packet_type):
        self.packets_prepared.append(packet_type)

    def record_branch_review(self, branch, base):
        self.branch_reviews_prepared.append({"branch": branch, "base": base})

    def record_ledger_write(self):
        self.ledger_records_created += 1

    def record_error(self, error):
        self.errors.append(error)

    def get_summary(self):
        return {
            "session_id": self.session_id,
            "started_at_utc": self.started_at,
            "ended_at_utc": datetime.now(timezone.utc).isoformat(),
            "current_screen": self.current_screen,
            "screens_viewed": self.screens_viewed,
            "actions_requested": len(self.actions_requested),
            "actions_completed": len(self.actions_completed),
            "actions_refused": len(self.actions_refused),
            "validator_runs": len(self.validator_runs),
            "packets_prepared": len(self.packets_prepared),
            "branch_reviews_prepared": len(self.branch_reviews_prepared),
            "ledger_records_created": self.ledger_records_created,
            "errors": len(self.errors),
            "final_boundary_state": {
                "official_repo_touched": False,
                "repo2_touched": False,
                "repo3_touched": False,
                "deployment_performed": False,
                "secrets_used": False,
                "credentials_used": False,
                "command_packets_executed": False,
            }
        }


def write_session_report(state):
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    summary = state.get_summary()
    sid = state.session_id
    report_md = SESSION_DIR / f"session_{sid}.md"
    report_json = SESSION_DIR / f"session_{sid}.json"
    lines = []
    lines.append(f"# Session Report: {sid}")
    lines.append("")
    lines.append(f"**Started at UTC:** {state.started_at}")
    lines.append(f"**Ended at UTC:** {summary['ended_at_utc']}")
    lines.append(f"**Current screen:** {summary['current_screen']}")
    lines.append("")
    lines.append("## Activity Summary")
    lines.append(f"- Screens viewed: {len(state.screens_viewed)}")
    lines.append(f"- Actions requested: {summary['actions_requested']}")
    lines.append(f"- Actions completed: {summary['actions_completed']}")
    lines.append(f"- Actions refused: {summary['actions_refused']}")
    lines.append(f"- Validator runs: {summary['validator_runs']}")
    lines.append(f"- Packets prepared: {summary['packets_prepared']}")
    lines.append(f"- Branch reviews prepared: {summary['branch_reviews_prepared']}")
    lines.append(f"- Ledger records created: {summary['ledger_records_created']}")
    lines.append(f"- Errors: {summary['errors']}")
    lines.append("")
    lines.append("## Boundary State")
    bs = summary["final_boundary_state"]
    for k, v in bs.items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    if state.last_action_name:
        lines.append(f"**Last action:** {state.last_action_name} [{state.last_action_status}]")
    if state.recommended_next_action:
        lines.append(f"**Recommended next:** {state.recommended_next_action}")
    report_md.write_text("\n".join(lines))
    report_json.write_text(json.dumps(summary, indent=2))
    return report_md
