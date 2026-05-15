#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def check():
    migrations = [
        ROOT / "migrations" / "001_supabase_request_runtime.sql",
        ROOT / "migrations" / "002_supabase_auth_rls_policies.sql",
    ]
    results = {
        "migrations_present": all(path.exists() for path in migrations),
        "manual_apply_only": True,
        "rls_enable_statements_present": True,
        "broad_public_write_policies_present": False,
        "anonymous_write_policies_present": False,
        "manual_apply_notes_present": True,
        "files": [],
    }

    for path in migrations:
        text = load_text(path)
        lower = text.lower()
        results["files"].append({
            "path": str(path.relative_to(ROOT)),
            "exists": path.exists(),
            "rls_enable_statements_present": "enable row level security" in lower,
            "manual_apply_notes_present": "manual" in lower and "apply" in lower,
            "broad_public_write_policies_present": any(term in lower for term in [
                "policy if not exists",
                "for insert",
                "for update",
                "for delete",
            ]) and ("authenticated" not in lower and "deny by default" not in lower),
        })

        if "enable row level security" not in lower:
            results["rls_enable_statements_present"] = False
        if "manual" not in lower or "apply" not in lower:
            results["manual_apply_notes_present"] = False
        if any(term in lower for term in ["anonymous write", "broad public write", "public write"]):
            results["anonymous_write_policies_present"] = True
        if "policy" in lower and "public" in lower and ("insert" in lower or "update" in lower or "delete" in lower):
            results["broad_public_write_policies_present"] = True

    results["ready"] = (
        results["migrations_present"]
        and results["rls_enable_statements_present"]
        and results["manual_apply_notes_present"]
        and not results["anonymous_write_policies_present"]
        and not results["broad_public_write_policies_present"]
    )
    return results


if __name__ == "__main__":
    print(json.dumps(check(), indent=2, sort_keys=False))
