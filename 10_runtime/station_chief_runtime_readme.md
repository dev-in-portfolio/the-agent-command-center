# Station Chief Runtime Skeleton

## Status
Station Chief Runtime upgraded to v2.6.0. Locked 175-family baseline preserved. Permissioned external API dry-run preview added.

## Purpose
The Station Chief runtime receives one command, classifies it, loads the locked Devinization overlay stack, selects an activation tier, creates a command brief, creates non-executing work orders, writes deterministic artifacts, supports registry/resume, supports gated sandbox and scoped repo patch operations, supports dry-run/approval/ledger/release-lock flows, supports controlled execution profile expansion, supports a dry-run-only work order executor skeleton, supports worker hiring registry preview, supports department routing runtime preview, supports a multi-agent orchestration sandbox, supports UI/operator console schemas, supports GitHub patch application hardening, supports a deployment/portfolio packaging bridge, supports first controlled single-worker sandbox execution, supports single-worker tool permission binding, supports live execution telemetry and abort controls, supports post-run audit proof expansion, supports multi-worker sandbox coordination, supports controlled external tool adapter preview, and now adds permissioned external API dry-run preview.

## What This Adds
- permissioned external API dry-run preview schema
- external API dry-run approval gate
- API endpoint preview registry
- request envelope validation
- credential absence proof
- outbound call prevention proof
- dry-run response fixture contract
- external API audit proof
- external API dry-run ledger
- external API dry-run readiness summary
- controlled multi-worker audit replay preview readiness bridge
- permissioned external API dry-run preview artifact writing
- permissioned external API dry-run preview manifest

## What This Does Not Do
- Does not modify baseline family files
- Does not regenerate exports
- Does not connect live APIs
- no live API calls
- no credential use
- no secret reads
- no environment reads
- no network access
- no socket access
- no external tool invocation
- no shell command execution
- no arbitrary code execution
- no repo mutation
- no deployment
- Does not call live APIs
- Does not invoke external tools
- Does not make network requests
- Does not open sockets
- Does not use credentials
- Does not read secrets
- Does not read environment variables
- Does not fetch external artifacts
- Does not send external telemetry
- Does not call hosting APIs
- Does not deploy to Netlify, Vercel, Cloudflare, Firebase, Railway, Render, GitHub Pages, or external platforms
- Does not animate all 47,250 worker agents
- Does not hire real worker agents
- Does not start worker processes
- Does not execute uncontrolled repo work orders
- Does not execute arbitrary code
- Does not run shell commands
- Does not terminate processes
- Does not start background monitoring
- Does not perform actual replay execution
- Does not assign broad live workers
- Does not route live workers
- Does not perform live orchestration
- Does not render a live UI
- Does not start a server
- Does not call GitHub APIs
- Does not apply uncontrolled repo patches
- Does not push commits
- Does not write to protected baseline or overlay paths
- Does not treat permissioned external API dry-run preview as external execution permission
- Does not build controlled multi-worker audit replay preview yet
- Does not claim full Agent Command Center production completion

## Commands

python3 10_runtime/station_chief_runtime.py --demo

python3 10_runtime/station_chief_runtime.py --external-api-dry-run-schema

python3 10_runtime/station_chief_runtime.py --command "check please" --permissioned-external-api-dry-run

python3 10_runtime/station_chief_runtime.py --command "check please" --permissioned-external-api-dry-run --external-api-confirm-token YES_I_APPROVE_PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW

python3 10_runtime/station_chief_runtime.py --command "build controlled multi-worker audit replay preview" --permissioned-external-api-dry-run --external-api-confirm-token YES_I_APPROVE_PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW

python3 10_runtime/station_chief_runtime.py --command "check please" --permissioned-external-api-dry-run --external-api-confirm-token YES_I_APPROVE_PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW --external-api-endpoint-id github_rest_preview --external-api-requested-endpoint github_rest_preview

python3 10_runtime/station_chief_runtime.py --command "check please" --permissioned-external-api-dry-run --external-api-confirm-token YES_I_APPROVE_PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW --external-api-request-payload-json '{"bad":"api_key=123"}'

python3 10_runtime/station_chief_runtime.py --command "check please" --write-permissioned-external-api-dry-run /tmp/station_chief_external_api_dry_run --external-api-confirm-token YES_I_APPROVE_PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW

python3 10_runtime/station_chief_runtime.py --command "check please" --write-artifacts /tmp/station_chief_runs --registry-dir /tmp/station_chief_registry --permissioned-external-api-dry-run --external-api-confirm-token YES_I_APPROVE_PERMISSIONED_EXTERNAL_API_DRY_RUN_PREVIEW

python3 10_runtime/station_chief_runtime.py --fixture-test

python3 10_runtime/station_chief_fixture_tests.py

## Permissioned External API Dry-Run Preview Artifacts

When --write-permissioned-external-api-dry-run is used, the runtime creates:
- permissioned_external_api_dry_run_preview_bundle.json
- permissioned_external_api_dry_run_preview_schema.json
- external_api_dry_run_approval_gate.json
- api_endpoint_preview_registry.json
- request_envelope_validation.json
- credential_absence_proof.json
- outbound_call_prevention_proof.json
- dry_run_response_fixture_contract.json
- external_api_audit_proof.json
- external_api_dry_run_ledger.json
- external_api_dry_run_readiness_summary.json
- controlled_multi_worker_audit_replay_preview_readiness_bridge.json
- permissioned_external_api_dry_run_preview_manifest.json

## Runtime Doctrine

Station Chief Runtime v2.6.0 adds Permissioned External API Dry-Run Preview without live API execution, credential use, secret reads, environment reads, network access, socket access, external tool invocation, deployment, or broad execution. It creates deterministic API dry-run schemas, approval gates, endpoint preview registries, request envelope validation records, credential absence proofs, outbound call prevention proofs, dry-run response fixture contracts, external API audit proofs, API dry-run ledgers, readiness summaries, and controlled multi-worker audit replay preview handoff records while preserving the locked 175-family baseline, avoiding live external actions, avoiding live API calls, avoiding credential use, avoiding secret reads, avoiding environment reads, avoiding network access, avoiding socket access, avoiding shell commands, avoiding arbitrary code execution, avoiding hosting API calls, avoiding live deployment, avoiding uncontrolled repo edits, avoiding baseline mutation, avoiding Devinization overlay mutation, and avoiding repo file modification.

## Next Recommended Step
Next recommended step: build controlled multi-worker audit replay preview.
