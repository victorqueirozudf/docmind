from django.db import models

# Modelo criado para guardar nossas mensagens
class MessageTalkPdf(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    def __str__(self):
        return self.message
"""
class PDFProcessView(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    question = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return self.message
"""