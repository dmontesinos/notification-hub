from typing import Any, Dict
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from ..core.abstract_provider import AbstractProvider

class SlackProvider(AbstractProvider):
    """
    Provider for sending notifications via Slack.
    """

    def __init__(self, token: str):
        """
        Initialize the Slack provider.

        Args:
            token (str): The Slack Bot User OAuth Token.
        """
        self.client = WebClient(token=token)

    def send_notification(self, destination: str, message: str, **kwargs) -> Dict[str, Any]:
        """
        Send a message to a Slack channel.

        Args:
            destination (str): The channel name (e.g., "#general") or ID.
            message (str): The text message to send.
            **kwargs: Additional arguments to pass to `chat_postMessage`.

        Returns:
            Dict[str, Any]: The API response.

        Raises:
            SlackApiError: If the request fails.
        """
        try:
            response = self.client.chat_postMessage(
                channel=destination,
                text=message,
                **kwargs
            )
            return response.data
        except SlackApiError as e:
            # You might want to wrap or log this error differently in a real app
            raise e
