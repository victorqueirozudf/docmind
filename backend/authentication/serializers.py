from rest_framework import serializers


class AuthenticationSerializers(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
