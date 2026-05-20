# Guided Demo Walkthrough Script — 10-15 Minute Session

## Opening Framing (1 min)
"This is The Agent Command Center — a read-only production-visible dashboard. It documents the readiness architecture for a controlled command center. Eight readiness layers are complete and production-verified through MVP-50. Runtime activation has not started. What you will see is a proof of architecture, not a live automation system."

## Navigation Path

### Welcome Section (30s)
- URL: https://the-agent-command-center-dashboard.netlify.app/
- "You see the welcome banner with the project tagline. This confirms we are at the correct live site."

### Current Status (1 min)
- Scroll to Current Status section
- "The Latest production verified MVP badge shows MVP-50 in green. This means MVP-50 has been verified as correct on the live production site."
- Point out "Latest verified milestone: MVP-50" in the Production State card
- "The safety posture reads: NOT_READY_FOR_REAL_AUTOMATION. This is by design."

### What the hell am I looking at? (1 min)
- Scroll to this section
- "This explains the system. Read-only dashboard. Readiness layers 43-50 are complete. Runtime is disabled. The dashboard does nothing on its own."

### Roadmap — Readiness Layers (3 min)
- Scroll through the collapsible sections
- For each, say: "MVP-[N] — [Name]. Production verified. Schema designed. Proves [key capability]. Does not enable runtime execution."
- Mention MVP-50 specifically: "Monitoring / Rollback / Incident Console — the readiness layer for observability and incident response. Schema-ready. Not executing."

### Archive (1 min)
- "The archive section shows all prior milestones for reference."

### Developer View (1 min)
- "The developer view shows validation checklists and technical details."

## Safety Highlight (1 min)
- Explicitly point to the NOT_READY_FOR_REAL_AUTOMATION badge
- "This marker is checked by our validators. If anyone changes it to claim readiness is complete, the validators will fail."
- "No runtime features are enabled. No endpoints. No execution. This is a demo/review artifact."

## What Not to Claim
- Do not claim the system executes commands
- Do not claim it writes to databases
- Do not claim it automates operations
- Do not claim it is production-ready for runtime
- Do not claim runtime activation has begun

## Closing Ask (1 min)
"Please review the package materials. Use the reviewer notes template to capture feedback. The next step after review is either: (a) stakeholder approval to begin runtime activation planning, or (b) further refinement of specific readiness layers."
