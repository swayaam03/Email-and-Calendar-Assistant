from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from state.agent_state import AgentState
from agents.intent_classifier import classify_intent_node
from agents.email_agent import email_agent_node
from agents.calendar_agent import calendar_agent_node
from agents.planner_agent import planner_agent_node
from graph.approval_node import approval_node
from graph.routing import route_intent, route_after_agent

def build_assistant_graph():
    """
    Constructs and compiles the complete LangGraph autonomous agent workflow.
    Features:
    - StateGraph(AgentState) state evolution.
    - Intent classification & conditional routing.
    - Specialized domain agents (email, calendar, planner).
    - Native Human-in-the-Loop (HITL) interrupt via langgraph.types.interrupt.
    - MemorySaver checkpointer state persistence.
    """
    builder = StateGraph(AgentState)

    # 1. Add Nodes
    builder.add_node("classify_intent", classify_intent_node)
    builder.add_node("email_agent", email_agent_node)
    builder.add_node("calendar_agent", calendar_agent_node)
    builder.add_node("planner_agent", planner_agent_node)
    builder.add_node("approval_node", approval_node)

    # 2. Set Entrypoint
    builder.set_entry_point("classify_intent")

    # 3. Add Conditional Edges from classify_intent
    builder.add_conditional_edges(
        "classify_intent",
        route_intent,
        {
            "email_agent": "email_agent",
            "calendar_agent": "calendar_agent",
            "planner_agent": "planner_agent",
        }
    )

    # 4. Add Conditional Edges from domain agents
    for agent_node in ["email_agent", "calendar_agent", "planner_agent"]:
        builder.add_conditional_edges(
            agent_node,
            route_after_agent,
            {
                "approval_node": "approval_node",
                "__end__": END,
            }
        )

    # 5. Add Edge from approval_node to END
    builder.add_edge("approval_node", END)

    # 6. Compile Graph with MemorySaver Checkpointer
    checkpointer = MemorySaver()
    compiled_graph = builder.compile(checkpointer=checkpointer)
    return compiled_graph

# Global compiled assistant graph instance
assistant_graph = build_assistant_graph()
