# Safety Boundary Brief

## Goal: Zero-Leak, Mutation-Gated Testing

### Token Posture
- **Memory-Only:** Tokens are never stored in `local-Storage`, `session-Storage`, cookies, or `indexed-DB`.
- **No URLs:** Tokens are never placed in query parameters or URL paths.
- **No Printing:** The system never logs or prints full bearer tokens.

### Mutation Gates
- **Blocked Actions:** Update, Delete, Approve, and Execute are intentionally not implemented in this phase.
- **Append-Only History:** Lifecycle events can be added, but existing event notes cannot be edited or deleted.
- **No Forced Writes:** Write flags (e.g., `MVP_ENABLE_REQUEST_API_WRITES`) are respected and cannot be overridden by the client.

### Environment Safety
- **No Client Migrations:** Database schema changes and migrations are never triggered from the app runtime.
- **No Client Env Changes:** Netlify environment variables cannot be modified via the dashboard.
- **Service Role:** The Supabase Service Role key is never exposed to or used by the browser.
