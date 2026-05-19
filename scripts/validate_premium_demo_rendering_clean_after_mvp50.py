#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "13_web_dashboard" / "dist"
INDEX = DIST / "index.html"
DEMO_DIR = DIST / "demo"

EXPECTED_DEMO_PAGES = [
    "index.html",
    "presentation.html",
    "system-story.html",
    "system-scale.html",
    "agent-hierarchy.html",
    "operating-model.html",
    "validator-safety-map.html",
    "safety-boundaries.html",
    "technical-appendix.html",
    "objections.html",
    "review.html",
]

FORBIDDEN_PHRASES = [
    "backend does not exist",
    "backend missing",
    "no backend integration",
    "backend integration is planned",
    "backend integration remains a later phase",
]

REQUIRED_INDEX_PHRASES = [
    "View Stakeholder Demo Hub",
    "/demo/",
    "Backend/Supabase readiness architecture exists",
    "Live backend runtime is disabled",
    "Public writes are disabled",
    "Supabase writes are disabled",
    "service-role usage",
]


class VisibleTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._skip_depth = 0
        self.chunks = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._skip_depth == 0:
            self.chunks.append(data)


def fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        fail(f"unable to read {path}: {exc}")


def visible_text(path):
    parser = VisibleTextParser()
    parser.feed(read_text(path))
    parser.close()
    return "\n".join(parser.chunks)


def assert_no_visible_newline_artifacts(path):
    text = visible_text(path)
    for line in text.splitlines():
        if "\\n" in line:
            fail(f"visible literal newline artifact found in {path}: {line.strip()!r}")


def assert_required_index_language():
    text = read_text(INDEX)
    for phrase in REQUIRED_INDEX_PHRASES:
        if phrase not in text:
            fail(f"required phrase missing from {INDEX}: {phrase}")

    lower = text.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in lower:
            fail(f"forbidden backend phrasing found in {INDEX}: {phrase}")


def assert_demo_pages():
    if not DEMO_DIR.is_dir():
        fail(f"demo directory missing: {DEMO_DIR}")

    for name in EXPECTED_DEMO_PAGES:
        path = DEMO_DIR / name
        if not path.is_file():
            fail(f"missing demo page: {path}")
        assert_no_visible_newline_artifacts(path)
        lower = read_text(path).lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase in lower:
                fail(f"forbidden backend phrasing found in {path}: {phrase}")


def assert_diff_scope():
    tracked = subprocess.run(
        ["git", "-C", str(ROOT), "diff", "--name-only"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    untracked = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "--others", "--exclude-standard"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    changed = [line.strip() for line in tracked + untracked if line.strip()]
    allowed = {
        "13_web_dashboard/dashboard_renderer.py",
        "13_web_dashboard/dist/index.html",
        "09_exports/mvp_product_track/premium_demo_rendering_clean_after_mvp50_report.md",
        "scripts/validate_premium_demo_rendering_clean_after_mvp50.py",
    }
    forbidden_prefixes = (
        "netlify/functions/",
        "endpoints/",
        "endpoint/",
        "api/",
        "packages/",
        ".env",
        "supabase/.temp",
        "mvp51",
        "mvp-51",
    )
    for path in changed:
        if path in allowed:
            continue
        if path.startswith("13_web_dashboard/dist/demo/"):
            fail(f"unexpected demo page change in rendering cleanup branch: {path}")
        if any(part in path for part in forbidden_prefixes):
            fail(f"forbidden path changed: {path}")
        if path.endswith(".json") and "dist/" in path:
            fail(f"unexpected generated JSON changed: {path}")
        if path.endswith(".html") and path.startswith("13_web_dashboard/dist/") and path != "13_web_dashboard/dist/index.html":
            fail(f"unexpected generated HTML changed: {path}")
        fail(f"unexpected file changed: {path}")


def main():
    if not INDEX.is_file():
        fail(f"missing dashboard index: {INDEX}")

    assert_no_visible_newline_artifacts(INDEX)
    assert_required_index_language()
    assert_demo_pages()
    assert_diff_scope()

    print("PREMIUM_DEMO_RENDERING_CLEAN_AFTER_MVP50_VALIDATION_PASS")


if __name__ == "__main__":
    main()
