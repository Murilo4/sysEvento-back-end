from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
import os
from ...models import Event, Plans, NormalUser, Questions, Subscription
from ...models import EventAnswer, Answers
import jwt
from dotenv import load_dotenv
from ...serializers.answer import CreateEventAnswer, CreateAnswer
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['PUT'])
def update_answer(request, eventId, questionId):
    if request.method != "PUT":
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
    except jwt.ExpiredSignatureError:
        return JsonResponse({"success": False,
                             "message": "Token expirado."},
                            status=status.HTTP_401_UNAUTHORIZED)
    except jwt.DecodeError:
        return JsonResponse({"success": False,
                             "message": "Erro ao decodificar o token."},
                            status=status.HTTP_401_UNAUTHORIZED)

    user_id = payload.get('id')
    event_id = eventId

    try:
        Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "Evento não encontrado."},
                            status=status.HTTP_404_NOT_FOUND)

    try:
        NormalUser.objects.get(id=user_id)
    except NormalUser.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "Usuário não encontrado."},
                            status=status.HTTP_404_NOT_FOUND)

    question_id = questionId
    answers_data = request.data.get('answers', [])

    # Verifica se a pergunta existe
    question_db = Questions.objects.filter(id=question_id).first()
    if not question_db:
        return JsonResponse({"success": False,
                             "message": "Pergunta não encontrada."},
                            status=status.HTTP_404_NOT_FOUND)

    # Verifica se a pergunta pertence ao evento
    if question_db.event != event_id:
        try:
            subscription = Subscription.objects.get(user=user_id)
            plan = Plans.objects.get(id=subscription.plan.id)

            if plan.plan_name == "standard":
                return JsonResponse({"success": False,
                                    "message":
                                     "Você não pode atualizar"},
                                    status=status.HTTP_403_FORBIDDEN)
        except (Plans.DoesNotExist, Subscription.DoesNotExist):
            return JsonResponse({"success": False,
                                "message": "Você não pode atualizar"},
                                status=status.HTTP_403_FORBIDDEN)

    for answer_data in answers_data:
        answer_option = answer_data.get('answer')
        is_correct = answer_data.get('isCorrect')

        existing_answer = Answers.objects.filter(answer_option=answer_option,
                                                 is_correct=is_correct).first()
        if existing_answer:
            exist_answr = EventAnswer.objects.filter(answer=existing_answer,
                                                     event_id=event_id,
                                                     question_id=question_db.id
                                                     ).first()

            if exist_answr:
                continue
            else:
                new_event_answer = {
                    "answer": existing_answer.id,
                    "event": event_id,
                    "question": question_db.id
                    }

                new_event_ans = CreateEventAnswer(data=new_event_answer)
                if not new_event_ans.is_valid():
                    return JsonResponse({"success": False,
                                         "message":
                                         "Erro ao criar nova resposta."},
                                        status=status.HTTP_400_BAD_REQUEST)
                new_event_ans.save()
                continue
        else:
            # Se a resposta não existir, criamos uma nova resposta
            new_answer_data = {
                "answer_option": answer_option,
                "is_correct": is_correct,
                "question": question_db.id,
                "event": event_id
            }
            serializer = CreateAnswer(data=new_answer_data)
            if serializer.is_valid():
                new_answer = serializer.save()
                new_event = {
                    "answer": new_answer.id,
                    "event": event_id,
                    "question": question_db.id
                }
                new_event_answer = CreateEventAnswer(data=new_event)
                if not new_event_answer.is_valid():
                    return JsonResponse({"success": False,
                                         "message":
                                         "Erro ao criar nova resposta."},
                                        status=status.HTTP_400_BAD_REQUEST)
                new_event_answer.save()
            else:
                return JsonResponse({"success": False,
                                     "message":
                                    "Erro ao criar nova resposta."},
                                    status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({"success": True,
                         "message": "Respostas atualizadas com sucesso!"},
                        status=status.HTTP_200_OK)
