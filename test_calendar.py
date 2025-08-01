#!/usr/bin/env python3
"""
Test Google Calendar Integration

This script tests the real Google Calendar integration with OAuth authentication.
"""

import sys
sys.path.append('.')

from agent_tools import calendar_tool
from datetime import datetime, timedelta

def test_google_calendar():
    """Test creating a real Google Calendar event"""
    print("🧪 Testing Google Calendar Integration")
    print("=" * 50)
    
    # Test event details
    tomorrow = datetime.now() + timedelta(days=1)
    event_datetime = tomorrow.strftime("%Y-%m-%d 14:30")  # 2:30 PM tomorrow
    
    print(f"📅 Creating test event for: {event_datetime}")
    print("🔐 This will trigger Google OAuth if not already authenticated...")
    print()
    
    # Create calendar event
    result = calendar_tool.schedule_event(
        calendar_id="primary",
        title="🤖 SaturdayPlanner Test Event",
        datetime_str=event_datetime
    )
    
    print("📊 Result:")
    print(f"   Status: {result.get('status')}")
    print(f"   Event ID: {result.get('event_id')}")
    print(f"   Provider: {result.get('provider')}")
    
    if result.get('confirmation_url'):
        print(f"   🔗 Calendar Link: {result.get('confirmation_url')}")
    
    if result.get('status') == 'scheduled':
        print("\n✅ SUCCESS: Real Google Calendar event created!")
        print("   Check your Google Calendar to see the event.")
    elif result.get('status') == 'mock_scheduled':
        print("\n⚠️  FALLBACK: Mock event created (Google Calendar API not available)")
    else:
        print("\n❌ FAILED: Could not create calendar event")
        if result.get('error'):
            print(f"   Error: {result.get('error')}")

if __name__ == "__main__":
    test_google_calendar()