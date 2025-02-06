from rest_framework import serializers
from ..models import NormalUser, lastPasswords, UserAuthorization


class CreateNormalUser(serializers.ModelSerializer):

    class Meta:
        model = NormalUser
        fields = ('email', 'password', 'cpf', 'phone', 'cnpj',
                  'photo', 'last_pass_change', 'user_type')

    def create(self, validated_data):
        user = NormalUser(**validated_data)
        user.save()
        return user


class UpdateNormalUser(serializers.ModelSerializer):
    class Meta:
        model = NormalUser
        fields = 'email', 'cpf', 'phone', 'cnpj', 'photo'

    def update(self, instance, validated_data):
        instance.email = validated_data.get(
            'email', instance.email)
        instance.cpf = validated_data.get(
            'cpf', instance.cpf)
        instance.phone = validated_data.get(
            'phone', instance.phone)
        instance.photo = validated_data.get(
            'photo', instance.photo)
        instance.cnpj = validated_data.get(
            'cnpj', instance.cnpj)

        instance.save()

        return instance


class UpdateValidationNormalUser(serializers.ModelSerializer):
    class Meta:
        model = NormalUser
        fields = ['is_validated']

    def update(self, instance, validated_data):
        instance.is_validated = validated_data.get(
            'is_validated', instance.is_validated)

        instance.save()

        return instance


class SaveOldPassword(serializers.ModelSerializer):
    class Meta:
        model = lastPasswords
        fields = ['password_hash', 'user']

    def create(self, validated_data):
        last_password = lastPasswords(**validated_data)
        last_password.save()
        return last_password


class UpdateaPassword(serializers.ModelSerializer):
    class Meta:
        model = NormalUser
        fields = ['password']

    def update(self, instance, validated_data):
        instance.password = validated_data.get(
            'password', instance.password)

        instance.save()

        return instance


class CreateAuthorizationEvents(serializers.ModelSerializer):

    class Meta:
        model = UserAuthorization
        fields = ('user', 'auth')

    def create(self, validated_data):
        user = UserAuthorization(**validated_data)
        user.save()
        return user
