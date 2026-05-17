# MVP-38 Demo Timing & Talking Points

## Timing Estimates

| Section | Duration | Cumulative | Notes |
|---------|----------|------------|-------|
| Landing | 0:30 | 0:30 | CTA click, brief narrative setup |
| Auth | 0:45 | 1:15 | Magic link flow (with simulated wait) |
| Dashboard | 1:00 | 2:15 | Metric overview, session launch |
| Feature A | 1:30 | 3:45 | Form fill, validation, submission |
| Feature B | 1:30 | 5:15 | Processing, preview, export |
| Review | 1:00 | 6:15 | History, undo flow |
| Conversion | 1:15 | 7:30 | Feature comparison, trial start |
| **Total** | **7:30** | | |

**Buffer:** 30 seconds per section recommended for live demos
**Live total with buffer:** 11:00 — 12:00

## Talking Points by Section

### Landing
- "MVP-38 solves the core problem of X by introducing Y"
- "Notice the single clear CTA — zero friction entry point"
- "This layout was optimized based on previous session heatmaps"

### Auth
- "One-click magic link — no password overhead"
- "Average auth completion under 15 seconds in beta"
- "Session token persists for 24 hours with refresh"

### Dashboard
- "Personalized metrics surface what matters most"
- "Session launch is one click from any view"
- "Widgets are configurable per user preference"

### Feature A
- "Inline validation catches errors before submission"
- "Parameters are auto-suggested based on session context"
- "Submission triggers the backend pipeline immediately"

### Feature B
- "Output preview updates in real time"
- "Export supports PDF, CSV, and JSON formats"
- "Preview quality matches final export exactly"

### Review
- "Full session history with undo capability"
- "Undo is instantaneous — no page reload required"
- "History persists across sessions for audit"

### Conversion
- "Feature comparison is personalized to actual usage"
- "Trial starts immediately with no credit card required"
- "Upgrade unlocks premium features visible in dashboard"

## Click Path Notes

- Pre-warm the demo environment before starting to avoid cold-start delays
- Keep the magic link email tab open to avoid navigation delays during auth
- Use realistic but non-sensitive test data for form fields
- If an export dialog does not appear within 3 seconds, proceed to review anyway
- The undo confirmation dialog auto-dismisses after 5 seconds
- Have a backup session pre-loaded in case of unexpected state issues
