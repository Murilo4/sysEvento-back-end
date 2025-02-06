from rest_framework import serializers
from ..models import Event, Questions, EventStatistics, Answers


class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answers
        fields = ['id', 'answer_text']


class QuestionSerializer(serializers.ModelSerializer):
    answer_options = AnswerOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Questions
        fields = ['id', 'question_text', 'question_type', 'photo', 'answer_options']


class EventStatisticsSerializer(serializers.ModelSerializer):
    answer_option = AnswerOptionSerializer(read_only=True)

    class Meta:
        model = EventStatistics
        fields = ['question', 'answer_option', 'answer_text']


class EventDataSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'event_name', 'description', 'photo', 'questions']
