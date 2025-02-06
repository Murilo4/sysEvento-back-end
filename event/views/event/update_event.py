import os
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
import jwt
from django.conf import settings
from ...models import Event, Names, NormalUser, UserName
from ...serializers.event import UpdateEvent
from django.db import transaction
from ...serializers.Names import CreateNames, CreateUserNameEvent
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['PUT'])
def update_event(request, eventId):
    if request.method != "PUT":
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
    except jwt.ExpiredSignatureError:
        return JsonResponse({"success": False,
                             "message": "Token expired"},
                            status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return JsonResponse({"success": False,
                             "message": "Invalid token"},
                            status=status.HTTP_401_UNAUTHORIZED)

    event_id = eventId
    try:
        event_db = Event.objects.get(id=event_id, event_creator=user_id)
    except Event.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "Event not found"},
                            status=status.HTTP_404_NOT_FOUND)

    NormalUser.objects.get(id=user_id)

    data = request.data.get("data")
    event_name = request.data.get("eventName")
    horario_ini = request.data.get("horarioIni")
    horario_final = request.data.get("horarioFinal")
    descricao = request.data.get("description")
    participants = request.data.get('participants')
    photo = request.data.get("photo")

    event = {
            "data": data,
            "horario_inicio": horario_ini,
            "horario_final": horario_final,
            "descricao": descricao,
            "participantes": participants
        }

    old_photo = event_db.photo.name if event_db.photo else None
    with transaction.atomic():
        if photo:
            if old_photo:
                old_photo_path = os.path.join(settings.MEDIA_ROOT, old_photo)
                if os.path.exists(old_photo_path):
                    os.remove(old_photo_path)

            event = {
                "data": data,
                "horario_inicio": horario_ini,
                "horario_final": horario_final,
                "descricao": descricao,
                "participantes": participants,
                "photo": photo
            }
        elif not photo:
            event_db.photo = old_photo

        update_event = UpdateEvent(event_db, data=event, partial=True)
        if update_event.is_valid(raise_exception=True):
            update_event.save()
        else:
            return JsonResponse({"success": False,
                                "message": "Erro inesperado"},
                                status=status.HTTP_400_BAD_REQUEST)

        # Names handling
        username_list = UserName.objects.filter(
            event_id=event_id).order_by('create_order')
        names = []
        for username in username_list:
            try:
                name_obj = Names.objects.get(id=username.name_id)
                names.append(name_obj.name)
            except Names.DoesNotExist:
                continue

        full_name_from_db = " ".join(names).lower().strip()
        update_name = event_name.lower().strip()

        if update_name != full_name_from_db:
            db_name = full_name_from_db.split()
            name_list = update_name.split()

            new_names = [name for name in name_list if name not in db_name]

            UserName.objects.filter(event_id=event_id).delete()
            referencias = []
            for new_name in new_names:
                try:
                    name_obj = Names.objects.get(name=new_name)
                    referencias.append(name_obj.id)
                except Names.DoesNotExist:
                    name_data = {"name": new_name}
                    serializer = CreateNames(data=name_data)
                    if serializer.is_valid():
                        new_name_obj = serializer.save()
                        referencias.append(new_name_obj.id)
                    else:
                        return JsonResponse({'success': False,
                                            'message':
                                             'Erro ao criar novo nome',
                                             'error': serializer.errors},
                                            status=status.HTTP_400_BAD_REQUEST)
            order = 1
            if referencias:
                for referencia in referencias:
                    try:
                        serializer_user = CreateUserNameEvent(
                            data={'name_id': referencia,
                                  'event_id': event_id,
                                  'create_order': order})
                        if serializer_user.is_valid():
                            serializer_user.save()
                            order += 1
                        else:
                            return JsonResponse({'success': False,
                                                'message':
                                                 'Erro ao criar nome'})
                    except Exception:
                        return JsonResponse({'success': False,
                                            'message': 'Erro inesperado'},
                                            status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({"success": True,
                            "message": "Evento atualizado com sucesso"},
                            status=status.HTTP_200_OK)


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
