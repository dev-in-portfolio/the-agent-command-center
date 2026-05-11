import importlib.util
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("interface_action_registry", str(_HERE / "interface_action_registry.py"))
_reg_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_reg_mod)
ACTION_REGISTRY = _reg_mod.ACTION_REGISTRY


class PolicyRefusal(Exception):
    pass


def get_action(action_id):
    return ACTION_REGISTRY.get(action_id)


def is_safe(action_id):
    entry = ACTION_REGISTRY.get(action_id)
    if not entry:
        return False
    return entry["category"] == "safe"


def is_controlled(action_id):
    entry = ACTION_REGISTRY.get(action_id)
    if not entry:
        return False
    return entry["category"] == "controlled"


def is_locked(action_id):
    entry = ACTION_REGISTRY.get(action_id)
    if not entry:
        return True
    return entry["category"] == "locked"


def enforce_allowed(action_id, session_log=None):
    entry = ACTION_REGISTRY.get(action_id)
    if not entry:
        if session_log:
            session_log.record_refused(action_id, f"Unknown action: {action_id}")
        raise PolicyRefusal(f"Unknown action: {action_id}")

    if entry["category"] == "locked":
        reason = f"Action '{action_id}' is permanently locked: {entry['label']}"
        if session_log:
            session_log.record_refused(action_id, reason)
        raise PolicyRefusal(reason)

    if entry["category"] not in ("safe", "controlled"):
        reason = f"Action '{action_id}' has unknown category: {entry['category']}"
        if session_log:
            session_log.record_refused(action_id, reason)
        raise PolicyRefusal(reason)

    return True


def refuse_locked_action(action_id, reason, session_log=None):
    refusal = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action_id": action_id,
        "reason": reason,
        "boundary_status": "refused",
        "execution_performed": False,
    }
    if session_log:
        session_log.record_refused(action_id, reason)
    return refusal


def validate_action_registry():
    errors = []
    for action_id, entry in ACTION_REGISTRY.items():
        if entry["action_id"] != action_id:
            errors.append(f"action_id mismatch: {action_id} vs {entry['action_id']}")

        if entry["category"] not in ("safe", "controlled", "locked"):
            errors.append(f"Invalid category for {action_id}: {entry['category']}")

        if entry["risk_level"] not in ("none", "low", "medium", "high", "locked"):
            errors.append(f"Invalid risk_level for {action_id}: {entry['risk_level']}")

        if entry["category"] == "locked" and entry.get("menu_option"):
            errors.append(f"Locked action {action_id} has menu_option: {entry['menu_option']}")

        if entry["category"] == "locked" and entry.get("cli_flags"):
            errors.append(f"Locked action {action_id} has cli_flags: {entry['cli_flags']}")

    return errors
