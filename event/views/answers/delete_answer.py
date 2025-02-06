from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import NormalUser, Event, EventAnswer
import jwt
import os
from django.db import transaction
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ADDRESS_API_URL = os.getenv('ADDRESS_API_URL')


@api_view(['DELETE'])
def delete_answer(request, eventId, answerId):
    if request.method != 'DELETE':
        return JsonResponse({'success': False,
                             'message': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)
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
        event_id = eventId
        answer_id = answerId
        try:
            user = NormalUser.objects.get(id=user_id)
            event = Event.objects.get(id=event_id)
            if event.event_creator.id != user.id:
                return JsonResponse({"success": False,
                                    "message":
                                     "sem permissão para deletar a pergunta"},
                                    status=status.HTTP_401_UNAUTHORIZED)
        except (NormalUser.DoesNotExist, Event.DoesNotExist):
            return JsonResponse({
                'success': False,
                'message': 'Usuário não encontrado.'
            }, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            try:
                EventAnswer.objects.get(
                    event=event_id,
                    answer=answer_id).delete()
            except EventAnswer.DoesNotExist:
                pass

            return JsonResponse({'success': True,
                                'message': 'Evento deletado com sucesso!'},
                                status=status.HTTP_200_OK)

    except jwt.ExpiredSignatureError:
        return JsonResponse({'success': False,
                             'message': 'Token expirado.'},
                            status=status.HTTP_401_UNAUTHORIZED)

    except jwt.InvalidTokenError:
        return JsonResponse({'success': False,
                             'message': 'Token inválido.'},
                            status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Erro interno no servidor.',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
