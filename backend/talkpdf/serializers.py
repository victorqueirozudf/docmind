from rest_framework import serializers
from .models import MessageTalkPdf

# serializando nossa mensagem, para facilitar na comunicação com outros aplicativos
class MessageTalkPdfSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageTalkPdf
        fields = ('__all__')
