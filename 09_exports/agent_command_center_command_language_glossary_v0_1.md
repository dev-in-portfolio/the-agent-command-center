# Agent Command Center Command Language Glossary v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- This is a non-runtime command language glossary.
- This document does not modify runtime behavior.
- This document does not create v4.8.
- This document does not authorize runtime behavior.

## Purpose
This glossary defines operator command language so builder agents interpret commands narrowly and do not infer roadmap direction.

- this is a glossary only
- it does not create command execution logic
- it does not create runtime behavior
- it does not grant permissions
- it does not activate workers
- it does not authorize v4.8

## Command Language Principle
- operator command wording controls scope
- builder agents must interpret commands narrowly
- builder agents must not infer extra tasks
- builder agents must not convert casual language into runtime authorization
- builder agents must not convert documentation commands into runtime work
- builder agents must not treat check commands as fix commands
- builder agents must not treat prompt-writing commands as execution commands

## Command Types

- **check command**: Verification of system state.
- **write prompt command**: Creation of prompt records.
- **run prompt command**: Execution of a prompt (Reserved for high-model).
- **fix command**: Repairing logic issues (Requires explicit approval).
- **documentation creation command**: Drafting governance/planning docs.
- **documentation bundle command**: Drafting a group of related docs.
- **status command**: Reporting report-back.
- **handoff command**: Finalizing a task report.
- **pause command**: Immediate work stop.
- **park command**: Confirming parking state.
- **resume command**: Resuming Station Chief runtime (Requires explicit operator trigger).
- **runtime build command**: Building a runtime layer (Requires high-model).
- **validator command**: Running validation chain.
- **scope correction command**: Adjusting scope boundaries.
- **stop command**: Immediate cessation of activity.

## Command Interpretation Table

| Operator Command | Narrow Meaning | Builder May Do | Builder Must Not Do | Runtime Effect | Requires Explicit Approval |
|---|---|---|---|---|---|
| check please | Verify repo state | Check status | Modify files | None | No |
| please write prompt | Draft text only | Generate content | Execute prompt | None | No |
| run prompt | Execute tool-use simulation | Execute sandbox | Modify runtime | None | Yes |
| fix [issue] | Repair specific error | Apply target fix | Broad refactor | Runtime changes | Yes |
| create doc | Draft new doc | Write markdown | Add next steps | None | Yes |
| create bundle | Draft bundle | Create listed files | Add extra files | None | Yes |
| handoff | Report status | Format report | Add roadmap | None | No |
| pause | Stop task | Cease action | Continue work | None | No |
| park | Confirm v4.7.0 | Log state | Edit locks | None | No |
| resume | Resume runtime ladder | Build v4.8 | Automate resume | Ladder cont | Yes |
| validate | Run validation chain | Run tests | Alter validator | None | No |
| stop | Immediate stop | Cease all activity | Explain | None | No |

## Ambiguous Command Handling
- ambiguity must not expand scope
- ambiguity must not authorize runtime work
- ambiguity must not authorize v4.8
- ambiguity must not authorize APIs, network, deployment, production, workers, tasks, queues, or routing
- if ambiguity could cause unauthorized changes, builder must stop and report the ambiguity
- builder may not guess a higher-risk interpretation

## “Check Please” Meaning
- verify visible current repo state
- report landed/not landed status
- confirm whether expected files exist in latest commit if visible
- confirm Station Chief parking state if relevant
- do not modify files
- do not run fixes
- do not create commits
- do not choose next tasks

## “Please Write Prompt” Meaning
- draft an operator-controlled prompt
- do not execute it
- do not assume it has been approved for running
- do not choose the next task unless the operator explicitly names the task
- do not create files in the repo
- do not modify runtime
- do not modify validators

## “Fix” Meaning
Requires:
- explicit target
- explicit file scope
- explicit allowed behavior
- explicit validation
- explicit commit/push instruction if a repo change is expected

“Fix” does not automatically authorize:
- v4.8
- broad refactors
- runtime ladder continuation
- validator redesign
- API/network behavior
- deployment
- production execution

## Parking and Resume Language

- **parked**: Station Chief version locked at v4.7.0. Authorization: No.
- **leave Station Chief alone**: Maintenance of parked state. Authorization: No.
- **resume Station Chief**: Requesting resumption. Requires explicit assignment. Authorization: Yes.
- **build v4.8**: Runtime ladder continuation. Requires explicit assignment. Authorization: Yes.
- **high-model reserved**: Pending top-tier capability. Authorization: No.
- **low-model safe**: Standard documentation work. Authorization: No.

## Always-Denied Interpretations

- interpreting documentation work as runtime work
- interpreting status checks as fix authorization
- interpreting prompt writing as prompt execution
- interpreting “next” as roadmap permission unless task is named
- interpreting high-model availability as runtime authorization
- interpreting v4.8 discussion as v4.8 approval
- interpreting glossary/index work as worker activation
- interpreting queue/routing language as live routing approval

## Runtime Authorization Boundary
- this glossary is not runtime authorization
- command definitions do not create runtime behavior
- command definitions do not create validators
- command definitions do not create workers
- command definitions do not create v4.8
- future approval still requires explicit operator instruction

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
