# Technical Reviewer Brief

## Focus: Architecture & Security

### The Stack
- **Dashboard:** Static HTML/JS with JSON UI models.
- **Backend:** Netlify Functions (Node.js).
- **Database:** Supabase (Auth, PostgREST, RLS).

### Key Architectural Patterns
1. **The Proxy Boundary:** The browser never calls Supabase directly. All requests go through Netlify Functions, which validate the bearer token and proxy the request using the `anon` key + user token.
2. **Row Level Security (RLS):** Data ownership is enforced at the database level. Queries automatically filter for `actor_id = auth.uid()`.
3. **Safe Error Handling:** Catch blocks map raw database errors to stable, generic error codes. `err.message` is never forwarded to the client.
4. **Controlled Writes:** Write actions (POST) are limited to creation of requests and lifecycle events only. Patching parent request rows is explicitly blocked in the API handler.

### What to Look For
- Inspect `netlify/functions/requests.js` for the action router and safe error mapping.
- Inspect `scripts/validate_...` for the tiered validation discipline.
- Check the `ui_models/` for the contract-driven dashboard design.
