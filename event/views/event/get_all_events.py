from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import status
import os
import jwt
from dotenv import load_dotenv
from ...models import NormalUser, Event, UserName, Names
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['GET'])
def get_user_events(request):
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
    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    user_id = payload.get('id')

    try:
        NormalUser.objects.get(id=user_id)
    except NormalUser.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "Usuário não encontrado."},
                            status=status.HTTP_404_NOT_FOUND)

    events = Event.objects.filter(event_creator=user_id)

    # Verificação se há eventos
    if not events:
        return JsonResponse({"success": False,
                             "message": "Nenhum evento encontrado."},
                            status=status.HTTP_404_NOT_FOUND)

    event_list = []
    for event in events:
        username_list = UserName.objects.filter(
            event_id=event.id).order_by('create_order')

        names = []
        for username in username_list:
            try:
                name_obj = Names.objects.get(id=username.name_id)
                names.append(name_obj.name)
            except Names.DoesNotExist:
                continue

        full_name = " ".join(names)

        # Obter a URL da foto
        photo_url = event.photo.url if event.photo else None

        # Obter a URL do QR Code
        qr_code_url = event.qr_code.url if event.qr_code else None

        # Preparando os dados para retorno
        event_data = {
            "id": event.id,
            "eventName": full_name,
            "data": event.data,
            "isActive": event.is_active,
            "horarioInicio": event.horario_inicio,
            "horarioFinal": event.horario_final,
            "description": event.descricao,
            "photo": photo_url,  # URL da foto do evento
            "qrCode": qr_code_url,  # URL do QR Code do evento
            "participantes": event.participantes
        }
        event_list.append(event_data)

    return JsonResponse({"success": True,
                         "message": "Eventos encontrados com sucesso",
                         "events": event_list},
                        status=status.HTTP_200_OK)
