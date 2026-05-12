# Interface Phase 2 Screen Map

## Screens

| Key | Screen Name | Handler | Renderer | Description |
|-----|-------------|---------|----------|-------------|
| 1 | dashboard | `handle_dashboard_input` | `render_dashboard` | Main status dashboard with safety status, action counts, validator results |
| 2 | action_registry | `handle_action_registry_input` | `render_action_registry` | All registered actions grouped by category (safe/controlled/locked) |
| 3 | artifact_inspector | `handle_artifact_inspector_input` | `render_artifact_inspector` | Read-only artifact package inspection |
| 4 | validator_wall | `handle_validator_wall_input` | `render_validator_wall` | Run Phase 1 validators with RUN_VALIDATOR_WALL confirmation |
| 5 | command_packet_prep | `handle_command_packet_prep_input` | `render_command_packet_prep` | Select and prepare command packets (no execution) |
| 6 | branch_review_prep | `handle_branch_review_prep_input` | `render_branch_review_prep` | Enter branch name to prepare review packet (no merge) |
| 7 | approval_ledger | `handle_approval_ledger_input` | `render_approval_ledger` | Review/approve/reject packets (exec=false invariant) |
| 8 | help | `handle_help_input` | `render_help` | Safety rules, capabilities, limitations |

## Special Keys

| Key | Action |
|-----|--------|
| q | Quit (writes session report, exits cleanly) |
| r | Refresh (re-renders current screen) |
| h | Navigate to help screen |

## Module Architecture

```
station_chief_tui.py  (entrypoint: --snapshot, --no-curses, --help)
  └─ tui_app.py       (controller: curses wrapper, plain-text loop)
       ├─ tui_state.py       (state management, session logging)
       ├─ tui_screens.py     (input handlers per screen)
       │    ├─ tui_renderer.py   (screen rendering functions)
       │    ├─ tui_safe_actions.py (safe wrappers around Phase 1 modules)
       │    └─ tui_keymap.py     (key bindings, forbidden names)
       └─ (Phase 1 backend modules via importlib)
```
