"""
Hybrid Google Calendar Tool

This provides both local development OAuth (Desktop) and production OAuth (Web) support.
Environment detection automatically chooses the right OAuth flow.
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from config import config


class HybridCalendarTool:
    """
    Hybrid Google Calendar integration with automatic environment detection
    
    - Local development: Uses Desktop OAuth (InstalledAppFlow)
    - Production/Brev: Uses Web OAuth (server-based flow)
    """
    
    def __init__(self):
        self.client_id = getattr(config, 'GOOGLE_CLIENT_ID', None)
        self.client_secret = getattr(config, 'GOOGLE_CLIENT_SECRET', None) 
        self.redirect_uri = getattr(config, 'GOOGLE_REDIRECT_URI', 'http://localhost:8080')
        self.oauth_environment = getattr(config, 'OAUTH_ENVIRONMENT', 'auto')
        self.credentials_file = "google_credentials.json"
        self.token_file = "google_token.json"
        self._service = None
        self._environment = self._detect_environment()
    
    def _detect_environment(self):
        """Detect whether we're running locally or in production"""
        if self.oauth_environment == 'local':
            return 'local'
        elif self.oauth_environment == 'production':
            return 'production'
        else:  # auto-detect
            # Check if we're running on localhost
            import socket
            hostname = socket.gethostname()
            
            # Common indicators of local development
            local_indicators = [
                'localhost' in hostname.lower(),
                hostname.lower().startswith('mac'),
                hostname.lower().startswith('pc'),
                os.path.exists('/Users'),  # macOS
                os.path.exists('/home') and not os.path.exists('/var/www'),  # Linux desktop
            ]
            
            if any(local_indicators):
                print("🏠 Detected local development environment")
                return 'local'
            else:
                print("☁️ Detected production/cloud environment")
                return 'production'
    
    def _get_calendar_service(self):
        """Get authenticated Google Calendar service with hybrid OAuth"""
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            
            SCOPES = ['https://www.googleapis.com/auth/calendar']
            
            # Try to load existing token
            creds = None
            if os.path.exists(self.token_file):
                creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
            
            # If no valid credentials, start OAuth flow
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    print("🔄 Refreshing Google Calendar token...")
                    creds.refresh(Request())
                else:
                    # Use appropriate OAuth flow based on environment
                    if self._environment == 'local':
                        creds = self._local_oauth_flow(SCOPES)
                    else:
                        creds = self._production_oauth_flow(SCOPES)
                
                if creds:
                    # Save credentials for future use
                    with open(self.token_file, 'w') as token:
                        token.write(creds.to_json())
                    print("✅ Google Calendar authentication successful!")
            
            if creds:
                return build('calendar', 'v3', credentials=creds)
            else:
                return None
            
        except ImportError as e:
            print(f"❌ Missing Google Calendar dependencies: {e}")
            print("📦 Install with: pip install google-auth google-auth-oauthlib google-api-python-client")
            return None
        except Exception as e:
            print(f"❌ Calendar authentication error: {e}")
            return None
    
    def _local_oauth_flow(self, scopes):
        """Desktop OAuth flow for local development"""
        try:
            print("🔐 Starting LOCAL OAuth flow (Desktop Application mode)...")
            print("📅 Your browser will open for Google Calendar authorization")
            
            # Create desktop credentials for local development
            desktop_config = {
                "installed": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost"]
                }
            }
            
            # Save temporary desktop config
            desktop_config_file = "temp_desktop_credentials.json"
            with open(desktop_config_file, 'w') as f:
                json.dump(desktop_config, f)
            
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file(desktop_config_file, scopes)
            creds = flow.run_local_server(port=8080, open_browser=True)
            
            # Clean up temp file
            if os.path.exists(desktop_config_file):
                os.remove(desktop_config_file)
                
            return creds
            
        except Exception as e:
            print(f"❌ Local OAuth flow failed: {e}")
            return None
    
    def _production_oauth_flow(self, scopes):
        """Web OAuth flow for production deployment"""
        try:
            print("🌐 Production OAuth flow not yet implemented")
            print("📋 For now, this will use fallback calendar events")
            print("🔧 Production OAuth requires web server integration")
            
            # TODO: Implement production OAuth flow
            # This would involve:
            # 1. Redirecting user to Google OAuth URL  
            # 2. Handling callback in web server
            # 3. Exchanging code for tokens
            # 4. Storing tokens securely per user
            
            return None
            
        except Exception as e:
            print(f"❌ Production OAuth flow error: {e}")
            return None
    
    def schedule_event(self, calendar_id: str, title: str, datetime_str: str) -> Dict[str, Any]:
        """
        Create a real Google Calendar event (hybrid environment support)
        
        Args:
            calendar_id: Usually 'primary' for main calendar
            title: Event title like 'Saturday Plan: Golden Gate Park'
            datetime_str: '2025-08-02 11:00' format
            
        Returns:
            Dictionary with event details and status
        """
        try:
            service = self._get_calendar_service()
            if not service:
                return self._fallback_calendar_event(title, datetime_str)
            
            from datetime import datetime, timedelta
            
            # Parse the datetime
            event_time = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
            end_time = event_time + timedelta(hours=2)  # 2-hour event
            
            # Format for Google Calendar API
            start_iso = event_time.strftime('%Y-%m-%dT%H:%M:%S')
            end_iso = end_time.strftime('%Y-%m-%dT%H:%M:%S')
            
            print(f"📅 Creating REAL Google Calendar event: '{title}' at {datetime_str}")
            
            # Create event object
            event = {
                'summary': title,
                'description': 'Planned by SaturdayPlanner AI Agent 🤖\n\nThis event was automatically created by your AI assistant!',
                'start': {
                    'dateTime': start_iso,
                    'timeZone': 'America/Los_Angeles',
                },
                'end': {
                    'dateTime': end_iso,
                    'timeZone': 'America/Los_Angeles',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 30},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }
            
            # Create the event
            created_event = service.events().insert(
                calendarId=calendar_id or 'primary',
                body=event
            ).execute()
            
            event_id = created_event.get('id')
            event_link = created_event.get('htmlLink')
            
            print(f"✅ REAL Google Calendar event created!")
            print(f"   📋 Event ID: {event_id}")
            print(f"   🔗 Link: {event_link}")
            
            return {
                "event_id": event_id,
                "confirmation_url": event_link,
                "status": "scheduled",
                "start_time": start_iso,
                "end_time": end_iso,
                "title": title,
                "provider": "google_calendar",
                "calendar_id": calendar_id or 'primary',
                "environment": self._environment
            }
            
        except Exception as e:
            print(f"❌ Google Calendar API error: {e}")
            return self._fallback_calendar_event(title, datetime_str)
    
    def _fallback_calendar_event(self, title: str, datetime_str: str) -> Dict[str, Any]:
        """Fallback when Google Calendar API isn't available"""
        from datetime import datetime, timedelta
        
        event_time = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        end_time = event_time + timedelta(hours=2)
        
        start_iso = event_time.strftime('%Y-%m-%dT%H:%M:%S')
        end_iso = end_time.strftime('%Y-%m-%dT%H:%M:%S')
        
        if self._environment == 'production':
            print(f"📅 PRODUCTION FALLBACK: Mock calendar event for '{title}' at {datetime_str}")
            print("🔧 Production OAuth flow needs to be completed for real calendar events")
        else:
            print(f"📅 LOCAL FALLBACK: Mock calendar event for '{title}' at {datetime_str}")
            print("🔐 Run OAuth setup to enable real calendar events")
        
        event_id = f"saturday_plan_{int(event_time.timestamp())}"
        
        return {
            "event_id": event_id,
            "confirmation_url": f"https://calendar.google.com/calendar/r/create?text={title}",
            "status": "mock_scheduled",
            "start_time": start_iso,
            "end_time": end_iso,
            "title": title,
            "provider": f"fallback_{self._environment}",
            "environment": self._environment
        }


# Create instance for backward compatibility
hybrid_calendar_tool = HybridCalendarTool()