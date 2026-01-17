import pytest

@pytest.fixture
def mock_slack_client(mocker):
    return mocker.patch("notification_hub.providers.slack.WebClient")

@pytest.fixture
def mock_jira_client(mocker):
    return mocker.patch("notification_hub.providers.jira.JIRA")
