import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BRANCH_REVIEWS_DIR = ROOT / "09_exports" / "interface_phase_1" / "branch_reviews"
REPO_NAME = "dev-in-portfolio/the-agent-command-center"
SOURCE_LINEAGE = "dev-in-portfolio/agent-command-center-3"


def sanitize_branch_name(name):
    if not name or not isinstance(name, str):
        return None
    if len(name) > 200:
        return None
    if ".." in name:
        return None
    if name.startswith("/") or name.startswith("~"):
        return None
    if re.search(r"[\x00-\x1f\x7f]", name):
        return None
    safe = name.replace("/", "_")
    safe = re.sub(r"[^a-zA-Z0-9_.-]", "_", safe)
    return safe


def prepare_branch_review(review_branch, base_branch="master"):
    safe_name = sanitize_branch_name(review_branch)
    if not safe_name:
        return {
            "status": "FAIL",
            "error": f"Invalid branch name: {review_branch}",
        }

    BRANCH_REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    review_path = BRANCH_REVIEWS_DIR / f"{safe_name}_review.md"

    review_id = f"BR-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{safe_name[:16]}"

    # Gather changed files
    changed_files = []
    try:
        r = subprocess.run(
            ["git", "diff", "--name-only", f"{base_branch}..{review_branch}"],
            capture_output=True, text=True, timeout=30
        )
        if r.returncode == 0 and r.stdout.strip():
            changed_files = [ln.strip() for ln in r.stdout.strip().splitlines() if ln.strip()]
    except Exception:
        changed_files = []

    # Categorize files
    interface_files = [f for f in changed_files if f.startswith("11_interface/")]
    export_files = [f for f in changed_files if f.startswith("09_exports/")]
    script_validator_files = [f for f in changed_files if f.startswith("scripts/validate_")]
    runtime_files = [f for f in changed_files if f.startswith("10_runtime/")]
    workflow_files = [f for f in changed_files if f.startswith(".github/")]
    unknown_files = [f for f in changed_files if not any([
        f.startswith("11_interface/"),
        f.startswith("09_exports/"),
        f.startswith("scripts/validate_"),
        f.startswith("10_runtime/"),
        f.startswith(".github/"),
        f.startswith("README"),
        f.startswith("00_"), f.startswith("01_"), f.startswith("02_"),
        f.startswith("03_"), f.startswith("04_"), f.startswith("05_"),
        f.startswith("06_"), f.startswith("07_"), f.startswith("08_"),
    ])]

    # Determine risk
    risk_level = "low"
    risk_reasons = []
    if runtime_files:
        risk_level = "high"
        risk_reasons.append("Runtime files changed")
    if unknown_files:
        risk_level = "high"
        risk_reasons.append("Unknown file types changed")
    if workflow_files:
        risk_level = "high"
        risk_reasons.append("Workflow files changed")
    if not risk_reasons and changed_files:
        risk_level = "low"
    if not changed_files:
        risk_level = "low"

    allowed_detected = bool(interface_files or export_files or script_validator_files)
    unexpected_detected = bool(runtime_files or unknown_files or workflow_files)

    lines = []
    lines.append("# Branch Review Packet")
    lines.append("")
    lines.append(f"**Review ID:** {review_id}")
    lines.append(f"**Created At (UTC):** {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"**Repo:** {REPO_NAME}")
    lines.append(f"**Base Branch:** {base_branch}")
    lines.append(f"**Review Branch:** {review_branch}")
    lines.append(f"**Source Lineage:** {SOURCE_LINEAGE}")
    lines.append("")
    lines.append("**Status:** prepared_not_merged")
    lines.append("**Merge Performed:** false")
    lines.append("**Deployment Performed:** false")
    lines.append("**Official Repo Touched:** false")
    lines.append("**Repo 2 Touched:** false")
    lines.append("**Repo 3 Touched:** false")
    lines.append("**Secrets/Credentials Used:** false")
    lines.append("")
    lines.append("## Risk Level")
    lines.append(f"{risk_level.upper()}")
    if risk_reasons:
        for rr in risk_reasons:
            lines.append(f"- {rr}")
    lines.append("")
    lines.append("## Changed Files")
    if changed_files:
        for cf in changed_files:
            lines.append(f"- {cf}")
    else:
        lines.append("No changes detected between branches.")
    lines.append("")
    lines.append("## File Type Summary")
    lines.append(f"- Interface files: {len(interface_files)}")
    lines.append(f"- Export/report files: {len(export_files)}")
    lines.append(f"- Scripts/validators: {len(script_validator_files)}")
    lines.append(f"- Runtime files: {len(runtime_files)}")
    lines.append(f"- Workflow files: {len(workflow_files)}")
    lines.append(f"- Unknown files: {len(unknown_files)}")
    if unexpected_detected:
        lines.append("")
        lines.append("**WARNING:** Unexpected file types detected in this branch.")
    lines.append("")
    lines.append("## Allowed Path Check")
    lines.append(f"- Allowed paths detected: {'Yes' if allowed_detected else 'No'}")
    lines.append(f"- Unexpected paths detected: {'Yes' if unexpected_detected else 'No'}")
    lines.append("")
    lines.append("## Validator Requirements")
    lines.append("- [ ] python3 scripts/validate_interface_phase_1_cli.py")
    lines.append("- [ ] python3 scripts/validate_auto_self_improve_2.py")
    lines.append("- [ ] python3 scripts/validate_station_chief_runtime_v25_0.py")
    lines.append("- [ ] python3 scripts/validate_station_chief_runtime_v24_0.py")
    if script_validator_files:
        lines.append("- [ ] python3 scripts/validate_interface_phase_1_command_packets.py")
    lines.append("")
    lines.append("## Human Review Checklist")
    lines.append("- [ ] Changed files reviewed")
    lines.append("- [ ] Validators passed")
    lines.append("- [ ] No locked repo touched")
    lines.append("- [ ] No deploy behavior")
    lines.append("- [ ] No secrets behavior")
    lines.append("- [ ] No unexpected runtime changes")
    lines.append("- [ ] Operator approves merge separately")
    lines.append("")
    lines.append("## Recommended Operator Decision")

    if risk_level == "blocked":
        decision = "blocked_do_not_merge"
    elif risk_level == "high":
        decision = "needs_fixes"
    elif risk_level == "low":
        decision = "ready_for_review"
    else:
        decision = "needs_fixes"

    lines.append(f"**{decision}**")

    review_path.write_text("\n".join(lines))

    return {
        "status": "PASS",
        "review_id": review_id,
        "review_path": str(review_path),
        "risk_level": risk_level,
        "changed_files": len(changed_files),
        "interface_files": len(interface_files),
        "export_files": len(export_files),
        "script_validator_files": len(script_validator_files),
        "runtime_files": len(runtime_files),
        "workflow_files": len(workflow_files),
        "unknown_files": len(unknown_files),
        "decision": decision,
    }
