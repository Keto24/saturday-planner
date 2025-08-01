"""
Quick test to make sure the weather tool works with your API key
Testing with San Francisco (our new default) and other cities
"""

from agent_tools import get_weather

print("🧪 Testing Weather Tool with Your API Key")
print("=" * 50)

# Test with San Francisco (our new default)
print("\n🌉 Testing San Francisco (94102)...")
sf_weather = get_weather("94102")
print(f"SF Weather: {sf_weather}")

# Test with Los Angeles  
print("\n🌴 Testing Los Angeles (90210)...")
la_weather = get_weather("90210")
print(f"LA Weather: {la_weather}")

# Test with New York
print("\n🗽 Testing New York (10001)...")
ny_weather = get_weather("10001")
print(f"NY Weather: {ny_weather}")

print("\n✅ Weather tool testing complete!")
print("The agent can now check weather for any zip code users provide.")