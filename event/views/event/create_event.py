from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from io import BytesIO
import os
import qrcode
from ...models import NormalUser, Names, UserAuthorization
from ...serializers.event import CreateEvent, CreateQrCode
from ...serializers.Names import CreateNames, CreateUserNameEvent
from django.db import transaction
from django.core.files.base import ContentFile
import jwt
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['POST'])
def create_event(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Método inválido"},
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
    except jwt.ExpiredSignatureError:
        return JsonResponse({"success": False,
                             "message": "Token expirado."},
                            status=status.HTTP_401_UNAUTHORIZED)
    except jwt.DecodeError:
        return JsonResponse({"success": False,
                             "message": "Erro ao decodificar o token."},
                            status=status.HTTP_401_UNAUTHORIZED)

    try:
        user = NormalUser.objects.get(id=user_id)
        user_valid = UserAuthorization.objects.filter(user=user.id)
        valid_user = any(i.auth == "SysEventos" for i in user_valid)
    except NormalUser.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "Usuário não encontrado."},
                            status=status.HTTP_404_NOT_FOUND)

    if not valid_user:
        return JsonResponse({"success": False,
                             "message":
                             "Você não tem permissão para criar um evento"},
                            status=status.HTTP_401_UNAUTHORIZED)

    # Recebendo os dados do evento
    data = request.data.get("data")
    event_name = request.data.get("eventName")
    horario_ini = request.data.get("horarioIni")
    horario_final = request.data.get("horarioFinal")
    descricao = request.data.get("description")
    participants = request.data.get('participants')
    photo = request.data.get("photo", None)

    event = {
        "data": data,
        "horario_inicio": horario_ini,
        "horario_final": horario_final,
        "descricao": descricao,
        "photo": photo,
        "participantes": participants,
        "event_creator": user_id
    }

    try:
        with transaction.atomic():
            new_event = CreateEvent(data=event)
            if new_event.is_valid(raise_exception=True):
                event_data = new_event.save()
                dt = f'http://127.0.0.1:3000/event/invitation/{event_data.id}'
                qr = qrcode.make(dt)
                image_buffer = BytesIO()
                qr.save(image_buffer, "PNG")
                image_data = image_buffer.getvalue()
                qr_filename = f'{event_data.id}_qr.png'

                qr_code_file = ContentFile(image_data, name=qr_filename)
                qr_code_serializer = CreateQrCode(
                    event_data,
                    data={'qr_code': qr_code_file},
                    partial=True)
                if qr_code_serializer.is_valid(raise_exception=True):
                    qr_code_serializer.save()

                userName = event_name.strip()
                name = [n.lower().strip()
                        for n in userName.split() if n.strip()]
                created_names, referencias = create_names(name)

                if not created_names:
                    return JsonResponse({"success": False,
                                         "message": "Erro ao criar nome"},
                                        status=status.HTTP_400_BAD_REQUEST)

                order = 1
                for referencia in referencias:
                    link_name = Names.objects.get(id=referencia)
                    serializer_user = CreateUserNameEvent(
                        data={'name_id': link_name.id,
                              'event_id': event_data.id,
                              'create_order': order})

                    if serializer_user.is_valid(raise_exception=True):
                        serializer_user.save()
                        order += 1
                    else:
                        return JsonResponse({"success": False,
                                             "message":
                                             "Erro ao criar nome do usuario"},
                                            status=status.HTTP_400_BAD_REQUEST)

                return JsonResponse({"success": True,
                                     "message": "Evento criado com sucesso"},
                                    status=status.HTTP_200_OK)

            else:
                return JsonResponse({"success": False,
                                     "message": "Erro inesperado"},
                                    status=status.HTTP_404_NOT_FOUND)

    except Exception:
        return JsonResponse({"success": False,
                             "message": "Erro inesperado"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def create_names(name):
    referencias = []
    created_names = True
    for nome in name:
        nome_lower = nome.lower().strip()
        try:
            obj = Names.objects.get(name=nome_lower)
            referencias.append(obj.id)
        except Names.DoesNotExist:
            test_data = {"name": nome_lower}
            serializer = CreateNames(data=test_data)
            if serializer.is_valid():
                obj = serializer.save()
                new_name = Names.objects.get(name=obj.name)
                referencias.append(new_name.id)
            else:
                created_names = False
    return created_names, referencias
