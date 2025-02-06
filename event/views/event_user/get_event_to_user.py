from rest_framework.decorators import api_view  # , throttle_classes
from django.http import JsonResponse
from rest_framework import status
import os
from ...models import Event, UserName, Names

from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['GET'])
def get_event_user(request, eventId):
    if request.method != "GET":
        return JsonResponse({"success": False,
                             "message": "método invalido"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

    event_id = eventId
    event_bd = Event.objects.get(id=event_id)
    username_list = UserName.objects.filter(
            event_id=event_id).order_by('create_order')

    names = []
    for username in username_list:
        try:
            name_obj = Names.objects.get(id=username.name_id)
            names.append(name_obj.name)
        except Names.DoesNotExist:
            continue
    photo_url = event_bd.photo.url if event_bd.photo else None

    full_name = " ".join(names)
    event = {
        "eventName": full_name,
        "data": event_bd.data,
        "horarioInicio": event_bd.horario_inicio,
        "horarioFinal": event_bd.horario_final,
        "description": event_bd.descricao,
        "photo": photo_url,
        "isActive": event_bd.is_active
    }
    return JsonResponse({"success": True,
                        "message": "Evento buscado com sucesso",
                         "event": event},
                        status=status.HTTP_200_OK)


@api_view(['GET'])
def get_event_active(request, eventId):
    if request.method != "GET":
        return JsonResponse({"success": False,
                             "message": "método invalido"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

    event_id = eventId
    event_bd = Event.objects.get(id=event_id)

    event = {
        "isActive": event_bd.is_active
    }
    return JsonResponse({"success": True,
                        "message": "Evento buscado com sucesso",
                         "event": event},
                        status=status.HTTP_200_OK)
