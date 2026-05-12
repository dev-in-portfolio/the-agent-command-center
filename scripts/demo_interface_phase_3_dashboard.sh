#!/usr/bin/env bash
set -euo pipefail

echo "SAFE DEMO ONLY"
python3 13_web_dashboard/build_phase3_dashboard.py --help
python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-json
python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-markdown
python3 13_web_dashboard/build_phase3_dashboard.py --snapshot-summary
python3 13_web_dashboard/build_phase3_dashboard.py --validate-only
python3 13_web_dashboard/build_phase3_dashboard.py

echo "dashboard path: 13_web_dashboard/dist/index.html"
echo "dashboard data: 13_web_dashboard/dist/dashboard_data.json"
echo "print page: 13_web_dashboard/dist/print.html"
echo "open locally in browser"
echo "no server required"
echo "validator commands:"
echo "python3 scripts/validate_interface_phase_3_dashboard.py"
echo "python3 scripts/validate_interface_phase_3_e2e.py"
echo "no deploy"
echo "no merge"
echo "no push"
echo "no PR creation"
echo "no packet execution"
echo "no secrets"
echo "no credentials"
echo "no network calls"
