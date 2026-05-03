# Station Chief Runtime Skeleton

## Status
Station Chief Runtime upgraded to v3.0.0. Locked 175-family baseline preserved. Controlled production readiness gate added.

## Purpose
The Station Chief runtime receives one command, classifies it, loads the locked Devinization overlay stack, selects an activation tier, creates a command brief, creates non-executing work orders, writes deterministic artifacts, supports registry/resume, supports gated sandbox and scoped repo patch operations, supports dry-run/approval/ledger/release-lock flows, supports controlled execution profile expansion, supports a dry-run-only work order executor skeleton, supports worker hiring registry preview, supports department routing runtime preview, supports a multi-agent orchestration sandbox, supports UI/operator console schemas, supports GitHub patch application hardening, supports a deployment/portfolio packaging bridge, supports first controlled single-worker sandbox execution, supports single-worker tool permission binding, supports live execution telemetry and abort controls, supports post-run audit proof expansion, supports multi-worker sandbox coordination, supports controlled external tool adapter preview, supports permissioned external API dry-run preview, supports controlled multi-worker audit replay preview, supports operator approval queue enforcement, supports release candidate hardening, and now adds controlled production readiness gate.

## What This Adds
- controlled production readiness gate schema
- controlled production readiness gate approval gate
- production activation denial by default
- final human approval requirement
- production capability manifest
- supervised pilot eligibility contract
- production rollback and kill-switch preview
- production readiness audit proof
- production readiness ledger
- production readiness summary
- controlled worker hiring activation pilot bridge
- controlled production readiness gate artifact writing
- controlled production readiness gate manifest

## What This Does Not Do
- Does not modify baseline family files
- Does not regenerate exports
- Does not activate production
- Does not execute production workflows
- Does not hire real workers
- Does not activate real workers
- Does not route live workers
- Does not perform live orchestration
- Does not execute queued actions
- Does not auto-approve queue items
- Does not bypass approval
- Does not execute actual replay
- Does not replay worker actions
- Does not replay external tools
- Does not connect live APIs
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
- Does not start worker processes
- Does not execute uncontrolled repo work orders
- Does not execute arbitrary code
- Does not run shell commands
- Does not terminate processes
- Does not start background monitoring
- Does not render a live UI
- Does not start a server
- Does not call GitHub APIs
- Does not apply uncontrolled repo patches
- Does not push commits
- Does not write to protected baseline or overlay paths
- Does not treat controlled production readiness gate records as execution permission
- Does not build controlled worker hiring activation pilot yet
- Does not claim full Agent Command Center production completion

## Commands

python3 10_runtime/station_chief_runtime.py --demo

python3 10_runtime/station_chief_runtime.py --production-readiness-gate-schema

python3 10_runtime/station_chief_runtime.py --command "check please" --controlled-production-readiness-gate

python3 10_runtime/station_chief_runtime.py --command "check please" --controlled-production-readiness-gate --production-gate-confirm-token YES_I_APPROVE_CONTROLLED_PRODUCTION_READINESS_GATE

python3 10_runtime/station_chief_runtime.py --command "build controlled worker hiring activation pilot" --controlled-production-readiness-gate --production-gate-confirm-token YES_I_APPROVE_CONTROLLED_PRODUCTION_READINESS_GATE

python3 10_runtime/station_chief_runtime.py --command "check please" --controlled-production-readiness-gate --production-gate-confirm-token YES_I_APPROVE_CONTROLLED_PRODUCTION_READINESS_GATE --production-gate-pilot-worker-limit 2

python3 10_runtime/station_chief_runtime.py --command "check please" --write-controlled-production-readiness-gate /tmp/station_chief_controlled_production_readiness_gate --production-gate-confirm-token YES_I_APPROVE_CONTROLLED_PRODUCTION_READINESS_GATE

python3 10_runtime/station_chief_runtime.py --command "check please" --write-artifacts /tmp/station_chief_runs --registry-dir /tmp/station_chief_registry --controlled-production-readiness-gate --production-gate-confirm-token YES_I_APPROVE_CONTROLLED_PRODUCTION_READINESS_GATE

python3 10_runtime/station_chief_runtime.py --fixture-test

python3 10_runtime/station_chief_fixture_tests.py

## Controlled Production Readiness Gate Artifacts

When --write-controlled-production-readiness-gate is used, the runtime creates:
- controlled_production_readiness_gate_bundle.json
- controlled_production_readiness_gate_schema.json
- controlled_production_readiness_gate_approval_gate.json
- production_activation_denial_by_default.json
- final_human_approval_requirement.json
- production_capability_manifest.json
- supervised_pilot_eligibility_contract.json
- production_rollback_kill_switch_preview.json
- production_readiness_audit_proof.json
- production_readiness_ledger.json
- production_readiness_summary.json
- controlled_worker_hiring_activation_pilot_bridge.json
- controlled_production_readiness_gate_manifest.json

## Runtime Doctrine

Station Chief Runtime v3.0.0 adds Controlled Production Readiness Gate without production execution, production activation, live worker hiring, live worker activation, live worker routing, live orchestration, queued action execution, automatic approval, approval bypass, actual replay execution, worker action re-execution, external tool replay, live API replay, credential use, secret reads, environment reads, network access, socket access, deployment, or broad execution. It creates deterministic controlled production readiness schemas, approval gates, production activation denial records, final human approval requirement records, production capability manifests, supervised pilot eligibility contracts, rollback and kill-switch preview records, production readiness audit proofs, production readiness ledgers, readiness summaries, and controlled worker hiring activation pilot handoff records while preserving the locked 175-family baseline, avoiding live external actions, avoiding production execution, avoiding production activation, avoiding real worker hiring, avoiding real worker activation, avoiding live worker routing, avoiding live orchestration, avoiding queued action execution, avoiding auto-approval, avoiding approval bypass, avoiding actual replay execution, avoiding worker action re-execution, avoiding external tool replay, avoiding live API calls, avoiding credential use, avoiding secret reads, avoiding environment reads, avoiding network access, avoiding socket access, avoiding shell commands, avoiding arbitrary code execution, avoiding hosting API calls, avoiding live deployment, avoiding uncontrolled repo edits, avoiding baseline mutation, avoiding Devinization overlay mutation, and avoiding repo file modification.

## Next Recommended Step
Next recommended step: build controlled worker hiring activation pilot.
