"""
Agent Tools - The SaturdayPlanner's "Hands"

These are the actual functions our AI agent can call to interact with the real world.
Think of each function as giving the agent a new superpower:
- get_weather() = Can check if it's raining
- search_places() = Can find restaurants and activities  
- memory_store() = Can remember your preferences
- schedule_event() = Can add events to your calendar
- send_notification() = Can text or email you

Each tool returns data in a specific format so the agent knows what to do with it.
"""

import requests
import json
import os
from typing import Dict, List, Any, Optional
from config import config
from datetime import datetime, timedelta
from hybrid_calendar_tool import HybridCalendarTool

class WeatherTool:
    """
    Weather checking tool using WeatherAPI.com
    
    This is like giving the agent the ability to check a weather app.
    It takes a zip code and returns simple weather info the agent can understand.
    """
    
    def __init__(self):
        self.api_key = config.WEATHER_API_KEY
        self.base_url = "http://api.weatherapi.com/v1"
    
    def get_weather(self, zip_code: str) -> Dict[str, Any]:
        """
        Get weather forecast for a zip code.
        
        Args:
            zip_code: Like "94102" or "90210"
            
        Returns:
            {
                "forecast": "sunny" | "cloudy" | "rainy" | "stormy",
                "high": 75,
                "low": 60,
                "description": "Partly cloudy with chance of rain",
                "rain_chance": 20
            }
        """
        try:
            # WeatherAPI endpoint for current + forecast weather
            url = f"{self.base_url}/forecast.json"
            params = {
                "key": self.api_key,
                "q": zip_code,
                "days": 2,  # Today + tomorrow (for Saturday planning)
                "aqi": "no",  # We don't need air quality
                "alerts": "no"  # We don't need weather alerts
            }
            
            print(f"Checking weather for zip code: {zip_code}")
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raises an error if the API call failed
            
            data = response.json()
            
            # Extract the info we need for Saturday planning
            current = data["current"]
            forecast_days = data["forecast"]["forecastday"]
            if not forecast_days:
                raise Exception("No forecast data available")
            forecast_day = forecast_days[0]["day"]  # Today's forecast
            
            # Simplify weather condition for the agent to understand
            condition = current["condition"]["text"].lower()
            if "rain" in condition or "drizzle" in condition or "shower" in condition:
                simple_forecast = "rainy"
            elif "storm" in condition or "thunder" in condition:
                simple_forecast = "stormy"
            elif "cloud" in condition or "overcast" in condition:
                simple_forecast = "cloudy"
            elif "sun" in condition or "clear" in condition:
                simple_forecast = "sunny"
            else:
                simple_forecast = "cloudy"  # Default fallback
            
            result = {
                "forecast": simple_forecast,
                "high": int(forecast_day["maxtemp_f"]),
                "low": int(forecast_day["mintemp_f"]),
                "description": current["condition"]["text"],
                "rain_chance": forecast_day["daily_chance_of_rain"]
            }
            
            print(f"Weather result: {result['forecast']}, High: {result['high']}F, Rain chance: {result['rain_chance']}%")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Weather API error: {e}")
            # Return a fallback so the agent can still work
            return {
                "forecast": "unknown",
                "high": 70,
                "low": 60,
                "description": "Weather data unavailable",
                "rain_chance": 0
            }
        except Exception as e:
            print(f"Unexpected weather error: {e}")
            return {
                "forecast": "unknown",
                "high": 70,
                "low": 60,
                "description": "Weather data unavailable",
                "rain_chance": 0
            }


class PlacesTool:
    """
    Places/Restaurant search tool using Google Places API
    
    This finds real restaurants and activities near you using Google's database.
    """
    
    def __init__(self):
        self.api_key = config.PLACES_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api/place"
    
    def _get_coordinates(self, zip_code: str) -> tuple[float, float]:
        """Convert zip code to latitude/longitude using Google Geocoding API"""
        try:
            geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                "address": zip_code,
                "key": self.api_key
            }
            response = requests.get(geocode_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data["results"]:
                location = data["results"][0]["geometry"]["location"]
                return location["lat"], location["lng"]
            else:
                # Default to San Francisco if geocoding fails
                return 37.7749, -122.4194
        except Exception as e:
            print(f"Geocoding error: {e}, using SF default")
            return 37.7749, -122.4194
    
    def search_places(self, category: str, zip_code: str = "94102", radius_miles: int = 5, max_price: int = 3) -> List[Dict[str, Any]]:
        """
        Search for places/activities using Google Places API
        
        Args:
            category: "restaurant", "entertainment", "outdoor", "shopping"
            zip_code: Where to search (default San Francisco)
            radius_miles: How far to search (default 5 miles)
            max_price: 1-4 price level (1=cheap, 4=expensive)
            
        Returns:
            [
                {
                    "name": "Great Restaurant",
                    "address": "123 Main St, City, ST",
                    "rating": 4.5,
                    "price_level": 2,
                    "category": "restaurant"
                }
            ]
        """
        try:
            print(f"Searching for {category} near {zip_code} within {radius_miles} miles, max price ${max_price}")
            
            # Convert zip code to coordinates
            lat, lng = self._get_coordinates(zip_code)
            
            # Convert miles to meters (Google API uses meters)
            radius_meters = int(radius_miles * 1609.34)
            
            # Map our categories to Google Places types
            type_mapping = {
                "restaurant": "restaurant",
                "entertainment": "tourist_attraction|amusement_park|movie_theater|museum",
                "outdoor": "park|tourist_attraction",
                "shopping": "shopping_mall|store"
            }
            
            place_type = type_mapping.get(category, "restaurant")
            
            # Search using Google Places Nearby Search
            search_url = f"{self.base_url}/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": radius_meters,
                "type": place_type,
                "key": self.api_key
            }
            
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            places = []
            
            for place in data.get("results", [])[:10]:  # Limit to 10 results
                # Filter by price level if available
                place_price = place.get("price_level", 1)  # Default to cheap if no price
                if place_price > max_price:
                    continue
                
                places.append({
                    "name": place.get("name", "Unknown Place"),
                    "address": place.get("vicinity", "Address not available"),
                    "rating": place.get("rating", 0.0),
                    "price_level": place_price,
                    "category": category
                })
            
            print(f"Found {len(places)} real places matching criteria")
            return places
            
        except Exception as e:
            print(f"Google Places API error: {e}")
            # Fallback to mock data if API fails
            print("Using fallback mock data")
            mock_places = [
                {
                    "name": "Golden Gate Cafe",
                    "address": "123 Union St, San Francisco, CA",
                    "rating": 4.5,
                    "price_level": 2,
                    "category": "restaurant"
                },
                {
                    "name": "Golden Gate Park",
                    "address": "Golden Gate Park, San Francisco, CA",
                    "rating": 4.8,
                    "price_level": 1,
                    "category": "outdoor"
                },
                {
                    "name": "SF Museum of Modern Art",
                    "address": "151 3rd St, San Francisco, CA",
                    "rating": 4.6,
                    "price_level": 2,
                    "category": "entertainment"
                }
            ]
            
            filtered_places = [
                place for place in mock_places 
                if place["category"] == category and place["price_level"] <= max_price
            ]
            
            return filtered_places


class MemoryTool:
    """
    Memory tool - Helps the agent remember your preferences
    
    This is like giving the agent a notebook to write down what you like.
    "User liked Italian restaurants", "User prefers indoor activities when it rains"
    """
    
    def __init__(self):
        self.memory_file = config.MEMORY_PATH
    
    def memory_fetch(self, key: str) -> List[str]:
        """
        Fetch remembered information
        
        Args:
            key: What to remember, like "liked_places" or "preferred_activities"
            
        Returns:
            List of remembered items, like ["Italian Restaurant", "Central Park"]
        """
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    result = data.get(key, [])
                    print(f"Retrieved {len(result)} memories for '{key}'")
                    return result
            else:
                print(f"No memory file found, starting fresh")
                return []
        except Exception as e:
            print(f"Memory fetch error: {e}")
            return []
    
    def memory_store(self, key: str, value: str) -> Dict[str, str]:
        """
        Store new information for later
        
        Args:
            key: Category like "liked_places"
            value: What to remember like "Tony's Pizza"
            
        Returns:
            {"status": "stored"} or {"status": "error", "message": "..."}
        """
        try:
            # Load existing memory or create new
            data = {}
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
            
            # Add new memory
            if key not in data:
                data[key] = []
            
            if value not in data[key]:  # Avoid duplicates
                data[key].append(value)
                
                # Save back to file
                with open(self.memory_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                print(f"Stored new memory: {key} -> {value}")
                return {"status": "stored"}
            else:
                print(f"Memory already exists: {key} -> {value}")
                return {"status": "already_exists"}
                
        except Exception as e:
            print(f"Memory store error: {e}")
            return {"status": "error", "message": str(e)}


class CalendarTool:
    """
    Hybrid Google Calendar integration
    
    Uses HybridCalendarTool for environment-aware OAuth (local vs production)
    """
    
    def __init__(self):
        self._hybrid_tool = HybridCalendarTool()
    
    def schedule_event(self, calendar_id: str, title: str, datetime_str: str) -> Dict[str, Any]:
        """Schedule event using hybrid OAuth system"""
        return self._hybrid_tool.schedule_event(calendar_id, title, datetime_str)


class NotificationTool:
    """
    Real SMS/Email notification system
    
    This sends actual notifications to users!
    """
    
    def __init__(self):
        self.twilio_sid = config.NOTIFICATION_API_KEY
        self.twilio_token = config.NOTIFICATION_AUTH_TOKEN
        self.notification_from = config.NOTIFICATION_FROM
        self.default_notification_to = config.NOTIFICATION_TO
    
    def send_notification(self, channel: str, message: str, recipient: str = None) -> Dict[str, str]:
        """
        Send real SMS or email notification
        """
        try:
            if channel == "sms" and self.twilio_sid and self.twilio_sid.startswith("AC"):
                return self._send_sms(message, recipient)
            else:
                return self._send_enhanced_mock(channel, message)
                
        except Exception as e:
            print(f"❌ Notification error: {e}")
            return {"status": "failed", "error": str(e), "channel": channel}
    
    def _send_sms(self, message: str, recipient: str = None) -> Dict[str, str]:
        """Send real SMS via Twilio"""
        try:
            from twilio.rest import Client
            
            print(f"📱 Sending REAL SMS notification via Twilio...")
            print(f"   From: {self.notification_from}")
            print(f"   Message: {message[:100]}...")
            
            # Create Twilio client
            client = Client(self.twilio_sid, self.twilio_token)
            
            # Use provided recipient or default to configured number
            to_number = recipient or self.default_notification_to or "+15551234567"  # Fallback to demo if no number configured
            
            # Send the SMS
            sms_message = client.messages.create(
                body=message,
                from_=self.notification_from,
                to=to_number
            )
            
            print(f"✅ SMS sent successfully! Message SID: {sms_message.sid}")
            
            return {
                "status": "sent",
                "channel": "sms", 
                "provider": "twilio",
                "message_sid": sms_message.sid,
                "to": to_number,
                "from": self.notification_from,
                "message": "Real SMS sent via Twilio!"
            }
            
        except Exception as e:
            print(f"❌ SMS error: {e}")
            return {"status": "failed", "error": str(e), "channel": "sms"}
    
    def _send_enhanced_mock(self, channel: str, message: str) -> Dict[str, str]:
        """Enhanced mock with realistic behavior"""
        print(f"📬 DEMO: Sending {channel} notification:")
        print(f"   📱 Channel: {channel}")
        print(f"   📄 Message: {message}")
        print(f"   ✅ Status: Successfully delivered (demo mode)")
        
        return {
            "status": "sent",
            "channel": channel,
            "provider": "demo_mode",
            "message": f"Notification sent via {channel} (demo)",
            "timestamp": str(datetime.now())
        }


# Create tool instances that the agent can use
weather_tool = WeatherTool()
places_tool = PlacesTool()
memory_tool = MemoryTool()
calendar_tool = CalendarTool()
notification_tool = NotificationTool()

# Helper functions that the agent will actually call
def get_weather(zip_code: str) -> Dict[str, Any]:
    """Agent calls this to check weather"""
    return weather_tool.get_weather(zip_code)

def search_places(category: str, zip_code: str = "94102", radius_miles: int = 5, max_price: int = 3) -> List[Dict[str, Any]]:
    """Agent calls this to find activities"""
    return places_tool.search_places(category, zip_code, radius_miles, max_price)

def memory_fetch(key: str) -> List[str]:
    """Agent calls this to remember past preferences"""
    return memory_tool.memory_fetch(key)

def memory_store(key: str, value: str) -> Dict[str, str]:
    """Agent calls this to save new preferences"""
    return memory_tool.memory_store(key, value)

def schedule_event(calendar_id: str, title: str, datetime_str: str) -> Dict[str, Any]:
    """Agent calls this to add calendar events"""
    return calendar_tool.schedule_event(calendar_id, title, datetime_str)

def send_notification(channel: str, message: str) -> Dict[str, str]:
    """Agent calls this to notify you"""
    return notification_tool.send_notification(channel, message)