from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
import os
from models import NormalUser
from ...serializers.answer import CreateAnswer, CreateEventAnswer
import jwt
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['POST'])
def create_answer(request):
    if request.method != "POST":
        return JsonResponse({"success": False,
                             "message": "método invalido"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({
            "success": False,
            "message": "Token de acesso não fornecido ou formato inválido."
        }, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]

    payload = jwt.decode(token,
                         SECRET_KEY, algorithms=['HS256'])
    user_id = payload.get('id')
    user = NormalUser.objects.get(id=user_id)
    event_id = request.data.get("eventId")
    if user.user_type != "speaker":
        return JsonResponse({"success": False,
                             "message":
                            "Você não tem permissão para criar um evento"},
                            status=status.HTTP_400_BAD_REQUEST)

    question = request.data.get("questionId")
    answer = request.data.get("answer")
    correct = request.data.get('isCorrect')
    new_answer = {
        "answer_options": answer,
        "is_correct": correct,
        "question": question
    }
    new_answer = CreateAnswer(data=new_answer)

    if new_answer.is_valid():
        new_answer.save()
        event_answer = {
            "answer": new_answer.id,
            "event": event_id
        }
        new_event_answer = CreateEventAnswer(data=event_answer)
        if new_event_answer.is_valid():
            new_event_answer.save()

            return JsonResponse({"success": True,
                                "message": "pergunta criado com sucesso"},
                                status=status.HTTP_200_OK)
    else:
        return JsonResponse({"succes": False,
                             "message": "Erro inesperado"},
                            status=status.HTTP_404_NOT_FOUND)
