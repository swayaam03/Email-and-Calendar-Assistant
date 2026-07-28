import pytest
from datetime import datetime, timedelta
from tools.email.reader import read_emails_tool
from tools.email.search import search_emails_tool
from tools.email.drafter import create_draft_tool
from tools.email.sender import send_email_tool
from tools.calendar.reader import get_schedule_tool
from tools.calendar.availability import check_availability_tool
from tools.calendar.creator import create_event_tool
from tools.utils.date_time_tool import get_current_datetime_tool, resolve_relative_date_tool
from tools.utils.contact_lookup import contact_lookup_tool


# ──────────────────── Email Tool Tests ────────────────────

def test_read_emails_tool():
    result = read_emails_tool.invoke({"unread_only": True})
    assert "Subject:" in result
    assert "From:" in result

def test_search_emails_tool_found():
    result = search_emails_tool.invoke({"query": "Google"})
    assert "Subject:" in result or "No emails found" in result

def test_search_emails_tool_not_found():
    result = search_emails_tool.invoke({"query": "nonexistent_query_xyz_999"})
    assert "No emails found" in result

def test_create_draft_tool():
    result = create_draft_tool.invoke({
        "to_email": "test@example.com",
        "subject": "Re: Meeting",
        "body": "I'll attend.",
        "reply_to_id": "email_3"
    })
    assert "Draft created successfully" in result
    assert "Draft ID:" in result

def test_send_email_tool():
    result = send_email_tool.invoke({
        "to_email": "test@example.com",
        "subject": "Re: Meeting",
        "body": "I'll attend."
    })
    assert "Email sent successfully" in result
    assert "SENT" in result


# ──────────────────── Calendar Tool Tests ────────────────────

def test_get_schedule_tool_all():
    result = get_schedule_tool.invoke({"date": ""})
    assert "Daily Engineering Standup" in result

def test_get_schedule_tool_empty_day():
    result = get_schedule_tool.invoke({"date": "2099-01-01"})
    assert "No" in result

def test_check_availability_tool():
    now = datetime.now()
    days_until_tuesday = (1 - now.weekday() + 7) % 7
    if days_until_tuesday == 0:
        days_until_tuesday = 7
    next_tuesday = (now + timedelta(days=days_until_tuesday)).strftime("%Y-%m-%d")
    result = check_availability_tool.invoke({"date": next_tuesday, "duration_minutes": 30})
    assert "Available" in result
    assert "14:00" in result

def test_create_event_tool():
    result = create_event_tool.invoke({
        "title": "Test Meeting",
        "date": "2026-08-01",
        "start_time": "14:00",
        "end_time": "14:30",
        "attendees": "rahul@test.com, sarah@test.com",
        "description": "Quick sync"
    })
    assert "Calendar event created successfully" in result
    assert "Test Meeting" in result


# ──────────────────── Utility Tool Tests ────────────────────

def test_get_current_datetime_tool():
    result = get_current_datetime_tool.invoke({})
    today_str = datetime.now().strftime("%Y-%m-%d")
    assert today_str in result
    assert "Current Time:" in result

def test_resolve_relative_date_tomorrow():
    result = resolve_relative_date_tool.invoke({"expression": "tomorrow afternoon"})
    tomorrow_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    assert tomorrow_str in result
    assert "14:00" in result

def test_resolve_relative_date_next_tuesday():
    result = resolve_relative_date_tool.invoke({"expression": "next tuesday morning"})
    assert "Tuesday" in result
    assert "09:00" in result

def test_contact_lookup_found():
    result = contact_lookup_tool.invoke({"name": "Rahul"})
    assert "Rahul Sharma" in result
    assert "rahul.sharma@techcorp.com" in result

def test_contact_lookup_not_found():
    result = contact_lookup_tool.invoke({"name": "Nonexistent"})
    assert "No contact found" in result
