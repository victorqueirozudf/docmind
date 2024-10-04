from django.db import models
import json

class ChatGraph(models.Model):
    user_id = models.UUIDField(primary_key=True)  # ID do usuário ou da conversa
    graph_data = models.JSONField()  # Armazena o grafo como um dicionário JSON
    created_at = models.DateTimeField(auto_now_add=True)  # Data de criação

    def update_graph(self, new_message):
        # Atualiza o grafo com uma nova mensagem
        if 'messages' not in self.graph_data:
            self.graph_data['messages'] = []
        self.graph_data['messages'].append(new_message)
        self.save()

    def __str__(self):
        return f"ChatGraph for user {self.user_id}"

# Classe do meu salvador de estados
class DjCheckpoint(models.Model):
    thread_id = models.TextField()
    thread_ts = models.TextField()
    parent_ts = models.TextField(null=True, blank=True, default=None)
    checkpoint = models.BinaryField()
    metadata = models.BinaryField()

    class Meta:
        unique_together = (("thread_id", "thread_ts"),)

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


# Modelo criado para guardar nossas mensagens
class MessageTalkPdf(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    def __str__(self):
        return self.message

# classe provisória, futuramente, adicionar usuário (id, ip, nome, ou algo do tipo), id do chat, outras informações, se necessário
class OrionTalk(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    userInput = models.TextField()
    orionOutput = models.TextField()
    model_name = models.TextField()
    inputTokens = models.IntegerField()
    outputTokens = models.IntegerField()
    totalTokes = models.IntegerField()

    def __str__(self):
        return "input created!"
"""
class PDFProcessView(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    question = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return self.message
"""