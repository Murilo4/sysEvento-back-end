from django.http import JsonResponse
from rest_framework.decorators import api_view
from ...models import Questions, Answers, EventFilter
from ...serializers.event import CreateStatistics
from rest_framework import status


@api_view(['POST'])
def store_answer(request, eventId, questionId, userId):
    if request.method != "POST":
        return JsonResponse({"success": False,
                             "message": "metodo invalido"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

    event_id = eventId
    question_id = questionId
    answer_ids = request.data.get('answerIds', [])
    answer_text = request.data.get('answer', '')
    filter_event = EventFilter.objects.filter(event=event_id, is_active=True)
    if filter_event.count() == 1:
        active_event = filter_event.first()
    else:
        return JsonResponse({"success": False,
                             "message": "Pergunta não encontrada."},
                            status=status.HTTP_404_NOT_FOUND)
    try:
        question = Questions.objects.get(id=question_id, event=event_id)
    except Questions.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "Pergunta não encontrada."},
                            status=status.HTTP_404_NOT_FOUND)

    if question.question_type == 'multiple_choice':
        # Múltiplas respostas podem ser enviadas
        if not answer_ids:
            return JsonResponse({"success": False,
                                 "message": "erro"},
                                status=status.HTTP_400_BAD_REQUEST)

        for answer_id in answer_ids:
            try:
                answer = Answers.objects.get(id=answer_id, question=question)

                new_stats = CreateStatistics(data={"event": active_event.id,
                                                   "question": question_id,
                                                   "answer": answer.id,
                                                   "user_event": userId})
                if not new_stats.is_valid():
                    return JsonResponse({"success": False,
                                         "message": "erro ao salvar resposta"},
                                        status=status.HTTP_404_NOT_FOUND)
                new_stats.save()
            except Answers.DoesNotExist:
                return JsonResponse({"success": False,
                                     "message": "Resposta não encontrada."},
                                    status=status.HTTP_404_NOT_FOUND)

    elif question.question_type == 'single_choice':
        # Para escolha única, apenas um answer_id será fornecido
        if not answer_ids or len(answer_ids) != 1:
            return JsonResponse({"success": False,
                                 "message": "Resposta invalida"},
                                status=status.HTTP_400_BAD_REQUEST)

        answer_id = answer_ids[0]
        try:
            answer = Answers.objects.get(id=answer_id, question=question)
            # Criar um registro na tabela event_statistics
            new_stats = CreateStatistics(data={"event": active_event.id,
                                               "question": question_id,
                                               "answer": answer.id,
                                               "user_event": userId})
            if not new_stats.is_valid():
                return JsonResponse({"success": False,
                                     "message": "erro ao salvar resposta"},
                                    status=status.HTTP_404_NOT_FOUND)
            new_stats.save()
        except Answers.DoesNotExist:
            return JsonResponse({"success": False,
                                 "message": "Resposta não encontrada."},
                                status=status.HTTP_404_NOT_FOUND)

    elif question.question_type in ['open_short', 'open_long']:
        # Para perguntas abertas, apenas o texto da resposta é necessário
        if not answer_text:
            return JsonResponse({"success": False,
                                 "message": "resposta não pode ser vazio."},
                                status=status.HTTP_400_BAD_REQUEST)
        # Criar um registro na tabela event_statistics para a resposta aberta
        new_stats = CreateStatistics(data={"event": active_event.id,
                                           "question": question_id,
                                           "answer_text": answer_text,
                                           "user_event": userId})
        if not new_stats.is_valid():
            return JsonResponse({"success": False,
                                "message": "erro ao salvar resposta"},
                                status=status.HTTP_404_NOT_FOUND)
        new_stats.save()

    else:
        return JsonResponse({"success": False,
                             "message": "Tipo de pergunta não reconhecido."},
                            status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({"success": True,
                         "message": "Resposta registrada com sucesso."},
                        status=status.HTTP_200_OK)
