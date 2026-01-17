from typing import Any, Dict
from jira import JIRA, JIRAError
from ..core.abstract_provider import AbstractProvider

class JiraProvider(AbstractProvider):
    """
    Provider for interacting with Jira.
    """

    def __init__(self, server: str, email: str, token: str):
        """
        Initialize the Jira provider.

        Args:
            server (str): The Jira server URL (e.g., "https://your-domain.atlassian.net").
            email (str): The email address associated with the account.
            token (str): The API token.
        """
        self.client = JIRA(
            server=server,
            basic_auth=(email, token)
        )

    def send_notification(self, destination: str, message: str, **kwargs) -> Dict[str, Any]:
        """
        Create a Jira issue. 
        Note: 'destination' is mapped to 'project' and 'message' to 'summary'.
        
        Args:
            destination (str): The project key (e.g., "PROJ").
            message (str): The summary of the issue.
            **kwargs: Additional arguments for issue creation (e.g., description, issue_type).
                      Defaults issue_type to 'Task' if not provided.

        Returns:
            Dict[str, Any]: A dictionary containing key, id, and self link of the created issue.
        """
        issue_dict = {
            'project': {'key': destination},
            'summary': message,
            'description': kwargs.get('description', ''),
            'issuetype': {'name': kwargs.get('issue_type', 'Task')},
        }
        
        # Add any other fields passed in kwargs that are not description/issue_type
        # Be careful with this as JIRA structure is nested
        
        try:
            new_issue = self.client.create_issue(fields=issue_dict)
            return {
                "key": new_issue.key,
                "id": new_issue.id,
                "self": new_issue.self
            }
        except JIRAError as e:
            raise e

    def create_issue(self, project: str, summary: str, description: str, issue_type: str = "Task", **kwargs) -> Dict[str, Any]:
        """
        Explicit method to create an issue, for better readability than send_notification.
        
        Args:
            project (str): Project key.
            summary (str): Issue summary.
            description (str): Issue description.
            issue_type (str): Issue type (default "Task").
            **kwargs: Additional fields.
            
        Returns:
            Dict[str, Any]: Issue details.
        """
        return self.send_notification(project, summary, description=description, issue_type=issue_type, **kwargs)
