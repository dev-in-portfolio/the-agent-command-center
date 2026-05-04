import json
import hashlib
from pathlib import Path

APPROVAL_LEDGER_MODULE_VERSION = "3.2.0"

def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_digest(data: object) -> str:
    if not isinstance(data, str):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def load_json_file(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_approval_record_summary(approval_record: dict, source_path: str | None = None) -> dict:
    return {
        "approval_record_version": approval_record.get("approval_record_version"),
        "approval_packet_digest": approval_record.get("approval_packet_digest"),
        "approval_signature": approval_record.get("approval_signature"),
        "reviewer_name": approval_record.get("reviewer_name"),
        "approval_decision": approval_record.get("approval_decision"),
        "record_status": approval_record.get("record_status"),
        "approval_required": approval_record.get("approval_required"),
        "recommended_next_action": approval_record.get("recommended_next_action"),
        "approval_handoff_version": approval_record.get("approval_handoff_version"),
        "source_path": source_path,
        "baseline_preserved": approval_record.get("baseline_preserved") is True,
        "external_actions_taken": approval_record.get("external_actions_taken") is True,
        "live_worker_agents_activated": approval_record.get("live_worker_agents_activated") is True
    }

def compare_signed_approval_records(before_record: dict, after_record: dict) -> dict:
    before_summary = extract_approval_record_summary(before_record, "before")
    after_summary = extract_approval_record_summary(after_record, "after")
    
    digest_changed = before_summary["approval_packet_digest"] != after_summary["approval_packet_digest"]
    signature_changed = before_summary["approval_signature"] != after_summary["approval_signature"]
    decision_changed = before_summary["approval_decision"] != after_summary["approval_decision"]
    status_changed = before_summary["record_status"] != after_summary["record_status"]
    reviewer_changed = before_summary["reviewer_name"] != after_summary["reviewer_name"]
    next_action_changed = before_summary["recommended_next_action"] != after_summary["recommended_next_action"]
    
    changed = any([
        digest_changed,
        signature_changed,
        decision_changed,
        status_changed,
        reviewer_changed,
        next_action_changed
    ])
    
    return {
        "approval_record_comparison_version": "3.2.0",
        "comparison_status": "CHANGED" if changed else "UNCHANGED",
        "before_summary": before_summary,
        "after_summary": after_summary,
        "approval_packet_digest_changed": digest_changed,
        "approval_signature_changed": signature_changed,
        "approval_decision_changed": decision_changed,
        "record_status_changed": status_changed,
        "reviewer_changed": reviewer_changed,
        "recommended_next_action_changed": next_action_changed,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False
    }

def collect_approval_records_from_paths(paths: list[str]) -> list[dict]:
    items = []
    for path in paths:
        try:
            data = load_json_file(path)
            if "signed_approval_record" in data:
                record = data["signed_approval_record"]
            elif "approval_record_version" in data:
                record = data
            else:
                continue
            items.append({
                "source_path": path,
                "approval_record": record,
                "summary": extract_approval_record_summary(record, path)
            })
        except Exception:
            pass
    return items

def create_approval_status_summary(record_items: list[dict]) -> dict:
    total = len(record_items)
    signed = sum(1 for r in record_items if r["summary"]["record_status"] == "SIGNED")
    blocked = sum(1 for r in record_items if r["summary"]["record_status"] == "BLOCKED")
    approve = sum(1 for r in record_items if r["summary"]["approval_decision"] == "approve")
    reject = sum(1 for r in record_items if r["summary"]["approval_decision"] == "reject")
    needs_changes = sum(1 for r in record_items if r["summary"]["approval_decision"] == "needs_changes")
    
    digests = [r["summary"]["approval_packet_digest"] for r in record_items if r["summary"]["approval_packet_digest"]]
    signatures = [r["summary"]["approval_signature"] for r in record_items if r["summary"]["approval_signature"]]
    
    unique_digests = len(set(digests))
    unique_signatures = len(set(signatures))
    
    return {
        "approval_status_summary_version": "3.2.0",
        "total_records": total,
        "signed_records": signed,
        "blocked_records": blocked,
        "approve_records": approve,
        "reject_records": reject,
        "needs_changes_records": needs_changes,
        "unique_approval_packet_digests": unique_digests,
        "unique_approval_signatures": unique_signatures,
        "duplicate_packet_digest_count": len(digests) - unique_digests,
        "duplicate_signature_count": len(signatures) - unique_signatures,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False
    }

def find_duplicate_approval_signals(record_items: list[dict]) -> dict:
    digest_map = {}
    signature_map = {}
    
    for r in record_items:
        d = r["summary"]["approval_packet_digest"]
        s = r["summary"]["approval_signature"]
        p = r["source_path"]
        
        if d:
            if d not in digest_map:
                digest_map[d] = {"value": d, "count": 0, "source_paths": []}
            digest_map[d]["count"] += 1
            digest_map[d]["source_paths"].append(p)
            
        if s:
            if s not in signature_map:
                signature_map[s] = {"value": s, "count": 0, "source_paths": []}
            signature_map[s]["count"] += 1
            signature_map[s]["source_paths"].append(p)
            
    dup_digests = [v for v in digest_map.values() if v["count"] > 1]
    dup_signatures = [v for v in signature_map.values() if v["count"] > 1]
    
    status = "DUPLICATES_FOUND" if dup_digests or dup_signatures else "CLEAR"
    
    return {
        "duplicate_signal_version": "3.2.0",
        "duplicate_packet_digests": dup_digests,
        "duplicate_approval_signatures": dup_signatures,
        "duplicate_signal_status": status,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False
    }

def create_approval_ledger_index(record_items: list[dict], ledger_label: str = "station-chief-approval-ledger") -> dict:
    summaries = [r["summary"] for r in record_items]
    
    ledger = {
        "approval_ledger_version": "3.2.0",
        "ledger_label": ledger_label,
        "record_count": len(summaries),
        "records": summaries,
        "approval_status_summary": create_approval_status_summary(record_items),
        "duplicate_approval_signals": find_duplicate_approval_signals(record_items),
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "execution_authorized": False,
        "note": "Approval ledger indexes approval history only. It does not execute repo patches by itself."
    }
    
    ledger["ledger_digest"] = sha256_digest(ledger)
    return ledger

def verify_approval_ledger_index(ledger_index: dict) -> dict:
    test_ledger = dict(ledger_index)
    expected_digest = test_ledger.pop("ledger_digest", None)
    
    actual_digest = sha256_digest(test_ledger)
    
    matches = actual_digest == expected_digest
    auth = test_ledger.get("execution_authorized") is False
    base = test_ledger.get("baseline_preserved") is True
    ext = test_ledger.get("external_actions_taken") is False
    live = test_ledger.get("live_worker_agents_activated") is False
    
    pass_all = matches and auth and base and ext and live
    
    return {
        "ledger_verification_version": "3.2.0",
        "verification_status": "PASS" if pass_all else "FAIL",
        "ledger_digest_matches": matches,
        "execution_authorized": False,
        "baseline_preserved": base,
        "external_actions_taken": ext,
        "live_worker_agents_activated": live,
        "reason": "OK" if pass_all else "Ledger corrupted or unauthorized"
    }

def lookup_approval_records_by_digest(ledger_index: dict, approval_packet_digest: str) -> dict:
    matches = [r for r in ledger_index.get("records", []) if r.get("approval_packet_digest") == approval_packet_digest]
    
    return {
        "lookup_version": "3.2.0",
        "approval_packet_digest": approval_packet_digest,
        "match_count": len(matches),
        "matches": matches,
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False
    }

def create_approval_ledger_bundle(record_items: list[dict], ledger_label: str = "station-chief-approval-ledger") -> dict:
    ledger_index = create_approval_ledger_index(record_items, ledger_label)
    
    return {
        "approval_ledger_bundle_version": "3.2.0",
        "ledger_index": ledger_index,
        "ledger_verification": verify_approval_ledger_index(ledger_index),
        "approval_status_summary": ledger_index["approval_status_summary"],
        "duplicate_approval_signals": ledger_index["duplicate_approval_signals"],
        "baseline_preserved": True,
        "external_actions_taken": False,
        "live_worker_agents_activated": False,
        "execution_authorized": False
    }
