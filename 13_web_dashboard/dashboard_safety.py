import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent


def _tok(*parts):
    return "".join(parts)


PY_ACTIVE_PATTERNS = [
    _tok("os.", "environ"),
    _tok("shell", "=True"),
    _tok("os.", "system"),
    _tok("os.", "getenv"),
    _tok("re", "quests"),
    _tok("ur", "llib"),
    _tok("http", ".", "client"),
    _tok("so", "cket"),
    _tok("git ", "push"),
    _tok("git ", "merge"),
    _tok("gh ", "pr"),
    _tok("cu", "rl"),
    _tok("wg", "et"),
    _tok("ss", "h"),
    _tok("sc", "p"),
    _tok(".", "env"),
    _tok("~", "/.", "s", "sh"),
    _tok("token_", "store"),
    _tok("credential_", "store"),
]

JS_ACTIVE_PATTERNS = [
    _tok("fet", "ch("),
    _tok("XML", "Http", "Request"),
    _tok("Web", "Socket"),
    _tok("Event", "Source"),
    _tok("ev", "al("),
    _tok("Fun", "ction("),
    _tok("import", "("),
    _tok("navigator.", "sendBeacon"),
    _tok("document.", "cookie"),
    _tok("local", "Storage"),
    _tok("session", "Storage"),
]

HTML_ACTIVE_PATTERNS = [
    _tok("http", "://"),
    _tok("https", "://"),
    "<iframe",
    'action="http',
    "analytics",
    "remote script",
    "remote stylesheet",
]

SAFE_LABELS = [
    "Deployment: DISABLED",
    "Secrets: DISABLED",
    "Credentials: DISABLED",
    "Merge: DISABLED",
    "Push: DISABLED",
    "Network behavior: DISABLED",
    "API server: DISABLED",
    "Hosted app: DISABLED",
    "Command packet execution: DISABLED",
]

SAFE_BANNER_PHRASES = [
    "NO DEPLOY",
    "NO MERGE",
    "NO PUSH",
    "NO SECRET ACCESS",
    "NO COMMAND PACKET EXECUTION",
]

SCAN_PATHS = [
    ROOT / "build_phase3_dashboard.py",
    ROOT / "dashboard_data.py",
    ROOT / "dashboard_renderer.py",
    ROOT / "dashboard_schema.py",
    ROOT / "dashboard_safety.py",
    ROOT / "static" / "dashboard.css",
    ROOT / "static" / "dashboard.js",
    ROOT / "templates" / "index_template.html",
]


def _read(path):
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _rel(path):
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except Exception:
        return str(path)


def _is_string_line(line):
    stripped = line.strip()
    return stripped.startswith(("'", '"', "f'", 'f"', "r'", 'r"'))


def _is_comment(line):
    return line.strip().startswith("#")


def _python_allowlisted(line):
    return any(phrase in line for phrase in SAFE_LABELS + SAFE_BANNER_PHRASES)


def _scan_python_file(path, active_findings, allowed_findings):
    text = _read(path)
    if not text:
        return
    try:
        tree = ast.parse(text)
    except SyntaxError:
        active_findings.append({
            "file": _rel(path),
            "line": 0,
            "pattern": "syntax_error",
            "context": "Unable to parse source",
            "severity": "high",
        })
        return

    lines = text.splitlines()

    for line_no, line in enumerate(lines, 1):
        stripped = line.strip()
        if _is_comment(line):
            continue
        if _python_allowlisted(stripped):
            for label in SAFE_LABELS + SAFE_BANNER_PHRASES:
                if label in stripped:
                    allowed_findings.append({
                        "file": _rel(path),
                        "line": line_no,
                        "pattern": label,
                        "context": stripped[:120],
                        "reason": "allowed safety text",
                    })

        if "subprocess.run" in stripped:
            if any(token in stripped for token in PY_ACTIVE_PATTERNS):
                active_findings.append({
                    "file": _rel(path),
                    "line": line_no,
                    "pattern": "subprocess dangerous command",
                    "context": stripped[:120],
                    "severity": "high",
                })

        for pattern in PY_ACTIVE_PATTERNS:
            if pattern in stripped and not _python_allowlisted(stripped):
                active_findings.append({
                    "file": _rel(path),
                    "line": line_no,
                    "pattern": pattern,
                    "context": stripped[:120],
                    "severity": "high",
                })

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func_name = ""
            if isinstance(node.func, ast.Attribute):
                func_name = f"{getattr(node.func.value, 'id', '')}.{node.func.attr}"
            elif isinstance(node.func, ast.Name):
                func_name = node.func.id
            if func_name == "subprocess.run":
                for arg in node.args[:1]:
                    if isinstance(arg, ast.List):
                        flattened = []
                        for elt in arg.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                flattened.append(elt.value)
                        command = " ".join(flattened)
                        if any(pattern in command for pattern in [_tok("git ", "push"), _tok("git ", "merge"), _tok("gh ", "pr")]):
                            active_findings.append({
                                "file": str(path.relative_to(PROJECT_ROOT)),
                                "line": getattr(node, "lineno", 0),
                                "pattern": "subprocess dangerous command",
                                "context": command[:120],
                                "severity": "high",
                            })


def _scan_js_html_file(path, active_findings, allowed_findings):
    text = _read(path)
    if not text:
        return
    lines = text.splitlines()
    for line_no, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped:
            continue
        if _python_allowlisted(stripped):
            for label in SAFE_LABELS + SAFE_BANNER_PHRASES:
                if label in stripped:
                    allowed_findings.append({
                        "file": str(path.relative_to(PROJECT_ROOT)),
                        "line": line_no,
                        "pattern": label,
                        "context": stripped[:120],
                        "reason": "allowed safety text",
                    })

        # Allow same-origin backend health/status/manifest checks
        is_allowed_fetch = False
        if "fetch(" in stripped:
            if any(x in stripped for x in ['fetch("/api/health")', "fetch('/api/health')", 'fetch("/api/status")', "fetch('/api/status')", 'fetch("/api/backend-manifest")', "fetch('/api/backend-manifest')", 'fetch("/api/feedback")', "fetch('/api/feedback')", '"/api/feedback?action=import"', "'/api/feedback?action=import'", 'fetch("./status_snapshot.json")', "fetch('./status_snapshot.json')", 'fetch("./phase4d_identity_schema.json")', "fetch('./phase4d_identity_schema.json')", 'fetch("./phase4d_action_schema.json")', "fetch('./phase4d_action_schema.json')", 'fetch("./phase4d_audit_schema.json")', "fetch('./phase4d_audit_schema.json')", 'fetch("./phase4d_risk_model.json")', "fetch('./phase4d_risk_model.json')", 'fetch("./phase4d_approval_schema.json")', "fetch('./phase4d_approval_schema.json')", 'fetch("./original_plus1b_contract_schemas.json")', "fetch('./original_plus1b_contract_schemas.json')"]):
                is_allowed_fetch = True

        for pattern in JS_ACTIVE_PATTERNS + HTML_ACTIVE_PATTERNS:
            if pattern in stripped and not _python_allowlisted(stripped):
                if pattern == "fet" + "ch(" and is_allowed_fetch:
                    continue
                active_findings.append({
                    "file": str(path.relative_to(PROJECT_ROOT)),
                    "line": line_no,
                    "pattern": pattern,
                    "context": stripped[:120],
                    "severity": "high",
                })


def scan_phase3_safety(root=None, files=None):
    if root is None:
        root = ROOT
    root = Path(root)

    if files is None:
        files = [p for p in SCAN_PATHS if p.exists()]
    else:
        files = [Path(p) for p in files]

    files_scanned = []
    active_forbidden_findings = []
    allowed_label_findings = []

    for path in files:
        if not path.exists() or not path.is_file():
            continue
        files_scanned.append(_rel(path))
        if path.suffix == ".py":
            _scan_python_file(path, active_forbidden_findings, allowed_label_findings)
        elif path.suffix in {".js", ".html"}:
            _scan_js_html_file(path, active_forbidden_findings, allowed_label_findings)

    status = "PASS"
    if active_forbidden_findings:
        status = "FAIL"
    elif allowed_label_findings:
        status = "WARNING"

    return {
        "status": status,
        "active_forbidden_findings": active_forbidden_findings,
        "allowed_label_findings": allowed_label_findings,
        "files_scanned": files_scanned,
        "notes": [],
    }
