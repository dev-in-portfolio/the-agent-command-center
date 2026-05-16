# Reviewer Checklist

### Technical Reviewer
- [ ] Verify `netlify/functions/requests.js` hardening.
- [ ] Confirm RLS policies on the `requests` and `request_lifecycle_events` tables.
- [ ] Inspect the `safe_error.js` helper.
- [ ] Check `scripts/validate_...` for automated safety gates.

### Recruiter / Founder
- [ ] Load the production dashboard.
- [ ] Confirm visual status of all MVP phases.
- [ ] Review the "Safety Boundary" panels.
- [ ] Walk through the "Operator Workspace" narrative.
- [ ] Verify the "Next Milestones" alignment with product goals.
