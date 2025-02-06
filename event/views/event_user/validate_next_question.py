from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import Event, EventQuestions, ActualQuestion


@api_view(['POST'])
def validate_next_question(request, eventId, questionId):
    if request.method != "POST":
        return JsonResponse({"success": False,
                             "message": "metodo invalido"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        # Obtém o evento
        event = Event.objects.get(id=eventId)
        question_id = questionId
        # Busca todas as perguntas associadas ao evento na ordem de criação
        event_questions = EventQuestions.objects.filter(
            event=event.id).order_by('created_at')
        try:
            actual_question = ActualQuestion.objects.get(event=event.id)
        except ActualQuestion.DoesNotExist:
            has_next = False
            next_question_available = None
            return JsonResponse({
                    "success": True,
                    "message": "estado verificado",
                    "has_next": has_next,
                    "next_question_available": next_question_available
                }, status=status.HTTP_200_OK)
        # Verifica se a pergunta atual existe na lista de perguntas
        question_index = None
        for i, eq in enumerate(event_questions):
            if eq.question.id == question_id:
                question_index = i
                break

        # Se a pergunta atual não for encontrada, retorna erro
        if question_index is None:
            return JsonResponse({
                'success': False,
                'message': 'Pergunta atual não encontrada no evento.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Verifica se existe uma próxima pergunta
        next_question_available = None
        has_next = False

        if question_index + 1 < len(event_questions):
            if actual_question.actual_question == question_id:
                has_next = True
            else:
                next_question_available = actual_question.actual_question
                has_next = True

        # Retorna a resposta com o estado atualizado
        return JsonResponse({
            "success": True,
            "message": "estado verificado",
            "has_next": has_next,
            "next_question_available": next_question_available
        }, status=status.HTTP_200_OK)

    except Event.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Evento não encontrado.'
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao verificar o estado do evento: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
