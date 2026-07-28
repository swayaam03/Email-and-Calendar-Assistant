from langchain_core.tools import tool
from services.local_email_service import email_service


@tool
def send_email_tool(to_email: str, subject: str, body: str) -> str:
    """
    Send an email to a recipient. THIS IS A MUTATING ACTION.
    Only call this tool AFTER the user has approved the draft.

    Args:
        to_email: Recipient email address.
        subject: Email subject line.
        body: Full email body text.
    """
    result = email_service.send_email(
        to_email=to_email,
        subject=subject,
        body=body,
    )
    return (
        f"Email sent successfully.\n"
        f"  Sent ID: {result['id']}\n"
        f"  To: {result['to']}\n"
        f"  Subject: {result['subject']}\n"
        f"  Status: {result['status']}"
    )
