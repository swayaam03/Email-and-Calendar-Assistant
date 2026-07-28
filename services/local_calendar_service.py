import os
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from services.real_calendar_service import real_calendar_service

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "calendar_data.json")

class LocalCalendarService:
    """
    Persistent local calendar service enhanced with 1-click Google Calendar sync links.
    Saves created events to disk (calendar_data.json) so they persist across process restarts.
    """
    def __init__(self):
        self._events: List[Dict[str, Any]] = []
        self._reminders: List[Dict[str, Any]] = []
        self._load_from_disk()

    def _load_from_disk(self):
        """Load stored calendar events from disk or seed defaults if file doesn't exist."""
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        tomorrow_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        
        days_until_tuesday = (1 - now.weekday() + 7) % 7
        if days_until_tuesday == 0:
            days_until_tuesday = 7
        next_tuesday_str = (now + timedelta(days=days_until_tuesday)).strftime("%Y-%m-%d")

        default_events = [
            {
                "id": "event_1",
                "title": "Daily Engineering Standup",
                "date": today_str,
                "start_time": "10:00",
                "end_time": "10:30",
                "attendees": ["team@techcorp.com"],
                "description": "Daily sync on agentic AI milestones."
            },
            {
                "id": "event_2",
                "title": "Strategy Alignment Session",
                "date": tomorrow_str,
                "start_time": "10:00",
                "end_time": "11:30",
                "attendees": ["john.doe@company.org"],
                "description": "Q3 strategy planning meeting."
            },
            {
                "id": "event_3",
                "title": "Client Sync",
                "date": next_tuesday_str,
                "start_time": "10:00",
                "end_time": "11:00",
                "attendees": ["client@external.com"],
                "description": "Weekly status update with client."
            },
            {
                "id": "event_4",
                "title": "Architecture Workshop",
                "date": next_tuesday_str,
                "start_time": "16:00",
                "end_time": "17:00",
                "attendees": ["architecture-group@techcorp.com"],
                "description": "Deep dive into LangGraph micro-agents."
            }
        ]

        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self._events = saved.get("events", default_events)
                    self._reminders = saved.get("reminders", [])
                    return
            except Exception as e:
                print(f"[LocalCalendarService] Disk load warning: {e}")

        self._events = default_events
        self._save_to_disk()

    def _save_to_disk(self):
        """Save current calendar events and reminders to disk."""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({"events": self._events, "reminders": self._reminders}, f, indent=2)
        except Exception as e:
            print(f"[LocalCalendarService] Disk save warning: {e}")

    def get_events(self, date_str: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get events for a specific date (YYYY-MM-DD) or all upcoming events if date_str is None."""
        if not date_str:
            return self._events
        return [event for event in self._events if event["date"] == date_str]

    def find_available_slots(self, date_str: str, duration_minutes: int = 30) -> List[Dict[str, Any]]:
        """Find available time slots on a given date during working hours (09:00 - 17:00)."""
        existing_events = self.get_events(date_str)
        busy_times = []
        for event in existing_events:
            s_hour, s_min = map(int, event["start_time"].split(":"))
            e_hour, e_min = map(int, event["end_time"].split(":"))
            busy_times.append((s_hour * 60 + s_min, e_hour * 60 + e_min))
        
        work_start = 9 * 60
        work_end = 17 * 60
        available_slots = []
        
        current_time = work_start
        while current_time + duration_minutes <= work_end:
            slot_start = current_time
            slot_end = current_time + duration_minutes
            
            is_overlap = False
            for b_start, b_end in busy_times:
                if not (slot_end <= b_start or slot_start >= b_end):
                    is_overlap = True
                    break
            
            if not is_overlap:
                start_str = f"{slot_start // 60:02d}:{slot_start % 60:02d}"
                end_str = f"{slot_end // 60:02d}:{slot_end % 60:02d}"
                available_slots.append({
                    "date": date_str,
                    "start_time": start_str,
                    "end_time": end_str,
                    "duration_minutes": duration_minutes
                })
            
            current_time += 30
            
        return available_slots

    def create_event(self, title: str, date_str: str, start_time: str, end_time: str, attendees: List[str], description: str = "") -> Dict[str, Any]:
        """Create a new calendar event, save to disk, and generate 1-click Google Calendar sync URL."""
        event_id = f"event_{uuid.uuid4().hex[:6]}"
        
        real_details = real_calendar_service.create_event(
            title=title,
            date_str=date_str,
            start_time=start_time,
            end_time=end_time,
            attendees=attendees,
            description=description
        )
        
        event = {
            "id": event_id,
            "title": title,
            "date": date_str,
            "start_time": start_time,
            "end_time": end_time,
            "attendees": attendees,
            "description": description,
            "gcal_link": real_details["gcal_link"],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self._events.append(event)
        self._save_to_disk()
        return event

    def create_reminder(self, title: str, date_time_str: str) -> Dict[str, Any]:
        """Create a quick task reminder and save to disk."""
        reminder_id = f"rem_{uuid.uuid4().hex[:6]}"
        reminder = {
            "id": reminder_id,
            "title": title,
            "date_time": date_time_str,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self._reminders.append(reminder)
        self._save_to_disk()
        return reminder

calendar_service = LocalCalendarService()
