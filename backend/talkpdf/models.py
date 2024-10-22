from django.db import models
import uuid
from django.db import models
from django.contrib.auth.models import User

class ChatDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Associar um chat a um usuário
    thread_id = models.UUIDField(primary_key=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    path = models.TextField()
    chatName = models.TextField()

    def __str__(self):
        return self.chatName

# Modelo para salvar os checkpoints, com relação ao ChatDetails (Foreign Key)
class DjCheckpoint(models.Model):
    #thread_id = models.ForeignKey(ChatDetails, on_delete=models.CASCADE, to_field='thread_id')  # ForeignKey para ChatDetails
    thread_id = models.TextField()
    thread_ts = models.TextField()  # Timestamp da thread
    parent_ts = models.TextField(null=True, blank=True, default=None)  # Timestamp do pai, opcional
    checkpoint = models.BinaryField()  # Dados binários do checkpoint
    metadata = models.BinaryField()  # Metadados binários

    class Meta:
        unique_together = (("thread_id", "thread_ts"),)  # Garantir que a combinação de thread_id e thread_ts seja única

# Classe do meu salvador de estados
class DjWrite(models.Model):
    thread_id = models.TextField()
    thread_ts = models.TextField()
    task_id = models.TextField()
    idx = models.IntegerField()
    channel = models.TextField()
    value = models.BinaryField(null=True, blank=True, default=None)

    class Meta:
        unique_together = (("thread_id", "thread_ts", "task_id", "idx"),)

"""
class ChatCost(models.Model):
    thread_id = models.TextField()
    thread_ts = models.TextField()
    input_tokens = models.IntegerField()
    output_tokens = models.IntegerField()
    model_cost = models.DecimalField()
    total_cost = models.DecimalField()

    class Meta:
        unique_together = (("thread_id", "thread_ts"),)
"""