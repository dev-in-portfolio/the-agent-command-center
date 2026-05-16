# Share-Safe Checklist — External Demo Package

Before sharing this package, ensure all safety checks pass.

## 1. Zero Secrets
- [ ] No bearer tokens in any markdown file.
- [ ] No Authorization headers with real values.
- [ ] No Supabase secret keys or service role keys.
- [ ] No database passwords or connection strings.
- [ ] No private environment variables.

## 2. Zero Persistent Tokens
- [ ] Dashboard confirmed not to use `local-Storage`.
- [ ] Dashboard confirmed not to use `session-Storage`.
- [ ] Dashboard confirmed not to use cookies or `indexed-DB`.

## 3. Honest Positioning (Non-Hype)
- [ ] Project described as a "safety-first request control layer."
- [ ] No claim of being a "fully-autonomous-execution-engine."
- [ ] Blocked actions (Approve/Execute/Automation) clearly stated.
- [ ] Live test status correctly reported (e.g., "manual test required").

## 4. Integrity
- [ ] Request row update/delete remains blocked in the API.
- [ ] Service Role is not exposed to the browser.
- [ ] Automation is intentionally disabled.
