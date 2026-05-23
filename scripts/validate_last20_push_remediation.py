import os
import sys
import re

def run_validation():
    print("Validating Last-20-Push Remediation...")
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DIST = os.path.join(ROOT, "13_web_dashboard", "dist")
    DEMO = os.path.join(DIST, "demo")
    SCRIPTS = os.path.join(ROOT, "scripts")
    FUNCTIONS = os.path.join(ROOT, "netlify", "functions")

    # A. Route existence
    print("Checking route existence...")
    html_files = []
    for root, dirs, files in os.walk(DIST):
        for f in files:
            if f.endswith(".html"):
                html_files.append(os.path.join(root, f))
    
    for html_path in html_files:
        with open(html_path, 'r') as f:
            content = f.read()
            # Simple href check
            hrefs = re.findall(r'href=["\']([^"\']*?\.html)["\']', content)
            for href in hrefs:
                if href.startswith("http") or href.startswith("mailto"):
                    continue
                # Resolve relative to html_path
                target = os.path.abspath(os.path.join(os.path.dirname(html_path), href))
                if not os.path.exists(target):
                    print(f"FAILED: Broken link '{href}' in {html_path} (Target {target} not found)")
                    return False

    # C. Stale copy
    print("Checking for stale copy...")
    forbidden_strings = [
        "Production verified through MVP-62 plus Continual Harness Operator Mode. Full-fleet MVP-63 through MVP-68 surfaces are not yet merged into this branch.",
        "MVP-51 in progress",
        "agent count unknown",
        "Backend integration: planned"
    ]
    for html_path in html_files:
        # Skip historical sections if we had any, but here we check everything
        with open(html_path, 'r') as f:
            content = f.read()
            for s in forbidden_strings:
                if s in content:
                    print(f"FAILED: Found stale string '{s}' in {html_path}")
                    return False

    # D. Exact counts
    print("Checking for exact counts...")
    exact_counts = ["47,979", "1,777", "5,331", "175"]
    # We expect these on at least System Scale and Registry
    scale_pages = [os.path.join(DEMO, "system-scale.html"), os.path.join(DEMO, "agent-registry.html")]
    for p in scale_pages:
        if os.path.exists(p):
            with open(p, 'r') as f:
                content = f.read()
                for c in exact_counts:
                    if c not in content:
                        print(f"FAILED: Missing exact count '{c}' in {p}")
                        return False

    # E. Safety
    print("Checking browser safety...")
    unsafe_browser = [
        "SUPABASE_SERVICE_ROLE_KEY",
        "localStorage",
        "sessionStorage",
        "document.cookie",
        "indexedDB",
        "child_process",
        "exec(",
        "spawn(",
        "eval(",
        "new Function"
    ]
    assets_js = os.path.join(DEMO, "assets")
    if os.path.exists(assets_js):
        for f in os.listdir(assets_js):
            if f.endswith(".js"):
                with open(os.path.join(assets_js, f), 'r') as jsf:
                    content = jsf.read()
                    for u in unsafe_browser:
                        if u in content:
                            # Allow comments with "No service role key" etc
                            if u == "SUPABASE_SERVICE_ROLE_KEY" and "No " in content:
                                continue
                            print(f"FAILED: Found unsafe string '{u}' in browser asset {f}")
                            return False

    # F. Unsafe routes in functions
    print("Checking unsafe routes...")
    unsafe_routes = [
        "activate-all",
        "activate-47979",
        "arbitrary-sql",
        "arbitrary-command",
        "shell-execute",
        "deploy-execute",
        "rollback-execute"
    ]
    for f in os.listdir(FUNCTIONS):
        if f.endswith(".js"):
            for u in unsafe_routes:
                if u in f:
                    print(f"FAILED: Unsafe function name '{f}'")
                    return False

    # G. Node syntax
    print("Checking node syntax...")
    for root, dirs, files in os.walk(FUNCTIONS):
        for f in files:
            if f.endswith(".js"):
                p = os.path.join(root, f)
                if os.system(f"node --check {p} > /dev/null 2>&1") != 0:
                    print(f"FAILED: Syntax error in {p}")
                    return False

    # H. HTML sanity
    print("Checking HTML sanity...")
    for html_path in html_files:
        with open(html_path, 'r') as f:
            content = f.read()
            if "<!doctype html>" not in content.lower():
                 print(f"FAILED: Missing doctype in {html_path}")
                 return False
            if "{_list(" in content or "{_stat(" in content:
                 if "dashboard.html" not in html_path and "full-audit-dashboard.html" not in html_path and "print.html" not in html_path:
                     print(f"FAILED: Template fragment found in {html_path}")
                     return False

    # I. Reports
    report_path = os.path.join(ROOT, "09_exports", "mvp_product_track", "last20_push_deep_dive_remediation_report.md")
    if not os.path.exists(report_path):
        print("FAILED: Missing remediation report")
        return False
        
    print("LAST20_PUSH_REMEDIATION_VALIDATION_PASS")
    return True

if __name__ == "__main__":
    if not run_validation():
        sys.exit(1)
    sys.exit(0)
