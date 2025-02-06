from rest_framework.decorators import api_view, throttle_classes
from django.http import JsonResponse
from rest_framework import status
from ...models import NormalUser, UserName
import jwt
import os
from ...throttles import DailyRateThrottle, HourlyRateThrottle
from ...throttles import MinuteRateThrottle
from django.db import transaction
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ADDRESS_API_URL = os.getenv('ADDRESS_API_URL')


@api_view(['DELETE'])
@throttle_classes([MinuteRateThrottle, HourlyRateThrottle, DailyRateThrottle])
def delete_user(request):
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

        try:
            user = NormalUser.objects.get(id=user_id)
        except NormalUser.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Usuário não encontrado.'
            }, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            deleted_usernames = UserName.objects.filter(
                user_id=user_id).delete()
            if deleted_usernames:
                user.delete()

        return JsonResponse({'success': True,
                             'message': 'Usuário deletado com sucesso!'},
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
