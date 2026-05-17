#!/usr/bin/env python3
"""MVP-33 E2E validator — runs direct validator + master wall + self-check."""

import subprocess
import sys

ROOT = __file__.rsplit("/", 2)[0]
TIMEOUT = 120

def run(cmd, label):
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=TIMEOUT,
            cwd=ROOT,
        )
        if result.returncode != 0:
            print(f"  [FAIL] {label}")
            for line in result.stderr.splitlines()[-5:]:
                print(f"    {line}")
            return False
        print(f"  [PASS] {label}")
        return True
    except subprocess.TimeoutExpired:
        print(f"  [FAIL] {label} (timeout {TIMEOUT}s)")
        return False

def self_check():
    text = open(__file__).read()
    issues = []
    for token in ["local" "Storage", "session" "Storage", "docu" "ment.cookie", "ev" "al(", "Func" "tion(", "imp" "ort("]:
        if token in text:
            issues.append(f"E2E validator contains forbidden token: {token}")
    return issues

all_pass = True

print("MVP-33 E2E Validation")
print()

print("Phase 1 — MVP-33 Direct Validator")
if not run("python3 scripts/validate_mvp33_product_launch_readiness_final_pitch_packet.py", "MVP-33 direct"):
    all_pass = False

print()
print("Phase 2 — Master Validator Wall")
if not run("python3 scripts/validate_phase5_plus1_master_validator_wall.py", "Master wall"):
    all_pass = False

print()
print("Phase 3 — Self-check")
issues = self_check()
if issues:
    print("  [FAIL] E2E self-check")
    for issue in issues:
        print(f"    {issue}")
    all_pass = False
else:
    print("  [PASS] E2E self-check")

print()
if all_pass:
    print("MVP33_PRODUCT_LAUNCH_READINESS_FINAL_PITCH_PACKET_E2E_VALIDATION_PASS")
    sys.exit(0)
else:
    print("MVP33_E2E_VALIDATION_FAIL")
    sys.exit(1)
