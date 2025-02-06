from rest_framework.decorators import api_view  # , throttle_classes
from django.http import JsonResponse
from rest_framework import status
import os
from ...models import NormalUser, Questions, ActualQuestion, EventAnswer
from ...models import Answers
from ...serializers.answer import GetAllAnswer
from ...serializers.question import GetAllQuestions
import jwt
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['GET'])
def get_question(request, eventId, questionId):
    if request.method != "GET":
        return JsonResponse({"success": False,
                             "message": "método invalido"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({
            "success": False,
            "message": "Token de acesso não fornecido ou formato inválido."
        }, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]

    payload = jwt.decode(token,
                         SECRET_KEY, algorithms=['HS256'])
    user_id = payload.get('id')
    NormalUser.objects.get(id=user_id)

    event_id = eventId
    question_id = questionId

    question_db = Questions.objects.get(
        id=question_id, event=event_id)
    photo_url = question_db.photo.url if question_db.photo else None

    question = {
        "id": question_db.id,
        "question": question_db.question,
        "questionType": question_db.question_type,
        "photo": photo_url
    }
    return JsonResponse({"success": True,
                        "message": "pergunta retornada com sucesso",
                         "question": question},
                        status=status.HTTP_200_OK)


@api_view(['GET'])
def get_question_event(request, eventId):
    if request.method != "GET":
        return JsonResponse({"success": False,
                             "message": "método invalido"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
    event_id = eventId
    question_actual = ActualQuestion.objects.get(event=event_id)
    print(question_actual)
    question_id = question_actual.actual_question

    question_db = Questions.objects.get(
        id=question_id, event=event_id)
    answer_event_db = EventAnswer.objects.filter(event=event_id,
                                                 question=question_db.id)
    answers = []
    response_data = []
    for answer_event in answer_event_db:
        answer_db = Answers.objects.get(id=answer_event.answer.id)

        answer_serializer = GetAllAnswer(answer_db)
        answers.append(answer_serializer.data)

    question_serializer = GetAllQuestions(question_db)
    question_data = question_serializer.data

    question_data['answers'] = answers

    response_data.append(question_data)
    return JsonResponse({"success": True,
                        "message": "pergunta retornada com sucesso",
                         "question": response_data},
                        status=status.HTTP_200_OK)
