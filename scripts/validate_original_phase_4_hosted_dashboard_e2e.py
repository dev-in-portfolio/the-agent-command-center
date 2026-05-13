import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def run_script(name):
    print(f"Running {name}...")
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / name)], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FAIL: {name} failed.")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)
    return result.stdout

def check():
    scripts = [
        "validate_original_phase_4_hosted_dashboard_polish.py",
        "validate_backend_phase_4d_schema_previews.py",
        "validate_backend_phase_4d_disabled_ui.py",
        "validate_backend_phase_4c_snapshot.py",
        "validate_backend_phase_4a_foundation.py",
        "validate_interface_phase_3_dashboard.py"
    ]
    
    for script in scripts:
        run_script(script)
        
    # Check reports for verdict
    reports_dir = ROOT / "09_exports" / "interface_phase_4"
    reports = list(reports_dir.glob("*.md"))
    if not reports:
        print("FAIL: No reports found in interface_phase_4")
        sys.exit(1)
        
    for report in reports:
        if "original_phase_4_acceptance_report.md" in report.name:
            if "PASS_WITH_HIGH_CONFIDENCE" not in report.read_text():
                 print(f"FAIL: Verdict missing in {report.name}")
                 sys.exit(1)

    print("ORIGINAL_PHASE_4_HOSTED_DASHBOARD_E2E_VALIDATION_PASS")

if __name__ == "__main__":
    check()
