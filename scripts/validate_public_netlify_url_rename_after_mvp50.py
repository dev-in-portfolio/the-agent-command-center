#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


OLD_HOST = "the-agent-command-center-" + "dashboard.netlify.app"
OLD_URL = "https://" + OLD_HOST
NEW_URL = "https://the-agent-command-center.netlify.app"
NEW_HOST = "the-agent-command-center.netlify.app"

TEXT_SUFFIXES = {
    ".html",
    ".css",
    ".js",
    ".json",
    ".md",
    ".txt",
    ".toml",
    ".py",
    ".yml",
    ".yaml",
    ".csv",
    ".tsv",
}

SCAN_ROOTS = [
    Path("13_web_dashboard/dist"),
    Path("13_web_dashboard/build_phase4c_status_snapshot.py"),
    Path("scripts"),
    Path("09_exports"),
]

ROOT_PAGE_FILES = [
    Path("13_web_dashboard/dist/index.html"),
    Path("13_web_dashboard/dist/dashboard.html"),
    Path("13_web_dashboard/dist/legal.html"),
    Path("13_web_dashboard/dist/copyright.html"),
]

DEMO_PAGE_FILES = sorted(Path("13_web_dashboard/dist/demo").glob("*.html"))

CURRENT_LIVE_VALIDATORS = [
    Path("scripts/validate_original_phase_4_hosted_dashboard_e2e.py"),
    Path("scripts/validate_phase5_plus1_master_validator_wall.py"),
    Path("scripts/validate_live_dashboard_dynamic_latest_status.py"),
    Path("scripts/validate_mvp50_monitoring_rollback_incident_console.py"),
    Path("scripts/validate_public_netlify_url_rename_after_mvp50.py"),
]

NEW_URL_REQUIRED_FILES = [
    Path("13_web_dashboard/dist/demo/demo-package.json"),
    Path("13_web_dashboard/dist/status_snapshot.json"),
    Path("09_exports/mvp_product_track/live_site_current_mvp50_dashboard_fix_report.md"),
    Path("09_exports/mvp_product_track/public_netlify_url_rename_after_mvp50_report.md"),
    Path("09_exports/external_demo_package_after_mvp50/demo_package_manifest.json"),
    Path("09_exports/stakeholder_presentation_after_mvp50/presentation_manifest.json"),
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def iter_text_files(root: Path):
    if root.is_file():
        if root.suffix.lower() in TEXT_SUFFIXES or root.name in {"README", "LICENSE"}:
            yield root
        return

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {"README", "LICENSE"}:
            yield path


def is_allowed_old_url_file(path: Path) -> bool:
    return path == Path("09_exports/mvp_product_track/public_netlify_url_rename_after_mvp50_report.md")


def fail(messages: list[str]) -> None:
    for message in messages:
        print(message, file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    errors: list[str] = []

    missing = [str(path) for path in ROOT_PAGE_FILES + DEMO_PAGE_FILES + CURRENT_LIVE_VALIDATORS + NEW_URL_REQUIRED_FILES if not path.exists()]
    if missing:
        errors.append("Missing required files:")
        errors.extend(f"  - {item}" for item in missing)

    scanned_files = []
    for root in SCAN_ROOTS:
        if root.exists():
            scanned_files.extend(iter_text_files(root))

    saw_new_url = False

    for path in sorted(set(scanned_files + ROOT_PAGE_FILES + DEMO_PAGE_FILES + CURRENT_LIVE_VALIDATORS + NEW_URL_REQUIRED_FILES)):
        if not path.exists():
            continue

        try:
            text = read_text(path)
        except UnicodeDecodeError:
            continue

        if NEW_URL in text or NEW_HOST in text:
            saw_new_url = True

        page_like = path in ROOT_PAGE_FILES or path in DEMO_PAGE_FILES or path.name in {"legal.html", "copyright.html"}
        if page_like and ".netlify.app" in text:
            if OLD_URL in text or OLD_HOST in text:
                errors.append(f"Old URL still present in public page: {path}")
            if NEW_URL not in text and NEW_HOST not in text:
                errors.append(f"Public page with netlify URL must use the new host: {path}")

        if path in CURRENT_LIVE_VALIDATORS or (path.parent.name == "scripts" and path.name.startswith("validate_")):
            if OLD_URL in text or OLD_HOST in text:
                errors.append(f"Old URL still present in current validator: {path}")

        if path in NEW_URL_REQUIRED_FILES and NEW_URL not in text and NEW_HOST not in text:
            errors.append(f"New URL missing from required current material: {path}")

        if (OLD_URL in text or OLD_HOST in text) and not is_allowed_old_url_file(path):
            if "OLD URL" not in text and "previous URL" not in text:
                errors.append(f"Unlabeled old URL reference remains in current public material: {path}")

    if not saw_new_url:
        errors.append("New public URL was not found in any scanned current material.")

    if errors:
        fail(errors)

    print("PUBLIC_NETLIFY_URL_RENAME_AFTER_MVP50_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
