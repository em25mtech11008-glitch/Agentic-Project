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
    A minimal, async-native MongoDB checkpointer for LangGraph using Motor.
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
        checkpoint_id = config["configurable"].get("checkpoint_id")
        
        query = {"thread_id": thread_id}
        if checkpoint_id:
            query["checkpoint_id"] = checkpoint_id
            
        doc = await self.collection.find_one(query, sort=[("ts", -1)])
        if not doc:
            return None
            
        checkpoint = self.serde.loads_typed(doc["checkpoint"])
        
        pending_writes = [
            (w["task_id"], w["channel"], self.serde.loads_typed(w["value"]))
            async for w in self.writes_collection.find(
                {"thread_id": thread_id, "checkpoint_id": checkpoint["id"]}
            )
        ]
            
        return CheckpointTuple(
            config={"configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint["id"]}},
            checkpoint=checkpoint,
            metadata=self.serde.loads_typed(doc["metadata"]),
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
        
        await self.collection.update_one(
            {"thread_id": thread_id, "checkpoint_id": checkpoint["id"]},
            {"$set": {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint["id"],
                "ts": checkpoint["ts"],
                "checkpoint": self.serde.dumps_typed(checkpoint),
                "metadata": self.serde.dumps_typed(metadata),
            }},
            upsert=True
        )
        
        return {"configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint["id"]}}

    async def aput_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
    ) -> None:
        if not writes:
            return
            
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = config["configurable"]["checkpoint_id"]
        
        docs = [{
            "thread_id": thread_id,
            "checkpoint_id": checkpoint_id,
            "task_id": task_id,
            "channel": channel,
            "value": self.serde.dumps_typed(value)
        } for channel, value in writes]
        
        await self.writes_collection.insert_many(docs)

    async def alist(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[Dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> AsyncIterator[CheckpointTuple]:
        query = {"thread_id": config["configurable"]["thread_id"]} if config else {}
        cursor = self.collection.find(query).sort("ts", -1)
        
        if limit:
            cursor = cursor.limit(limit)
            
        async for doc in cursor:
            yield CheckpointTuple(
                config={"configurable": {"thread_id": doc["thread_id"], "checkpoint_id": doc["checkpoint_id"]}},
                checkpoint=self.serde.loads_typed(doc["checkpoint"]),
                metadata=self.serde.loads_typed(doc["metadata"]),
                parent_config=None,
                pending_writes=[]
            )
