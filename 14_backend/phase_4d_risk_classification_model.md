# Phase 4D Risk Classification Model

## Goal
Classify future request-only actions by review strictness before any execution system exists.

## Risk Classes
- `low`: read-only inspection, export generation, or harmless metadata refresh.
- `moderate`: state proposal, queue movement, or policy edits that remain non-executing.
- `high`: actions that could affect deploy, merge, push, secrets, credentials, or external systems if later implemented incorrectly.
- `critical`: actions that would alter production state, credentials, or repository history.

## Required Future Controls
- `low`: single requester plus audit event.
- `moderate`: requester plus approver.
- `high`: dual control plus explicit confirmation phrase.
- `critical`: blocked until a later execution phase with hardened storage, auth, and audit acceptance.

## Hard Boundaries In This Build
- Command execution added: false
- GitHub API calls added: false
- Netlify API calls added: false
- External API calls added: false
- Deploy controls added: false
- Merge controls added: false
- Push controls added: false
- PR controls added: false

---
*Planning only. This risk model is a static contract with no live classification engine.*
