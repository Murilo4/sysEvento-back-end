from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import NormalUser, UserName, Names, UserEvent
from ...serializers.event import UserEventSerializer
import jwt
import os
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['POST'])
def register_user_event(request, eventId):
    if request.method != "POST":
        return JsonResponse({"success": False,
                             "message": "metodo invalido"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        event_id = eventId
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get('id')
        get_user = NormalUser.objects.get(id=user_id)
        username_list = UserName.objects.filter(
            user_id=get_user.id).order_by('create_order')
        names = []
        for username in username_list:
            try:
                name_obj = Names.objects.get(id=username.name_id)
                names.append(name_obj.name)
            except Names.DoesNotExist:
                continue

        full_name = " ".join(names)
        user_event = {
            "name": full_name,
            "email": get_user.email,
            "phone": get_user.phone if get_user.phone else None,
            "cpf": get_user.cpf if get_user.cpf else None,
            "cnpj": get_user.cnpj if get_user.cnpj else None,
            "event": event_id,
            "user": get_user.id
        }
        try:
            user = UserEvent.objects.get(user=user_id)
            user.delete()
        except UserEvent.DoesNotExist:
            pass
        new_user_event = UserEventSerializer(data=user_event)
        if not new_user_event.is_valid():
            return JsonResponse({"success": False,
                                 "message": "erro ao cadastrar ao evento"},
                                status=status.HTTP_400_BAD_REQUEST)
        new_user_event.save()
        get_user_event = UserEvent.objects.get(event=event_id,
                                               user=get_user.id)
        user_event_res = {
            "id": get_user_event.id,
            "name": get_user_event.name,
            "email": get_user_event.email if get_user_event.email else None,
            "phone": get_user_event.phone if get_user_event.phone else None,
            "cpf": get_user_event.cpf if get_user_event.cpf else None,
            "cnpj": get_user_event.cnpj if get_user_event.cnpj else None,
            "event": get_user_event.event
        }
        return JsonResponse({
            'success': True,
            'message': "criado com sucesso",
            "data": user_event_res,
        }, status=status.HTTP_200_OK)
    except Exception:
        userName = request.data.get("fullName")
        email = request.data.get(
            "email")
        phone = request.data.get(
            "phone")
        cpf = request.data.get("cpf")
        cnpj = request.data.get("cnpj")
        user_event = {
            "name": userName,
            "email": email,
            "phone": phone,
            "cpf": cpf,
            "cnpj": cnpj,
            "event": event_id
        }
        if email is None:
            user_event["email"] = None
        if phone is None:
            user_event["phone"] = None
        if cpf is None:
            user_event["cpf"] = None
        if cnpj is None:
            user_event["cnpj"] = None
        try:
            user = UserEvent.objects.get(email=email, phone=phone,
                                         cpf=cpf, cnpj=cnpj, event=event_id)
            user.delete()
        except UserEvent.DoesNotExist:
            pass
        new_user_event = UserEventSerializer(data=user_event)
        if not new_user_event.is_valid(raise_exception=True):
            return JsonResponse({"success": False,
                                 "message": "erro ao cadastrar ao evento"},
                                status=status.HTTP_400_BAD_REQUEST)
        new_user_event.save()
        if cpf:
            get_user_event = UserEvent.objects.get(event=event_id,
                                                   cpf=cpf)
        if cnpj:
            get_user_event = UserEvent.objects.get(event=event_id,
                                                   cnpj=cnpj)

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
