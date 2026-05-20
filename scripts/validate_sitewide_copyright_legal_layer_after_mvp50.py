#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "13_web_dashboard" / "dist"

TARGET_PAGES = [
    DIST / "index.html",
    DIST / "dashboard.html",
    DIST / "full-audit-dashboard.html",
    DIST / "internal" / "full-audit-dashboard.html",
    DIST / "legal.html",
    DIST / "copyright.html",
    DIST / "demo" / "index.html",
    DIST / "demo" / "presentation.html",
    DIST / "demo" / "simulator.html",
    DIST / "demo" / "system-story.html",
    DIST / "demo" / "system-scale.html",
    DIST / "demo" / "agent-hierarchy.html",
    DIST / "demo" / "agent-registry.html",
    DIST / "demo" / "operating-model.html",
    DIST / "demo" / "validator-safety-map.html",
    DIST / "demo" / "safety-boundaries.html",
    DIST / "demo" / "technical-appendix.html",
    DIST / "demo" / "objections.html",
    DIST / "demo" / "review.html",
]

REQUIRED_FILES = [
    DIST / "legal.html",
    DIST / "copyright.html",
    DIST / "_redirects",
    DIST / "demo" / "assets" / "demo.css",
]

FOOTER_RE = re.compile(r'<footer class="footer site-legal-footer">.*?</footer>', re.S)

DEMO_PAGES = {p for p in TARGET_PAGES if p.parent.name == "demo" and p.name != "index.html"}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


def read(path: Path) -> str:
    if not path.exists():
        fail(f"Missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def footer_block(text: str, path: Path) -> str:
    match = FOOTER_RE.search(text)
    if not match:
        fail(f"Missing site legal footer on {path.relative_to(ROOT)}")
    return match.group(0)


def hrefs_from_block(block: str) -> list[str]:
    return re.findall(r'href="([^"]+)"', block)


def normalize_target(page: Path, href: str) -> Path | None:
    parsed = urlparse(href)
    if parsed.scheme or parsed.netloc:
        return None
    if href.startswith("#") or href.startswith("mailto:"):
        return None
    clean = href.split("#", 1)[0].split("?", 1)[0]
    target = (page.parent / clean).resolve()
    return target


def assert_contains(text: str, needle: str, path: Path) -> None:
    if needle not in text:
        fail(f"Missing required text on {path.relative_to(ROOT)}: {needle}")


def assert_not_contains(text: str, needle: str, path: Path) -> None:
    if needle in text:
        fail(f"Forbidden text found on {path.relative_to(ROOT)}: {needle}")


def check_footer_links(page: Path, footer: str, expected_hrefs: list[str]) -> None:
    hrefs = hrefs_from_block(footer)
    for expected in expected_hrefs:
        if expected not in hrefs:
            fail(f"Missing required footer link on {page.relative_to(ROOT)}: {expected}")
        resolved = normalize_target(page, expected)
        if resolved is not None and not resolved.exists():
            fail(
                f"Broken footer link on {page.relative_to(ROOT)}: {expected} -> {resolved.relative_to(ROOT) if resolved.is_relative_to(ROOT) else resolved}"
            )


def check_page(page: Path, expected_hrefs: list[str]) -> None:
    text = read(page)
    head = text.split("</head>", 1)[0]
    footer = footer_block(text, page)

    assert_contains(text, "site-legal-footer", page)
    assert_contains(text, "© 2026 Devin O’Rourke", page)
    assert_contains(text, "All rights reserved", page)
    assert_contains(text, "Legal / Copyright", page)
    assert_contains(footer, "site-legal-footer", page)
    check_footer_links(page, footer, expected_hrefs)

    if page in {
        DIST / "index.html",
        DIST / "dashboard.html",
        DIST / "full-audit-dashboard.html",
        DIST / "internal" / "full-audit-dashboard.html",
    }:
        assert_contains(head, ".site-legal-footer {", page)
        assert_contains(head, ".legal-links", page)
        assert_contains(head, ".legal-muted", page)

    assert_not_contains(text, "copyright registration", page)
    assert_not_contains(text, "claim of trademark registration", page)
    assert_not_contains(text, "claim of patent protection", page)
    assert_not_contains(text, "attorney review", page)
    assert_not_contains(text, "fake company ownership", page)
    assert_not_contains(text, "contact form", page)


def main() -> None:
    for path in REQUIRED_FILES:
        if not path.exists():
            fail(f"Missing required file: {path.relative_to(ROOT)}")

    css = read(DIST / "demo" / "assets" / "demo.css")
    for needle in [
        ".site-legal-footer",
        ".legal-page",
        ".legal-section",
        ".legal-links",
        "overflow-wrap",
    ]:
        assert_contains(css, needle, DIST / "demo" / "assets" / "demo.css")

    redirects = read(DIST / "_redirects")
    for needle in [
        "/legal /legal.html 200",
        "/copyright /copyright.html 200",
        "/demo/legal /legal.html 200",
        "/demo/copyright /copyright.html 200",
    ]:
        assert_contains(redirects, needle, DIST / "_redirects")

    page_expectations: dict[Path, list[str]] = {
        DIST / "index.html": ["./legal.html", "./index.html", "./demo/", "./full-audit-dashboard.html", "./copyright.html"],
        DIST / "dashboard.html": ["./legal.html", "./index.html", "./demo/", "./full-audit-dashboard.html", "./copyright.html"],
        DIST / "full-audit-dashboard.html": ["./legal.html", "./index.html", "./demo/", "./full-audit-dashboard.html", "./copyright.html"],
        DIST / "internal" / "full-audit-dashboard.html": ["../legal.html", "../index.html", "../demo/", "../full-audit-dashboard.html", "../copyright.html"],
        DIST / "legal.html": ["./legal.html", "./index.html", "./demo/", "./full-audit-dashboard.html", "./copyright.html"],
        DIST / "copyright.html": ["./legal.html", "./index.html", "./demo/", "./full-audit-dashboard.html"],
        DIST / "demo" / "index.html": ["../legal.html", "../index.html", "./index.html", "../full-audit-dashboard.html", "../copyright.html"],
        DIST / "demo" / "presentation.html": ["../legal.html", "../index.html", "./index.html", "../full-audit-dashboard.html", "../copyright.html"],
        DIST / "demo" / "simulator.html": ["../legal.html", "../index.html", "./index.html", "../full-audit-dashboard.html", "../copyright.html"],
        DIST / "demo" / "system-story.html": ["../legal.html", "../index.html", "./index.html", "../full-audit-dashboard.html", "../copyright.html"],
        DIST / "demo" / "system-scale.html": ["../legal.html", "../index.html", "./index.html", "../full-audit-dashboard.html", "../copyright.html"],
        DIST / "demo" / "agent-hierarchy.html": ["../legal.html", "../index.html", "./index.html", "../full-audit-dashboard.html", "../copyright.html"],
        DIST / "demo" / "agent-registry.html": ["../legal.html", "../index.html", "./index.html", "../full-audit-dashboard.html", "../copyright.html"],
        DIST / "demo" / "operating-model.html": ["../legal.html", "../index.html", "./index.html", "../full-audit-dashboard.html", "../copyright.html"],
        DIST / "demo" / "validator-safety-map.html": ["../legal.html", "../index.html", "./index.html", "../full-audit-dashboard.html", "../copyright.html"],
        DIST / "demo" / "safety-boundaries.html": ["../legal.html", "../index.html", "./index.html", "../full-audit-dashboard.html", "../copyright.html"],
        DIST / "demo" / "technical-appendix.html": ["../legal.html", "../index.html", "./index.html", "../full-audit-dashboard.html", "../copyright.html"],
        DIST / "demo" / "objections.html": ["../legal.html", "../index.html", "./index.html", "../full-audit-dashboard.html", "../copyright.html"],
        DIST / "demo" / "review.html": ["../legal.html", "../index.html", "./index.html", "../full-audit-dashboard.html", "../copyright.html"],
    }

    for page, expected in page_expectations.items():
        check_page(page, expected)

    legal = read(DIST / "legal.html")
    for needle in [
        "Legal / Copyright Notice",
        "© 2026 Devin O’Rourke. All rights reserved.",
        "Protected Materials",
        "No License Granted",
        "Static Demo Boundary",
        "Registered Agents vs Live Runtime",
        "Third-Party References",
        "Portfolio / Review Use",
        "Non-Legal Advice Note",
        "Live runtime agents enabled: 0",
        "Runtime activation has not started",
        "does not run live agents",
        "does not execute commands",
        "does not write to Supabase",
        "written permission",
    ]:
        assert_contains(legal, needle, DIST / "legal.html")

    copyright = read(DIST / "copyright.html")
    for needle in [
        "© 2026 Devin O’Rourke",
        "Legal / Copyright",
        "Open Legal / Copyright Notice",
    ]:
        assert_contains(copyright, needle, DIST / "copyright.html")

    print("SITEWIDE_COPYRIGHT_LEGAL_LAYER_AFTER_MVP50_VALIDATION_PASS")


if __name__ == "__main__":
    main()
