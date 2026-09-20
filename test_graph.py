import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage
from app.dependencies import graph_app

async def main():
    print("Testing LangGraph invocation...")
    config = {"configurable": {"thread_id": "test-chat-123"}}
    input_state = {"messages": [HumanMessage(content="Hello!")]}
    
    try:
        async for event in graph_app.astream(input_state, config=config, stream_mode="updates"):
            print("Event:", event)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
