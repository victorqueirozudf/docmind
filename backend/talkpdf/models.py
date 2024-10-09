from django.db import models
import json
import uuid

"""
class TalkPDF(models.Model):
    id = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class DocumentsVectors(models.Model):
    thread_id = models.TextField()
    #listaVetores =
    created_at = models.DateTimeField(auto_now_add=True)
"""

import uuid
from django.db import models

# Modelo para armazenar os detalhes do chat
class ChatDetails(models.Model):
    thread_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Chave primária com UUID
    created_at = models.DateTimeField(auto_now_add=True)  # Data de criação automática
    path = models.TextField()  # Caminho para o documento PDF
    chatName = models.TextField()  # Nome personalizado do chat

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
