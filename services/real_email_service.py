import imaplib
import smtplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Any, Optional
from config.settings import settings

class RealEmailService:
    """
    Real IMAP / SMTP email service connecting directly to Gmail, Outlook, or any standard mail server.
    Uses SSL for IMAP (port 993) and TLS for SMTP (port 587).
    """
    def __init__(self):
        self.email_address = settings.EMAIL_ADDRESS
        self.app_password = settings.EMAIL_APP_PASSWORD
        self.imap_server = settings.IMAP_SERVER or "imap.gmail.com"
        self.imap_port = settings.IMAP_PORT or 993
        self.smtp_server = settings.SMTP_SERVER or "smtp.gmail.com"
        self.smtp_port = settings.SMTP_PORT or 587
        
        self._drafts: List[Dict[str, Any]] = []

    def is_configured(self) -> bool:
        """Return True if real email credentials are configured in .env."""
        if not self.email_address or not self.app_password:
            return False
        if "your.email" in self.email_address or "your_16_char" in self.app_password:
            return False
        return True

    def _decode_header_str(self, header_value: Optional[str]) -> str:
        """Helper to decode MIME encoded headers."""
        if not header_value:
            return ""
        decoded_list = decode_header(header_value)
        header_text = ""
        for bytes_or_str, encoding in decoded_list:
            if isinstance(bytes_or_str, bytes):
                header_text += bytes_or_str.decode(encoding or "utf-8", errors="ignore")
            else:
                header_text += str(bytes_or_str)
        return header_text

    def _extract_body(self, msg: email.message.Message) -> str:
        """Extract plain text payload from an email message."""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body += payload.decode(part.get_content_charset() or "utf-8", errors="ignore")
                        break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode(msg.get_content_charset() or "utf-8", errors="ignore")
        return body.strip() or "(No text body)"

    def get_unread_emails(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetch unread emails from real IMAP server."""
        if not self.is_configured():
            return []

        emails_found = []
        mail = None
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.app_password)
            mail.select("INBOX")

            _, search_data = mail.search(None, "UNSEEN")
            mail_ids = search_data[0].split()
            
            # Process latest unread emails up to limit
            recent_ids = mail_ids[-limit:] if len(mail_ids) >= limit else mail_ids
            recent_ids.reverse()

            for msg_id in recent_ids:
                _, msg_data = mail.fetch(msg_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = self._decode_header_str(msg.get("Subject"))
                        sender = self._decode_header_str(msg.get("From"))
                        date_str = msg.get("Date", "")
                        body = self._extract_body(msg)

                        emails_found.append({
                            "id": f"imap_{msg_id.decode('utf-8')}",
                            "sender": sender,
                            "sender_name": sender.split("<")[0].strip() if "<" in sender else sender,
                            "subject": subject or "(No Subject)",
                            "body": body[:settings.MAX_EMAIL_BODY_LENGTH],
                            "timestamp": date_str[:25] if date_str else datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "is_unread": True,
                            "category": "Inbox Email",
                            "priority": "Medium"
                        })
        except Exception as e:
            print(f"[RealEmailService] IMAP error: {e}")
        finally:
            if mail:
                try:
                    mail.close()
                    mail.logout()
                except Exception:
                    pass

        return emails_found

    def search_emails(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search emails matching query from IMAP inbox."""
        if not self.is_configured():
            return []

        results = []
        mail = None
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.app_password)
            mail.select("INBOX")

            # Search subject or body
            _, search_data = mail.search(None, f'TEXT "{query}"')
            mail_ids = search_data[0].split()
            recent_ids = mail_ids[-limit:] if len(mail_ids) >= limit else mail_ids
            recent_ids.reverse()

            for msg_id in recent_ids:
                _, msg_data = mail.fetch(msg_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = self._decode_header_str(msg.get("Subject"))
                        sender = self._decode_header_str(msg.get("From"))
                        body = self._extract_body(msg)

                        results.append({
                            "id": f"imap_{msg_id.decode('utf-8')}",
                            "sender": sender,
                            "sender_name": sender.split("<")[0].strip() if "<" in sender else sender,
                            "subject": subject or "(No Subject)",
                            "body": body[:settings.MAX_EMAIL_BODY_LENGTH],
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "is_unread": False,
                            "category": "SearchResult",
                            "priority": "Medium"
                        })
        except Exception as e:
            print(f"[RealEmailService] IMAP Search error: {e}")
        finally:
            if mail:
                try:
                    mail.close()
                    mail.logout()
                except Exception:
                    pass

        return results

    def create_draft(self, to_email: str, subject: str, body: str, reply_to_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a draft reply locally."""
        draft = {
            "draft_id": f"draft_real_{len(self._drafts)+1}",
            "to": to_email,
            "subject": subject,
            "body": body,
            "reply_to_id": reply_to_id,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self._drafts.append(draft)
        return draft

    def send_email(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        """Send a real email via SMTP TLS."""
        if not self.is_configured():
            raise ValueError("Real email credentials (EMAIL_ADDRESS & EMAIL_APP_PASSWORD) not configured in .env")

        msg = MIMEMultipart()
        msg["From"] = self.email_address
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        server = None
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.app_password)
            server.sendmail(self.email_address, [to_email], msg.as_string())
            
            return {
                "id": f"smtp_sent_{int(datetime.now().timestamp())}",
                "to": to_email,
                "subject": subject,
                "body": body,
                "sent_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "status": "SENT_VIA_SMTP"
            }
        except Exception as e:
            print(f"[RealEmailService] SMTP send error: {e}")
            raise RuntimeError(f"Failed to send email via SMTP: {str(e)}")
        finally:
            if server:
                try:
                    server.quit()
                except Exception:
                    pass

real_email_service = RealEmailService()
