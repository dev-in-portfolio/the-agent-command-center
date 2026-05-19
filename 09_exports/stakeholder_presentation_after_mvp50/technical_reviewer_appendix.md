# Technical Reviewer Appendix

## Architecture Summary
The Agent Command Center is a static single-page application served via Netlify. The source repository contains:
- Dashboard HTML/JS/CSS under `13_web_dashboard/dist/`
- JSON data files for structured content
- Python validators under `scripts/`
- Documentation and reports under `09_exports/`
- Netlify configuration in `netlify.toml`

## Validator Strategy
Each readiness layer has one or more Python validators that check:
- Specific text markers in the dashboard HTML
- JSON schema structure in data files
- Safety boundary markers
- Production verification status

Validators are designed to be run locally with `python3 scripts/validate_*.py`.

## Flat E2E Strategy
Validators use a flat E2E pattern — each validator is independent and checks a specific layer. There are no nested E2E chains. This means:
- Validators can run in parallel
- A single failure does not cascade
- Each validator is simple to debug and maintain

## Dynamic Latest-Status Strategy
The dashboard dynamically shows the latest verified milestone by checking the production verification report. The latest status is:
- Latest production verified MVP: MVP-50
- Latest verified milestone: MVP-50
- This is checked by validate_live_dashboard_dynamic_latest_status.py

## Safety-Denial Marker Strategy
The dashboard includes explicit markers that deny safety-critical capabilities:
- NOT_READY_FOR_REAL_AUTOMATION
- READINESS_ROADMAP_COMPLETE_PENDING_REVIEW
These markers are checked by automated validators. If any code change removes or alters them, the validators fail.

## Known Limitations
- Validators are not a substitute for a security review
- Validators check marker presence, not external correctness
- Validators do not test runtime behavior (no runtime exists)
- No penetration testing has been performed
- No dependency vulnerability scanning is in place

## Future Runtime Activation Gates
Before any runtime activation:
1. External security audit
2. Feature flag infrastructure
3. Human approval gates
4. Monitoring and alert integration
5. Rollback procedures
6. Stakeholder sign-off
