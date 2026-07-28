import pytest
from langgraph.types import Command
from state.agent_state import create_initial_state
from graph.state_graph import assistant_graph

def test_read_email_workflow():
    config = {"configurable": {"thread_id": "thread_1"}}
    initial_state = create_initial_state("Summarize today's unread emails.")
    
    res = assistant_graph.invoke(initial_state, config=config)
    assert res["detected_intent"] == "SUMMARIZE_INBOX"
    assert res["approval_required"] is False
    assert "Found" in res["final_response"]

def test_check_schedule_workflow():
    config = {"configurable": {"thread_id": "thread_2"}}
    initial_state = create_initial_state("What is my schedule for today?")
    
    res = assistant_graph.invoke(initial_state, config=config)
    assert res["detected_intent"] == "CHECK_SCHEDULE"
    assert res["approval_required"] is False
    assert "Daily Engineering Standup" in res["final_response"]

def test_daily_plan_workflow():
    config = {"configurable": {"thread_id": "thread_3"}}
    initial_state = create_initial_state("Plan my day today.")
    
    res = assistant_graph.invoke(initial_state, config=config)
    assert res["detected_intent"] == "DAILY_PLAN"
    assert "DAILY EXECUTIVE PLAN" in res["final_response"]

def test_send_email_hitl_approval():
    config = {"configurable": {"thread_id": "thread_4"}}
    initial_state = create_initial_state("Send an email to John saying I'll attend.")
    
    # 1. First execution - triggers native interrupt at approval_node
    res_interrupt = assistant_graph.invoke(initial_state, config=config)
    assert "__interrupt__" in res_interrupt
    
    # Check pending state
    state_vals = assistant_graph.get_state(config).values
    assert state_vals["approval_required"] is True
    assert state_vals["pending_action"]["tool_name"] == "send_email_tool"
    
    # 2. Resume execution with Command(resume={"approval_status": "APPROVED"})
    res_final = assistant_graph.invoke(Command(resume={"approval_status": "APPROVED"}), config=config)
    assert "ACTION EXECUTED (APPROVED)" in res_final["final_response"]
    assert res_final["approval_status"] == "COMPLETED"

def test_schedule_meeting_hitl_rejection():
    config = {"configurable": {"thread_id": "thread_5"}}
    initial_state = create_initial_state("Schedule a meeting with Rahul next Tuesday afternoon.")
    
    # 1. First execution - triggers native interrupt at approval_node
    res_interrupt = assistant_graph.invoke(initial_state, config=config)
    assert "__interrupt__" in res_interrupt
    
    # Check pending state
    state_vals = assistant_graph.get_state(config).values
    assert state_vals["approval_required"] is True
    assert state_vals["pending_action"]["tool_name"] == "create_event_tool"
    
    # 2. Resume execution with Command(resume={"approval_status": "REJECTED"})
    res_final = assistant_graph.invoke(Command(resume={"approval_status": "REJECTED"}), config=config)
    assert "ACTION CANCELLED (REJECTED)" in res_final["final_response"]
    assert res_final["approval_status"] == "CANCELLED"
