from rest_framework import serializers
from ..models import userSession


class CreateSession(serializers.ModelSerializer):
    class Meta:
        model = userSession
        fields = ('user_session', 'session_token')

    def create(self, validated_data):
        session = userSession(**validated_data)
        session.save()
        return session
