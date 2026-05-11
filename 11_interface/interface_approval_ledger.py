import json
import re
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER_DIR = HERE.parent / "09_exports" / "interface_phase_1" / "approval_ledger"
LEDGER_FILE = LEDGER_DIR / "approval_ledger.jsonl"
COMMAND_PACKETS_DIR = HERE.parent / "09_exports" / "interface_phase_1" / "command_packets"

ALLOWED_STATES = ["prepared", "reviewed", "approved_by_operator", "rejected_by_operator", "expired", "superseded"]


def _ensure_ledger(ledger_file=None):
    if ledger_file is None:
        ledger_file = LEDGER_FILE
    ledger_file.parent.mkdir(parents=True, exist_ok=True)
    if not ledger_file.exists():
        ledger_file.write_text("")


def _read_ledger(ledger_file=None):
    if ledger_file is None:
        ledger_file = LEDGER_FILE
    _ensure_ledger(ledger_file)
    records = []
    for line in ledger_file.read_text().strip().splitlines():
        if line.strip():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return records


def _write_record(record, ledger_file=None):
    if ledger_file is None:
        ledger_file = LEDGER_FILE
    _ensure_ledger(ledger_file)
    with open(str(ledger_file), "a") as f:
        f.write(json.dumps(record) + "\n")


def _validate_packet_path(packet_path_str):
    path = Path(packet_path_str)
    if not path.is_absolute():
        path = Path.cwd() / path
    try:
        path = path.resolve()
    except Exception:
        return None
    allowed = COMMAND_PACKETS_DIR.resolve()
    if not str(path).startswith(str(allowed)):
        return None
    if not path.exists():
        return None
    return path


def _extract_packet_metadata(packet_path):
    content = packet_path.read_text()
    packet_id = None
    approval_phrase = None
    for line in content.splitlines():
        ls = line.strip()
        if "**Packet ID:**" in ls:
            packet_id = ls.split("**Packet ID:**")[-1].strip()
        if "**Required Approval Phrase**" in ls or "## Required Approval Phrase" in ls:
            continue
        if "I_APPROVE_PREPARED_PACKET_" in ls and "`" in ls:
            approval_phrase = ls.strip().strip("`").strip()
        if packet_id and approval_phrase:
            break
    if not approval_phrase:
        for line in content.splitlines():
            if "I_APPROVE_PREPARED_PACKET_" in line:
                m = re.search(r"I_APPROVE_PREPARED_PACKET_\w+", line)
                if m:
                    approval_phrase = m.group(0)
                    break
    return packet_id, approval_phrase


def show_ledger(ledger_file=None):
    if ledger_file is None:
        ledger_file = LEDGER_FILE
    _ensure_ledger(ledger_file)
    records = _read_ledger(ledger_file)
    if not records:
        print("  Approval ledger is empty.")
        return
    print(f"  Approval ledger contains {len(records)} record(s):")
    for rec in records:
        state = rec.get("state", "unknown")
        pid = rec.get("packet_id", "unknown")
        ptype = rec.get("packet_type", "unknown")
        ts = rec.get("timestamp_utc", "unknown")
        match = rec.get("approval_phrase_match", False)
        exec_p = rec.get("execution_performed", True)
        print(f"  [{state}] {pid} ({ptype}) @ {ts} | phrase_match={match} | exec={exec_p}")


def review_packet(packet_path_str, ledger_file=None):
    if ledger_file is None:
        ledger_file = LEDGER_FILE
    p = _validate_packet_path(packet_path_str)
    if not p:
        print(f"  ERROR: Invalid packet path: {packet_path_str}")
        return {"status": "FAIL", "error": "Invalid packet path"}

    packet_id, approval_phrase = _extract_packet_metadata(p)
    packet_type = p.stem.replace("_packet", "")

    record = {
        "ledger_id": f"LEDGER-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "packet_id": packet_id or "unknown",
        "packet_type": packet_type,
        "packet_path": str(p),
        "state": "reviewed",
        "operator_phrase_entered": None,
        "approval_phrase_expected": approval_phrase or "unknown",
        "approval_phrase_match": False,
        "execution_performed": False,
        "notes": "Packet reviewed. No approval or rejection recorded.",
    }
    _write_record(record, ledger_file)
    print(f"  [INFO] Packet reviewed: {packet_id or 'unknown'}")
    print(f"  Expected approval phrase: {approval_phrase or 'not detected'}")
    return {"status": "PASS", "record": record}


def approve_packet(packet_path_str, phrase_entered, ledger_file=None):
    if ledger_file is None:
        ledger_file = LEDGER_FILE
    p = _validate_packet_path(packet_path_str)
    if not p:
        print(f"  ERROR: Invalid packet path: {packet_path_str}")
        return {"status": "FAIL", "error": "Invalid packet path"}

    if not phrase_entered:
        print("  ERROR: No approval phrase entered.")
        return {"status": "FAIL", "error": "Missing approval phrase"}

    packet_id, approval_phrase = _extract_packet_metadata(p)
    packet_type = p.stem.replace("_packet", "")
    phrase_match = phrase_entered.strip() == (approval_phrase or "").strip()
    state = "approved_by_operator" if phrase_match else "rejected_by_operator"

    record = {
        "ledger_id": f"LEDGER-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "packet_id": packet_id or "unknown",
        "packet_type": packet_type,
        "packet_path": str(p),
        "state": state,
        "operator_phrase_entered": phrase_entered.strip(),
        "approval_phrase_expected": approval_phrase or "unknown",
        "approval_phrase_match": phrase_match,
        "execution_performed": False,
        "notes": f"Packet {'approved' if phrase_match else 'rejected'} by operator. No commands executed.",
    }
    _write_record(record, ledger_file)
    if phrase_match:
        print(f"  [PASS] Packet approved: {packet_id or 'unknown'}")
        print(f"  Phrase match: YES")
        print(f"  NOTE: Packet has been approved but NOT executed.")
    else:
        print(f"  [WARNING] Packet NOT approved: {packet_id or 'unknown'}")
        print(f"  Phrase mismatch: entered '{phrase_entered.strip()}' != expected '{approval_phrase or 'unknown'}'")
        print(f"  State set to: rejected_by_operator")
    print(f"  Execution performed: false")
    return {"status": "PASS" if phrase_match else "WARNING", "record": record}


def reject_packet(packet_path_str, note, ledger_file=None):
    if ledger_file is None:
        ledger_file = LEDGER_FILE
    p = _validate_packet_path(packet_path_str)
    if not p:
        print(f"  ERROR: Invalid packet path: {packet_path_str}")
        return {"status": "FAIL", "error": "Invalid packet path"}

    packet_id, approval_phrase = _extract_packet_metadata(p)
    packet_type = p.stem.replace("_packet", "")

    record = {
        "ledger_id": f"LEDGER-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "packet_id": packet_id or "unknown",
        "packet_type": packet_type,
        "packet_path": str(p),
        "state": "rejected_by_operator",
        "operator_phrase_entered": None,
        "approval_phrase_expected": approval_phrase or "unknown",
        "approval_phrase_match": False,
        "execution_performed": False,
        "notes": note or "Rejected by operator.",
    }
    _write_record(record, ledger_file)
    print(f"  [INFO] Packet rejected: {packet_id or 'unknown'}")
    print(f"  Reason: {note or 'Not specified'}")
    return {"status": "PASS", "record": record}
