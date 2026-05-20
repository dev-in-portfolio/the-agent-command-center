import os
import re
from pathlib import Path
import sys

def validate():
    netlify_toml = Path("netlify.toml")
    dist_dir = Path("13_web_dashboard/dist")
    index_html = dist_dir / "index.html"
    demo_index = dist_dir / "demo/index.html"
    simulator = dist_dir / "demo/simulator.html"
    agent_registry = dist_dir / "demo/agent-registry.html"
    system_scale = dist_dir / "demo/system-scale.html"
    redirects = dist_dir / "_redirects"
    headers = dist_dir / "_headers"

    required_files = [netlify_toml, index_html, demo_index, simulator, agent_registry, redirects, headers]
    for f in required_files:
        if not f.exists():
            print(f"MISSING: {f}")
            return False

    with open(netlify_toml, "r") as f:
        toml_content = f.read()
        if 'publish = "13_web_dashboard/dist"' not in toml_content:
            print("INVALID_NETLIFY_PUBLISH_PATH")
            return False

    with open(index_html, "r") as f:
        index_content = f.read()
        
    root_markers = [
        "Command Center Launchpad",
        "Premium Stakeholder Demo",
        "Open Premium Demo Hub",
        "Runnable Static Simulator",
        "Open Static Simulator",
        "./demo/",
        "./demo/simulator.html",
        "./demo/agent-registry.html",
        "Backend/Supabase readiness architecture",
        "Live backend runtime disabled",
        "MVP-50",
        "MVP-51 not started"
    ]
    for m in root_markers:
        if m not in index_content:
            print(f"MISSING_ROOT_MARKER: {m}")
            return False
            
    with open(system_scale, "r") as f:
        system_scale_content = f.read()
        
    scale_markers = [
        "47,979",
        "1,777",
        "Exact agent count",
        "Exact department count",
        "org_chart_export.json"
    ]
    for m in scale_markers:
        if m not in system_scale_content:
            print(f"MISSING_SCALE_MARKER: {m}")
            return False

    with open(agent_registry, "r") as f:
        registry_content = f.read()
        
    registry_markers = [
        "Exact agent count: 47,979",
        "Exact department count: 1,777",
        "Live runtime agents enabled: 0",
        "Runtime activation not started"
    ]
    for m in registry_markers:
        if m not in registry_content:
            print(f"MISSING_REGISTRY_MARKER: {m}")
            return False

    with open(simulator, "r") as f:
        simulator_content = f.read()
        
    simulator_markers = [
        "Command Center Sandbox Simulator",
        "Safe content-review request",
        "High-risk deploy request",
        "Incident rollback request",
        "Approval denied request",
        "Auth",
        "Storage",
        "Audit",
        "Approval",
        "Dry Run",
        "Queue",
        "Human Review",
        "Monitoring Readiness",
        "STATIC SANDBOX",
        "LIVE BACKEND RUNTIME DISABLED"
    ]
    for m in simulator_markers:
        if m not in simulator_content:
            print(f"MISSING_SIMULATOR_MARKER: {m}")
            return False

    # Stale checks for Root
    stale_root_markers = [
        "Backend integration: planned",
        "backend integration is planned",
        "old jump list ending around MVP-23 as the main visible navigation",
        "Next milestone: 51 (In Progress)",
        "MVP-51 in progress"
    ]
    for m in stale_root_markers:
        if m in index_content:
            print(f"STALE_ROOT_MARKER_FOUND: {m}")
            return False
            
    if "Current build: static preview" in index_content and "Hosting readiness: static hosting ready" not in index_content:
        print("STALE_ROOT_MARKER_FOUND: Current build: static preview (old version)")
        return False

    # Check generated HTML for all pages
    html_files = [index_html] + list((dist_dir / "demo").rglob("*.html"))
    for html_file in html_files:
        with open(html_file, "r") as f:
            content = f.read()
            # Strip script tags to avoid checking embedded JSON
            visible_content = re.sub(r'<script\b[^>]*>(.*?)</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
            
            stale_global = [
                "{_list(",
                "{_stat(",
                "{_badge("
            ]
            for m in stale_global:
                if m in visible_content:
                    print(f"STALE_HTML_MACRO_OR_NEWLINE_FOUND: {m} in {html_file}")
                    return False
            # Check for visible "{_"
            if "{_" in visible_content:
                print(f"VISIBLE_MACRO_START_FOUND in {html_file}")
                return False

    # Internal links resolution
    href_pattern = re.compile(r'href="([^"]+)"')
    with open(redirects, "r") as f:
        redirects_content = f.read()
        redirect_aliases = []
        for line in redirects_content.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split()
                if len(parts) >= 1:
                    redirect_aliases.append(parts[0])

    for html_file in html_files:
        with open(html_file, "r") as f:
            content = f.read()
            for match in href_pattern.finditer(content):
                link = match.group(1)
                if link.startswith("http") or link.startswith("mailto:") or link.startswith("javascript:") or link.startswith("#") or link.startswith("data:"):
                    continue
                # Resolve absolute path
                if link.startswith("/"):
                    link_path = link.split("?")[0].split("#")[0]
                    if link_path in redirect_aliases:
                        continue
                    
                    target = dist_dir / link_path.lstrip("/")
                    if target.is_dir() and (target / "index.html").exists():
                        continue
                    if not target.exists():
                        print(f"BROKEN_ABSOLUTE_LINK: {link} in {html_file}")
                        return False
                else:
                    # Relative path
                    link_path = link.split("?")[0].split("#")[0]
                    if not link_path: # e.g. "?query=1" or ""
                        continue
                    
                    target = (html_file.parent / link_path).resolve()
                    if not target.exists():
                        if target.is_dir() and (target / "index.html").exists():
                            continue
                        
                        # Calculate relative path to root to check against aliases
                        try:
                            rel_to_root = target.relative_to(dist_dir.resolve())
                            alias_path = "/" + str(rel_to_root).replace("\\", "/")
                            if alias_path in redirect_aliases:
                                continue
                        except ValueError:
                            # If target is outside dist_dir, it's clamped to root by browsers
                            continue
                            
                        print(f"BROKEN_RELATIVE_LINK: {link} in {html_file} -> {target}")
                        return False

    print("NETLIFY_CURRENT_MASTER_PUBLISH_AFTER_MVP50_VALIDATION_PASS")
    return True

if __name__ == "__main__":
    if not validate():
        sys.exit(1)
