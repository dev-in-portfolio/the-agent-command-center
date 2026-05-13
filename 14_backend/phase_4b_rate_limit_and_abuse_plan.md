# Phase 4B: Rate Limit & Abuse Plan

## Strategy
Protect the backend foundation from spam, brute-force attacks, and accidental recursive loops.

## Recommendations

### 1. Public Endpoint Limits
- Strict rate limiting for `/api/health`, `/api/status`, and `/api/backend-manifest`.
- Default: 10 requests per minute per IP.

### 2. Authenticated Endpoint Limits
- Higher limits for verified operators.
- Default: 60 requests per minute per user.

### 3. Action Request Throttling
- Specific limits on non-idempotent actions (e.g., requesting an action).
- Default: 5 requests per minute per user.

### 4. Failed Auth Handling
- Progressive backoff for repeated failed login attempts.
- Temporary IP blocking for detected brute-force patterns.

### 5. Abuse Detection
- Monitor for unusual request spikes or patterns suggesting scraping or exploitation attempts.

## Implementation
Rate limiting should be enforced at the API gateway layer (e.g., Netlify Edge Functions) or within a shared backend middleware.

---
*Note: This is a planning document only. No functional implementation is included in this build.*
