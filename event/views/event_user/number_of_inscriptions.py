from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import Event, UserEvent


@api_view(['GET'])
def get_registration_count(request, eventId):
    if request.method != "GET":
        return JsonResponse({"success": False,
                             "message": "metodo invalido"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        event_id = eventId
        event = Event.objects.get(id=event_id)
        try:
            number_inscription = UserEvent.objects.filter(
                event=event).count()
        except UserEvent.DoesNotExist:
            number_inscription = 0

        return JsonResponse({"success": True,
                             "message": "estado atualizado",
                             "count": number_inscription},
                            status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao buscar os dados do evento: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
