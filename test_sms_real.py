#!/usr/bin/env python3
"""
Test Real SMS to Your Phone Number

This will send an actual SMS to +12137092430 to verify Twilio integration works.
"""

import sys
sys.path.append('.')

from agent_tools import notification_tool

def test_real_sms():
    """Test sending SMS to your real phone number"""
    print("📱 Testing Real SMS Integration")
    print("=" * 50)
    print("📞 Sending to: +12137092430")
    print()
    
    # Test message
    test_message = """🤖 SaturdayPlanner SMS Test!

Your AI agent is ready to send you real notifications about your Saturday plans!

This message confirms Twilio integration is working. ✅"""
    
    print("📤 Sending test SMS...")
    
    try:
        result = notification_tool.send_notification("sms", test_message)
        
        print("\n📊 Result:")
        print(f"   Status: {result.get('status')}")
        print(f"   Provider: {result.get('provider')}")
        print(f"   Channel: {result.get('channel')}")
        
        if result.get('message_sid'):
            print(f"   Message SID: {result.get('message_sid')}")
        if result.get('to'):
            print(f"   Sent to: {result.get('to')}")
        
        if result.get('status') == 'sent' and result.get('provider') == 'twilio':
            print("\n✅ SUCCESS: Real SMS sent via Twilio!")
            print("📱 Check your phone for the message!")
        elif result.get('status') == 'sent':
            print(f"\n⚠️  SMS sent via {result.get('provider')} (may be fallback)")
        else:
            print(f"\n❌ SMS failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_sms()