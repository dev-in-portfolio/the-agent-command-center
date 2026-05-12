# Interface Phase 1 → Phase 2 Handoff Contract

## 1. Source of Truth Rules

1. **`11_interface/` is the single source of truth** for all interface code. No interface logic lives outside this directory.
2. **`scripts/validate_interface_phase_1_*.py` are the single source of truth** for validation. No validation logic lives in the interface modules themselves.
3. **`09_exports/interface_phase_1/` is the single source of truth** for exported reports, command packets, branch reviews, and approval ledger.
4. **Policy definitions live in `interface_policy.py`** — both the `POLICY` dict and the `SAFE_ACTIONS`/`CONTROLLED_ACTIONS`/`LOCKED_ACTIONS` lists. Action registry in `interface_action_registry.py` is derived from these.
5. **No secrets, credentials, tokens, or deploy keys** are stored in this repo. The `gho_` push token exists only in shell env and `.git/config`, never in source.

## 2. Reuse Boundaries

### May Be Reused in Phase 2
- `interface_policy.py` — Policy definitions remain valid
- `interface_actions.py` — Action implementations (TUI can call same functions)
- `interface_session_log.py` — Session model unchanged
- `interface_action_registry.py` — Registry structure reusable
- `interface_policy_enforcer.py` — Enforcement logic reusable
- `interface_artifact_inspector.py` — Inspection engine reusable
- `interface_branch_review.py` — Branch review logic reusable
- `interface_approval_ledger.py` — Ledger logic reusable
- `interface_config.json` — Config schema reusable
- `interface/README.md` — Documentation foundation

### Must Be Replaced or Wrapped in Phase 2
- `station_chief_cli.py` — The CLI entrypoint must be wrapped or replaced by a TUI entrypoint. The non-interactive CLI flags should remain accessible.

### Must Remain Separate in Phase 2
- Validator scripts (`scripts/validate_interface_phase_1_*.py`) — Must not be merged with interface source
- Exports (`09_exports/interface_phase_1/`) — Must remain a separate output directory
- Runtime (`10_runtime/`) — Interface is a consumer of runtime validators but must never modify them

## 3. Architectural Invariants

1. Interface never mutates official repos, never deploys, never accesses secrets.
2. Interface never executes command packets — all records have `execution_performed: false`.
3. Interface never uses `shell=True`, `os.environ`, or network imports (`requests`, `urllib`, `http.client`, `socket`).
4. Interface never reads environment variables, credential stores, or configuration outside `interface_config.json`.
5. All `subprocess` calls use explicit command arrays with `shell=False`.
6. All file writes are restricted to `09_exports/interface_phase_1/` and its subdirectories.
7. Branch review never merges, pushes, or deletes branches.
8. Test ledger is always separate from production ledger.

## 4. Phase 2 Contract

Phase 2 (TUI) agrees to:
1. Preserve all Phase 1 CLI flags for non-interactive use.
2. Keep the approval ledger at `09_exports/interface_phase_1/approval_ledger/approval_ledger.jsonl`.
3. Keep the test ledger at `09_exports/interface_phase_1/test_runs/e2e_ledger_test.jsonl`.
4. Add new validator checks in `scripts/validate_interface_phase_2_*.py` — never modify Phase 1 validators.
5. Document all changes in a new upgrade report.
6. Maintain the empty-ledger-is-allowed contract.
7. Never change the `execution_performed: false` invariant.

## 5. Handoff Verdict

**READY_FOR_PHASE_2**

Phase 1 delivers a complete, validated, documented CLI operator console with operational hardening. All architectural invariants are enforced by validators. Phase 2 can build on this foundation without breaking existing contracts.
