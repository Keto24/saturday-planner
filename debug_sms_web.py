#!/usr/bin/env python3
"""
Debug SMS in Web Context

Test SMS exactly as the web server would call it
"""

import sys
sys.path.append('.')

from saturday_agent import saturday_agent

def debug_web_sms():
    """Test SMS the same way the web interface does"""
    print("🔍 Debugging Web Interface SMS")
    print("=" * 50)
    
    # This mimics exactly what the web interface does
    print("🤖 Testing via Saturday Agent (same as web interface)...")
    
    try:
        # Test the agent's planning workflow which includes SMS
        result = saturday_agent.plan_saturday(
            zip_code="94102",
            user_message="Debug SMS test"
        )
        
        print(f"\n📊 Agent Result:")
        print(f"   Choice: {result.get('choice', {}).get('name', 'None')}")
        
        notification = result.get('notification', {})
        print(f"   Notification Status: {notification.get('status', 'None')}")
        print(f"   Notification Provider: {notification.get('provider', 'None')}")
        print(f"   Notification Channel: {notification.get('channel', 'None')}")
        
        if notification.get('to'):
            print(f"   📱 Sent To: {notification.get('to')}")
        if notification.get('message_sid'):
            print(f"   Message SID: {notification.get('message_sid')}")
        
        # Check what the agent's notification tool has
        from agent_tools import notification_tool
        print(f"\n🔧 Agent's NotificationTool Config:")
        print(f"   default_notification_to: {notification_tool.default_notification_to}")
        print(f"   notification_from: {notification_tool.notification_from}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_web_sms()