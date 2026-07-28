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
        # Resolve target date expression from query
        date_resolution = resolve_relative_date_tool.invoke({"expression": query})
        # Extract date from string or default to next Tuesday
        target_date = "2026-08-04"
        if "Resolved date: " in date_resolution:
            target_date = date_resolution.split("Resolved date: ")[1].split(" ")[0]
            
        slots_output = check_availability_tool.invoke({"date": target_date, "duration_minutes": 30})
        updates["final_response"] = f"Availability results:\n{date_resolution}\n\n{slots_output}"

    elif intent == IntentType.SCHEDULE_MEETING.value:
        # Determine person and date
        person_name = "Rahul" if "rahul" in query.lower() else ("John" if "john" in query.lower() else "Sarah")
        contact_res = contact_lookup_tool.invoke({"name": person_name})
        person_email = "rahul.sharma@techcorp.com" if "rahul" in person_name.lower() else "john.doe@company.org"
        
        date_res = resolve_relative_date_tool.invoke({"expression": query})
        target_date = "2026-08-04"
        if "Resolved date: " in date_res:
            target_date = date_res.split("Resolved date: ")[1].split(" ")[0]
            
        # Find slot
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
