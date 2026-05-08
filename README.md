# Agent Command Center

This repository is the source-of-truth architecture for an Agent Command Center / artificial organization. It contains the strict schema, department registry, role definitions, and workflow templates required to govern and execute automated tasks systematically.

## Station Chief Validation

- Pushes to master run `.github/workflows/station-chief-validation.yml`.
- The workflow runs the Station Chief validator chain (v5.0 through current version).
- The workflow is verification-only and does not deploy, commit, push, or mutate repo state.
- Build prompts still require committed validation reports.
- Human review checks pushed source, validator source, report, and GitHub Actions run result.
