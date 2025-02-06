from rest_framework import serializers
from ..models import Names, UserName


class CreateNames(serializers.ModelSerializer):
    class Meta:
        model = Names
        fields = ['name']

    def create(self, validated_data):
        name = Names(**validated_data)
        name.save()
        return name


class CreateUserName(serializers.ModelSerializer):
    class Meta:
        model = UserName
        fields = ['name_id', 'user_id', 'create_order']

    def create(self, validated_data):
        username = UserName(**validated_data)
        username.save()
        return username


class CreateUserNameAddress(serializers.ModelSerializer):
    class Meta:
        model = UserName
        fields = ['name_id', 'address', 'create_order']

    def create(self, validated_data):
        username = UserName(**validated_data)
        username.save()
        return username


class CreateUserNameEvent(serializers.ModelSerializer):
    class Meta:
        model = UserName
        fields = ['name_id', 'event_id', 'create_order']

    def create(self, validated_data):
        username = UserName(**validated_data)
        username.save()
        return username
