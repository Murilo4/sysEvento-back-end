from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
import os
from ...models import NormalUser, Event, UserName, Names, Questions
from ...models import Answers, EventQuestions, EventAnswer
from ...serializers.question import GetAllQuestions
from ...serializers.answer import GetAllAnswer
import jwt
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['GET'])
def get_event_and_questions(request, eventId):
    if request.method != "GET":
        return JsonResponse({"success": False,
                             "message": "Método inválido"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

    auth_header = request.headers.get('Authorization')
    if not auth_header:
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

    try:
        event_bd = Event.objects.get(id=event_id)
        username_list = UserName.objects.filter(
            event_id=event_id).order_by('create_order')

        # Montando o nome do evento
        names = [Names.objects.get(
            id=username.name_id
            ).name for username in username_list if Names.objects.filter(
            id=username.name_id).exists()]
        full_name = " ".join(names)

        photo_url = event_bd.photo.url if event_bd.photo else None

        event = {
            "eventName": full_name,
            "data": event_bd.data,
            "horarioInicio": event_bd.horario_inicio,
            "horarioFinal": event_bd.horario_final,
            "description": event_bd.descricao,
            "photo": photo_url
        }
    except Event.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "Evento não encontrado."},
                            status=status.HTTP_404_NOT_FOUND)

    # Buscar as perguntas associadas ao evento
    question_event_db = EventQuestions.objects.filter(event=event_id)
    if not question_event_db:
        return JsonResponse({"success": False,
                             "message":
                             "Nenhuma pergunta encontrada para este evento."},
                            status=status.HTTP_404_NOT_FOUND)

    response_data = []

    # Para cada pergunta associada ao evento
    for quest_event in question_event_db:
        question_db = Questions.objects.get(id=quest_event.question.id)

        # Buscar as respostas associadas à pergunta
        answer_event_db = EventAnswer.objects.filter(
            event=event_id, question=question_db.id)
        answers = []

        for answer_event in answer_event_db:
            answer_db = Answers.objects.get(id=answer_event.answer.id)
            # Serializar as respostas
            answer_serializer = GetAllAnswer(answer_db)
            answers.append(answer_serializer.data)

        # Serializar a pergunta
        question_serializer = GetAllQuestions(question_db)
        question_data = question_serializer.data

        # Adicionar as respostas à pergunta
        question_data['answers'] = answers

        response_data.append(question_data)

    return JsonResponse({
        "success": True,
        "message": "Evento, perguntas e respostas buscados com sucesso.",
        "event": event,
        "questions_and_answers": response_data
    }, status=status.HTTP_200_OK)
