# MVP-3 — Env Contract Report

## Verdict
PASS_WITH_HIGH_CONFIDENCE

## Environment Variable Names
- SUPABASE_PROJECT_REF
- SUPABASE_URL
- SUPABASE_ANON_KEY
- SUPABASE_SERVICE_ROLE_KEY
- SUPABASE_DB_PASSWORD
- DATABASE_URL
- MVP_ENABLE_SUPABASE_REQUEST_API
- MVP_ENABLE_REQUEST_API_WRITES
- MVP_ENABLE_SUPABASE_AUTH

## Safety Boundary
- Env values are never printed.
- Browser exposure for the service role is forbidden.
- Request API writes are disabled by default.
- Supabase Auth is disabled by default.

