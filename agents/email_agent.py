import re
import json
from typing import Dict, Any
from state.agent_state import AgentState
from config.constants import IntentType
from tools.email.reader import read_emails_tool
from tools.email.search import search_emails_tool
from tools.email.drafter import create_draft_tool
from tools.utils.contact_lookup import contact_lookup_tool
from services.local_email_service import email_service
from llm.openrouter_client import get_openrouter_llm
from langchain_core.messages import SystemMessage, HumanMessage

def _extract_email_details(query: str) -> Dict[str, str]:
    """
    Dynamically extract recipient email, subject, and body from user query.
    1. Checks regex for explicit email addresses (e.g. user@domain.com).
    2. Uses contact lookup and search to resolve recipient addresses.
    3. Extracts message payload and generates contextual subject and body.
    """
    # 1. Look for explicit email addresses in the user query
    emails_found = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', query)
    target_email = emails_found[0] if emails_found else None

    # 2. Extract recipient name if no explicit email address
    recipient_name = None
    if not target_email:
        words = query.split()
        for i, word in enumerate(words):
            if word.lower() in ["to", "reply", "email", "with"]:
                if i + 1 < len(words):
                    potential = words[i+1].strip(".,!?:;\"'")
                    if len(potential) > 2 and potential.lower() not in ["the", "a", "an", "saying", "asking"]:
                        recipient_name = potential
                        break
        
        if recipient_name:
            contact_res = contact_lookup_tool.invoke({"name": recipient_name})
            emails_in_contact = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', contact_res)
            if emails_in_contact:
                target_email = emails_in_contact[0]
            else:
                search_res = email_service.search_emails(recipient_name)
                if search_res:
                    target_email = search_res[0]["sender"]

    if not target_email:
        target_email = f"{recipient_name.lower()}@example.com" if recipient_name else "recipient@example.com"

    # 3. Extract custom message payload from query (e.g. "saying ...")
    message_text = None
    query_lower = query.lower()
    for trigger in ["saying ", "that ", "telling ", "asking "]:
        if trigger in query_lower:
            idx = query_lower.find(trigger) + len(trigger)
            message_text = query[idx:].strip().strip(".'\"")
            break

    if not message_text:
        message_text = "I am following up regarding your request."

    # Build clean subject and body
    subject = "Update regarding your request"
    if "lecture" in message_text.lower():
        subject = "Absence regarding today's lecture"
    elif "meeting" in message_text.lower():
        subject = "Meeting attendance update"

    body = f"Hi,\n\n{message_text.capitalize()}.\n\nBest regards."

    return {
        "to_email": target_email,
        "subject": subject,
        "body": body
    }

def email_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node handling all email workflow intents:
    READ_EMAIL, SUMMARIZE_INBOX, DRAFT_REPLY, SEND_EMAIL.
    """
    intent = state.get("detected_intent")
    query = state.get("user_query", "")
    log = state.get("execution_log", []) + [f"Node [email_agent]: Processing email workflow for intent '{intent}'"]
    
    updates: Dict[str, Any] = {"execution_log": log}
    
    if intent in [IntentType.READ_EMAIL.value, IntentType.SUMMARIZE_INBOX.value]:
        emails = email_service.get_unread_emails(limit=5)
        raw_output = read_emails_tool.invoke({"unread_only": True})
        
        summary = f"Found {len(emails)} unread email(s):\n\n{raw_output}"
        updates["email_results"] = emails
        updates["email_summary"] = summary
        updates["final_response"] = summary

    elif intent in [IntentType.DRAFT_REPLY.value, IntentType.SEND_EMAIL.value]:
        extracted = _extract_email_details(query)
        target_email = extracted["to_email"]
        subject = extracted["subject"]
        body = extracted["body"]

        if intent == IntentType.DRAFT_REPLY.value:
            draft = email_service.create_draft(to_email=target_email, subject=subject, body=body)
            draft_msg = f"Created email draft for review:\n  To: {draft['to']}\n  Subject: {draft['subject']}\n  Body: {draft['body']}"
            updates["draft_email"] = draft
            updates["final_response"] = draft_msg
        else: # SEND_EMAIL
            pending = {
                "tool_name": "send_email_tool",
                "tool_args": {
                    "to_email": target_email,
                    "subject": subject,
                    "body": body
                },
                "reason": f"Sending email to {target_email} requires human confirmation."
            }
            updates["pending_action"] = pending
            updates["approval_required"] = True
            updates["approval_status"] = "PENDING"
            updates["final_response"] = f"Action Required: Proposed email to {target_email} requires your approval before sending."

    return updates
