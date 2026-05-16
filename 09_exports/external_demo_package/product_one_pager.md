# Product One-Pager — The Agent Command Center

## Title
**The Agent Command Center**

## Subtitle
Safety-first request control layer for agentic workflows.

## The Problem
As agentic systems move from chat into production tasks, they need a structured way to handle requests. Automating actions without visibility or control gates is highly risky and difficult to audit.

## The Solution
An authenticated workspace that separates request intake and review from actual execution. Operators can inspect request details, view activity feeds, and add lifecycle notes while dangerous mutations remain blocked until later reviewed phases.

## Current Capabilities
- **Authenticated Reads:** Users see only their own requests via RLS.
- **Controlled Creation:** Specific, validated write paths for requests and events.
- **Activity Feed:** Unified view of request history and operator notes.
- **Safe Error Handling:** No internal infrastructure details leaked to clients.
- **Zero-Persistence:** Tokens are handled in memory only.

## What is Blocked (By Design)
- Approvals, Execution, and Automation.
- Request Update and Delete.
- Environment mutation and database migrations from the client.

## Next Milestones
1. Persistent frontend sessions (without token storage).
2. Controlled approval preview.
3. Execution simulation layer.
