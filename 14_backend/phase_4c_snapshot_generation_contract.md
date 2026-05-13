# Phase 4C: Snapshot Generation Contract

## Constraints
1. **Local Only**: The generator must only read files from the local repository.
2. **Standard Library Only**: Only Python standard library modules are allowed.
3. **No Side Effects**: The script must not modify any files outside the `13_web_dashboard/dist/` directory.
4. **No Network**: Network access (HTTP, socket, etc.) is strictly forbidden.
5. **No Mutation**: No commands that alter the repository state (Git, etc.) are permitted.

## Generation Lifecycle
1. Scan `09_exports/backend_phase_4/` for verification and acceptance reports.
2. Extract status and verdict metadata.
3. Construct a JSON payload matching the `phase_4c_snapshot_v1` schema.
4. Output to `13_web_dashboard/dist/status_snapshot.json`.

---
*Note: This is a planning contract only. The prototype implementation follows these rules strictly.*
