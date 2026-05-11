# The Agent Command Center

This repository is the dedicated operator-interface and product workspace cloned from the validated `agent-command-center-3` sandbox line.

Source lineage:
- Original sandbox repo: `dev-in-portfolio/agent-command-center-3`
- New interface/product repo: `dev-in-portfolio/the-agent-command-center`

Purpose:
- preserve validated runtime evidence
- build the human-facing operator interface
- keep official repo and repo 2 untouched
- separate product/interface work from sandbox validation work

Current status:
- Station Chief Runtime v25.0.0 preserved
- Auto-Self-Improve-2 sandbox lineage preserved
- 100-Round Trial v3 evidence preserved
- Non-Repo Extreme Work Gauntlet #1 evidence preserved

Safety:
- No official repo mutation
- No repo 2 mutation
- No deployment
- No secrets/credentials access
- Interface work starts in future branches

---

# Agent Command Center

This repository is the source-of-truth architecture for an Agent Command Center / artificial organization. It contains the strict schema, department registry, role definitions, and workflow templates required to govern and execute automated tasks systematically.

## Station Chief Validation

- Pushes to master run `.github/workflows/station-chief-validation.yml`.
- The workflow runs the Station Chief validator chain (v5.0 through current version).
- The workflow is verification-only and does not deploy, commit, push, or mutate repo state.
- Build prompts still require committed validation reports.
- Human review checks pushed source, validator source, report, and GitHub Actions run result.
