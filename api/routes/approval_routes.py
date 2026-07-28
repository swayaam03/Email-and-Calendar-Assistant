from fastapi import APIRouter, HTTPException
from langgraph.types import Command
from api.schemas.requests import AgentApprovalRequest, AgentResponse
from graph.state_graph import assistant_graph

router = APIRouter(prefix="/api/v1/agent", tags=["Human Approval"])

@router.post("/approve", response_model=AgentResponse)
def approve_action(req: AgentApprovalRequest):
    """
    Submit Human-in-the-Loop approval decision (APPROVED or REJECTED)
    to resume interrupted LangGraph execution.
    """
    status = req.approval_status.upper()
    if status not in ["APPROVED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Approval status must be 'APPROVED' or 'REJECTED'.")
        
    config = {"configurable": {"thread_id": req.thread_id}}
    state_snap = assistant_graph.get_state(config)
    
    if not state_snap.values:
        raise HTTPException(status_code=444 if False else 404, detail=f"No active state found for thread_id '{req.thread_id}'.")
        
    try:
        res = assistant_graph.invoke(Command(resume={"approval_status": status}), config=config)
        final_vals = assistant_graph.get_state(config).values
        
        return AgentResponse(
            thread_id=req.thread_id,
            detected_intent=final_vals.get("detected_intent"),
            approval_required=False,
            approval_status=final_vals.get("approval_status"),
            pending_action=final_vals.get("pending_action"),
            final_response=final_vals.get("final_response"),
            execution_log=final_vals.get("execution_log", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resume graph execution: {str(e)}")
