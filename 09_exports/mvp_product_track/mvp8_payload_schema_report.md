# MVP-8 — Payload Schema Report

## Status
DEFINED_AND_ENFORCED

## Verdict
PASS

## Allowed Fields
- title (required, max 160)
- summary (optional, max 2000, maps to `intent`)
- request_type (required, enum, maps to `requested_action`)
- priority (optional, enum)
- source (optional, enum)
- metadata (optional, object)

## Rejected Fields
- id, user_id, actor_id, status, approved, executed, command, secret, etc.

## Result
Strict schema ensures data integrity and prevents unauthorized field injection.
