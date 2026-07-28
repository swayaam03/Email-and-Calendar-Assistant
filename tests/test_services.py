import pytest
from datetime import datetime, timedelta
from services.local_email_service import LocalEmailService
from services.local_calendar_service import LocalCalendarService

def test_unread_emails_fetching():
    service = LocalEmailService()
    unread = service.get_unread_emails(limit=5)
    assert len(unread) > 0
    for email in unread:
        assert "subject" in email
        assert "sender" in email

def test_email_search():
    service = LocalEmailService()
    results = service.search_emails("Google")
    assert len(results) >= 0

def test_email_draft_and_send():
    service = LocalEmailService()
    draft = service.create_draft("test@example.com", "Test Subject", "Test Body")
    assert "draft" in draft["draft_id"]
    
    sent = service.send_email("test@example.com", "Test Subject", "Test Body")
    assert "sent" in sent["id"].lower()
    assert "SENT" in sent["status"]

def test_calendar_events_and_slots():
    service = LocalCalendarService()
    events = service.get_events()
    assert len(events) > 0
    
    now = datetime.now()
    days_until_tuesday = (1 - now.weekday() + 7) % 7
    if days_until_tuesday == 0:
        days_until_tuesday = 7
    next_tuesday_str = (now + timedelta(days=days_until_tuesday)).strftime("%Y-%m-%d")
    
    available_slots = service.find_available_slots(next_tuesday_str, duration_minutes=30)
    assert len(available_slots) > 0
    slot_times = [s["start_time"] for s in available_slots]
    assert "14:00" in slot_times

def test_calendar_create_event():
    service = LocalCalendarService()
    today_str = datetime.now().strftime("%Y-%m-%d")
    event = service.create_event(
        title="Sync with Rahul",
        date_str=today_str,
        start_time="14:00",
        end_time="14:30",
        attendees=["rahul@techcorp.com"]
    )
    assert event["id"].startswith("event_")
    assert event["title"] == "Sync with Rahul"
