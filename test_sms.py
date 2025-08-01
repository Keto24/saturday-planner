"""
Quick SMS test to verify Twilio integration
"""
from twilio.rest import Client

# Your Twilio credentials
account_sid = "AC31f664d1efe43fe00ad60181f4505ed3"
auth_token = "419d54d0b32b2433648d1f5007e8ba70"
from_number = "+18669421468"

print("🧪 Testing Twilio SMS Integration")
print(f"Account SID: {account_sid}")
print(f"From Number: {from_number}")

try:
    # Create Twilio client
    client = Client(account_sid, auth_token)
    
    # Test message
    message = "🤖 TEST: SaturdayPlanner AI Agent SMS integration working! This is a test from your hackathon project."
    
    # Send to test number
    sms = client.messages.create(
        body=message,
        from_=from_number,
        to="+15551234567"  # Test number
    )
    
    print(f"✅ SMS sent successfully!")
    print(f"Message SID: {sms.sid}")
    print(f"Status: {sms.status}")
    
except Exception as e:
    print(f"❌ SMS test failed: {e}")