from rest_framework.decorators import api_view
from ...models import Subscription, Plans, PlansConfig, NormalUser
from django.http import JsonResponse
import jwt
from rest_framework import status
from dotenv import load_dotenv
import os
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['GET'])
def get_all_plans(request):
    if request.method != 'GET':
        return JsonResponse({'success': False,
                            'message': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({"success": False,
                             "message":
                             "Token de acesso não fornecido"},
                            status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('id')
        NormalUser.objects.get(id=user_id)
    except jwt.ExpiredSignatureError:
        return JsonResponse({"success": False,
                             "message": "Token expirado."},
                            status=status.HTTP_401_UNAUTHORIZED)
    try:
        subscription = Subscription.objects.get(user=user_id)

        plan = Plans.objects.get(id=subscription.plan.id)

        planName = plan.id

        all_plans = Plans.objects.filter(belonging_system='SysEventos')
        new_plans = []
        for new_plan in all_plans:
            plan_config = PlansConfig.objects.get(plan=new_plan.id)
            plans = {
                'id': new_plan.id,
                'description': new_plan.description,
                'price': new_plan.price,
                'planName': new_plan.plan_name,
                'numberEvents': plan_config.number_events,
                'imageOnQuestions': plan_config.image_on_questions,
            }
            new_plans.append(plans)
        print(new_plans, planName)
        return JsonResponse({'success': True,
                            'message': 'Dados retornados',
                             'activePlan': planName,
                             'availablePlans': new_plans},
                            status=status.HTTP_200_OK)

    except (Subscription.DoesNotExist, Plans.DoesNotExist):
        return JsonResponse({'success': False,
                             'message': 'Plan not found'},
                            status=status.HTTP_404_NOT_FOUND)
