#!/usr/bin/env bash
set -euo pipefail

# SAFE DEMO ONLY
# Does not push to any environment.
# Does not perform any merge action.
# Does not push to remote.
# Does not open PRs.
# Does not call network.
# Does not execute command packets.
# Does not touch official/repo2/repo3.
# Does not use any secret or credential values.
# Validator wall is intentionally not executed by this safe demo.

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLI="$ROOT/11_interface/station_chief_cli.py"
EXPORTS="$ROOT/09_exports/interface_phase_1"

echo "============================================================"
echo "  Interface Phase 1 — CLI Operator Console Demo"
echo "  Repo: dev-in-portfolio/the-agent-command-center"
echo "============================================================"
echo ""

# 1. Show system status
echo ">>> 1. Show system status"
python3 "$CLI" --status
echo ""

# 2. Show locked actions
echo ">>> 2. Show locked actions"
python3 "$CLI" --show-locked
echo ""

# 3. List artifact packages
echo ">>> 3. List artifact packages"
python3 "$CLI" --list-artifacts
echo ""

# 4. Inspect artifact packages
echo ">>> 4. Inspect artifact packages"
python3 "$CLI" --inspect-artifacts
echo ""

# 5. Inspect specific artifact package
echo ">>> 5. Inspect artifact package: trial_v3"
python3 "$CLI" --inspect-artifact trial_v3
echo ""

# 6. Show session state
echo ">>> 6. Show session state"
python3 "$CLI" --session-state
echo ""

# 7. Prepare command packet (validator_wall)
echo ">>> 7. Prepare command packet: validator_wall"
python3 "$CLI" --prepare-packet validator_wall
echo ""

# 8. Show approval ledger
echo ">>> 8. Show approval ledger"
python3 "$CLI" --show-approval-ledger
echo ""

# 9. Show summaries
echo ">>> 9. Show latest summaries"
python3 "$CLI" --show-summaries
echo ""

echo ">>> Optional validation step skipped in safe demo"
echo "To run the validator wall manually, use the CLI validator-wall flag."
echo "Note: validators may run checks that depend on local runtime/repo state."
echo ""

# 10. Generate session report
echo ">>> 10. Generate session report"
python3 "$CLI" --generate-session-report
echo ""

echo "============================================================"
echo "  Demo complete."
echo "  Session report: $EXPORTS/sessions/"
echo "  Command packet: $EXPORTS/command_packets/validator_wall_packet.md"
echo "============================================================"
