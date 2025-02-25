from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import Event, Questions, EventStatistics, Answers


@api_view(['GET'])
def get_end_data(request, eventId, userId):
    if request.method != "GET":
        return JsonResponse({"success": False,
                             "message": "metodo invalido"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        event = Event.objects.get(id=eventId)

        questions = Questions.objects.filter(event=event.id)

        user_answers = EventStatistics.objects.filter(user_event=userId)
    except (Event.DoesNotExist, Questions.DoesNotExist,
            EventStatistics.DoesNotExist):
        return JsonResponse({"success": False,
                             "message": "Erro ao buscar dados do evento"},
                            status=status.HTTP_400_BAD_REQUEST)

    question_responses = []

    for question in questions:
        user_answer_for_question = user_answers.filter(question=question)

        formatted_answers = []

        for user_answer in user_answer_for_question:
            if question.question_type in ['open_short', 'open_long']:

                formatted_answers.append({
                    'answer_text': user_answer.answer_text
                })
            else:
                answers = Answers.objects.filter(id=user_answer.answer.id,
                                                 question=question)
                for answer in answers:
                    formatted_answers.append({
                     'answer_text': answer.answer_option if answer else None
                    })
        options = Answers.objects.filter(question=question)

        question_responses.append({
            'question_id': question.id,
            'question_text': question.question,
            'question_type': question.question_type,
            'options': [option.answer_option for option in options],
            'user_answers': formatted_answers
        })

    data = {
        'questions': question_responses
    }
    return JsonResponse({"success": True,
                         "message": "dados retornados",
                         "data": data},
                        status=status.HTTP_200_OK)
