import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from product_runtime.request_lifecycle import RequestLifecycleOrchestrator, load_demo_fixture


def main():
    runtime = RequestLifecycleOrchestrator()
    result = runtime.run(load_demo_fixture())
    print(json.dumps(result, indent=2, sort_keys=False))


if __name__ == "__main__":
    main()
