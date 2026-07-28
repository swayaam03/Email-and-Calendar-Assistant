from langchain_core.tools import tool
from services.local_email_service import email_service
from config.constants import SystemLimits


@tool
def search_emails_tool(query: str) -> str:
    """
    Search emails by keyword. Matches against sender name, email address,
    subject, and body content. Returns compact results.

    Args:
        query: The search keyword (e.g. a person's name, topic, or phrase).
    """
    results = email_service.search_emails(query, limit=SystemLimits.MAX_EMAILS_PER_FETCH)

    if not results:
        return f"No emails found matching '{query}'."

    lines = []
    for i, email in enumerate(results, 1):
        body_snippet = email["body"][:SystemLimits.MAX_EMAIL_BODY_LENGTH]
        lines.append(
            f"[{i}] ID: {email['id']}\n"
            f"    From: {email['sender_name']} <{email['sender']}>\n"
            f"    Subject: {email['subject']}\n"
            f"    Body: {body_snippet}"
        )
    return "\n\n".join(lines)
