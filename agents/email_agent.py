from typing import Dict, Any
from state.agent_state import AgentState
from config.constants import IntentType
from tools.email.reader import read_emails_tool
from tools.email.search import search_emails_tool
from tools.email.drafter import create_draft_tool
from tools.utils.contact_lookup import contact_lookup_tool
from services.local_email_service import email_service

def email_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node handling all email workflow intents:
    READ_EMAIL, SUMMARIZE_INBOX, DRAFT_REPLY, SEND_EMAIL.
    """
    intent = state.get("detected_intent")
    query = state.get("user_query", "")
    log = state.get("execution_log", []) + [f"Node [email_agent]: Processing email workflow for intent '{intent}'"]
    
    # Default updates
    updates: Dict[str, Any] = {"execution_log": log}
    
    if intent == IntentType.READ_EMAIL.value or intent == IntentType.SUMMARIZE_INBOX.value:
        emails = email_service.get_unread_emails(limit=5)
        raw_output = read_emails_tool.invoke({"unread_only": True})
        
        summary = f"Found {len(emails)} unread email(s):\n\n{raw_output}"
        updates["email_results"] = emails
        updates["email_summary"] = summary
        updates["final_response"] = summary

    elif intent == IntentType.DRAFT_REPLY.value:
        # Resolve target recipient from query
        target_name = "John" if "john" in query.lower() else ("Rahul" if "rahul" in query.lower() else "Sarah")
        contact_info = contact_lookup_tool.invoke({"name": target_name})
        
        # Search relative email
        search_res = email_service.search_emails(target_name)
        target_email = "john.doe@company.org"
        subject = f"Re: Follow-up regarding {target_name}"
        body = f"Hi {target_name},\n\nThanks for reaching out! I confirm that I will attend as requested.\n\nBest regards,\nExecutive Assistant"
        
        if search_res:
            target_email = search_res[0]["sender"]
            subject = f"Re: {search_res[0]['subject']}"
            
        draft = email_service.create_draft(to_email=target_email, subject=subject, body=body)
        draft_msg = f"Created email draft for review:\n  To: {draft['to']}\n  Subject: {draft['subject']}\n  Body: {draft['body']}"
        
        updates["draft_email"] = draft
        updates["final_response"] = draft_msg

    elif intent == IntentType.SEND_EMAIL.value:
        target_name = "John" if "john" in query.lower() else ("Rahul" if "rahul" in query.lower() else "Sarah")
        search_res = email_service.search_emails(target_name)
        target_email = search_res[0]["sender"] if search_res else "john.doe@company.org"
        subject = f"Re: Confirmation for {target_name}"
        body = f"Hi {target_name},\n\nI confirm I will attend the upcoming meeting.\n\nBest regards."
        
        # Prepare HITL pending action
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
