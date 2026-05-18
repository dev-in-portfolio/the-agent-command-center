#!/usr/bin/env python3
# MVP-41 E2E Validator — runs direct validator + chain dependencies + master wall + self-check

import subprocess, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILURES = []


def run_script(name, *args):
    path = os.path.join(REPO, 'scripts', name)
    if not os.path.isfile(path):
        return f'[FAIL] Script not found: {name}'
    try:
        result = subprocess.run([sys.executable, path] + list(args), capture_output=True, text=True, cwd=REPO, timeout=360)
        out = result.stdout.strip()
        err = result.stderr.strip()
        if result.returncode != 0:
            return f'[FAIL] Exit code {result.returncode}\\n{out}\\n{err}'
        return out
    except subprocess.TimeoutExpired:
        return '[FAIL] Timeout'
    except Exception as e:
        return f'[FAIL] {e}'

print('MVP-41 E2E Validation')
print()

print('Phase 1 — MVP-41 Direct Validator')
r1 = run_script('validate_mvp41_controlled_reviewer_response_intake_blueprint.py')
if 'MVP41_CONTROLLED_REVIEWER_RESPONSE_INTAKE_BLUEPRINT_VALIDATION_PASS' in r1:
    print('  [PASS] MVP-41 direct')
else:
    print(f'  [FAIL] MVP-41 direct\\n{r1}')
    FAILURES.append('MVP-41 direct validator failed')

print()
print('Phase 2 — MVP-40 E2E Validator (chain dependency)')
r2 = run_script('validate_mvp40_reviewer_response_capture_readiness_lock_e2e.py')
if 'MVP40_REVIEWER_RESPONSE_CAPTURE_READINESS_LOCK_E2E_VALIDATION_PASS' in r2:
    print('  [PASS] MVP-40 E2E')
else:
    print(f'  [FAIL] MVP-40 E2E\\n{r2}')
    FAILURES.append('MVP-40 E2E validator failed')

print()
print('Phase 3 — MVP-39 E2E Validator (chain dependency)')
r3 = run_script('validate_mvp39_external_demo_review_share_package_lock_e2e.py')
if 'MVP39_EXTERNAL_DEMO_REVIEW_SHARE_PACKAGE_LOCK_E2E_VALIDATION_PASS' in r3:
    print('  [PASS] MVP-39 E2E')
else:
    print(f'  [FAIL] MVP-39 E2E\\n{r3}')
    FAILURES.append('MVP-39 E2E validator failed')

print()
print('Phase 4 — Master Validator Wall')
r4 = run_script('validate_phase5_plus1_master_validator_wall.py')
if 'PHASE5_PLUS1_MASTER_VALIDATOR_WALL_PASS' in r4:
    print('  [PASS] Master wall')
else:
    print(f'  [FAIL] Master wall\\n{r4}')
    FAILURES.append('Master validator wall failed')

print()
print('Phase 5 — Self-check: MVP-41 direct validator safety contract')
required_markers = [
    'MVP41_DIRECT_VALIDATOR_FULL_SAFETY_CONTRACT',
    'MVP41_NO_PUBLIC_ENDPOINT_CHECK',
    'MVP41_NO_LIVE_INTAKE_CHECK',
    'MVP41_NO_PUBLIC_RESPONSE_SUBMISSION_CHECK',
    'MVP41_NO_REVIEWER_RESPONSE_WRITES_CHECK',
    'MVP41_NO_RESPONSE_CAPTURE_ENABLED_CHECK',
    'MVP41_NO_RESPONSE_PERSISTENCE_ENABLED_CHECK',
    'MVP41_NO_AUTOMATIC_IMPORT_CHECK',
    'MVP41_NO_EMAIL_SENDING_CHECK',
    'MVP41_NO_REVIEWER_CONTACT_CHECK',
    'MVP41_NO_AUTOMATED_OUTREACH_CHECK',
    'MVP41_NO_LIVE_WRITES_CHECK',
    'MVP41_NO_PUBLIC_WRITES_CHECK',
    'MVP41_NO_TOKEN_INPUT_CHECK',
    'MVP41_NO_SECRETS_EXPOSED_CHECK',
    'MVP41_NO_SERVICE_ROLE_CHECK',
    'MVP41_NO_BROWSER_PERSISTENCE_CHECK',
    'MVP41_NO_DIRECT_SUPABASE_CHECK',
    'MVP41_NO_UPDATE_DELETE_APPROVE_EXECUTE_CHECK',
    'MVP41_CONTROLLED_REVIEWER_RESPONSE_INTAKE_EXPORT_ARTIFACTS_CHECK',
    'MVP41_NO_WHOLE_FILE_SAFETY_LABEL_SKIP',
]
dv_path = os.path.join(REPO, 'scripts', 'validate_mvp41_controlled_reviewer_response_intake_blueprint.py')
if os.path.isfile(dv_path):
    with open(dv_path) as f:
        dv_src = f.read()
    missing = [m for m in required_markers if m not in dv_src]
    if missing:
        print(f'  [FAIL] Missing markers: {", ".join(missing)}')
        FAILURES.append('MVP-41 direct validator missing safety contract markers')
    else:
        print('  [PASS] MVP-41 direct validator full safety contract coverage verified')
else:
    print('  [FAIL] MVP-41 direct validator file not found')
    FAILURES.append('MVP-41 direct validator file not found')

print()
if FAILURES:
    print(f'FAILURES: {len(FAILURES)}')
    for f in FAILURES:
        print(f'  {f}')
    sys.exit(1)

print('MVP41_CONTROLLED_REVIEWER_RESPONSE_INTAKE_BLUEPRINT_E2E_VALIDATION_PASS')
