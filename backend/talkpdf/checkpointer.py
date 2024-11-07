from typing import Any, List, Tuple

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import Checkpoint, CheckpointMetadata, CheckpointTuple, BaseCheckpointSaver

from .models import ChatDetails, ChatCheckpoint, ChatWrite
import os

class DjangoSaver(BaseCheckpointSaver):
    def get_tuple(self, config: RunnableConfig) -> CheckpointTuple | None:
        thread_id = config["configurable"]["thread_id"]
        thread_ts = config["configurable"].get("thread_ts")

        try:
            chat = ChatDetails.objects.get(thread_id=thread_id)
        except ChatDetails.DoesNotExist:
            return None

        if thread_ts:
            chat_checkpoint = (
                ChatCheckpoint.objects.filter(chat=chat, thread_ts=thread_ts)
                .values_list("checkpoint", "metadata", "thread_ts", "parent_ts")
                .first()
            )
        else:
            chat_checkpoint = (
                ChatCheckpoint.objects.filter(chat=chat)
                .order_by("-thread_ts")
                .values_list("checkpoint", "metadata", "thread_ts", "parent_ts")
                .first()
            )

        if chat_checkpoint:
            checkpoint, metadata, thread_ts, parent_ts = chat_checkpoint
            if not config["configurable"].get("thread_ts"):
                config = {
                    "configurable": {
                        "thread_id": thread_id,
                        "thread_ts": thread_ts,
                    }
                }

                chat_writes = ChatWrite.objects.filter(
                    chat=chat, thread_ts=thread_ts
                ).values_list("task_id", "channel", "value")

                return CheckpointTuple(
                    config=config,
                    checkpoint=self.serde.loads(checkpoint),
                    metadata=self.serde.loads(metadata),
                    parent_config=(
                        {
                            "configurable": {
                                "thread_id": thread_id,
                                "thread_ts": parent_ts,
                            }
                        }
                        if parent_ts
                        else None
                    ),
                    pending_writes=[
                        (task_id, channel, self.serde.loads(value))
                        for task_id, channel, value in chat_writes
                    ],
                )

    def put(
            self,
            config: RunnableConfig,
            checkpoint: Checkpoint,
            metadata: CheckpointMetadata,
            parent_config: RunnableConfig | None  # Novo parâmetro adicionado
    ) -> RunnableConfig:
        thread_id = config["configurable"]["thread_id"]
        parent_ts = config["configurable"].get("thread_ts")

        try:
            chat = ChatDetails.objects.get(thread_id=thread_id)
        except ChatDetails.DoesNotExist:
            raise ValueError(f"ChatDetails com thread_id {thread_id} não encontrado.")

        ChatCheckpoint.objects.update_or_create(
            chat=chat,
            thread_ts=checkpoint["id"],
            defaults={
                "parent_ts": parent_ts if parent_ts else None,
                "checkpoint": self.serde.dumps(checkpoint),
                "metadata": self.serde.dumps(metadata),
            },
        )

    def put_writes(
        self, config: RunnableConfig, writes: List[Tuple[str, Any]], task_id: str
    ) -> None:
        thread_id = config["configurable"]["thread_id"]
        thread_ts = config["configurable"].get("thread_ts")

        try:
            chat = ChatDetails.objects.get(thread_id=thread_id)
        except ChatDetails.DoesNotExist:
            raise ValueError(f"ChatDetails com thread_id {thread_id} não encontrado.")

        ChatWrite.objects.bulk_create(
            [
                ChatWrite(
                    chat=chat,
                    thread_ts=thread_ts,
                    task_id=task_id,
                    idx=idx,
                    channel=channel,
                    value=self.serde.dumps(value),
                )
                for idx, (channel, value) in enumerate(writes)
            ],
            ignore_conflicts=False,
            update_conflicts=True,
            update_fields=["value"],
            unique_fields=["chat", "thread_ts", "task_id", "idx"],
        )
