# Station Chief Runtime Skeleton

## Status
Station Chief Runtime upgraded to v2.8.0. Locked 175-family baseline preserved. Operator approval queue enforcement added.

## Purpose
The Station Chief runtime receives one command, classifies it, loads the locked Devinization overlay stack, selects an activation tier, creates a command brief, creates non-executing work orders, writes deterministic artifacts, supports registry/resume, supports gated sandbox and scoped repo patch operations, supports dry-run/approval/ledger/release-lock flows, supports controlled execution profile expansion, supports a dry-run-only work order executor skeleton, supports worker hiring registry preview, supports department routing runtime preview, supports a multi-agent orchestration sandbox, supports UI/operator console schemas, supports GitHub patch application hardening, supports a deployment/portfolio packaging bridge, supports first controlled single-worker sandbox execution, supports single-worker tool permission binding, supports live execution telemetry and abort controls, supports post-run audit proof expansion, supports multi-worker sandbox coordination, supports controlled external tool adapter preview, supports permissioned external API dry-run preview, supports controlled multi-worker audit replay preview, and now adds operator approval queue enforcement.

## What This Adds
- operator approval queue enforcement schema
- operator approval queue enforcement approval gate
- queued action registry
- approval item priority classifier
- operator decision contract
- approval expiry and stale-item detector
- queue enforcement safety gate
- approval queue audit proof
- approval queue ledger
- approval queue readiness summary
- release candidate hardening readiness bridge
- operator approval queue enforcement artifact writing
- operator approval queue enforcement manifest

## What This Does Not Do
- Does not modify baseline family files
- Does not regenerate exports
- no queued action execution
- no automatic approval
- no approval bypass
- no actual replay execution
- no worker action re-execution
- no external tool replay
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
- no actual replay execution

## Commands

python3 10_runtime/station_chief_runtime.py --demo

python3 10_runtime/station_chief_runtime.py --operator-approval-queue-schema

python3 10_runtime/station_chief_runtime.py --command "check please" --operator-approval-queue-enforcement

python3 10_runtime/station_chief_runtime.py --command "check please" --operator-approval-queue-enforcement --approval-queue-confirm-token YES_I_APPROVE_OPERATOR_APPROVAL_QUEUE_ENFORCEMENT

python3 10_runtime/station_chief_runtime.py --command "build release candidate hardening" --operator-approval-queue-enforcement --approval-queue-confirm-token YES_I_APPROVE_OPERATOR_APPROVAL_QUEUE_ENFORCEMENT

python3 10_runtime/station_chief_runtime.py --command "check please" --operator-approval-queue-enforcement --approval-queue-confirm-token YES_I_APPROVE_OPERATOR_APPROVAL_QUEUE_ENFORCEMENT --approval-queue-action-count 2

python3 10_runtime/station_chief_runtime.py --command "check please" --operator-approval-queue-enforcement --approval-queue-confirm-token YES_I_APPROVE_OPERATOR_APPROVAL_QUEUE_ENFORCEMENT --approval-queue-operator-decisions-json '{"queued-action-001":"APPROVE_AND_EXECUTE"}'

python3 10_runtime/station_chief_runtime.py --command "check please" --write-operator-approval-queue-enforcement /tmp/station_chief_operator_approval_queue --approval-queue-confirm-token YES_I_APPROVE_OPERATOR_APPROVAL_QUEUE_ENFORCEMENT

python3 10_runtime/station_chief_runtime.py --command "check please" --write-artifacts /tmp/station_chief_runs --registry-dir /tmp/station_chief_registry --operator-approval-queue-enforcement --approval-queue-confirm-token YES_I_APPROVE_OPERATOR_APPROVAL_QUEUE_ENFORCEMENT

python3 10_runtime/station_chief_runtime.py --fixture-test

python3 10_runtime/station_chief_fixture_tests.py

## Operator Approval Queue Enforcement Artifacts

When --write-operator-approval-queue-enforcement is used, the runtime creates:
- operator_approval_queue_enforcement_bundle.json
- operator_approval_queue_enforcement_schema.json
- operator_approval_queue_enforcement_approval_gate.json
- queued_action_registry.json
- approval_item_priority_classifier.json
- operator_decision_contract.json
- approval_expiry_stale_item_detector.json
- queue_enforcement_safety_gate.json
- approval_queue_audit_proof.json
- approval_queue_ledger.json
- approval_queue_readiness_summary.json
- release_candidate_hardening_readiness_bridge.json
- operator_approval_queue_enforcement_manifest.json

## Runtime Doctrine

Station Chief Runtime v2.8.0 adds Operator Approval Queue Enforcement without queued action execution, automatic approval, approval bypass, actual replay execution, worker action re-execution, external tool replay, live API replay, credential use, secret reads, environment reads, network access, socket access, deployment, or broad execution. It creates deterministic approval queue schemas, approval gates, queued action registries, priority classifiers, operator decision contracts, stale-item detectors, queue enforcement safety gates, approval queue audit proofs, queue ledgers, readiness summaries, and release candidate hardening handoff records while preserving the locked 175-family baseline, avoiding live external actions, avoiding queued action execution, avoiding auto-approval, avoiding approval bypass, avoiding actual replay execution, avoiding worker action re-execution, avoiding external tool replay, avoiding live API calls, avoiding credential use, avoiding secret reads, avoiding environment reads, avoiding network access, avoiding socket access, avoiding shell commands, avoiding arbitrary code execution, avoiding hosting API calls, avoiding live deployment, avoiding uncontrolled repo edits, avoiding baseline mutation, avoiding Devinization overlay mutation, and avoiding repo file modification.

## Next Recommended Step
Next recommended step: build release candidate hardening.
