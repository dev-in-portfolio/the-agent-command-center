#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "13_web_dashboard" / "dist"
DEMO = DIST / "demo"

PAGES = {
    "index.html": {
        "title": "Stakeholder Demo Hub",
        "breadcrumb": ["Home", "Demo Hub"],
    },
    "presentation.html": {
        "title": "Stakeholder Presentation",
        "breadcrumb": ["Home", "Demo Hub", "Stakeholder Presentation"],
    },
    "simulator.html": {
        "title": "Command Center Sandbox Simulator",
        "breadcrumb": ["Home", "Demo Hub", "Command Center Sandbox Simulator"],
    },
    "system-story.html": {
        "title": "System Story",
        "breadcrumb": ["Home", "Demo Hub", "System Story"],
    },
    "system-scale.html": {
        "title": "System Scale",
        "breadcrumb": ["Home", "Demo Hub", "System Scale"],
    },
    "agent-hierarchy.html": {
        "title": "Agent Hierarchy",
        "breadcrumb": ["Home", "Demo Hub", "Agent Hierarchy"],
    },
    "agent-registry.html": {
        "title": "Agent Registry",
        "breadcrumb": ["Home", "Demo Hub", "Agent Registry"],
    },
    "operating-model.html": {
        "title": "Operating Model",
        "breadcrumb": ["Home", "Demo Hub", "Operating Model"],
    },
    "validator-safety-map.html": {
        "title": "Validator Map",
        "breadcrumb": ["Home", "Demo Hub", "Validator Map"],
    },
    "safety-boundaries.html": {
        "title": "Safety Boundaries",
        "breadcrumb": ["Home", "Demo Hub", "Safety Boundaries"],
    },
    "technical-appendix.html": {
        "title": "Technical Appendix",
        "breadcrumb": ["Home", "Demo Hub", "Technical Appendix"],
    },
    "objections.html": {
        "title": "Objections",
        "breadcrumb": ["Home", "Demo Hub", "Objections"],
    },
    "review.html": {
        "title": "Review / Scorecard",
        "breadcrumb": ["Home", "Demo Hub", "Review / Scorecard"],
    },
}

MENU_ITEMS = [
    ("../index.html", "Home"),
    ("./index.html", "Demo Hub"),
    ("./presentation.html", "Presentation"),
    ("./simulator.html", "Simulator"),
    ("./system-story.html", "System Story"),
    ("./system-scale.html", "System Scale"),
    ("./agent-hierarchy.html", "Agent Hierarchy"),
    ("./agent-registry.html", "Agent Registry"),
    ("./operating-model.html", "Operating Model"),
    ("./validator-safety-map.html", "Validator Map"),
    ("./safety-boundaries.html", "Safety Boundaries"),
    ("./technical-appendix.html", "Technical Appendix"),
    ("./objections.html", "Objections"),
    ("./review.html", "Review"),
    ("../full-audit-dashboard.html", "Full Audit Dashboard"),
]

REQUIRED_CSS = [
    ".menu-panel[hidden]",
    "display: none !important",
    ".menu-panel.is-open",
    ".collapsible-topbar",
    "position: sticky",
    ".topbar-main",
    "justify-content: space-between",
    ".breadcrumb",
    "@media (max-width: 768px)",
]

REQUIRED_JS = [
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

FORBIDDEN_HTML = [
    "href=\"#\"",
    "href=''",
    'href=""',
    "Home → Demo Hub → Demo Hub",
    "{_list(",
    "{_stat(",
    "{_badge(",
    "Current build: static preview",
    "Backend integration: planned",
    "agent count unknown",
    "UNKNOWN_NOT_CURRENTLY_DECLARED",
    "MVP-51 in progress",
]


def read(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"MISSING_FILE {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def normalize_path(href: str, source: Path) -> Path | None:
    href = href.strip()
    if not href:
        return None
    parsed = urlparse(href)
    if parsed.scheme or parsed.netloc:
        return None
    if href.startswith("#"):
        return None
    raw = href.split("#", 1)[0].split("?", 1)[0]
    if not raw:
        return None
    return (source.parent / raw).resolve()


def strip_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def main() -> None:
    css = read(DEMO / "assets" / "demo.css")
    js = read(DEMO / "assets" / "demo.js")
    for needle in REQUIRED_CSS:
        ensure(needle in css, f"CSS_MISSING {needle}")
    for needle in REQUIRED_JS:
        ensure(needle in js, f"JS_MISSING {needle}")

    for filename, meta in PAGES.items():
        path = DEMO / filename
        html = read(path)

        for needle in FORBIDDEN_HTML:
            ensure(needle not in html, f"HTML_FORBIDDEN {filename} {needle}")

        ensure(html.count('aria-label="Breadcrumb"') == 1, f"BREADCRUMB_COUNT {filename}")
        ensure(html.count('data-collapsible-menu') == 1, f"MENU_ROOT_COUNT {filename}")
        ensure(html.count('data-menu-panel') == 1, f"MENU_PANEL_COUNT {filename}")
        ensure('aria-expanded="false"' in html, f"MENU_NOT_COLLAPSED_BY_DEFAULT {filename}")
        ensure('hidden' in html, f"MENU_PANEL_NOT_HIDDEN {filename}")
        ensure('Menu' in html, f"MENU_LABEL_MISSING {filename}")

        title = meta["title"]
        title_snippet = re.compile(
            r'<a class="topbar-title" href="\./index\.html">\s*' + re.escape(title) + r'\s*</a>',
            re.S,
        )
        ensure(title_snippet.search(html) is not None, f"TOPBAR_TITLE_MISSING {filename}")

        breadcrumb = re.search(
            r'<nav\b[^>]*class="breadcrumb"[^>]*>(.*?)</nav>',
            html,
            re.S | re.I,
        )
        ensure(breadcrumb is not None, f"BREADCRUMB_MISSING {filename}")
        breadcrumb_html = breadcrumb.group(1)
        for crumb in meta["breadcrumb"]:
            ensure(crumb in breadcrumb_html, f"BREADCRUMB_TEXT_MISSING {filename} {crumb}")
        if filename == "index.html":
            ensure("Home" in breadcrumb_html and "Demo Hub" in breadcrumb_html, f"INDEX_BREADCRUMB_BAD {filename}")
            ensure("Stakeholder Demo Hub" not in breadcrumb_html, f"INDEX_BREADCRUMB_TOO_LONG {filename}")
        else:
            ensure(title in breadcrumb_html, f"CURRENT_PAGE_BREADCRUMB_MISSING {filename}")
            ensure("Home → Demo Hub → Demo Hub" not in html, f"DUPLICATE_DEMO_HUB_BREADCRUMB {filename}")

        menu = re.search(
            r'<nav\b[^>]*id="demo-menu-panel"[^>]*>(.*?)</nav>',
            html,
            re.S | re.I,
        )
        ensure(menu is not None, f"MENU_PANEL_MISSING {filename}")
        menu_html = menu.group(1)
        ensure('hidden' in menu.group(0), f"MENU_PANEL_NOT_HIDDEN_DEFAULT {filename}")
        for href, label in MENU_ITEMS:
            ensure(label in menu_html, f"MENU_LABEL_MISSING {filename} {label}")
            ensure(href in menu_html, f"MENU_HREF_MISSING {filename} {href}")

        nav_blocks = list(re.finditer(r'<nav\b[^>]*>(.*?)</nav>', html, re.S | re.I))
        ensure(len(nav_blocks) == 2, f"EXTRA_NAV_BLOCKS {filename}")
        for block in nav_blocks:
            text = block.group(1)
            if text == breadcrumb_html or text == menu_html:
                continue
            raise SystemExit(f"ALWAYS_VISIBLE_NAV_STILL_PRESENT {filename}")

        for href in re.findall(r'href="([^"]+)"', html):
            target = normalize_path(href, path)
            if target is None:
                continue
            ensure(target.exists(), f"BROKEN_LINK {filename} -> {href}")
            ensure(DIST in target.parents or target == DIST, f"LINK_OUTSIDE_DIST {filename} -> {href}")

    print("GLOBAL_DEMO_COLLAPSIBLE_MENU_BREADCRUMBS_AFTER_MVP50_VALIDATION_PASS")


if __name__ == "__main__":
    main()
