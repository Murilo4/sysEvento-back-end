from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
import os
from django.db.models import Count
from ...models import EventStatistics, Event, Answers, Questions
from ...models import NormalUser
import jwt
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['GET'])
def get_event_stats(request, eventId):
    if request.method != "GET":
        return JsonResponse({"success": False,
                             "message": "Método inválido"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({
            "success": False,
            "message": "Token de acesso não fornecido ou formato inválido."
        }, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('id')
        NormalUser.objects.get(id=user_id)
    except jwt.ExpiredSignatureError:
        return JsonResponse({"success": False,
                             "message": "Token expirado."},
                            status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return JsonResponse({"success": False,
                             "message": "Token inválido."},
                            status=status.HTTP_401_UNAUTHORIZED)
    except NormalUser.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "usuario inválido."},
                            status=status.HTTP_401_UNAUTHORIZED)

    event_id = eventId
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "Evento não encontrado."},
                            status=status.HTTP_404_NOT_FOUND)

    questions = Questions.objects.filter(event=event.id)

    event_statistics = []

    for question in questions:
        question_data = {
            'question': question.question,
            'type': question.question_type,
            'answers': []
        }
        question_tp = question.question_type
        if question_tp == 'single_choice' or question_tp == 'multiple_choice':
            answers = Answers.objects.filter(question=question)

            for answer in answers:
                answer_count = EventStatistics.objects.filter(
                    answer=answer, question=question.id).count()

                question_data['answers'].append({
                    'answer': answer.answer_option,
                    'isCorrect': answer.is_correct,
                    'votes': answer_count
                })

        # Perguntas abertas
        elif question_tp == 'open_short' or question_tp == 'open_long':
            open_answers = EventStatistics.objects.filter(
                question=question.id).values('answer_text').annotate(
                    count=Count('id'))

            for open_answer in open_answers:
                question_data['answers'].append({
                    'answerText': open_answer['answer_text'],
                    'count': open_answer['count']
                })

        event_statistics.append(question_data)

    # Retorna os dados de estatísticas
    return JsonResponse({
        'event_name': event.descricao,
        'questions': event_statistics
    })
