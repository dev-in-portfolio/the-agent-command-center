SCREENS = {
    "1": "dashboard",
    "2": "action_registry",
    "3": "artifact_inspector",
    "4": "validator_wall",
    "5": "command_packet_prep",
    "6": "branch_review_prep",
    "7": "approval_ledger",
    "8": "help",
}
KEY_TO_SCREEN = {k: v for k, v in SCREENS.items()}
KEY_TO_SCREEN["q"] = "quit"
KEY_TO_SCREEN["r"] = "refresh"
KEY_TO_SCREEN["h"] = "help"

FORBIDDEN_KEYS = []
FORBIDDEN_SCREEN_NAMES = [
    "deploy", "merge", "push", "official_mutation",
    "repo2_mutation", "repo3_mutation", "secrets",
    "credentials", "free_shell",
]

HELP_TEXT = """Available Keys:
  q = quit
  1 = Main Dashboard
  2 = Action Registry
  3 = Artifact Inspector
  4 = Validator Wall
  5 = Command Packet Prep
  6 = Branch Review Prep
  7 = Approval Ledger
  8 = Help / Safety Rules
  r = Refresh current screen
  h = Help

Locked / Forbidden (no key binding):
  deploy, merge, push
  official/repo2/repo3 mutation
  secrets, credentials
  free-form shell
"""


def is_valid_key(key):
    return key in KEY_TO_SCREEN


def get_screen_for_key(key):
    return KEY_TO_SCREEN.get(key, None)
