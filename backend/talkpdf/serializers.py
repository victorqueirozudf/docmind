from rest_framework import serializers
from .models import ChatDetails, DjCheckpoint

class ChatDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatDetails
        fields = '__all__'

class DjCheckpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = DjCheckpoint
        fields = '__all__'