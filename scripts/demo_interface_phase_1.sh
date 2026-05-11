#!/usr/bin/env bash
set -euo pipefail

# Interface Phase 1 — Demo Script
# This script demonstrates the CLI Operator Console in demo mode.
# It runs safe, read-only commands and prepares controlled artifacts.
# No git push, merge, PR, curl, or secrets are used.

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

# 5. Show session state
echo ">>> 5. Show session state"
python3 "$CLI" --session-state
echo ""

# 6. Prepare command packet (validator_wall)
echo ">>> 6. Prepare command packet: validator_wall"
python3 "$CLI" --prepare-packet validator_wall
echo ""

# 7. Show approval ledger
echo ">>> 7. Show approval ledger"
python3 "$CLI" --show-approval-ledger
echo ""

# 8. Show summaries
echo ">>> 8. Show latest summaries"
python3 "$CLI" --show-summaries
echo ""

# 9. Run validator wall
echo ">>> 9. Run validator wall (all validators)"
python3 "$CLI" --validator-wall
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
