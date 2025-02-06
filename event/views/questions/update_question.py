from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
import os
from ...models import Event, Plans, NormalUser, Questions, Subscription
from ...models import EventQuestions, EventAnswer
from ...serializers.question import UpdateQuestion, CreateEventQuestions
from ...serializers.question import CreateQuestions
from django.db import transaction
import jwt
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['PUT'])
def update_question(request, eventId, questionId):
    if request.method != "PUT":
        return JsonResponse({"success": False, "message": "Método inválido"},
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
        return JsonResponse({"success": False, "message": "Token expirado."},
                            status=status.HTTP_401_UNAUTHORIZED)
    except jwt.DecodeError:
        return JsonResponse({"success": False,
                             "message": "Erro ao decodificar o token."},
                            status=status.HTTP_401_UNAUTHORIZED)

    user_id = payload.get('id')
    event_id = eventId

    try:
        event = Event.objects.get(id=event_id)
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
    question = request.data.get("question", None)
    question_type = request.data.get("questionType", None)

    existing_events = Event.objects.filter(
        id__in=Questions.objects.filter(
            id=question_id, question_type=question_type).values(
                'event')).exclude(id=event_id)
    with transaction.atomic():
        if existing_events.exists():
            # Caso de duplicação de pergunta
            question_db = Questions.objects.filter(id=question_id).first()
            if question_db.question == question:
                return JsonResponse({"success": True,
                                    "message": "Não tem o que atualizar."})
            elif question_db:
                get_event = Event.objects.get(id=question_db.event)
                if user_id != get_event.event_creator:
                    subscription = Subscription.objects.get(user=user_id)
                    plan = Plans.objects.get(id=subscription.plan)
                    if plan.plan_name == "standard":
                        return JsonResponse({"success": False,
                                            "message":
                                             "Você não pode atualizar"},
                                            status=status.HTTP_403_FORBIDDEN)

                # Criar a nova pergunta (duplicando)
                question_data = {
                    "question": question,
                    "question_type": question_type,
                    "event": event_id
                }
                new_question = CreateQuestions(data=question_data)
                if not new_question.is_valid():
                    raise Exception("Erro ao criar a pergunta.")
                question = new_question.save()

                # Criar o vínculo entre a nova pergunta e o evento
                event_question_data = {
                    "question": question.id,
                    "event": event_id
                }
                new_event_question = CreateEventQuestions(
                    data=event_question_data)
                if not new_event_question.is_valid(raise_exception=True):
                    raise Exception("Erro ao associar a pergunta ao evento.")
                new_event_question.save()

                # Vinculando as respostas antigas à nova pergunta
                event_answers = event.eventanswer_set.filter(
                    question=question_db)
                for event_answer in event_answers:
                    event_answer.question = question
                    event_answer.save()

                # Apagar vínculo antigo da pergunta com o evento
                event_question_delete = event.questions.filter(
                    id=question_id).first()
                if event_question_delete:
                    event_question_delete.delete()

                return JsonResponse({"success": True,
                                    "message":
                                     "Pergunta atualizada com sucesso"},
                                    status=status.HTTP_200_OK)
        else:
            # Caso de atualização da pergunta existente
            question_db = Questions.objects.filter(id=question_id).first()
            if question_db.question == question:
                return JsonResponse({"success": True,
                                    "message": "Não tem o que atualizar."})

            if question_db:
                get_event = Event.objects.get(id=question_db.event)
                if user_id != get_event.event_creator.id:
                    try:
                        subscription = Subscription.objects.get(user=user_id)
                        plan = Plans.objects.get(id=subscription.plan)
                        if plan.plan_name == "standard":
                            return JsonResponse({
                                "success": False,
                                "message":
                                "Você não pode atualizar"},
                                status=status.HTTP_403_FORBIDDEN)
                        # Criar a nova pergunta (duplicando)
                        question_data = {
                            "question": question,
                            "question_type": question_type,
                            "event": event_id
                        }
                        new_question = CreateQuestions(data=question_data)
                        if not new_question.is_valid():
                            raise Exception("Erro ao criar a pergunta.")
                        question = new_question.save()

                        # Criar o vínculo entre a nova pergunta e o evento
                        event_question_data = {
                            "question": question.id,
                            "event": event_id
                        }
                        new_event_question = CreateEventQuestions(
                            data=event_question_data)
                        if not new_event_question.is_valid(
                                raise_exception=True):
                            raise Exception("Erro ao associar a pergunta")
                        new_event_question.save()

                        # Vinculando as respostas antigas à nova pergunta
                        event_answers = EventAnswer.objects.filter(
                            question=question_db)
                        for event_answer in event_answers:
                            event_answer.question = question
                            event_answer.save()

                        # Apagar vínculo antigo da pergunta com o evento
                        event_question_delete = EventQuestions.objects.filter(
                            id=question_id).first()
                        if event_question_delete:
                            event_question_delete.delete()
                    except Exception:
                        return JsonResponse({"success": False,
                                            "message":
                                             "Você não pode atualizar"},
                                            status=status.HTTP_403_FORBIDDEN)
                question_update = {
                    "question": question,
                    "question_type": question_type
                }
                serializer = UpdateQuestion(question_db,
                                            data=question_update, partial=True)

                if not serializer.is_valid():
                    return JsonResponse({
                        "success": False,
                        "message":
                        "Você não pode atualizar esta pergunta."},
                        status=status.HTTP_400_BAD_REQUEST)
                serializer.save()

                return JsonResponse({"success": True,
                                    "message":
                                     "Pergunta atualizada com sucesso!"},
                                    status=status.HTTP_200_OK)
