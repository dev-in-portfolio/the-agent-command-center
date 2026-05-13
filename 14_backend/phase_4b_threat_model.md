# Phase 4B: Threat Model

## Threat Matrix

| Threat | Risk | Mitigation | Phase |
|---|---|---|---|
| Exposed Secrets | Critical | No secrets in repo/client. redacting logs. | 4A+ |
| Browser Token Theft | High | HTTP-only cookies, short TTLs. | 4B+ |
| CSRF | High | Same-origin restriction, Anti-CSRF tokens. | 4B+ |
| XSS | Medium | Strict Content Security Policy (CSP). | 3+ |
| Command Injection | Critical | No shell execution from web logic. | 1+ |
| GitHub Token Misuse | Critical | Server-side only, scoped permissions. | 4C+ |
| Unauthorized Deploy | High | Multiple human approvals (Action Queue). | 4D+ |
| Audit Log Tampering | High | Immutable storage goal. | 4B+ |
| Operator Confusion | Medium | Clear UI status, explicit confirmation steps. | 3+ |
| Accidental Production Mutation | High | Separate staging/preview boundaries. | 4A+ |

## Boundary Invariants
- No backend code will ever use `eval()` or dynamic command string construction.
- GitHub mutation is forbidden until Phase 5+.
- Every sensitive action must have a traceable human-in-the-loop approval.

---
*Note: This is a planning document only. No functional implementation is included in this build.*
