# Screen-Share Runbook

## Browser Setup
- Use incognito/private browsing mode
- Clear browser cache
- Set browser to full-screen (F11)
- Prepare a second monitor or window with presenter notes

## Cache-Bust Check
Before starting, verify the live site is serving current content:
https://the-agent-command-center.netlify.app/?cache_bust=stakeholder_demo

Expected: Latest production verified MVP: MVP-50 badge

## Live Site URL
https://the-agent-command-center.netlify.app/

## Exact Click Path
1. Open URL
2. Point to Welcome banner
3. Scroll down to Current Status section
4. Point to Latest production verified MVP badge (MVP-50)
5. Point to Production State card
6. Point to NOT_READY_FOR_REAL_AUTOMATION badge
7. Scroll to What the hell am I looking at? section
8. Scroll to Roadmap section
9. Expand MVP-50 section
10. Scroll through Archive
11. Scroll to Developer View

## Timing Guide
- Welcome + Status: 1 minute
- What the hell am I looking at?: 1 minute
- Roadmap (8 layers): 3-4 minutes
- Safety posture: 1 minute
- Archive + Developer View: 1 minute
- Q&A: remaining time

## Fallback If Live Site Looks Stale
1. Add ?cache_bust=[timestamp] to the URL
2. If still stale, open in a different browser
3. If still stale, use the local dist/index.html as a backup
4. Note the issue and investigate after the demo

## What to Show
- Welcome banner
- Latest production verified MVP badge
- Production State card
- Safety posture badge
- All 8 readiness layers (expand at least MVP-50)
- NOT_READY_FOR_REAL_AUTOMATION marker

## What to Skip Unless Asked
- Individual validation checklist details
- Archive content detail
- JSON data files (dashboard_data.json, status_snapshot.json)
- Source code and repository structure

## What to Say While Clicking
"As you can see, the dashboard shows the current readiness state clearly. Each badge and marker is checked by automated validators. I encourage you to visit the URL yourself after this session."
