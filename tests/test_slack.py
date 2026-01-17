import pytest
from slack_sdk.errors import SlackApiError
from notification_hub.providers.slack import SlackProvider

def test_slack_send_notification_success(mock_slack_client):
    # Setup mock
    mock_instance = mock_slack_client.return_value
    mock_instance.chat_postMessage.return_value.data = {"ok": True, "ts": "123.456"}

    provider = SlackProvider(token="fake-token")
    result = provider.send_notification(destination="#general", message="Hello")

    mock_instance.chat_postMessage.assert_called_once_with(
        channel="#general",
        text="Hello"
    )
    assert result == {"ok": True, "ts": "123.456"}

def test_slack_send_notification_failure(mock_slack_client):
    mock_instance = mock_slack_client.return_value
    mock_instance.chat_postMessage.side_effect = SlackApiError(
        message="The request failed",
        response={"ok": False, "error": "channel_not_found"}
    )

    provider = SlackProvider(token="fake-token")
    
    with pytest.raises(SlackApiError):
        provider.send_notification(destination="#unknown", message="Hello")
