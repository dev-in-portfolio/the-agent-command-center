# Demo Q&A — The Agent Command Center

### Q: Is this an autonomous agent execution system?
**A:** Not yet. It is intentionally designed as a **safety-first request control layer**. We focus on request intake, review, and activity tracking. Approval and execution are blocked until later reviewed phases to ensure human-in-the-loop safety.

### Q: Does it expose secrets in the browser?
**A:** No. All database calls are proxied through Netlify Functions. The browser only uses the user's bearer token. Private keys like the Supabase Service Role remain secure in the server environment.

### Q: Why is there no "Execute" button?
**A:** This is a design decision. We prioritize the integrity of the request review process. Execution will be added in a controlled manner in future milestones once the review layer is fully verified.

### Q: Is the live test complete?
**A:** The manual live test harness is ready. The system is verified to support authenticated reads and controlled creation. Full end-to-end live results with real tokens are gated for final review.

### Q: What is intentionally not enabled?
**A:** Request updates/deletes, approvals, execution, automation, and client-side database schema changes.
