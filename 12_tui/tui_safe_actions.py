import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
PHASE1 = ROOT / "11_interface"

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


def run_validator_wall(state=None):
    validators = [
        ("CLI", ["python3", str(ROOT / "scripts/validate_interface_phase_1_cli.py")]),
        ("Command Packets", ["python3", str(ROOT / "scripts/validate_interface_phase_1_command_packets.py")]),
        ("E2E", ["python3", str(ROOT / "scripts/validate_interface_phase_1_e2e.py")]),
        ("RC", ["python3", str(ROOT / "scripts/validate_interface_phase_1_release_candidate.py")]),
    ]
    results = {}
    stdout_data = {}
    for name, cmd in validators:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            stdout_data[name] = r.stdout
            if r.returncode == 0:
                results[name] = "PASS"
            else:
                results[name] = "FAIL"
        except subprocess.TimeoutExpired:
            results[name] = "TIMEOUT"
            stdout_data[name] = ""
        except Exception as e:
            results[name] = f"ERROR: {e}"
            stdout_data[name] = ""
        if state:
            state.record_validator_run(name, results[name])
    if state:
        state.last_validator_results = results
        state.record_action_completed("validator_wall")
        _save_validator_wall_log(state, results, stdout_data)
    return results


def _save_validator_wall_log(state, results, stdout_data):
    from tui_state import SESSION_DIR
    sid = state.session_id
    session_dir = SESSION_DIR / sid
    session_dir.mkdir(parents=True, exist_ok=True)
    result_path = session_dir / "validator_wall_result.json"
    result_path.write_text(json.dumps(results, indent=2))
    stdout_path = session_dir / "validator_wall_stdout.txt"
    stdout_lines = []
    for name, text in stdout_data.items():
        stdout_lines.append(f"=== {name} ===")
        stdout_lines.append(text)
    stdout_path.write_text("\n".join(stdout_lines))


def prepare_command_packet(packet_type):
    actions = _load_p1_module("interface_actions")
    if hasattr(actions, "generate_command_packet"):
        try:
            result = actions.generate_command_packet(packet_type)
            return {"status": "PASS", "result": result}
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    cli_script = str(PHASE1 / "station_chief_cli.py")
    r = subprocess.run(
        [sys.executable, cli_script, "--prepare-packet", packet_type],
        capture_output=True, text=True, timeout=60
    )
    if r.returncode == 0:
        return {"status": "PASS", "output": r.stdout}
    return {"status": "FAIL", "output": r.stdout, "error": r.stderr}


def prepare_branch_review(branch, base=None):
    brm = _load_p1_module("interface_branch_review")
    sanitized = brm.sanitize_branch_name(branch) if hasattr(brm, "sanitize_branch_name") else branch
    if sanitized is None:
        return {"status": "FAIL", "error": "Invalid branch name"}
    cmd = [sys.executable, str(PHASE1 / "station_chief_cli.py"), "--prepare-branch-review", branch]
    if base:
        cmd.extend(["--base", base])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if r.returncode == 0:
        return {"status": "PASS", "output": r.stdout}
    return {"status": "FAIL", "output": r.stdout, "error": r.stderr}


def review_packet(packet_path):
    ledger = _load_p1_module("interface_approval_ledger")
    if hasattr(ledger, "review_packet"):
        return ledger.review_packet(packet_path)
    return {"status": "FAIL", "error": "review_packet not found"}


def approve_packet(packet_path, phrase):
    ledger = _load_p1_module("interface_approval_ledger")
    if hasattr(ledger, "approve_packet"):
        return ledger.approve_packet(packet_path, phrase)
    return {"status": "FAIL", "error": "approve_packet not found"}


def reject_packet(packet_path, note=""):
    ledger = _load_p1_module("interface_approval_ledger")
    if hasattr(ledger, "reject_packet"):
        return ledger.reject_packet(packet_path, note)
    return {"status": "FAIL", "error": "reject_packet not found"}
