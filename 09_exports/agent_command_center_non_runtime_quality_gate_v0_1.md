# Agent Command Center Non-Runtime Quality Gate v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- This is a non-runtime quality gate document.
- This document does not modify runtime behavior.
- This document does not create v4.8.
- This document does not authorize runtime behavior.

## Purpose
Define documentation-only acceptance checks for non-runtime bundles.

- this is a quality gate only
- it does not enforce checks in code
- it does not modify files
- it does not grant permissions
- it does not activate workers
- it does not authorize v4.8

## Quality Gate Principle
- quality gates verify non-runtime compliance
- quality gates do not check runtime performance
- quality gates do not authorize execution
- quality gates do not permit scope drift
- quality gates do not provide runtime security guarantees
- quality gates require explicit operator instruction to build/maintain

## Non-Runtime Quality Checks
- exact expected file count
- exact expected file paths
- no optional files
- no existing document modifications unless allowed
- required sections present
- planning-only language present
- runtime authorization boundary present
- no recommended next step section
- no builder-selected task language
- Station Chief parking language present
- v4.8 denial language present
- no runtime files changed
- no validators changed
- no release locks changed
- no protected exports changed
- no overlays changed
- no ownership metadata changed

## Quality Gate Table

| Check | Expected Result | Failure Meaning | Required Response |
|---|---|---|---|
| exact file count | Match task | Scope drift | Stop |
| exact file paths | Match task | Forbidden path | Stop |
| no optional files | True | Scope expansion | Stop |
| no existing doc edits | None | Unrequested edit | Stop |
| required sections present | All present | Governance gap | Stop |
| planning-only language | Included | Runtime ambiguity | Stop |
| runtime authorization boundary | Included | Governance gap | Stop |
| no recommended next steps | True | Builder freelancing | Stop |
| no builder-selected task | True | Builder freelancing | Stop |
| Station Chief parking language | Included | Governance gap | Stop |
| v4.8 denial language | Included | Governance gap | Stop |
| no runtime files | None modified | Runtime modification | Stop |
| no validators | None modified | Validator modification | Stop |
| no release locks | None modified | Lock modification | Stop |
| no protected exports | None modified | Export mutation | Stop |
| no overlays | None modified | Overlay mutation | Stop |
| no ownership metadata | None modified | Ownership mutation | Stop |

## Documentation Language Checks
Documents must include:
- current context
- purpose
- principle section
- denied behavior
- runtime authorization boundary
- final note
- no recommended next step section
- no roadmap selection
- no runtime authorization
- no v4.8 authorization

## File-Scope Checks
- only listed files may be staged
- unexpected changed files trigger stop
- forbidden paths trigger stop
- documentation-only tasks must not touch `10_runtime/`
- documentation-only tasks must not touch `scripts/validate_*`

## Report-Back Checks
- files created
- commit hash
- no runtime files changed
- no validators changed
- no release locks changed
- v4.8 not created
- planning-only confirmation
- no next task selected or suggested
- exact expected file count created
- no existing planning docs modified

## Quality Gate Failure Response
- stop
- report exact failure
- do not stage
- do not commit
- do not push
- do not broaden scope
- do not auto-fix unless explicitly assigned
- do not recommend next task

## Runtime Authorization Boundary
- this quality gate is not runtime authorization
- quality gate compliance does not grant permissions
- quality gate compliance does not create validators
- quality gate compliance does not create workers
- quality gate compliance does not create v4.8
- future approval still requires explicit operator instruction

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
