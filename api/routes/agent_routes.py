from fastapi import APIRouter, HTTPException
from api.schemas.requests import AgentRunRequest, AgentResponse
from state.agent_state import create_initial_state
from graph.state_graph import assistant_graph

router = APIRouter(prefix="/api/v1/agent", tags=["Agent Execution"])

@router.post("/run", response_model=AgentResponse)
def run_agent(req: AgentRunRequest):
    """
    Execute an autonomous agent query via LangGraph.
    Runs until task completion or interrupts at an approval node if human review is required.
    """
    config = {"configurable": {"thread_id": req.thread_id}}
    initial_state = create_initial_state(req.user_query)
    
    try:
        res = assistant_graph.invoke(initial_state, config=config)
        state_vals = assistant_graph.get_state(config).values
        
        return AgentResponse(
            thread_id=req.thread_id,
            detected_intent=state_vals.get("detected_intent"),
            approval_required=state_vals.get("approval_required", False),
            approval_status=state_vals.get("approval_status"),
            pending_action=state_vals.get("pending_action"),
            final_response=state_vals.get("final_response"),
            execution_log=state_vals.get("execution_log", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph execution failed: {str(e)}")
