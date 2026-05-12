import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent

ACTIVE_FORBIDDEN_PATTERNS = [
    "shell=True",
    "os.system",
    "os.popen",
    "subprocess.Popen",
    "eval(",
    "exec(",
]

FLAGGED_COMMANDS = [
    "git push",
    "git merge",
    "gh pr",
]

BROAD_FLAGS = [
    "deploy",
    "os.environ",
]


def _get_docstring_ranges(source):
    ranges = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
            ds = ast.get_docstring(node, clean=False)
            if ds and node.body:
                first = node.body[0]
                if isinstance(first, ast.Expr) and isinstance(first.value, (ast.Constant, ast.Str)):
                    start_line = first.lineno
                    end_line = getattr(first, "end_lineno", start_line)
                    ranges.append((start_line, end_line))
    return ranges


def _is_in_docstring(line_no, docstring_ranges):
    for start, end in docstring_ranges:
        if start <= line_no <= end:
            return True
    return False


def _is_comment_line(line):
    stripped = line.strip()
    return stripped.startswith("#") or stripped == ""


def _is_string_literal_line(line, source):
    stripped = line.strip()
    if stripped.startswith(('"', "'", 'f"', "f'")):
        return True
    if "=" in stripped:
        parts = stripped.split("=", 1)
        val = parts[1].strip()
        if val.startswith(('"', "'", 'f"', "f'")):
            return True
    return False


def scan_source_files(source_dir=None):
    if source_dir is None:
        source_dir = ROOT
    source_dir = Path(source_dir)
    files_scanned = []
    active_forbidden_findings = []
    allowed_label_findings = []

    for pyfile in sorted(source_dir.glob("*.py")):
        files_scanned.append(pyfile.name)
        source = pyfile.read_text()
        lines = source.splitlines()

        try:
            docstring_ranges = _get_docstring_ranges(source)
        except SyntaxError:
            docstring_ranges = []

        for line_no, line in enumerate(lines, 1):
            raw_stripped = line.strip()

            if _is_comment_line(line):
                continue

            in_docstring = _is_in_docstring(line_no, docstring_ranges)
            is_string = _is_string_literal_line(line, source)

            for pat in ACTIVE_FORBIDDEN_PATTERNS:
                if pat in raw_stripped:
                    if in_docstring or is_string:
                        allowed_label_findings.append({
                            "file": pyfile.name,
                            "line": line_no,
                            "pattern": pat,
                            "context": raw_stripped[:80],
                            "reason": "found in string literal or docstring",
                        })
                    else:
                        active_forbidden_findings.append({
                            "file": pyfile.name,
                            "line": line_no,
                            "pattern": pat,
                            "context": raw_stripped[:80],
                            "severity": "high",
                        })

            for cmd in FLAGGED_COMMANDS:
                if cmd in raw_stripped:
                    if in_docstring or is_string:
                        allowed_label_findings.append({
                            "file": pyfile.name,
                            "line": line_no,
                            "pattern": cmd,
                            "context": raw_stripped[:80],
                            "reason": "found in string literal or docstring",
                        })
                    elif raw_stripped.startswith("#"):
                        continue
                    else:
                        active_forbidden_findings.append({
                            "file": pyfile.name,
                            "line": line_no,
                            "pattern": cmd,
                            "context": raw_stripped[:80],
                            "severity": "high",
                        })

            for flag in BROAD_FLAGS:
                if flag in raw_stripped:
                    if in_docstring or is_string:
                        allowed_label_findings.append({
                            "file": pyfile.name,
                            "line": line_no,
                            "pattern": flag,
                            "context": raw_stripped[:80],
                            "reason": "found in string literal or docstring",
                        })

    if active_forbidden_findings:
        status = "FAIL"
    elif allowed_label_findings:
        status = "WARNING"
    else:
        status = "PASS"

    return {
        "status": status,
        "active_forbidden_findings": active_forbidden_findings,
        "allowed_label_findings": allowed_label_findings,
        "files_scanned": files_scanned,
        "notes": [],
    }
