# Station Chief GitHub Actions Validation Setup Report

**Status**: LANDED

## Purpose

This creates GitHub-visible validator execution on push so reviewers can inspect source, validator source, reports, and GitHub Actions result/receipt.

## Workflow Created

- .github/workflows/station-chief-validation.yml

## Validation Model

- GitHub Actions runs validators on push.
- Builder still commits the validation report.
- Operator/ChatGPT inspects pushed source, validator source, report, and GitHub Actions result/receipt.

## Safety Boundaries

- no runtime behavior changed
- no runtime version changed
- no release lock version changed
- no adapter version changed
- no v6.3 created
- no deployment behavior added
- no production behavior added
- no secrets added
- no credentials added
- workflow does not commit
- workflow does not push
- workflow does not deploy

## Validator Commands

The workflow runs these commands in order:

```
python3 scripts/validate_station_chief_runtime_v6_2.py
python3 scripts/validate_station_chief_runtime_v6_1.py
python3 scripts/validate_station_chief_runtime_v6_0.py
python3 scripts/validate_station_chief_runtime_v5_9.py
python3 scripts/validate_station_chief_runtime_v5_8.py
python3 scripts/validate_station_chief_runtime_v5_7.py
python3 scripts/validate_station_chief_runtime_v5_6.py
python3 scripts/validate_station_chief_runtime_v5_5.py
python3 scripts/validate_station_chief_runtime_v5_4.py
python3 scripts/validate_station_chief_runtime_v5_3.py
python3 scripts/validate_station_chief_runtime_v5_2.py
python3 scripts/validate_station_chief_runtime_v5_1.py
python3 scripts/validate_station_chief_runtime_v5_0.py
```

After validation, the workflow verifies `git status --short` is clean and uploads all markdown reports from `09_exports/` as artifacts.

## Manual Run

The workflow can be triggered manually via the GitHub Actions UI using `workflow_dispatch`.

## Review Procedure

Future checks should verify:
- latest pushed source
- top validator source
- matching version report
- GitHub Actions run status
- uploaded validation artifacts / logs
- no unexpected version files

## Final Validation

All validators pass locally:
- v6.2: STATION_CHIEF_RUNTIME_V6_2_VALIDATION_PASS
- v6.1: STATION_CHIEF_RUNTIME_V6_1_VALIDATION_PASS
- v6.0: STATION_CHIEF_RUNTIME_V6_0_VALIDATION_PASS
- v5.9: STATION_CHIEF_RUNTIME_V5_9_VALIDATION_PASS
- v5.8: STATION_CHIEF_RUNTIME_V5_8_VALIDATION_PASS
- v5.7: STATION_CHIEF_RUNTIME_V5_7_VALIDATION_PASS
- v5.6: STATION_CHIEF_RUNTIME_V5_6_VALIDATION_PASS
- v5.5: STATION_CHIEF_RUNTIME_V5_5_VALIDATION_PASS
- v5.4: STATION_CHIEF_RUNTIME_V5_4_VALIDATION_PASS
- v5.3: STATION_CHIEF_RUNTIME_V5_3_VALIDATION_PASS
- v5.2: STATION_CHIEF_RUNTIME_V5_2_VALIDATION_PASS
- v5.1: STATION_CHIEF_RUNTIME_V5_1_VALIDATION_PASS
- v5.0: STATION_CHIEF_RUNTIME_V5_0_VALIDATION_PASS

GitHub Actions will run the same chain on push to master.
