from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status


@api_view(["GET"])
def cron_job(request):
    if request.method != "GET":
        return JsonResponse({"success": True,
                             "message": "método invalido"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

    return JsonResponse({"success": True,
                         "message": "cron job acessou com sucesso"},
                        status=status.HTTP_200_OK)
