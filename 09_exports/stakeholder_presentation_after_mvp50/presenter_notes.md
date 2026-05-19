# Presenter Notes

## Before-Demo Notes
- Test the live site URL in incognito mode before the demo
- Clear browser cache or use cache-bust query parameter
- Have the demo package files open as backup reference
- Practice the click path at least once
- Know the 8 readiness layers by heart
- Prepare for the question "Is this live automation?"

## Confidence Points
- All 8 layers are production-verified
- Validators provide machine-checkable proof
- Live site confirmed serving correct content
- Safety markers are enforced by automated scripts
- No runtime means no risk of accidental execution

## Caveats
- The system has not undergone external security review
- Validators check markers, not runtime behavior
- Dashboard is static HTML — no interactive forms
- Some sections are schema documentation, not running services

## Terms to Avoid
- "Production-ready" (runtime is not active)
- "Live operations center" (it is a readiness dashboard)
- "Automation platform" (automation is disabled)
- "Command execution system" (execution is disabled)
- "Real-time" (it is a static dashboard)

## Claims Not to Make
- Do not claim the system executes commands
- Do not claim it writes to databases
- Do not claim it automates operations
- Do not claim it is security-reviewed
- Do not claim runtime activation has started
- Do not claim it is ready for production operations
- Do not claim it can send alerts or roll back changes

## How to Answer "Is It Live Automation?"
"No. This is a readiness architecture displayed as a read-only dashboard. It shows that the design, schema, and validation for each layer are complete. But nothing executes. No commands run. No automation is active. Runtime activation requires a separate planning phase and your explicit approval."
