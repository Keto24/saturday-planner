"""
Configuration Management for SaturdayPlanner Agent

This file handles all the settings and API keys our agent needs.
Think of it like the agent's "settings menu" where we store
all the important information like API keys and preferences.
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
# This reads our secret API keys safely
load_dotenv()

class Config:
    """
    Configuration class that holds all our agent's settings.
    
    Think of this like the agent's memory for important settings
    that don't change often (like your preferred zip code).
    """
    
    # NVIDIA AI Model Settings
    NEMO_ENDPOINT: str = os.getenv("NEMO_ENDPOINT", "https://integrate.api.nvidia.com/v1")
    NEMO_API_KEY: str = os.getenv("NEMO_API_KEY", "")
    NEMO_MODEL: str = "nvidia/llama-3.3-nemotron-super-49b-v1"
    
    # Weather Service Settings
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    WEATHER_SERVICE: str = os.getenv("WEATHER_SERVICE", "openweathermap")
    
    # Places/Venue Search Settings
    PLACES_API_KEY: str = os.getenv("PLACES_API_KEY", "")
    PLACES_SERVICE: str = os.getenv("PLACES_SERVICE", "google_places")
    
    # Calendar Integration Settings
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8080")
    DEFAULT_CALENDAR_ID: str = os.getenv("DEFAULT_CALENDAR_ID", "primary")
    OAUTH_ENVIRONMENT: str = os.getenv("OAUTH_ENVIRONMENT", "auto")
    
    # Notification Settings
    NOTIFICATION_SERVICE: str = os.getenv("NOTIFICATION_SERVICE", "twilio")
    NOTIFICATION_API_KEY: str = os.getenv("NOTIFICATION_API_KEY", "")
    NOTIFICATION_AUTH_TOKEN: str = os.getenv("NOTIFICATION_AUTH_TOKEN", "")
    NOTIFICATION_FROM: str = os.getenv("NOTIFICATION_FROM", "")
    NOTIFICATION_TO: str = os.getenv("NOTIFICATION_TO", "")
    
    # Memory Storage Settings
    MEMORY_TYPE: str = os.getenv("MEMORY_TYPE", "file")
    MEMORY_PATH: str = os.getenv("MEMORY_PATH", "./agent_memory.json")
    
    # User Preference Defaults
    DEFAULT_ZIP_CODE: str = os.getenv("DEFAULT_ZIP_CODE", "10001")
    DEFAULT_RADIUS_MILES: int = int(os.getenv("DEFAULT_RADIUS_MILES", "5"))
    DEFAULT_MAX_PRICE: int = int(os.getenv("DEFAULT_MAX_PRICE", "3"))
    
    @classmethod
    def validate_required_keys(cls) -> list[str]:
        """
        Check if we have all the API keys we need.
        Returns a list of missing keys if any are missing.
        
        This is like checking if you have your wallet and keys
        before leaving the house.
        """
        missing_keys = []
        
        required_keys = {
            "NEMO_API_KEY": cls.NEMO_API_KEY,
            "WEATHER_API_KEY": cls.WEATHER_API_KEY,
            "PLACES_API_KEY": cls.PLACES_API_KEY,
        }
        
        for key_name, key_value in required_keys.items():
            if not key_value or key_value == "":
                missing_keys.append(key_name)
        
        return missing_keys

# Create a global config instance
config = Config()