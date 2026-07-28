import re
from typing import Dict, Any
from state.agent_state import AgentState
from config.constants import IntentType
from tools.calendar.reader import get_schedule_tool
from tools.calendar.availability import check_availability_tool
from tools.utils.date_time_tool import resolve_relative_date_tool
from tools.utils.contact_lookup import contact_lookup_tool
from services.local_calendar_service import calendar_service

def calendar_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node handling all calendar & scheduling workflows:
    CHECK_SCHEDULE, FIND_SLOTS, SCHEDULE_MEETING.
    """
    intent = state.get("detected_intent")
    query = state.get("user_query", "")
    log = state.get("execution_log", []) + [f"Node [calendar_agent]: Processing calendar workflow for intent '{intent}'"]
    
    updates: Dict[str, Any] = {"execution_log": log}
    
    if intent == IntentType.CHECK_SCHEDULE.value:
        schedule_output = get_schedule_tool.invoke({"date": ""})
        updates["final_response"] = f"Your upcoming calendar schedule:\n\n{schedule_output}"

    elif intent == IntentType.FIND_SLOTS.value:
        date_resolution = resolve_relative_date_tool.invoke({"expression": query})
        target_date = "2026-08-04"
        if "Resolved date: " in date_resolution:
            target_date = date_resolution.split("Resolved date: ")[1].split(" ")[0]
            
        slots_output = check_availability_tool.invoke({"date": target_date, "duration_minutes": 30})
        updates["final_response"] = f"Availability results:\n{date_resolution}\n\n{slots_output}"

    elif intent == IntentType.SCHEDULE_MEETING.value:
        # Extract explicit email address or contact name
        emails_found = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', query)
        person_email = emails_found[0] if emails_found else None
        person_name = person_email if person_email else "Rahul"

        if not person_email:
            words = query.split()
            for i, word in enumerate(words):
                if word.lower() in ["with", "to", "meeting"]:
                    if i + 1 < len(words):
                        potential = words[i+1].strip(".,!?:;\"'")
                        if len(potential) > 2 and potential.lower() not in ["the", "a", "an", "next", "tomorrow"]:
                            person_name = potential
                            break
            
            contact_res = contact_lookup_tool.invoke({"name": person_name})
            contact_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', contact_res)
            if contact_emails:
                person_email = contact_emails[0]
            else:
                person_email = "rahul.sharma@techcorp.com"
        
        date_res = resolve_relative_date_tool.invoke({"expression": query})
        target_date = "2026-08-04"
        if "Resolved date: " in date_res:
            target_date = date_res.split("Resolved date: ")[1].split(" ")[0]
            
        slots = calendar_service.find_available_slots(target_date, duration_minutes=30)
        selected_slot = slots[0] if slots else {"start_time": "14:00", "end_time": "14:30"}
        
        pending = {
            "tool_name": "create_event_tool",
            "tool_args": {
                "title": f"Meeting with {person_name}",
                "date": target_date,
                "start_time": selected_slot["start_time"],
                "end_time": selected_slot["end_time"],
                "attendees": person_email,
                "description": f"Scheduled meeting requested via assistant for {person_name}."
            },
            "reason": f"Creating calendar meeting on {target_date} at {selected_slot['start_time']} with {person_name} requires approval."
        }
        
        updates["selected_slot"] = selected_slot
        updates["pending_action"] = pending
        updates["approval_required"] = True
        updates["approval_status"] = "PENDING"
        updates["final_response"] = (
            f"Action Required: Proposed meeting with {person_name} on {target_date} "
            f"({selected_slot['start_time']} - {selected_slot['end_time']}) requires your approval."
        )

    return updates
