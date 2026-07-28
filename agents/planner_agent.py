from typing import Dict, Any
from datetime import datetime
from state.agent_state import AgentState
from services.local_email_service import email_service
from services.local_calendar_service import calendar_service

def planner_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node for constructing a Daily Productivity Plan or handling General Queries.
    Combines inbox highlights with today's calendar schedule.
    """
    intent = state.get("detected_intent")
    query = state.get("user_query", "")
    log = state.get("execution_log", []) + [f"Node [planner_agent]: Synthesizing executive plan for intent '{intent}'"]
    
    updates: Dict[str, Any] = {"execution_log": log}
    
    if intent == "DAILY_PLAN":
        today_str = datetime.now().strftime("%Y-%m-%d")
        events = calendar_service.get_events(today_str)
        unread_emails = email_service.get_unread_emails(limit=3)
        
        # Build structured daily plan
        lines = [
            f"📅 DAILY EXECUTIVE PLAN ({today_str})",
            "----------------------------------------",
            "1. TODAY'S SCHEDULED MEETINGS:"
        ]
        if events:
            for ev in events:
                lines.append(f"   • {ev['start_time']} - {ev['end_time']}: {ev['title']}")
        else:
            lines.append("   • No scheduled meetings for today. Open calendar!")
            
        lines.append("\n2. HIGH PRIORITY UNREAD EMAILS:")
        if unread_emails:
            for em in unread_emails:
                lines.append(f"   • [{em['priority']}] {em['sender_name']}: {em['subject']}")
        else:
            lines.append("   • Inbox zero! No unread emails.")
            
        lines.append("\n3. RECOMMENDED ACTIONS:")
        lines.append("   • Review and reply to priority emails above.")
        lines.append("   • Focus block available in afternoon.")
        
        plan_output = "\n".join(lines)
        updates["final_response"] = plan_output
    else:
        # General query response
        updates["final_response"] = (
            f"I am your AI Executive Assistant. I understood your query: '{query}'. "
            "I can manage your unread emails, draft replies, check your calendar schedule, "
            "find open meeting slots, and construct daily productivity plans."
        )
        
    return updates
