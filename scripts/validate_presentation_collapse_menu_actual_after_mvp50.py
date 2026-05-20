#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "html": ROOT / "13_web_dashboard/dist/demo/presentation.html",
    "css": ROOT / "13_web_dashboard/dist/demo/assets/demo.css",
    "js": ROOT / "13_web_dashboard/dist/demo/assets/demo.js",
}

REQUIRED_HTML_STRINGS = [
    'data-collapsible-menu',
    'data-action="toggle-menu"',
    'aria-expanded="false"',
    'aria-controls="presentation-menu-panel"',
    'id="presentation-menu-panel"',
    'data-menu-panel',
    'hidden',
    'Stakeholder Presentation',
    'Menu',
    'Home',
    'Demo Hub',
    'Simulator',
    'System Story',
    'System Scale',
    'Agent Registry',
    'Safety Boundaries',
    'Review',
    'Full Audit Dashboard',
    'Live Dashboard',
]

FORBIDDEN_HTML_STRINGS = [
    'Home → Demo Hub → Demo Hub',
    'href="#"',
    'href=""',
    'nav-links',
]

REQUIRED_CSS_STRINGS = [
    '.menu-panel[hidden]',
    'display: none !important',
    '.menu-panel.is-open',
    '.collapsible-topbar',
    'position: sticky',
    '.topbar-main',
    'justify-content: space-between',
]

REQUIRED_JS_STRINGS = [
    'initCollapsibleMenu',
    'data-collapsible-menu',
    "data-action='toggle-menu'",
    'data-menu-panel',
    'aria-expanded',
    'panel.hidden',
    'is-open',
    'Escape',
    'addEventListener',
]


def read(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"MISSING_FILE {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    html = read(FILES["html"])
    css = read(FILES["css"])
    js = read(FILES["js"])

    for needle in REQUIRED_HTML_STRINGS:
        ensure(needle in html, f"HTML_MISSING {needle}")
    for needle in REQUIRED_CSS_STRINGS:
        ensure(needle in css, f"CSS_MISSING {needle}")
    for needle in REQUIRED_JS_STRINGS:
        ensure(needle in js, f"JS_MISSING {needle}")

    for needle in FORBIDDEN_HTML_STRINGS:
        ensure(needle not in html, f"HTML_FORBIDDEN {needle}")

    panel_match = re.search(
        r'<nav\b[^>]*id="presentation-menu-panel"[^>]*>(.*?)</nav>',
        html,
        re.IGNORECASE | re.DOTALL,
    )
    ensure(panel_match is not None, "MENU_PANEL_MISSING")
    panel_html = panel_match.group(1)
    ensure('hidden' in panel_match.group(0), "MENU_PANEL_NOT_HIDDEN_BY_DEFAULT")

    required_panel_labels = [
        'Home',
        'Demo Hub',
        'Simulator',
        'System Story',
        'System Scale',
        'Agent Registry',
        'Safety Boundaries',
        'Review',
        'Full Audit Dashboard',
        'Live Dashboard',
    ]
    for label in required_panel_labels:
        ensure(label in panel_html, f"PANEL_MISSING_LABEL {label}")

    required_panel_hrefs = [
        '../index.html',
        './index.html',
        './simulator.html',
        './system-story.html',
        './system-scale.html',
        './agent-registry.html',
        './safety-boundaries.html',
        './review.html',
        '../full-audit-dashboard.html',
    ]
    for href in required_panel_hrefs:
        ensure(href in panel_html, f"PANEL_MISSING_HREF {href}")

    nav_blocks = list(re.finditer(r'<nav\b[^>]*>(.*?)</nav>', html, re.IGNORECASE | re.DOTALL))
    ensure(nav_blocks, "NO_NAV_BLOCKS_FOUND")
    for match in nav_blocks:
        block = match.group(1)
        if block == panel_html:
            continue
        if all(label in block for label in required_panel_labels):
            raise SystemExit("ALWAYS_VISIBLE_NAV_STILL_PRESENT")

    if html.count('Home → Demo Hub → Demo Hub') > 0:
        raise SystemExit("DUPLICATE_BREADCRUMB_PRESENT")

    print("PRESENTATION_COLLAPSE_MENU_ACTUAL_AFTER_MVP50_VALIDATION_PASS")


if __name__ == "__main__":
    main()
