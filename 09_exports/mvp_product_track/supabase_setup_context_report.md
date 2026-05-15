# Supabase Setup Context Report

## Status
PROVIDER_CONTEXT_READY

## Project Ref
mobvzrkcsfbumgbwvkcp

## Project URL
https://mobvzrkcsfbumgbwvkcp.supabase.co

## Provider Direction
- Production database target: Supabase Postgres
- Production auth target: Supabase Auth
- Hosting/runtime target: Netlify Functions
- Local development persistence target: SQLite

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

## Secret Destinations
- Netlify environment variables
- ignored local env file `.supabase.env.local`
- Supabase CLI interactive password prompt

## Safety Boundary
- Request API disabled by default.
- Request API writes disabled by default.
- Supabase Auth disabled by default.
- RLS is required before production writes.
- Production migrations are not auto-applied.
- Service role key must never be exposed to browser code.
- Real automation remains disabled.

## Next Step
Use this setup context while running the MVP-2 merge + MVP-3 Supabase Provider Request API Scaffold prompt.

