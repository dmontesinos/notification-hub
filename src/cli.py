import argparse
import json
import os
import sys

# Ensure we can import from the package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from notification_hub.providers.jira import JiraProvider
from notification_hub.utils.jira_utils import format_description, map_status

def setup_provider(args):
    return JiraProvider(
        server=args.server,
        email=args.user,
        token=args.token,
        auth_method=args.auth_method
    )

def main():
    parser = argparse.ArgumentParser(description="Notification Hub CLI for Jira")
    
    # Global args
    parser.add_argument("--server", required=True, help="Jira Server URL")
    parser.add_argument("--user", required=True, help="Jira Username/Email")
    parser.add_argument("--token", help="Jira API Token (optional, defaults to config/secrets/jira_token)")
    parser.add_argument("--auth-method", default="basic", choices=["basic", "token"], help="Authentication method")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: create
    parser_create = subparsers.add_parser("create", help="Create issue")
    parser_create.add_argument("--project", required=True)
    parser_create.add_argument("--summary", required=True)
    parser_create.add_argument("--type", default="Task")
    parser_create.add_argument("--description", help="Raw description")
    parser_create.add_argument("--description-data", help="JSON data for formatted description")
    parser_create.add_argument("--app-url", default="http://localhost", help="App URL for links")
    parser_create.add_argument("--id", help="Intervention ID for links")

    # Command: update
    parser_update = subparsers.add_parser("update", help="Update issue")
    parser_update.add_argument("--key", required=True)
    parser_update.add_argument("--summary")
    parser_update.add_argument("--description", help="Raw description")
    parser_update.add_argument("--description-data", help="JSON data for formatted description")
    parser_update.add_argument("--app-url", default="http://localhost", help="App URL for links")
    parser_update.add_argument("--id", help="Intervention ID for links")

    # Command: delete
    parser_delete = subparsers.add_parser("delete", help="Delete issue")
    parser_delete.add_argument("--key", required=True)

    # Command: transition
    parser_transition = subparsers.add_parser("transition", help="Transition issue")
    parser_transition.add_argument("--key", required=True)
    parser_transition.add_argument("--id", help="Transition ID")
    parser_transition.add_argument("--status", help="Target Status Name")

    # Command: map-status
    parser_map = subparsers.add_parser("map-status", help="Map internal status")
    parser_map.add_argument("--status", required=True)
    parser_map.add_argument("--file", help="Mapping file path")

    # Command: find-transition
    parser_find_trans = subparsers.add_parser("find-transition", help="Find transition ID")
    parser_find_trans.add_argument("--key", required=True)
    parser_find_trans.add_argument("--status", required=True)

    # Command: format
    parser_format = subparsers.add_parser("format", help="Format description")
    parser_format.add_argument("--description-data", required=True)
    parser_format.add_argument("--app-url", default="http://localhost")
    parser_format.add_argument("--id")

    args = parser.parse_args()

    # Handle map-status (Logic only, no provider needed)
    if args.command == "map-status":
        mapped = map_status(args.status, args.file)
        print(json.dumps({"status": mapped}))
        return

    # Handle format (Logic only, no provider needed)
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

    # Initialize Provider
    try:
        if not args.token:
            # Try to read from default secrets file
            secret_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'secrets', 'jira_token')
            if os.path.exists(secret_path):
                with open(secret_path, 'r') as f:
                    args.token = f.read().strip()
            else:
                 raise Exception(f"Token not provided and secret file not found at {secret_path}")

        provider = setup_provider(args)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    result = {}
    try:
        if args.command == "create":
            desc = args.description
            if args.description_data:
                data = json.loads(args.description_data)
                # Should include ID in data if not present? 
                # PHP passes ID separately in formatDescription($input, $id).
                # Adding ID to data if provided arg
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


        print(json.dumps(result))

    except Exception as e:
        # Wrap error in JSON for reliable parsing by PHP
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
