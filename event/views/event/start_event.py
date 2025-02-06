from rest_framework.decorators import api_view  # , throttle_classes
from django.http import JsonResponse
from rest_framework import status
import os
from ...models import NormalUser, Event, ActualQuestion
from ...serializers.event import StartEvent, ActualQuestionSeria
from ...serializers.event import CreateFilter, UpdateQuestionSeria
import jwt
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['POST'])
def start_event(request, eventId, questionId):
    if request.method != "POST":
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
    user = NormalUser.objects.get(id=user_id)

    event_id = eventId
    event_bd = Event.objects.get(id=event_id,
                                 event_creator=user.id)
    question_id = questionId

    set_start = StartEvent(event_bd,
                           data={"is_active": 1},
                           partial=True)
    if not set_start.is_valid():
        return JsonResponse({"success": False,
                             "message": "Não foi possivel iniciar o evento"},
                            status=status.HTTP_406_NOT_ACCEPTABLE)

    set_start.save()
    event_filter = CreateFilter(data={"event": event_id, "is_active": True})
    if not event_filter.is_valid():
        return JsonResponse({"success": False,
                             "message": "Não foi possivel iniciar o evento"},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
    new_filter = event_filter.save()
    try:
        alread_exist = ActualQuestion.objects.get(event=event_id)
        update_actual = UpdateQuestionSeria(
            alread_exist,
            data={"actual_question": question_id},
            partial=True)
        if not update_actual.is_valid():
            return JsonResponse({"success": False,
                                "message":
                                 "Não foi possivel iniciar o evento"},
                                status=status.HTTP_406_NOT_ACCEPTABLE)

        update_actual.save()

    except ActualQuestion.DoesNotExist:

        actual_question = ActualQuestionSeria(
            data={"event": event_id, "actual_question": question_id})

        if not actual_question.is_valid():
            return JsonResponse({"success": False,
                                "message":
                                 "Não foi possivel iniciar o evento"},
                                status=status.HTTP_406_NOT_ACCEPTABLE)

        actual_question.save()

    return JsonResponse({"success": True,
                        "message": "Evento iniciado com sucesso",
                         "filterId": new_filter.id},
                        status=status.HTTP_200_OK)
