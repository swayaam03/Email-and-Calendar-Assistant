from typing import Dict, Any
from datetime import datetime
from state.agent_state import AgentState
from services.local_email_service import email_service
from services.local_calendar_service import calendar_service
from llm.openrouter_client import get_openrouter_llm
from langchain_core.messages import SystemMessage, HumanMessage

SYSTEM_GENERAL_ASSISTANT_PROMPT = """You are an Executive AI Assistant.
Respond politely, concisely, and helpfully to the user's query.
If they are asking a general question, answer directly.
If they are greeting you, greet them professionally.
Keep your response under 100 words.
"""

def planner_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node for constructing a Daily Productivity Plan or dynamically answering General Queries via OpenRouter LLM.
    """
    intent = state.get("detected_intent")
    query = state.get("user_query", "")
    log = state.get("execution_log", []) + [f"Node [planner_agent]: Processing request for intent '{intent}'"]
    
    updates: Dict[str, Any] = {"execution_log": log}
    
    if intent == "DAILY_PLAN":
        today_str = datetime.now().strftime("%Y-%m-%d")
        events = calendar_service.get_events(today_str)
        unread_emails = email_service.get_unread_emails(limit=3)
        
        # Build structured daily plan
        lines = [
            f"DAILY EXECUTIVE PLAN ({today_str})",
            "----------------------------------------",
            "1. TODAY'S SCHEDULED MEETINGS:"
        ]
        if events:
            for ev in events:
                lines.append(f"   • {ev['start_time']} - {ev['end_time']}: {ev['title']}")
        else:
            lines.append("   • No scheduled meetings for today.")
            
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
        # Dynamic LLM response for general queries (No hardcoded text)
        try:
            llm = get_openrouter_llm(temperature=0.7)
            response = llm.invoke([
                SystemMessage(content=SYSTEM_GENERAL_ASSISTANT_PROMPT),
                HumanMessage(content=query)
            ])
            updates["final_response"] = response.content.strip()
        except Exception:
            updates["final_response"] = f"I am your AI Executive Assistant. How can I help you manage your emails, calendar, or daily plan today?"
        
    return updates
