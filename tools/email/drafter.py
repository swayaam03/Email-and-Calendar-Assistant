from langchain_core.tools import tool
from services.local_email_service import email_service


@tool
def create_draft_tool(to_email: str, subject: str, body: str, reply_to_id: str = "") -> str:
    """
    Create an email draft. Use this before sending to allow human review.

    Args:
        to_email: Recipient email address.
        subject: Email subject line.
        body: Full email body text.
        reply_to_id: Optional original email ID if this is a reply.
    """
    reply_id = reply_to_id if reply_to_id else None
    draft = email_service.create_draft(
        to_email=to_email,
        subject=subject,
        body=body,
        reply_to_id=reply_id,
    )
    return (
        f"Draft created successfully.\n"
        f"  Draft ID: {draft['draft_id']}\n"
        f"  To: {draft['to']}\n"
        f"  Subject: {draft['subject']}\n"
        f"  Body: {draft['body']}"
    )
