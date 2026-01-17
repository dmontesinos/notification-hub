# Notification Hub

A centralized Python library to facilitate communication between your applications and external tools like Slack and Jira.

## Features

- **Slack Integration**: Send messages to channels easily.
- **Jira Integration**: Create issues in Jira projects.
- **Extensible Architecture**: Built with an abstract provider pattern to easily add new integrations (e.g., YouTrack) in the future.

## Installation

```bash
pip install .
```

## Usage

### Slack

```python
from notification_hub.providers.slack import SlackProvider

slack = SlackProvider(token="xoxb-your-token")
slack.send_notification(channel="#general", message="Hello from Notification Hub!")
```

### Jira

```python
from notification_hub.providers.jira import JiraProvider

jira = JiraProvider(
    server="https://your-domain.atlassian.net",
    email="user@example.com",
    token="api-token"
)
jira.create_issue(
    project="PROJ",
    summary="New issue from Hub",
    description="This issue was created automatically.",
    issue_type="Task"
)
```
