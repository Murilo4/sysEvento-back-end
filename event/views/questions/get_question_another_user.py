from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
import jwt
import os
from ...models import Questions, Answers, EventStatistics, Event, EventQuestions
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['GET'])
def get_questions_user(request, filter_type):
    if request.method != "GET":
        return JsonResponse({"success": False,
                             "message": "Invalid method"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({
            "success": False,
            "message": "Token de acesso não fornecido ou formato inválido."
        }, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('id')
        if filter_type == 'user':
            user_events = EventStatistics.objects.filter(
                user_event=user_id).values_list('event', flat=True)
            created_events = Event.objects.filter(
                event_creator=user_id).values_list('id', flat=True)
            all_events = list(user_events) + list(created_events)
            questions = Questions.objects.filter(
                eventquestions__event__in=all_events)
        elif filter_type == 'other':
            user_events = EventStatistics.objects.filter(
                user_event=user_id).values_list('event', flat=True)
            questions = Questions.objects.exclude(
                eventquestions__event__in=user_events)
        else:
            questions = Questions.objects.all()
    except Questions.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "Error fetching questions"},
                            status=status.HTTP_400_BAD_REQUEST)

    question_responses = []

    for question in questions:
        options = Answers.objects.filter(question=question)
        events = Event.objects.filter(eventquestions__question=question)
        question_responses.append({
            'question_id': question.id,
            'question_text': question.question,
            'question_type': question.question_type,
            'options': [{'id': option.id, 'text': option.answer_option} for option in options],
            'events': [{'id': event.id} for event in events]
        })

    data = {
        'questions': question_responses
    }
    print(data)
    return JsonResponse({"success": True,
                         "message": "Questions fetched successfully",
                         "data": data},
                        status=status.HTTP_200_OK)
