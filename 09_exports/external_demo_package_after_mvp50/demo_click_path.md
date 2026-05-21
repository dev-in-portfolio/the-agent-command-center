# Demo Click Path — Live Site Navigation

## Starting Point
https://the-agent-command-center.netlify.app/

## Welcome Section
- Show the welcome banner "The Agent Command Center"
- Say: "This confirms we are on the live production dashboard."

## Current Status Section
- Show the "Latest production verified MVP" card with badge "MVP-50"
- Show the "Latest Milestone" card with badge "OPERATIONAL"
- Show the "Production State" card listing:
  - Latest verified milestone: MVP-50
  - Current production branch: master
  - Current production role: read-only review dashboard
  - Next milestone: 51 (In Progress)
- Show the "Current safety posture" card with "NOT_READY_FOR_REAL_AUTOMATION"

## What the hell am I looking at? Section
- Read the explanatory text aloud
- Emphasize: read-only, no automation, runtime disabled

## Latest Verified MVP Section
- Point to the MVP-50 entry in the production verification list

## Safety Posture Section
- Point to explicit disabled capabilities
- Say: "Nothing here can execute, write, automate, alert, or deploy."

## Roadmap Section
- Expand MVP-43 through MVP-50 one by one
- For MVP-50 (Monitoring / Rollback / Incident Console), show the monitoring signals, health schema, incident record schema
- Mention: "Schema-ready, not executing"

## Archive Section
- Briefly scroll past — "Earlier milestones for reference"

## Developer View Section
- Show the copy-validation-checklist button (do not click it unless asked)
- Mention: "Technical reviewers can use this for detailed validation"

## What to Skip Unless Asked
- Individual validation checklist details
- Archive content beyond scrolling past
- Dashboard_data.json or status_snapshot.json URLs
