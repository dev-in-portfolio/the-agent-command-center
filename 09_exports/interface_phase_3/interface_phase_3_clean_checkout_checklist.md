# Read-Only Operations Dashboard Clean Checkout Checklist

## Goal

Confirm the working tree is clean outside the authorized Phase 3 paths.

## Verify

```bash
git status --short
git diff --name-only
```

## Allowed Changed Paths

- `13_web_dashboard/**`
- `scripts/validate_interface_phase_3_dashboard.py`
- `scripts/validate_interface_phase_3_e2e.py`
- `scripts/demo_interface_phase_3_dashboard.sh`
- `09_exports/interface_phase_3/**`

## Must Remain Unchanged

- `11_interface/**`
- `12_tui/**`
- `10_runtime/**`
- `09_exports/interface_phase_1/**`
- `09_exports/interface_phase_2/**`
- `dev-in-portfolio/agent-command-center`
- `dev-in-portfolio/agent-command-center-2`
- `dev-in-portfolio/agent-command-center-3`

## Clean Checkout Decision Rule

If anything outside the allowed Phase 3 scope is modified, stop and reconcile before commit or push.
