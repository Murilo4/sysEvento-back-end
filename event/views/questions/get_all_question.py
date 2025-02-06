from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
import os
from ...models import NormalUser, Questions, Answers, EventQuestions
from ...models import EventAnswer, EventFilter
from ...serializers.question import GetAllQuestions
from ...serializers.answer import GetAllAnswer
import jwt
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['GET'])
def get_questions_and_answers(request, eventId):
    if request.method != "GET":
        return JsonResponse({"success": False,
                             "message": "Método inválido"},
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
        NormalUser.objects.get(id=user_id)
    except jwt.ExpiredSignatureError:
        return JsonResponse({"success": False,
                             "message": "Token expirado."},
                            status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return JsonResponse({"success": False,
                             "message": "Token inválido."},
                            status=status.HTTP_401_UNAUTHORIZED)

    event_id = eventId
    if not event_id:
        return JsonResponse({"success": False,
                             "message": "O ID do evento não foi fornecido."},
                            status=status.HTTP_400_BAD_REQUEST)

    # Buscar as perguntas associadas ao evento
    question_event_db = EventQuestions.objects.filter(event=event_id)
    if not question_event_db:
        return JsonResponse({"success": False,
                             "message": "Nenhuma pergunta encontrada"},
                            status=status.HTTP_404_NOT_FOUND)

    response_data = []

    # Para cada pergunta associada ao evento
    for quest_event in question_event_db:
        question_db = Questions.objects.get(id=quest_event.question.id)

        answer_event_db = EventAnswer.objects.filter(event=event_id,
                                                     question=question_db.id)
        answers = []

        for answer_event in answer_event_db:
            answer_db = Answers.objects.get(id=answer_event.answer.id)

            answer_serializer = GetAllAnswer(answer_db)
            answers.append(answer_serializer.data)

        question_serializer = GetAllQuestions(question_db)
        question_data = question_serializer.data

        question_data['answers'] = answers

        response_data.append(question_data)
    filter = None
    try:
        get_filter = EventFilter.objects.get(event=event_id, is_active=1)
        filter = get_filter.id
    except EventFilter.DoesNotExist:
        pass
    return JsonResponse({"success": True,
                         "message":
                         "Perguntas e respostas buscadas com sucesso",
                         "data": response_data,
                         "filter": filter},
                        status=status.HTTP_200_OK)
