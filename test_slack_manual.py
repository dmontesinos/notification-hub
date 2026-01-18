import os
import sys
from notification_hub import NotificationFactory

# Configuration
# You can set the SLACK_BOT_TOKEN environment variable or edit this file directly
SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "xoxb-10346132914400-10315883622326-eO3L7Tzy2IiyygEhRZPF1bC7")
CHANNEL = "#automations" # Change this to the channel you want to test (ensure the bot is in the channel)

def main():
    if "YOUR_TOKEN" in SLACK_TOKEN:
        print("⚠️  ERROR: You need to configure a valid Slack token.")
        print("   Edit the file 'test_slack_manual.py' or set the SLACK_BOT_TOKEN environment variable.")
        sys.exit(1)

    # Ask user for the message
    user_message = input(f"📝 Enter the message to send to {CHANNEL}: ")
    
    if not user_message:
        print("❌ Message cannot be empty.")
        sys.exit(1)

    print(f"🚀 Sending message to {CHANNEL}...")
    
    try:
        slack = NotificationFactory.get_provider("slack", token=SLACK_TOKEN)
        
        # Send the notification
        response = slack.send_notification(
            destination=CHANNEL, 
            message=user_message
        )
        
        print("✅ Message sent successfully!")
        print(f"   Message Timestamp: {response.get('ts')}")
        
    except Exception as e:
        print(f"❌ Error sending message: {e}")

if __name__ == "__main__":
    main()
