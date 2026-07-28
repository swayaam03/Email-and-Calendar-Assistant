import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from services.real_email_service import real_email_service

class LocalEmailService:
    """
    A zero-config, in-memory email storage and management service.
    Replaces Gmail API dependency with pre-seeded, realistic email threads.
    """
    def __init__(self):
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        
        # Pre-seeded sample inbox
        self._emails: List[Dict[str, Any]] = [
            {
                "id": "email_1",
                "sender": "rahul.sharma@techcorp.com",
                "sender_name": "Rahul Sharma",
                "subject": "Project Review Meeting Request",
                "body": "Hi, are you free next Tuesday afternoon around 2 PM to discuss the Q3 Agentic AI roadmap? Let me know if that works or propose another slot.",
                "timestamp": (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
                "is_unread": True,
                "category": "Meeting Request",
                "priority": "High"
            },
            {
                "id": "email_2",
                "sender": "sarah.jenkins@designstudio.io",
                "sender_name": "Sarah Jenkins",
                "subject": "Updated UI Mockups for Executive Assistant",
                "body": "Hey! I have finalized the dark mode UI mockups for the dashboard. Please review the attached specs when you get a chance.",
                "timestamp": (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"),
                "is_unread": True,
                "category": "Project Update",
                "priority": "Medium"
            },
            {
                "id": "email_3",
                "sender": "john.doe@company.org",
                "sender_name": "John Doe",
                "subject": "Attending tomorrow's Strategy Meeting",
                "body": "Hi, just confirming if you will be attending tomorrow's strategy alignment session at 10 AM. Please reply to confirm.",
                "timestamp": yesterday.strftime("%Y-%m-%d %H:%M"),
                "is_unread": True,
                "category": "Confirmation Request",
                "priority": "High"
            },
            {
                "id": "email_4",
                "sender": "newsletter@techinsider.com",
                "sender_name": "Tech Insider Digest",
                "subject": "Weekly AI Research Round-up",
                "body": "Discover the latest trends in autonomous multi-agent orchestration, tool usage, and LLM benchmarking.",
                "timestamp": yesterday.strftime("%Y-%m-%d %H:%M"),
                "is_unread": False,
                "category": "Newsletter",
                "priority": "Low"
            }
        ]
        
        self._drafts: List[Dict[str, Any]] = []
        self._sent_emails: List[Dict[str, Any]] = []

    def get_unread_emails(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetch unread emails. Uses RealEmailService if configured, else local storage."""
        if real_email_service.is_configured():
            real_emails = real_email_service.get_unread_emails(limit=limit)
            if real_emails:
                return real_emails
        unread = [email for email in self._emails if email.get("is_unread", False)]
        return unread[:limit]

    def get_all_emails(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch inbox emails up to limit."""
        if real_email_service.is_configured():
            real_emails = real_email_service.get_unread_emails(limit=limit)
            if real_emails:
                return real_emails
        return self._emails[:limit]

    def search_emails(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search emails matching query."""
        if real_email_service.is_configured():
            real_results = real_email_service.search_emails(query, limit=limit)
            if real_results:
                return real_results

        q = query.lower()
        results = []
        for email in self._emails:
            if (q in email["sender"].lower() or 
                q in email["sender_name"].lower() or 
                q in email["subject"].lower() or 
                q in email["body"].lower()):
                results.append(email)
        return results[:limit]

    def get_email_by_id(self, email_id: str) -> Optional[Dict[str, Any]]:
        """Find an email by ID."""
        for email in self._emails:
            if email["id"] == email_id:
                return email
        return None

    def create_draft(self, to_email: str, subject: str, body: str, reply_to_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a draft reply."""
        if real_email_service.is_configured():
            return real_email_service.create_draft(to_email, subject, body, reply_to_id)

        draft_id = f"draft_{uuid.uuid4().hex[:6]}"
        draft = {
            "draft_id": draft_id,
            "to": to_email,
            "subject": subject,
            "body": body,
            "reply_to_id": reply_to_id,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self._drafts.append(draft)
        return draft

    def send_email(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        """Send an email. Dispatches to real SMTP if configured."""
        if real_email_service.is_configured():
            return real_email_service.send_email(to_email, subject, body)

        sent_id = f"sent_{uuid.uuid4().hex[:6]}"
        sent_record = {
            "id": sent_id,
            "to": to_email,
            "subject": subject,
            "body": body,
            "sent_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "SENT"
        }
        self._sent_emails.append(sent_record)
        return sent_record

# Global singleton instance
email_service = LocalEmailService()
