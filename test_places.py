"""
Test Google Places API integration
"""

from agent_tools import search_places

print("🧪 Testing Google Places API with Your API Key")
print("=" * 50)

# Test restaurants in San Francisco
print("\n🍕 Testing restaurants in San Francisco...")
restaurants = search_places("restaurant", "94102", 5, 3)
print(f"Found {len(restaurants)} restaurants:")
for place in restaurants[:3]:  # Show first 3
    print(f"  - {place['name']}: {place['rating']}⭐ (${place['price_level']}) - {place['address']}")

# Test outdoor activities in San Francisco
print("\n🌳 Testing outdoor activities in San Francisco...")
outdoor = search_places("outdoor", "94102", 5, 3)
print(f"Found {len(outdoor)} outdoor places:")
for place in outdoor[:3]:  # Show first 3
    print(f"  - {place['name']}: {place['rating']}⭐ (${place['price_level']}) - {place['address']}")

# Test entertainment in a different city (LA)
print("\n🎭 Testing entertainment in Los Angeles...")
entertainment = search_places("entertainment", "90210", 5, 3)
print(f"Found {len(entertainment)} entertainment venues:")
for place in entertainment[:3]:  # Show first 3
    print(f"  - {place['name']}: {place['rating']}⭐ (${place['price_level']}) - {place['address']}")

print("\n✅ Google Places API testing complete!")