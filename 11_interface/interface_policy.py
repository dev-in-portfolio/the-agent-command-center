SAFE_ACTIONS = [
    "show_status",
    "list_artifacts",
    "show_locked_actions",
    "show_summaries",
]

CONTROLLED_ACTIONS = [
    "run_validator_wall",
    "generate_session_report",
    "prepare_command_packet",
]

LOCKED_ACTIONS = [
    "mutate_official_repo",
    "mutate_repo_2",
    "mutate_repo_3",
    "deploy",
    "use_secrets",
    "use_credentials",
    "read_environment",
    "inspect_credential_stores",
    "promote_to_official",
    "open_official_pr",
    "merge_official",
    "production_mutation",
    "uncontrolled_autonomy",
    "free_form_shell",
]

LOCKED_ACTION_LABELS = {
    "mutate_official_repo": "Mutate official repo (agent-command-center)",
    "mutate_repo_2": "Mutate agent-command-center-2",
    "mutate_repo_3": "Mutate agent-command-center-3",
    "deploy": "Deploy to any environment",
    "use_secrets": "Access or use secrets",
    "use_credentials": "Access or use credentials",
    "read_environment": "Read environment variables",
    "inspect_credential_stores": "Inspect ~/.ssh, ~/.config, token stores",
    "promote_to_official": "Promote lab work to official",
    "open_official_pr": "Open PR against official repo",
    "merge_official": "Merge into official repo",
    "production_mutation": "Mutate production systems",
    "uncontrolled_autonomy": "Unrestricted autonomous operation",
    "free_form_shell": "Free-form shell execution from user input",
}
