#!/usr/bin/env python3
"""Validate global demo overflow containment after MVP-50."""

from __future__ import annotations

from html import unescape
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "13_web_dashboard" / "dist"
DEMO_DIR = DIST / "demo"

ROOT_PAGE = DIST / "index.html"
DEMO_PAGES = [
    ("index.html", "Stakeholder Demo Hub", "Home → Demo Hub"),
    ("presentation.html", "Stakeholder Presentation", "Home → Demo Hub → Stakeholder Presentation"),
    ("simulator.html", "Command Center Sandbox Simulator", "Home → Demo Hub → Command Center Sandbox Simulator"),
    ("system-story.html", "System Story", "Home → Demo Hub → System Story"),
    ("system-scale.html", "System Scale", "Home → Demo Hub → System Scale"),
    ("agent-hierarchy.html", "Agent Hierarchy", "Home → Demo Hub → Agent Hierarchy"),
    ("agent-registry.html", "Agent Registry", "Home → Demo Hub → Agent Registry"),
    ("operating-model.html", "Operating Model", "Home → Demo Hub → Operating Model"),
    ("validator-safety-map.html", "Validator Map", "Home → Demo Hub → Validator Map"),
    ("safety-boundaries.html", "Safety Boundaries", "Home → Demo Hub → Safety Boundaries"),
    ("technical-appendix.html", "Technical Appendix", "Home → Demo Hub → Technical Appendix"),
    ("objections.html", "Objections", "Home → Demo Hub → Objections"),
    ("review.html", "Review / Scorecard", "Home → Demo Hub → Review / Scorecard"),
]

FILES = [
    ROOT_PAGE,
    *(DEMO_DIR / name for name, _, _ in DEMO_PAGES),
    DEMO_DIR / "assets" / "demo.css",
    DEMO_DIR / "assets" / "demo.js",
]

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def check(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def get_tag_opening(html: str, selector: str) -> str | None:
    match = re.search(selector, html, re.I | re.S)
    return match.group(0) if match else None


def extract_tag_inner(html: str, pattern: str) -> str | None:
    match = re.search(pattern, html, re.I | re.S)
    return match.group(1) if match else None


def hrefs_in_html(html: str) -> list[str]:
    return re.findall(r'href=["\']([^"\']+)["\']', html, re.I)


def resolve_href(page: Path, href: str) -> Path | None:
    if not href or href.startswith("#"):
        return None
    if href.startswith(("mailto:", "tel:")):
        return None
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", href):
        return None
    resolved = (page.parent / href).resolve()
    try:
        resolved.relative_to(DIST)
    except ValueError:
        return None
    return resolved


def validate_root_page() -> None:
    html = read_text(ROOT_PAGE)
    check("width: min(100% - 2rem, 1280px)" in html, "root page missing centered shell width containment")
    check("grid-template-columns: repeat(auto-fit, minmax(min(320px, 100%), 1fr))" in html, "root page missing responsive hero grid")
    check("white-space: normal" in html, "root page missing wrapping nav/button text rule")
    check("overflow-wrap: anywhere" in html, "root page missing overflow wrap rule")
    check("@media (max-width: 900px)" in html, "root page missing 900px mobile containment rule")
    check("nav-links" in html, "root page missing launchpad navigation")
    check("Command Center Launchpad" in html, "root page missing launchpad title")
    check("Premium Stakeholder Demo" in html, "root page missing premium demo label")
    check("Exact agent count: 47,979" in html, "root page missing exact agent count")
    check("Exact department count: 1,777" in html, "root page missing exact department count")

    for href in hrefs_in_html(html):
        target = resolve_href(ROOT_PAGE, href)
        if target is None:
            continue
        check(target.exists(), f"root page broken internal link: {href} -> {target.relative_to(ROOT)}")


def validate_demo_page(name: str, title: str, breadcrumb: str) -> None:
    page = DEMO_DIR / name
    html = read_text(page)
    path_label = f"demo/{name}"

    check("data-collapsible-menu" in html, f"{path_label} missing collapsible menu root")
    check('data-action="toggle-menu"' in html, f"{path_label} missing toggle-menu action")
    check('aria-expanded="false"' in html, f"{path_label} missing collapsed menu state")
    check('aria-controls="demo-menu-panel"' in html, f"{path_label} missing menu aria-controls")
    check('data-menu-panel' in html, f"{path_label} missing menu panel")
    check('hidden' in html.lower(), f"{path_label} missing hidden menu state")
    check("breadcrumb" in html.lower(), f"{path_label} missing breadcrumb")
    check(title in html, f"{path_label} missing current page title")
    check(breadcrumb in clean_text(html), f"{path_label} breadcrumb incorrect")
    check("Home → Demo Hub → Demo Hub" not in clean_text(html), f"{path_label} has duplicate Demo Hub breadcrumb")
    check("Current build: static preview" not in html, f"{path_label} contains stale preview copy")
    check("Backend integration: planned" not in html, f"{path_label} contains backend integration planned copy")
    check("agent count unknown" not in html, f"{path_label} contains unknown agent count copy")
    check("UNKNOWN_NOT_CURRENTLY_DECLARED" not in html, f"{path_label} contains UNKNOWN_NOT_CURRENTLY_DECLARED")
    check("MVP-51 in progress" not in html, f"{path_label} contains MVP-51 in progress copy")
    check("\\n" not in html, f"{path_label} contains literal newline escape")
    check("{_list(" not in html, f"{path_label} contains templating artifact {{_list(}}")
    check("{_stat(" not in html, f"{path_label} contains templating artifact {{_stat(}}")
    check("{_badge(" not in html, f"{path_label} contains templating artifact {{_badge(}}")
    check('class="nav-links"' not in html, f"{path_label} still contains always-visible nav-links")

    menu_panel = extract_tag_inner(html, r"<nav\b[^>]*data-menu-panel[^>]*>(.*?)</nav>")
    check(menu_panel is not None, f"{path_label} missing menu panel markup")
    if menu_panel is not None:
        required_links = [
            ("Home", "../index.html"),
            ("Demo Hub", "./index.html"),
            ("Presentation", "./presentation.html"),
            ("Simulator", "./simulator.html"),
            ("System Story", "./system-story.html"),
            ("System Scale", "./system-scale.html"),
            ("Agent Hierarchy", "./agent-hierarchy.html"),
            ("Agent Registry", "./agent-registry.html"),
            ("Operating Model", "./operating-model.html"),
            ("Validator Map", "./validator-safety-map.html"),
            ("Safety Boundaries", "./safety-boundaries.html"),
            ("Technical Appendix", "./technical-appendix.html"),
            ("Objections", "./objections.html"),
            ("Review", "./review.html"),
            ("Full Audit Dashboard", "../full-audit-dashboard.html"),
        ]
        for label, href in required_links:
            pattern = rf'href=["\']{re.escape(href)}["\'][^>]*>\s*{re.escape(label)}\s*<'
            check(re.search(pattern, menu_panel, re.I | re.S) is not None, f"{path_label} missing menu link {label} -> {href}")

    nav_count = len(re.findall(r"<nav\b", html, re.I))
    check(nav_count == 2, f"{path_label} should have exactly 2 nav elements (menu + breadcrumb), found {nav_count}")

    breadcrumb_count = len(re.findall(r'<nav\b[^>]*aria-label=["\']Breadcrumb["\']', html, re.I))
    check(breadcrumb_count == 1, f"{path_label} should have exactly one breadcrumb nav, found {breadcrumb_count}")

    has_main_shell = any(token in html for token in ('class="demo-shell"', "class='demo-shell'", "class=\"page-shell\"", "<main"))
    check(has_main_shell, f"{path_label} missing main/page shell container")

    # Validate internal links are resolvable from the file system.
    for href in hrefs_in_html(html):
        target = resolve_href(page, href)
        if target is None:
            continue
        check(target.exists(), f"{path_label} broken internal link: {href} -> {target.relative_to(ROOT)}")

    if name == "system-scale.html":
        check("Exact agent count: 47,979" in html, f"{path_label} missing exact agent count")
        check("Exact department count: 1,777" in html, f"{path_label} missing exact department count")
        check("System Scale" in clean_text(html), f"{path_label} missing System Scale breadcrumb/title text")
        check("Home → Demo Hub → Demo Hub" not in clean_text(html), f"{path_label} still has Demo Hub breadcrumb bug")
        if "<table" in html.lower():
            wrapped = any(token in html for token in ("table-wrap", "table-scroll", "table-container"))
            check(wrapped, f"{path_label} table is not wrapped or contained")


def validate_css() -> None:
    css = read_text(DEMO_DIR / "assets" / "demo.css")
    required = [
        "box-sizing: border-box",
        "overflow-x: hidden",
        "overflow-wrap: anywhere",
        "min-width: 0",
        "max-width: 100%",
        ".menu-panel[hidden]",
        "display: none !important",
        ".table-scroll",
        "overflow-x: auto",
        "white-space: pre-wrap",
        "grid-template-columns: repeat(auto-fit",
        "@media (max-width: 900px)",
        "clamp(",
    ]
    for snippet in required:
        check(snippet in css, f"demo.css missing required containment snippet: {snippet}")

    for snippet in [
        ".collapsible-topbar",
        ".topbar-main",
        ".breadcrumb",
        ".menu-panel.is-open",
        ".menu-panel a",
        ".card-grid > *",
        ".page-grid > *",
        ".table-wrap",
        ".data-table",
        "white-space: pre-wrap",
    ]:
        check(snippet in css, f"demo.css missing expected containment rule: {snippet}")


def validate_js() -> None:
    js = read_text(DEMO_DIR / "assets" / "demo.js")
    required = [
        "initCollapsibleMenu",
        "data-collapsible-menu",
        "data-action='toggle-menu'",
        "data-menu-panel",
        "aria-expanded",
        "panel.hidden",
        "is-open",
        "Escape",
        "addEventListener",
    ]
    for snippet in required:
        check(snippet in js, f"demo.js missing required navigation behavior: {snippet}")

    forbidden = [
        "fetch(",
        "XMLHttpRequest",
        "WebSocket",
        "EventSource",
        "localStorage",
        "sessionStorage",
        "document.cookie",
        "indexedDB",
        "navigator.sendBeacon",
        "serviceWorker",
        "eval(",
        "new Function",
    ]
    for token in forbidden:
        check(token not in js, f"demo.js contains forbidden browser/API token: {token}")


def main() -> int:
    for path in FILES:
        check(path.exists(), f"Missing required file: {path.relative_to(ROOT)}")

    validate_root_page()
    validate_css()
    validate_js()

    for name, title, breadcrumb in DEMO_PAGES:
        validate_demo_page(name, title, breadcrumb)

    if errors:
        for error in errors:
            print(error)
        return 1

    print("GLOBAL_DEMO_OVERFLOW_CONTAINMENT_AFTER_MVP50_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
