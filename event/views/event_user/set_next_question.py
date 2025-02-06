from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import Event, ActualQuestion
from ...serializers.event import UpdateQuestionSeria


@api_view(['POST'])
def update_event_state(request, eventId, questionId):
    if request.method != "POST":
        return JsonResponse({"success": False,
                             "message": "metodo invalido"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        event_id = eventId
        event = Event.objects.get(id=event_id)

        question_actual = ActualQuestion.objects.get(
            event=event)
        new_question = {
            "actual_question": questionId
        }
        update_question = UpdateQuestionSeria(
            question_actual,
            data=new_question,
            partial=True)
        if not update_question.is_valid():
            return JsonResponse({'success': False,
                                'message':
                                 'Erro ao atualizar estado do evento'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        update_question.save()
        return JsonResponse({"success": True,
                             "message": "estado atualizado"},
                            status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao buscar os dados do evento: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
