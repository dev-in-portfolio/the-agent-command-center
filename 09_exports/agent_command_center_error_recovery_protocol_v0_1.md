# Agent Command Center Error Recovery Protocol v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- This is a non-runtime error recovery protocol.
- This document does not modify runtime behavior.
- This document does not create v4.8.
- This document does not authorize runtime behavior.

## Purpose
Define how builder agents should respond to blocked tasks, dirty repo state, unexpected files, scope drift, validation failures, and ambiguity.

- this is a protocol only
- it does not auto-recover errors
- it does not modify files
- it does not grant permissions
- it does not activate workers
- it does not authorize v4.8

## Error Recovery Principle
- builder agents must not attempt recovery unless explicitly assigned
- builder agents must stop immediately on scope drift
- builder agents must preserve dirty state for operator review
- builder agents must report facts, not opinions or guesses
- error recovery does not authorize runtime ladder continuation

## Error Categories

- **dirty working tree**
  - definition: Uncommitted changes present.
  - likely cause: Prior work left state.
  - required builder response: Stop, report state, await instruction.
  - commit allowed: No.
  - operator review required: Yes.

- **unexpected changed file**
  - definition: Git diff includes unauthorized files.
  - likely cause: Scope expansion or accidental edit.
  - required builder response: Stop, report unexpected files, await instruction.
  - commit allowed: No.
  - operator review required: Yes.

- **forbidden path touched**
  - definition: Modification of protected areas.
  - likely cause: Misinterpreted path or intent.
  - required builder response: Stop, report violation.
  - commit allowed: No.
  - operator review required: Yes.

- **runtime drift**
  - definition: Runtime/validator file change.
  - likely cause: Accidental runtime edit.
  - required builder response: Stop, report runtime drift.
  - commit allowed: No.
  - operator review required: Yes.

- **validator drift**
  - definition: Validator file edit.
  - likely cause: Accidental edit.
  - required builder response: Stop, report validator drift.
  - commit allowed: No.
  - operator review required: Yes.

- **release lock drift**
  - definition: Lock file edit.
  - likely cause: Accidental edit.
  - required builder response: Stop, report lock drift.
  - commit allowed: No.
  - operator review required: Yes.

- **v4.8 file appeared**
  - definition: v4.8 artifact generated.
  - likely cause: Prohibited v4.8 automation.
  - required builder response: Stop, report violation.
  - commit allowed: No.
  - operator review required: Yes.

- **generated cache appeared**
  - definition: `__pycache__` commits.
  - likely cause: Failure to clean.
  - required builder response: Stop, report.
  - commit allowed: No.
  - operator review required: No.

- **target file already exists**
  - definition: Overwrite attempt without approval.
  - likely cause: Re-running prompt.
  - required builder response: Stop, report conflict.
  - commit allowed: No.
  - operator review required: Yes.

- **validation command failed**
  - definition: Validator returned non-zero code.
  - likely cause: Bug or system drift.
  - required builder response: Stop, report failure.
  - commit allowed: No.
  - operator review required: Yes.

- **commit failed**
  - definition: Git commit returned non-zero.
  - likely cause: Repo state/locks.
  - required builder response: Stop, report failure.
  - commit allowed: No.
  - operator review required: Yes.

- **push failed**
  - definition: Git push returned non-zero.
  - likely cause: Network/auth.
  - required builder response: Stop, report failure.
  - commit allowed: No.
  - operator review required: Yes.

- **ambiguous instruction**
  - definition: Command permits scope expansion.
  - likely cause: Underspecified instruction.
  - required builder response: Stop, report ambiguity.
  - commit allowed: No.
  - operator review required: Yes.

- **credential/secret encountered**
  - definition: Secrets found in logs/files.
  - likely cause: Insecure handling.
  - required builder response: Stop, report violation.
  - commit allowed: No.
  - operator review required: Yes.

- **API/network requirement discovered**
  - definition: Task needs network/API.
  - likely cause: Misunderstanding task boundary.
  - required builder response: Stop, report requirement.
  - commit allowed: No.
  - operator review required: Yes.

- **deployment requirement discovered**
  - definition: Task needs deployment.
  - likely cause: Misunderstanding task boundary.
  - required builder response: Stop, report requirement.
  - commit allowed: No.
  - operator review required: Yes.

## Recovery Response Table

| Error Category | Severity | Builder Response | Commit Allowed | Push Allowed | Operator Review Required |
|---|---|---|---|---|---|
| dirty working tree | Severity 0 | STOP | No | No | Yes |
| unexpected changed file | Severity 1 | STOP | No | No | Yes |
| forbidden path touched | Severity 4 | STOP | No | No | Yes |
| runtime drift | Severity 3 | STOP | No | No | Yes |
| validator drift | Severity 4 | STOP | No | No | Yes |
| release lock drift | Severity 5 | STOP | No | No | Yes |
| v4.8 file appeared | Severity 7 | STOP | No | No | Yes |
| generated cache appeared | Severity 0 | STOP | No | No | Yes |
| target file exists | Severity 2 | STOP | No | No | Yes |
| validation failed | Severity 3 | STOP | No | No | Yes |
| commit failed | Severity 1 | STOP | No | No | Yes |
| push failed | Severity 1 | STOP | No | No | Yes |
| ambiguous instruction | Severity 0 | STOP | No | No | Yes |
| credential/secret | Severity 9 | STOP | No | No | Yes |
| API/network requirement | Severity 8 | STOP | No | No | Yes |
| deployment requirement | Severity 9 | STOP | No | No | Yes |

## Blocked State Report Template
Blocked state:
Reason:
Current branch:
Dirty files:
Unexpected files:
Forbidden paths:
Runtime files touched:
Validators touched:
Release locks touched:
v4.8 files detected:
Generated caches detected:
Credentials/secrets involved:
APIs/network involved:
Commit created:
Push performed:
Required operator decision:
Notes:

## Recovery Stop Rules
- do not stage files after a stop condition
- do not commit after a stop condition
- do not push after a stop condition
- do not auto-delete files
- do not auto-clean caches unless explicitly assigned
- do not rewrite scope
- do not substitute files
- do not continue with partial work unless explicitly assigned

## Safe Recovery Reporting
- allow exact facts only
- deny recommendations
- deny next-task suggestions
- deny roadmap commentary
- deny unrequested fix plans
- deny optional follow-ups

## Runtime Authorization Boundary
- this protocol is not runtime authorization
- error recovery does not create runtime behavior
- error recovery does not create validators
- error recovery does not create workers
- error recovery does not create v4.8
- future approval still requires explicit operator instruction

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
