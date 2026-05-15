from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from product_runtime.persistence.sqlite_adapter import DEFAULT_LOCAL_DEV_DB_PATH


MIGRATION_PATH = Path(__file__).resolve().parent.parent / "migrations" / "001_mvp_request_lifecycle.sql"


def apply_local_migrations(db_path=None, sql_path=None):
    target_path = Path(db_path) if db_path else DEFAULT_LOCAL_DEV_DB_PATH
    target_sql = Path(sql_path) if sql_path else MIGRATION_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(str(target_path)) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(target_sql.read_text(encoding="utf-8"))
        connection.commit()

    return {
        "ok": True,
        "local_dev_only": True,
        "db_path": str(target_path),
        "sql_path": str(target_sql),
        "migration_applied": True,
    }


def main():
    parser = argparse.ArgumentParser(description="Apply local MVP-2 SQLite migrations.")
    parser.add_argument("--db-path", default=str(DEFAULT_LOCAL_DEV_DB_PATH))
    parser.add_argument("--sql-path", default=str(MIGRATION_PATH))
    args = parser.parse_args()

    print("LOCAL_DEV_ONLY: applying SQLite migrations for MVP-2")
    result = apply_local_migrations(args.db_path, args.sql_path)
    print(json.dumps(result, indent=2, sort_keys=False))


if __name__ == "__main__":
    main()
