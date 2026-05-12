# Interface Phase 2 Screen Map

## Screens (9 total after Phase 2.1–2.11 upgrade)

| Key | Screen Name | Handler | Renderer | Description |
|-----|-------------|---------|----------|-------------|
| 1 | dashboard | `handle_dashboard_input` | `render_dashboard` | Main status dashboard with safety status, action counts, validator results, session info, repo info |
| 2 | action_registry | `handle_action_registry_input` | `render_action_registry` | All registered actions grouped by category (safe/controlled/locked) |
| 3 | artifact_inspector | `handle_artifact_inspector_input` | `render_artifact_inspector` | Read-only artifact package inspection with detail view, expected files checklist, verdict |
| 4 | validator_wall | `handle_validator_wall_input` | `render_validator_wall` | Run Phase 1 validators with RUN_VALIDATOR_WALL confirmation, per-validator progress, stdout capture |
| 5 | command_packet_prep | `handle_command_packet_prep_input` | `render_command_packet_prep` | Select and prepare command packets (no execution) |
| 6 | branch_review_prep | `handle_branch_review_prep_input` | `render_branch_review_prep` | Branch review cockpit: input validation, risk preview, safety status, prepared_not_merged |
| 7 | approval_ledger | `handle_approval_ledger_input` | `render_approval_ledger` | Approval ledger viewer: state filters, execution_performed invariant, record table |
| 8 | help | `handle_help_input` | `render_help` | Safety rules, capabilities, limitations, snapshot flags |
| 9 | safety_monitor | `handle_safety_monitor_input` | `render_safety_monitor` | Safety boundary status, self-checks (keymap scan, source scan, ledger scan) |

## Special Keys

| Key | Action |
|-----|--------|
| q | Quit (writes session report, exits cleanly) |
| r | Refresh (re-renders current screen, updates timestamp) |
| h | Navigate to help screen |
| b | Back (navigate to previous screen) |
| d | Dashboard / Home (navigate to dashboard) |
| ? | Screen-specific help |

## Module Architecture

```
station_chief_tui.py  (entrypoint: --snapshot, --no-curses, --help, --format, --save)
  +-- tui_app.py       (controller: curses wrapper, plain-text loop, snapshot mode)
       +-- tui_state.py       (state management, navigation, breadcrumbs, session logging)
       +-- tui_screens.py     (input handlers per screen)
       |    +-- tui_renderer.py   (screen rendering, snapshot formats, status badges)
       |    +-- tui_safe_actions.py (safe wrappers around Phase 1 modules)
       |    +-- tui_keymap.py     (key bindings, forbidden names, navigation)
       +-- (Phase 1 backend modules via importlib)
```

## Upgraded in Phase 2.1–2.11

- Screen 9 (safety_monitor) added
- Navigation keys b, d, ? added
- All screens: status badges, action banners, breadcrumbs, consistent borders, keymap display
- Snapshot formats: text, markdown, json, compact, full
