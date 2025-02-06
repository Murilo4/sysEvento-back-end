from rest_framework import serializers
from ..models import Answers, EventAnswer


class CreateAnswer(serializers.ModelSerializer):
    class Meta:
        model = Answers
        fields = ['answer_option', 'is_correct', 'question', 'event']

    def create(self, validated_data):
        answer = Answers(**validated_data)
        answer.save()
        return answer


class CreateEventAnswer(serializers.ModelSerializer):
    class Meta:
        model = EventAnswer
        fields = ['event', 'answer', 'question']

    def create(self, validated_data):
        event_answer = EventAnswer(**validated_data)
        event_answer.save()
        return event_answer


class GetAllAnswer(serializers.ModelSerializer):
    answer = serializers.CharField(source="answer_option")
    isCorrect = serializers.BooleanField(source="is_correct")

    class Meta:
        model = EventAnswer
        fields = ['id', 'answer', 'isCorrect']


class UpdateAnswer(serializers.ModelSerializer):

    class Meta:
        model = Answers
        fields = ['answer_option', 'is_correct']

    def update(self, instance, validated_data):
        instance.answer_option = validated_data.get(
            'answer_option', instance.answer_option)
        instance.is_correct = validated_data.get(
            'is_correct', instance.is_correct)

        instance.save()

        return instance
