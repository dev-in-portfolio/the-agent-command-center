import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PHASE1 = ROOT / "11_interface"
PHASE2_EXPORTS = ROOT / "09_exports" / "interface_phase_2"
SESSION_DIR = PHASE2_EXPORTS / "sessions"

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
        self.session_id = f"TUI-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        self.started_at = datetime.now(timezone.utc).isoformat()
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

    def record_screen(self, screen_name):
        if screen_name not in self.screens_viewed:
            self.screens_viewed.append(screen_name)

    def record_action_requested(self, action):
        self.actions_requested.append(action)

    def record_action_completed(self, action):
        self.actions_completed.append(action)

    def record_action_refused(self, action, reason):
        self.actions_refused.append({"action": action, "reason": reason})

    def record_validator_run(self, name, status):
        self.validator_runs.append({"name": name, "status": status, "ts": datetime.now(timezone.utc).isoformat()})
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
    report_path = SESSION_DIR / f"session_{state.session_id}.json"
    report_path.write_text(json.dumps(summary, indent=2))
    return report_path
