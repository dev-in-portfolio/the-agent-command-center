#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIGRATION_DIR = ROOT / "14_backend" / "product_runtime" / "providers" / "supabase" / "migrations"


def fail(message):
    print(f"FAIL: {message}")
    sys.exit(1)


def main():
    m003 = MIGRATION_DIR / "003_feedback_persistence_schema.sql"
    m004 = MIGRATION_DIR / "004_feedback_persistence_rls_policies.sql"

    if not m003.exists(): fail("Missing 003 migration file.")
    if not m004.exists(): fail("Missing 004 migration file.")

    text003 = m003.read_text(encoding="utf-8", errors="replace")
    if "CREATE TABLE IF NOT EXISTS external_feedback_packets" not in text003:
        fail("003 migration missing table definition.")
    if "owner_user_id UUID NOT NULL REFERENCES auth.users(id)" not in text003:
        fail("003 migration missing owner_user_id foreign key.")

    text004 = m004.read_text(encoding="utf-8", errors="replace")
    if "ALTER TABLE external_feedback_packets ENABLE ROW LEVEL SECURITY" not in text004:
        fail("004 migration missing RLS enablement.")
    if "auth.uid() = owner_user_id" not in text004:
        fail("004 migration missing owner-scoped policy.")
    
    forbidden = ["FOR UPDATE", "FOR DELETE", "ALL", "PUBLIC"]
    for pattern in forbidden:
        if f"FOR {pattern}" in text004 or f"TO {pattern}" in text004:
            if pattern == "PUBLIC" and "TO PUBLIC" in text004:
                 fail(f"004 migration contains broad public policy: {pattern}")
            if pattern in ["UPDATE", "DELETE"] and f"FOR {pattern}" in text004:
                 fail(f"004 migration contains forbidden modification policy: {pattern}")

    print("MVP23_FEEDBACK_MIGRATION_FILES_VERIFICATION_PASS")


if __name__ == "__main__":
    main()
