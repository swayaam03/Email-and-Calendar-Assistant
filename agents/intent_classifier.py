from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from state.agent_state import AgentState
from config.constants import IntentType
from prompts.intent_prompts import INTENT_CLASSIFICATION_SYSTEM_PROMPT
from llm.openrouter_client import get_openrouter_llm

def classify_intent_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node that classifies the user query intent.
    Updates detected_intent and execution_log in AgentState.
    """
    query = state["user_query"].strip()
    query_lower = query.lower()
    
    # 1. Rule-based heuristic check for fast, 0-token matching
    detected = None
    if "summarize" in query_lower and ("email" in query_lower or "inbox" in query_lower):
        detected = IntentType.SUMMARIZE_INBOX.value
    elif "reply" in query_lower or "draft" in query_lower:
        detected = IntentType.DRAFT_REPLY.value
    elif "send" in query_lower and "email" in query_lower:
        detected = IntentType.SEND_EMAIL.value
    elif "schedule" in query_lower and ("meeting" in query_lower or "with" in query_lower):
        detected = IntentType.SCHEDULE_MEETING.value
    elif ("free" in query_lower or "available" in query_lower or "slot" in query_lower) and "calendar" in query_lower:
        detected = IntentType.FIND_SLOTS.value
    elif "schedule" in query_lower or "calendar" in query_lower or "event" in query_lower:
        detected = IntentType.CHECK_SCHEDULE.value
    elif "plan" in query_lower and ("day" in query_lower or "today" in query_lower):
        detected = IntentType.DAILY_PLAN.value
    elif "unread" in query_lower or "email" in query_lower or "inbox" in query_lower:
        detected = IntentType.READ_EMAIL.value

    # 2. LLM Classification fallback for complex natural language queries
    if not detected:
        try:
            llm = get_openrouter_llm(temperature=0.0)
            response = llm.invoke([
                SystemMessage(content=INTENT_CLASSIFICATION_SYSTEM_PROMPT),
                HumanMessage(content=query)
            ])
            llm_output = response.content.strip().upper()
            
            # Match against known enum values
            valid_intents = {item.value for item in IntentType}
            if llm_output in valid_intents:
                detected = llm_output
            else:
                detected = IntentType.GENERAL_QUERY.value
        except Exception:
            detected = IntentType.GENERAL_QUERY.value

    log_entry = f"Node [classify_intent]: Classified query into intent '{detected}'"
    return {
        "detected_intent": detected,
        "execution_log": state.get("execution_log", []) + [log_entry]
    }
