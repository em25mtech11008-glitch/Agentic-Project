"""
==================================================
AI COMMAND API — Connects LangGraph to React UI
==================================================

Educational Comment:
This is the bridge between the new React Frontend and your existing
LangGraph AI Agents (`app/graph/workflow.py`).

When a user types a command in the UI, this endpoint:
1. Passes the query to LangGraph.
2. Extracts the final LLM response.
3. Automatically parses any "Actions" the AI wants to take.
4. Saves them in the Action Engine.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import json
import re

from app.auth.middleware import require_permission
from app.engines.action_engine import create_action

# Import the existing LangGraph workflow and MemorySaver
from app.graph.workflow import create_workflow
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage

router = APIRouter(prefix="/api/ai", tags=["AI Command"])

# Keep one global graph instance loaded
memory_saver = MemorySaver()
graph_app = create_workflow(checkpointer=memory_saver)


class CommandRequest(BaseModel):
    query: str
    thread_id: str


@router.post("/command")
async def execute_ai_command(req: CommandRequest, user: dict = Depends(require_permission("ai.execute"))):
    try:
        org_id = user["org"]
        user_id = user["user_id"]
        
        # 1. Prepare LangGraph state
        config = {"configurable": {"thread_id": req.thread_id}}
        input_state = {"messages": [HumanMessage(content=req.query)]}
        
        # 2. Run LangGraph (Wait for completion)
        # In a real app we might stream this, but for MVP we wait for the final state
        result_state = None
        async for event in graph_app.astream(input_state, config=config, stream_mode="values"):
            result_state = event
            
        if not result_state or "messages" not in result_state:
            raise HTTPException(status_code=500, detail="AI returned no response.")
            
        final_message = result_state["messages"][-1]
        
        raw_content = final_message.content
        if isinstance(raw_content, list):
            raw_text = "".join([part.get("text", "") for part in raw_content if isinstance(part, dict) and "text" in part])
        else:
            raw_text = str(raw_content)
        
        # 3. Parse Structured Actions
        actions_created = []
        
        # Look for JSON blocks in the response containing "actions"
        json_match = re.search(r'```json\s*(\{.*"actions"\s*:\s*\[.*\})\s*```', raw_text, re.DOTALL)
        if json_match:
            try:
                action_data = json.loads(json_match.group(1))
                for action in action_data.get("actions", []):
                    action_id = await create_action(
                        organization_id=org_id,
                        created_by="AI Supervisor",
                        action_type=action.get("action_type", "UNKNOWN"),
                        target=action.get("target", {}),
                        payload=action.get("payload", {}),
                        requires_approval=action.get("requires_approval", True)
                    )
                    actions_created.append({
                        "id": str(action_id),
                        "title": action.get("title", "AI Action"),
                        "description": action.get("description", "Recommended action"),
                        "confidence": 0.95,
                        "requiresApproval": action.get("requires_approval", True)
                    })
                
                # Remove the JSON block from the text shown to the user
                raw_text = raw_text[:json_match.start()].strip()
            except Exception as e:
                print(f"Failed to parse action JSON: {e}")
                
        # Fallback naive parsing
        elif "SEND_EMAIL" in raw_text or "REMINDER" in raw_text.upper():
            # Create a pending action in the DB
            action_id = await create_action(
                organization_id=org_id,
                created_by="Finance Agent",
                action_type="SEND_EMAIL",
                target={"type": "CUSTOMER", "id": "unknown"},
                payload={"subject": "Follow up", "body": "Please pay your invoice."},
                requires_approval=True
            )
            actions_created.append({
                "id": str(action_id),
                "title": "Send Payment Reminder",
                "description": "AI recommends sending a follow-up email.",
                "confidence": 0.92,
                "requiresApproval": True
            })
            
        # 4. Return to Frontend
        return {
            "text": raw_text,
            "actions": actions_created
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
