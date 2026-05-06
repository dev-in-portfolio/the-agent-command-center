# Station Chief v4.0 Operator Playbook v0.1

## Purpose
This playbook explains how the human operator should manage the first tiny real-world supervised execution candidate.

## Operator Role
The operator is responsible for:
- approving or denying the candidate
- confirming scope
- confirming output directory
- confirming forbidden paths
- confirming no credentials, secrets, environment, API, network, deployment, production, or workforce activation
- reviewing output
- deciding whether cleanup is required
- stopping the process if anything drifts

## Before Running v4.0
Checklist:
- v3.9 landed
- v3.9 runtime hardening passed
- non-runtime readiness docs created
- v4.0 prompt reviewed
- output directory chosen
- approval token chosen
- cleanup policy chosen
- forbidden paths confirmed
- expected output artifact confirmed

## Approved First Candidate Shape
The first candidate should be:
- one local proof artifact
- one explicit output directory
- deterministic content
- reversible or cleanable
- no external effects
- no production effects
- no worker activation

## Operator Approval Record
The operator approval record must include:
- operator name
- approval timestamp or deterministic placeholder
- candidate label
- output directory
- explicit approval token
- forbidden operations
- expected artifact
- cleanup rule
- verification rule

## STOP Conditions
STOP if:
- unexpected files appear in git status
- any forbidden path changes
- any runtime creates v4.0 files before approval
- any network/API/socket/credential/secret/environment operation is requested
- any deployment operation is requested
- any production operation is requested
- any worker activation is requested
- any command tries to broaden scope
- any validator fails and the proposed fix broadens scope
- any generated directory is accidentally staged
- any dashboard/org/master export is modified
- any Devinization overlay is modified
- any ownership metadata is modified
- any approval token is treated as blanket permission

## Review After Candidate
After candidate runs, operator must verify:
- only expected file was written
- output directory is correct
- JSON parses
- safety booleans remain false
- no forbidden files changed
- git status is clean except expected files, if any
- no generated directories were staged
- no runtime version advanced unexpectedly
- no v4.1 or later work started

## Cleanup
Cleanup is allowed only inside the approved output directory.
No git reset.
No production rollback.
No process termination.
No worker termination.
No external cleanup.

## Escalation
Escalate to human review if:
- any validator fails
- any file scope is unexpected
- any artifact contains a dangerous authorization true
- any command attempts API, network, socket, credential, secret, environment, deployment, production, or worker activation access

## Operator Summary
The operator’s job is not to make v4.0 impressive.
The operator’s job is to make v4.0 boring, tiny, reversible, and provably contained.
