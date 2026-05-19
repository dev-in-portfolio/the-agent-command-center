# MVP-50 — Health Signal Schema Report

## Overview
Defines the health signal schema for alert source modeling.

## Status
HEALTH_SIGNAL_SCHEMA_READY

## Key Fields
- signal_type: category of health signal (latency, error, uptime, throughput)
- severity: severity level of the signal
- source: origin component or service
- condition: threshold expression that triggers the signal
- cooldown: minimum interval between repeated signals
- notification_target: intended recipient or channel

## Safety
SCHEMA_READINESS_ONLY | NO_REAL_ALERT_DISPATCH
