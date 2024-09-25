from rest_framework import serializers
from .models import UserPdf, MessageTalkPdf

class UserPdfSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=65.535, required=True)
    last_name = serializers.CharField(max_length=65.535, required=True)
    address = serializers.CharField(max_length=65.535, required=True)
    roll_number = serializers.IntegerField()
    mobile = serializers.CharField(max_length=65.535, required=True)

    class Meta:
        model = UserPdf
        fields = ('__all__')

# serializando nossa mensagem, para facilitar na comunicação com outros aplicativos
class MessageTalkPdfSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageTalkPdf
        fields = ('__all__')
