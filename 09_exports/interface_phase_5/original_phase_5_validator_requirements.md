# Original Phase 5 — Validator Requirements

## Status
PLANNING_ONLY

## Purpose
Define the validators that must exist and pass before any Phase 5 implementation can merge. These validators ensure that Phase 5 remains planning-only and does not accidentally enable any execution, mutation, or unauthorized behavior.

## Required Validators

### 1. Netlify Functions Validator
- No Netlify Functions modified unless explicitly authorized by a separate planning review
- Check: git diff --name-only against base branch
- File patterns: netlify/functions/**
- Pass condition: no modified files in this path

### 2. External Fetches Validator
- No external fetch targets beyond approved same-origin endpoints
- Approved targets: /api/health, /api/status, /api/backend-manifest, ./status_snapshot.json, ./phase4d_*.json
- Check: regex scan for fetch() calls in all JS files
- Pass condition: all fetch targets are in the approved list

### 3. Unauthorized Endpoint Validator
- No unauthorized same-origin endpoints
- Check: scan for /api/* endpoints not in the approved list
- Pass condition: no unauthorized endpoints found

### 4. Storage API Validator
- No storage APIs used
- Check: scan for localStorage, sessionStorage, IndexedDB
- Pass condition: none found

### 5. Cookies Validator
- No cookie usage
- Check: scan for document.cookie
- Pass condition: none found

### 6. Real-Time Transport Validator
- No WebSocket, EventSource, or sendBeacon usage
- Check: scan for WebSocket, EventSource, sendBeacon
- Pass condition: none found

### 7. Dynamic Code Validator
- No eval(), Function(), or dynamic import() usage
- Check: scan for eval(, Function(, import(
- Pass condition: none found

### 8. Deploy/Merge/Push/PR Controls Validator
- No enabled deploy, merge, push, or PR controls
- Check: scan for workflow_dispatch, merge_pull_request, create_pull_request, update_file, delete_file, netlify deploy
- Pass condition: none found

### 9. Command Execution Validator
- No command execution strings
- Check: scan for command execution patterns
- Pass condition: none found

### 10. GitHub Mutation Validator
- No GitHub mutation API calls
- Check: scan for GitHub API write patterns
- Pass condition: none found

### 11. Netlify Mutation Validator
- No Netlify mutation API calls
- Check: scan for Netlify API write patterns
- Pass condition: none found

### 12. Secrets/Token/Env Validator
- No secrets, tokens, or environment variable reads
- Check: scan for secret patterns, token patterns, env var reads
- Pass condition: none found

### 13. Disabled Labels Validator
- All action-like controls must display standard disabled labels
- Required labels: DISABLED — PLANNING ONLY, DISABLED — REVIEW ONLY, DISABLED — NO EXECUTION IN PHASE 5, DISABLED — FUTURE AUTH/STORAGE REQUIRED, DISABLED — FUTURE CONTROLLED AUTOMATION GATE
- Check: scan for interactive control elements without disabled labels
- Pass condition: all interactive controls have disabled labels

### 14. Planning-Only Labels Validator
- Planning documents must contain PLANNING_ONLY status
- Check: scan for files under 09_exports/interface_phase_5/
- Pass condition: all files contain PLANNING_ONLY

### 15. Safety Language Validator
- Planning documents must contain appropriate safety language
- Check: scan for safety boundary references
- Pass condition: safety language present

### 16. State Machine Terms Validator
- Request state machine must not include forbidden states
- Forbidden states: executing, deployed, merged, pushed, pr_created, mutation_completed
- Check: scan for forbidden state names in state machine definitions
- Pass condition: forbidden states not present in allowed states

### 17. Report Verdicts Validator
- Safety report must contain PASS_WITH_HIGH_CONFIDENCE
- Acceptance report must contain PASS_WITH_HIGH_CONFIDENCE
- Check: grep for verdict strings
- Pass condition: both reports have PASS verdict

## Validator Pass String Convention
Each validator must print a unique pass string on success:
- PHASE_5_NETLIFY_FUNCTIONS_VALIDATOR_PASS
- PHASE_5_EXTERNAL_FETCHES_VALIDATOR_PASS
- PHASE_5_UNAUTHORIZED_ENDPOINT_VALIDATOR_PASS
- PHASE_5_STORAGE_API_VALIDATOR_PASS
- PHASE_5_COOKIES_VALIDATOR_PASS
- PHASE_5_REAL_TIME_TRANSPORT_VALIDATOR_PASS
- PHASE_5_DYNAMIC_CODE_VALIDATOR_PASS
- PHASE_5_DEPLOY_MERGE_PUSH_PR_CONTROLS_VALIDATOR_PASS
- PHASE_5_COMMAND_EXECUTION_VALIDATOR_PASS
- PHASE_5_GITHUB_MUTATION_VALIDATOR_PASS
- PHASE_5_NETLIFY_MUTATION_VALIDATOR_PASS
- PHASE_5_SECRETS_TOKEN_ENV_VALIDATOR_PASS
- PHASE_5_DISABLED_LABELS_VALIDATOR_PASS
- PHASE_5_PLANNING_ONLY_LABELS_VALIDATOR_PASS
- PHASE_5_SAFETY_LANGUAGE_VALIDATOR_PASS
- PHASE_5_STATE_MACHINE_TERMS_VALIDATOR_PASS
- PHASE_5_REPORT_VERDICTS_VALIDATOR_PASS

## Validator Failure Handling
If any validator fails:
- STOP
- Report which validator failed
- Report the specific failure reason
- Do not merge
- Do not deploy
- Fix the issue before re-running
