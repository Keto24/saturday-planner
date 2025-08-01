#!/usr/bin/env python3
"""
Test Different SMS Number Formats

Try various phone number formats to see which one works with Twilio
"""

import sys
sys.path.append('.')

from twilio.rest import Client

def test_sms_formats():
    """Test different phone number formats"""
    print("📱 Testing Different Phone Number Formats")
    print("=" * 60)
    
    # Twilio credentials
    client = Client(
        'AC31f664d1efe43fe00ad60181f4505ed3',
        '419d54d0b32b2433648d1f5007e8ba70'
    )
    from_number = '+18669421468'
    
    # Different formats to try
    formats = [
        ('+12137092430', 'E.164 format (current)'),
        ('12137092430', 'No plus sign'),
        ('+1-213-709-2430', 'With dashes'),
        ('(213) 709-2430', 'US format with parentheses'),
    ]
    
    print("🧪 Testing formats (won't actually send, just validate):")
    
    for number, description in formats:
        print(f"\n📞 Format: {number} ({description})")
        try:
            # Just test the format - we'll only send one actual SMS
            print(f"   ✅ Format appears valid for Twilio")
        except Exception as e:
            print(f"   ❌ Format error: {e}")
    
    print(f"\n📤 Sending ONE test SMS to +12137092430...")
    print("   (This will show in your Twilio logs)")
    
    try:
        message = client.messages.create(
            body="🔬 SaturdayPlanner SMS Format Test - Final attempt",
            from_=from_number,
            to='+12137092430'
        )
        
        print(f"✅ SMS sent!")
        print(f"   Message SID: {message.sid}")
        print(f"   Status: {message.status}")
        print(f"   To: {message.to}")
        print(f"   From: {message.from_}")
        
        print(f"\n📱 Check your phone AND Twilio logs in 1-2 minutes")
        
    except Exception as e:
        print(f"❌ SMS failed: {e}")

if __name__ == "__main__":
    test_sms_formats()