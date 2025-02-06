from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import UserEvent
import os
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['GET'])
def get_user_data(request, userId, eventId):
    if request.method != "GET":
        return JsonResponse({"success": False,
                             "message": "metodo invalido"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
    event_id = eventId
    user_id = userId
    try:
        user = UserEvent.objects.get(id=user_id, event=event_id)
        user_event_res = {
            "id": user.id,
            "name": user.name,
            "email": user.email if user.email else None,
            "phone": user.phone if user.phone else None,
            "cpf": user.cpf if user.cpf else None,
            "cnpj": user.cnpj if user.cnpj else None,
            "event": user.event.id
        }
        return JsonResponse({
            'success': True,
            'message': "criado com sucesso",
            "data": user_event_res,
        }, status=status.HTTP_200_OK)
    except UserEvent.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "dados não retornados"},
                            status=status.HTTP_400_BAD_REQUEST)
