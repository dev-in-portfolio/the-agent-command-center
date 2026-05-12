#!/usr/bin/env bash
set -euo pipefail

echo "=============================================="
echo "  Interface Phase 2 TUI Operator Dashboard"
echo "  Safe Demo Script"
echo "  No deploy, no merge, no push, no secrets,"
echo "  no credentials, no command packet execution,"
echo "  no validator wall execution."
echo "=============================================="
echo ""

TUI="python3 12_tui/station_chief_tui.py"

echo "--- 1. Help ---"
$TUI --help
echo ""
echo ""

echo "--- 2. Snapshot (text) ---"
$TUI --snapshot
echo ""
echo ""

echo "--- 3. Snapshot (markdown) ---"
$TUI --snapshot --format markdown
echo ""
echo ""

echo "--- 4. Snapshot (json) ---"
$TUI --snapshot --format json
echo ""
echo ""

echo "--- 5. No-curses: start and quit ---"
printf "q\n" | $TUI --no-curses
echo ""
echo ""

echo "--- 6. Snapshot (compact) ---"
$TUI --snapshot --format compact
echo ""
echo ""

echo "--- 7. Snapshot (full) ---"
$TUI --snapshot --format full
echo ""
echo ""

echo "--- 8. Snapshot save (json) ---"
$TUI --snapshot --format json --save
echo ""
echo ""

echo "=============================================="
echo "  Demo complete."
echo ""
echo "  Validator wall is controlled and intentionally"
echo "  not run by this safe demo."
echo "  To run manually from TUI, open screen 4 and"
echo "  type RUN_VALIDATOR_WALL."
echo "=============================================="
