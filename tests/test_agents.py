import pytest
from state.agent_state import create_initial_state
from agents.intent_classifier import classify_intent_node
from agents.email_agent import email_agent_node
from agents.calendar_agent import calendar_agent_node
from agents.planner_agent import planner_agent_node
from config.constants import IntentType

def test_create_initial_state():
    state = create_initial_state("Summarize unread emails")
    assert state["user_query"] == "Summarize unread emails"
    assert state["detected_intent"] is None
    assert state["approval_required"] is False
    assert len(state["execution_log"]) == 1

def test_intent_classifier_read_email():
    state = create_initial_state("Summarize today's unread emails.")
    res = classify_intent_node(state)
    assert res["detected_intent"] == IntentType.SUMMARIZE_INBOX.value

def test_intent_classifier_schedule_meeting():
    state = create_initial_state("Schedule a meeting with Rahul next Tuesday afternoon.")
    res = classify_intent_node(state)
    assert res["detected_intent"] == IntentType.SCHEDULE_MEETING.value

def test_intent_classifier_add_birthday():
    state = create_initial_state("can u add a birthday at 30th July of Dakshita Kandarkar")
    res = classify_intent_node(state)
    assert res["detected_intent"] == IntentType.SCHEDULE_MEETING.value

def test_email_agent_read():
    state = create_initial_state("Summarize today's unread emails.")
    state["detected_intent"] = IntentType.SUMMARIZE_INBOX.value
    res = email_agent_node(state)
    assert "Found" in res["email_summary"]
    assert res["final_response"] is not None

def test_email_agent_send_approval_trigger():
    state = create_initial_state("Send an email to John saying I'll attend.")
    state["detected_intent"] = IntentType.SEND_EMAIL.value
    res = email_agent_node(state)
    assert res["approval_required"] is True
    assert res["approval_status"] == "PENDING"
    assert res["pending_action"]["tool_name"] == "send_email_tool"

def test_calendar_agent_check_schedule():
    state = create_initial_state("What is my schedule for today?")
    state["detected_intent"] = IntentType.CHECK_SCHEDULE.value
    res = calendar_agent_node(state)
    assert "Daily Engineering Standup" in res["final_response"]

def test_calendar_agent_schedule_meeting_approval_trigger():
    state = create_initial_state("Schedule a meeting with Rahul next Tuesday afternoon.")
    state["detected_intent"] = IntentType.SCHEDULE_MEETING.value
    res = calendar_agent_node(state)
    assert res["approval_required"] is True
    assert res["approval_status"] == "PENDING"
    assert res["pending_action"]["tool_name"] == "create_event_tool"

def test_planner_agent_daily_plan():
    state = create_initial_state("Plan my day today.")
    state["detected_intent"] = IntentType.DAILY_PLAN.value
    res = planner_agent_node(state)
    assert "DAILY EXECUTIVE PLAN" in res["final_response"]
