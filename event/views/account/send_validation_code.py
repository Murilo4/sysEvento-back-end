from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
import re
from ...models import NormalUser
from ...serializers.NormalUser import UpdateValidationNormalUser
from django.core.mail import send_mail
from django.core.cache import cache
import random
import os
email = os.getenv('EMAIL')


@api_view(['POST'])
def email_validation(request):
    if request.method != 'POST':
        return JsonResponse({'success': False,
                            'message': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)

    try:
        email = request.data.get('email', None)
        cpf = request.data.get("cpf", None)
        cnpj = request.data.get("cnpj", None)
        if not email:
            if not cpf and not cnpj:
                return JsonResponse({'success': False,
                                    'message': 'Email é obrigatório'},
                                    status=status.HTTP_400_BAD_REQUEST)
            if cpf:
                user = NormalUser.objects.get(cpf=cpf)
                email = user.email
            elif cnpj:
                user = NormalUser.objects.get(cnpj=cnpj)
                email = user.email

        r = re.compile(r'^[\w.-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$')
        if not r.match(email):
            return JsonResponse({'success': False,
                                 'message': 'Invalid email format'},
                                status=status.HTTP_400_BAD_REQUEST)
        print(email)
        validation_code = f'{random.randint(100000, 999999)}'

        subject = 'Código de validação'
        message = f'Seu código de validação é: {validation_code}'
        from_email = email
        recipient_list = [email]

        send_mail(
            subject, message, from_email, recipient_list, fail_silently=False)

        cache.set(f'validation_code_{email}', validation_code, timeout=600)

        return JsonResponse({'success': True,
                             'message': 'Email enviado com sucesso'},
                            status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'success': False,
                             'message': 'Erro ao enviar o e-mail',
                             'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def verify_email_code(request):
    if request.method != 'POST':
        return JsonResponse({'success': False,
                            'message': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        email = request.data.get('email', None)
        cpf = request.data.get("cpf", None)
        cnpj = request.data.get("cnpj", None)
        if not email:
            if not cpf and not cnpj:
                return JsonResponse({'success': False,
                                    'message': 'Email é obrigatório'},
                                    status=status.HTTP_400_BAD_REQUEST)
            if cpf:
                user = NormalUser.objects.get(cpf=cpf)
                email = user.email
            elif cnpj:
                user = NormalUser.objects.get(cnpj=cnpj)
                email = user.email
        code = request.data.get('code')

        if not email or not code:
            return JsonResponse({'success': False,
                                 'message': 'Email e código são obrigatórios'},
                                status=status.HTTP_400_BAD_REQUEST)
        stored_code = cache.get(f'validation_code_{email}')

        if stored_code is None:
            return JsonResponse({'success': False,
                                 'message': 'O código expirou ou não existe'},
                                status=status.HTTP_400_BAD_REQUEST)

        if stored_code == code:
            user = NormalUser.objects.get(email=email)
            cache.delete(f'validation_code_{email}')
            user_updated = UpdateValidationNormalUser(user,
                                                      data={'is_validated': 1},
                                                      partial=True)
            if user_updated.is_valid(raise_exception=True):
                user_updated.save()
                return JsonResponse({'success': True,
                                    'message': 'Código validado com sucesso'},
                                    status=status.HTTP_200_OK)

        return JsonResponse({'success': False,
                             'message': 'O código está incorreto'},
                            status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return JsonResponse({'success': False,
                             'message': 'Erro ao validar o código',
                             'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
