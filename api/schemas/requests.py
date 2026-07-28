from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class AgentRunRequest(BaseModel):
    """Request model for executing an assistant query."""
    user_query: str = Field(..., description="Natural language request or instruction for the AI assistant.")
    thread_id: str = Field("default_thread", description="Unique conversation thread ID for LangGraph checkpointer state.")

class AgentApprovalRequest(BaseModel):
    """Request model for submitting a Human-in-the-Loop approval decision."""
    thread_id: str = Field(..., description="The thread ID of the interrupted task requiring approval.")
    approval_status: str = Field(..., description="Decision: 'APPROVED' or 'REJECTED'.")

class AgentResponse(BaseModel):
    """Unified response model containing assistant output and HITL state."""
    thread_id: str
    detected_intent: Optional[str] = None
    approval_required: bool = False
    approval_status: Optional[str] = None
    pending_action: Optional[Dict[str, Any]] = None
    final_response: Optional[str] = None
    execution_log: List[str] = []
