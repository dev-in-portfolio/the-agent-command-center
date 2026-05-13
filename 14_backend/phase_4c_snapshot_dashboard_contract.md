# Phase 4C: Snapshot Dashboard Contract

## Integration Rules
1. **Same-Origin Only**: Fetch requests are restricted to `./status_snapshot.json`.
2. **Explicit Trigger**: Data must only be loaded upon user interaction (click-to-load).
3. **No Storage**: Data must be stored in memory only. No `localStorage` or `cookies`.
4. **Safety Check**: The dashboard must verify all danger flags in the JSON are `false` before displaying status data.

## Fallback
If the JSON file is missing or malformed, the UI must display a clear "Snapshot not available" message.

---
*Note: This is a planning contract only. The prototype implementation follows these rules strictly.*
