# MVP-8 — Write Path Review Report

## Verdict
PASS_WITH_TARGETED_REVIEW

## Reviewed Files
- netlify/functions/requests.js
- netlify/functions/_shared/supabase_write_client.js
- netlify/functions/_shared/request_payload_validator.js
- netlify/functions/_shared/auth_context.js
- 14_backend/product_runtime/providers/supabase/migrations/001_supabase_request_runtime.sql
- 14_backend/product_runtime/providers/supabase/migrations/002_supabase_auth_rls_policies.sql

## Confirmations
- **Action Scope:** `create` is the only implemented write action. All other methods (PUT/PATCH/DELETE) and actions are strictly blocked.
- **Feature Flag Gate:** POST create is gated by `MVP_ENABLE_REQUEST_API_WRITES`.
- **Authentication:** Valid Supabase user bearer token is required.
- **Service Role Safety:** `SUPABASE_SERVICE_ROLE_KEY` is not used in the write path. All operations use the anon key + user bearer token.
- **Payload Integrity:** `request_payload_validator.js` enforces a strict schema and rejects forbidden fields (e.g., `secret`, `command`, `status`).
- **RLS Compliance:** The `requests_insert_own` policy (`auth.uid() = actor_id`) matches the server-side insert mapping.
- **Data Integrity:** UUIDs are generated server-side using `crypto.randomUUID()`.
- **Automation Safety:** No command execution, subprocess spawning, or external system mutation (GitHub/Netlify) is enabled.
- **Information Leakage:** Error responses do not leak sensitive environment variables or bearer tokens.

## Result
The MVP-8 write path is secure, narrowly scoped, and adheres to all project safety mandates.
