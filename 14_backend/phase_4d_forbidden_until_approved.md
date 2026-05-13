# Phase 4D: Forbidden Capabilities until Approved

## Strictly Prohibited
The following capabilities are forbidden at the backend layer until a formal gate review approval is reached:

1. **Direct Execution**: No `child_process.exec` or equivalent calls.
2. **Git Mutation**: No `git push`, `git merge`, or branch creation from backend logic.
3. **Secret Exposure**: No reading of encrypted env vars without redaction middleware.
4. **API Mutation**: No POST/PUT calls to GitHub or Netlify management APIs.
5. **Database Mutation**: No writes to persistent storage.
6. **File Mutation**: No updating or deleting repository files.
7. **Autonomous Backgrounding**: No background agents or long-running tasks.

---
*Note: These prohibitions remain in force for the current build.*
