import urllib.parse
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from config.settings import settings

class RealCalendarService:
    """
    Real Calendar service layer.
    Supports:
    1. Direct 1-Click Google Calendar web link generation for instant sync to real Google Calendar.
    2. Google Calendar API v3 (if OAuth credentials.json or token is configured).
    """
    def __init__(self):
        self.creds_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials.json")
        self.token_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "token.json")
        self._gcal_service = None

    def _init_gcal_api(self):
        """Try initializing Google Calendar API client if credentials exist."""
        if self._gcal_service:
            return True
            
        if os.path.exists(self.creds_file) or os.path.exists(self.token_file):
            try:
                from google.oauth2.credentials import Credentials
                from googleapiclient.discovery import build
                if os.path.exists(self.token_file):
                    creds = Credentials.from_authorized_user_file(self.token_file, ['https://www.googleapis.com/auth/calendar'])
                    self._gcal_service = build('calendar', 'v3', credentials=creds)
                    return True
            except Exception as e:
                print(f"[RealCalendarService] Google Calendar API init warning: {e}")
        return False

    def generate_google_calendar_link(
        self,
        title: str,
        date_str: str,
        start_time: str,
        end_time: str,
        description: str = "",
        attendees: Optional[str] = None
    ) -> str:
        """
        Generate a direct 1-click Google Calendar web link (action=TEMPLATE).
        Clicking this link opens Google Calendar with title, date, time, and details pre-filled.
        """
        # Convert YYYY-MM-DD + HH:MM into ISO compact format (YYYYMMDDTHHMMSS)
        s_date_clean = date_str.replace("-", "")
        s_time_clean = start_time.replace(":", "") + "00"
        e_time_clean = end_time.replace(":", "") + "00"
        
        dates_param = f"{s_date_clean}T{s_time_clean}/{s_date_clean}T{e_time_clean}"
        
        params = {
            "action": "TEMPLATE",
            "text": title,
            "dates": dates_param,
            "details": description,
        }
        if attendees:
            params["add"] = attendees
            
        query_str = urllib.parse.urlencode(params)
        return f"https://calendar.google.com/calendar/render?{query_str}"

    def create_event(
        self,
        title: str,
        date_str: str,
        start_time: str,
        end_time: str,
        attendees: List[str],
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Create a calendar event. If Google Calendar API credentials are present,
        inserts into real Google Calendar. Also generates a 1-click Google Calendar web link.
        """
        gcal_link = self.generate_google_calendar_link(
            title=title,
            date_str=date_str,
            start_time=start_time,
            end_time=end_time,
            description=description,
            attendees=", ".join(attendees) if attendees else None
        )
        
        gcal_event_id = None
        if self._init_gcal_api():
            try:
                start_iso = f"{date_str}T{start_time}:00"
                end_iso = f"{date_str}T{end_time}:00"
                body = {
                    'summary': title,
                    'description': description,
                    'start': {'dateTime': start_iso, 'timeZone': 'UTC'},
                    'end': {'dateTime': end_iso, 'timeZone': 'UTC'},
                    'attendees': [{'email': a} for a in attendees if '@' in a]
                }
                created = self._gcal_service.events().insert(calendarId='primary', body=body).execute()
                gcal_event_id = created.get('id')
            except Exception as e:
                print(f"[RealCalendarService] GCal API insert warning: {e}")

        return {
            "title": title,
            "date": date_str,
            "start_time": start_time,
            "end_time": end_time,
            "attendees": attendees,
            "description": description,
            "gcal_link": gcal_link,
            "gcal_event_id": gcal_event_id
        }

real_calendar_service = RealCalendarService()
