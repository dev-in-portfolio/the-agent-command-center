# Stakeholder FAQ

## Q1: Is this live automation?
No. This is a read-only dashboard that documents readiness architecture. No automation runs.

## Q2: Does it write to a database?
No. There are no database write endpoints. No write paths exist in the deployed system.

## Q3: Can it deploy or merge code?
No. Deploy and merge controls are not in the app. The dashboard is a static site.

## Q4: Can it trigger alerts?
No. No alert endpoints or channels are configured. Alert sending is disabled.

## Q5: Can it roll back production?
No. Rollback execution is disabled. No rollback endpoints exist.

## Q6: What does "production verified" mean?
It means the artifact was tested against the live site using automated validators, and the correct markers were confirmed. It proves the live site serves the expected content.

## Q7: What is "schema readiness"?
Schema readiness means the data model, contracts, and validation logic for a capability have been designed and documented. It does not mean the runtime implementation is complete.

## Q8: What is the next step?
External demo and stakeholder review. If approved, runtime activation planning begins as a separate phase.

## Q9: What would runtime activation require?
A separate planning phase with feature flags, human approval gates, monitoring integration, security review, and stakeholder sign-off.

## Q10: Is it safe to demo externally?
Yes. The system is read-only. No data can be modified. No execution can be triggered. It is safe to share the live URL with external reviewers.

## Q11: What are the 8 readiness layers?
MVP-43 (Auth), MVP-44 (Storage), MVP-45 (Audit), MVP-46 (Approval), MVP-47 (Dry-Run), MVP-48 (Action Queue), MVP-49 (Execution), MVP-50 (Monitoring/Rollback/Incident Console).

## Q12: What does NOT_READY_FOR_REAL_AUTOMATION mean?
It means the system explicitly documents that it is not ready for real automation. This marker is checked by validators to prevent false claims.

## Q13: Does the dashboard use any APIs?
No. The dashboard is a static HTML file with inline content and JSON data files. No API calls are made from the client.

## Q14: What happens if someone tries to use this as a real command center?
They cannot. There are no execution endpoints, no runtime workers, no automation triggers. The system is architecturally incapable of performing actions.

## Q15: How do validators work?
Validators are Python scripts that check for specific text markers and structural patterns in the dashboard HTML and JSON files. They run locally and must pass before any commit.

## Q16: Are there any security reviews?
Not yet. The system has not undergone external security review. This is a recommended step before any runtime activation.

## Q17: What is in the 09_exports directory?
All production reports, readiness assessments, and now the external demo package. These are the documentation artifacts of the readiness roadmap.

## Q18: Can I see the code?
Yes. The repository is at https://github.com/dev-in-portfolio/the-agent-command-center.
