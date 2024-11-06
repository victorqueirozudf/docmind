from rest_framework import serializers
from .models import ChatDetails, ChatCheckpoint, ChatWrite

class ChatDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatDetails
        fields = '__all__'

class ChatCheckpointSerializer(serializers.ModelSerializer):
    chat = serializers.PrimaryKeyRelatedField(queryset=ChatDetails.objects.all())

    class Meta:
        model = ChatCheckpoint
        fields = '__all__'

class ChatWriteSerializer(serializers.ModelSerializer):
    chat = serializers.PrimaryKeyRelatedField(queryset=ChatDetails.objects.all())

    class Meta:
        model = ChatWrite
        fields = '__all__'