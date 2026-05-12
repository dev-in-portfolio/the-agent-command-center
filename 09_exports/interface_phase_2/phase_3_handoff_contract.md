# Phase 3 Handoff Contract

## Source of Truth Rules

1. Phase 1 action registry remains source of truth for actions.
2. Phase 1 policy enforcer remains permission boundary.
3. Phase 1 artifact inspector remains artifact/report backend.
4. Phase 1 branch review builder remains merge-review backend.
5. Phase 1 approval ledger remains approval receipt backend.
6. Phase 1/2 session logs remain audit backend.
7. Phase 2 screen architecture is visual/reference layer.
8. Future web dashboard must call backend modules, not duplicate rules.
9. Future web dashboard must not add deploy/promotion/secret behavior.
10. Future web dashboard must not execute command packets.

## Reusable Phase 2 Components

- `12_tui/tui_state.py` — Session state management, module loading, session logging
- `12_tui/tui_renderer.py` — Screen rendering, snapshot formats, status badges
- `12_tui/tui_screens.py` — Input handlers per screen, interactive UX patterns
- `12_tui/tui_keymap.py` — Key bindings, forbidden screen names, navigation state
- `12_tui/tui_safe_actions.py` — Safe wrappers around Phase 1 backend modules

## Phase 3 Allowed Scope

**Allowed:**
- local web dashboard
- render status
- render action registry
- render artifacts
- render branch review packets
- render approval ledger
- render session timeline
- show safety monitor
- prepare command packets
- prepare branch review packets
- run validator wall only with explicit operator confirmation

**Forbidden:**
- deploy
- promote to official
- mutate official repo
- mutate repo 2
- mutate repo 3
- execute command packets
- merge branches
- push master
- open PRs unless explicitly approved in a later separate phase
- use secrets
- use credentials
- free-form shell

## Phase 3 Acceptance Criteria

- uses Phase 1 backend modules
- uses Phase 2 screen concepts
- cannot call locked actions
- has no deploy button
- has no secret access
- has no free-form shell
- has tests
- CLI remains functional
- TUI remains functional
