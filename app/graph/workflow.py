from langgraph.graph import StateGraph, START, END
from app.graph.state import AgentState
from app.graph.nodes import (
    supervisor_node,
    worker_node,
    tools_node,
    should_continue,
    supervisor_router
)

def create_workflow(checkpointer=None):
    """
    Assembles and compiles the LangGraph State Machine workflow.
    """
    workflow = StateGraph(AgentState)
    
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("worker", worker_node)
    workflow.add_node("tools", tools_node)
    
    workflow.add_edge(START, "supervisor")
    
    workflow.add_conditional_edges(
        "supervisor",
        supervisor_router,
        {
            "worker": "worker",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "worker",
        should_continue,
        {
            "tools": "tools",
            "supervisor": "supervisor",
            "end": END
        }
    )
    
    workflow.add_edge("tools", "worker")
    
    return workflow.compile(checkpointer=checkpointer)
