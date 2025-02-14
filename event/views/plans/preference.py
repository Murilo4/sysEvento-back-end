import mercadopago
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.conf import settings
from ...models import Plans, NormalUser, UserName, Names
from rest_framework import status
from dotenv import load_dotenv
import pytz
import jwt
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
import json
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')
SECRET_KEY_MERCADO = os.getenv('MERCADO_PAGO_ACCESS_TOKEN')


@csrf_exempt
@api_view(['POST'])
def create_preference(request):
    if request.method == 'POST':
        auth_header = request.headers.get('Authorization')
        if not auth_header:
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
            print(user_id, request.data)
            user = NormalUser.objects.get(id=user_id)
            sdk = mercadopago.SDK(SECRET_KEY_MERCADO)
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
            plan_id = request.data.get('plan_id')

            try:
                plan = Plans.objects.get(id=plan_id)
            except Plans.DoesNotExist:
                return JsonResponse({'error': 'Plan not found'}, status=404)

            start_date = datetime.now(pytz.utc)
            end_date = start_date + relativedelta(months=1)

            start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            if SECRET_KEY_MERCADO.startswith('TEST'):
                print("Modo Sandbox ativado")
            preapproval_data = {
                "back_url": "http://127.0.0.1:3000/pagamento-sucesso",
                "reason": plan.plan_name,
                "auto_recurring": {
                    "frequency": 1,  # 1 vez por mês
                    "frequency_type": "months",  # Frequência mensal
                    "transaction_amount": plan.price,  # Preço da assinatura
                    "currency_id": "BRL",  # Moeda
                    "start_date": start_date_str,  # Data de início
                    "end_date": end_date_str,  # Data final (se necessário)
                },
                "payer_email": user.email,
                "subscriber": {
                    "name": full_name,  # Nome do assinante
                    "email": user.email  # Email do assinante
                },
                # URL para receber notificações de status
                "notification_url": "http://127.0.0.1:3000/notifications",
                "external_reference": "1"  # Referência externa única para identificar a transação
            }

            # Criar a pré-aprovação
            preapproval_response = sdk.preapproval().create(preapproval_data)
            print(preapproval_response)
            preapproval_data = preapproval_response['response']
            preapproval_id = preapproval_data['id']
            init_point = preapproval_data.get('init_point', None)  # Para produção
            sandbox_init_point = preapproval_data.get('sandbox_init_point', None)  # Para ambiente de teste
            print(init_point, sandbox_init_point)
            # Se você tiver o sandbox_init_point, use ele em vez de init_point
            if sandbox_init_point:
                payment_link = sandbox_init_point
            else:
                payment_link = init_point

            return JsonResponse({
                "success": True,
                'preapproval_id': preapproval_id,
                'payment_link': payment_link},
                status=status.HTTP_200_OK)
        except NormalUser.DoesNotExist:
            return JsonResponse({'error': 'Failed to create preapproval'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        if data.get('type') == 'payment':
            payment_id = data['data']['id']
            sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
            payment_info = sdk.payment().get(payment_id)
            status = payment_info['response']['status']

            print(f"Payment {payment_id} status: {status}")

        elif data.get('type') == 'subscription':
            subscription_id = data['data']['id']
            sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
            subscription_info = sdk.subscription().get(subscription_id)
            status = subscription_info['response']['status']
            print(f"Subscription {subscription_id} status: {status}")

        return JsonResponse({'status': 'success'})

    return JsonResponse({'error':
                         'Invalid request method'},
                        status=400)
