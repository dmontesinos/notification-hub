from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class AbstractProvider(ABC):
    """
    Abstract base class for all notification providers.
    """

    @abstractmethod
    def send_notification(self, destination: str, message: str, **kwargs) -> Dict[str, Any]:
        """
        Send a notification to the specified destination.

        Args:
            destination (str): Where to send the notification (e.g., Slack channel, email address).
            message (str): The content of the notification.
            **kwargs: Additional provider-specific arguments.

        Returns:
            Dict[str, Any]: The response from the provider.
        """
        pass
