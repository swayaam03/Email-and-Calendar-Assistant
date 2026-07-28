from state.agent_state import AgentState
from config.constants import IntentType

def route_intent(state: AgentState) -> str:
    """
    Conditional edge router after classify_intent node.
    Routes to email_agent, calendar_agent, or planner_agent based on detected_intent.
    """
    intent = state.get("detected_intent")
    
    if intent in [
        IntentType.READ_EMAIL.value,
        IntentType.SUMMARIZE_INBOX.value,
        IntentType.DRAFT_REPLY.value,
        IntentType.SEND_EMAIL.value,
    ]:
        return "email_agent"
        
    elif intent in [
        IntentType.CHECK_SCHEDULE.value,
        IntentType.FIND_SLOTS.value,
        IntentType.SCHEDULE_MEETING.value,
    ]:
        return "calendar_agent"
        
    else:
        return "planner_agent"

def route_after_agent(state: AgentState) -> str:
    """
    Conditional edge router after email_agent, calendar_agent, or planner_agent.
    Routes to approval_node if Human-in-the-Loop review is required, otherwise to END.
    """
    if state.get("approval_required") and state.get("approval_status") == "PENDING":
        return "approval_node"
    return "__end__"
