import mercadopago
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.conf import settings
from ...models import Plans
from dotenv import load_dotenv
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
import json
load_dotenv()
SECRET_KEY = os.getenv('MERCADO_PAGO_ACCESS_TOKEN')


@csrf_exempt
@api_view(['POST'])
def create_preference(request):
    if request.method == 'POST':
        sdk = mercadopago.SDK(SECRET_KEY)

        # Pega o ID do plano enviado no frontend
        plan_id = request.data.get('plan_id')

        # Supondo que você tenha uma lógica para recuperar o plano do banco de dados
        plan = Plans.objects.get(id=plan_id)  # Aqui você deve buscar o plano no banco

        # Calculando a data atual e a data de um mês depois
        start_date = datetime.now()
        end_date = start_date + relativedelta(months=1)

        # Formatando as datas no formato ISO 8601 (exemplo: 2025-02-11T00:00:00Z)
        start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')

        # Criação da preferência de pagamento com base no plano recuperado
        preference_data = {
            "back_url": "https://www.your-site.com",
            "reason": plan.planName,  # Usando o nome do plano
            "auto_recurring": {
                "frequency": "1",
                "frequency_type": "months",
                "transaction_amount": plan.price,
                "currency_id": "BRL",
                "start_date": start_date_str,
                "end_date": end_date_str,
            },
            "payer_email": request.data.get("payer_email"),
        }

        # Criando a preferência no MercadoPago
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]

        return JsonResponse({
            'preference_id': preference['id']
        })

    return JsonResponse({'error': 'Invalid request method'}, status=400)
# Função para tratar notificações de pagamento (webhook)
@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        # Verifique o tipo de notificação (pode ser 'payment', 'subscription' etc.)
        if data.get('type') == 'payment':
            payment_id = data['data']['id']
            sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
            payment_info = sdk.payment().get(payment_id)
            status = payment_info['response']['status']
            
            # Atualize o status do pagamento no seu banco de dados (como exemplo)
            # Payment.objects.filter(payment_id=payment_id).update(status=status)
            print(f"Payment {payment_id} status: {status}")

        # Você também pode tratar notificações de assinatura se necessário
        elif data.get('type') == 'subscription':
            subscription_id = data['data']['id']
            sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
            subscription_info = sdk.subscription().get(subscription_id)
            status = subscription_info['response']['status']
            print(f"Subscription {subscription_id} status: {status}")

        return JsonResponse({'status': 'success'})

    return JsonResponse({'error': 'Invalid request method'}, status=400)