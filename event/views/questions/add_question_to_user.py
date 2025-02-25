from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import Questions, Answers, Event
from ...serializers.question import CreateEventQuestions
from ...serializers.answer import CreateEventAnswer
import jwt
import os
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['POST'])
def add_question_to_user(request):
    if request.method != "POST":
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
        jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return JsonResponse({"success": False,
                             "message": "Token expirado"},
                            status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return JsonResponse({"success": False,
                             "message": "Token inválido"},
                            status=status.HTTP_401_UNAUTHORIZED)

    question_id = request.data.get('questionId')
    event_ids = request.data.get('eventIds', [])
    add_options = request.data.get('includeOptions', False)
    print(question_id, event_ids, add_options)
    try:
        question = Questions.objects.get(id=question_id)
    except Questions.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "Pergunta não encontrada"},
                            status=status.HTTP_400_BAD_REQUEST)

    for event_id in event_ids:
        try:
            event = Event.objects.get(id=event_id)
            event_question_data = {'event': event.id, 'question': question.id}
            event_question_serializer = CreateEventQuestions(
                data=event_question_data)
            if event_question_serializer.is_valid():
                event_question_serializer.save()
            else:
                return JsonResponse({"success": False,
                                     "message": "Erro ao criar EventQuestions",
                                     "errors":
                                     event_question_serializer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)
            if add_options and question.question_type in ['multiple_choice',
                                                          'single_choice']:
                options = Answers.objects.filter(question=question)
                for option in options:
                    event_answer_data = {
                        'event': event.id,
                        'question': question.id,
                        'answer': option.id}
                    event_answer_serializer = CreateEventAnswer(
                        data=event_answer_data)
                    if event_answer_serializer.is_valid():
                        event_answer_serializer.save()
                    else:
                        return JsonResponse({"success": False,
                                             "message":
                                             "Erro ao criar EventAnswer",
                                             "errors":
                                             event_answer_serializer.errors},
                                            status=status.HTTP_400_BAD_REQUEST)
        except Event.DoesNotExist:
            return JsonResponse({"success": False,
                                 "message":
                                 f"Evento com id {event_id} não encontrado"},
                                status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({"success": True,
                         "message": "Pergunta adicionada com sucesso"},
                        status=status.HTTP_200_OK)
