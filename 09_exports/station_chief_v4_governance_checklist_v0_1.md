# Station Chief v4.0 Governance Checklist v0.1

## Gate 1 - Runtime Readiness
- [ ] v3.9 landed
- [ ] v3.9 runtime hardening passed
- [ ] v3.9 validator passes
- [ ] validator chain passes
- [ ] no accidental v4.0 files exist

## Gate 2 - Non-Runtime Readiness
- [ ] non-runtime readiness report exists
- [ ] non-runtime readiness summary JSON parses
- [ ] operator playbook exists
- [ ] governance checklist exists
- [ ] worker architecture boundaries documented
- [ ] approval doctrine documented
- [ ] STOP rules documented
- [ ] audit requirements documented
- [ ] rollback/cleanup doctrine documented

## Gate 3 - Candidate Safety
- [ ] candidate is local only
- [ ] candidate is deterministic
- [ ] candidate is reversible
- [ ] candidate writes only to explicit output directory
- [ ] candidate has no API call
- [ ] candidate has no network access
- [ ] candidate opens no sockets
- [ ] candidate performs no DNS resolution
- [ ] candidate uses no credentials
- [ ] candidate reads no secrets
- [ ] candidate reads no environment variables
- [ ] candidate performs no deployment
- [ ] candidate performs no production execution
- [ ] candidate performs no worker activation
- [ ] candidate performs no live task routing

## Gate 4 - Approval
- [ ] approval token is explicit
- [ ] human operator is identified
- [ ] output directory is identified
- [ ] expected artifact is identified
- [ ] forbidden paths are identified
- [ ] cleanup rule is identified
- [ ] verification rule is identified

## Gate 5 - Artifact and Audit
- [ ] pre-action contract exists
- [ ] approval gate exists
- [ ] output manifest exists
- [ ] post-action verification exists
- [ ] audit proof exists
- [ ] ledger exists
- [ ] machine-readable summary exists

## Gate 6 - Scope
- [ ] no baseline files modified
- [ ] no Devinization overlays modified
- [ ] no dashboard exports modified
- [ ] no org chart export modified
- [ ] no master department list modified
- [ ] no ownership metadata modified
- [ ] no generated runtime artifact directories committed
- [ ] no forbidden files staged

## Final Governance Decision
- [ ] Approved to write v4.0 prompt
- [ ] Approved to run v4.0 candidate after separate token
- [ ] Not approved - blockers remain
