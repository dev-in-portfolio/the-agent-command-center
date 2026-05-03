# Station Chief Runtime Skeleton

## Status
Station Chief Runtime upgraded to v2.9.0. Locked 175-family baseline preserved. Release candidate hardening added.

## Purpose
The Station Chief runtime receives one command, classifies it, loads the locked Devinization overlay stack, selects an activation tier, creates a command brief, creates non-executing work orders, writes deterministic artifacts, supports registry/resume, supports gated sandbox and scoped repo patch operations, supports dry-run/approval/ledger/release-lock flows, supports controlled execution profile expansion, supports a dry-run-only work order executor skeleton, supports worker hiring registry preview, supports department routing runtime preview, supports a multi-agent orchestration sandbox, supports UI/operator console schemas, supports GitHub patch application hardening, supports a deployment/portfolio packaging bridge, supports first controlled single-worker sandbox execution, supports single-worker tool permission binding, supports live execution telemetry and abort controls, supports post-run audit proof expansion, supports multi-worker sandbox coordination, supports controlled external tool adapter preview, supports permissioned external API dry-run preview, supports controlled multi-worker audit replay preview, supports operator approval queue enforcement, and now adds release candidate hardening.

## What This Adds
- release candidate hardening schema
- release candidate hardening approval gate
- full runtime invariant scan
- validator chain lock proof
- artifact contract freeze manifest
- known issue register
- pre-v3 production readiness checklist
- release candidate safety gate
- release candidate audit proof
- release candidate ledger
- release candidate readiness summary
- controlled production readiness gate bridge
- release candidate hardening artifact writing
- release candidate hardening manifest
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
- no production execution
- no production readiness gate activation
- no queued action execution
- no auto-approval
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

python3 10_runtime/station_chief_runtime.py --release-candidate-hardening-schema

python3 10_runtime/station_chief_runtime.py --command "check please" --release-candidate-hardening

python3 10_runtime/station_chief_runtime.py --command "check please" --release-candidate-hardening --release-candidate-confirm-token YES_I_APPROVE_RELEASE_CANDIDATE_HARDENING

python3 10_runtime/station_chief_runtime.py --command "build controlled production readiness gate" --release-candidate-hardening --release-candidate-confirm-token YES_I_APPROVE_RELEASE_CANDIDATE_HARDENING

python3 10_runtime/station_chief_runtime.py --command "check please" --release-candidate-hardening --release-candidate-confirm-token YES_I_APPROVE_RELEASE_CANDIDATE_HARDENING --release-candidate-known-issue-json '{"issue_label":"manual review required","issue_severity":"HIGH","blocks_release_candidate":true}'

python3 10_runtime/station_chief_runtime.py --command "check please" --write-release-candidate-hardening /tmp/station_chief_release_candidate_hardening --release-candidate-confirm-token YES_I_APPROVE_RELEASE_CANDIDATE_HARDENING

python3 10_runtime/station_chief_runtime.py --command "check please" --write-artifacts /tmp/station_chief_runs --registry-dir /tmp/station_chief_registry --release-candidate-hardening --release-candidate-confirm-token YES_I_APPROVE_RELEASE_CANDIDATE_HARDENING

python3 10_runtime/station_chief_runtime.py --fixture-test

python3 10_runtime/station_chief_fixture_tests.py

## Release Candidate Hardening Artifacts

When --write-release-candidate-hardening is used, the runtime creates:
- release_candidate_hardening_bundle.json
- release_candidate_hardening_schema.json
- release_candidate_hardening_approval_gate.json
- full_runtime_invariant_scan.json
- validator_chain_lock_proof.json
- artifact_contract_freeze_manifest.json
- known_issue_register.json
- pre_v3_production_readiness_checklist.json
- release_candidate_safety_gate.json
- release_candidate_audit_proof.json
- release_candidate_ledger.json
- release_candidate_readiness_summary.json
- controlled_production_readiness_gate_bridge.json
- release_candidate_hardening_manifest.json

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

Station Chief Runtime v2.9.0 adds Release Candidate Hardening without production execution, production readiness gate activation, queued action execution, automatic approval, approval bypass, actual replay execution, worker action re-execution, external tool replay, live API replay, credential use, secret reads, environment reads, network access, socket access, deployment, or broad execution. It creates deterministic release candidate schemas, approval gates, full runtime invariant scans, validator chain lock proofs, artifact contract freeze manifests, known issue registers, pre-v3 production readiness checklists, release candidate safety gates, release candidate audit proofs, release candidate ledgers, readiness summaries, and controlled production readiness gate handoff records while preserving the locked 175-family baseline, avoiding live external actions, avoiding production execution, avoiding production readiness gate activation, avoiding queued action execution, avoiding auto-approval, avoiding approval bypass, avoiding actual replay execution, avoiding worker action re-execution, avoiding external tool replay, avoiding live API calls, avoiding credential use, avoiding secret reads, avoiding environment reads, avoiding network access, avoiding socket access, avoiding shell commands, avoiding arbitrary code execution, avoiding hosting API calls, avoiding live deployment, avoiding uncontrolled repo edits, avoiding baseline mutation, avoiding Devinization overlay mutation, and avoiding repo file modification.

## Next Recommended Step
Next recommended step: build controlled production readiness gate.
