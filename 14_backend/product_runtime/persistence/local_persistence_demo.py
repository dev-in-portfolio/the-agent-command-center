from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from product_runtime.persistence.request_repository import RequestRepository
from product_runtime.request_lifecycle import load_demo_fixture


DEMO_DB_PATH = Path(".agent_command_center/demo_runtime.sqlite3")
DEMO_LIFECYCLE_STATES = [
    "request_received",
    "request_validated",
    "dry_run_plan_generated",
    "approval_required",
    "audit_event_prepared",
    "blocked_before_execution",
    "ready_for_human_review",
]


def run_demo():
    repository = RequestRepository(db_path=DEMO_DB_PATH)
    try:
        initialization = repository.initialize_local_dev_database()
        fixture = load_demo_fixture()
        created = repository.create_request(fixture)
        request = created["request"]
        transitions = []
        for state in DEMO_LIFECYCLE_STATES:
            transition = repository.transition_request_state(
                request["id"],
                state,
                event_summary=f"Demo lifecycle transition: {state}",
            )
            transitions.append(transition)
        request_record = repository.get_request(request["id"])
        lifecycle_events = repository.get_lifecycle_events(request["id"])
        return {
            "ok": True,
            "demo_db_path": str(DEMO_DB_PATH),
            "initialization": initialization,
            "created_request": created,
            "transitions": transitions,
            "request_record": request_record,
            "lifecycle_events": lifecycle_events,
            "requested_states": DEMO_LIFECYCLE_STATES,
            "local_dev_only": True,
            "no_external_mutation": True,
            "real_automation_enabled": False,
        }
    finally:
        repository.close()


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2, sort_keys=False))
