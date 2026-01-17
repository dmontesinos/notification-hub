from typing import Optional
from .core.abstract_provider import AbstractProvider
from .providers.slack import SlackProvider
from .providers.jira import JiraProvider

class NotificationFactory:
    """
    Factory class to create notification providers.
    """

    @staticmethod
    def get_provider(provider_type: str, **kwargs) -> AbstractProvider:
        """
        Get a notification provider instance.

        Args:
            provider_type (str): The type of provider ('slack' or 'jira').
            **kwargs: Configuration arguments for the provider.

        Returns:
            AbstractProvider: An instance of the requested provider.

        Raises:
            ValueError: If the provider type is unsupported.
        """
        if provider_type.lower() == "slack":
            return SlackProvider(token=kwargs.get("token"))
        elif provider_type.lower() == "jira":
            return JiraProvider(
                server=kwargs.get("server"),
                email=kwargs.get("email"),
                token=kwargs.get("token")
            )
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")
