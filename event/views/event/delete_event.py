from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import NormalUser, UserName, Event, EventQuestions
from ...models import EventStatistics, EventAnswer, UserEvent
import jwt
import os
from django.db import transaction
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['DELETE'])
def delete_event(request, eventId):
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
        try:
            NormalUser.objects.get(id=user_id)
            event = Event.objects.get(id=event_id)
            if event.event_creator.id != user_id:
                return JsonResponse({"success": False,
                                     "message":
                                    "sem permissão para deletar o evento"},
                                    status=status.HTTP_401_UNAUTHORIZED)
        except (NormalUser.DoesNotExist, Event.DoesNotExist):
            return JsonResponse({
                'success': False,
                'message': 'Usuário não encontrado.'
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            photo_path = event.photo.path if event.photo else None
            qr_code_path = event.qr_code.path if event.qr_code else None

            if photo_path and os.path.exists(photo_path):
                os.remove(photo_path)

            if qr_code_path and os.path.exists(qr_code_path):
                os.remove(qr_code_path)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Erro ao tentar apagar arquivos do evento.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        with transaction.atomic():
            try:
                UserName.objects.filter(event_id=event_id).delete()
                EventQuestions.objects.filter(event=event_id).delete()
                EventStatistics.objects.filter(event=event_id).delete()
                EventAnswer.objects.filter(event=event_id).delete()
                UserEvent.objects.filter(event=event_id).delete()
                event.delete()
            except (UserName.DoesNotExist, EventQuestions.DoesNotExist,
                    EventStatistics.DoesNotExist, EventAnswer.DoesNotExist,
                    EventQuestions.DoesNotExist):
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
