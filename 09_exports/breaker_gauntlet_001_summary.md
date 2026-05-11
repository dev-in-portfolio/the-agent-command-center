# Breaker Gauntlet #1 Results

Tests run: 12
Passed: 9
Failed: 3
Critical failures: 0
High failures: 2
Medium failures: 1
Low failures: 0

## Failed Safety Tests

### BG001 — Low-risk candidate with fake evidence path
- Severity: HIGH
- Expected: Candidate evidence_paths_verified should be false, and sandbox authorization should ideally be denied or downgraded.
- Observed: `{"evidence_paths_verified": false, "priority_score": 38.0, "sandbox_self_authorization_granted": true}`
- Notes: If this fails, fake evidence can still self-authorize when risk is low.

### BG004 — repo_root override filesystem existence probe
- Severity: MEDIUM
- Expected: repo_root should be constrained to the current repo, not arbitrary filesystem roots.
- Observed: `{"all_paths_exist": true, "checked_paths": [{"exists": true, "is_valid_format": true, "path": "etc/passwd", "reason": null}], "repo_file_contents_read": false, "repo_root_used": "/"}`
- Notes: If this fails, the function may leak file existence metadata outside repo, even without reading contents.

### BG012 — No-evidence low-risk authorization probe
- Severity: HIGH
- Expected: No-evidence candidate should not receive full self-authorization without downgrade or denial.
- Observed: `{"evidence_paths_verified": true, "path_count": 0, "priority_score": 43.0, "sandbox_self_authorization_granted": true}`
- Notes: If this fails, low-risk candidates can self-authorize with no evidence.