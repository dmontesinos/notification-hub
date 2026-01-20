import argparse
import json
import os
import sys

# Ensure we can import from the package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from notification_hub.providers.jira import JiraProvider
from notification_hub.providers.slack import SlackProvider
from notification_hub.utils.jira_utils import format_description, map_status

def setup_jira_provider(args):
    server = args.server
    email = args.user
    token = args.token
    
    # Try to load token from secret if not provided
    if not token:
        secret_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'secrets', 'jira_token')
        if os.path.exists(secret_path):
            with open(secret_path, 'r') as f:
                token = f.read().strip()
                
    if not token and args.auth_method == 'token':
         # Depending on auth method, token might be mandatory. 
         # For basic auth, password/token is needed.
         pass
         
    if not token:
         raise Exception("Jira token not provided and secret file not found.")

    return JiraProvider(
        server=server,
        email=email,
        token=token,
        auth_method=args.auth_method
    )

def setup_slack_provider(args):
    token = args.token
    
    if not token:
        secret_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'secrets', 'slack_token')
        if os.path.exists(secret_path):
             with open(secret_path, 'r') as f:
                token = f.read().strip()
    
    if not token:
        raise Exception("Slack token not provided and secret file not found.")
        
    return SlackProvider(token=token)


def main():
    parser = argparse.ArgumentParser(description="Notification Hub CLI")
    subparsers = parser.add_subparsers(dest="provider_command", help="Provider to use", required=True)

    # ==========================================
    # JIRA Subcommand
    # ==========================================
    jira_parser = subparsers.add_parser("jira", help="Jira operations")
    
    # Jira Global Args
    jira_parser.add_argument("--server", required=True, help="Jira Server URL")
    jira_parser.add_argument("--user", required=True, help="Jira Username/Email")
    jira_parser.add_argument("--token", help="Jira API Token (optional, defaults to config/secrets/jira_token)")
    jira_parser.add_argument("--auth-method", default="basic", choices=["basic", "token"], help="Authentication method")
    
    jira_subparsers = jira_parser.add_subparsers(dest="command", help="Jira commands", required=True)

    # Jira: create
    parser_create = jira_subparsers.add_parser("create", help="Create issue")
    parser_create.add_argument("--project", required=True)
    parser_create.add_argument("--summary", required=True)
    parser_create.add_argument("--type", default="Task")
    parser_create.add_argument("--description", help="Raw description")
    parser_create.add_argument("--description-data", help="JSON data for formatted description")
    parser_create.add_argument("--app-url", default="http://localhost", help="App URL for links")
    parser_create.add_argument("--id", help="Intervention ID for links")

    # Jira: update
    parser_update = jira_subparsers.add_parser("update", help="Update issue")
    parser_update.add_argument("--key", required=True)
    parser_update.add_argument("--summary")
    parser_update.add_argument("--description", help="Raw description")
    parser_update.add_argument("--description-data", help="JSON data for formatted description")
    parser_update.add_argument("--app-url", default="http://localhost", help="App URL for links")
    parser_update.add_argument("--id", help="Intervention ID for links")

    # Jira: delete
    parser_delete = jira_subparsers.add_parser("delete", help="Delete issue")
    parser_delete.add_argument("--key", required=True)

    # Jira: transition
    parser_transition = jira_subparsers.add_parser("transition", help="Transition issue")
    parser_transition.add_argument("--key", required=True)
    parser_transition.add_argument("--id", help="Transition ID")
    parser_transition.add_argument("--status", help="Target Status Name")

    # Jira: map-status
    parser_map = jira_subparsers.add_parser("map-status", help="Map internal status")
    parser_map.add_argument("--status", required=True)
    parser_map.add_argument("--file", help="Mapping file path")

    # Jira: find-transition
    parser_find_trans = jira_subparsers.add_parser("find-transition", help="Find transition ID")
    parser_find_trans.add_argument("--key", required=True)
    parser_find_trans.add_argument("--status", required=True)

    # Jira: format
    parser_format = jira_subparsers.add_parser("format", help="Format description")
    parser_format.add_argument("--description-data", required=True)
    parser_format.add_argument("--app-url", default="http://localhost")
    parser_format.add_argument("--id")

    # ==========================================
    # SLACK Subcommand
    # ==========================================
    slack_parser = subparsers.add_parser("slack", help="Slack operations")
    slack_parser.add_argument("--token", help="Slack Bot Token (optional, defaults to config/secrets/slack_token)")
    
    slack_subparsers = slack_parser.add_subparsers(dest="command", help="Slack commands", required=True)
    
    # Slack: send
    parser_send = slack_subparsers.add_parser("send", help="Send message")
    parser_send.add_argument("--channel", required=True, help="Channel ID or name")
    parser_send.add_argument("--message", required=True, help="Message text")


    try:
        args = parser.parse_args()
        result = {}

        # ----------------------------------------
        # JIRA HANDLING
        # ----------------------------------------
        if args.provider_command == "jira":
            
            # Tools that don't need provider
            if args.command == "map-status":
                mapped = map_status(args.status, args.file)
                print(json.dumps({"status": mapped}))
                return

            if args.command == "format":
                try:
                    data = json.loads(args.description_data)
                    if args.id:
                        data['id'] = args.id
                    desc = format_description(data, args.app_url)
                    print(json.dumps({"description": desc}))
                    return
                except Exception as e:
                    print(json.dumps({"error": str(e)}))
                    sys.exit(1)

            # Operations needing provider
            provider = setup_jira_provider(args)
            
            if args.command == "create":
                desc = args.description
                if args.description_data:
                    data = json.loads(args.description_data)
                    if args.id:
                        data['id'] = args.id
                    desc = format_description(data, args.app_url)
                
                result = provider.create_issue(
                    project=args.project,
                    summary=args.summary,
                    description=desc,
                    issue_type=args.type
                )

            elif args.command == "update":
                fields = {}
                if args.summary:
                    fields['summary'] = args.summary
                
                desc = args.description
                if args.description_data:
                    data = json.loads(args.description_data)
                    if args.id:
                        data['id'] = args.id
                    desc = format_description(data, args.app_url)
                
                if desc:
                    fields['description'] = desc

                if fields:
                    provider.update_issue(args.key, **fields)
                result = {"status": "success", "key": args.key}

            elif args.command == "delete":
                provider.delete_issue(args.key)
                result = {"status": "success", "key": args.key}

            elif args.command == "transition":
                t_id = args.id
                if not t_id and args.status:
                    t_id = provider.get_transition_id_for_status(args.key, args.status)
                    if not t_id:
                         raise Exception(f"No transition found for status '{args.status}'")
                
                if t_id:
                    provider.transition_issue(args.key, t_id)
                    result = {"status": "success", "key": args.key, "transition_id": t_id}
                else:
                     raise Exception("Either --id or --status must be provided")

            elif args.command == "find-transition":
                t_id = provider.get_transition_id_for_status(args.key, args.status)
                result = {"transition_id": t_id}

        # ----------------------------------------
        # SLACK HANDLING
        # ----------------------------------------
        elif args.provider_command == "slack":
            provider = setup_slack_provider(args)
            
            if args.command == "send":
                res = provider.send_notification(
                    destination=args.channel, 
                    message=args.message
                )
                result = {"status": "success", "response": res}

        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
