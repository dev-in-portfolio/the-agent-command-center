import os
import sys
import re

def run_validation():
    print("Validating MVP-68 Homepage Alignment...")
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DIST = os.path.join(ROOT, "13_web_dashboard", "dist")
    DEMO = os.path.join(DIST, "demo")
    
    # Files exist
    files = [
        os.path.join(DIST, "index.html"),
        os.path.join(DEMO, "index.html"),
        os.path.join(DEMO, "runtime-fleet.html"),
        os.path.join(DEMO, "full-fleet-load-test.html"),
        os.path.join(DEMO, "observability-command-wall.html"),
        os.path.join(DEMO, "executive-control-room.html"),
        os.path.join(DEMO, "enterprise-pilot-room.html"),
        os.path.join(DEMO, "enterprise-pilot-packet.html"),
        os.path.join(DEMO, "assets", "demo.css")
    ]
    for f in files:
        if not os.path.exists(f):
            print(f"FAILED: Missing file {f}")
            return False
            
    # Root checks
    with open(os.path.join(DIST, "index.html"), 'r') as f:
        root_content = f.read()
        
    root_checks = [
        "MVP-68 — Enterprise Pilot Packet Exporter",
        "47,979",
        "1,777",
        "5,331",
        "175",
        "Executive Control Room",
        "Enterprise Pilot Packet",
        "Full 47,979-Agent Runtime Fleet",
        "Full-Fleet Load Test",
        "Full-Fleet Observability Command Wall",
        "Enterprise Pilot Room",
        "Raw activate all: disabled",
        "Command execution: disabled",
        "Deploy execution: disabled",
        "Rollback execution: disabled",
        "Alert sending: disabled",
        "Shell execution: disabled",
        "Arbitrary SQL: disabled"
    ]
    for check in root_checks:
        if check not in root_content:
            print(f"FAILED: Root index missing '{check}'")
            return False
            
    # Demo Hub checks
    with open(os.path.join(DEMO, "index.html"), 'r') as f:
        demo_content = f.read()
        
    demo_checks = [
        "MVP-68 — Enterprise Pilot Packet Exporter",
        "./runtime-fleet.html",
        "./full-fleet-load-test.html",
        "./observability-command-wall.html",
        "./executive-control-room.html",
        "./enterprise-pilot-room.html",
        "./enterprise-pilot-packet.html"
    ]
    for check in demo_checks:
        if check not in demo_content:
            print(f"FAILED: Demo Hub missing '{check}'")
            return False
            
    # Stale copy check
    stale_copy = [
        "MVP-51 not started",
        "The next runtime phase has not started",
        "agent count unknown",
        "Backend integration: planned",
        "Not writing to Supabase"
    ]
    # We check root and demo hub primarily
    for html in [os.path.join(DIST, "index.html"), os.path.join(DEMO, "index.html")]:
        with open(html, 'r') as f:
            content = f.read()
            for s in stale_copy:
                if s in content:
                    print(f"FAILED: Found stale string '{s}' in {html}")
                    return False
                    
    # Route validation
    print("Checking route existence...")
    # Get all hrefs from root and demo hub
    for html in [os.path.join(DIST, "index.html"), os.path.join(DEMO, "index.html")]:
        with open(html, 'r') as f:
            content = f.read()
            hrefs = re.findall(r'href=["\']([^"\']*?\.html)["\']', content)
            for href in hrefs:
                if href.startswith("http") or href.startswith("mailto"):
                    continue
                # Resolve relative
                target = os.path.abspath(os.path.join(os.path.dirname(html), href))
                if not os.path.exists(target):
                    print(f"FAILED: Broken link '{href}' in {html}")
                    return False

    # CSS validation
    with open(os.path.join(DEMO, "assets", "demo.css"), 'r') as f:
        css = f.read()
        if "box-sizing: border-box;" not in css:
            print("FAILED: demo.css missing box-sizing")
            return False
        if "overflow-wrap: anywhere;" not in css:
            print("FAILED: demo.css missing overflow-wrap")
            return False
            
    # Safety validation
    assets_js = os.path.join(DEMO, "assets")
    for f in os.listdir(assets_js):
        if f.endswith(".js"):
            with open(os.path.join(assets_js, f), 'r') as jsf:
                content = jsf.read()
                if "SUPABASE_SERVICE_ROLE_KEY" in content and "No " not in content:
                    print(f"FAILED: Unsafe string 'SUPABASE_SERVICE_ROLE_KEY' in {f}")
                    return False

    print("MVP68_HOMEPAGE_ALIGNMENT_VALIDATION_PASS")
    return True

if __name__ == "__main__":
    if not run_validation():
        sys.exit(1)
    sys.exit(0)
