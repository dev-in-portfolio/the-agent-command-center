## Supabase / Netlify Provider Context

Project: The Agent Command Center

Supabase project ref:

mobvzrkcsfbumgbwvkcp

Supabase project URL:

https://mobvzrkcsfbumgbwvkcp.supabase.co

Provider direction:
- Production database target: Supabase Postgres
- Production auth target: Supabase Auth
- Hosting/runtime target: Netlify + Netlify Functions
- Local development persistence target: SQLite under `.agent_command_center/`

Required local tools:
- Supabase CLI
- Netlify CLI
- Node/npm if installing CLIs with npm

Environment variable names:
- SUPABASE_PROJECT_REF
- SUPABASE_URL
- SUPABASE_ANON_KEY
- SUPABASE_SERVICE_ROLE_KEY
- SUPABASE_DB_PASSWORD
- DATABASE_URL
- MVP_ENABLE_SUPABASE_REQUEST_API
- MVP_ENABLE_REQUEST_API_WRITES
- MVP_ENABLE_SUPABASE_AUTH

Secret destinations:
- Real Supabase anon/publishable key goes in Netlify env and ignored local env files.
- Real Supabase service role key goes in Netlify env and ignored local env files only.
- Real database password goes in Supabase CLI prompt, Netlify env, or ignored local env files only.
- Real full Postgres connection string goes in Netlify env or ignored local env files only.

Never commit:
- Supabase service role key
- Supabase secret key
- database password
- full Postgres connection string with password
- Netlify tokens
- GitHub tokens
- `.env`
- `.env.local`
- `.env.development.local`
- `.supabase.env.local`
- `.agent_command_center/`
- `*.sqlite`
- `*.sqlite3`
- `supabase/.temp`

Current feature flags:
- MVP_ENABLE_SUPABASE_REQUEST_API=false
- MVP_ENABLE_REQUEST_API_WRITES=false
- MVP_ENABLE_SUPABASE_AUTH=false

Safety posture:
- Request API disabled unless explicitly enabled.
- Request API writes disabled unless explicitly enabled.
- Supabase Auth disabled unless explicitly enabled.
- RLS required before production writes.
- Service role key must never be exposed to browser code.
- Production migrations must not be auto-applied by Codex.
- Real automation remains disabled.
- GitHub/Netlify mutation remains disabled.
- Deploy/merge/push/PR controls remain disabled.

Next product direction:
- Merge MVP-2 local durable request persistence.
- Build MVP-3 Supabase Provider + Request API Scaffold.
- Keep request API disabled by default.
- Keep writes disabled by default.
- Build provider status, env contract, migration scaffold, and request API boundary first.
- Do not enable real request writes until auth/RLS/provider setup is reviewed.

