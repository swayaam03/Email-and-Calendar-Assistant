from langchain_core.tools import tool
from services.local_email_service import email_service
from config.constants import SystemLimits


@tool
def read_emails_tool(unread_only: bool = True) -> str:
    """
    Fetch emails from the inbox. Returns a compact summary of each email
    containing sender, subject, priority, and a truncated body snippet.

    Args:
        unread_only: If True, fetch only unread emails. If False, fetch all.
    """
    if unread_only:
        emails = email_service.get_unread_emails(limit=SystemLimits.MAX_EMAILS_PER_FETCH)
    else:
        emails = email_service.get_all_emails(limit=SystemLimits.MAX_EMAILS_PER_FETCH)

    if not emails:
        return "No emails found."

    # Build a compact, token-efficient summary string
    lines = []
    for i, email in enumerate(emails, 1):
        body_snippet = email["body"][:SystemLimits.MAX_EMAIL_BODY_LENGTH]
        lines.append(
            f"[{i}] ID: {email['id']}\n"
            f"    From: {email['sender_name']} <{email['sender']}>\n"
            f"    Subject: {email['subject']}\n"
            f"    Priority: {email['priority']} | Category: {email['category']}\n"
            f"    Time: {email['timestamp']}\n"
            f"    Body: {body_snippet}"
        )
    return "\n\n".join(lines)
