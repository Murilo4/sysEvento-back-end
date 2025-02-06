from rest_framework.decorators import api_view  # , throttle_classes
from django.http import JsonResponse
from rest_framework import status
import os
from ...models import NormalUser, Event, UserName, Names
import jwt
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['GET'])
def get_event(request, eventId):
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
        "participants": event_bd.participantes,
        "photo": photo_url,
        "isActive": event_bd.is_active
    }
    return JsonResponse({"success": True,
                        "message": "Evento buscado com sucesso",
                         "event": event},
                        status=status.HTTP_200_OK)
