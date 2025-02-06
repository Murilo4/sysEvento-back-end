from rest_framework import serializers
from ..models import Event, ActualQuestion, UserEvent, EventStatistics
from ..models import EventFilter


class CreateEvent(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'data', 'participantes', 'horario_inicio',
                  'horario_final', 'descricao', 'photo', 'event_creator']

    def create(self, validated_data):
        event = Event(**validated_data)
        event.save()
        return event


class CreateFilter(serializers.ModelSerializer):
    class Meta:
        model = EventFilter
        fields = ['id', 'event', 'is_active']

    def create(self, validated_data):
        event = EventFilter(**validated_data)
        event.save()
        return event
    

class UpdateEventFilter(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['is_active']

    def update(self, instance, validated_data):
        instance.is_active = validated_data.get(
            'is_active', instance.is_active)

        instance.save()

        return instance


class CreateQrCode(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['qr_code']

    def create(self, validated_data):
        event = Event(**validated_data)
        event.save()
        return event


class UpdateEvent(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['data', 'horario_inicio', 'participantes', 'horario_final',
                  'descricao', 'photo']

    def update(self, instance, validated_data):
        instance.data = validated_data.get(
            'data', instance.data)
        instance.horario_inicio = validated_data.get(
            'horario_inicio', instance.horario_inicio)
        instance.horario_final = validated_data.get(
            'horario_final', instance.horario_final)
        instance.descricao = validated_data.get(
            'descricao', instance.descricao)
        instance.participantes = validated_data.get(
            'participantes', instance.participantes)
        instance.photo = validated_data.get(
            'photo', instance.photo)

        instance.save()

        return instance


class StartEvent(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['is_active']

    def update(self, instance, validated_data):
        instance.is_active = validated_data.get(
            'is_active', instance.is_active)
        instance.save()

        return instance


class ActualQuestionSeria(serializers.ModelSerializer):
    class Meta:
        model = ActualQuestion
        fields = ['event', 'actual_question']

    def create(self, validated_data):
        event = ActualQuestion(**validated_data)
        event.save()
        return event


class UpdateQuestionSeria(serializers.ModelSerializer):
    class Meta:
        model = ActualQuestion
        fields = ['event', 'actual_question']

    def update(self, instance, validated_data):
        instance.actual_question = validated_data.get(
            'actual_question', instance.actual_question)
        instance.save()

        return instance


class UserEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEvent
        fields = ['event', 'name', 'email',
                  'cpf', 'cnpj', 'phone', 'user']

    def create(self, validated_data):
        event = UserEvent(**validated_data)
        event.save()
        return event


class CreateStatistics(serializers.ModelSerializer):
    class Meta:
        model = EventStatistics
        fields = ['event', 'answer_text', 'answer', 'question', 'user_event']

    def create(self, validated_data):
        event = EventStatistics(**validated_data)
        event.save()
        return event
