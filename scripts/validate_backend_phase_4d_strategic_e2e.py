#!/usr/bin/env python3
import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

VALIDATOR_CHAIN = [
    "scripts/validate_backend_phase_4d_schema_previews.py",
    "scripts/validate_backend_phase_4d_disabled_ui.py",
    "scripts/validate_backend_phase_4d_strategic_build.py",
    "scripts/validate_backend_phase_4c_snapshot.py",
    "scripts/validate_backend_phase_4d_gate_review.py",
    "scripts/validate_backend_phase_4c_planning.py",
    "scripts/validate_backend_phase_4b_planning.py",
    "scripts/validate_backend_phase_4a_foundation.py",
]

DANGEROUS_TEXT_PATTERNS = [
    "child_process",
    "process.env",
    "workflow_dispatch",
    "merge_pull_request",
    "create_pull_request",
    "update_file",
    "delete_file",
    "netlify deploy",
    "deploy_controls true",
    "merge_controls true",
    "push_controls true",
]

JS_DANGEROUS_PATTERNS = [
    "api.github.com",
    "api.netlify.com",
    "github.com/repos",
    "netlify.com/api",
]

SCAN_PATHS = [
    ROOT / "13_web_dashboard",
    ROOT / "14_backend",
    ROOT / "scripts" / "validate_backend_phase_4d_schema_previews.py",
    ROOT / "scripts" / "validate_backend_phase_4d_disabled_ui.py",
    ROOT / "scripts" / "validate_backend_phase_4d_strategic_build.py",
    ROOT / "scripts" / "validate_backend_phase_4d_strategic_e2e.py",
]


def _fail(message):
    print(f"ERROR: {message}")
    sys.exit(1)


def _run(path):
    return subprocess.run([sys.executable, str(ROOT / path)], capture_output=True, text=True)


def _should_scan(path):
    if path.is_dir():
        return False
    if path.suffix not in {".py", ".js", ".html", ".css", ".json"}:
        return False
    return True


def _scan_python_ast(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    rel = path.relative_to(ROOT)
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        _fail(f"Syntax error while scanning {rel}: {exc}")

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in {"requests", "urllib", "socket"}:
                    _fail(f"Dangerous import found in {rel}: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module in {"requests", "urllib", "socket", "child_process"}:
                _fail(f"Dangerous import-from found in {rel}: {node.module}")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                owner = getattr(node.func.value, "id", "")
                attr = node.func.attr
                if owner == "os" and attr in {"system", "getenv"}:
                    _fail(f"Dangerous os call found in {rel}: os.{attr}")
                if owner == "subprocess" and attr == "run":
                    if "scripts/validate_backend_phase_4d_" not in str(rel).replace("\\", "/"):
                        _fail(f"Unauthorized subprocess.run found in {rel}")
            elif isinstance(node.func, ast.Name):
                if node.func.id in {"exec", "eval"}:
                    _fail(f"Dangerous builtin call found in {rel}: {node.func.id}")
        elif isinstance(node, ast.Attribute):
            owner = getattr(node.value, "id", "")
            if owner == "os" and node.attr == "environ":
                _fail(f"Dangerous os.environ access found in {rel}")


def _scan_file(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    rel = path.relative_to(ROOT)
    if path.suffix == ".py":
        _scan_python_ast(path)
    else:
        for pattern in DANGEROUS_TEXT_PATTERNS:
            if pattern in text:
                _fail(f"Dangerous pattern found in {rel}: {pattern}")
    if path.suffix in {".js", ".html"}:
        for pattern in JS_DANGEROUS_PATTERNS:
            if pattern in text:
                _fail(f"Dangerous external integration pattern found in {rel}: {pattern}")
    if path.suffix == ".json":
        lowered = text.lower()
        for pattern in ["deploy_controls\": true", "merge_controls\": true", "push_controls\": true"]:
            if pattern in lowered:
                _fail(f"Dangerous true control flag found in {rel}: {pattern}")


def _scan_paths():
    for scan_path in SCAN_PATHS:
        if scan_path.is_dir():
            for path in scan_path.rglob("*"):
                if _should_scan(path):
                    _scan_file(path)
        elif scan_path.exists():
            _scan_file(scan_path)


def main():
    for validator in VALIDATOR_CHAIN:
        result = _run(validator)
        if result.returncode != 0:
            _fail(f"{validator} failed: {result.stdout}{result.stderr}")

    _scan_paths()

    report = (ROOT / "09_exports/backend_phase_4/backend_phase_4d_strategic_build_acceptance_report.md").read_text(encoding="utf-8")
    if "PASS_WITH_HIGH_CONFIDENCE" not in report:
        _fail("Strategic build acceptance report missing required verdict")

    html = (ROOT / "13_web_dashboard/dist/index.html").read_text(encoding="utf-8")
    for forbidden in ["http://", "https://", "fetch(\"https://", "fetch('https://"]:
        if forbidden in html:
            _fail(f"Forbidden external reference found in dashboard HTML: {forbidden}")

    print("BACKEND_PHASE_4D_STRATEGIC_E2E_VALIDATION_PASS")


if __name__ == "__main__":
    main()
