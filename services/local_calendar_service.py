import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class LocalCalendarService:
    """
    A zero-config, in-memory Google Calendar replacement service.
    Handles schedule viewing, free/busy slot detection, and event creation.
    """
    def __init__(self):
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        tomorrow_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Calculate next Tuesday
        days_until_tuesday = (1 - now.weekday() + 7) % 7
        if days_until_tuesday == 0:
            days_until_tuesday = 7
        next_tuesday_str = (now + timedelta(days=days_until_tuesday)).strftime("%Y-%m-%d")

        # Pre-seeded schedule events
        self._events: List[Dict[str, Any]] = [
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
        self._reminders: List[Dict[str, Any]] = []

    def get_events(self, date_str: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get events for a specific date (YYYY-MM-DD) or all upcoming events if date_str is None."""
        if not date_str:
            return self._events
        return [event for event in self._events if event["date"] == date_str]

    def find_available_slots(self, date_str: str, duration_minutes: int = 30) -> List[Dict[str, Any]]:
        """
        Find available time slots on a given date during working hours (09:00 - 17:00).
        """
        existing_events = self.get_events(date_str)
        busy_times = []
        for event in existing_events:
            s_hour, s_min = map(int, event["start_time"].split(":"))
            e_hour, e_min = map(int, event["end_time"].split(":"))
            busy_times.append((s_hour * 60 + s_min, e_hour * 60 + e_min))
        
        # Working hours: 09:00 (540 min) to 17:00 (1020 min)
        work_start = 9 * 60
        work_end = 17 * 60
        available_slots = []
        
        current_time = work_start
        while current_time + duration_minutes <= work_end:
            slot_start = current_time
            slot_end = current_time + duration_minutes
            
            # Check overlap with any busy time
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
            
            current_time += 30 # Check in 30 min steps
            
        return available_slots

    def create_event(self, title: str, date_str: str, start_time: str, end_time: str, attendees: List[str], description: str = "") -> Dict[str, Any]:
        """Create a new calendar event (Mutating action)."""
        event_id = f"event_{uuid.uuid4().hex[:6]}"
        event = {
            "id": event_id,
            "title": title,
            "date": date_str,
            "start_time": start_time,
            "end_time": end_time,
            "attendees": attendees,
            "description": description,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self._events.append(event)
        return event

    def create_reminder(self, title: str, date_time_str: str) -> Dict[str, Any]:
        """Create a quick task reminder."""
        reminder_id = f"rem_{uuid.uuid4().hex[:6]}"
        reminder = {
            "id": reminder_id,
            "title": title,
            "date_time": date_time_str,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self._reminders.append(reminder)
        return reminder

# Global singleton instance for local testing
calendar_service = LocalCalendarService()
