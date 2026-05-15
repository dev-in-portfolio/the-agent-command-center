import os
from pathlib import Path
import json

def check():
    dist_dir = Path("13_web_dashboard/dist")
    if not dist_dir.exists():
        raise SystemExit("FAIL: dist dir not found")
        
    index = dist_dir / "index.html"
    if not index.exists():
        raise SystemExit("FAIL: index.html not found")
        
    js = dist_dir / "static/dashboard.js"
    css = dist_dir / "static/dashboard.css"
    if not js.exists() or not css.exists():
        raise SystemExit("FAIL: JS/CSS not found")
        
    index_text = index.read_text(encoding="utf-8")
    
    required_strings = [
        "Original +1E",
        "Backend Implementation Gate",
        "Build Ticket Generator",
        "BACKEND IMPLEMENTATION GATE",
        "BUILD TICKET GENERATOR",
        "IMPLEMENTATION PLANNING ONLY",
        "COPYABLE CODEX PROMPTS",
        "READINESS ONLY",
        "NO LIVE AUTOMATION",
        "NO EXECUTION",
        "NO MUTATION",
        "NO BACKEND WRITES",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "READY_FOR_BACKEND_IMPLEMENTATION_PLANNING_ONLY",
        "PLAN_PLUS2A_NEXT",
        "DO_NOT_ENABLE_REAL_AUTOMATION",
        "Backend Implementation Gate Overview Panel",
        "Future Phase Ticket Map Panel",
        "Dependency Prerequisite Panel",
        "Build Ticket Detail Panel",
        "Codex Prompt Generator Panel",
        "Implementation Gate Status Panel",
        "Ticket Validator Requirements Panel",
        "Ticket Report Requirements Panel",
        "Rollback / No-Go Ticket Policy Panel",
        "Backend Build Readiness Summary Panel",
        "+2A", "Backend Auth Foundation",
        "+2B", "Persistent Request Storage",
        "+2C", "Immutable Audit Log",
        "+2D", "Approval Gate Storage",
        "+2E", "Server-Side Dry-Run Engine",
        "+2F", "Queue / Job Runner",
        "+2G", "Mutation Gateway",
        "+2H", "GitHub / Netlify Integration Adapters",
        "+2I", "Rollback / No-Go Enforcement",
        "+2J", "Production Hardening & Monitoring",
        "Copy selected build ticket",
        "Copy selected Codex prompt",
        "Copy full backend implementation roadmap",
        "Copy dependency prerequisite map",
        "Copy validator requirements matrix",
        "Copy report requirements matrix",
        "Copy rollback/no-go ticket policy",
        "Copy backend build readiness summary"
    ]
    
    for req in required_strings:
        if req not in index_text:
            raise SystemExit(f"FAIL: Missing from index.html: {req}")
            
    forbidden_controls = [
        "type=\"submit\"",
        "<button>Submit</button>",
        "<button>Save</button>",
        "<button>Queue</button>",
        "<button>Execute</button>",
        "<button>Deploy</button>",
        "<button>Merge</button>",
        "<button>Push</button>",
        "<button>Create PR</button>",
        "<button>Start automation</button>",
        "<button>Approve live action</button>",
        "<button>Trigger workflow</button>",
        "<button>Create endpoint</button>",
        "<button>Start +2A</button>"
    ]
    for req in forbidden_controls:
        if req in index_text:
            raise SystemExit(f"FAIL: Forbidden control found: {req}")

    js_text = js.read_text(encoding="utf-8")
    
    forbidden_js = [
        "localStorage",
        "sessionStorage",
        "document.cookie",
        "indexedDB",
        "IndexedDB",
        "method: \"POST\"",
        "method:'POST'",
        "method: \"PUT\"",
        "method:'PUT'",
        "method: \"PATCH\"",
        "method:'PATCH'",
        "method: \"DELETE\"",
        "method:'DELETE'",
        "api.github.com",
        "api.netlify.com",
        "WebSocket",
        "EventSource",
        "sendBeacon",
        "eval(",
        "Function(",
        "import(",
        "Blob",
        "URL.createObjectURL",
        "FileReader"
    ]
    for req in forbidden_js:
        if req in js_text:
            raise SystemExit(f"FAIL: Forbidden JS found: {req}")
            
    # Check allowed fetches
    import re
    fetches = re.findall(r'fetch\(["\']([^"\']+)["\']', js_text)
    allowed_fetch = {
        "/api/health",
        "/api/status",
        "/api/backend-manifest",
        "./status_snapshot.json",
        "./phase4d_identity_schema.json",
        "./phase4d_action_schema.json",
        "./phase4d_audit_schema.json",
        "./phase4d_approval_schema.json",
        "./phase4d_risk_model.json",
        "./original_plus1b_contract_schemas.json",
        "./original_plus1c_readiness_qa_model.json",
        "./original_plus1d_backend_boundary_model.json",
        "./original_plus1e_backend_build_tickets.json"
    }
    for f in fetches:
        if f not in allowed_fetch:
            raise SystemExit(f"FAIL: Unauthorized fetch: {f}")

    reports = [
        "original_plus1e_backend_implementation_gate_report.md",
        "original_plus1e_build_ticket_generator_report.md",
        "original_plus1e_future_phase_ticket_map_report.md",
        "original_plus1e_dependency_prerequisite_report.md",
        "original_plus1e_codex_prompt_generator_report.md",
        "original_plus1e_validator_requirements_report.md",
        "original_plus1e_report_requirements_report.md",
        "original_plus1e_rollback_no_go_policy_report.md",
        "original_plus1e_design_report.md",
        "original_plus1e_safety_report.md",
        "original_plus1e_acceptance_report.md"
    ]
    
    for report in reports:
        report_path = Path(f"09_exports/original_plus1/{report}")
        if not report_path.exists():
            raise SystemExit(f"FAIL: Missing report {report}")
            
    acc_report = Path("09_exports/original_plus1/original_plus1e_acceptance_report.md").read_text(encoding="utf-8")
    req_acc = [
        "PASS_WITH_HIGH_CONFIDENCE",
        "IMPLEMENTATION_PLANNING_ONLY",
        "NOT_READY_FOR_REAL_AUTOMATION",
        "PLAN_PLUS2A_NEXT"
    ]
    for r in req_acc:
        if r not in acc_report:
            raise SystemExit(f"FAIL: Missing from acceptance report: {r}")

    print("ORIGINAL_PLUS1E_BACKEND_IMPLEMENTATION_GATE_VALIDATION_PASS")

if __name__ == "__main__":
    check()
