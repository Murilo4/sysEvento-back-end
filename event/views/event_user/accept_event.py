from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
import jwt
import os
from ...models import NormalUser, Names, UserName, UserEvent
from ...models import Event
from ...serializers.event import UserEventSerializer
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['POST'])
def accept_event(request, eventId):
    if request.method != 'POST':
        return JsonResponse({"success": False,
                             "message": "Metodo invalido"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({
                "success": False,
                "message": "Token de acesso não fornecido ou formato inválido."
            }, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]

        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        user_id = payload.get('id')
        user = NormalUser.objects.get(id=user_id)
    except NormalUser.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "usuario não localizado"},
                            status=status.HTTP_400_BAD_REQUEST)
    username_list = UserName.objects.filter(
            user_id=user.id).order_by('create_order')
    names = []
    for username in username_list:
        try:
            name_obj = Names.objects.get(id=username.name_id)
            names.append(name_obj.name)
        except Names.DoesNotExist:
            continue

    full_name = " ".join(names)
    user_event = {
        "email": user.email,
        "cpf": user.cpf if user.cpf else None,
        "cnpj": user.cnpj if user.cnpj else None,
        "name": full_name,
        "phone": user.phone if user.phone else None,
        "event": eventId
    }

    try:
        user = UserEvent.objects.get(email=user.email, phone=user.phone,
                                     cpf=user.cpf, cnpj=user.cnpj,
                                     event=eventId)
        user.delete()
    except UserEvent.DoesNotExist:
        pass
    new_user_event = UserEventSerializer(data=user_event)
    if not new_user_event.is_valid(raise_exception=True):
        return JsonResponse({"success": False,
                             "message": "erro ao cadastrar ao evento"},
                            status=status.HTTP_400_BAD_REQUEST)
    new_user_event.save()

    if user.cpf:
        get_user_event = UserEvent.objects.get(event=eventId,
                                               cpf=user.cpf)
    elif user.cnpj:
        get_user_event = UserEvent.objects.get(event=eventId,
                                               cnpj=user.cnpj)

    user_event_res = {
        "id": get_user_event.id,
        "name": get_user_event.name,
        "email": get_user_event.email if get_user_event.email else None,
        "phone": get_user_event.phone if get_user_event.phone else None,
        "cpf": get_user_event.cpf if get_user_event.cpf else None,
        "cnpj": get_user_event.cnpj if get_user_event.cnpj else None,
        "event": get_user_event.event.id
    }
    return JsonResponse({
        'success': True,
        'message': "criado com sucesso",
        "data": user_event_res,
    }, status=status.HTTP_200_OK)


@api_view(["POST"])
def validate_owner(request, eventId):
    if request.method != "POST":
        return JsonResponse({"success": False,
                             "message": "Metodo invalido"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({
                "success": False,
                "message": "Token de acesso não fornecido ou formato inválido."
            }, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]

        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        user_id = payload.get('id')
        user = NormalUser.objects.get(id=user_id)
    except NormalUser.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "usuario não localizado"},
                            status=status.HTTP_400_BAD_REQUEST)

    get_event = Event.objects.get(id=eventId)

    if user.id == get_event.id:
        return JsonResponse({"success": True,
                             "message": "evento do criado"},
                            status=status.HTTP_200_OK)
    else:
        return JsonResponse({"success": False,
                             "message": "evento não pertence a este usuario"},
                            status=status.HTTP_400_BAD_REQUEST)
