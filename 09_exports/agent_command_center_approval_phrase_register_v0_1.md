# Agent Command Center Approval Phrase Register v0.1

## Current Context
- Station Chief runtime is parked at v4.7.0.
- This is a non-runtime approval phrase register.
- This document does not modify runtime behavior.
- This document does not create v4.8.
- This document does not authorize runtime behavior.

## Purpose
This register distinguishes casual discussion from explicit operator approval.

- this is a register only
- it does not create approval tokens
- it does not enforce approval in code
- it does not resume Station Chief
- it does not grant runtime permissions
- it does not authorize v4.8

## Approval Phrase Principle
- approval must be explicit
- approval must name the task
- approval must name the file scope or runtime layer when applicable
- approval for documentation does not authorize runtime
- approval for planning does not authorize execution
- approval for preview does not authorize live behavior
- approval for high-model use does not authorize runtime work by itself

## Explicit Approval Examples

- **create this exact documentation file**: Authorizes: Specified file creation. Does not authorize: Runtime changes. Requires: File path specificity.
- **create exactly these listed files**: Authorizes: Listed file creation. Does not authorize: Extra files. Requires: List provided.
- **build Station Chief Runtime v4.8**: Authorizes: Runtime build. Does not authorize: Unapproved dependencies. Requires: Version explicit.
- **modify this validator file**: Authorizes: Targeted validator edit. Does not authorize: Logic bypass. Requires: File path.
- **fix this specific runtime error**: Authorizes: Runtime fix. Does not authorize: Refactor. Requires: Issue description.
- **resume Station Chief ladder with v4.8**: Authorizes: Ladder progression. Does not authorize: Workforce activation. Requires: Version explicit.
- **run this exact validation command**: Authorizes: Validation execution. Does not authorize: Logic change. Requires: Command explicit.
- **commit these exact files**: Authorizes: Repository update. Does not authorize: Unlisted files. Requires: List provided.
- **add documentation bundle**: Authorizes: Bundle creation. Does not authorize: Runtime modification. Requires: Specific bundle prompt.
- **approve safety boundary matrix**: Authorizes: Matrix persistence. Does not authorize: Runtime enforcement. Requires: Document name.

## Non-Approval Examples

- **what do you think**: Safe: Conversational. Does not authorize: System change. Builder: Provide opinion only.
- **what should we do**: Safe: Procedural inquiry. Does not authorize: Roadmap selection. Builder: Await explicit direction.
- **can we**: Safe: Capability check. Does not authorize: Permission grant. Builder: State capability status.
- **maybe later**: Safe: Delay. Does not authorize: Future work. Builder: Log note.
- **while we wait**: Safe: Contextual bridge. Does not authorize: Execution. Builder: Wait for operator.
- **easier tasks**: Safe: Planning categorization. Does not authorize: Next task. Builder: State planning backlog.
- **high-model is almost out**: Safe: Capability note. Does not authorize: Runtime work. Builder: Acknowledge capability.
- **let’s talk about**: Safe: Discussion. Does not authorize: Expansion. Builder: Maintain scope.
- **check please**: Safe: Verification. Does not authorize: Fixes. Builder: Report only.
- **please write prompt**: Safe: Drafting. Does not authorize: Execution. Builder: Write text only.
- **next**: Safe: Sequence reference. Does not authorize: Task selection. Builder: Await explicit assignment.
- **continue**: Safe: Resuming doc work. Does not authorize: Runtime execution. Builder: Maintain mode.
- **good enough**: Safe: Completion check. Does not authorize: Roadmap skip. Builder: Confirm completion.
- **looks good**: Safe: Review acknowledgment. Does not authorize: Merge. Builder: Await push instruction.

## Approval Scope Table

| Phrase Type | Example | Authorizes Documentation | Authorizes Runtime | Authorizes v4.8 | Authorizes APIs/Network | Authorizes Production | Builder Action |
|---|---|---|---|---|---|---|---|
| Explicit Task Assignment | "Create this file" | Yes | No | No | No | No | Execute |
| Explicit Build Instruction | "Build Station Chief v4.8" | Yes | Yes | Yes | No | No | Execute |
| Verification Request | "Check please" | Yes | No | No | No | No | Verify |
| Conversational Discussion | "What do you think" | No | No | No | No | No | Discuss |
| Roadmap Inquiry | "What should we do" | No | No | No | No | No | Await Direction |
| Capability Inquiry | "Can we run tools" | No | No | No | No | No | State Capability |
| Sequence Reference | "Next" | No | No | No | No | No | Await Task |
| Acknowledgment | "Looks good" | No | No | No | No | No | Await Direction |
| Prompt Drafting | "Please write prompt" | Yes | No | No | No | No | Draft Text |
| Fix Request | "Fix this bug" | No | Yes | No | No | No | Apply Fix |
| Validator Request | "Run validator" | No | Yes | No | No | No | Validate |
| Safety Review | "Review boundaries" | Yes | No | No | No | No | Review |
| Status Report | "Handoff status" | Yes | No | No | No | No | Report |
| Parking Check | "Are we parked" | Yes | No | No | No | No | Verify Parking |
| Mode Switch | "Low-model mode" | Yes | No | No | No | No | Switch Mode |
| Scope Correction | "Stop scope expansion" | Yes | No | No | No | No | Stop/Pause |
| Commit Request | "Commit these files" | Yes | No | No | No | No | Commit |
| Build Artifact Request | "Build runtime layer" | Yes | Yes | No | No | No | Build |
| Deployment Readiness | "Deployment readiness" | Yes | No | No | No | No | Review Readiness |
| Rollback Plan | "Rollback plan" | Yes | No | No | No | No | Plan |

## Approval Specificity Rules
- documentation approval must name files or document family
- runtime approval must name runtime layer or file scope
- validator approval must name validator scope
- v4.8 approval must explicitly say v4.8 or the full layer name
- API/network approval must explicitly name API/network scope
- deployment approval must explicitly name deployment target
- production approval must explicitly name production action
- broad enthusiasm is not approval
- general discussion is not approval

## Invalid Approval Inference
- previous similar tasks
- progress pressure
- model availability
- repeated “next prompt” requests
- status checks
- documentation landing
- high-level strategy discussion
- shorthand
- humor
- impatience
- urgency

## Runtime Authorization Boundary
- this register is not runtime authorization
- approval phrase examples do not grant permissions
- approval phrase examples do not create tokens
- approval phrase examples do not create validators
- approval phrase examples do not create v4.8
- future approval still requires explicit operator instruction

## Final Note
This document is planning/governance-only and should not be treated as runtime authorization.
