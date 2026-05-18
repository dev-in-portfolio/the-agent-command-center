#!/usr/bin/env python3
"""Context-aware control scan helpers for validation scripts.

These helpers distinguish between dangerous enabled controls/actions and
explicit safety-denial language so validators do not fail on report text,
disabled controls, or read-only copy.
"""

from __future__ import annotations

import re
from pathlib import Path


_SAFE_PHRASES = (
    "no deploy controls added",
    "no deploy controls",
    "deployment is not enabled",
    "deploy controls are not exposed",
    "deploy controls are blocked",
    "deploy controls are disabled",
    "deploy is blocked",
    "deploy is disabled",
    "send is blocked",
    "send is disabled",
    "import is blocked",
    "import is disabled",
    "capture is blocked",
    "capture is disabled",
    "submit is blocked",
    "submit is disabled",
    "approve is blocked",
    "approve is disabled",
    "execute is blocked",
    "execute is disabled",
    "no public writes",
    "no token input",
    "no email sending",
    "no reviewer contact",
    "no automation",
    "not ready for real automation",
    "operator review only",
    "readiness only",
    "blueprint only",
    "dry run only",
    "preview only",
    "copy only",
    "package not sent",
    "service role not used",
    "not required",
    "automation still disabled",
    "remains blocked",
    "remains disabled",
    "not ready",
    "not enabled",
    "not exposed",
    "is not enabled",
    "are not enabled",
    "is not exposed",
    "are not exposed",
    "read only",
    "read-only",
    "blocked",
    "disabled",
)

_DANGEROUS_CONTROL_WORDS = (
    "deploy",
    "merge",
    "push",
    "create pr",
    "pr controls",
    "release",
    "launch",
    "submit",
    "save",
    "queue",
    "execute",
    "approve",
    "send email",
    "email reviewer",
    "contact reviewer",
    "automated outreach",
    "public write",
    "response persistence",
    "browser persistence",
    "token input",
    "service role",
    "reviewer response",
)

_DANGEROUS_RUNTIME_PATTERNS = (
    (re.compile(r"fetch\(['\"]/api/(?:deploy|reviewer-response|review-response|response-import)", re.IGNORECASE), "dangerous endpoint fetch"),
    (re.compile(r"\bdeployToNetlify\b", re.IGNORECASE), "dangerous deploy runtime function"),
    (re.compile(r"\bmergePullRequest\b", re.IGNORECASE), "dangerous merge runtime function"),
    (re.compile(r"\bpushToGithub\b", re.IGNORECASE), "dangerous push runtime function"),
    (re.compile(r"\bcreatePullRequest\b", re.IGNORECASE), "dangerous PR runtime function"),
    (re.compile(r"\bsendEmail\b", re.IGNORECASE), "dangerous email runtime function"),
    (re.compile(r"\bemailReviewer\b", re.IGNORECASE), "dangerous reviewer email runtime function"),
    (re.compile(r"\bcontactReviewer\b", re.IGNORECASE), "dangerous reviewer contact runtime function"),
    (re.compile(r"\bautomateOutreach\b", re.IGNORECASE), "dangerous outreach runtime function"),
    (re.compile(r"\blocalStorage\.setItem\b", re.IGNORECASE), "browser persistence path"),
    (re.compile(r"\bsessionStorage\.setItem\b", re.IGNORECASE), "browser persistence path"),
    (re.compile(r"\bindexedDB\b", re.IGNORECASE), "browser persistence path"),
    (re.compile(r"\bdocument\.cookie\b", re.IGNORECASE), "browser persistence path"),
    (re.compile(r"\bcreateClient\(", re.IGNORECASE), "direct browser Supabase client path"),
    (re.compile(r"\bSUPABASE_SERVICE_ROLE\b", re.IGNORECASE), "service role exposure"),
    (re.compile(r"\bservice_role\b", re.IGNORECASE), "service role exposure"),
    (re.compile(r"\benableWrites\b", re.IGNORECASE), "enabled write path"),
    (re.compile(r"\bapproveRelease\b", re.IGNORECASE), "release approval runtime path"),
    (re.compile(r"\bexecuteRelease\b", re.IGNORECASE), "release execution runtime path"),
    (re.compile(r"\brunImport\b", re.IGNORECASE), "import runtime path"),
    (re.compile(r"\bcommitImport\b", re.IGNORECASE), "import commit runtime path"),
    (re.compile(r"\bpersistResponse\b", re.IGNORECASE), "response persistence runtime path"),
    (re.compile(r"\bsubmitResponse\b", re.IGNORECASE), "response submission runtime path"),
    (re.compile(r"\bsaveResponse\b", re.IGNORECASE), "response persistence runtime path"),
    (re.compile(r"\bcaptureResponse\b", re.IGNORECASE), "response capture runtime path"),
)

_DANGEROUS_JSON_FLAGS = (
    "public_write_enabled",
    "live_write_enabled",
    "token_input_enabled",
    "service_role_used",
    "browser_persistence_enabled",
    "browser_direct_supabase_calls",
    "automation_enabled",
)

_SAFE_BUTTON_PREFIXES = ("copy ", "load ", "phase ", "original +")
_SAFE_BUTTON_EXACT = {"submit feedback packet manually"}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def is_safety_denial_line(line: str) -> bool:
    """Return True when the text is explicitly denying live controls."""

    text = _normalize(line)
    if not text:
        return False
    if text.startswith("no_"):
        return True
    if text.startswith("no ") or text.startswith("not "):
        if any(
            hint in text
            for hint in (
                "enabled",
                "exposed",
                "added",
                "used",
                "allowed",
                "permitted",
                "ready",
                "blocked",
                "disabled",
                "sent",
                "submitted",
                "captured",
                "approved",
                "executed",
                "written",
                "persisted",
                "review only",
                "operator review only",
            )
        ):
            return True
    if any(phrase in text for phrase in _SAFE_PHRASES):
        return True
    return False


def contains_dangerous_runtime_pattern(text: str) -> bool:
    """Return True when the text contains an enabled dangerous runtime path."""

    if is_safety_denial_line(text):
        return False
    for pattern, _reason in _DANGEROUS_RUNTIME_PATTERNS:
        if pattern.search(text):
            return True
    return False


def contains_dangerous_enabled_control(text: str) -> bool:
    """Return True when text names an enabled dangerous UI/control action."""

    normalized = _normalize(text)
    if is_safety_denial_line(normalized):
        return False
    return any(word in normalized for word in _DANGEROUS_CONTROL_WORDS)


def scan_text_for_dangerous_controls(path: str, text: str) -> list[str]:
    """Return control-scan findings for the given file text."""

    findings: list[str] = []
    suffix = Path(path).suffix.lower() if path else ""
    lines = text.splitlines()

    for index, line in enumerate(lines, start=1):
        if is_safety_denial_line(line):
            continue

        lower = line.lower()

        for pattern, reason in _DANGEROUS_RUNTIME_PATTERNS:
            if pattern.search(line):
                findings.append(f"{path}:{index}: dangerous runtime pattern: {reason}")
                break

        for flag in _DANGEROUS_JSON_FLAGS:
            if flag in lower and ": true" in lower:
                findings.append(f"{path}:{index}: dangerous semantic JSON flag set true: {flag}")
                break

        if re.search(r"\bon(?:click|submit|change|input)\s*=", lower) and any(
            word in lower for word in _DANGEROUS_CONTROL_WORDS
        ):
            findings.append(f"{path}:{index}: dangerous handler binding: {line.strip()}")

    if suffix in {".html", ".htm"}:
        for match in re.finditer(r"(<button[^>]*>)([^<]+)(</button>)", text, re.IGNORECASE | re.DOTALL):
            tag, label, _closing = match.groups()
            if "disabled" in tag.lower() or 'aria-disabled="true"' in tag.lower():
                continue
            normalized_label = _normalize(label)
            if normalized_label in _SAFE_BUTTON_EXACT:
                continue
            if normalized_label.startswith(_SAFE_BUTTON_PREFIXES):
                continue
            if is_safety_denial_line(label):
                continue
            if contains_dangerous_enabled_control(label):
                findings.append(f"{path}: enabled dangerous button label: {label.strip()}")

    return findings


# Backward-compatible alias for older callers.
def scan_for_forbidden_runtime_controls(path, text: str) -> list[str]:
    return scan_text_for_dangerous_controls(path, text)
