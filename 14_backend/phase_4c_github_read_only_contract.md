# Phase 4C: GitHub Read-Only Contract

## Goal
Define the strict boundary for future read-only interactions with the GitHub API.

## Allowed Data Categories
- Repository metadata (stars, description, primary language).
- Branch names and last-commit timestamps.
- Pull request titles, numbers, states, and authors.
- Check run results (CI status).
- Workflow run status (Success/Failure).

## Forbidden Actions
- **No Writing**: Creating or updating files is strictly forbidden.
- **No Branching**: Creating or deleting branches is forbidden.
- **No PR Creation**: Opening or closing pull requests is forbidden.
- **No Merging**: Triggering merges via API is forbidden.
- **No Commenting**: Posting comments or labels is forbidden.
- **No Dispatching**: Triggering `workflow_dispatch` events is forbidden.

## Implementation Rules
- GitHub tokens must **never** be exposed to the browser.
- All calls must be performed server-side by Netlify Functions.
- Every call must be logged in the immutable audit ledger.
- API tokens must have the minimum possible read-only scope.

---
*Note: This is a planning document only. No functional implementation is included in this build.*
