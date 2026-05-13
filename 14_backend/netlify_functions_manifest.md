# Netlify Functions Manifest

## Same-Site Reuse
This backend foundation reuses the existing Netlify site `the-agent-command-center-dashboard.netlify.app`.

## Directory
`netlify/functions`

## Functions
- `health.js`: Exposes `/api/health`
- `status.js`: Exposes `/api/status`
- `backend-manifest.js`: Exposes `/api/backend-manifest`

## Shared
- `_shared/response.js`: JSON response helpers

## Redirects
Configured in `netlify.toml`:
```toml
[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

## Branch Preview
Netlify will automatically create a deploy preview for the `backend/phase-4-read-only-api-foundation` branch, allowing the new endpoints to be tested before merging to master.
