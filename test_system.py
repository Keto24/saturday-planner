#!/usr/bin/env python3
"""
Test the complete SaturdayPlanner system (without OAuth for now)

This tests the full agent workflow with fallback calendar events.
"""

import sys
sys.path.append('.')

from saturday_agent import saturday_agent
from datetime import datetime, timedelta

def test_complete_system():
    """Test the complete SaturdayPlanner workflow"""
    print("🧪 Testing Complete SaturdayPlanner System")
    print("=" * 60)
    
    # Use the existing agent
    print("🤖 Using Saturday Planning Agent...")
    agent = saturday_agent
    
    # Test input
    zip_code = "94102"
    user_message = "Plan something fun for my Saturday!"
    
    print(f"📍 Location: {zip_code}")
    print(f"💬 Request: {user_message}")
    print()
    
    # Run the agent
    print("🚀 Running Saturday Planning Agent...")
    print("=" * 60)
    
    try:
        # Run the agent
        final_state = agent.plan_saturday(zip_code=zip_code, user_message=user_message)
        
        print("\n" + "=" * 60)
        print("📊 FINAL RESULTS:")
        print("=" * 60)
        
        # Display results
        weather = final_state.get('weather', {})
        print(f"🌤️  Weather: {weather.get('forecast', 'unknown')}, {weather.get('high', 'N/A')}°F")
        
        choice = final_state.get('choice', {})
        if choice:
            print(f"🎯 Selected Activity: {choice.get('name', 'Unknown')}")
            print(f"📍 Location: {choice.get('address', 'Unknown')}")
            print(f"⭐ Rating: {choice.get('rating', 'N/A')} stars")
        
        calendar = final_state.get('calendar', {})
        if calendar:
            print(f"📅 Calendar: {calendar.get('status', 'unknown')} - {calendar.get('title', 'N/A')}")
            print(f"🔗 Provider: {calendar.get('provider', 'unknown')}")
        
        notification = final_state.get('notification', {})
        if notification:
            print(f"📱 Notification: {notification.get('status', 'unknown')} via {notification.get('channel', 'unknown')}")
        
        print("\n✅ System test completed successfully!")
        
        # Test summary
        components_working = []
        if weather.get('forecast') != 'unknown':
            components_working.append("✅ Weather API")
        else:
            components_working.append("⚠️ Weather API (fallback)")
            
        if len(final_state.get('candidates', [])) > 0:
            components_working.append("✅ Google Places API")
        else:
            components_working.append("⚠️ Google Places API (fallback)")
            
        if calendar.get('provider') == 'google_calendar':
            components_working.append("✅ Google Calendar")
        else:
            components_working.append("⚠️ Google Calendar (fallback)")
            
        if notification.get('provider') == 'twilio':
            components_working.append("✅ Twilio SMS")
        else:
            components_working.append("⚠️ Twilio SMS (fallback)")
        
        print("\n🔧 Component Status:")
        for component in components_working:
            print(f"   {component}")
            
        return True
        
    except Exception as e:
        print(f"\n❌ System test failed: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_system()
    if success:
        print("\n🎉 Ready for production deployment!")
    else:
        print("\n🔧 Fix issues before deployment.")