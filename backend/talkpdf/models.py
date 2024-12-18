from django.db import models
import uuid
from django.contrib.auth.models import User

class ChatDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    thread_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    path = models.TextField()
    chat_name = models.TextField()
    file_names = models.JSONField(default=list)  # Para armazenar os nomes dos arquivos como lista de strings

    def __str__(self):
        return self.chat_name

class ChatCheckpoint(models.Model):
    chat = models.ForeignKey(ChatDetails, on_delete=models.CASCADE, related_name='checkpoints')
    thread_ts = models.TextField()
    parent_ts = models.TextField(null=True, blank=True, default=None)
    checkpoint = models.BinaryField()
    metadata = models.BinaryField()

    class Meta:
        unique_together = (("chat", "thread_ts"),)

    def __str__(self):
        return f"Checkpoint {self.thread_ts} for Chat {self.chat.chatName}"

class ChatWrite(models.Model):
    chat = models.ForeignKey(ChatDetails, on_delete=models.CASCADE, related_name='writes')
    thread_ts = models.TextField()
    task_id = models.TextField()
    idx = models.IntegerField()
    channel = models.TextField()
    value = models.BinaryField(null=True, blank=True, default=None)

    class Meta:
        unique_together = (("chat", "thread_ts", "task_id", "idx"),)

    def __str__(self):
        return f"Write {self.task_id} at index {self.idx} for Chat {self.chat.chatName}"
