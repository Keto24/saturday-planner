"""
Test the complete Saturday Planning Agent
"""

from saturday_agent import plan_saturday

print("🧪 Testing Complete Saturday Planning Agent")
print("=" * 60)

# Test with San Francisco (our default)
print("Testing Saturday planning for San Francisco...")

try:
    result = plan_saturday(
        zip_code="94102",
        user_message="Plan something fun for Saturday"
    )
    
    print("\n📋 Final Result:")
    if result:
        print(f"Weather: {result.get('weather', {}).get('forecast', 'unknown')}")
        print(f"Candidates found: {len(result.get('candidates', []))}")
        print(f"After filtering: {len(result.get('filtered', []))}")
        print(f"Top choices: {len(result.get('ranking', []))}")
        
        if result.get('choice'):
            choice = result['choice']
            print(f"\n🎯 Final Choice: {choice['name']}")
            print(f"   Rating: {choice['rating']}⭐")
            print(f"   Address: {choice['address']}")
            print(f"   Category: {choice['category']}")
        
        print(f"\n📅 Calendar: {result.get('calendar', {}).get('status', 'unknown')}")
        print(f"📱 Notification: {result.get('notification', {}).get('status', 'unknown')}")
    else:
        print("❌ No result returned")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Agent testing complete!")