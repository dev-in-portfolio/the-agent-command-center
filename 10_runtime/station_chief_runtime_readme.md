# Station Chief Runtime Skeleton

## Status
Station Chief Runtime upgraded to v3.2.0. Locked 175-family baseline preserved. First supervised production dry-run added.

## Purpose
The Station Chief runtime receives one command, classifies it, loads the locked Devinization overlay stack, selects an activation tier, creates a command brief, creates non-executing work orders, writes deterministic artifacts, supports registry/resume, supports gated sandbox and scoped repo patch operations, supports dry-run/approval/ledger/release-lock flows, supports controlled execution profile expansion, supports a dry-run-only work order executor skeleton, supports worker hiring registry preview, supports department routing runtime preview, supports a multi-agent orchestration sandbox, supports UI/operator console schemas, supports GitHub patch application hardening, supports deployment/portfolio packaging bridge, supports first controlled single-worker sandbox execution, supports single-worker tool permission binding, supports live execution telemetry and abort controls, supports post-run audit proof expansion, supports multi-worker sandbox coordination, supports controlled external tool adapter preview, supports permissioned external API dry-run preview, supports controlled multi-worker audit replay preview, supports operator approval queue enforcement, supports release candidate hardening, supports controlled production readiness gate, supports controlled worker hiring activation pilot, and now adds first supervised production dry-run.

## What This Adds
- first supervised production dry-run schema
- first supervised production dry-run approval gate
- single controlled task dry-run envelope
- dry-run-only production context contract
- human preflight approval gate
- worker task simulation contract
- external action denial by default
- dry-run rollback and quarantine preview
- dry-run audit proof
- dry-run ledger
- dry-run readiness summary
- limited external tool supervised pilot bridge
- first supervised production dry-run artifact writing
- first supervised production dry-run manifest

## What This Does Not Do
- Does not modify baseline family files
- Does not regenerate exports
- Does not execute real production
- Does not activate production
- Does not execute real tasks
- Does not assign live tasks
- Does not route live workers
- Does not perform live orchestration
- Does not invoke external tools
- Does not call live APIs
- Does not make network requests
- Does not open sockets
- Does not use credentials
- Does not read secrets
- Does not read environment variables
- Does not call hosting APIs
- Does not deploy
- Does not execute arbitrary code
- Does not run shell commands
- Does not terminate processes
- Does not start background monitoring
- Does not write to protected baseline or overlay paths
- Does not treat first supervised production dry-run records as execution permission
- Does not build limited external tool supervised pilot yet
- no real production execution
- no production activation
- no real task execution
- no live task assignment
- no live worker routing
- no live orchestration
- no external tool invocation
- no live API calls
- no credential use
- no secret reads
- no environment reads
- no network access
- no socket access
- no deployment
- no shell command execution
- no arbitrary code execution
- no full workforce activation

## Commands

python3 10_runtime/station_chief_runtime.py --demo

python3 10_runtime/station_chief_runtime.py --first-supervised-production-dry-run-schema

python3 10_runtime/station_chief_runtime.py --command "check please" --first-supervised-production-dry-run

python3 10_runtime/station_chief_runtime.py --command "check please" --first-supervised-production-dry-run --dry-run-confirm-token YES_I_APPROVE_FIRST_SUPERVISED_PRODUCTION_DRY_RUN

python3 10_runtime/station_chief_runtime.py --command "build limited external tool supervised pilot" --first-supervised-production-dry-run --dry-run-confirm-token YES_I_APPROVE_FIRST_SUPERVISED_PRODUCTION_DRY_RUN

python3 10_runtime/station_chief_runtime.py --command "check please" --first-supervised-production-dry-run --dry-run-confirm-token YES_I_APPROVE_FIRST_SUPERVISED_PRODUCTION_DRY_RUN --dry-run-task-label "single simulated production task"

python3 10_runtime/station_chief_runtime.py --command "check please" --write-first-supervised-production-dry-run /tmp/station_chief_first_supervised_production_dry_run --dry-run-confirm-token YES_I_APPROVE_FIRST_SUPERVISED_PRODUCTION_DRY_RUN

python3 10_runtime/station_chief_runtime.py --command "check please" --write-artifacts /tmp/station_chief_runs --registry-dir /tmp/station_chief_registry --first-supervised-production-dry-run --dry-run-confirm-token YES_I_APPROVE_FIRST_SUPERVISED_PRODUCTION_DRY_RUN

python3 10_runtime/station_chief_runtime.py --fixture-test

python3 10_runtime/station_chief_fixture_tests.py

## Runtime Doctrine

Station Chief Runtime v3.2.0 adds First Supervised Production Dry-Run without real production execution, production activation, real task execution, live task assignment, live worker routing, live orchestration, external tool invocation, live API calls, credential use, secret reads, environment reads, network access, socket access, deployment, worker process starts, shell command execution, or broad workforce activation. It creates deterministic dry-run schemas, approval gates, single controlled task dry-run envelopes, dry-run-only production context contracts, human preflight approval gates, worker task simulation contracts, external action denial-by-default records, rollback and quarantine preview records, dry-run audit proofs, dry-run ledgers, readiness summaries, and limited external tool supervised pilot bridge records while preserving the locked 175-family baseline, avoiding live external actions, avoiding real production execution, avoiding production activation, avoiding real task execution, avoiding live task assignment, avoiding live worker routing, avoiding live orchestration, avoiding external tool invocation, avoiding live API calls, avoiding credential use, avoiding secret reads, avoiding environment reads, avoiding network access, avoiding socket access, avoiding shell commands, avoiding arbitrary code execution, avoiding hosting API calls, avoiding live deployment, avoiding uncontrolled repo edits, avoiding baseline mutation, avoiding Devinization overlay mutation, and avoiding repo file modification.

## Next Recommended Step
Next recommended step: build limited external tool supervised pilot.
