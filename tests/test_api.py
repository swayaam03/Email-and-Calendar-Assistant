from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "model" in data

def test_agent_run_read_email():
    payload = {
        "user_query": "Summarize unread emails",
        "thread_id": "api_test_thread_1"
    }
    response = client.post("/api/v1/agent/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["thread_id"] == "api_test_thread_1"
    assert data["detected_intent"] == "SUMMARIZE_INBOX"
    assert data["approval_required"] is False
    assert "Found" in data["final_response"]

def test_agent_run_and_approve():
    # 1. Run email send query (triggers HITL interrupt)
    run_payload = {
        "user_query": "Send an email to John saying I'll attend.",
        "thread_id": "api_test_thread_2"
    }
    response_run = client.post("/api/v1/agent/run", json=run_payload)
    assert response_run.status_code == 200
    data_run = response_run.json()
    assert data_run["approval_required"] is True
    assert data_run["pending_action"]["tool_name"] == "send_email_tool"

    # 2. Submit HITL approval
    approve_payload = {
        "thread_id": "api_test_thread_2",
        "approval_status": "APPROVED"
    }
    response_app = client.post("/api/v1/agent/approve", json=approve_payload)
    assert response_app.status_code == 200
    data_app = response_app.json()
    assert "ACTION EXECUTED (APPROVED)" in data_app["final_response"]
