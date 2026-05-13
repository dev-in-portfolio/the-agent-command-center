# Phase 4C: External API Safety Rules

## Core Rules
Every external API interaction in The Agent Command Center must adhere to these safety invariants.

### 1. Server-Side Execution
No browser-side `fetch()` or `XMLHttpRequest` calls to any domain other than the dashboard's same origin are permitted.

### 2. Allowlisted Domains
All external API calls must be restricted to a hardcoded allowlist (e.g., `api.github.com`, `api.netlify.com`).

### 3. No Raw Upstream Payloads
Backend functions must shape and sanitize external responses before returning them to the dashboard. Never dump an upstream JSON payload directly to the client.

### 4. Minimum Scoped Tokens
API tokens used by Netlify Functions must have the absolute minimum permissions required (Read-Only).

### 5. Mandatory Rate Limiting
External calls must be throttled to prevent accidental abuse of upstream services or DoS attacks.

### 6. Audit Requirement
Every external request must generate a corresponding audit event in the immutable ledger.

### 7. Failure Fallbacks
The system must gracefully handle upstream outages without breaking the dashboard UI.

---
*Note: This is a planning document only. No functional implementation is included in this build.*
