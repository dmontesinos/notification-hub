
import json
import os

def map_status(internal_status: str, map_file: str = None) -> str:
    """
    Map internal status to Jira status using a JSON mapping file.
    """
    mapping = {}
    if map_file and os.path.exists(map_file):
        try:
            with open(map_file, 'r') as f:
                mapping = json.load(f)
        except Exception as e:
            # Fallback will be used
            pass
    
    # Fallback default map
    if not mapping:
        mapping = {
            'Creation': 'Creation',
            'To Approve': 'To Approve',
            'To Review': 'To Review',
            'Accepted': 'Accepted',
            'Changes Required': 'Changes Required',
            'Scheduled': 'Scheduled',
            'In Progress': 'In Progress',
            'Completed': 'Completed',
            'Rollback': 'Rollback',
            'Cancelled': 'Cancelled'
        }
    
    return mapping.get(internal_status, internal_status)

def format_description(data: dict, app_url: str) -> str:
    """
    Format the intervention data into Jira Wiki Markup.
    """
    base_url = app_url.rstrip('/')
    interv_id = data.get('id')
    link = f"{base_url}/#detail/{interv_id}" if interv_id else base_url

    desc = "h2. 🔗 Intervention Details\n"
    desc += f"See full details and manage this intervention here: [Open in Intervention Manager|{link}]\n\n"

    desc += "h2. ℹ️ General Info\n"
    if data.get('description'):
        desc += f"*Description:* {data['description']}\n\n"
    
    etc = data.get('etc_minutes', 'N/A')
    desc += f"*Duration:* {etc} minutes\n"

    if data.get('steps_url'):
        desc += f"*Procedure URL:* [Open Procedures|{data['steps_url']}]\n"
    desc += "\n"

    desc += "h2. 💥 Impact\n"
    desc += "|| Type || Description ||\n"
    desc += f"| *System* | {data.get('impact_system', 'N/A')} |\n"
    desc += f"| *Client* | {data.get('impact_client', 'N/A')} |\n"
    desc += "\n"

    pr_links = data.get('pr_links')
    if pr_links:
        desc += "h2. 🐙 Pull Requests\n"
        if isinstance(pr_links, str):
            try:
                pr_links = json.loads(pr_links)
            except:
                pr_links = []
        
        if isinstance(pr_links, list):
            for pr in pr_links:
                url = pr.get('url') if isinstance(pr, dict) else pr
                if url:
                    desc += f"- [{url}|{url}]\n"
        desc += "\n"

    additional_links = data.get('additional_links')
    if additional_links:
        desc += "h2. 🔗 Additional Info\n"
        if isinstance(additional_links, str):
            try:
                additional_links = json.loads(additional_links)
            except:
                additional_links = []
        
        if isinstance(additional_links, list):
            for l in additional_links:
                url = l.get('url') if isinstance(l, dict) else l
                if url:
                    desc += f"- [{url}|{url}]\n"
    
    return desc
