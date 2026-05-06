# Agent Command Center Scope Drift Response Protocol v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- This is a non-runtime scope drift response protocol.
- This document does not modify runtime behavior.
- This document does not create v4.8.
- This document does not authorize runtime behavior.

## Purpose
Define how to identify and respond to scope drift during bounded documentation and governance tasks.

- this is a protocol only
- it does not auto-recover drift
- it does not modify files
- it does not grant permissions
- it does not activate workers
- it does not authorize v4.8

## Scope Drift Principle
- scope drift is a failure of task boundaries
- scope drift must be identified and reported immediately
- builder agents must not fix scope drift without operator instruction
- drift registers are for operator visibility only
- operator controls the response to drift

## Scope Drift Categories

- **extra file creation**
  - definition: Files exist not in the approved list.
  - severity: Severity 1
  - expected builder response: Stop, report extra files.
  - commit allowed: No.
  - operator review required: Yes.

- **existing doc modification**
  - definition: Edits to unapproved existing documents.
  - severity: Severity 2
  - expected builder response: Stop, report changes.
  - commit allowed: No.
  - operator review required: Yes.

- **runtime file modification**
  - definition: Modification of `10_runtime/`.
  - severity: Severity 5
  - expected builder response: Stop, report violation.
  - commit allowed: No.
  - operator review required: Yes.

- **validator modification**
  - definition: Modification of validation scripts.
  - severity: Severity 4
  - expected builder response: Stop, report violation.
  - commit allowed: No.
  - operator review required: Yes.

- **release lock modification**
  - definition: Modification of `station_chief_release_lock.py`.
  - severity: Severity 5
  - expected builder response: Stop, report violation.
  - commit allowed: No.
  - operator review required: Yes.

- **v4.8 creation**
  - definition: Generation of v4.8 runtime layer.
  - severity: Severity 7
  - expected builder response: Stop, report violation.
  - commit allowed: No.
  - operator review required: Yes.

- **runtime report creation**
  - definition: Creating non-requested runtime reports.
  - severity: Severity 3
  - expected builder response: Stop, report violation.
  - commit allowed: No.
  - operator review required: Yes.

- **protected export modification**
  - definition: Changing seed/org/master files.
  - severity: Severity 4
  - expected builder response: Stop, report violation.
  - commit allowed: No.
  - operator review required: Yes.

- **Devinization overlay modification**
  - definition: Changing overlay files.
  - severity: Severity 4
  - expected builder response: Stop, report violation.
  - commit allowed: No.
  - operator review required: Yes.

- **ownership metadata modification**
  - definition: Changing ownership definitions.
  - severity: Severity 4
  - expected builder response: Stop, report violation.
  - commit allowed: No.
  - operator review required: Yes.

- **generated cache commit**
  - definition: Committing `__pycache__` or other caches.
  - severity: Severity 0
  - expected builder response: Stop, report cache.
  - commit allowed: No.
  - operator review required: No.

- **API/network use**
  - definition: Network access or API calls.
  - severity: Severity 8
  - expected builder response: Stop, report violation.
  - commit allowed: No.
  - operator review required: Yes.

- **credential/secret touch**
  - definition: Reading secrets/credentials.
  - severity: Severity 9
  - expected builder response: Stop, report violation.
  - commit allowed: No.
  - operator review required: Yes.

- **deployment action**
  - definition: Initiating deployment logic.
  - severity: Severity 9
  - expected builder response: Stop, report violation.
  - commit allowed: No.
  - operator review required: Yes.

- **production action**
  - definition: Mutating production state.
  - severity: Severity 10
  - expected builder response: Stop, report violation.
  - commit allowed: No.
  - operator review required: Yes.

- **builder next-task suggestion**
  - definition: Builder suggesting work order.
  - severity: Severity 0
  - expected builder response: Stop, report.
  - commit allowed: No.
  - operator review required: Yes.

- **builder roadmap commentary**
  - definition: Builder discussing roadmap.
  - severity: Severity 0
  - expected builder response: Stop, report.
  - commit allowed: No.
  - operator review required: Yes.

- **optional file creation**
  - definition: Creating files not in task.
  - severity: Severity 1
  - expected builder response: Stop, report.
  - commit allowed: No.
  - operator review required: Yes.

## Scope Drift Severity Scale

- Severity 0 — Wording drift
- Severity 1 — Extra file issue
- Severity 2 — Existing planning doc modified
- Severity 3 — Runtime-adjacent issue
- Severity 4 — Protected non-runtime export touched
- Severity 5 — Validator/Lock issue
- Severity 6 — Worker/Task execution issue
- Severity 7 — v4.8 creation
- Severity 8 — API/Network issue
- Severity 9 — Credential/Deployment issue
- Severity 10 — Production/Workforce activation issue

## Scope Drift Response Table

| Drift Type | Severity | Stop Required | Commit Allowed | Push Allowed | Operator Review Required |
|---|---|---|---|---|---|
| extra file creation | Severity 1 | Yes | No | No | Yes |
| existing doc modification | Severity 2 | Yes | No | No | Yes |
| runtime file modification | Severity 5 | Yes | No | No | Yes |
| validator modification | Severity 4 | Yes | No | No | Yes |
| release lock modification | Severity 5 | Yes | No | No | Yes |
| v4.8 creation | Severity 7 | Yes | No | No | Yes |
| runtime report creation | Severity 3 | Yes | No | No | Yes |
| protected export modification | Severity 4 | Yes | No | No | Yes |
| Devinization overlay modification | Severity 4 | Yes | No | No | Yes |
| ownership metadata modification | Severity 4 | Yes | No | No | Yes |
| generated cache commit | Severity 0 | Yes | No | No | No |
| API/network use | Severity 8 | Yes | No | No | Yes |
| credential/secret touch | Severity 9 | Yes | No | No | Yes |
| deployment action | Severity 9 | Yes | No | No | Yes |
| production action | Severity 10 | Yes | No | No | Yes |
| builder next-task suggestion | Severity 0 | Yes | No | No | Yes |
| builder roadmap commentary | Severity 0 | Yes | No | No | Yes |
| optional file creation | Severity 1 | Yes | No | No | Yes |

## Scope Drift Report Template
Scope drift detected:
Drift type:
Severity:
Unexpected files:
Forbidden paths:
Runtime files touched:
Validators touched:
Release locks touched:
v4.8 files detected:
Protected exports touched:
Generated caches:
APIs/network involved:
Credentials/secrets involved:
Commit created:
Push performed:
Required operator decision:
Notes:

## Non-Drift Examples
- creating exact listed files
- committing exact listed files
- running git status
- running git diff --name-only
- reporting exact confirmations
- creating planning-only documentation
- creating a bundle with exact file count

## Drift Prevention Rules
- list exact files before work begins
- list forbidden paths before work begins
- avoid broad git add
- avoid editing existing docs unless requested
- avoid generated caches
- avoid runtime paths during documentation
- stop on unexpected files
- report only requested confirmations

## Runtime Authorization Boundary
- this protocol is not runtime authorization
- scope drift reporting does not grant permissions
- scope drift protocol does not create validators
- scope drift protocol does not create workers
- scope drift protocol does not create v4.8
- future approval still requires explicit operator instruction

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
