from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

def create_chat_prompt() -> ChatPromptTemplate:
    """
    Creates and returns a ChatPromptTemplate for our agent.
    
    WHY PROMPT TEMPLATES?
    Instead of hardcoding prompt strings, templates allow us to define a reusable structure 
    with placeholders (like {input}) that get populated at runtime.
    
    THEORY - MessagesPlaceholder:
    A MessagesPlaceholder is a special placeholder that doesn't just insert a single string, 
    but inserts a LIST of Message objects (like SystemMessage, HumanMessage, AIMessage).
    - "chat_history" stores past conversations (short-term memory).
    - "agent_scratchpad" stores tool execution messages within the current turn.
    """
    return ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a helpful company AI assistant. "
            "Explain technical topics clearly and use the available tools to answer queries when necessary. "
            "If you cannot answer using the tools or your general knowledge, be honest."
        ),
        # Injects the list of past messages representing the conversation history.
        MessagesPlaceholder(variable_name="chat_history"),
        # Injects the user's current question.
        ("human", "{input}"),
        # Injects the list of temporary tool calls/responses for the current reasoning chain.
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
