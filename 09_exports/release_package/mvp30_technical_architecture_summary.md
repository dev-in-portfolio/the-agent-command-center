# MVP-30 — Technical Architecture Summary

The release package is built on top of the static dashboard and exported UI models.

Architecture summary:
- read-only dashboard rendering,
- exportable markdown and JSON packets,
- local copy-to-clipboard controls,
- no client-side secret storage,
- no direct browser Supabase access,
- no execution controls,
- no automation controls,
- no deploy/merge/push controls.
