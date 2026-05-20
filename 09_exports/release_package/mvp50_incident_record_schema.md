# MVP-50 — Incident Record Schema

## Overview
Defines the incident record schema: incident ID, severity, status, affected components, timestamps, resolution notes.

## Fields
- incident_id: unique identifier
- severity: critical/high/medium/low
- status: open/acknowledged/investigating/resolved/closed
- affected_components: list of impacted services
- detected_at: incident detection timestamp
- resolved_at: resolution timestamp
- resolution_notes: summary of corrective action

## Safety
SCHEMA_READINESS_ONLY | NO_REAL_INCIDENT_RESPONSE
