"""
==================================================
CHAT HISTORY ROUTES — Manage Chat Sessions & Messages
==================================================

Manages persistent chat history in MongoDB.
Enforces multi-tenant RBAC by filtering queries on `user_id` and `organization_id`.
"""

import os
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from app.dependencies import graph_app, get_db
from app.auth.middleware import get_current_user

router = APIRouter(prefix="/api/chats", tags=["Chat History"])


# ==================================================
# REQUEST/RESPONSE SCHEMAS
# ==================================================

class ChatCreateRequest(BaseModel):
    title: str = Field(default="New Chat")

class ChatRenameRequest(BaseModel):
    title: str

class ChatResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

class MessageResponse(BaseModel):
    id: str
    chat_id: str
    role: str
    content: str
    metadata: dict
    created_at: datetime

class ChatDetailResponse(BaseModel):
    chat: ChatResponse
    messages: List[MessageResponse]


# ==================================================
# CREATE CHAT
# ==================================================
@router.post("", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(body: ChatCreateRequest, user: dict = Depends(get_current_user), db = Depends(get_db)):
    """
    Creates a new empty chat session for the current user.
    """
    chat_id = str(uuid.uuid4())
    
    chat = {
        "_id": chat_id,
        "user_id": user["user_id"],
        "organization_id": user["org"],
        "title": body.title,
        "status": "ACTIVE",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    
    await db.chats.insert_one(chat)
    
    return {
        "id": chat_id,
        "title": chat["title"],
        "created_at": chat["created_at"],
        "updated_at": chat["updated_at"],
    }


# ==================================================
# LIST CHATS
# ==================================================
@router.get("", response_model=List[ChatResponse])
async def list_chats(user: dict = Depends(get_current_user), db = Depends(get_db)):
    """
    Returns a list of all active chats for the current user.
    """
    cursor = db.chats.find(
        {"user_id": user["user_id"], "organization_id": user["org"], "status": "ACTIVE"}
    ).sort("updated_at", -1)
    
    chats = []
    async for chat in cursor:
        chats.append({
            "id": chat["_id"],
            "title": chat["title"],
            "created_at": chat["created_at"],
            "updated_at": chat["updated_at"],
        })
        
    return chats


# ==================================================
# GET CHAT (WITH MESSAGES)
# ==================================================
@router.get("/{chat_id}", response_model=ChatDetailResponse)
async def get_chat(chat_id: str, user: dict = Depends(get_current_user), db = Depends(get_db)):
    """
    Retrieves a specific chat and all its messages.
    """
    chat = await db.chats.find_one({
        "_id": chat_id,
        "user_id": user["user_id"],
        "organization_id": user["org"],
        "status": "ACTIVE"
    })
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
        
    cursor = db.messages.find({"chat_id": chat_id}).sort("created_at", 1)
    
    messages = []
    async for msg in cursor:
        messages.append({
            "id": msg["_id"],
            "chat_id": msg["chat_id"],
            "role": msg["role"],
            "content": msg["content"],
            "metadata": msg.get("metadata", {}),
            "created_at": msg["created_at"],
        })
        
    return {
        "chat": {
            "id": chat["_id"],
            "title": chat["title"],
            "created_at": chat["created_at"],
            "updated_at": chat["updated_at"],
        },
        "messages": messages
    }


# ==================================================
# RENAME CHAT
# ==================================================
@router.patch("/{chat_id}", response_model=ChatResponse)
async def rename_chat(chat_id: str, body: ChatRenameRequest, user: dict = Depends(get_current_user), db = Depends(get_db)):
    """
    Renames a specific chat.
    """
    chat = await db.chats.find_one({
        "_id": chat_id,
        "user_id": user["user_id"],
        "organization_id": user["org"],
        "status": "ACTIVE"
    })
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
        
    await db.chats.update_one(
        {"_id": chat_id},
        {"$set": {"title": body.title, "updated_at": datetime.now(timezone.utc)}}
    )
    
    return {
        "id": chat["_id"],
        "title": body.title,
        "created_at": chat["created_at"],
        "updated_at": datetime.now(timezone.utc),
    }


# ==================================================
# DELETE CHAT
# ==================================================
@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(chat_id: str, user: dict = Depends(get_current_user), db = Depends(get_db)):
    """
    Soft-deletes a chat by changing its status to ARCHIVED.
    """
    result = await db.chats.update_one(
        {
            "_id": chat_id,
            "user_id": user["user_id"],
            "organization_id": user["org"],
        },
        {"$set": {"status": "ARCHIVED", "updated_at": datetime.now(timezone.utc)}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Chat not found")

# ==================================================
# SEND MESSAGE (LANGGRAPH INTEGRATION)
# ==================================================
class SendMessageRequest(BaseModel):
    content: str

@router.post("/{chat_id}/messages", response_model=MessageResponse)
async def send_message(chat_id: str, body: SendMessageRequest, user: dict = Depends(get_current_user), db = Depends(get_db)):
    """
    Saves a user message and routes it through the LangGraph AI Operations Assistant.
    """
    # 1. Verify chat ownership
    chat = await db.chats.find_one({
        "_id": chat_id,
        "user_id": user["user_id"],
        "organization_id": user["org"],
        "status": "ACTIVE"
    })
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
        
    # 2. Save User Message
    user_msg_id = str(uuid.uuid4())
    user_msg = {
        "_id": user_msg_id,
        "chat_id": chat_id,
        "user_id": user["user_id"],
        "organization_id": user["org"],
        "role": "user",
        "content": body.content,
        "metadata": {},
        "created_at": datetime.now(timezone.utc)
    }
    await db.messages.insert_one(user_msg)
    
    # 3. Invoke LangGraph
    # We use the chat_id as the LangGraph thread_id to maintain conversational memory
    config = {"configurable": {"thread_id": chat_id}}
    input_state = {"messages": [HumanMessage(content=body.content)]}
    
    steps = []
    try:
        async for event in graph_app.astream(input_state, config=config, stream_mode="updates"):
            for node_name, node_update in event.items():
                if node_name == "retrieve":
                    doc_count = len(node_update.get("context", []))
                    steps.append(f"RAG: Retrieved {doc_count} document chunks.")
                elif node_name == "tools":
                    steps.append("Tools: Executed operations.")
                elif node_name == "worker":
                    steps.append(f"Worker ({node_update.get('active_agent', 'Agent')}): Processed task.")
    except Exception as e:
        print(f"LangGraph Error: {e}")
        raise HTTPException(status_code=500, detail="AI Workflow encountered an error")

    # Retrieve final state
    final_state = await graph_app.aget_state(config)
    final_messages = final_state.values.get("messages", [])
    
    if not final_messages:
        raise HTTPException(status_code=500, detail="No response generated by the agent.")
        
    raw_content = final_messages[-1].content
    if isinstance(raw_content, list):
        final_response = "".join([part.get("text", "") for part in raw_content if isinstance(part, dict) and "text" in part])
    else:
        final_response = str(raw_content)
        
    active_agent = final_state.values.get("active_agent", "AI COO")
    
    # 4. Save AI Message
    ai_msg_id = str(uuid.uuid4())
    ai_msg = {
        "_id": ai_msg_id,
        "chat_id": chat_id,
        "user_id": user["user_id"],
        "organization_id": user["org"],
        "role": "assistant",
        "content": final_response,
        "metadata": {"agent": active_agent, "steps": steps},
        "created_at": datetime.now(timezone.utc)
    }
    await db.messages.insert_one(ai_msg)
    
    # 5. Update chat updated_at
    await db.chats.update_one(
        {"_id": chat_id},
        {"$set": {"updated_at": datetime.now(timezone.utc)}}
    )
    
    return {
        "id": ai_msg_id,
        "chat_id": chat_id,
        "role": "assistant",
        "content": final_response,
        "metadata": {"agent": active_agent, "steps": steps},
        "created_at": ai_msg["created_at"]
    }
