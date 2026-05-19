# MVP-50 — Health Signal Schema

## Overview
Defines the health signal schema: signal type, severity, source, condition, cooldown, notification preferences.

## Fields
- signal_type: type identifier
- severity: critical/warning/info
- source: originating component
- condition: evaluation rule expression
- cooldown: minimum interval between signals
- notification_target: destination channel

## Safety
SCHEMA_READINESS_ONLY | NO_REAL_ALERT_DISPATCH
