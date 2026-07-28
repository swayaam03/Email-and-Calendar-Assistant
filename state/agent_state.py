from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    Central LangGraph state object that evolves as nodes execute.
    
    Fields:
    - messages: Conversation history with automatic message appending via add_messages.
    - user_query: Original user input prompt.
    - detected_intent: IntentType string (e.g. READ_EMAIL, SCHEDULE_MEETING, DAILY_PLAN).
    - email_results: List of email dictionaries retrieved by email tools.
    - email_summary: Generated inbox/email summary text.
    - draft_email: Dict containing target email draft {to, subject, body, reply_to_id}.
    - calendar_events: List of calendar event dictionaries.
    - available_slots: List of open meeting time slots.
    - selected_slot: Slot chosen for meeting creation.
    - pending_action: Proposed tool call needing human review {tool_name, tool_args, reason}.
    - approval_required: True if hitting HITL gate before mutating action.
    - approval_status: "PENDING", "APPROVED", or "REJECTED".
    - execution_log: List of trace messages documenting node execution.
    - final_response: Final user-facing response string.
    """
    messages: Annotated[List[Any], add_messages]
    user_query: str
    detected_intent: Optional[str]
    email_results: Optional[List[Dict[str, Any]]]
    email_summary: Optional[str]
    draft_email: Optional[Dict[str, Any]]
    calendar_events: Optional[List[Dict[str, Any]]]
    available_slots: Optional[List[Dict[str, Any]]]
    selected_slot: Optional[Dict[str, Any]]
    pending_action: Optional[Dict[str, Any]]
    approval_required: bool
    approval_status: Optional[str]
    execution_log: List[str]
    final_response: Optional[str]

def create_initial_state(user_query: str) -> AgentState:
    """Helper function to create a clean initial state for a user query."""
    return {
        "messages": [],
        "user_query": user_query,
        "detected_intent": None,
        "email_results": None,
        "email_summary": None,
        "draft_email": None,
        "calendar_events": None,
        "available_slots": None,
        "selected_slot": None,
        "pending_action": None,
        "approval_required": False,
        "approval_status": None,
        "execution_log": [f"Initialized graph for query: '{user_query}'"],
        "final_response": None,
    }
