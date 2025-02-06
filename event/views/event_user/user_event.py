from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from models import Event, Questions, EventQuestions, Answers, EventAnswer


@api_view(['GET'])
def get_event_details(request):
    if request.method != "GET":
        return JsonResponse({"success": False,
                             "message": "metodo invalido"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        event_id = request.data.get("eventId")
        event = Event.objects.get(id=event_id)

        event_questions = EventQuestions.objects.filter(event=event)

        event_data = {
            'event_name': event.descricao,
            'data': event.data,
            'horario_inicio': event.horario_inicio,
            'horario_final': event.horario_final,
            'participants': event.participantes,
            'photo': event.photo,
            'qr_code': event.qr_code,
            'questions': []
        }

        for event_question in event_questions:
            question = Questions.objects.get(id=event_question.question)
            answers = Answers.objects.filter(question=question, event=event_id)

            event_answers = EventAnswer.objects.filter(event=event,
                                                       answer__in=answers)

            question_data = {
                'question_text': question.question,
                'question_type': question.question_type,
                'answers': []
            }

            for answer in event_answers:
                answer_data = {
                    'answer_option': answer.answer_option,
                    'is_correct': answer.is_correct
                }
                question_data['answers'].append(answer_data)
            event_data['questions'].append(question_data)

        return JsonResponse({
            'success': True,
            'event': event_data
        }, status=status.HTTP_200_OK)

    except Event.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Evento não encontrado.'
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao buscar os dados do evento: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
