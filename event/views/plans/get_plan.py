from rest_framework.decorators import api_view
from ...models import Subscription, Plans
from django.http import JsonResponse
from rest_framework import status


@api_view(['GET'])
def get_plan(request):
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

        return JsonResponse({'success': True,
                            'message': 'Dados retornados',
                             'data': plan_data},
                            status=status.HTTP_200_OK)

    except (Subscription.DoesNotExist, Plans.DoesNotExist):
        return JsonResponse({'success': False,
                             'message': 'Plan not found'},
                            status=status.HTTP_404_NOT_FOUND)
