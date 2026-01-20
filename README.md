# Notification Hub

A centralized Python library and CLI tool designed to facilitate communication between your applications and external tools like Slack and Jira. It uses an abstract provider pattern, allowing for easy extension to other platforms (e.g., YouTrack) in the future.

## Features

- **Slack Integration**: Send notifications to channels effortlessly.
- **Jira Integration**:
    - Create, update, delete, and transition issues.
    - specialized CLI commands for extensive issue management.
    - Support for both Basic Auth (Email/Token) and Personal Access Tokens (PAT).
- **Extensible Architecture**: generic `AbstractProvider` interface.
- **CLI Interface**: Robust command-line tool for scripting and CI/CD integration.
- **Formatted Descriptions**: Utilities to format JSON data into readable Jira descriptions.

## Installation

You can install the package directly from the source:

```bash
pip install .
```

For development installations (editable mode):

```bash
pip install -e .[dev]
```

## Configuration

The library and CLI require credentials to interact with external services.

### Jira Credentials

You can provide credentials via CLI arguments or store your Jira API Token in a secret file for convenience (and security).

**Default Secret File:**
The CLI looks for a token file at: `config/secrets/jira_token` (relative to the project root).
If this file exists, you can omit the `--token` argument in CLI calls.

### Environment Variables

Currently, the tool relies primarily on explicit arguments or the secret file mentioned above. Future versions may support `JIRA_TOKEN` or `SLACK_TOKEN` environment variables.

## CLI Usage

The package exposes a CLI entry point.

Assuming you are running from the source root:
```bash
python src/cli.py <provider> <command> [args]
```

### Jira Commands (`jira`)

All Jira commands require connection details. You can pass them as arguments or rely on the `config/secrets/jira_token` file.

**Global Arguments:**
- `--server`: Jira Server URL
- `--user`: Jira Username/Email
- `--token`: API Token (optional if secret file exists)

#### Create Issue

```bash
python src/cli.py jira --server "https://my.jira.com" --user "me@company.com" create \
  --project "PROJ" \
  --summary "Issue Title" \
  --type "Task" \
  --description "Detailed description here"
```

#### Update Issue

```bash
python src/cli.py jira --server "..." --user "..." update \
  --key "PROJ-123" \
  --summary "Updated Title"
```

#### Delete Issue

```bash
python src/cli.py jira --server "..." --user "..." delete --key "PROJ-123"
```

#### Transition Issue

```bash
python src/cli.py jira --server "..." --user "..." transition --key "PROJ-123" --status "Done"
```

#### Other Tools

```bash
# Map Status
python src/cli.py jira map-status --status "backend_status" --file "mapping.json"

# Format Description
python src/cli.py jira format --description-data '{"key": "value"}'
```

### Slack Commands (`slack`)

Slack commands require a bot token, either via argument or `config/secrets/slack_token`.

**Global Arguments:**
- `--token`: Slack Bot Token (optional if secret file exists)

#### Send Message

```bash
python src/cli.py slack send --channel "#general" --message "Hello World"
```

## Advanced Features

### 1. Jira Description Formatting

The `format` command (and the corresponding Python utility `format_description`) allows you to generate standardized, rich-text Jira descriptions (Wiki Markup) from a structured JSON object. This is particularly useful for automated reporting.

**JSON Schema:**
```json
{
  "id": "INT-123",
  "description": "Main text description of the issue.",
  "etc_minutes": 120,
  "steps_url": "http://link-to-procedures.com",
  "impact_system": "Low",
  "impact_client": "None",
  "pr_links": [
    {"url": "http://github.com/org/repo/pull/1"},
    {"url": "http://github.com/org/repo/pull/2"}
  ],
  "additional_links": [
    {"url": "http://logs.com/123"}
  ]
}
```

**Usage:**
```bash
python src/cli.py jira format --description-data '{"id": "123", "description": "Test"}'
```

**Output (Jira Wiki Markup):**
```text
h2. 🔗 Intervention Details
See full details... [Open in Intervention Manager|http://localhost/#detail/123]

h2. ℹ️ General Info
*Description:* Test
*Duration:* N/A minutes
...
```

### 2. Status Mapping

The `map-status` command helps convert internal application statuses (which might vary) to a standardized set of Jira statuses. This decouples your internal logic from Jira's specific workflow names.

**Internal Fallback Mapping:**
If no file is provided, it uses a default mapping:
- `Creation` -> `Creation`
- `To Approve` -> `To Approve`
- `In Progress` -> `In Progress`
- ... (see `src/notification_hub/utils/jira_utils.py` for full list)

**Custom Mapping File (JSON):**
You can provide your own mapping:
```json
{
  "backend_pending": "To Do",
  "backend_processing": "In Progress",
  "backend_done": "Done"
}
```

**Usage:**
```bash
python src/cli.py jira map-status --status "backend_processing" --file "my_mapping.json"
# Output: {"status": "In Progress"}
```

## Troubleshooting

### "No se encontró Python" (Windows)
If you see this error, Python is likely not added to your system PATH or you have the Windows Store alias enabled without Python installed.
**Fix:**
- Install Python from python.org.
- Ensure "Add Python to PATH" is checked during installation.
- Or use `py` instead of `python` in your terminal.

### Authentication Errors (401/403)
- **Basic Auth**: Ensure you are using your **Email** and an **API Token** (not your password). Atlassian requires API Tokens for basic auth.
- **Token Auth**: If using Personal Access Tokens (PAT, common in Jira Data Center), ensure you set `--auth-method token`.

### "Secret file not found"
If you omit `--token`, the tool looks in `config/secrets/jira_token` (or `slack_token`). Ensure these files exist and contain *only* the token string (no newlines or spaces).

## Python Library Usage

You can use the providers directly in your Python code.

### Jira Provider

```python
from notification_hub.providers.jira import JiraProvider

jira = JiraProvider(
    server="https://your-domain.atlassian.net",
    email="user@example.com",
    token="your-api-token"
)

# Create an issue
issue = jira.create_issue(
    project="PROJ",
    summary="New Bug Found",
    description="Steps to reproduce...",
    issue_type="Bug"
)
print(f"Created issue: {issue['key']}")

# Transition an issue
jira.transition_issue(key="PROJ-123", transition_id="31")
```

### Slack Provider

```python
from notification_hub.providers.slack import SlackProvider

slack = SlackProvider(token="xoxb-your-bot-token")

slack.send_notification(
    destination="#deployments",
    message="Deployment started successfully!"
)
```

### Using the Factory

The `NotificationFactory` allows for dynamic provider instantiation.

```python
from notification_hub.factory import NotificationFactory

# Get a Jira provider
jira = NotificationFactory.get_provider("jira", 
    server="...", 
    email="...", 
    token="..."
)

# Get a Slack provider
slack = NotificationFactory.get_provider("slack", token="...")
```

## Running Tests

This project uses `pytest` for testing.

1. Install test dependencies:
   ```bash
   pip install .[dev]
   ```

2. Run tests:
   ```bash
   pytest
   ```
