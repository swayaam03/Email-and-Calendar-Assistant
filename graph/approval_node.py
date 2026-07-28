from typing import Dict, Any
from langgraph.types import interrupt
from state.agent_state import AgentState
from tools.email.sender import send_email_tool
from tools.calendar.creator import create_event_tool

def approval_node(state: AgentState) -> Dict[str, Any]:
    """
    Human-in-the-Loop approval gate node.
    
    If approval_status is "PENDING", pauses execution with langgraph.types.interrupt()
    and waits for human decision via Command(resume={"approval_status": "APPROVED" | "REJECTED"}).
    
    Executes mutating tools if APPROVED, or cancels action if REJECTED.
    """
    status = state.get("approval_status")
    pending = state.get("pending_action")
    log = state.get("execution_log", []) + [f"Node [approval_node]: Processing HITL state with status '{status}'"]
    
    # 1. Trigger native LangGraph interrupt if decision is still PENDING
    if status == "PENDING" and pending:
        human_decision = interrupt({
            "message": "Human approval required for mutating action",
            "pending_action": pending
        })
        
        # Parse decision payload received from Command(resume=...)
        if isinstance(human_decision, dict) and "approval_status" in human_decision:
            status = human_decision["approval_status"]
        elif isinstance(human_decision, str):
            status = human_decision.upper()

    updates: Dict[str, Any] = {
        "execution_log": log,
        "approval_required": False
    }
    
    if not pending:
        updates["final_response"] = "No pending action found for approval."
        return updates
        
    tool_name = pending.get("tool_name")
    tool_args = pending.get("tool_args", {})
    
    # 2. Execute or cancel action based on resolved status
    if status == "APPROVED":
        if tool_name == "send_email_tool":
            result = send_email_tool.invoke(tool_args)
            updates["final_response"] = f"✅ ACTION EXECUTED (APPROVED):\n\n{result}"
        elif tool_name == "create_event_tool":
            result = create_event_tool.invoke(tool_args)
            updates["final_response"] = f"✅ ACTION EXECUTED (APPROVED):\n\n{result}"
        else:
            updates["final_response"] = f"Action '{tool_name}' executed successfully."
            
        updates["pending_action"] = None
        updates["approval_status"] = "COMPLETED"
        
    elif status == "REJECTED":
        updates["final_response"] = f"❌ ACTION CANCELLED (REJECTED): The proposed action '{tool_name}' was declined by the user."
        updates["pending_action"] = None
        updates["approval_status"] = "CANCELLED"
    else:
        updates["final_response"] = f"Action '{tool_name}' is pending human approval."
        updates["approval_status"] = "PENDING"
        updates["approval_required"] = True
        
    return updates
