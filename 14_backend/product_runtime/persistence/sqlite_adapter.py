from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


DEFAULT_LOCAL_DEV_DB_PATH = Path(".agent_command_center/dev_runtime.sqlite3")
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "migrations" / "001_mvp_request_lifecycle.sql"


def _utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _generate_id(prefix):
    return f"{prefix}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}"


def _row_to_dict(row):
    return dict(row) if row is not None else None


class SQLiteRequestPersistenceAdapter:
    def __init__(self, db_path=None):
        self.db_path = Path(db_path) if db_path else DEFAULT_LOCAL_DEV_DB_PATH
        self._connection = None
        self._initialized = False

    def _connect(self, create_parent=False):
        if self._connection is not None:
            return self._connection
        if create_parent:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        elif not self.db_path.parent.exists():
            raise RuntimeError("Local dev database is not initialized. Call initialize_local_dev_database().")
        self._connection = sqlite3.connect(str(self.db_path))
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    def _ensure_ready(self):
        if not self._initialized and not self.db_path.exists():
            raise RuntimeError("Local dev database is not initialized. Call initialize_local_dev_database().")
        return self._connect(create_parent=False)

    def _apply_schema(self):
        connection = self._connect(create_parent=True)
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        connection.executescript(schema_sql)
        connection.commit()
        self._initialized = True

    def initialize_local_dev_database(self):
        self._apply_schema()
        return {
            "ok": True,
            "db_path": str(self.db_path),
            "local_dev_only": True,
            "schema_applied": True,
        }

    def create_request(self, payload):
        connection = self._ensure_ready()
        request_id = str(payload.get("request_id") or _generate_id("REQ-LOCAL"))
        created_at_utc = str(payload.get("created_at_utc") or _utc_now())
        row = {
            "id": request_id,
            "actor_id": str(payload.get("actor_id") or "demo_operator"),
            "actor_role": str(payload.get("actor_role") or "operator"),
            "title": str(payload.get("title") or ""),
            "intent": str(payload.get("intent") or ""),
            "requested_action": str(payload.get("requested_action") or payload.get("requested_action_type") or "planning_review_only"),
            "lifecycle_state": str(payload.get("lifecycle_state") or "request_received"),
            "created_at_utc": created_at_utc,
        }
        connection.execute(
            """
            INSERT INTO requests (
                id, actor_id, actor_role, title, intent, requested_action, lifecycle_state, created_at_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["id"],
                row["actor_id"],
                row["actor_role"],
                row["title"],
                row["intent"],
                row["requested_action"],
                row["lifecycle_state"],
                row["created_at_utc"],
            ),
        )
        connection.commit()
        self.add_lifecycle_event(request_id, "request_received", "Local request stored in SQLite.")
        return self.get_request(request_id)

    def get_request(self, request_id):
        connection = self._ensure_ready()
        cursor = connection.execute("SELECT * FROM requests WHERE id = ?", (request_id,))
        return _row_to_dict(cursor.fetchone())

    def list_requests(self, limit=50):
        connection = self._ensure_ready()
        cursor = connection.execute(
            "SELECT * FROM requests ORDER BY created_at_utc DESC, id DESC LIMIT ?",
            (int(limit) if limit is not None else 50,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def update_request_state(self, request_id, next_state, event_summary=None):
        connection = self._ensure_ready()
        existing = self.get_request(request_id)
        if existing is None:
            raise KeyError(f"Unknown request_id: {request_id}")
        connection.execute(
            "UPDATE requests SET lifecycle_state = ? WHERE id = ?",
            (str(next_state), request_id),
        )
        connection.commit()
        self.add_lifecycle_event(
            request_id,
            str(next_state),
            event_summary or f"Lifecycle advanced to {next_state}.",
        )
        return self.get_request(request_id)

    def add_lifecycle_event(self, request_id, event_type, event_summary):
        connection = self._ensure_ready()
        event = {
            "id": _generate_id("EVENT"),
            "request_id": str(request_id),
            "lifecycle_state": str(event_type),
            "event_type": str(event_type),
            "details": str(event_summary or ""),
            "created_at_utc": _utc_now(),
        }
        connection.execute(
            """
            INSERT INTO request_lifecycle_events (
                id, request_id, lifecycle_state, event_type, details, created_at_utc
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                event["id"],
                event["request_id"],
                event["lifecycle_state"],
                event["event_type"],
                event["details"],
                event["created_at_utc"],
            ),
        )
        connection.commit()
        return event

    def get_lifecycle_events(self, request_id):
        connection = self._ensure_ready()
        cursor = connection.execute(
            "SELECT * FROM request_lifecycle_events WHERE request_id = ? ORDER BY created_at_utc ASC, id ASC",
            (request_id,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def close(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None
        self._initialized = False

