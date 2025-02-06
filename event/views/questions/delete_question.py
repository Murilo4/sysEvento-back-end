from rest_framework.decorators import api_view  # , throttle_classes
from django.http import JsonResponse
from rest_framework import status
from ...models import NormalUser, Event, EventQuestions, Questions, Answers
from django.db import transaction
import jwt
import os
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['DELETE'])
def delete_question(request, eventId, questionId):
    if request.method != 'DELETE':
        return JsonResponse({'success': False,
                             'message': 'Método de requisição inválido'},
                            status=status.HTTP_400_BAD_REQUEST)

    try:
        # Autenticação do usuário
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
        question_id = questionId

        # Verificação se o usuário e o evento existem
        try:
            NormalUser.objects.get(id=user_id)
            event = Event.objects.get(id=event_id)
            question = Questions.objects.get(id=question_id)
            if event.event_creator.id != user_id:
                return JsonResponse({"success": False,
                                     "message":
                                    "Você não tem permissão."},
                                    status=status.HTTP_401_UNAUTHORIZED)
        except (NormalUser.DoesNotExist, Event.DoesNotExist,
                Questions.DoesNotExist):
            return JsonResponse({
                'success': False,
                'message': 'Usuário, evento ou pergunta não encontrados.'
            }, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            # Verificar se a pergunta está vinculada a mais de um evento
            event_count = EventQuestions.objects.filter(
                question=question).count()

            if event_count > 1:
                EventQuestions.objects.filter(question=question).delete()
                return JsonResponse({'success': True,
                                    'message':
                                     'Vínculo com o evento removido.'},
                                    status=status.HTTP_200_OK)

            if event_count == 1:
                Answers.objects.filter(question=question).delete()
                photo_path = question.photo.path if question.photo else None
                if photo_path and os.path.exists(photo_path):
                    os.remove(photo_path)
                EventQuestions.objects.filter(
                    event=event, question=question).delete()

                question.delete()
                return JsonResponse({'success': True,
                                     'message':
                                     'Pergunta, respostas deletados.'},
                                    status=status.HTTP_200_OK)

            EventQuestions.objects.filter(
                event=event, question=question).delete()
            return JsonResponse({'success': True,
                                 'message': 'Vínculo com o evento removido.'},
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
