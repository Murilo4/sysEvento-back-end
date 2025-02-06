from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
import os
from models import NormalUser, Answers
import jwt
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['GET'])
def get_answer(request):
    if request.method != "GET":
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
    if user.user_type != "speaker":
        return JsonResponse({"success": False,
                             "message":
                            "Você não tem permissão para criar um evento"},
                            status=status.HTTP_400_BAD_REQUEST)

    event_id = request.data.get("eventId")

    answer_id = request.data.get("answerId")
    answer = Answers.objects.get(
        id=answer_id, event=event_id)
    answer = {
        "answer": answer,
        "isCorrect": answer.is_correct,
    }
    return JsonResponse({"success": True,
                        "message": "Evento criado com sucesso",
                         "answer": answer},
                        status=status.HTTP_200_OK)
