# Station Chief Runtime Skeleton

## Status
Station Chief Runtime upgraded to v3.4.0. Locked 175-family baseline preserved. Supervised external API pilot added.

## Purpose
The Station Chief runtime receives one command, classifies it, loads the locked Devinization overlay stack, selects an activation tier, creates a command brief, creates non-executing work orders, writes deterministic artifacts, supports registry/resume, supports gated sandbox and scoped repo patch operations, supports dry-run/approval/ledger/release-lock flows, supports controlled execution profile expansion, supports a dry-run-only work order executor skeleton, supports worker hiring registry preview, supports department routing runtime preview, supports a multi-agent orchestration sandbox, supports UI/operator console schemas, supports GitHub patch application hardening, supports deployment/portfolio packaging bridge, supports first controlled single-worker sandbox execution, supports single-worker tool permission binding, supports live execution telemetry and abort controls, supports post-run audit proof expansion, supports multi-worker sandbox coordination, supports controlled external tool adapter preview, supports permissioned external API dry-run preview, supports controlled multi-worker audit replay preview, supports operator approval queue enforcement, supports release candidate hardening, supports controlled production readiness gate, supports controlled worker hiring activation pilot, supports first supervised production dry-run, supports limited external tool supervised pilot, and now adds supervised external API pilot.

## What This Adds
- supervised external API pilot schema
- supervised external API pilot approval gate
- single API category contract
- credential denial by default
- secret handling denial by default
- network/socket denial by default
- human API-use preflight gate
- API request envelope preview
- API response quarantine preview
- API audit proof
- API pilot ledger
- API pilot readiness summary
- monitored rollback and recovery drill bridge
- supervised external API pilot artifact writing
- supervised external API pilot manifest

## What This Does Not Do
- Does not modify baseline family files
- Does not regenerate exports
- no live API calls
- no network access
- no socket access
- no credential use
- no secret reads
- no environment reads
- Does not invoke external tools
- no deployment
- no production execution
- Does not activate production
- Does not execute real tasks
- Does not assign live tasks
- Does not route live workers
- Does not perform live orchestration
- Does not start worker processes
- Does not activate the full 47,250-worker workforce
- Does not execute queued actions
- Does not auto-approve queue items
- Does not bypass approval
- Does not execute actual replay
- Does not execute arbitrary code
- Does not run shell commands
- Does not terminate processes
- Does not start background monitoring
- Does not write to protected baseline or overlay paths
- Does not treat supervised external API pilot records as execution permission
- Does not build monitored rollback and recovery drill yet

## Commands

python3 10_runtime/station_chief_runtime.py --demo

python3 10_runtime/station_chief_runtime.py --supervised-external-api-pilot-schema

python3 10_runtime/station_chief_runtime.py --command "check please" --supervised-external-api-pilot

python3 10_runtime/station_chief_runtime.py --command "check please" --supervised-external-api-pilot --api-pilot-confirm-token YES_I_APPROVE_SUPERVISED_EXTERNAL_API_PILOT

python3 10_runtime/station_chief_runtime.py --command "build monitored rollback and recovery drill" --supervised-external-api-pilot --api-pilot-confirm-token YES_I_APPROVE_SUPERVISED_EXTERNAL_API_PILOT

python3 10_runtime/station_chief_runtime.py --command "check please" --supervised-external-api-pilot --api-pilot-confirm-token YES_I_APPROVE_SUPERVISED_EXTERNAL_API_PILOT --api-category-label "read-only-public-status-api-preview"

python3 10_runtime/station_chief_runtime.py --command "check please" --write-supervised-external-api-pilot /tmp/station_chief_supervised_external_api_pilot --api-pilot-confirm-token YES_I_APPROVE_SUPERVISED_EXTERNAL_API_PILOT

python3 10_runtime/station_chief_runtime.py --command "check please" --write-artifacts /tmp/station_chief_runs --registry-dir /tmp/station_chief_registry --supervised-external-api-pilot --api-pilot-confirm-token YES_I_APPROVE_SUPERVISED_EXTERNAL_API_PILOT

python3 10_runtime/station_chief_runtime.py --fixture-test

python3 10_runtime/station_chief_fixture_tests.py

## Runtime Doctrine

Station Chief Runtime v3.4.0 adds Supervised External API Pilot without live API calls, network access, socket access, credential use, secret reads, environment reads, deployment, real external tool invocation, real production execution, production activation, real task execution, live task assignment, live worker routing, live orchestration, worker process starts, shell command execution, or broad workforce activation. It creates deterministic API pilot schemas, approval gates, single API category contracts, credential denial-by-default records, secret handling denial-by-default records, network/socket denial-by-default records, human API-use preflight gates, API request envelope previews, API response quarantine previews, API audit proofs, API pilot ledgers, readiness summaries, and monitored rollback and recovery drill bridge records while preserving the locked 175-family baseline, avoiding live external actions, avoiding live API calls, avoiding credential use, avoiding secret reads, avoiding environment reads, avoiding network access, avoiding socket access, avoiding shell commands, avoiding arbitrary code execution, avoiding hosting API calls, avoiding live deployment, avoiding uncontrolled repo edits, avoiding baseline mutation, avoiding Devinization overlay mutation, and avoiding repo file modification.

## Next Recommended Step
Next recommended step: build monitored rollback and recovery drill.