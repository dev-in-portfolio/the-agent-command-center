# MVP-50 — Incident Record Schema Report

## Overview
Defines the incident record model for tracking operational incidents.

## Status
INCIDENT_RECORD_SCHEMA_READY

## Key Fields
- id: unique incident identifier
- title: human-readable incident summary
- severity: incident severity classification
- status: current incident lifecycle state
- assigned_resource: operator or team responsible
- timestamps: detection, acknowledgment, resolution times
- linked_signals: references to related health signals

## Safety
SCHEMA_READINESS_ONLY | NO_REAL_INCIDENT_RESPONSE
