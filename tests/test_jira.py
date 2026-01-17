import pytest
from jira import JIRAError
from notification_hub.providers.jira import JiraProvider

def test_jira_send_notification_success(mock_jira_client):
    # Setup mock
    mock_instance = mock_jira_client.return_value
    mock_issue = mock_instance.create_issue.return_value
    mock_issue.key = "PROJ-123"
    mock_issue.id = "10001"
    mock_issue.self = "http://jira/issue/10001"

    provider = JiraProvider(server="http://jira", email="user", token="token")
    result = provider.send_notification(destination="PROJ", message="Summary of issue")

    mock_instance.create_issue.assert_called_once()
    # Check arguments passed to create_issue
    call_args = mock_instance.create_issue.call_args[1]['fields']
    assert call_args['project']['key'] == "PROJ"
    assert call_args['summary'] == "Summary of issue"
    assert call_args['issuetype']['name'] == "Task"

    assert result['key'] == "PROJ-123"

def test_jira_create_issue_explicit_success(mock_jira_client):
    mock_instance = mock_jira_client.return_value
    mock_issue = mock_instance.create_issue.return_value
    mock_issue.key = "PROJ-456"
    mock_issue.id = "10002"
    mock_issue.self = "http://jira/issue/10002"

    provider = JiraProvider(server="http://jira", email="user", token="token")
    result = provider.create_issue(
        project="PROJ",
        summary="Bug report",
        description="Detailed description",
        issue_type="Bug"
    )

    call_args = mock_instance.create_issue.call_args[1]['fields']
    assert call_args['project']['key'] == "PROJ"
    assert call_args['summary'] == "Bug report"
    assert call_args['description'] == "Detailed description"
    assert call_args['issuetype']['name'] == "Bug"

    assert result['key'] == "PROJ-456"

def test_jira_send_notification_failure(mock_jira_client):
    mock_instance = mock_jira_client.return_value
    mock_instance.create_issue.side_effect = JIRAError(status_code=400, text="Bad Request")

    provider = JiraProvider(server="http://jira", email="user", token="token")

    with pytest.raises(JIRAError):
        provider.send_notification(destination="PROJ", message="Fail")
