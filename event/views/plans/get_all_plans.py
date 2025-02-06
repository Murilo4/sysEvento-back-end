from rest_framework.decorators import api_view
from ...models import Subscription, Plans, PlansConfig
from django.http import JsonResponse
from rest_framework import status


@api_view(['GET'])
def get_all_plans(request):
    if request.method != 'GET':
        return JsonResponse({'success': False,
                            'message': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)
    user_id = request.data.get('userId')
    try:
        subscription = Subscription.objects.get(user=user_id)

        plan = Plans.objects.get(subscription=subscription.id)

        plan_data = {
            'dataTime': subscription.subscription_data,
            'imagesAllowed': subscription.images_allowed,
            'videosAllowed': subscription.videos_allowed,
            'description': plan.description,
            'price': plan.price,
            'planName': plan.plan_name
        }

        all_plans = Plans.objects.filter()

        for new_plan in all_plans:
            plan_config = PlansConfig.objects.get(plan=new_plan.id)
            new_plans = []
            plans = {
                'description': new_plan.description,
                'price': new_plan.price,
                'planName': new_plan.plan_name,
                'imagesAllowed': plan_config.images_allowed,
                'videosAllowed': plan_config.videos_allowed,
                'pointsMulti': plan_config.points_multiplier
            }
            new_plans.append(plans)

        return JsonResponse({'success': True,
                            'message': 'Dados retornados',
                             'ActivePlan': plan_data,
                             'availablePlans': new_plans},
                            status=status.HTTP_200_OK)

    except (Subscription.DoesNotExist, Plans.DoesNotExist):
        return JsonResponse({'success': False,
                             'message': 'Plan not found'},
                            status=status.HTTP_404_NOT_FOUND)
