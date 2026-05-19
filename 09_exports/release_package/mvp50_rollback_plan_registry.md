# MVP-50 — Rollback Plan Registry

## Overview
Defines the rollback plan registry schema: plan ID, target component, rollback steps, validation criteria, approval gate.

## Fields
- plan_id: unique rollback plan identifier
- target_component: service or resource to rollback
- rollback_steps: ordered sequence of rollback actions
- validation_criteria: conditions confirming successful rollback
- approval_required: gate requirement flag
- rollback_timeout: maximum execution window

## Safety
SCHEMA_READINESS_ONLY | NO_REAL_ROLLBACK
