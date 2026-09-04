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
    
    This implements the 'AI Workforce Operating System' Multi-Agent Supervisor Pattern.
    """
    # 1. Initialize the StateGraph with our AgentState structure
    workflow = StateGraph(AgentState)
    
    # 2. Define the core graph nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("worker", worker_node)
    workflow.add_node("tools", tools_node)
    
    # 3. Always start with the AI COO (Supervisor)
    workflow.add_edge(START, "supervisor")
    
    # 4. Supervisor routes to the Worker node (with injected persona) or terminates
    workflow.add_conditional_edges(
        "supervisor",
        supervisor_router,
        {
            "worker": "worker",
            "end": END
        }
    )
    
    # 5. Worker determines if it needs tools, or if it is done reporting to the COO
    workflow.add_conditional_edges(
        "worker",
        should_continue,
        {
            "tools": "tools",
            "supervisor": "supervisor",
            "end": END
        }
    )
    
    # 6. Tools Executor feeds results directly back to the active Worker
    workflow.add_edge("tools", "worker")
    
    # 7. Compile the graph into an executable Runnable with the checkpointer
    return workflow.compile(checkpointer=checkpointer)
