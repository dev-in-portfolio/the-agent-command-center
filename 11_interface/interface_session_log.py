from datetime import datetime, timezone


class InterfaceSessionLog:
    def __init__(self, repo_name="the-agent-command-center"):
        self.started_at_utc = datetime.now(timezone.utc).isoformat()
        self.ended_at_utc = None
        self.repo_name = repo_name
        self.actions_requested = []
        self.actions_completed = []
        self.actions_refused = []
        self.validator_results = []
        self.reports_generated = []
        self.command_packets_prepared = []
        self.errors = []
        self.final_boundary_state = "unknown"

    def record_action(self, action_name):
        self.actions_requested.append(action_name)
        self.actions_completed.append(action_name)

    def record_refused(self, action_name, reason):
        self.actions_requested.append(action_name)
        self.actions_refused.append({"action": action_name, "reason": reason})

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

    def record_error(self, error_message):
        self.errors.append(error_message)

    def close(self):
        self.ended_at_utc = datetime.now(timezone.utc).isoformat()
        refused_count = len(self.actions_refused)
        error_count = len(self.errors)
        self.final_boundary_state = "secure" if refused_count == 0 and error_count == 0 else "secure_with_notes"

    def generate_report(self):
        if self.ended_at_utc is None:
            self.close()

        lines = []
        lines.append("# Operator Session Report")
        lines.append("")
        lines.append(f"**Repo:** {self.repo_name}")
        lines.append(f"**Started:** {self.started_at_utc}")
        lines.append(f"**Ended:** {self.ended_at_utc}")
        lines.append(f"**Final boundary state:** {self.final_boundary_state}")
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

        lines.append("## Safety Summary")
        lines.append(f"- Locked actions refused: {len(self.actions_refused)}")
        lines.append(f"- Errors encountered: {len(self.errors)}")
        lines.append(f"- Boundary state: {self.final_boundary_state}")
        lines.append("")

        return "\n".join(lines)
