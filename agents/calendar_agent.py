import re
from datetime import datetime
from typing import Dict, Any
from state.agent_state import AgentState
from config.constants import IntentType
from tools.calendar.reader import get_schedule_tool
from tools.calendar.availability import check_availability_tool
from tools.utils.date_time_tool import resolve_relative_date_tool
from tools.utils.contact_lookup import contact_lookup_tool
from services.local_calendar_service import calendar_service

_MONTHS_MAP = {
    "january": "01", "jan": "01",
    "february": "02", "feb": "02",
    "march": "03", "mar": "03",
    "april": "04", "apr": "04",
    "may": "05",
    "june": "06", "jun": "06",
    "july": "07", "jul": "07",
    "august": "08", "aug": "08",
    "september": "09", "sep": "09",
    "october": "10", "oct": "10",
    "november": "11", "nov": "11",
    "december": "12", "dec": "12"
}

def _parse_explicit_date(query: str) -> str:
    """
    Parse explicit dates from query string like '30th July', 'July 30', '30 July 2026'.
    Returns date in YYYY-MM-DD format.
    """
    query_lower = query.lower()
    now = datetime.now()
    year = now.year

    # Check for month name in query
    found_month = None
    for month_name, month_num in _MONTHS_MAP.items():
        if month_name in query_lower:
            found_month = month_num
            break

    if found_month:
        # Search for day number near month
        day_match = re.search(r'\b(\d{1,2})(?:st|nd|rd|th)?\b', query_lower)
        if day_match:
            day_num = int(day_match.group(1))
            if 1 <= day_num <= 31:
                return f"{year}-{found_month}-{day_num:02d}"

    # Fallback to resolve_relative_date_tool
    date_res = resolve_relative_date_tool.invoke({"expression": query})
    if "Resolved date: " in date_res:
        return date_res.split("Resolved date: ")[1].split(" ")[0]
        
    return now.strftime("%Y-%m-%d")

def _extract_calendar_event_details(query: str) -> Dict[str, Any]:
    """
    Dynamically extract event title, target date, attendees, and description.
    """
    query_lower = query.lower()
    target_date = _parse_explicit_date(query)
    
    # Extract explicit email address if present
    emails_found = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', query)
    attendee_email = emails_found[0] if emails_found else None

    # Parse title & person name
    title = "Calendar Event"
    person_name = None

    if "birthday" in query_lower:
        for marker in ["of ", "for ", "is "]:
            if marker in query_lower:
                idx = query_lower.find(marker) + len(marker)
                person_name = query[idx:].strip().strip(".,!?")
                break
        if not person_name:
            words = query.split()
            if len(words) >= 2:
                person_name = " ".join(words[-2:])

        title = f"Birthday - {person_name}" if person_name else "Birthday Celebration"
    else:
        for marker in ["with ", "to ", "meeting ", "for "]:
            if marker in query_lower:
                idx = query_lower.find(marker) + len(marker)
                potential_name = query[idx:].split(" at ")[0].split(" on ")[0].strip().strip(".,!?")
                if len(potential_name) > 2:
                    person_name = potential_name
                    break
        
        if person_name:
            title = f"Meeting with {person_name}"
        else:
            title = "Scheduled Meeting"

    if not attendee_email and person_name:
        contact_res = contact_lookup_tool.invoke({"name": person_name.split()[0]})
        contact_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', contact_res)
        if contact_emails:
            attendee_email = contact_emails[0]
        else:
            attendee_email = f"{person_name.lower().replace(' ', '.')}@example.com"
    elif not attendee_email:
        attendee_email = "organizer@example.com"

    return {
        "title": title,
        "date": target_date,
        "attendees": attendee_email,
        "person_name": person_name or "Event",
        "description": f"Calendar entry for {title} created via AI Executive Assistant."
    }

def calendar_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node handling all calendar & scheduling workflows:
    CHECK_SCHEDULE, FIND_SLOTS, SCHEDULE_MEETING.
    """
    intent = state.get("detected_intent")
    query = state.get("user_query", "")
    query_lower = query.lower()
    log = state.get("execution_log", []) + [f"Node [calendar_agent]: Processing calendar workflow for intent '{intent}'"]
    
    updates: Dict[str, Any] = {"execution_log": log}
    
    if intent == IntentType.CHECK_SCHEDULE.value:
        target_date = _parse_explicit_date(query)
        # Check if query specifically mentioned a date/day vs asking for general upcoming schedule
        has_specific_date = (
            any(m in query_lower for m in _MONTHS_MAP.keys()) or 
            any(rel in query_lower for rel in ["today", "tomorrow", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]) or
            bool(re.search(r'\b\d{1,2}(st|nd|rd|th)?\b', query_lower))
        )
        
        if has_specific_date:
            schedule_output = get_schedule_tool.invoke({"date": target_date})
            updates["final_response"] = f"Your schedule for {target_date}:\n\n{schedule_output}"
        else:
            schedule_output = get_schedule_tool.invoke({"date": ""})
            updates["final_response"] = f"Your upcoming calendar schedule:\n\n{schedule_output}"

    elif intent == IntentType.FIND_SLOTS.value:
        target_date = _parse_explicit_date(query)
        slots_output = check_availability_tool.invoke({"date": target_date, "duration_minutes": 30})
        updates["final_response"] = f"Availability results for {target_date}:\n\n{slots_output}"

    elif intent in [IntentType.SCHEDULE_MEETING.value, IntentType.CREATE_REMINDER.value, IntentType.GENERAL_QUERY.value]:
        details = _extract_calendar_event_details(query)
        target_date = details["date"]
        title = details["title"]
        attendee_email = details["attendees"]
        person_name = details["person_name"]
            
        slots = calendar_service.find_available_slots(target_date, duration_minutes=30)
        selected_slot = slots[0] if slots else {"start_time": "09:00", "end_time": "09:30"}
        
        pending = {
            "tool_name": "create_event_tool",
            "tool_args": {
                "title": title,
                "date": target_date,
                "start_time": selected_slot["start_time"],
                "end_time": selected_slot["end_time"],
                "attendees": attendee_email,
                "description": details["description"]
            },
            "reason": f"Creating calendar event '{title}' on {target_date} at {selected_slot['start_time']} requires approval."
        }
        
        updates["selected_slot"] = selected_slot
        updates["pending_action"] = pending
        updates["approval_required"] = True
        updates["approval_status"] = "PENDING"
        updates["final_response"] = (
            f"Action Required: Proposed event '{title}' on {target_date} "
            f"({selected_slot['start_time']} - {selected_slot['end_time']}) requires your approval."
        )

    return updates
