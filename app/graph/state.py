from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    Defines the state of the LangGraph workflow.
    """
    # The full conversation transcript (history + scratchpad)
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # Retrieved document chunks from RAG context
    context: list[str]
    
    # The next agent to route to (set by the Supervisor)
    next_agent: str
