# from rest_framework.decorators import api_view
# from ...models import Plans
# from django.http import JsonResponse
# from rest_framework import status
# import stripe
# from rest_framework import settings


# @api_view(['POST'])
# def update_plan(request):
#     if request.method != 'POST':
#         return JsonResponse({"success": False,
#                              "message": "Invalid request method"},
#                             status=status.HTTP_405_METHOD_NOT_ALLOWED)
#     try:
#         # Dados do plano (exemplo, pode vir de request)
#         plano_id = request.data.get('plano_id')
#         plano = Plans.objects.get(id=plano_id)

#         # Criação da sessão de checkout no Stripe
#         checkout_session = stripe.checkout.Session.create(
#             payment_method_types=['card'],
#             line_items=[
#                 {
#                     'price_data': {
#                         'currency': 'brl',
#                         'product_data': {
#                                 'name': plano.plan_name,
#                         },
#                         'unit_amount': int(plano.price * 100),
#                     },
#                     'quantity': 1,
#                 },
#             ],
#             mode='payment',
#             success_url=request.build_absolute_uri('/pagamento/sucesso/'),
#             cancel_url=request.build_absolute_uri('/pagamento/cancelado/'),
#         )

#         return JsonResponse({'id': checkout_session.id})
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=400)


# def webhook(request):
#     payload = request.body
#     sig_header = request.META['HTTP_STRIPE_SIGNATURE']
#     endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
#     event = None

#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, endpoint_secret)
#     except ValueError:
#         return JsonResponse({'error': 'Invalid payload'}, status=400)
#     except stripe.error.SignatureVerificationError:
#         return JsonResponse({'error': 'Invalid signature'}, status=400)

#     # Agora você pode lidar com o evento do Stripe
#     if event['type'] == 'checkout.session.completed':
#         event['data']['object']

#     return JsonResponse({'status': 'success'})
