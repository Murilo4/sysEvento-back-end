from rest_framework import serializers
from ..models import Questions, EventQuestions


class CreateQuestions(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields = ['question', 'question_type', 'event', 'photo']

    def create(self, validated_data):
        question = Questions(**validated_data)
        question.save()
        return question


class CreateEventQuestions(serializers.ModelSerializer):
    class Meta:
        model = EventQuestions
        fields = ['event', 'question']

    def create(self, validated_data):
        event_question = EventQuestions(**validated_data)
        event_question.save()
        return event_question


class GetAllQuestions(serializers.ModelSerializer):
    questionType = serializers.CharField(source="question_type")

    class Meta:
        model = Questions
        fields = ['id', 'question', 'questionType', 'photo']


class UpdateQuestion(serializers.ModelSerializer):

    class Meta:
        model = Questions
        fields = ['question', 'question_type', 'photo']

    def update(self, instance, validated_data):
        instance.question = validated_data.get(
            'question', instance.question)
        instance.question_type = validated_data.get(
            'question_type', instance.question_type)
        instance.photo = validated_data.get(
            'photo', instance.photo)

        instance.save()

        return instance


class UpdateQuestionPhoto(serializers.ModelSerializer):

    class Meta:
        model = Questions
        fields = ['photo']

    def update(self, instance, validated_data):
        instance.photo = validated_data.get(
            'photo', instance.photo)

        instance.save()

        return instance
