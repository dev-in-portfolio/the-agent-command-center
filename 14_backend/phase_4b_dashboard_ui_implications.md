# Phase 4B: Dashboard UI Implications

## Future UI States

### 1. Public Read-Only Mode
- Default state for unauthenticated viewers.
- "Backend Status" panel shows read-only health.
- All action request buttons are hidden or disabled with a "Login required" tooltip.

### 2. Authenticated Operator Mode
- Operator name and role visible in header.
- Action request forms enabled.
- Audit panel visible (recent events).

### 3. Admin Mode
- Approval Queue panel enabled.
- Role management (future) enabled.
- Detailed audit logs accessible.

## UI Components
- **Auth Banner**: Prominent login/logout controls.
- **Status Labels**: Dynamic labels indicating the current backend session state.
- **Audit Panel**: A streaming view of non-sensitive audit events.
- **Action Dashboard**: A tailored view of the Action Registry with "Request" buttons for allowed actions.

---
*Note: This is a planning document only. No functional implementation is included in this build.*
