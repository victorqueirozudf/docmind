from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ChatDetails, DjCheckpoint

class ChatDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatDetails
        fields = '__all__'

class DjCheckpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = DjCheckpoint
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user