import os
from typing import Any, AsyncIterator, Dict, Optional, Sequence, Tuple
from motor.motor_asyncio import AsyncIOMotorClient
from langgraph.checkpoint.base import (
    BaseCheckpointSaver, 
    Checkpoint, 
    CheckpointMetadata, 
    CheckpointTuple, 
    ChannelVersions, 
    SerializerProtocol
)
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langchain_core.runnables import RunnableConfig

class AsyncMongoDBSaver(BaseCheckpointSaver):
    """
    A custom asynchronous MongoDB checkpointer for LangGraph.
    Uses Motor to store conversation states, enabling persistent memory.
    """
    
    def __init__(
        self,
        client: AsyncIOMotorClient,
        db_name: str = "startup_ai",
        collection_name: str = "checkpoints",
        *,
        serde: Optional[SerializerProtocol] = None,
    ):
        super().__init__(serde=serde or JsonPlusSerializer())
        self.collection = client[db_name][collection_name]
        self.writes_collection = client[db_name][f"{collection_name}_writes"]

    async def aget_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        thread_id = config["configurable"]["thread_id"]
        
        # Check if a specific checkpoint is requested
        checkpoint_id = config["configurable"].get("checkpoint_id")
        query = {"thread_id": thread_id}
        if checkpoint_id:
            query["checkpoint_id"] = checkpoint_id
            
        doc = await self.collection.find_one(query, sort=[("ts", -1)])
        
        if not doc:
            return None
            
        checkpoint = self.serde.loads(doc["checkpoint"])
        metadata = self.serde.loads(doc["metadata"])
        
        # Fetch pending writes (if any)
        writes_cursor = self.writes_collection.find(
            {"thread_id": thread_id, "checkpoint_id": checkpoint["id"]}
        )
        pending_writes = []
        async for w in writes_cursor:
            pending_writes.append((w["task_id"], w["channel"], self.serde.loads(w["value"])))
            
        return CheckpointTuple(
            config={"configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint["id"]}},
            checkpoint=checkpoint,
            metadata=metadata,
            parent_config=None,
            pending_writes=pending_writes
        )

    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        thread_id = config["configurable"]["thread_id"]
        doc = {
            "thread_id": thread_id,
            "checkpoint_id": checkpoint["id"],
            "ts": checkpoint["ts"],
            "checkpoint": self.serde.dumps(checkpoint),
            "metadata": self.serde.dumps(metadata),
        }
        # Upsert just in case a retry happens with the same checkpoint ID
        await self.collection.update_one(
            {"thread_id": thread_id, "checkpoint_id": checkpoint["id"]},
            {"$set": doc},
            upsert=True
        )
        
        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint["id"],
            }
        }

    async def aput_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
    ) -> None:
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = config["configurable"]["checkpoint_id"]
        
        docs = []
        for channel, value in writes:
            docs.append({
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id,
                "task_id": task_id,
                "channel": channel,
                "value": self.serde.dumps(value)
            })
        if docs:
            await self.writes_collection.insert_many(docs)

    async def alist(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[Dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> AsyncIterator[CheckpointTuple]:
        thread_id = config["configurable"].get("thread_id") if config else None
        query = {}
        if thread_id:
            query["thread_id"] = thread_id
            
        cursor = self.collection.find(query).sort("ts", -1)
        if limit:
            cursor = cursor.limit(limit)
            
        async for doc in cursor:
            checkpoint = self.serde.loads(doc["checkpoint"])
            metadata = self.serde.loads(doc["metadata"])
            yield CheckpointTuple(
                config={"configurable": {"thread_id": doc["thread_id"], "checkpoint_id": doc["checkpoint_id"]}},
                checkpoint=checkpoint,
                metadata=metadata,
                parent_config=None,
                pending_writes=[]
            )
            
    # Raise errors for sync methods since we are fully async in FastAPI
    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        raise NotImplementedError("Use aget_tuple in an async environment.")
    
    def put(self, config: RunnableConfig, checkpoint: Checkpoint, metadata: CheckpointMetadata, new_versions: ChannelVersions) -> RunnableConfig:
        raise NotImplementedError("Use aput in an async environment.")
        
    def put_writes(self, config: RunnableConfig, writes: Sequence[Tuple[str, Any]], task_id: str) -> None:
        raise NotImplementedError("Use aput_writes in an async environment.")
        
    def list(self, config: Optional[RunnableConfig], *, filter: Optional[Dict[str, Any]] = None, before: Optional[RunnableConfig] = None, limit: Optional[int] = None) -> AsyncIterator[CheckpointTuple]:
        raise NotImplementedError("Use alist in an async environment.")
