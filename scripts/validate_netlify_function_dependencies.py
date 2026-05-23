import json
import os
import re
import subprocess
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGE_JSON = os.path.join(ROOT, "package.json")
PACKAGE_LOCK = os.path.join(ROOT, "package-lock.json")
FUNCTIONS_DIR = os.path.join(ROOT, "netlify", "functions")
BROWSER_JS_ROOTS = [
    os.path.join(ROOT, "13_web_dashboard"),
    os.path.join(ROOT, "11_interface"),
    os.path.join(ROOT, "12_tui"),
]


def fail(message: str) -> None:
    print(f"FAILED: {message}")
    sys.exit(1)


def load_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        fail(f"Missing file: {os.path.relpath(path, ROOT)}")
    except Exception as exc:
        fail(f"Invalid JSON in {os.path.relpath(path, ROOT)}: {exc}")


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def walk_js_files(root_dir: str):
    for current_root, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [name for name in dirnames if name not in {".git", "node_modules"}]
        for filename in filenames:
            if filename.endswith(".js"):
                yield os.path.join(current_root, filename)


def git_output(*args: str) -> str:
    return subprocess.check_output(["git", "-C", ROOT, *args], text=True).strip()


if not os.path.isfile(PACKAGE_JSON):
    fail("package.json does not exist at repo root")
if not os.path.isfile(PACKAGE_LOCK):
    fail("package-lock.json does not exist at repo root")

package_json = load_json(PACKAGE_JSON)
dependencies = package_json.get("dependencies", {})
if "@supabase/supabase-js" not in dependencies:
    fail("package.json dependencies is missing @supabase/supabase-js")

staged_node_modules = git_output("diff", "--cached", "--name-only", "--", "node_modules")
tracked_node_modules = git_output("ls-files", "--", "node_modules")
if staged_node_modules:
    fail("node_modules has staged entries")
if tracked_node_modules:
    fail("node_modules is tracked in git")

function_imports = []
for file_path in walk_js_files(FUNCTIONS_DIR):
    content = read_text(file_path)
    if "@supabase/supabase-js" in content:
        function_imports.append(os.path.relpath(file_path, ROOT))

if not function_imports:
    fail("No Netlify functions import or require @supabase/supabase-js")

for file_path in function_imports:
    if dependencies.get("@supabase/supabase-js") is None:
        fail(f"{file_path} imports @supabase/supabase-js but package.json does not declare it")

try:
    resolved = subprocess.check_output(
        [
            "node",
            "-e",
            "require.resolve('@supabase/supabase-js'); console.log('SUPABASE_JS_RESOLVE_PASS')",
        ],
        text=True,
        cwd=ROOT,
    ).strip()
except subprocess.CalledProcessError as exc:
    fail(f"node resolution failed: {exc}")

if "SUPABASE_JS_RESOLVE_PASS" not in resolved:
    fail("node resolution check did not print SUPABASE_JS_RESOLVE_PASS")

for file_path in walk_js_files(FUNCTIONS_DIR):
    try:
        subprocess.check_call(["node", "--check", file_path], cwd=ROOT)
    except subprocess.CalledProcessError as exc:
        fail(f"node --check failed for {os.path.relpath(file_path, ROOT)}: {exc}")

unsafe_script_patterns = (
    "deploy",
    "runtime activation",
    "activate-all",
    "shell",
    "curl",
    "bash",
    "sh ",
    "netlify deploy",
)
for script_name, script_value in package_json.get("scripts", {}).items():
    normalized = f"{script_name} {script_value}".lower()
    if any(pattern in normalized for pattern in unsafe_script_patterns):
        fail(f"Unsafe script detected in package.json scripts: {script_name}")

browser_js_files = []
for browser_root in BROWSER_JS_ROOTS:
    if not os.path.isdir(browser_root):
        continue
    for file_path in walk_js_files(browser_root):
        if "/netlify/functions/" in file_path.replace("\\", "/"):
            continue
        browser_js_files.append(file_path)

for file_path in browser_js_files:
    content = read_text(file_path)
    if "SUPABASE_SERVICE_ROLE_KEY" in content:
        fail(f"Browser JS exposes SUPABASE_SERVICE_ROLE_KEY: {os.path.relpath(file_path, ROOT)}")
    if "@supabase/supabase-js" in content and "service role" in content.lower():
        fail(f"Browser JS mixes @supabase/supabase-js with service role logic: {os.path.relpath(file_path, ROOT)}")

print("NETLIFY_FUNCTION_DEPENDENCY_VALIDATION_PASS")
