# Interface Phase 2 Clean Checkout Checklist

This document describes how a reviewer can perform an independent green-field validation of the `interface/phase-2-tui-operator-dashboard` branch.

## Prerequisites

- Git
- Python 3.8+
- No external dependencies beyond Python standard library
- Terminal with at least 80x24 characters for curses mode (optional — plain-text fallback works without curses)

## Step 1: Clone and Checkout

```bash
git clone https://github.com/dev-in-portfolio/the-agent-command-center.git
cd the-agent-command-center
git checkout interface/phase-2-tui-operator-dashboard
```

Expected result: clean checkout on branch `interface/phase-2-tui-operator-dashboard`.

## Step 2: Verify Minimal Dirty Working Tree

```bash
git status --short
```

Expected: only `.gitignore` as untracked (or nothing if `.gitignore` was committed). No modified tracked files.

```bash
git status --short | grep -v '^\?\?' | grep -v '\.gitignore'
```

Expected: empty output — zero dirty tracked files.

## Step 3: Verify Generated Paths Are Ignored

```bash
git status --short | grep -E 'sessions/|snapshots/|test_runs/|__pycache__|\.pyc$'
```

Expected: empty output — all generated paths are excluded by `.gitignore`.

## Step 4: Verify Scope — Only Phase 2 Files Changed

```bash
git diff master...HEAD --name-only
```

Expected output should only contain paths under:
- `12_tui/`
- `scripts/validate_interface_phase_2_*`
- `scripts/demo_interface_phase_2_tui.sh`
- `09_exports/interface_phase_2/`
- `.gitignore`

Verify no Phase 1, runtime, or cross-repo changes:

```bash
git diff master...HEAD --name-only | grep -E '^(11_interface/|10_runtime/|station_chief\.py$)'
```

Expected: empty output.

## Step 5: Run TUI Validator

```bash
python3 scripts/validate_interface_phase_2_tui.py 2>&1 | tail -5
```

Expected output ends with:
```
Results: 32 passed, 0 failed, 32 total
INTERFACE_PHASE_2_TUI_VALIDATION_PASS
```

## Step 6: Run E2E Validator

```bash
python3 scripts/validate_interface_phase_2_e2e.py 2>&1 | tail -5
```

Expected output ends with:
```
Results: 32 passed, 0 failed, 32 total
INTERFACE_PHASE_2_E2E_VALIDATION_PASS
```

## Step 7: Verify Validator Test Artifact Isolation

Check that validators wrote to `test_runs/`, not production paths:

```bash
ls 09_exports/interface_phase_2/test_runs/sessions/ | head -3
ls 09_exports/interface_phase_2/test_runs/reports/ | head -3
```

Expected: timestamped session files exist under `test_runs/`.

Verify production paths are operator-only (not created by validators):

```bash
ls 09_exports/interface_phase_2/sessions/ 2>&1 | head -1
ls 09_exports/interface_phase_2/snapshots/ 2>&1 | head -1
```

Expected: these directories may be empty or contain operator-generated files — but validators must NOT have written to them.

## Step 8: Verify Snapshot Schema

```bash
python3 -c "
import json, glob
snaps = glob.glob('09_exports/interface_phase_2/snapshots/snapshot_*.json')
if not snaps:
    print('No production snapshots — run --snapshot --format json --save first')
else:
    with open(snaps[-1]) as f:
        d = json.load(f)
    required = ['snapshot_id','created_at_utc','phase','repo','source_lineage','format','safety_status','artifact_summary','approval_ledger_summary','validator_status','boundary_status','recommended_next_action']
    missing = [k for k in required if k not in d]
    print('Schema OK' if not missing else f'Missing: {missing}')
"
```

Expected: `Schema OK` — all 11 required fields present.

## Step 9: Test Snapshot With --save

```bash
python3 12_tui/station_chief_tui.py --no-curses --snapshot --format json --save 2>&1 | tail -3
```

Expected: snapshot saved to `09_exports/interface_phase_2/snapshots/snapshot_<timestamp>.json`.

## Step 10: Verify Safety Scanner

```bash
python3 -c "
from 12_tui.tui_safety_scanner import scan_source_safety
result = scan_source_safety()
print(f'Active forbidden: {result[\"active_forbidden_findings\"]}')
print(f'Allowed label findings: {result[\"allowed_label_findings\"]}')
"
```

Expected: `Active forbidden: 0`

## Step 11: Test Error Handling

```bash
python3 12_tui/station_chief_tui.py --snapshot --format invalid 2>&1; echo "Exit: $?"
python3 12_tui/station_chief_tui.py --format json 2>&1; echo "Exit: $?"
python3 12_tui/station_chief_tui.py --save 2>&1; echo "Exit: $?"
python3 12_tui/station_chief_tui.py positional_arg 2>&1; echo "Exit: $?"
```

Expected: all exit with code 2.

## Step 12: Verify Demo Script Supports Listed Operations

```bash
bash scripts/demo_interface_phase_2_tui.sh --help 2>&1 | head -5
```

Expected: help output, not an error.

## Summary Checklist

- [ ] Step 1: Clean clone and checkout
- [ ] Step 2: Minimal dirty working tree
- [ ] Step 3: Generated paths ignored
- [ ] Step 4: Only Phase 2 files changed
- [ ] Step 5: TUI validator 32/32 PASS
- [ ] Step 6: E2E validator 32/32 PASS
- [ ] Step 7: Test artifact isolation confirmed
- [ ] Step 8: Snapshot schema contract satisfied
- [ ] Step 9: --snapshot --save works
- [ ] Step 10: Safety scanner — zero active forbidden
- [ ] Step 11: Error handling — exit 2 for bad input
- [ ] Step 12: Demo script operational

## Next Steps After Clean Checkout

1. Review the diff: `git diff master...HEAD`
2. Review the merge-readiness packet: `09_exports/interface_phase_2/merge_readiness/interface_phase_2_merge_readiness_packet.md`
3. Merge to `master` via approved PR/review process
4. Re-run all validators post-merge to confirm base branch compatibility
