# auto-self-improve-2 Lab Doctrine

## Internal Lab Identity
- **ID:** auto-self-improve-2
- **Repo Role:** contained_sandbox_self_improvement_lab
- **Target Repo:** dev-in-portfolio/agent-command-center-3

## Core Purpose
The auto-self-improve-2 lab is established for contained self-improvement WITH sandbox self-authorization. It is an experimental environment for testing mutations within a restricted boundary.

## Authorization Model
- **Sandbox Self-Authorization:** ALLOWED (for sandbox artifacts only)
- **Sandbox Mutation:** ALLOWED (within `/tmp/auto_self_improve_2_sandbox/`)
- **Official Repo Mutation:** FORBIDDEN
- **Self-Promotion:** FORBIDDEN
- **Operator Decision Required:** YES (for any official promotion)

## Official Repo Protection
The official repository (`dev-in-portfolio/agent-command-center`) and the propose-only lab (`dev-in-portfolio/agent-command-center-2`) are strictly protected. This lab layer is prohibited from modifying, promoting, or touching any lineage outside its own repository boundary.

## Allowed Actions
- Propose improvement candidates for sandbox testing.
- Evaluate candidates against sandbox safety and utility benchmarks.
- Self-authorize sandbox mutations for low/medium risk candidates.
- Create sandbox candidate patches (metadata-only simulations).
- Write controlled sandbox artifacts to the temporary workspace.
- Run sandbox metadata tests to verify containment.
- Create promotion barriers to prevent accidental self-promotion.

## Denied Actions
- Mutate the official repository or any repo other than itself.
- Promote lab results to the official repository automatically.
- Deploy.
- Use secrets or credentials.
- Call the network or start unauthorized subprocesses.
- Bypassing existing safety validators for official status.

## Sandbox Boundary
All authorized mutations and artifacts must be contained within:
`/tmp/auto_self_improve_2_sandbox/`
Any attempt to write outside this directory during self-improvement execution is a violation of the lab doctrine.
