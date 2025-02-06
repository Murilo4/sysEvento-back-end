from rest_framework.decorators import api_view  # , throttle_classes
from django.http import JsonResponse
from rest_framework import status
from ...models import NormalUser, UserName, Names, Subscription
import jwt
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')
KEY = os.getenv("KEY")
cipher_suite = Fernet(KEY)


@api_view(['GET'])
# @throttle_classes([
#     MinuteRateThrottle, HourlyRateThrottle, DailyRateThrottle])
def get_user_profile(request):
    if request.method != "GET":
        return JsonResponse({
            "success": False,
            "message": "Invalid request method"
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({
            "success": False,
            "message": "Token de acesso não fornecido ou formato inválido."
        }, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        user_id = payload.get('id')
        cpf = payload.get('cpf')
        cnpj = payload.get('cnpj')
        user_data = {
            'id': user_id,
            'cpf': cpf,
        }
    except Exception:
        return JsonResponse({
            "success": False,
            "message": "Token JWT inválido ou expirado."
        }, status=status.HTTP_401_UNAUTHORIZED)  # 401 - Unauthorized

    # 4️⃣ Busca o usuário no banco de dados
    try:
        if cpf:
            user = NormalUser.objects.get(cpf=cpf)
        elif cnpj:
            user = NormalUser.objects.get(cnpj=cnpj)
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

        user_data = {
            'username': full_name,
            'email': user.email,
            'cpf': user.cpf,
            'cnpj': user.cnpj,
            'phone': user.phone,
            'photo': user.photo
        }
        try:
            plan = Subscription.objects.get(user=user_id)

            plan_data = {
                'dataTime': plan.subscription_data,
                'imagesAllowed': plan.images_allowed,
                'videosAllowed': plan.videos_allowed
            }
        except Subscription.DoesNotExist:
            plan_data = {}

        return JsonResponse({
            "success": True,
            "message": "Dados do usuário recuperados com sucesso.",
            "userData": user_data,
            "subscriptionData": plan_data
        }, status=status.HTTP_200_OK)
    except NormalUser.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Usuário não encontrado."
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": "Erro interno no servidor.",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
