import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path


class InterfaceSessionLog:
    def __init__(self, repo_name="the-agent-command-center"):
        self.session_id = datetime.now(timezone.utc).strftime("SES-%Y%m%d-%H%M%S-%f")
        self.started_at_utc = datetime.now(timezone.utc).isoformat()
        self.ended_at_utc = None
        self.repo_name = repo_name
        self.repo_path = str(Path.cwd())
        self.git_branch_start = self._get_git_branch()
        self.git_commit_start = self._get_git_commit()
        self.git_branch_end = None
        self.git_commit_end = None
        self.actions_requested = []
        self.actions_completed = []
        self.actions_refused = []
        self.action_results = []
        self.action_durations = []
        self.last_action_name = None
        self.last_action_status = None
        self.last_action_timestamp = None
        self.recommended_next_action = None
        self.validator_results = []
        self.reports_generated = []
        self.command_packets_prepared = []
        self.command_packet_hashes = []
        self.artifacts_inspected = []
        self.errors = []
        self.final_boundary_state = "unknown"

    def _get_git_branch(self):
        try:
            import subprocess
            r = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                               capture_output=True, text=True, timeout=5)
            return r.stdout.strip() if r.returncode == 0 else "unknown"
        except Exception:
            return "unknown"

    def _get_git_commit(self):
        try:
            import subprocess
            r = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                               capture_output=True, text=True, timeout=5)
            return r.stdout.strip() if r.returncode == 0 else "unknown"
        except Exception:
            return "unknown"

    def record_action(self, action_name, result=None, recommended_next=None):
        self.actions_requested.append(action_name)
        self.actions_completed.append(action_name)
        self.last_action_name = action_name
        self.last_action_status = "PASS"
        self.last_action_timestamp = datetime.now(timezone.utc).isoformat()
        if result:
            self.action_results.append(result)
        if recommended_next:
            self.recommended_next_action = recommended_next

    def record_refused(self, action_name, reason):
        self.actions_requested.append(action_name)
        self.actions_refused.append({"action": action_name, "reason": reason})
        self.last_action_name = action_name
        self.last_action_status = "REFUSED"
        self.last_action_timestamp = datetime.now(timezone.utc).isoformat()

    def record_action_duration(self, action_name, seconds):
        self.action_durations.append({"action": action_name, "seconds": seconds})

    def record_validator_result(self, name, returncode, stdout, timestamp):
        self.validator_results.append({
            "name": name,
            "returncode": returncode,
            "passed": returncode == 0,
            "stdout": stdout,
            "timestamp": timestamp,
        })

    def record_report(self, path):
        self.reports_generated.append(path)

    def record_command_packet(self, path):
        self.command_packets_prepared.append(path)
        try:
            content = Path(path).read_bytes()
            h = hashlib.sha256(content).hexdigest()
            self.command_packet_hashes.append({"path": str(path), "sha256": h})
        except Exception:
            self.command_packet_hashes.append({"path": str(path), "sha256": "unknown"})

    def record_artifact_inspection(self, package_name, status):
        self.artifacts_inspected.append({"package": package_name, "status": status})

    def record_error(self, error_message):
        self.errors.append(error_message)
        self.last_action_status = "ERROR"

    def set_recommended_next(self, recommendation):
        self.recommended_next_action = recommendation

    def close(self):
        self.ended_at_utc = datetime.now(timezone.utc).isoformat()
        self.git_branch_end = self._get_git_branch()
        self.git_commit_end = self._get_git_commit()
        refused_count = len(self.actions_refused)
        error_count = len(self.errors)
        self.final_boundary_state = "secure" if refused_count == 0 and error_count == 0 else "secure_with_notes"

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "started_at_utc": self.started_at_utc,
            "ended_at_utc": self.ended_at_utc,
            "repo_name": self.repo_name,
            "repo_path": self.repo_path,
            "git_branch_start": self.git_branch_start,
            "git_commit_start": self.git_commit_start,
            "git_branch_end": self.git_branch_end,
            "git_commit_end": self.git_commit_end,
            "actions_requested": self.actions_requested,
            "actions_completed": self.actions_completed,
            "actions_refused": self.actions_refused,
            "action_results": self.action_results,
            "action_durations": self.action_durations,
            "last_action_name": self.last_action_name,
            "last_action_status": self.last_action_status,
            "last_action_timestamp": self.last_action_timestamp,
            "recommended_next_action": self.recommended_next_action,
            "validator_results": [
                {
                    "name": v["name"],
                    "returncode": v["returncode"],
                    "passed": v["passed"],
                    "timestamp": v["timestamp"],
                }
                for v in self.validator_results
            ],
            "reports_generated": self.reports_generated,
            "command_packets_prepared": self.command_packets_prepared,
            "command_packet_hashes": self.command_packet_hashes,
            "artifacts_inspected": self.artifacts_inspected,
            "errors": self.errors,
            "final_boundary_state": self.final_boundary_state,
        }

    def generate_report(self):
        if self.ended_at_utc is None:
            self.close()

        lines = []
        lines.append("# Operator Session Report")
        lines.append("")
        lines.append(f"**Session ID:** {self.session_id}")
        lines.append(f"**Repo:** {self.repo_name}")
        lines.append(f"**Repo path:** {self.repo_path}")
        lines.append(f"**Started:** {self.started_at_utc}")
        lines.append(f"**Ended:** {self.ended_at_utc}")
        lines.append(f"**Branch start:** {self.git_branch_start} @ {self.git_commit_start}")
        lines.append(f"**Branch end:** {self.git_branch_end} @ {self.git_commit_end}")
        lines.append(f"**Final boundary state:** {self.final_boundary_state}")
        lines.append("")
        lines.append(f"**Last action:** {self.last_action_name} [{self.last_action_status}]")
        lines.append(f"**Recommended next:** {self.recommended_next_action or 'None'}")
        lines.append("")
        lines.append("## Actions Requested")
        for a in self.actions_requested:
            lines.append(f"- {a}")
        lines.append("")
        lines.append("## Actions Completed")
        for a in self.actions_completed:
            lines.append(f"- {a}")
        lines.append("")
        if self.actions_refused:
            lines.append("## Actions Refused (Locked)")
            for r in self.actions_refused:
                lines.append(f"- {r['action']}: {r['reason']}")
            lines.append("")
        if self.validator_results:
            lines.append("## Validator Results")
            for v in self.validator_results:
                status = "PASS" if v["passed"] else "FAIL"
                lines.append(f"- {v['name']}: {status} (rc={v['returncode']}) @ {v['timestamp']}")
            lines.append("")
        if self.reports_generated:
            lines.append("## Reports Generated")
            for rp in self.reports_generated:
                lines.append(f"- {rp}")
            lines.append("")
        if self.command_packets_prepared:
            lines.append("## Command Packets Prepared")
            for cp in self.command_packets_prepared:
                lines.append(f"- {cp}")
            lines.append("")
        if self.errors:
            lines.append("## Errors")
            for e in self.errors:
                lines.append(f"- {e}")
            lines.append("")
        if self.artifacts_inspected:
            lines.append("## Artifacts Inspected")
            for a in self.artifacts_inspected:
                lines.append(f"- {a['package']}: {a['status']}")
            lines.append("")

        lines.append("## Safety Summary")
        lines.append(f"- Locked actions refused: {len(self.actions_refused)}")
        lines.append(f"- Errors encountered: {len(self.errors)}")
        lines.append(f"- Boundary state: {self.final_boundary_state}")
        lines.append("")

        return "\n".join(lines)
