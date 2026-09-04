from typing import List, Any
# from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

def create_model(tools: List[Any] = None):
    """
    # Creates and returns a configured ChatOpenAI model object.
    Creates and returns a configured ChatGoogleGenerativeAI model object.
    
    CONCEPT:
    # Your Python application -> ChatOpenAI -> Model API -> LLM
    Your Python application -> ChatGoogleGenerativeAI -> Model API -> LLM
    LangChain gives us a common interface around the model.
    
    If tools are provided, we bind them to the model using `.bind_tools()`.
    This tells the LLM that these tools exist and it can decide to call them.
    """
    # Ensure environment variables are loaded before client validation runs
    load_dotenv()
    
    # model = ChatOpenAI(
    #     model="gpt-4o-mini",
    #     # Temperature controls how much randomness the model uses during generation.
    #     # temperature = 0 -> More predictable, deterministic. Good for factual company assistant.
    #     # temperature = 1 -> More variation, creative, less predictable.
    #     temperature=0
    # )
    model = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        temperature=0
    )
    
    if tools:
        # bind_tools tells the Google model about the schemas of our tools
        return model.bind_tools(tools)
    return model
