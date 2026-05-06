# Station Chief v4.0 Prompt v0.1

## Purpose
Write one local deterministic reversible proof artifact only.

This prompt is for the first tiny real-world supervised execution candidate after separate human approval.
It does not authorize broad automation, production execution, live API use, network use, sockets, credentials, secrets, environment reads, deployment, or worker activation.

## Candidate
- Candidate label: `station-chief-v4-local-deterministic-reversible-proof-artifact`
- Artifact name: `first_tiny_supervised_execution_candidate_proof.json`
- Output directory: `<<OPERATOR_APPROVED_OUTPUT_DIR>>`
- Approval token: `<<OPERATOR_APPROVED_V4_TOKEN>>`

## Required Preconditions
- Station Chief Runtime v3.9.0 is confirmed.
- Pre-v4 runtime hardening is confirmed.
- Non-runtime readiness docs exist.
- Operator playbook exists.
- Governance checklist exists.
- Separate human approval is recorded for this exact candidate.
- The output directory is explicit and operator-approved.
- The approved candidate is local only, deterministic, reversible, supervised, and tiny.

## Instructions
1. Write exactly one JSON file named `first_tiny_supervised_execution_candidate_proof.json` inside `<<OPERATOR_APPROVED_OUTPUT_DIR>>`.
2. Do not write any other file unless the operator explicitly approved it in writing.
3. Do not modify repo files, baseline files, Devinization overlays, dashboard exports, org-chart exports, master department list files, ownership metadata, runtime code, validators, or scripts.
4. Do not call APIs.
5. Do not use network access.
6. Do not open sockets.
7. Do not read secrets.
8. Do not read environment variables.
9. Do not deploy.
10. Do not execute production.
11. Do not activate workers.
12. Do not route live tasks.

## Artifact Contract
The JSON artifact must include:
- `runtime_version`
- `candidate_label`
- `approval_token_valid`
- `output_directory`
- `forbidden_paths`
- `safety_booleans`
- `digest`
- `cleanup_instructions`
- `verification_status`

The JSON artifact must omit nondeterministic timestamps unless an explicit deterministic timestamp scheme is part of the approved design.

## Required Safety Booleans
All dangerous booleans must remain `false`, including:
- live API call performed
- network access performed
- socket opened
- DNS resolution performed
- outbound connection performed
- credential use
- secret read
- environment read
- deployment performed
- production execution performed
- production activation performed
- live task assignment performed
- live worker routing performed
- live orchestration performed
- worker processes started
- full workforce activation performed

## Cleanup
Cleanup is allowed only inside `<<OPERATOR_APPROVED_OUTPUT_DIR>>`.
No git reset.
No production rollback.
No process termination.
No worker termination.
No external-state mutation.

## STOP Rules
STOP immediately if:
- the approval token is missing or invalid
- the output directory is ambiguous
- any forbidden path would be touched
- any dangerous boolean would become true
- any non-approved file would be written
- any runtime, validator, or other repo file would be changed
- any API, network, socket, credential, secret, environment, deployment, production, or worker action is requested

## Verification
After writing the artifact:
- confirm the JSON parses
- confirm the output path is correct
- confirm the digest is stable
- confirm all safety booleans remain false
- confirm no repo files changed

## Report Back
Report:
- the output directory used
- the artifact path written
- whether the JSON parsed
- whether the safety booleans remained false
- whether the candidate stayed local, deterministic, reversible, supervised, and tiny

## Final Position
This prompt is the next step only.
It is not v4.0 execution.
