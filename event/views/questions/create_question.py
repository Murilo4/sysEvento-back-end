from rest_framework.decorators import api_view  # , throttle_classes
from django.http import JsonResponse
from rest_framework import status
import os
from ...models import NormalUser, Questions
from django.db import transaction
from ...serializers.question import CreateQuestions, CreateEventQuestions
from ...serializers.answer import CreateAnswer, CreateEventAnswer
import jwt
import json
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['POST'])
def create_question(request, eventId):
    if request.method != "POST":
        return JsonResponse({"success": False,
                             "message": "Método inválido"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # Validar token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({"success": False,
                             "message":
                             "Token de acesso não fornecido"},
                            status=status.HTTP_401_UNAUTHORIZED)

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

    # Obter dados da requisição
    event_id = eventId
    question_text = request.data.get("question")
    question_type = request.data.get("questionType")
    question_photo = request.data.get("photo", None)
    answers = request.data.get("answers", [])
    if not question_text or not question_type:
        return JsonResponse({"success": False,
                             "message": "Todos os campos são obrigatórios."},
                            status=status.HTTP_400_BAD_REQUEST)
    if not answers and question_type in ["multiple_choice", "single_choice"]:
        return JsonResponse({"success": False,
                             "message":
                             "As respostas são obrigatorias"},
                            status=status.HTTP_400_BAD_REQUEST)
    if answers:
        try:
            answers = json.loads(answers)
        except json.JSONDecodeError:
            return JsonResponse({"success": False,
                                "message":
                                 "Erro ao decodificar as respostas."},
                                status=status.HTTP_400_BAD_REQUEST)
    else:
        answers = []
    try:
        with transaction.atomic():
            existing_question = Questions.objects.filter(
                question=question_text, question_type=question_type).first()
            print("o erro não deu aqui")
            if existing_question:
                # Se a pergunta já existir, apenas vincular ao evento
                event_question_data = {
                    "question": existing_question.id,
                    "event": event_id
                }
                new_event_question = CreateEventQuestions(
                    data=event_question_data)
                if not new_event_question.is_valid():
                    raise Exception("Erro ao associar a pergunta ao evento.")
                new_event_question.save()

                return JsonResponse({"success": True,
                                     "message": "vinculada ao evento"},
                                    status=status.HTTP_200_OK)

            # Caso contrário, criar a nova pergunta

            question_data = {
                "question": question_text,
                "question_type": question_type,
                "event": event_id,
                "photo": question_photo
            }
            print("gerou o question data da nova pergunta")
            new_question = CreateQuestions(data=question_data)
            if not new_question.is_valid():
                raise Exception("Erro ao criar a pergunta.")
            question = new_question.save()
            print("gerou a pergunta e está gerando o question data da tabela intermediaria")
            # Associar a nova pergunta ao evento
            event_question_data = {
                "question": question.id,
                "event": event_id
            }
            new_event_question = CreateEventQuestions(data=event_question_data)
            if not new_event_question.is_valid(raise_exception=True):
                raise Exception("Erro ao associar a pergunta ao evento.")
            new_event_question.save()
            print("fez o processo completo")
            if question_type in ['multiple_choice', 'single_choice']:
                for answer_data in answers:
                    print(answer_data)
                    answer_text = answer_data.get("answer")
                    is_correct = answer_data.get("isCorrect", False)

                    answer_payload = {
                        "answer_option": answer_text,
                        "is_correct": is_correct,
                        "question": question.id,
                        "event": event_id
                    }
                    new_answer = CreateAnswer(data=answer_payload)
                    if new_answer.is_valid(raise_exception=True):
                        answer_created = new_answer.save()

                        # Associar a resposta ao evento
                        event_answer_data = {
                            "answer": answer_created.id,
                            "event": event_id,
                            "question": question.id
                        }
                        new_event_answer = CreateEventAnswer(
                            data=event_answer_data)
                        if new_event_answer.is_valid(raise_exception=True):
                            new_event_answer.save()
                        else:
                            raise Exception("Erro ao associar a resposta")
                    else:
                        raise Exception("Erro ao salvar a resposta.")

            return JsonResponse({"success": True,
                                 "message": "Pergunta e respostas criadas"},
                                status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
