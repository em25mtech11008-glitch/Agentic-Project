from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    Defines the state of our LangGraph workflow.
    
    THEORY: State in LangGraph
    LangGraph is based on state machines.
    Every node in the graph:
    1. Receives the current state as input.
    2. Performs some operations.
    3. Returns a dictionary containing UPDATES to the state.
    
    The `Annotated[Sequence[BaseMessage], add_messages]` tells LangGraph that:
    - `messages` is a sequence of Message objects.
    - Whenever a node returns a dictionary like `{"messages": [new_msg]}`, 
      it should APPEND `new_msg` to the existing list instead of replacing it (this is 
      what the `add_messages` reducer function does).
    """
    # The full conversation transcript (history + scratchpad)
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # Retrieved document chunks from RAG context
    context: list[str]
    
    # The next agent to route to (set by the Supervisor)
    next_agent: str
